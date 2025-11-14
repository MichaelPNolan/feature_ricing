import re

# Keywords from sway_vim_syntax.vim
vim_keywords = [
    "set", "bindsym", "bindcode", "exec", "workspace", "output", "mode", "for_window",
    "floating_modifier", "default_border", "gaps", "bar", "font", "include", "input",
    "client.focused", "client.focused_inactive", "client.unfocused", "client.urgent",
    "client.placeholder", "client.background",
    "Mod1", "Mod4", "Shift", "Control", "Alt", "Super",
    "Return", "Tab", "Escape", "BackSpace", "Delete", "Insert", "Home", "End", "PageUp", "PageDown",
    "Up", "Down", "Left", "Right", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
    "on", "off", "yes", "no", "enabled", "disabled"
]

# Keywords from sway_man.txt (sway(1))
man1_keywords = [
    "-h", "--help", "-c", "--config", "-C", "--validate", "-d", "--debug", "-v", "--version",
    "-V", "--verbose", "--get-socketpath",
    "swaymsg", "i3-msg", "i3",
    "SWAYSOCK", "XKB_DEFAULT_RULES", "XKB_DEFAULT_MODEL", "XKB_DEFAULT_LAYOUT",
    "XKB_DEFAULT_VARIANT", "XKB_DEFAULT_OPTIONS", "DISPLAY", "I3SOCK",
    "WAYLAND_DISPLAY", "XCURSOR_SIZE", "XCURSOR_THEME"
]

# Keywords from sway_man_5.txt (sway(5))
man5_keywords = [
    "bar", "default_orientation", "include", "swaybg_command", "swaynag_command",
    "workspace_layout", "xwayland", "assign", "bindsym", "bindcode", "bindswitch",
    "bindgesture", "client.background", "default_border", "default_floating_border",
    "exec", "exec_always", "floating_maximum_size", "floating_minimum_size",
    "floating_modifier", "focus_follows_mouse", "focus_on_window_activation",
    "focus_wrapping", "font", "force_display_urgency_hint", "titlebar_border_thickness",
    "titlebar_padding", "for_window", "gaps", "hide_edge_borders", "input", "seat",
    "kill", "smart_borders", "smart_gaps", "mark", "mode", "mouse_warping", "no_focus",
    "output", "popup_during_fullscreen", "primary_selection", "set", "show_marks",
    "opacity", "tiling_drag", "tiling_drag_threshold", "title_align", "unbindswitch",
    "unbindgesture", "unbindsym", "unbindcode", "unmark", "urgent", "workspace",
    "workspace_auto_back_and_forth",
    # Arguments/Values
    "horizontal", "vertical", "auto", "default", "stacking", "tabbed", "enable", "disable",
    "force", "none", "normal", "csd", "pixel", "toggle", "exit", "floating", "focus",
    "up", "right", "down", "left", "prev", "next", "sibling", "child", "parent", "tiling",
    "mode_toggle", "fullscreen", "global", "inner", "outer", "top", "bottom", "all",
    "current", "set", "plus", "minus", "open", "visible", "splith", "splitv", "off",
    "yes", "no", "absolute", "position", "center", "cursor", "mouse", "pointer",
    "container", "window", "number", "prev_on_output", "next_on_output", "back_and_forth",
    "scratchpad", "reload", "rename", "shrink", "grow", "width", "height", "show",
    "shortcuts_inhibitor", "split", "v", "h", "n", "t", "splitt", "sticky", "swap", "id",
    "con_id", "title_format", "%title", "%app_id", "%class", "%instance", "%shell",
    "%sandbox_engine", "%sandbox_app_id", "%sandbox_instance_id", "--whole-window",
    "--border", "--exclude-titlebar", "--release", "--locked", "--to-code", "--input-device",
    "--no-warn", "--no-repeat", "--inhibited", "Group<1-4>+", "Lock", "Mod2", "Mod3", "Mod5",
    "Ctrl", "Alt", "Super", "button[1-9]", "BTN_LEFT", "BTN_RIGHT", "lid", "tablet",
    "--reload", "--exact", "hold", "pinch", "swipe", "inward", "outward", "clockwise",
    "counterclockwise", "background", "text", "indicator", "child_border", "smart", "urgent",
    "pango:", "force_display_urgency_hint", "titlebar_border_thickness", "titlebar_padding",
    "no_focus", "popup_during_fullscreen", "ignore", "leave_fullscreen", "primary_selection",
    "$", "show_marks", "opacity", "tiling_drag", "tiling_drag_threshold", "title_align",
    "unbindswitch", "unbindgesture", "unbindsym", "unbindcode", "unmark", "allow", "deny",
    "workspace_auto_back_and_forth",
    # CRITERIA attributes
    "all", "app_id", "class", "con_id", "con_mark", "floating", "id", "instance", "pid",
    "shell", "tiling", "title", "urgent", "window_role", "window_type", "workspace",
    "sandbox_engine", "sandbox_app_id", "sandbox_instance_id", "__focused__"
]

all_keywords = sorted(list(set(vim_keywords + man1_keywords + man5_keywords)))

# Filter out keywords that are just single characters or very short,
# unless they are clearly commands or options (e.g., 'h', 'v', 't', '$')
# This is a heuristic to reduce noise.
filtered_keywords = []
for kw in all_keywords:
    if len(kw) > 1 or kw in ["$", "h", "v", "t", "n"]:
        filtered_keywords.append(kw)

# Format for app_keyword_defs.conf
keyword_string = ", ".join(filtered_keywords)

# Read the existing content of app_keyword_defs.conf
with open("app_keyword_defs.conf", "r") as f:
    content = f.read()

# Find the [SWAY] section and replace its KEYWORD line
sway_section_start = content.find("[SWAY]")
if sway_section_start != -1:
    keyword_line_start = content.find("KEYWORD =", sway_section_start)
    if keyword_line_start != -1:
        keyword_line_end = content.find("\n", keyword_line_start)
        if keyword_line_end == -1:
            keyword_line_end = len(content) # If KEYWORD is the last line

        old_keyword_line = content[keyword_line_start:keyword_line_end]
        new_keyword_line = f"KEYWORD = {keyword_string}"
        content = content.replace(old_keyword_line, new_keyword_line)
    else:
        print("Error: 'KEYWORD =' line not found in [SWAY] section.")
else:
    print("Error: [SWAY] section not found.")

# Write the modified content back to app_keyword_defs.conf
with open("app_keyword_defs.conf", "w") as f:
    f.write(content)

print("Sway keywords updated in app_keyword_defs.conf")
