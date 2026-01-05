#!/bin/bash
# Block reading of credential files to prevent leaking to LLM
set -euo pipefail

# Read input from stdin
input=$(cat)

# Extract file path from tool input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# If no file path, allow
[ -z "$file_path" ] && exit 0

# Block credential files (credentials.json in .claude/data-analyze/)
if [[ "$file_path" == *".claude/data-analyze/credentials.json"* ]]; then
  echo '{"decision":"block","reason":"Credential files are protected to prevent leaking sensitive data"}' >&2
  exit 2
fi

# Block any file with "credentials" in the name that's a JSON file
if [[ "$file_path" == *"credentials"* ]] && [[ "$file_path" == *.json ]]; then
  echo '{"decision":"block","reason":"Credential files are protected to prevent leaking sensitive data"}' >&2
  exit 2
fi

# Allow all other files
exit 0
