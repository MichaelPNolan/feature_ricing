import os
import re
from collections import defaultdict

class FileMetadata:
    def __init__(self, path, file_type="other", is_active=False):
        self.path = path
        self.type = file_type
        self.is_active = is_active
        self.sourced_by = set()  # Files that source/include this file
        self.sources = set()     # Files that this file sources/includes

    def add_sourced_by(self, file_path):
        self.sourced_by.add(file_path)

    def add_source(self, file_path):
        self.sources.add(file_path)

    def __repr__(self):
        return f"FileMetadata(path='{self.path}', type='{self.type}', active={self.is_active}, sourced_by={len(self.sourced_by)}, sources={len(self.sources)})"

class FileCollector:
    def __init__(self):
        self.files = {} # Stores FileMetadata objects, keyed by path
        self.wal_detected = False

    def _get_or_create_file_metadata(self, file_path, file_type="other", is_active=False):
        if file_path not in self.files:
            self.files[file_path] = FileMetadata(file_path, file_type, is_active)
        else:
            # Update type and active status if more specific information is provided
            if file_type != "other" and self.files[file_path].type == "other":
                self.files[file_path].type = file_type
            if is_active:
                self.files[file_path].is_active = True
        return self.files[file_path]

    def add_active_config(self, file_path, file_type="active_config"):
        metadata = self._get_or_create_file_metadata(file_path, file_type, is_active=True)
        metadata.type = file_type # Ensure type is set correctly for active configs

    def add_inactive_config(self, file_path, file_type="inactive_config"):
        metadata = self._get_or_create_file_metadata(file_path, file_type, is_active=False)
        metadata.type = file_type # Ensure type is set correctly for inactive configs

    def add_script(self, file_path):
        self._get_or_create_file_metadata(file_path, "script")

    def add_design_file(self, file_path):
        self._get_or_create_file_metadata(file_path, "design_file")

    def add_wal_generated_file(self, file_path):
        self._get_or_create_file_metadata(file_path, "wal_generated")

    def add_sourced_relationship(self, source_file_path, sourced_file_path):
        source_metadata = self._get_or_create_file_metadata(source_file_path)
        sourced_metadata = self._get_or_create_file_metadata(sourced_file_path)

        source_metadata.add_source(sourced_file_path)
        sourced_metadata.add_sourced_by(source_file_path)
        
        # If a sourced file was initially 'other', and it's sourced by an active config,
        # it's likely an active part of the configuration.
        if source_metadata.is_active and sourced_metadata.type == "other":
            sourced_metadata.type = "sourced_config"
            sourced_metadata.is_active = True # Mark as active if sourced by an active config

    def get_files(self):
        return {k: sorted(list(v)) for k, v in self.files.items()}

    def find_sway_configs(self):
        # Prioritize ~/.config/sway/config as the primary active config
        user_config_path = os.path.expanduser("~/.config/sway/config")
        active_sway_config_found = False

        if os.path.exists(user_config_path):
            resolved_path = os.path.realpath(user_config_path)
            self.add_active_config(resolved_path, file_type="sway_config")
            active_sway_config_found = True
        
        # Other potential Sway config paths (will be marked inactive if they exist)
        potential_sway_configs = [
            "/etc/sway/config",
            os.path.join(os.getcwd(), "config_link/sway/config") # Assuming a symlink for testing
        ]

        for path in potential_sway_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                # Only mark as inactive if it's not the primary active config
                if resolved_path != os.path.realpath(user_config_path):
                    self.add_inactive_config(resolved_path, file_type="sway_config")
        
        # Also check for ~/.cache/wal/colors-sway
        wal_colors_sway = os.path.expanduser("~/.cache/wal/colors-sway")
        if os.path.exists(wal_colors_sway):
            self.add_wal_generated_file(wal_colors_sway)
            # Its active status will be determined if it's sourced by the active sway config.
        
        return [f.path for f in self.files.values() if f.type == "sway_config" and f.is_active]

    def find_waybar_configs(self):
        potential_waybar_configs = [
            os.path.expanduser("~/.config/waybar/config"),
            os.path.expanduser("~/.config/waybar/config.jsonc"),
            os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "waybar/config"),
            os.path.expanduser("~/waybar/config"),
            "/etc/xdg/waybar/config",
            os.path.join(os.getcwd(), "config_link/waybar/config"), # Assuming a symlink for testing
            os.path.join(os.getcwd(), "config_link/waybar/config.jsonc") # Assuming a symlink for testing
        ]

        found_active = False
        for path in potential_waybar_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                if not found_active:
                    self.add_active_config(resolved_path, file_type="waybar_config")
                    found_active = True
                else:
                    self.add_inactive_config(resolved_path, file_type="waybar_config")
        
        return [f.path for f in self.files.values() if f.type == "waybar_config" and f.is_active]

    def find_waybar_styles(self):
        potential_waybar_styles = [
            os.path.expanduser("~/.config/waybar/style.css"),
            os.path.join(os.getcwd(), "config_link/waybar/style.css") # Assuming a symlink for testing
        ]

        for path in potential_waybar_styles:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                self.add_design_file(resolved_path) # Add to design files
                # Mark as active if it's the primary style.css
                self.files[resolved_path].is_active = True
                self.files[resolved_path].type = "waybar_style"
                break # Only take the first found style.css
        
        return [f.path for f in self.files.values() if f.type == "waybar_style" and f.is_active]

    def find_kitty_configs(self):
        potential_kitty_configs = [
            os.path.expanduser("~/.config/kitty/kitty.conf"),
            os.path.join(os.getcwd(), "config_link/kitty/kitty.conf")
        ]

        found_active = False
        for path in potential_kitty_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                if not found_active:
                    self.add_active_config(resolved_path, file_type="kitty_config")
                    found_active = True
                else:
                    self.add_inactive_config(resolved_path, file_type="kitty_config")
        
        return [f.path for f in self.files.values() if f.type == "kitty_config" and f.is_active]

    def find_hyprland_configs(self):
        potential_hyprland_configs = [
            os.path.expanduser("~/.config/hypr/hyprland.conf"),
            os.path.join(os.getcwd(), "config_link/hypr/hyprland.conf")
        ]

        found_active = False
        for path in potential_hyprland_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                if not found_active:
                    self.add_active_config(resolved_path, file_type="hyprland_config")
                    found_active = True
                else:
                    self.add_inactive_config(resolved_path, file_type="hyprland_config")
        
        return [f.path for f in self.files.values() if f.type == "hyprland_config" and f.is_active]

    def find_hyprpaper_configs(self):
        potential_hyprpaper_configs = [
            os.path.expanduser("~/.config/hypr/hyprpaper.conf"),
            os.path.join(os.getcwd(), "config_link/hypr/hyprpaper.conf")
        ]

        found_active = False
        for path in potential_hyprpaper_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                if not found_active:
                    self.add_active_config(resolved_path, file_type="hyprpaper_config")
                    found_active = True
                else:
                    self.add_inactive_config(resolved_path, file_type="hyprpaper_config")
        
        return [f.path for f in self.files.values() if f.type == "hyprpaper_config" and f.is_active]

    def find_hyprlock_configs(self):
        potential_hyprlock_configs = [
            os.path.expanduser("~/.config/hypr/hyprlock.conf"),
            os.path.join(os.getcwd(), "config_link/hypr/hyprlock.conf")
        ]

        found_active = False
        for path in potential_hyprlock_configs:
            if os.path.exists(path):
                resolved_path = os.path.realpath(path)
                if not found_active:
                    self.add_active_config(resolved_path, file_type="hyprlock_config")
                    found_active = True
                else:
                    self.add_inactive_config(resolved_path, file_type="hyprlock_config")
        
        return [f.path for f in self.files.values() if f.type == "hyprlock_config" and f.is_active]

    def find_colors_waybar_css(self):
        colors_waybar_path = None
        potential_colors_waybar = [
            os.path.expanduser("~/.cache/wal/colors-waybar.css"),
            # os.path.join(os.getcwd(), "colors-waybar.css") # Removed as per user request
        ]

        for path in potential_colors_waybar:
            if os.path.exists(path):
                colors_waybar_path = os.path.realpath(path)
                self.add_wal_generated_file(colors_waybar_path) # Mark as wal_generated
                break
        return colors_waybar_path