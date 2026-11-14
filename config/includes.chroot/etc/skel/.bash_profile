# ~/.bash_profile - MarsOS
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

# No primeiro console: mostra o planeta e abre o X sozinho (como nos Linux de antigamente,
# mas sem precisar lembrar do "startx").
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
	clear
	marsfetch
	printf '  \033[1;33mIniciando o sistema de janelas X em 5 segundos...\033[0m\n'
	printf '  \033[0;33m(aperte qualquer tecla para ficar no console)\033[0m\n'
	if read -r -s -n 1 -t 5; then
		printf '\n  Ficando no console. Digite \033[1;31mstartx\033[0m quando quiser as janelas.\n\n'
	else
		startx -- -nolisten tcp
		printf '\n  O X foi encerrado. Digite \033[1;31mstartx\033[0m para voltar.\n\n'
	fi
fi
