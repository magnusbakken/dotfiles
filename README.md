# Dotfiles

My personal configuration for various Linux tools, for use with GNU Stow.

## Overview

These are my current dotfiles:

- `desktop`: Some desktop settings for Linux
- `fzf`: Fuzzy Finder settings
- `git`: Configuration for git
- `kitty`: Kitty terminal settings
- `shell`: `.profile` settings (I use zsh as my shell)
- `tmux`: Terminal Multiplexer settings
- `tmux-service`: Some startup settings for tmux
- `zsh`: Z Shell settings

## Machine-specific customization

Some of the files allow separate hooks for machine-specific settings:

- `~/.config/shell/local.env` for `.profile` and `.zshenv`
- `~/.config/shell/local.zsh` for `.zshrc`
- `~/.config/git/local` for git

## Installation with Stow

From this checkout, preview application of the packages:

    stow --dir="$PWD" --target="$HOME" --no-folding --simulate --verbose fzf git kitty shell tmux zsh

To apply everything:

    stow --dir="$PWD" --target="$HOME" --no-folding fzf git kitty shell tmux zsh

## Claude window status

After applying the `tmux` package with Stow, merge the hook entries from
`~/.config/tmux/claude-hooks.json` into `~/.claude/settings.json`, preserving
unrelated settings and hooks. Reload tmux with prefix + `r`, then start a new
Claude session normally; no extra launch arguments are needed.

Active and inactive window tabs show `[RUN]`, `[WAIT]`, or `[DONE]`. State is
shared by all Claude panes in a window: the last hook wins, including clearing
the indicator when a session ends. Focusing a window does not clear `[DONE]`.

## Per-clone Git setup

I've set up git commit and push hooks to ensure that I only use my private
GitHub account when working from a device associated with a work account.

To make git use the `.githooks` folder as its source of hooks:

    git config core.hooksPath .githooks

If you want to reuse this repo and use the hooks, replace the email address in
`.githooks/identity-check.py` with your own.