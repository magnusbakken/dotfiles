# History
HISTFILE=$HOME/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt APPEND_HISTORY INC_APPEND_HISTORY SHARE_HISTORY
setopt HIST_IGNORE_DUPS HIST_IGNORE_SPACE HIST_REDUCE_BLANKS

# lesspipe + colors (must precede completion)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"
[ -x /usr/bin/dircolors ] && eval "$(dircolors -b)"

# Completions and Oh-My-Zsh setup
fpath=($HOME/.zfunc $fpath)
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)

source "$ZSH/oh-my-zsh.sh"

autoload -Uz bashcompinit
bashcompinit

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*:descriptions' format '%F{yellow}%d%f'
setopt COMPLETE_IN_WORD ALWAYS_TO_END AUTO_MENU
setopt AUTO_CD EXTENDED_GLOB

# Prompt
#PROMPT='%F{green}%n@%m%f:%F{blue}%~%f%# '
#precmd() { print -Pn "\e]0;%n@%m: %~\a" }

# Zoxide
eval "$(zoxide init zsh)"

# Aliases
alias ls='eza --color=auto --icons=auto --group-directories-first'
alias ll='eza -la --icons=auto --group-directories-first --git --header'
alias lt='eza --tree --level=2 --icons=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias bat='batcat'

# Bindings
bindkey '^[[1;5D' backward-word     # Ctrl+Left
bindkey '^[[1;5C' forward-word      # Ctrl+Right
bindkey '^[[1;3D' backward-word     # Alt+Left
bindkey '^[[1;3C' forward-word      # Alt+Right
bindkey '^[[H'    beginning-of-line # Home
bindkey '^[[F'    end-of-line       # End
bindkey '^[OH'    beginning-of-line # Home (tmux)
bindkey '^[OF'    end-of-line       # End (tmux)

# fd's binary is `fdfind` here; ~/.local/bin/fd symlinks to it.
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git --strip-cwd-prefix=always'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git --strip-cwd-prefix=always'
export FZF_DEFAULT_OPTS_FILE="$HOME/.config/fzf/fzfrc"
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:200 --{}' --preview-window=right:60%:wrap --bind 'ctrl-/:toggle-preview'"
export FZF_ALT_C_OPTS="--preview 'tree -C -L 2 {} | head -200'"

# fd rejects --strip-cwd-prefix when fzf completion supplies a search path
_fzf_compgen_path() { fd --hidden --follow --exclude .git . "$1" }
_fzf_compgen_dir()  { fd --type d --hidden --follow --exclude .git . "$1" }

source <(fzf --zsh)

# NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"

# Plugins
[ -f /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh ] && . /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
[ -f /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ] && . /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

if [ -f "$HOME/.config/shell/local.zsh" ]; then
    . "$HOME/.config/shell/local.zsh"
fi
