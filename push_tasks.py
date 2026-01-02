#!/usr/bin/env python3
"""
Script to publish JSON files from the release directory to a remote URL.
"""

import argparse
import base64
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List


def read_json_files(directory: str) -> List[tuple]:
    """
    Read all JSON files from the specified directory recursively.

    Returns:
        List of tuples (filename, json_data)
    """
    json_files = []
    release_path = Path(directory)

    if not release_path.exists():
        print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
        sys.exit(1)

    for json_file in release_path.rglob("*.json"):
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


def publish_task_batch(
    url: str, tasks_batch: List[tuple], visibility: str, origin: str, auth_token: str
) -> dict:
    """
    Publish a batch of tasks to the remote URL with gzip compression and base64 encoding.

    Args:
        url: The target URL
        tasks_batch: List of tuples (filename, task_data)
        visibility: Visibility setting ('public' or 'hidden')
        origin: Origin of the tasks
        auth_token: Authorization token from environment

    Returns:
        Dictionary with 'success' count and 'failed' list of filenames
    """
    result = {"success": 0, "failed": []}

    # Prepare the tasks list (just the task data, no wrapping)
    tasks_list = [task_data for _, task_data in tasks_batch]

    # Convert to JSON, compress with gzip, and encode with base64
    json_data = json.dumps(tasks_list).encode("utf-8")
    compressed_data = gzip.compress(json_data)
    base64_payload = base64.b64encode(compressed_data).decode("ascii")

    # Prepare the final payload structure matching the API
    payload = {
        "payload": base64_payload,
        "visibility": visibility,
        "origin": origin,
    }

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    if auth_token:
        headers["X-AUTH-KEY"] = auth_token

    # Convert payload to JSON bytes
    request_data = json.dumps(payload).encode("utf-8")

    # Create request
    req = urllib.request.Request(url, data=request_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            response_body = response.read().decode("utf-8")
            if status in (200, 201):
                result["success"] = len(tasks_batch)
                return result
            else:
                print(f"  Warning: Received status {status}", file=sys.stderr)
                print(f"  Response: {response_body}", file=sys.stderr)
                result["failed"] = [filename for filename, _ in tasks_batch]
                return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"  HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if error_body:
            # Truncate very long error messages
            if len(error_body) > 500:
                print(f"  Response: {error_body[:500]}...", file=sys.stderr)
            else:
                print(f"  Response: {error_body}", file=sys.stderr)
        result["failed"] = [filename for filename, _ in tasks_batch]
        return result
    except urllib.error.URLError as e:
        print(f"  URL Error: {e.reason}", file=sys.stderr)
        result["failed"] = [filename for filename, _ in tasks_batch]
        return result
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        result["failed"] = [filename for filename, _ in tasks_batch]
        return result


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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Number of tasks to send in each batch (default: 20)",
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

    print(f"\nPublishing {len(json_files)} tasks to {args.url}...")
    print(f"Visibility: {visibility}")
    print(f"Origin: {args.origin}")
    print(f"Batch size: {args.batch_size}")
    print()

    # Publish tasks in batches
    success_count = 0
    fail_count = 0
    total_batches = (len(json_files) + args.batch_size - 1) // args.batch_size

    for batch_num in range(0, len(json_files), args.batch_size):
        batch = json_files[batch_num : batch_num + args.batch_size]
        batch_index = batch_num // args.batch_size + 1

        print(
            f"Batch {batch_index}/{total_batches} ({len(batch)} tasks)... ",
            end="",
            flush=True,
        )

        result = publish_task_batch(
            args.url, batch, visibility, args.origin, auth_token
        )

        if result["success"] > 0:
            print(f"✓ ({result['success']} tasks)")
            success_count += result["success"]

        if result["failed"]:
            print(f"✗ Failed tasks: {', '.join(result['failed'])}")
            fail_count += len(result["failed"])

        # Add a small delay between batches to avoid rate limiting
        if batch_index < total_batches:
            time.sleep(1)

    # Summary
    print()
    print(f"Summary: {success_count} successful, {fail_count} failed")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
