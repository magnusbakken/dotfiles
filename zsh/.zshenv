typeset -U path PATH

path=(
    $HOME/bin(N)
    $HOME/.local/bin(N)
    $path
)

if [ -f "$HOME/.config/shell/local.env" ]; then
    . "$HOME/.config/shell/local.env"
fi
