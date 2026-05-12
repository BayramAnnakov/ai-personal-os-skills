#!/usr/bin/env bash
# calibrate.sh — Pre-filter user's Claude Code conversation history for pptx-related corrections.
#
# Output: one candidate correction message per block, prefixed with project + session.
# Designed to be small enough to feed to Claude for clustering.
#
# Usage: bash calibrate.sh > /tmp/slide-inspector-calibration-corpus.txt

set -uo pipefail

PROJECTS_DIR="${HOME}/.claude/projects"
MAX_FILES_PER_PROJECT=15           # cap per project to control corpus size
MAX_MSG_LENGTH=400                 # truncate long messages

if [ ! -d "$PROJECTS_DIR" ]; then
    echo "ERROR: $PROJECTS_DIR not found. No CC history to mine." >&2
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq not installed. Install with: brew install jq" >&2
    exit 1
fi

# Filter regex for pptx-related sessions
PPTX_PATTERN='pptx|powerpoint|slide-inspector|pptxgenjs|edu-workshop-slides|presentation\.|\.pptx'

# Filter regex for correction-language messages (English + Russian)
CORRECTION_PATTERN='\b(change|fix|instead|wrong|broken|remove|replace|move|resize|too (small|big|narrow|wide|much|many|few)|should be|please (fix|change|update|remove)|переделай|не нравится|неправильно|почини|убери|поменяй|исправ|сделай)\b'

echo "# slide-inspector calibration corpus"
echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# Source: $PROJECTS_DIR"
echo ""

# Iterate over each project directory
for project_dir in "$PROJECTS_DIR"/*/; do
    [ -d "$project_dir" ] || continue
    project_name=$(basename "$project_dir")

    # Find pptx-related jsonl files in this project (newest first, capped)
    mapfile -t matching_files < <(
        grep -lEi "$PPTX_PATTERN" "$project_dir"*.jsonl 2>/dev/null \
            | head -n $MAX_FILES_PER_PROJECT
    )

    [ ${#matching_files[@]} -eq 0 ] && continue

    for jsonl_file in "${matching_files[@]}"; do
        session_id=$(basename "$jsonl_file" .jsonl)

        # Extract user-role messages, filter by correction-language pattern
        # Different jsonl schemas exist; try the most common shape first
        jq -r '
            select(.type == "user" and (.message.content | type == "string"))
            | .message.content
        ' "$jsonl_file" 2>/dev/null \
            | grep -iE "$CORRECTION_PATTERN" \
            | sort -u \
            | while IFS= read -r msg; do
                # Truncate long messages
                if [ ${#msg} -gt $MAX_MSG_LENGTH ]; then
                    msg="${msg:0:$MAX_MSG_LENGTH}..."
                fi
                # Skip empty / whitespace-only
                [ -z "${msg// }" ] && continue
                echo "[${project_name} | ${session_id:0:8}] ${msg}"
              done

        # Fallback for the alt content-array shape (some CC versions)
        jq -r '
            select(.type == "user" and (.message.content | type == "array"))
            | .message.content[]
            | select(.type == "text")
            | .text
        ' "$jsonl_file" 2>/dev/null \
            | grep -iE "$CORRECTION_PATTERN" \
            | sort -u \
            | while IFS= read -r msg; do
                if [ ${#msg} -gt $MAX_MSG_LENGTH ]; then
                    msg="${msg:0:$MAX_MSG_LENGTH}..."
                fi
                [ -z "${msg// }" ] && continue
                echo "[${project_name} | ${session_id:0:8}] ${msg}"
              done
    done
done | sort -u

echo ""
echo "# End of corpus."
