#!/bin/sh
# ~/.xinitrc - sessao X do MarsOS (startx)

xrdb -merge "$HOME/.Xresources"

# Resolucao retro: se a tela vier menor que 1024 px (comum em VM), sobe para 1024x768
if command -v xrandr >/dev/null 2>&1; then
	largura=$(xrandr 2>/dev/null | sed -n 's/.*current \([0-9]*\) x.*/\1/p' | head -n 1)
	if [ -n "$largura" ] && [ "$largura" -lt 1024 ]; then
		saida=$(xrandr | awk '/ connected/ {print $1; exit}')
		[ -n "$saida" ] && xrandr --output "$saida" --mode 1024x768 2>/dev/null
	fi
fi

xset s off -dpms 2>/dev/null
xset b off 2>/dev/null

# Configuracoes do usuario (teclado, mouse, resolucao) + som de inicializacao
marsos-aplicar-config
xsetroot -cursor_name left_ptr -fg '#ff8933' -bg '#1a1117'
marsos-papel-de-parede --restaurar &

if command -v fvwm >/dev/null 2>&1; then
	exec fvwm
else
	exec fvwm3
fi
