import re
import os

def parse_hyprpaper_config(config_path, file_collector):
    """
    Parses the hyprpaper configuration file and extracts features.

    Args:
        config_path: The path to the hyprpaper configuration file.
        file_collector: A FileCollector instance (for adding sourced files, etc.)

    Returns:
        A dictionary of categorized features.
    """
    features = {
        "Settings": [],
        "Other": [],
    }

    if not os.path.exists(config_path):
        print(f"Warning: hyprpaper config file not found: {config_path}")
        return features

    try:
        with open(config_path, "r") as f:
            for line in f:
                original_line = line.rstrip('\n')
                stripped_line = line.strip()

                if not stripped_line or stripped_line.startswith("#"):
                    features["Settings"].append((original_line, config_path))
                    continue

                # Handle 'preload = /path/to/image.jpg' or 'wallpaper = monitor, /path/to/image.jpg'
                if stripped_line.startswith(("preload", "wallpaper")):
                    features["Settings"].append((original_line, config_path))
                elif stripped_line.startswith("source"):
                    # Handle sourced files within hyprpaper.conf if any
                    source_match = re.match(r'^\s*source\s*=\s*(.*)$', stripped_line)
                    if source_match:
                        sourced_path = source_match.group(1).strip()
                        expanded_sourced_path = os.path.expanduser(sourced_path)
                        if not os.path.isabs(expanded_sourced_path):
                            sourced_path = os.path.join(os.path.dirname(config_path), expanded_sourced_path)
                        else:
                            sourced_path = expanded_sourced_path
                        
                        if file_collector:
                            file_collector.add_sourced_relationship(config_path, sourced_path)
                        # Recursively parse sourced hyprpaper configs if needed, or just add to files
                        # For now, just add as sourced relationship
                        features["Settings"].append((original_line, config_path))
                else:
                    features["Other"].append((original_line, config_path))

    except Exception as e:
        print(f"Error parsing hyprpaper config file {config_path}: {e}")

    return features
