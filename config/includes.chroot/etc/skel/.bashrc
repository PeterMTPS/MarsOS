# ~/.bashrc - MarsOS
case $- in
	*i*) ;;
	*) return ;;
esac

HISTCONTROL=ignoreboth
HISTSIZE=2000
HISTFILESIZE=4000
shopt -s histappend checkwinsize

[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# Prompt marciano:  astronauta@marte:~$
PS1='\[\e[1;31m\]\u\[\e[0;33m\]@\[\e[1;33m\]\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
case "$TERM" in
	xterm*) PS1="\[\e]0;\u@\h: \w\a\]$PS1" ;;
esac

if [ -x /usr/bin/dircolors ]; then
	eval "$(dircolors -b)"
	alias ls='ls --color=auto'
	alias grep='grep --color=auto'
fi
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias marte='sol'

if ! shopt -oq posix && [ -f /usr/share/bash-completion/bash_completion ]; then
	. /usr/share/bash-completion/bash_completion
fi
