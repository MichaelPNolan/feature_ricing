import re
import os

def parse_kitty_config(file_path):
    """
    Parses a Kitty configuration file (.conf).
    Extracts key-value pairs, ignoring comments and empty lines.
    """
    kitty_config = {}
    if not os.path.exists(file_path):
        return kitty_config

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Handle key-value pairs
            match = re.match(r'^\s*(\S+)\s+(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                kitty_config[key] = value
            else:
                # If it's not a key-value pair, just store the line as a generic setting
                # This might happen for settings that are just flags or single keywords
                kitty_config[line] = True # Store as True if it's just a keyword
    return kitty_config
