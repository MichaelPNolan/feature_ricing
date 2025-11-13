import re
import os

def parse_sway_config(config_path, file_collector):
    """
    Parses the Sway configuration file and extracts features.

    Args:
        config_path: The path to the Sway configuration file.
        file_collector: A FileCollector instance.

    Returns:
        A dictionary of categorized features.
    """
    features = {
        "Design and Appearance": [],
        "Keybindings": [],
        "Workspace Management": [],
        "Application Autostart": [],
        "Bar Configuration": None,
        "Variables": {},
        "Other": [],
    }
    if not config_path:
        return features

    _parse_sway_file(config_path, features, file_collector)

    # Resolve variables in Design and Appearance
    resolved_appearance = []
    for item, file_path in features["Design and Appearance"]:
        for var_name, (var_value, _) in features["Variables"].items():
            if var_name in item:
                item = item.replace(var_name, var_value)
        resolved_appearance.append((item, file_path))
    features["Design and Appearance"] = resolved_appearance


    return features

def _parse_sway_file(file_path, features, file_collector):
    """
    Parses a single sway configuration file and adds features to the dictionary.
    """
    try:
        with open(file_path, "r") as f:
            in_bar_block = False
            bar_block_lines = 0
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("source"): # Corrected from "include" to "source"
                    parts = line.split(" ", 1)
                    if len(parts) > 1:
                        included_path = os.path.expanduser(parts[1])
                        # Add relationship: current file sources the included file
                        file_collector.add_sourced_relationship(file_path, included_path)
                        _parse_sway_file(included_path, features, file_collector)
                    continue

                if line.startswith("set"):
                    parts = line.split()
                    var_name = parts[1]
                    var_value = " ".join(parts[2:])
                    features["Variables"][var_name] = (var_value, file_path)
                elif line.startswith("bindsym"):
                    features["Keybindings"].append((line, file_path))
                    # Check if an 'exec' command is part of the bindsym
                    exec_match = re.search(r'exec\s+(.*)', line)
                    if exec_match:
                        full_command = exec_match.group(1).strip()
                        # Resolve variables in the command
                        resolved_command = full_command
                        for var_name, (var_value, _) in features["Variables"].items():
                            resolved_command = resolved_command.replace(var_name, var_value)
                        
                        # Attempt to find an executable script in the resolved command
                        script_patterns = [
                            r'((?:~|\/)[a-zA-Z0-9_\/\.-]+\.(?:sh|py|pl|rb|js|lua|fish|zsh|bash))', # Paths with common extensions
                            r'((?:~|\/)[a-zA-Z0-9_\/\.-]+)', # General paths
                        ]
                        
                        found_script = False
                        for pattern in script_patterns:
                            for match in re.finditer(pattern, resolved_command):
                                potential_script_path = os.path.expanduser(match.group(1))
                                if os.path.exists(potential_script_path) and \
                                   os.path.isfile(potential_script_path) and \
                                   os.access(potential_script_path, os.X_OK):
                                    file_collector.add_script(potential_script_path, app_name="Sway")
                                    found_script = True
                                    break # Found an executable script, move to next line
                            if found_script:
                                break
                elif "workspace" in line:
                    features["Workspace Management"].append((line, file_path))
                elif line.startswith("exec") or line.startswith("exec_always"):
                    features["Application Autostart"].append((line, file_path))
                    
                    # Extract the command part after 'exec' or 'exec_always'
                    command_start_index = line.find("exec")
                    if command_start_index == -1: # Should not happen if line.startswith("exec_always")
                        command_start_index = line.find("exec_always")
                    
                    full_command = line[command_start_index + len("exec_always") if line.startswith("exec_always") else command_start_index + len("exec"):].strip()

                    # Resolve variables in the command
                    resolved_command = full_command
                    for var_name, (var_value, _) in features["Variables"].items():
                        resolved_command = resolved_command.replace(var_name, var_value)
                    
                    
                    # Attempt to find an executable script in the resolved command
                    # This is a heuristic and might not catch all cases
                    # Attempt to find an executable script in the resolved command
                    # Look for paths starting with / or ~/ or ending with common script extensions
                    script_patterns = [
                        r'((?:~|\/)[a-zA-Z0-9_\/\.-]+\.(?:sh|py|pl|rb|js|lua|fish|zsh|bash))', # Paths with common extensions
                        r'((?:~|\/)[a-zA-Z0-9_\/\.-]+)', # General paths
                    ]
                    
                    found_script = False
                    for pattern in script_patterns:
                        for match in re.finditer(pattern, resolved_command):
                            potential_script_path = os.path.expanduser(match.group(1))
                            print(f"DEBUG: Checking script: {potential_script_path}")
                            print(f"DEBUG:   exists: {os.path.exists(potential_script_path)}")
                            print(f"DEBUG:   isfile: {os.path.isfile(potential_script_path)}")
                            print(f"DEBUG:   is_executable: {os.access(potential_script_path, os.X_OK)}")
                            if os.path.exists(potential_script_path) and \
                               os.path.isfile(potential_script_path) and \
                               os.access(potential_script_path, os.X_OK):
                                file_collector.add_script(potential_script_path, app_name="Sway")
                                found_script = True
                                break # Found an executable script, move to next line
                        if found_script:
                            break
                    
                    if not found_script:
                        # Fallback to previous logic if no specific script pattern matched
                        command_parts = resolved_command.split()
                        for part in command_parts:
                            expanded_part = os.path.expanduser(part)
                            if os.path.exists(expanded_part):
                                if os.path.isfile(expanded_part) and os.access(expanded_part, os.X_OK):
                                    file_collector.add_script(expanded_part, app_name="Sway")
                                    break # Assume the first executable file found is the main script

                elif line.startswith("gaps") or "background" in line or re.search(r'client\.', line):
                    features["Design and Appearance"].append((line, file_path))
                elif line.startswith("bar {"):
                    in_bar_block = True
                    bar_block_lines = 0
                elif line == "}" and in_bar_block:
                    in_bar_block = False
                    features["Bar Configuration"] = (f"There is a bar section with {bar_block_lines} instruction statements.", file_path)
                elif in_bar_block:
                    bar_block_lines += 1
                else:
                    features["Other"].append((line, file_path))
    except FileNotFoundError:
        print(f"Warning: Included file not found: {file_path}")