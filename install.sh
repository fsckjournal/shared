#!/usr/bin/env bash
# Bootstrap the tag handoff spine on a fresh machine / web container / phone checkout.
#
# Safe to run repeatedly. Clones (or updates) the shared spine next to the tag
# repos, makes the helpers executable, and prints the resume commands.
#
#   curl -fsSL https://raw.githubusercontent.com/fsckjournal/shared/master/install.sh | bash
# or, if you already have this repo:
#   ~/Projects/tag/shared/install.sh
set -euo pipefail

REMOTE="https://github.com/fsckjournal/shared.git"
DEST="${TAG_SHARED_DIR:-$HOME/Projects/tag/shared}"

if [ -d "$DEST/.git" ]; then
  echo "→ updating existing spine at $DEST"
  git -C "$DEST" pull --ff-only
else
  echo "→ cloning spine into $DEST"
  mkdir -p "$(dirname "$DEST")"
  git clone "$REMOTE" "$DEST"
fi

chmod +x "$DEST/bin/handoff-append" "$DEST/bin/handoff-tail" 2>/dev/null || true

# Detect which side we're on, if run from inside a tag repo.
SIDE=""
case "$PWD" in
  *"/tag/hag"*)  SIDE="hag" ;;
  *"/tag/slut"*) SIDE="slut" ;;
esac

cat <<EOF

✅ Spine ready at $DEST
   remote: $REMOTE (branch master)

Resume any session with:
   git -C "$DEST" pull --ff-only
   "$DEST/bin/handoff-tail" --to ${SIDE:-<hag|slut>} --open

Read the canonical locked decisions:
   less "$DEST/decisions/DECISIONS_LOCKED.md"

Hand work over (example):
   HANDOFF_SRC="\$PWD" "$DEST/bin/handoff-append" \\
     --from ${SIDE:-<hag|slut>} --to <other> --kind handoff \\
     --summary "<what changed / what the other side should do>"
   git -C "$DEST" commit -am "handoff" && git -C "$DEST" push

Full contract: $DEST/README.md
EOF
