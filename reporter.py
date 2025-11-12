import re
from collections import defaultdict
import os
from colorize_app_keywords import AppKeywordColorizer, COLOR_BRIGHT_BLACK, COLOR_RESET

# Initialize the generic colorizer
app_colorizer = AppKeywordColorizer()

# Custom colors for the report
COMMENT_COLOR_INLINE = COLOR_BRIGHT_BLACK

def hex_to_rgb(hex_color):
    """Converts a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return None
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None

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

def generate_report(sway_features, waybar_modules, kitty_configs, hyprland_features, hyprpaper_features, hyprlock_config_paths, detected_applications, all_possible_applications, file_collector):
    """
    Generates a report of the enabled features.

    Args:
        sway_features: A dictionary of categorized Sway features.
        waybar_modules: A dictionary of categorized Waybar modules.
        kitty_configs: A dictionary of parsed Kitty configurations.
        hyprland_features: A dictionary of categorized Hyprland features.
        hyprpaper_features: A dictionary of categorized Hyprpaper features.
        hyprlock_config_paths: A list of paths to detected Hyprlock configuration files.
        detected_applications: A list of application names that were detected.
        all_possible_applications: A list of all applications the reporter can scan for.
        file_collector: A FileCollector instance.
    """
    print("-" * 60)
    print("--- Start Report ---")
    print("-" * 60)
    print("Scanning settings for the following applications:")
    
    print("  Applications Detected:")
    if detected_applications:
        for app in detected_applications:
            print(f"    - {app}")
    else:
        print("    None")

    not_detected_applications = sorted(list(set(all_possible_applications) - set(detected_applications)))
    print("  Applications Not Detected:")
    if not_detected_applications:
        for app in not_detected_applications:
            print(f"    - {app}")
    else:
        print("    None")
    
    print("-" * 40)
    print()

    if "Sway" in detected_applications:
        print("--- Sway Configuration ---")
        for category, items in sway_features.items():
            if category == "Variables":
                if items:
                    print()
                    print(f"  [{category}]")
                    for var_name, (var_value, file_path) in items.items():
                        # Colorize the variable definition line
                        colored_line = app_colorizer.colorize_line(f"set {var_name} {var_value}", "SWAY")
                        print(f"    {colored_line} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
            elif category == "Bar Configuration":
                if items:
                    line, file_path = items
                    colored_line = app_colorizer.colorize_line(line, "SWAY")
                    print()
                    print(f"  [{category}]")
                    print(f"    {colored_line} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
            elif items:
                print()
                print(f"  [{category}]")
                for item, file_path in items:
                    # Colorize each line item
                    colored_line = app_colorizer.colorize_line(item, "SWAY")
                    print(f"    {colored_line} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
        print("-" * 40)
        print()

    if "Waybar" in detected_applications:
        print_waybar_modules(waybar_modules)

    if "Kitty" in detected_applications:
        print("--- Kitty Configuration ---")
        if kitty_configs:
            for config_path, config_data in kitty_configs.items():
                print(f"  [{os.path.basename(config_path)}]")
                for key, value in config_data.items():
                    print(f"    {key}: {value}")
        else:
            print("  No Kitty configurations found.")
        print("-" * 40)
        print()

    if "Hyprland" in detected_applications:
        print("--- Hyprland Configuration ---")
        
        last_block_file_path = None # Track file_path for block comments
        
        # Print Variables section first if it exists
        if "Variables" in hyprland_features and hyprland_features["Variables"]:
            print()
            print(f"  [Variables]")
            for var_name, (var_value, file_path) in hyprland_features["Variables"].items():
                colored_line = app_colorizer.colorize_line(f"{var_name} = {var_value}", "HYPRLAND")
                print(f"    {colored_line} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
        
        # Print other categories
        for category, items in hyprland_features.items():
            if category == "Variables":
                continue # Already printed
            elif items:
                print()
                print(f"  [{category}]")
                for item, file_path in items:
                    colored_item = app_colorizer.colorize_line(item, "HYPRLAND")
                    
                    # Logic for single file origin comment for blocks
                    if item.strip().endswith('{'):
                        print(f"    {colored_item} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
                        last_block_file_path = file_path
                    elif item.strip() == '}':
                        print(f"    {colored_item}")
                        last_block_file_path = None # Reset on closing brace
                    elif last_block_file_path and file_path == last_block_file_path:
                        print(f"    {colored_item}") # Don't print comment if same block
                    else:
                        print(f"    {colored_item} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
        print("-" * 40)
        print()

    if "Hyprpaper" in detected_applications: # New section for Hyprpaper
        print("--- Hyprpaper Configuration ---")
        for category, items in hyprpaper_features.items():
            if items:
                print()
                print(f"  [{category}]")
                for item, file_path in items:
                    colored_item = app_colorizer.colorize_line(item, "HYPRLAND") # Use HYPRLAND colorization for now
                    print(f"    {colored_item} {COMMENT_COLOR_INLINE}(from {os.path.basename(file_path)}){COLOR_RESET}")
        print("-" * 40)
        print()

    if "Hyprlock" in detected_applications: # New section for Hyprlock
        print("--- Hyprlock Configuration ---")
        if hyprlock_config_paths:
            for config_path in hyprlock_config_paths:
                print(f"  - Detected: {config_path} {COMMENT_COLOR_INLINE}(from {os.path.basename(config_path)}){COLOR_RESET}")
        else:
            print("  No Hyprlock configuration files found.")
        print("-" * 40)
        print()

        print("[Files Overview]")
    sway_active_configs = []
    sway_inactive_configs = []
    waybar_active_configs = []
    waybar_inactive_configs = []
    kitty_active_configs = []
    kitty_inactive_configs = []
    hyprland_active_configs = []
    hyprland_inactive_configs = []
    hyprpaper_active_configs = [] # New list for hyprpaper
    hyprpaper_inactive_configs = [] # New list for hyprpaper
    hyprlock_active_configs = [] # New list for hyprlock
    hyprlock_inactive_configs = [] # New list for hyprlock
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
        elif metadata.type == "kitty_config":
            if metadata.is_active:
                kitty_active_configs.append(metadata)
            else:
                kitty_inactive_configs.append(metadata)
        elif metadata.type == "hyprland_config":
            if metadata.is_active:
                hyprland_active_configs.append(metadata)
            else:
                hyprland_inactive_configs.append(metadata)
        elif metadata.type == "hyprpaper_config": # New condition for hyprpaper
            if metadata.is_active:
                hyprpaper_active_configs.append(metadata)
            else:
                hyprpaper_inactive_configs.append(metadata)
        elif metadata.type == "hyprlock_config": # New condition for hyprlock
            if metadata.is_active:
                hyprlock_active_configs.append(metadata)
            else:
                hyprlock_inactive_configs.append(metadata)
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
                    sourced_by_info = f" {COLOR_BRIGHT_BLACK}(sourced by: {', '.join(sourcing_files)}){COLOR_RESET}"
                print(f"  - {f_meta.path}{sourced_by_info}") # Print full path

    print_file_list("Sway Active configurations", sway_active_configs)
    print_file_list("Sway Inactive configurations", sway_inactive_configs)
    print_file_list("Waybar Active configurations", waybar_active_configs)
    print_file_list("Waybar Inactive configurations", waybar_inactive_configs)
    print_file_list("Kitty Active configurations", kitty_active_configs)
    print_file_list("Kitty Inactive configurations", kitty_inactive_configs)
    print_file_list("Hyprland Active configurations", hyprland_active_configs)
    print_file_list("Hyprland Inactive configurations", hyprland_inactive_configs)
    print_file_list("Hyprpaper Active configurations", hyprpaper_active_configs)
    print_file_list("Hyprpaper Inactive configurations", hyprpaper_inactive_configs)
    print_file_list("Hyprlock Active configurations", hyprlock_active_configs) # New print for hyprlock
    print_file_list("Hyprlock Inactive configurations", hyprlock_inactive_configs) # New print for hyprlock
    print_file_list("Waybar Styles", waybar_styles)
    print_file_list("Sourced configurations", sourced_configs)
    print_file_list("Scripts", scripts)
    print_file_list("Other files", other_files)

    # WAL Report Section - moved to the end
    if file_collector.wal_detected: # Only print WAL report if wal command was detected
        # Ensure wal_generated_files are collected if wal is detected
        file_collector.find_colors_waybar_css() # This will add ~/.cache/wal/colors-waybar.css if it exists
        
        # Re-populate wal_generated_files list after calling find_colors_waybar_css
        wal_generated_files = [f for f in file_collector.files.values() if f.type == "wal_generated"]

        if wal_generated_files:
            print()
            print("-" * 40)
            print("--- WAL Report ---")
            for f_meta in wal_generated_files:
                print()
                print(f"  WAL Generated File: {f_meta.path}") # Print full path
                if f_meta.sourced_by:
                    sourcing_files = [os.path.basename(p) for p in f_meta.sourced_by]
                    print(f"    Sourced by: {COLOR_BRIGHT_BLACK}{', '.join(sourcing_files)}{COLOR_RESET}")
                else:
                    print("    Not explicitly sourced by other configs (might be implicitly used).")

    print()
    print("-" * 60)
    print("--- End Report ---")
    print("-" * 60)