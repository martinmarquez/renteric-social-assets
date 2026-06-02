#!/usr/bin/env bash
# Upload an image to renteric-social-assets and print the public URL.
#
# Usage: ./upload.sh /path/to/image.png [subfolder]
# Example: ./upload.sh ig_slide_1.png instagram
#
# Requires: GITHUB_TOKEN env var, curl, base64, jq
set -euo pipefail

FILE="${1:?Usage: $0 <file> [subfolder]}"
SUBFOLDER="${2:-instagram}"
REPO="martinmarquez/renteric-social-assets"
BRANCH="main"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "Error: GITHUB_TOKEN not set" >&2
  exit 1
fi

FILENAME="$(date -u +%Y%m%d-%H%M%S)-$(basename "$FILE")"
REPO_PATH="${SUBFOLDER}/${FILENAME}"
CONTENT=$(base64 < "$FILE" | tr -d '\n')

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X PUT \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${REPO}/contents/${REPO_PATH}" \
  -d "{\"message\":\"add ${REPO_PATH}\",\"content\":\"${CONTENT}\",\"branch\":\"${BRANCH}\"}")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" != "201" ]]; then
  echo "Error: GitHub API returned $HTTP_CODE" >&2
  echo "$BODY" | jq '.message // .' >&2
  exit 1
fi

echo "$BODY" | jq -r '.content.download_url'
