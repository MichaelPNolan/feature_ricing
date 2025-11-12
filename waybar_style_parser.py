import re
import os
import json

def parse_colors_waybar(colors_waybar_path):
    """
    Parses the colors-waybar.css file and extracts @define-color variables.

    Args:
        colors_waybar_path: The path to the colors-waybar.css file.

    Returns:
        A dictionary mapping @define-color names to their hex codes.
    """
    colors_waybar_variables = {}
    if not colors_waybar_path or not os.path.exists(colors_waybar_path):
        return colors_waybar_variables

    with open(colors_waybar_path, "r") as f:
        content = f.read()
        # Regex to find @define-color variables
        define_color_pattern = re.compile(r'@define-color\s+([a-zA-Z0-9_-]+)\s+(#[a-fA-F0-9]{6});')
        for match in define_color_pattern.finditer(content):
            var_name = match.group(1)
            hex_code = match.group(2)
            colors_waybar_variables[var_name] = hex_code
    return colors_waybar_variables

def resolve_color_value(color_value, colors_waybar_vars, sway_variables):
    """Resolves a color value (hex, @colorX, or @define-color) to a hex code."""
    if color_value is None:
        return None
    if color_value.startswith("@color"):
        var_name = color_value[1:]
        if var_name in colors_waybar_vars:
            return colors_waybar_vars[var_name]
        else:
            sway_var_name = "$" + var_name
            if sway_var_name in sway_variables:
                return sway_variables[sway_var_name][0] # Assuming [0] is the hex
            else:
                return color_value # Keep @colorX if not resolved
    elif color_value.startswith("@"):
        var_name = color_value[1:]
        if var_name in colors_waybar_vars:
            return colors_waybar_vars[var_name]
        else:
            return color_value # Keep @define-color if not resolved
    else:
        return color_value # Already a hex code

def parse_waybar_style(style_path, sway_variables, colors_waybar_path, file_collector, debug_mode=False):
    """
    Parses the Waybar style.css file and extracts module-specific colors,
    considering global Waybar defaults.

    Args:
        style_path: The path to the Waybar style.css file.
        sway_variables: A dictionary of variables from the Sway config.
        colors_waybar_path: The path to the colors-waybar.css file.
        file_collector: The FileCollector instance to record file relationships.
        debug_mode: A boolean to enable debug output.

    Returns:
        A dictionary mapping module names to their foreground and background hex codes or @colorX names.
    """
    module_colors = {}
    
    colors_waybar_vars = parse_colors_waybar(colors_waybar_path)

    if colors_waybar_path and os.path.exists(colors_waybar_path):
        file_collector.add_sourced_relationship(style_path, colors_waybar_path)

    if not style_path or not os.path.exists(style_path):
        return module_colors

    with open(style_path, "r") as f:
        content = f.read()

        # 1. Extract global Waybar defaults
        fg_color_default = None
        bg_color_default = None
        waybar_global_match = re.search(r'#waybar\s*\{([^}]+)\}', content)
        if waybar_global_match:
            global_styles = waybar_global_match.group(1)
            
            # Use negative lookbehind for color:
            fg_matches = re.findall(r'(?<!background-)color:\s*(#[a-fA-F0-9]{6}|@color[0-9]+|@([a-zA-Z0-9_-]+));', global_styles)
            if fg_matches:
                fg_color_default = resolve_color_value(fg_matches[-1][0], colors_waybar_vars, sway_variables)
            
            bg_matches = re.findall(r'background-color:\s*(#[a-fA-F0-9]{6}|@color[0-9]+|@([a-zA-Z0-9_-]+));', global_styles)
            if bg_matches:
                bg_color_default = resolve_color_value(bg_matches[-1][0], colors_waybar_vars, sway_variables)
        
        # 2. Iterate through module-specific rules
        module_rule_pattern = re.compile(r'#([a-zA-Z0-9_/-]+)\s*\{([^}]+)\}')
        
        for module_match in module_rule_pattern.finditer(content):
            module_id = module_match.group(1)
            styles = module_match.group(2)
            
            # Initialize with global defaults
            fg_color = fg_color_default
            bg_color = bg_color_default

            # Extract foreground color - find all and take the last one (overrides default)
            # Use negative lookbehind for color:
            fg_matches = re.findall(r'((?<!background-)color:\s*(#[a-fA-F0-9]{6}|@color[0-9]+|@([a-zA-Z0-9_-]+));)', styles)
            if fg_matches:
                full_directive, color_value, _ = fg_matches[-1] # Corrected unpacking
                resolved_fg_color = resolve_color_value(color_value, colors_waybar_vars, sway_variables)
                fg_color = resolved_fg_color
            
            # Extract background color - find all and take the last one (overrides default)
            bg_matches = re.findall(r'(background-color:\s*(#[a-fA-F0-9]{6}|@color[0-9]+|@([a-zA-Z0-9_-]+));)', styles)
            if bg_matches:
                full_directive, color_value, _ = bg_matches[-1] # Corrected unpacking
                resolved_bg_color = resolve_color_value(color_value, colors_waybar_vars, sway_variables)
                bg_color = resolved_bg_color
            
            if fg_color or bg_color:
                module_colors[module_id] = {"foreground": fg_color, "background": bg_color}

    return module_colors
