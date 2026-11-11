#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    printf 'Usage: window-agent-status.sh <window-id>\n' >&2
    exit 2
fi

panes=$(tmux list-panes -t "$1" -F '#{pane_id}')
tmux show-environment -g | awk -v panes="$panes" '
    BEGIN {
        count = split(panes, ids, "\n")
        for (i = 1; i <= count; i++)
            keys["TMUX_AGENT_PANE_" ids[i] "_STATE"] = 1
        ranks["running"] = 1
        ranks["done"] = 2
        ranks["needs-input"] = 3
    }
    {
        separator = index($0, "=")
        key = substr($0, 1, separator - 1)
        state = substr($0, separator + 1)
        if (key in keys && ranks[state] > rank)
            rank = ranks[state]
    }
    END {
        if (rank == 3)
            printf "#[fg=yellow,bg=colour16,bold] [WAIT]#[default]"
        else if (rank == 2)
            printf "#[fg=green,bg=colour16] [DONE]#[default]"
        else if (rank == 1)
            printf "#[fg=cyan,bg=colour16] [RUN]#[default]"
    }
'
