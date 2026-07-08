#!/usr/bin/env python3
"""
Check that task scoring metadata stays within level-specific maximums.
"""

import os
import sys
from typing import Dict, List, Tuple

import tomli
from termcolor import colored


LIMITS: Dict[str, Dict[str, int]] = {
    "elementary": {"base_score": 50, "time_to_solve_sec": 150},
    "easy": {"base_score": 100, "time_to_solve_sec": 300},
    "medium": {"base_score": 150, "time_to_solve_sec": 450},
    "hard": {"base_score": 250, "time_to_solve_sec": 900},
}


def find_toml_files(directory: str) -> List[str]:
    """Recursively find all .toml files in directory."""
    if not os.path.exists(directory):
        return []

    toml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".toml"):
                toml_files.append(os.path.join(root, file))

    return toml_files


def check_file(toml_path: str, base_dir: str) -> List[str]:
    """Return validation errors for one task file."""
    try:
        with open(toml_path, "rb") as f:
            data = tomli.load(f)
    except Exception as e:
        return [f"Failed to parse TOML: {str(e)}"]

    level = data.get("level")
    if level not in LIMITS:
        return [f"unknown or missing level: {level!r}"]

    errors = []
    for field, maximum in LIMITS[level].items():
        value = data.get(field)
        if value is None:
            errors.append(f"missing {field}")
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{field} must be numeric, got {type(value).__name__}")
            continue
        if value > maximum:
            errors.append(f"{field}={value} exceeds max {maximum} for {level}")

    return errors


def main():
    """Main entry point."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    paths = sys.argv[1:] or ["tasks", "private"]

    toml_files = []
    for path in paths:
        full_path = path if os.path.isabs(path) else os.path.join(base_dir, path)
        if os.path.isfile(full_path) and full_path.endswith(".toml"):
            toml_files.append(full_path)
        else:
            toml_files.extend(find_toml_files(full_path))

    if not toml_files:
        print(colored("WARNING: No TOML files found", "yellow"))
        sys.exit(0)

    print(colored("Checking task score and time limits...", "cyan"))
    print(f"Found {colored(str(len(toml_files)), 'cyan')} task files\n")

    errors: List[Tuple[str, str]] = []
    for toml_path in sorted(toml_files):
        rel_path = os.path.relpath(toml_path, base_dir)
        for error in check_file(toml_path, base_dir):
            errors.append((rel_path, f"{rel_path}: {error}"))

    if not errors:
        print(colored("All task score and time limits are valid!", "green"))
        return

    print(colored("TASK LIMIT VIOLATIONS FOUND:", "red", attrs=["bold"]))
    print()
    for _, error in errors:
        print(colored(f"  - {error}", "yellow"))

    print()
    print(colored("=" * 70, "blue"))
    print(
        colored(
            f"Summary: Found {len(errors)} task limit violation(s)",
            "red",
            attrs=["bold"],
        )
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
