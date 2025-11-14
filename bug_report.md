# Bug Report: Variable Names Not Colorized

## Description
Variable names (e.g., `$mod`, `$ws1`) in Sway configuration output are not being colorized, despite changes made to `colorize_app_keywords.py` and `app_keyword_defs.conf` to enable this feature.

## Steps to Reproduce
1. Run `python3 main.py`.
2. Observe the "--- Sway Configuration ---" section in the output.
3. Note that variable names (e.g., `$mod` in `bindsym $mod+1 workspace $ws1`) are displayed in the default terminal color, not the expected yellow (`COLOR_VARIABLE`).

## Expected Behavior
Variable names starting with `$` should be colorized with `COLOR_VARIABLE` (yellow).

## Actual Behavior
Variable names are displayed in the default terminal color.

## Relevant Files and Sections
*   `colorize_app_keywords.py`:
    *   `_compile_patterns` method, specifically the `VARIABLE` pattern compilation.
    *   `COLOR_VARIABLE` definition.
*   `app_keyword_defs.conf`:
    *   `[SWAY]` section, `VARIABLE` entry.
*   `sway_parser.py`:
    *   `parse_sway_config` and `_parse_sway_file` for variable extraction.
*   `reporter.py`:
    *   `generate_report` for passing dynamic variables to `AppKeywordColorizer`.
*   `main.py`:
    *   Collection of `sway_defined_variables` and passing them to `generate_report`.

## Debugging Notes
*   The `VARIABLE` regex in `app_keyword_defs.conf` is `$[a-zA-Z0-9_]+`.
*   `colorize_app_keywords.py` has been modified to:
    *   Process `VARIABLE` patterns first.
    *   Escape the `$` character in variable names before compiling the regex pattern.
*   The `sway_parser.py` extracts variable names correctly.
*   The `reporter.py` and `main.py` pass these dynamic variables to the `AppKeywordColorizer`.

The issue likely lies in the regex matching logic within `colorize_app_keywords.py` or a conflict with other patterns.