import re
import os

def parse_hyprland_config(config_path, file_collector):
    """
    Parses the Hyprland configuration file and extracts features.

    Args:
        config_path: The path to the Hyprland configuration file.
        file_collector: A FileCollector instance.

    Returns:
        A dictionary of categorized features.
    """
    features = {
        "Variables": {},
        "Keybindings": [],
        "Application Autostart": [],
        "Window Rules": [],
        "Monitor Configuration": [],
        "Input Configuration": [],
        "General Settings": [],
        "Decoration Settings": [],
        "Animation Settings": [],
        "Layout Settings": [],
        "Gestures": [],
        "Other": [],
    }
    if not config_path:
        return features

    _parse_hyprland_file(config_path, features, file_collector)
    return features

def _parse_hyprland_file(file_path, features, file_collector):
    """
    Parses a single Hyprland configuration file and adds features to the dictionary,
    handling nested configuration blocks.
    """
    try:
        with open(file_path, "r") as f:
            current_section = None
            section_stack = [] # To handle nested sections

            # Mapping of section names to feature categories
            section_category_map = {
                "input": "Input Configuration",
                "general": "General Settings",
                "decoration": "Decoration Settings",
                "animations": "Animation Settings",
                "dwindle": "Layout Settings",
                "master": "Layout Settings",
                "gestures": "Gestures",
                "blur": "Decoration Settings", # Nested within decoration
                "shadow": "Decoration Settings", # Nested within decoration
                "touchpad": "Input Configuration", # Nested within input
                "misc": "Other", # Grouping misc under Other for now
            }

            for line in f:
                original_line = line.rstrip('\n') # Keep original line for reporting
                stripped_line = line.strip()

                if not stripped_line or stripped_line.startswith("#"):
                    # Add comments and empty lines to the current section if active, otherwise skip
                    if current_section:
                        features[section_category_map.get(current_section, "Other")].append((original_line, file_path))
                    continue

                # Handle 'source = /path/to/file'
                source_match = re.match(r'^\s*source\s*=\s*(.*)$', stripped_line)
                if source_match:
                    sourced_path = source_match.group(1).strip()
                    
                    # First, expand user for ~
                    expanded_sourced_path = os.path.expanduser(sourced_path)

                    # Then, if it's not an absolute path, resolve it relative to the current config file's directory
                    if not os.path.isabs(expanded_sourced_path):
                        sourced_path = os.path.join(os.path.dirname(file_path), expanded_sourced_path)
                    else:
                        sourced_path = expanded_sourced_path # Use the expanded path if it's already absolute
                    
                    if file_collector:
                        file_collector.add_sourced_relationship(file_path, sourced_path)
                    _parse_hyprland_file(sourced_path, features, file_collector) # Recursive call
                    continue

                # Section handling
                if stripped_line.endswith('{'):
                    section_name = stripped_line.split('{')[0].strip()
                    section_stack.append(current_section) # Save parent section
                    current_section = section_name
                    features[section_category_map.get(current_section, "Other")].append((original_line, file_path))
                elif stripped_line == '}':
                    if section_stack:
                        features[section_category_map.get(current_section, "Other")].append((original_line, file_path))
                        current_section = section_stack.pop() # Restore parent section
                    else:
                        current_section = None # Should not happen if braces are balanced
                elif current_section:
                    # Add line to current active section
                    features[section_category_map.get(current_section, "Other")].append((original_line, file_path))
                else:
                    # Handle key-value pairs and categorize for top-level items
                    if stripped_line.startswith("set $"):
                        parts = stripped_line.split(" ", 2)
                        if len(parts) > 2:
                            var_name = parts[1]
                            var_value = parts[2]
                            features["Variables"][var_name] = (var_value, file_path)
                    elif re.match(r'^\$[a-zA-Z0-9_]+\s*=\s*.*$', stripped_line):
                        parts = stripped_line.split("=", 1)
                        var_name = parts[0].strip()
                        var_value = parts[1].strip()
                        features["Variables"][var_name] = (var_value, file_path)
                    elif stripped_line.startswith(("bind ", "binde ", "bindm ", "bindem ")):
                        features["Keybindings"].append((original_line, file_path))
                        exec_match = re.search(r'exec\s+([^\s].*)', stripped_line)
                        if exec_match:
                            full_command = exec_match.group(1).strip()
                            _detect_and_add_script(full_command, file_collector)
                    elif stripped_line.startswith(("exec ", "exec-once ")):
                        features["Application Autostart"].append((original_line, file_path))
                        full_command = stripped_line.split(" ", 1)[1].strip()
                        _detect_and_add_script(full_command, file_collector)
                    elif stripped_line.startswith(("windowrule ", "windowrule v2 ")):
                        features["Window Rules"].append((original_line, file_path))
                    elif stripped_line.startswith("monitor "):
                        features["Monitor Configuration"].append((original_line, file_path))
                    else:
                        features["Other"].append((original_line, file_path))

    except FileNotFoundError:
        print(f"Warning: Included Hyprland file not found: {file_path}")
    except Exception as e:
        print(f"Error parsing Hyprland file {file_path}: {e}")

def _detect_and_add_script(command_string, file_collector):
    """
    Detects if a command string contains an executable script and adds it to the file_collector.
    Also detects if the 'wal' command is used.
    """
    if "wal" in command_string:
        file_collector.wal_detected = True
    
    if "hyprpaper" in command_string:
        file_collector.find_hyprpaper_configs()

    script_patterns = [
        r'((?:~|\/)[a-zA-Z0-9_\/\.-]+\.(?:sh|py|pl|rb|js|lua|fish|zsh|bash))', # Paths with common extensions
        r'((?:~|\/)[a-zA-Z0-9_\/\.-]+)', # General paths
    ]
    
    for pattern in script_patterns:
        for match in re.finditer(pattern, command_string):
            potential_script_path = os.path.expanduser(match.group(1))
            if os.path.exists(potential_script_path) and \
               os.path.isfile(potential_script_path) and \
               os.access(potential_script_path, os.X_OK):
                file_collector.add_script(potential_script_path)
                return # Found an executable script, no need to check further