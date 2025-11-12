import re

def colorize_sway_config_line(line):
    COLOR_KEYWORD = "\033[96m"  # Cyan
    COLOR_VARIABLE = "\033[93m" # Yellow
    COLOR_KEY_NAME = "\033[92m" # Green
    COLOR_RESET = "\033[0m"

    # Define patterns and their corresponding colors
    patterns = [
        (re.compile(r'\b(set|bindsym|exec_always|exec|source|bar|gaps|client\.|workspace)\b'), COLOR_KEYWORD),
        (re.compile(r'\$[a-zA-Z0-9_]+'), COLOR_VARIABLE),
        # Key names: Mod4, Shift, Control, Alt, Up, Down, Left, Right, Return, Escape, Tab, Delete, Insert, Home, End, Page_Up, Page_Down, F1-F12
        # This pattern is designed to match specific key names and avoid over-coloring common words.
        (re.compile(r'\b(Mod4|Shift|Control|Alt|Up|Down|Left|Right|Return|Escape|Tab|Delete|Insert|Home|End|Page_Up|Page_Down|F[1-9]|F1[0-2])\b'), COLOR_KEY_NAME),
    ]

    # Collect all matches with their start, end, and color
    all_matches = []
    for pattern, color in patterns:
        for match in pattern.finditer(line):
            all_matches.append((match.start(), match.end(), color))

    # Sort matches by their start position
    all_matches.sort(key=lambda x: x[0])

    # Build the colored line, avoiding overlapping matches
    colored_parts = []
    last_idx = 0
    for start, end, color in all_matches:
        # If the current match starts before or at the last processed index, it's an overlap or already covered.
        # We prioritize earlier matches or longer matches if they overlap.
        # For simplicity, let's just skip if it's fully contained within a previous match.
        if start < last_idx:
            continue

        # Add the text before the current match (uncolored)
        colored_parts.append(line[last_idx:start])
        # Add the colored match
        colored_parts.append(color + line[start:end] + COLOR_RESET)
        last_idx = end

    # Add any remaining text after the last match
    colored_parts.append(line[last_idx:])

    return "".join(colored_parts)

def colorize_sway_config_file(file_path):
    try:
        with open(file_path, 'r') as f:
            for line in f:
                print(colorize_sway_config_line(line.rstrip('\n')))
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")

if __name__ == '__main__':
    # This part is for demonstration. In a real scenario, you'd call colorize_sway_config_file
    # with the actual path to your Sway config.
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
"""
    dummy_file_path = "/home/owner/gemini-projects/feature_ricing/sway_config.conf"
    with open(dummy_file_path, "w") as f:
        f.write(dummy_config_content.strip())

    print(f"--- Colorizing {dummy_file_path} ---")
    colorize_sway_config_file(dummy_file_path)
    print(f"--- End of colorization ---")
