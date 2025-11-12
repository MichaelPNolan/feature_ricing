import os

def find_config_files(file_collector):
    """
    Finds the configuration files for Sway and Waybar.

    Args:
        file_collector: A FileCollector instance.

    Returns:
        A dictionary with the paths to the active configuration files.
    """
    active_configs = {
        "sway": None,
        "waybar": None,
        "waybar_style": None,
        "colors_waybar": None,
    }

    # Base path for linked config files
    linked_config_base = os.path.join(os.getcwd(), "config_link")

    # Find Sway config file
    sway_locations = [
        os.path.join(linked_config_base, "sway/config"),
        os.path.expanduser("~/.sway/config"), # Original location for inactive tracking
        os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "sway/config"), # Original location for inactive tracking
        os.path.expanduser("~/.i3/config"), # Original location for inactive tracking
        os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "i3/config"), # Original location for inactive tracking
        "/etc/sway/config", # Original location for inactive tracking
        "/etc/i3/config", # Original location for inactive tracking
    ]
    found_sway = False
    for loc in sway_locations:
        if os.path.exists(loc):
            if not found_sway: # Prioritize the first found config
                active_configs["sway"] = loc
                file_collector.add_active_config(loc)
                found_sway = True
            else:
                file_collector.add_inactive_config(loc)

    # Find Waybar config file
    waybar_locations = [
        os.path.join(linked_config_base, "waybar/config.jsonc"),
        os.path.join(linked_config_base, "waybar/config"),
        os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "waybar/config.jsonc"), # Original location for inactive tracking
        os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "waybar/config"), # Original location for inactive tracking
    ]
    found_waybar = False
    for loc in waybar_locations:
        if os.path.exists(loc):
            if not found_waybar: # Prioritize the first found config
                active_configs["waybar"] = loc
                file_collector.add_active_config(loc)
                found_waybar = True
            else:
                file_collector.add_inactive_config(loc)

    # Find Waybar style file
    waybar_style_location = os.path.join(linked_config_base, "waybar/style.css")
    if os.path.exists(waybar_style_location):
        active_configs["waybar_style"] = waybar_style_location
        file_collector.add_design_file(waybar_style_location)
    else: # Fallback to original location for inactive tracking
        waybar_style_location = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "waybar/style.css")
        if os.path.exists(waybar_style_location):
            file_collector.add_inactive_config(waybar_style_location)

    # Find colors-waybar.css
    colors_waybar_locations = [
        os.path.join(os.path.expanduser("~/.cache/wal/"), "colors-waybar.css"), # Explicitly look in ~/.cache/wal/
        os.path.join(linked_config_base, "waybar/colors-waybar.css"),
        os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "waybar/colors-waybar.css"),
        os.path.join(os.getcwd(), "colors-waybar.css"), # Temporary location for development
    ]
    found_colors_waybar = False
    for loc in colors_waybar_locations:
        if os.path.exists(loc):
            if not found_colors_waybar:
                active_configs["colors_waybar"] = loc
                file_collector.add_design_file(loc)
                found_colors_waybar = True
            else:
                file_collector.add_inactive_config(loc)

    return active_configs
