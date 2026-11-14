# ~/.bash_profile - MarsOS
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

# On the first console: show the planet and start X automatically (like the Linux
# of old, without having to remember "startx").
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
	clear
	marsfetch
	printf '  \033[1;33mStarting the X window system in 5 seconds...\033[0m\n'
	printf '  \033[0;33m(press any key to stay on the console)\033[0m\n'
	if read -r -s -n 1 -t 5; then
		printf '\n  Staying on the console. Type \033[1;31mstartx\033[0m when you want windows.\n\n'
	else
		startx -- -nolisten tcp
		printf '\n  X has exited. Type \033[1;31mstartx\033[0m to go back.\n\n'
	fi
fi
