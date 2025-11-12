import os

file_path = "/home/owner/gemini-projects/feature_ricing/reporter.py"
target_line = "    print() # Add newline after the last 40-char line"
insertion_line_number = -1
in_waybar_modules_section = False

with open(file_path, "r") as f:
    for i, line in enumerate(f):
        if "--- Waybar Modules ---" in line:
            in_waybar_modules_section = True
        
        if in_waybar_modules_section and target_line in line:
            # Check if the next line is "[Files Overview]" to confirm it's the correct insertion point
            # This is a heuristic to avoid inserting in the wrong place if the target_line appears elsewhere
            # For now, let's assume the first match after "--- Waybar Modules ---" is correct.
            insertion_line_number = i + 1 # Insert after this line
            break

if insertion_line_number != -1:
    print(f"Insertion point found at line: {insertion_line_number}")
else:
    print("Error: Could not find the insertion point.")
