#!/usr/bin/env python3
"""
Check uniqueness of task names across tasks/ and private/ directories.
Task names are checked case-insensitively to prevent confusion.
Also verifies that file names match the 'name' field in each TOML file.
"""

import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

import tomli
from termcolor import colored


def find_toml_files(directory: str) -> List[str]:
    """
    Recursively find all .toml files in directory.
    Returns list of absolute paths.
    Returns empty list if directory doesn't exist.
    """
    if not os.path.exists(directory):
        return []

    toml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".toml"):
                toml_files.append(os.path.join(root, file))

    return toml_files


def extract_task_names(
    toml_files: List[str], base_dir: str
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str, str]]]:
    """
    Extract task names from TOML files.
    Returns:
        - mapping of lowercase_name -> [file_paths]
        - list of mismatches: [(file_path, file_name, toml_name), ...]
    Raises ValueError if any file is missing 'name' field.
    """
    name_to_files = defaultdict(list)
    mismatches = []

    for toml_path in toml_files:
        rel_path = os.path.relpath(toml_path, base_dir)
        file_name = os.path.basename(toml_path).replace(".toml", "")

        # Parse TOML file
        try:
            with open(toml_path, "rb") as f:
                data = tomli.load(f)
        except Exception as e:
            print(colored(f"ERROR: Failed to parse '{rel_path}': {str(e)}", "red"))
            sys.exit(1)

        # Extract name field
        name = data.get("name")
        if not name:
            print(
                colored(
                    f"ERROR: File '{rel_path}' is missing required 'name' field", "red"
                )
            )
            sys.exit(1)

        # Check if file name matches the name field
        if file_name != name:
            mismatches.append((rel_path, file_name, name))

        # Store with lowercase key for case-insensitive comparison
        lowercase_name = name.lower()
        name_to_files[lowercase_name].append(toml_path)

    return dict(name_to_files), mismatches


def check_uniqueness(
    name_to_files: Dict[str, List[str]], base_dir: str
) -> Tuple[bool, int, int]:
    """
    Check for duplicate task names and print report.
    Returns (is_unique, total_files, duplicate_count)
    """
    total_files = sum(len(files) for files in name_to_files.values())

    print(colored("Checking task names for uniqueness...", "cyan"))
    print(
        f"Found {colored(str(total_files), 'cyan')} task files across tasks/ and private/\n"
    )

    # Find duplicates (names appearing in more than one file)
    duplicates = {
        name: files for name, files in name_to_files.items() if len(files) > 1
    }

    if not duplicates:
        print(colored("All task names are unique!", "green"))
        return (True, total_files, 0)

    # Report duplicates
    print(colored("DUPLICATE TASK NAMES FOUND:", "red", attrs=["bold"]))
    print()

    for name, files in sorted(duplicates.items()):
        print(colored(f"Task name: '{name}' appears in {len(files)} files:", "yellow"))
        for file_path in files:
            rel_path = os.path.relpath(file_path, base_dir)
            print(f"  - {rel_path}")
        print()

    # Print summary
    duplicate_file_count = sum(len(files) for files in duplicates.values())
    print(colored("=" * 70, "blue"))
    print(
        colored(
            f"Summary: Found {len(duplicates)} duplicate task name(s) across {duplicate_file_count} files",
            "red",
            attrs=["bold"],
        )
    )

    return (False, total_files, len(duplicates))


def check_filename_matches(mismatches: List[Tuple[str, str, str]]) -> bool:
    """
    Check for file name / TOML name mismatches and print report.
    Returns True if all match, False otherwise.
    """
    if not mismatches:
        print(colored("All file names match their TOML 'name' field!", "green"))
        return True

    print(colored("FILE NAME MISMATCHES FOUND:", "red", attrs=["bold"]))
    print()

    for rel_path, file_name, toml_name in sorted(mismatches):
        print(colored(f"File: {rel_path}", "yellow"))
        print(f"  file name: '{file_name}'")
        print(f"  toml name: '{toml_name}'")
        print()

    print(colored("=" * 70, "blue"))
    print(
        colored(
            f"Summary: Found {len(mismatches)} file name mismatch(es)",
            "red",
            attrs=["bold"],
        )
    )

    return False


def main():
    """Main entry point."""
    # Get base directory (project root)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths to check
    tasks_dir = os.path.join(base_dir, "tasks")
    private_dir = os.path.join(base_dir, "private")

    # Find all TOML files
    toml_files = []
    toml_files.extend(find_toml_files(tasks_dir))
    toml_files.extend(find_toml_files(private_dir))

    if not toml_files:
        print(colored("WARNING: No TOML files found in tasks/ or private/", "yellow"))
        sys.exit(0)

    # Extract task names (case-insensitive) and check for file name mismatches
    try:
        name_to_files, mismatches = extract_task_names(toml_files, base_dir)
    except Exception as e:
        print(colored(f"ERROR: {str(e)}", "red"))
        sys.exit(1)

    # Check for duplicates
    is_unique, total_files, duplicate_count = check_uniqueness(name_to_files, base_dir)

    # Check for file name mismatches
    print()
    names_match = check_filename_matches(mismatches)

    # Exit with appropriate code
    sys.exit(0 if (is_unique and names_match) else 1)


if __name__ == "__main__":
    main()
