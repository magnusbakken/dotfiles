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

## Per-clone Git setup

I've set up some git hooks to make sure I use my private GitHub account,
even if I'm working from a device associated with a work account.

If you want to clone this repo and reuse it, delete the `.githooks` folder or
replace the email address in `.githooks/identity-check.py` with your own.

## Installation with Stow

From this checkout, preview application of the packages:

    stow --dir="$PWD" --target="$HOME" --no-folding --simulate --verbose fzf git kitty shell tmux zsh

To apply everything:

    stow --dir="$PWD" --target="$HOME" --no-folding fzf git kitty shell tmux zsh