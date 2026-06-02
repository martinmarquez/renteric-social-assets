#!/usr/bin/env python3
"""
Upload a PNG image to the renteric-social-assets GitHub repo and return its public URL.

Usage:
    python upload.py /path/to/image.png [--subfolder instagram]

Output:
    https://raw.githubusercontent.com/martinmarquez/renteric-social-assets/main/instagram/filename.png

Requires:
    GITHUB_TOKEN env var with repo write access to martinmarquez/renteric-social-assets
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

REPO = "martinmarquez/renteric-social-assets"
BRANCH = "main"
API_BASE = "https://api.github.com"


def upload_image(file_path: str, subfolder: str = "instagram") -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN env var not set")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Build unique filename with timestamp to avoid collisions
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{ts}-{path.name}"
    repo_path = f"{subfolder}/{filename}"

    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    payload = json.dumps({
        "message": f"add {repo_path}",
        "content": content,
        "branch": BRANCH,
    }).encode()

    url = f"{API_BASE}/repos/{REPO}/contents/{repo_path}"
    req = urllib.request.Request(
        url,
        data=payload,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            raw_url = result["content"]["download_url"]
            return raw_url
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"GitHub API error {e.code}: {body}") from e


def main():
    parser = argparse.ArgumentParser(description="Upload image to social assets repo")
    parser.add_argument("file", help="Path to PNG image file")
    parser.add_argument("--subfolder", default="instagram", help="Subfolder in repo")
    args = parser.parse_args()

    url = upload_image(args.file, args.subfolder)
    print(url)


if __name__ == "__main__":
    main()
