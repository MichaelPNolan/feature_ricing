import argparse
from file_collector import FileCollector
from sway_parser import parse_sway_config
from waybar_parser import parse_waybar_config
from waybar_style_parser import parse_waybar_style
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

    # Generate final report if not in debug mode
    generate_report(sway_features, waybar_modules, file_collector)

if __name__ == "__main__":
    main()