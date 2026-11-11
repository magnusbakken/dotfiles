#!/usr/bin/env bash
set -u

case "${1:-}" in
    working | waiting | done | clear) ;;
    *) exit 2 ;;
esac

[ -n "${TMUX_PANE:-}" ] || exit 0
command -v tmux >/dev/null 2>&1 || exit 0

# Hook payloads are not needed; drain stdin before updating tmux.
cat >/dev/null 2>&1 || true

# A closed pane must not cause a Claude hook to fail.
case "$1" in
    working | waiting | done)
        tmux set-option -w -t "$TMUX_PANE" @claude_state "$1" 2>/dev/null ;;
    clear)
        tmux set-option -wu -t "$TMUX_PANE" @claude_state 2>/dev/null ;;
esac

tmux refresh-client -S 2>/dev/null
exit 0
