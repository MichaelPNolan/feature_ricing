import json
import re

def parse_waybar_config(config_path, sway_variables, waybar_style_colors):
    """
    Parses the Waybar configuration file and extracts features.

    Args:
        config_path: The path to the Waybar configuration file.
        sway_variables: A dictionary of variables from the Sway config.
        waybar_style_colors: A dictionary of colors extracted from waybar_style.css.

    Returns:
        A dictionary of categorized modules.
    """
    modules = {
        "modules-left": [],
        "modules-center": [],
        "modules-right": [],
    }
    if not config_path:
        return modules

    processed_modules = []
    with open(config_path, "r") as f:
        # Simple JSONC parser: remove comments and trailing commas
        lines = f.readlines()
        json_content = "".join(lines)
        json_content = re.sub(r'//.*', '', json_content)
        json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)
        json_content = re.sub(r',\s*([\}\]])', r'\1', json_content)

        try:
            config = json.loads(json_content)
            
            # Collect all potential module configuration keys
            module_config_keys = {k for k in config.keys() if k not in ["modules-left", "modules-center", "modules-right"]}

            for position in ["modules-left", "modules-center", "modules-right"]:
                if position in config:
                    for module_name in config[position]:
                        # Check if the module (or its non-asterisk version) has already been processed
                        if module_name in processed_modules:
                            continue
                        if "*" in module_name and module_name.replace("*", "") in processed_modules:
                            continue
                        
                        display_name = module_name
                        
                        # Check for custom configuration in config.jsonc
                        has_custom_config_in_jsonc = False
                        module_config = None
                        
                        # Try exact match
                        if module_name in module_config_keys and isinstance(config[module_name], dict):
                            has_custom_config_in_jsonc = True
                            module_config = config[module_name]
                        else:
                            # Try matching with instance identifiers (e.g., "cpu" matches "cpu#0")
                            for key in module_config_keys:
                                if key.startswith(module_name + "#") and isinstance(config[key], dict):
                                    has_custom_config_in_jsonc = True
                                    module_config = config[key]
                                    break
                        
                        colors_info = []
                        if has_custom_config_in_jsonc:
                            display_name += "*"
                            for color_type in ["foreground", "background"]:
                                if color_type in module_config:
                                    color_value = module_config[color_type]
                                    if color_value.startswith("$"):
                                        if color_value in sway_variables:
                                            hex_color, _ = sway_variables[color_value]
                                            colors_info.append(f"{color_type[0].upper()}:{hex_color}")
                                    else:
                                        colors_info.append(f"{color_type[0].upper()}:{color_value}")
                        
                        # Check for custom configuration in style.css
                        if module_name in waybar_style_colors:
                            style_colors = waybar_style_colors[module_name]
                            if "foreground" in style_colors and style_colors["foreground"]:
                                colors_info.append(f"F:{style_colors['foreground']}")
                            if "background" in style_colors and style_colors["background"]:
                                colors_info.append(f"B:{style_colors['background']}")
                            
                            if not has_custom_config_in_jsonc: # Only add asterisk if not already added from jsonc
                                display_name += "*"

                        if colors_info:
                            display_name += f" ({', '.join(colors_info)})"
                        elif has_custom_config_in_jsonc:
                            display_name += " (no style detected)"
                        elif module_name in waybar_style_colors:
                            display_name += " (style detected)"
                        else:
                            display_name += " (no style detected)"

                        modules[position].append(display_name)
                        processed_modules.append(module_name)
        except json.JSONDecodeError as e:
            print(f"Error parsing Waybar config: {e}")

    return modules
