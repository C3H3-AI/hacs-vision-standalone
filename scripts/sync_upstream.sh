#!/usr/bin/env bash
# sync_upstream.sh — Keep hacs-vision-standalone in sync with upstream HACS.
#
# WHY: This project is a full fork-merge of hacs/integration. Upstream ships
# bug fixes, security patches and new features continuously. Falling behind
# rots the fork and reintroduces regressions (we already hit a panel-blank
# regression from an un-reviewed merge). This script makes staying current
# a one-command, reviewable operation.
#
# SAFE BY DEFAULT: With no arguments it only PREVIEWS what upstream would bring
# in (commit list + changed files). Nothing is merged. Pass --apply to actually
# merge upstream/main into the current branch — conflicts are left for the human
# to resolve, never auto-resolved.
#
# USAGE:
#   ./scripts/sync_upstream.sh            # preview only
#   ./scripts/sync_upstream.sh --apply    # merge upstream/main (no auto-commit of conflicts)
#
set -euo pipefail

UPSTREAM_REMOTE="${UPSTREAM_REMOTE:-upstream}"
UPSTREAM_BRANCH="${UPSTREAM_BRANCH:-main}"
UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/hacs/integration.git}"
APPLY=0

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    *) echo "Unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# Ensure the upstream remote exists
if ! git remote get-url "$UPSTREAM_REMOTE" >/dev/null 2>&1; then
  echo "➕ Adding upstream remote '$UPSTREAM_REMOTE' -> $UPSTREAM_URL"
  git remote add "$UPSTREAM_REMOTE" "$UPSTREAM_URL"
fi

echo "🔄 Fetching upstream..."
git fetch "$UPSTREAM_REMOTE" "$UPSTREAM_BRANCH"

echo ""
echo "📋 Commits upstream would bring in (newest first):"
git log --oneline "HEAD..${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}" | head -50 || true

echo ""
echo "📁 Files changed vs current HEAD:"
git diff --stat "HEAD..${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}" | tail -30 || true

if [ "$APPLY" -eq 1 ]; then
  echo ""
  echo "⚠️  Merging ${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH} into current branch..."
  echo "    Conflicts (if any) are left for YOU to resolve. Nothing is force-pushed."
  git merge --no-edit "${UPSTREAM_REMOTE}/${UPSTREAM_BRANCH}" || {
    echo "❌ Merge produced conflicts. Resolve them, then 'git commit' and test before pushing."
    echo "   To abort: git merge --abort"
    exit 1
  }
  echo "✅ Merge complete. Run your smoke test, then commit/push per release rules."
else
  echo ""
  echo "✅ Preview only. Re-run with --apply to merge (conflicts left for manual resolve)."
fi
