#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-all}"
FORCE="${FORCE:-0}"

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$REPO/skills/opencode-free"

if [ ! -f "$SOURCE/SKILL.md" ]; then
  echo "SKILL.md not found at $SOURCE" >&2
  exit 1
fi

install_skill() {
  local name="$1" dest="$2"
  if [ -e "$dest" ] && [ "$FORCE" != "1" ]; then
    echo "skip      $name (already present: $dest)"
    return
  fi
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$SOURCE" "$dest"
  echo "installed $name -> $dest"
}

case "$TARGET" in
  all)
    install_skill opencode "$HOME/.config/opencode/skills/opencode-free"
    install_skill claude   "$HOME/.claude/skills/opencode-free"
    install_skill codex    "$HOME/.agents/skills/opencode-free"
    ;;
  opencode) install_skill opencode "$HOME/.config/opencode/skills/opencode-free" ;;
  claude)   install_skill claude   "$HOME/.claude/skills/opencode-free" ;;
  codex)    install_skill codex    "$HOME/.agents/skills/opencode-free" ;;
  *) echo "unknown target: $TARGET (use all|opencode|claude|codex)" >&2; exit 1 ;;
esac

if command -v opencode >/dev/null 2>&1; then
  echo "reloading OpenCode..."
  opencode reload >/dev/null 2>&1 || true
fi

echo
echo "Restart the OpenCode desktop app (if open) so it re-scans skills."
echo "Invoke with /opencode-free (OpenCode, Claude Code) or \$opencode-free (Codex)."
