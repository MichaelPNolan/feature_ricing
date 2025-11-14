import re
import configparser

# ANSI escape codes for colors and styles (global constants)
COLOR_RESET = "\033[0m"
COLOR_KEYWORD = "\033[96m"  # Cyan
COLOR_VARIABLE = "\033[93m" # Yellow
COLOR_KEY_NAME = "\033[92m" # Green
COLOR_COMMENT = "\033[33m" # Brown/Yellow for comments
COLOR_BRIGHT_BLACK = "\x1b[90m" # Often used for comments
COLOR_BRACKET = "\033[95m" # Magenta for curly brackets
COLOR_OPTION = "\033[36m" # Cyan for options/flags
COLOR_NUMBER = "\033[34m" # Blue for numbers

class AppKeywordColorizer:
    def __init__(self, config_file='app_keyword_defs.conf', dynamic_variables=None):
        self.keyword_defs = self._load_keyword_definitions(config_file)
        self.compiled_patterns = {}
        self.dynamic_variables = dynamic_variables # Store dynamic variables

    def _load_keyword_definitions(self, config_file):
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file)
        
        defs = {}
        for section in config.sections():
            app_name = section.upper()
            defs[app_name] = {}
            for key, value in config.items(section):
                defs[app_name][key.upper()] = [item.strip() for item in value.split(',')]
        return defs

    def _compile_patterns(self, app_name):
        if app_name not in self.compiled_patterns:
            app_defs = self.keyword_defs.get(app_name, {})
            patterns = []

            # VARIABLEs (process first to ensure '$' is not consumed by other patterns)
            variables = app_defs.get('VARIABLE', [])
            if variables:
                # Explicitly escape '$' in variable patterns
                escaped_variables = [v.replace('$', r'\$') for v in variables]
                compiled_variable_pattern = re.compile(r'(' + '|'.join(escaped_variables) + r')')
                patterns.append((compiled_variable_pattern, COLOR_VARIABLE))

            all_keywords = app_defs.get('KEYWORD', [])
            command_keywords = []
            option_keywords = []
            
            # Separate keywords into commands and options
            for k in all_keywords:
                if k.startswith('-'):
                    option_keywords.append(k)
                elif len(k) > 1 or k in ['h', 'v', 'n']: # Explicitly keep single-char commands if they are common, removed 't'
                    command_keywords.append(k)

            if command_keywords:
                command_keywords.sort(key=len, reverse=True)
                patterns.append((re.compile(r'\b(' + '|'.join(re.escape(k) for k in command_keywords) + r')\b'), COLOR_KEYWORD))
            
            if option_keywords:
                option_keywords.sort(key=len, reverse=True)
                patterns.append((re.compile(r'\b(' + '|'.join(re.escape(k) for k in option_keywords) + r')\b'), COLOR_OPTION))

            # Numbers
            numbers = app_defs.get('NUMBER', [])
            if numbers:
                patterns.append((re.compile(r'\b(' + '|'.join(numbers) + r')\b'), COLOR_NUMBER))

            # KEY_NAMEs
            key_names = app_defs.get('KEY_NAME', [])
            if key_names:
                key_names.sort(key=len, reverse=True)
                patterns.append((re.compile(r'(?:^|[\s+])(' + '|'.join(re.escape(k) for k in key_names) + r')(?=\W|$)', re.IGNORECASE), COLOR_KEY_NAME))
            


            # Curly Brackets
            patterns.append((re.compile(r'([{}])'), COLOR_BRACKET))

            self.compiled_patterns[app_name] = patterns
        return self.compiled_patterns[app_name]

    def colorize_line(self, line, app_name):
        code_part = line
        comment_part = ""
        
        # Find the first '#' that is not escaped
        comment_start_index = -1
        for i in range(len(line)):
            if line[i] == '#' and (i == 0 or line[i-1] != '\\'):
                comment_start_index = i
                break

        if comment_start_index != -1:
            code_part = line[:comment_start_index]
            comment_part = line[comment_start_index:]

        patterns = self._compile_patterns(app_name)
        
        # List of (text, is_colored) tuples
        # Initially, the whole code_part is one uncolored segment
        segments = [(code_part, False)] 
        
        for pattern, color in patterns:
            new_segments = []
            for text, is_colored in segments:
                if is_colored:
                    new_segments.append((text, True))
                    continue
                
                last_idx = 0
                for match in pattern.finditer(text):
                    start, end = (match.start(1), match.end(1)) if pattern.groups > 0 else (match.start(0), match.end(0))
                    
                    # Add the uncolored part before the match
                    if start > last_idx:
                        new_segments.append((text[last_idx:start], False))
                    
                    # Add the colored part
                    new_segments.append((color + text[start:end] + COLOR_RESET, True))
                    last_idx = end
                
                # Add any remaining uncolored part after the last match
                if last_idx < len(text):
                    new_segments.append((text[last_idx:], False))
            segments = new_segments
        
        final_code_part = "".join([text for text, _ in segments])

        if comment_part:
            final_code_part += COLOR_COMMENT + comment_part + COLOR_RESET
        
        return final_code_part

# Example Usage (for testing this module directly)
if __name__ == '__main__':
    colorizer = AppKeywordColorizer()

    print("--- Testing Hyprland Colorization ---")
    hyprland_test_lines = [
        "bindsym $mainMod+Shift+Return exec alacritty",
        "bindsym $mainMod+Alt+L exec swaylock",
        "bindsym $mainMod+CTRL+R exec systemctl restart sway",
        "bindsym $mainMod+left movefocus left",
        "bindsym $mainMod+right movefocus right",
        "bindsym $mainMod+up movefocus up",
        "bindsym $mainMod+down movefocus down",
        "bindsym $mainMod+Mod4+F fullscreen",
        "bindsym $mainMod+Page_Up workspace next",
        "bindsym $mainMod+F1 exec firefox",
        "set $mod Mod5",
        "movetoworkspace 1",
        "# This is a comment",
        "exec-once = waybar",
        "$myVar = some_value",
        "input {",
        "    touchpad {",
        "        natural_scroll = false",
        "    }",
        "}"
    ]
    for line in hyprland_test_lines:
        print(colorizer.colorize_line(line, "HYPRLAND"))

    print("\n--- Testing Sway Colorization (Example) ---")
    sway_test_lines = [
        "bindsym $mod+Shift+Return exec alacritty",
        "set $mod Mod1",
        "# This is a sway comment",
        "workspace 1",
        "client.focused #aabbcc"
    ]
    for line in sway_test_lines:
        print(colorizer.colorize_line(line, "SWAY"))