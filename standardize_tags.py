#!/usr/bin/env python3
"""
Script to standardize tags in TOML files across the tasks directory.

Standardization rules:
Round 1 (completed):
- string -> strings
- array -> collections
- arrays -> collections
- alog -> algo (typo fix)
- bits_operation -> bits-operation
- bits -> bits-operation
- hash_map -> hash-maps
- hashmap -> hash-maps
- algorithms -> algo

Round 2 (current):
- graph -> graphs
- graphs -> graphs (keep as-is)
- map -> hash_maps
- hash-maps -> hash_maps
- dict -> hash_maps
- set -> sets
- sets -> sets (keep as-is)
- date -> date_time
- date-time -> date_time
- prefix-scan -> prefix_scan
- two-pointers -> two_pointers
- bits-operation -> bits
- linear-scan -> linear_scan
- sliding_window -> sliding_window (keep as-is, already has underscore)
"""

import os
import re
from pathlib import Path

# Tag replacement mapping
TAG_REPLACEMENTS = {
    # Round 1 (already applied)
    "string": "strings",
    "array": "collections",
    "arrays": "collections",
    "alog": "algo",  # Typo fix
    "algorithms": "algo",
    # Round 2 (new changes)
    "graph": "graphs",
    "map": "hash_maps",
    "hash-maps": "hash_maps",
    "dict": "hash_maps",
    "set": "sets",
    "date": "date_time",
    "date-time": "date_time",
    "prefix-scan": "prefix_scan",
    "two-pointers": "two_pointers",
    "bits-operation": "bits",
    "linear-scan": "linear_scan",
}


def standardize_tags_in_line(line):
    """Standardize tags in a single line containing a tags declaration."""
    if not line.strip().startswith("tags"):
        return line

    # Extract the tags array
    match = re.search(r"tags\s*=\s*\[(.*?)\]", line)
    if not match:
        return line

    tags_content = match.group(1)

    # Parse individual tags
    tags = []
    for tag in re.findall(r'"([^"]+)"', tags_content):
        # Replace tag if it's in our mapping
        standardized_tag = TAG_REPLACEMENTS.get(tag, tag)
        tags.append(standardized_tag)

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    # Reconstruct the line with standardized tags
    tags_str = ", ".join(f'"{tag}"' for tag in unique_tags)

    # Preserve the original indentation
    indent_match = re.match(r"^(\s*)", line)
    indent = indent_match.group(1) if indent_match else ""

    return f"{indent}tags              = [{tags_str}]\n"


def process_toml_file(file_path):
    """Process a single TOML file to standardize its tags."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        new_lines = []

        for line in lines:
            new_line = standardize_tags_in_line(line)
            new_lines.append(new_line)
            if new_line != line:
                modified = True

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Find and process all TOML files in the tasks directory."""
    tasks_dir = Path("tasks")

    if not tasks_dir.exists():
        print(f"Error: {tasks_dir} directory not found")
        return

    # Find all TOML files
    toml_files = list(tasks_dir.rglob("*.toml"))

    print(f"Found {len(toml_files)} TOML files")
    print("Processing files...")

    modified_count = 0
    for toml_file in toml_files:
        if process_toml_file(toml_file):
            modified_count += 1
            print(f"  Modified: {toml_file}")

    print(f"\nDone! Modified {modified_count} out of {len(toml_files)} files")


if __name__ == "__main__":
    main()
