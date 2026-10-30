# Dotfiles

Personal configuration for Linux tools, installed with GNU Stow.
Install applications and plugins separately; this repository is not a
provisioner. Existing initialization may fail when prerequisites are absent.

## Per-clone Git setup

Run from this checkout before committing:

    git config --local user.name "Magnus Grindal Bakken"
    git config --local user.email "magnusbakken@gmail.com"
    git config --local user.useConfigOnly true
    git config --local core.hooksPath .githooks

The hooks require Python 3 and validate author and committer before ordinary
commits and before pushing outgoing history. Enable them after every clone.
They prevent mistakes, not deliberate bypass or commits made on GitHub.

After registering a dedicated personal public SSH key, select it locally:

    git config --local core.sshCommand "ssh -i \"$HOME/.ssh/id_ed25519_github_personal\" -o IdentitiesOnly=yes"

Verify the key authenticates as the intended personal account before pushing.
Alternatively use repository/account-scoped HTTPS authentication in a secure
credential manager. Never embed a token in the URL or tracked configuration.
Authentication configuration is local and must be repeated after cloning.

## Packages

From this checkout, preview selected packages:

    stow --dir="$PWD" --target="$HOME" --no-folding --simulate --verbose shell zsh git tmux kitty fzf

Apply by removing --simulate and --verbose. Repeat application adds missing
links; simulation is not a strict integrity audit. To remove the selected
links, use the same command with --delete.

desktop and tmux-service are additional, explicitly selected packages.
Their files depend on the machine's desktop/session setup. Installing a
service file does not enable or start it.

Before using Stow, review any existing .stowrc in this directory or your home.
Resource options can alter behavior. Never use --adopt or --override.
Conflicting files, even identical ordinary files, require explicit inspection
and backup outside this checkout. Stow does not make backups.

## Optional machine-local customization

~/.config/shell/local.env is sourced by .profile and .zshenv. Keep it
POSIX-compatible, safe to load repeatedly, quiet, and noninteractive.
~/.config/shell/local.zsh is sourced only by interactive .zshrc.
~/.config/git/local can provide machine-specific Git identity/authentication.
Keep these files and all secrets outside this repository.

Current shell prerequisites include zsh, Oh My Zsh, zoxide, fzf with zsh
integration, and the tools used by configured aliases/previews: eza, fd
(or a compatible local fd executable), bat, and tree. NVM initialization
is conditional. Tmux configuration uses tpack, resurrect/continuum plugins,
and wl-copy for clipboard bindings. Install them separately as needed.
The files do not preserve downloaded plugins, session state, or credentials.

## Checks

    sh -n shell/.profile
    zsh -n zsh/.zshenv
    zsh -n zsh/.zshrc
    python3 -m unittest discover -s tests -v

Tests require Python 3, Git, zsh, and GNU Stow and use disposable homes.
Commits and pushes are manual; only pushed changes survive loss of a machine.
