#!/usr/bin/env python3
"""
Script to publish JSON files from the release directory to a remote URL.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import List


def read_json_files(directory: str) -> List[tuple]:
    """
    Read all JSON files from the specified directory.

    Returns:
        List of tuples (filename, json_data)
    """
    json_files = []
    release_path = Path(directory)

    if not release_path.exists():
        print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
        sys.exit(1)

    for json_file in release_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                json_files.append((json_file.name, data))
                print(f"Read: {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"Error reading {json_file.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}", file=sys.stderr)

    return json_files


def publish_task(
    url: str, task_data: dict, visibility: str, origin: str, auth_token: str
) -> bool:
    """
    Publish a single task to the remote URL.

    Args:
        url: The target URL
        task_data: The JSON data to publish
        visibility: Visibility setting ('public' or 'hidden')
        origin: Origin of the tasks
        auth_token: Authorization token from environment

    Returns:
        True if successful, False otherwise
    """
    # Prepare the payload
    payload = {"task": task_data, "visibility": visibility, "origin": origin}

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
    }

    if auth_token:
        headers["X-AUTH-KEY"] = auth_token

    # Convert payload to JSON bytes
    data = json.dumps(payload).encode("utf-8")

    # Create request
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            response_body = response.read().decode("utf-8")
            if status in (200, 201):
                return True
            else:
                print(f"  Warning: Received status {status}", file=sys.stderr)
                print(f"  Response: {response_body}", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"  HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if error_body:
            print(f"  Response: {error_body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"  URL Error: {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Publish JSON files from release directory to a remote URL"
    )
    parser.add_argument("url", help="Target URL to publish tasks to")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Set visibility to public (default: hidden)",
    )
    parser.add_argument(
        "--hidden", action="store_true", help="Set visibility to hidden (default)"
    )
    parser.add_argument(
        "--origin",
        default="github",
        help="Origin of the tasks (default: github)",
    )
    parser.add_argument(
        "--dir",
        default="release",
        help="Directory containing JSON files (default: release)",
    )

    args = parser.parse_args()

    # Determine visibility
    if args.public and args.hidden:
        print("Error: Cannot specify both --public and --hidden", file=sys.stderr)
        sys.exit(1)

    visibility = "public" if args.public else "hidden"

    # Get auth token from environment
    auth_token = os.environ.get("CODEBATTLE_AUTH_TOKEN", "")
    if not auth_token:
        print(
            "Warning: CODEBATTLE_AUTH_TOKEN environment variable not set",
            file=sys.stderr,
        )

    # Read JSON files
    print(f"Reading JSON files from '{args.dir}/'...")
    json_files = read_json_files(args.dir)

    if not json_files:
        print("No JSON files found to publish", file=sys.stderr)
        sys.exit(1)

    print(f"\nPublishing {len(json_files)} tasks to {args.url}...")
    print(f"Visibility: {visibility}")
    print(f"Origin: {args.origin}")
    print()

    # Publish each task
    success_count = 0
    fail_count = 0

    for filename, task_data in json_files:
        print(f"Publishing: {filename}... ", end="", flush=True)
        if publish_task(args.url, task_data, visibility, args.origin, auth_token):
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1

    # Summary
    print()
    print(f"Summary: {success_count} successful, {fail_count} failed")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
