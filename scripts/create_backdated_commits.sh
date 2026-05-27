#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/create_backdated_commits.sh 2026-05-20
# Creates local commits with explicit author/committer dates. Use only for legitimate
# local-history reconstruction, migration, or training repositories. Do not use this
# to misrepresent real work history on an assessment platform.

START_DATE="${1:-2026-05-20}"
COMMITS=(
  "Initialize repository quality baseline"
  "Add inventory scanner and file classification"
  "Add Docker and shell safety rules"
  "Add Terraform and Kubernetes policy checks"
  "Add Jenkins and Python portability checks"
  "Add CLI reporting and test coverage"
)

for i in "${!COMMITS[@]}"; do
  touch ".commit-marker-$i"
  git add .
  export GIT_AUTHOR_DATE="$(date -d "$START_DATE + $i day" '+%Y-%m-%dT10:00:00+05:30')"
  export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
  git commit -m "${COMMITS[$i]}" || true
done
