#!/usr/bin/env python3
"""
Reorganize tasks according to the project structure rule:
- Task path should always be: /tasks/<level>/<tags[0]>/<name>.toml
"""

import os
import subprocess
import tomllib
from pathlib import Path
from collections import defaultdict


def read_task_tags(task_path):
    """Read tags from a task file."""
    try:
        with open(task_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("tags", [])
    except Exception as e:
        print(f"Error reading {task_path}: {e}")
        return None


def get_expected_path(task_path, base_dir):
    """Calculate the expected path for a task based on its tags."""
    # Get relative path from base_dir
    rel_path = task_path.relative_to(base_dir)
    parts = rel_path.parts

    # Extract level (elementary, easy, medium, hard)
    level = parts[0]

    # Get the task filename
    filename = parts[-1]

    # Read tags
    tags = read_task_tags(task_path)
    if not tags or len(tags) == 0:
        print(f"Warning: No tags found for {task_path}")
        return None

    # Expected path: tasks/<level>/<tags[0]>/<filename>
    first_tag = tags[0]
    expected_path = base_dir / level / first_tag / filename

    return expected_path


def main():
    base_dir = Path("/Users/v/Projects/tasks/tasks")

    # Find all .toml files
    all_tasks = sorted(base_dir.glob("**/*.toml"))
    print(f"Found {len(all_tasks)} task files\n")

    # Track statistics
    already_correct = []
    needs_moving = []
    new_dirs_needed = set()

    # First pass: determine what needs to be moved
    print("Analyzing tasks...")
    for task_path in all_tasks:
        expected_path = get_expected_path(task_path, base_dir)

        if expected_path is None:
            continue

        if task_path == expected_path:
            already_correct.append(task_path)
        else:
            needs_moving.append((task_path, expected_path))
            # Track new directories that need to be created
            expected_dir = expected_path.parent
            if not expected_dir.exists():
                new_dirs_needed.add(expected_dir)

    print(f"\nAnalysis complete:")
    print(f"  - Tasks already in correct location: {len(already_correct)}")
    print(f"  - Tasks that need to be moved: {len(needs_moving)}")
    print(f"  - New directories needed: {len(new_dirs_needed)}")

    if new_dirs_needed:
        print(f"\nNew directories to create:")
        for d in sorted(new_dirs_needed):
            print(f"  - {d.relative_to(base_dir)}")

    if not needs_moving:
        print("\nAll tasks are already in the correct location!")
        return

    print(f"\nMoving {len(needs_moving)} files...")

    # Create necessary directories
    for new_dir in sorted(new_dirs_needed):
        new_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {new_dir.relative_to(base_dir)}")

    # Move files using git mv
    moved_count = 0
    repo_root = Path("/Users/v/Projects/tasks")
    for current_path, expected_path in needs_moving:
        try:
            # Use git mv to preserve history
            result = subprocess.run(
                ["git", "mv", str(current_path), str(expected_path)],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                moved_count += 1
                print(
                    f"Moved: {current_path.relative_to(base_dir)} -> {expected_path.relative_to(base_dir)}"
                )
            else:
                print(f"Error moving {current_path}: {result.stderr}")
        except Exception as e:
            print(f"Error moving {current_path}: {e}")

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total tasks processed: {len(all_tasks)}")
    print(f"Tasks already in correct location: {len(already_correct)}")
    print(f"Tasks moved: {moved_count}")
    print(f"New directories created: {len(new_dirs_needed)}")

    if new_dirs_needed:
        print(f"\nNew directories created:")
        for d in sorted(new_dirs_needed):
            print(f"  - {d.relative_to(base_dir)}")


if __name__ == "__main__":
    main()
