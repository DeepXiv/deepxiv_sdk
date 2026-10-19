# Shared helpers for the demo scripts: print each command before running it.
# DEMO_PAUSE=1 waits for Enter between steps (for screen recording).
step() { printf '\n\033[1;36m━━ %s\033[0m\n' "$*"; }
run()  { printf '\033[1;33m$ %s\033[0m\n' "$*" >&2; "$@"; [ "${DEMO_PAUSE:-0}" = 1 ] && read -r -p "  ⏎ " _ || true; }
