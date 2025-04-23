#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls -la --color=auto'
alias grep='grep --color=auto'
alias rofi='rofi -show drun &'
alias nmce='nm-connection-editor'
alias pm='sudo pacman -S'
alias obby='OBSIDIAN_USE_WAYLAND=1 obsidian -enable-features=UseOzonePlatform -ozone-platform=wayland'


PS1='[\u@\h \W]\$ '


#Pkgs



export OBSIDIAN_USE_WAYLAND=1
export PATH=$HOME/.local/bin:$PATH
eval "$(oh-my-posh init bash --config '~/posh/honukai.json')"

eval "$(zoxide init bash)"

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
