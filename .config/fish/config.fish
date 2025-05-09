if status is-interactive
    # Commands to run in interactive sessions can go here
end

oh-my-posh init fish --config '~/.dotfiles/.config/ompsh/theme.toml' | source

zoxide init fish | source
/home/linuxbrew/.linuxbrew/bin/brew shellenv | source

export PATH="$PATH:/home/zen/.spicetify"
abbr --add ls ls -la
abbr --add vifish nvim ~/.dotfiles/.config/fish/config.fish
function fish_greeting                                            
    # do nothing
end

export PATH="$PATH:/home/zen/.local/bin"
abbr --add v nvim
abbr --add matuconf nvim ~/.dotfiles/.config/Ax-Shell/config/matugen/config.toml
abbr --add ky nvim ~/.dotfiles/.config/kitty/kitty.conf
abbr --add hy nvim ~/.dotfiles/.config/hypr/hyprland.conf
