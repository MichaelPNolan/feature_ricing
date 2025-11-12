import argparse
from file_collector import FileCollector
from sway_parser import parse_sway_config
from waybar_parser import parse_waybar_config
from waybar_style_parser import parse_waybar_style
from kitty_parser import parse_kitty_config
from hyprland_parser import parse_hyprland_config
from hyprpaper_parser import parse_hyprpaper_config
from reporter import generate_report

def main():
    parser = argparse.ArgumentParser(description="Analyze Sway and Waybar configurations.")
    parser.add_argument("--waybar-styles-debug", action="store_true",
                        help="Enable debug output for Waybar style parsing.")
    args = parser.parse_args()

    # Initialize FileCollector
    file_collector = FileCollector()

    # Collect Sway configurations
    sway_config_paths = file_collector.find_sway_configs()
    sway_variables = {}
    sway_features = {}
    for config_path in sway_config_paths:
        current_features = parse_sway_config(config_path, file_collector)
        sway_features.update(current_features)
        sway_variables.update(current_features.get("Variables", {}))
    
    # Collect Waybar configurations
    waybar_config_paths = file_collector.find_waybar_configs()
    waybar_style_paths = file_collector.find_waybar_styles()
    colors_waybar_path = file_collector.find_colors_waybar_css()

    waybar_style_colors = {}
    # Iterate through active Waybar style paths
    for style_path in waybar_style_paths:
        # Pass the debug flag to waybar_style_parser
        style_colors = parse_waybar_style(style_path, sway_variables, colors_waybar_path, file_collector, args.waybar_styles_debug)
        waybar_style_colors.update(style_colors)

    # Conditional reporting based on debug flag
    if args.waybar_styles_debug:
        print("--- Waybar Style Debug Report ---")
        # The debug prints are already handled within parse_waybar_style
        # We just need to ensure the main report is not generated.
        return # Exit early after debug output
    
    waybar_modules = {}
    for config_path in waybar_config_paths:
        modules = parse_waybar_config(config_path, sway_variables, waybar_style_colors)
        for position, module_list in modules.items():
            if position not in waybar_modules:
                waybar_modules[position] = []
            waybar_modules[position].extend(module_list)

    # Collect Kitty configurations
    kitty_config_paths = file_collector.find_kitty_configs()
    kitty_configs = {}
    for config_path in kitty_config_paths:
        current_kitty_config = parse_kitty_config(config_path)
        kitty_configs[config_path] = current_kitty_config

    # Collect Hyprland configurations
    hyprland_config_paths = file_collector.find_hyprland_configs()
    hyprland_features = {}
    for config_path in hyprland_config_paths:
        current_hyprland_features = parse_hyprland_config(config_path, file_collector)
        # Merge features from all Hyprland config files
        for category, items in current_hyprland_features.items():
            if category == "Variables":
                hyprland_features.setdefault(category, {}).update(items)
            else:
                hyprland_features.setdefault(category, []).extend(items)

    # Collect Hyprpaper configurations
    hyprpaper_config_paths = file_collector.find_hyprpaper_configs()
    hyprpaper_features = {}
    for config_path in hyprpaper_config_paths:
        current_hyprpaper_features = parse_hyprpaper_config(config_path, file_collector)
        for category, items in current_hyprpaper_features.items():
            hyprpaper_features.setdefault(category, []).extend(items)

    # Collect Hyprlock configurations
    hyprlock_config_paths = file_collector.find_hyprlock_configs() # New call to find hyprlock configs


    # Determine detected applications
    detected_applications = []
    if sway_config_paths:
        detected_applications.append("Sway")
    if waybar_config_paths:
        detected_applications.append("Waybar")
    if kitty_config_paths:
        detected_applications.append("Kitty")
    if hyprland_config_paths:
        detected_applications.append("Hyprland")
    if hyprpaper_config_paths:
        detected_applications.append("Hyprpaper")
    if hyprlock_config_paths: # New condition for Hyprlock
        detected_applications.append("Hyprlock")

    all_possible_applications = ["Sway", "Waybar", "Kitty", "Hyprland", "Hyprpaper", "Hyprlock"] # Update all_possible_applications

    # Generate final report if not in debug mode
    generate_report(sway_features, waybar_modules, kitty_configs, hyprland_features, hyprpaper_features, hyprlock_config_paths, detected_applications, all_possible_applications, file_collector) # Pass hyprlock_config_paths

if __name__ == "__main__":
    # This part is for demonstration. In a real scenario, you'd call colorize_hyprland_config_file
    # with the actual path to your Hyprland config.
    # For now, let's assume a dummy file for testing.
    dummy_config_content = """
# This is a comment
set $mod Mod4
bindsym $mod+Shift+Return exec alacritty
bindsym $mod+Up workspace next
bindsym $mod+Down workspace prev
source ~/.config/sway/config.d/keybindings
exec_always systemctl --user import-environment DISPLAY WAYLAND_DISPLAY SWAYSOCK
bar {
    status_command i3status
    position top
}
gaps inner 10
client.focused #aabbcc
# Another comment
set $term alacritty
bindsym $mod+t exec $term
bindsym $mod+Shift+Q exec killall alacritty
bindsym $mod+Alt+L exec swaylock
bindsym $mod+CTRL+R exec systemctl restart sway
bindsym $mod+left movefocus left
bindsym $mod+right movefocus right
bindsym $mod+up movefocus up
bindsym $mod+down movefocus down
bindsym $mod+Mod4+F fullscreen
bindsym $mod+Page_Up workspace next
bindsym $mod+F1 exec firefox
set $mainMod SUPER
movetoworkspace 1
"""
    dummy_file_path = "/home/owner/gemini-projects/feature_ricing/sway_config.conf" # Still using old name for dummy
    with open(dummy_file_path, "w") as f:
        f.write(dummy_config_content.strip())

    main()