#!/usr/bin/env python3
"""
Script to publish task pack JSON files to a remote URL.
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
    task_packs_path = Path(directory)

    if not task_packs_path.exists():
        print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
        sys.exit(1)

    for json_file in task_packs_path.glob("*.json"):
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


def publish_task_pack(
    url: str, pack_data: dict, visibility: str, origin: str, auth_token: str
) -> bool:
    """
    Publish a single task pack to the remote URL.

    Args:
        url: The target URL
        pack_data: The JSON data to publish
        visibility: Visibility setting ('public' or 'hidden')
        origin: Origin of the task packs
        auth_token: Authorization token from environment

    Returns:
        True if successful, False otherwise
    """
    # Prepare the payload
    payload = {"task_pack": pack_data, "visibility": visibility, "origin": origin}

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


def load_env_file(env_path: str = ".env") -> dict:
    """
    Load environment variables from a .env file.

    Args:
        env_path: Path to the .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    env_file = Path(env_path)

    if not env_file.exists():
        return env_vars

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip().strip("\"'")
                    env_vars[key.strip()] = value
    except Exception as e:
        print(f"Warning: Error reading .env file: {e}", file=sys.stderr)

    return env_vars


def main():
    parser = argparse.ArgumentParser(
        description="Publish task pack JSON files to a remote URL"
    )
    parser.add_argument("url", help="Target URL to publish task packs to")
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
        help="Origin of the task packs (default: github)",
    )
    parser.add_argument(
        "--dir",
        default="task_packs",
        help="Directory containing JSON files (default: task_packs)",
    )

    args = parser.parse_args()

    # Determine visibility
    if args.public and args.hidden:
        print("Error: Cannot specify both --public and --hidden", file=sys.stderr)
        sys.exit(1)

    visibility = "public" if args.public else "hidden"

    # Get auth token from environment variable first, then fall back to .env file
    auth_token = os.environ.get("CODEBATTLE_AUTH_TOKEN", "")
    if not auth_token:
        env_vars = load_env_file()
        auth_token = env_vars.get("CODEBATTLE_AUTH_TOKEN", "")

    if not auth_token:
        print(
            "Warning: CODEBATTLE_AUTH_TOKEN not found in environment or .env file",
            file=sys.stderr,
        )

    # Read JSON files
    print(f"Reading JSON files from '{args.dir}/'...")
    json_files = read_json_files(args.dir)

    if not json_files:
        print("No JSON files found to publish", file=sys.stderr)
        sys.exit(1)

    print(f"\nPublishing {len(json_files)} task packs to {args.url}...")
    print(f"Visibility: {visibility}")
    print(f"Origin: {args.origin}")
    print()

    # Publish each task pack
    success_count = 0
    fail_count = 0

    for filename, pack_data in json_files:
        print(f"Publishing: {filename}... ", end="", flush=True)
        if publish_task_pack(args.url, pack_data, visibility, args.origin, auth_token):
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
