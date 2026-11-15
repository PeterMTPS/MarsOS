# ~/.bash_profile - MarsOS
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

# Messages in the session language (English or Portuguese, picked in the boot menu)
case "${LANG:-}" in
pt*)	MSG_INICIO='Iniciando o sistema de janelas X em 5 segundos...'
	MSG_TECLA='(aperte qualquer tecla para ficar no console)'
	MSG_CONSOLE='Ficando no console. Digite \033[1;31mstartx\033[0m quando quiser as janelas.'
	MSG_SAIU='O X foi encerrado. Digite \033[1;31mstartx\033[0m para voltar.' ;;
*)	MSG_INICIO='Starting the X window system in 5 seconds...'
	MSG_TECLA='(press any key to stay on the console)'
	MSG_CONSOLE='Staying on the console. Type \033[1;31mstartx\033[0m when you want windows.'
	MSG_SAIU='X has exited. Type \033[1;31mstartx\033[0m to go back.' ;;
esac

# On the first console: show the planet and start X automatically (like the Linux
# of old, without having to remember "startx").
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
	clear
	marsfetch
	printf '  \033[1;33m%s\033[0m\n' "$MSG_INICIO"
	printf '  \033[0;33m%s\033[0m\n' "$MSG_TECLA"
	if read -r -s -n 1 -t 5; then
		printf "\n  $MSG_CONSOLE\n\n"
	else
		# The Settings app can ask for a new session (e.g. after changing the language)
		reinicio="$HOME/.cache/marsos/reiniciar-sessao"
		while :; do
			rm -f "$reinicio"
			startx -- -nolisten tcp
			[ -f "$reinicio" ] || break
		done
		printf "\n  $MSG_SAIU\n\n"
	fi
fi
unset MSG_INICIO MSG_TECLA MSG_CONSOLE MSG_SAIU reinicio
