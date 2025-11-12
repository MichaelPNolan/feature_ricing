import re
from collections import defaultdict
import os
from colorize_sway import colorize_sway_config_line as colorize_sway_line

# ANSI escape codes for colors and styles
COLOR_RESET = "\x1b[0m"
COLOR_RED = "\x1b[31m"
COLOR_GREEN = "\x1b[32m"
COLOR_YELLOW = "\x1b[33m"
COLOR_BLUE = "\x1b[34m"
COLOR_MAGENTA = "\x1b[35m"
COLOR_CYAN = "\x1b[36m"
COLOR_WHITE = "\x1b[37m"
COLOR_BRIGHT_BLACK = "\x1b[90m" # Often used for comments
COLOR_BRIGHT_RED = "\x1b[91m"
COLOR_BRIGHT_GREEN = "\x1b[92m"
COLOR_BRIGHT_YELLOW = "\x1b[93m"
COLOR_BRIGHT_BLUE = "\x1b[94m"
COLOR_BRIGHT_MAGENTA = "\x1b[95m"
COLOR_BRIGHT_CYAN = "\x1b[96m"
COLOR_BRIGHT_WHITE = "\x1b[97m"

STYLE_BOLD = "\x1b[1m"
STYLE_ITALIC = "\x1b[3m"
STYLE_UNDERLINE = "\x1b[4m"

def hex_to_rgb(hex_color):
    """Converts a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return None
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

def colorize_line(line, patterns_to_colors):
    """
    Applies ANSI escape codes to colorize patterns in a line.
    patterns_to_colors: A dictionary where keys are regex patterns and values are ANSI color codes.
    """
    colored_line = line
    # Sort patterns by length in descending order to prioritize longer matches
    # This helps prevent partial matches of keywords that are substrings of other keywords
    sorted_patterns = sorted(patterns_to_colors.items(), key=lambda item: len(item[0]), reverse=True)

    for pattern_str, color_code in sorted_patterns:
        # Use word boundaries to avoid partial word matches, unless the pattern itself is not a word
        if re.match(r'^\w+$', pattern_str): # If pattern is a whole word
            pattern = re.compile(r'\b(' + re.escape(pattern_str) + r')\b')
        else: # If pattern contains non-word characters, match it as is
            pattern = re.compile('(' + re.escape(pattern_str) + ')')
        
        # Replace matches with colored version, being careful not to re-colorize already colored parts
        # This is a simplified approach; a full lexer would be more robust for complex cases.
        def replacer(match):
            # Only colorize if the match is not already part of an ANSI sequence
            # This is a basic check and might not cover all edge cases
            if color_code not in match.string[max(0, match.start()-10):match.end()+10]: # Check nearby for existing color
                return color_code + match.group(1) + COLOR_RESET
            return match.group(1)
        
        colored_line = pattern.sub(replacer, colored_line)
    return colored_line





def print_waybar_modules(waybar_modules):
    """Prints the Waybar modules section."""
    print("--- Waybar Modules ---")
    if waybar_modules:
        for position, modules in waybar_modules.items():
            if modules:
                print(f"  [{position}]")
                for module in modules:
                    display_name = module
                    color_boxes = ""
                    
                    # Extract foreground color
                    fg_hex = None
                    fg_match = re.search(r'F:(#[a-fA-F0-9]{6})', module)
                    if fg_match:
                        fg_hex = fg_match.group(1)
                        rgb = hex_to_rgb(fg_hex)
                        if rgb:
                            r, g, b = rgb
                            color_boxes += f" F:\x1b[48;2;{r};{g};{b}m  \x1b[0m"
                    
                    # Extract background color
                    bg_hex = None
                    bg_match = re.search(r'B:(#[a-fA-F0-9]{6})', module)
                    if bg_match:
                        bg_hex = bg_match.group(1)
                        rgb = hex_to_rgb(bg_hex)
                        if rgb:
                            r, g, b = rgb
                            color_boxes += f" B:\x1b[48;2;{r};{g};{b}m  \x1b[0m"
                    
                    module_name_only_match = re.match(r'([a-zA-Z0-9_/-]+\*?)\s*(\(.*\))?', module)
                    if module_name_only_match:
                        base_module_name = module_name_only_match.group(1)
                        # Check if there was a style status message
                        style_status_match = re.search(r'\(no style detected\)', module) or re.search(r'\(style detected\)', module)
                        
                        final_display_name = base_module_name
                        if style_status_match:
                            final_display_name += f" {style_status_match.group(0)}"
                        
                        print(f"    - {final_display_name}{color_boxes}")
                    else:
                        # Fallback if the regex doesn't match, though it should for valid modules
                        print(f"    - {display_name}{color_boxes}")
    else:
        print("  No Waybar modules found.")
    print("-" * 40)

def generate_report(sway_features, waybar_modules, file_collector):
    """
    Generates a report of the enabled features.

    Args:
        sway_features: A dictionary of categorized Sway features.
        waybar_modules: A dictionary of categorized Waybar modules.
        file_collector: A FileCollector instance.
    """
    print("-" * 60)
    print("--- Start Report ---")
    print("-" * 60)
    print("Scanning settings for the following applications:")
    print("  - Sway")
    print("  - Waybar")
    print("-" * 40)
    print()

    print("--- Sway Configuration ---")
    for category, items in sway_features.items():
        if category == "Variables":
            if items:
                print()
                print(f"  [{category}]")
                for var_name, (var_value, file_path) in items.items():
                    # Colorize the variable definition line
                    colored_line = colorize_sway_line(f"set {var_name} {var_value}")
                    print(f"    {colored_line} (from {os.path.basename(file_path)})")
        elif category == "Bar Configuration":
            if items:
                line, file_path = items
                colored_line = colorize_sway_line(line)
                print()
                print(f"  [{category}]")
                print(f"    {colored_line} (from {os.path.basename(file_path)})")
        elif items:
            print()
            print(f"  [{category}]")
            for item, file_path in items:
                # Colorize each line item
                colored_line = colorize_sway_line(item)
                print(f"    {colored_line} (from {os.path.basename(file_path)})")
    print("-" * 40)
    print()

    # New file reporting section - moved to the end
    print()
    print("[Files Overview]")
    sway_active_configs = []
    sway_inactive_configs = []
    waybar_active_configs = []
    waybar_inactive_configs = []
    waybar_styles = []
    wal_generated_files = []
    scripts = []
    sourced_configs = []
    other_files = []

    for file_path, metadata in file_collector.files.items():
        if metadata.type == "sway_config":
            if metadata.is_active:
                sway_active_configs.append(metadata)
            else:
                sway_inactive_configs.append(metadata)
        elif metadata.type == "waybar_config":
            if metadata.is_active:
                waybar_active_configs.append(metadata)
            else:
                waybar_inactive_configs.append(metadata)
        elif metadata.type == "waybar_style":
            waybar_styles.append(metadata)
        elif metadata.type == "wal_generated":
            wal_generated_files.append(metadata)
        elif metadata.type == "script":
            scripts.append(metadata)
        elif metadata.type == "sourced_config":
            sourced_configs.append(metadata)
        else:
            other_files.append(metadata)

    def print_file_list(title, file_list):
        if file_list:
            print(f"  {title}:")
            for f_meta in file_list:
                sourced_by_info = ""
                if f_meta.sourced_by:
                    sourcing_files = [os.path.basename(p) for p in f_meta.sourced_by]
                    sourced_by_info = f" (sourced by: {', '.join(sourcing_files)})"
                print(f"  - {f_meta.path}{sourced_by_info}") # Print full path

    print_file_list("Sway Active configurations", sway_active_configs)
    print_file_list("Sway Inactive configurations", sway_inactive_configs)
    print_file_list("Waybar Active configurations", waybar_active_configs)
    print_file_list("Waybar Inactive configurations", waybar_inactive_configs)
    print_file_list("Waybar Styles", waybar_styles)
    print_file_list("Sourced configurations", sourced_configs)
    print_file_list("Scripts", scripts)
    print_file_list("Other files", other_files)

    # WAL Report Section - moved to the end
    if wal_generated_files:
        print()
        print("-" * 40)
        print("--- WAL Report ---")
        for f_meta in wal_generated_files:
            print()
            print(f"  WAL Generated File: {f_meta.path}") # Print full path
            if f_meta.sourced_by:
                sourcing_files = [os.path.basename(p) for p in f_meta.sourced_by]
                print(f"    Sourced by: {', '.join(sourcing_files)}")
            else:
                print("    Not explicitly sourced by other configs (might be implicitly used).")

    print()
    print_waybar_modules(waybar_modules)