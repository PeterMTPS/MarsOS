# /etc/profile.d/marsos-boasvindas.sh - MarsOS welcome on text consoles (English / Portugues)
case "$-" in *i*) ;; *) return 0 ;; esac
[ -n "$DISPLAY" ] && return 0
[ "$(tty 2>/dev/null)" = /dev/tty1 ] && return 0   # tty1 already shows marsfetch (~/.bash_profile)

case "${LANG:-}" in
pt*)
	printf '\n  \033[1;31mBem-vindo ao %s\033[0m (base Debian GNU/Linux 13)\n\n' "${MARSOS_NOME:-MarsOS 1.2 \"Olympus\"}"
	printf '  Comandos marcianos:\n'
	printf '    sol ........... hora e data em Marte (e o atraso do sinal até a Terra)\n'
	printf '    marsfetch ..... informações do sistema\n'
	printf '    startx ........ abre o sistema de janelas (FVWM)\n'
	printf '    mc ............ gerenciador de arquivos no terminal\n'
	[ -d /run/live ] && printf '    sudo -i ....... vira root  (usuário live: astronauta / senha: live)\n'
	;;
*)
	printf '\n  \033[1;31mWelcome to %s\033[0m (based on Debian GNU/Linux 13)\n\n' "${MARSOS_NOME:-MarsOS 1.2 \"Olympus\"}"
	printf '  Martian commands:\n'
	printf '    sol ........... date and time on Mars (and the signal delay to Earth)\n'
	printf '    marsfetch ..... system information\n'
	printf '    startx ........ start the window system (FVWM)\n'
	printf '    mc ............ file manager in the terminal\n'
	[ -d /run/live ] && printf '    sudo -i ....... become root  (live user: astronauta / password: live)\n'
	;;
esac
printf '\n'
