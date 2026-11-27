#!/bin/sh
# ~/.xinitrc - MarsOS X session (startx)

# Session language: the one chosen in Settings, or else the one from the boot menu (LANG)
idioma=$(sed -n 's/^idioma *= *\([a-z]*\).*/\1/p' "$HOME/.config/marsos/config.ini" 2>/dev/null | head -n 1)
case "$idioma" in
	en) export LANG=en_US.UTF-8 LANGUAGE=en_US:en ;;
	pt) export LANG=pt_BR.UTF-8 LANGUAGE=pt_BR:pt ;;
esac
case "${LANG:-}" in
	pt*) MARSOS_IDIOMA=pt; pastas="Downloads Documentos Imagens" ;;
	*)   MARSOS_IDIOMA=en; pastas="Downloads Documents Pictures" ;;
esac
export MARSOS_IDIOMA

# FVWM menus in that language, and the usual folders
ln -sf "textos.$MARSOS_IDIOMA" "$HOME/.fvwm/textos"
for p in $pastas; do mkdir -p "$HOME/$p"; done

# Dillo saves to ~/Downloads (its config needs the full path)
if [ ! -f "$HOME/.dillo/dillorc" ] && [ -f /etc/dillo/dillorc ]; then
	mkdir -p "$HOME/.dillo"
	sed "s|^save_dir=.*|save_dir=$HOME/Downloads/|" /etc/dillo/dillorc > "$HOME/.dillo/dillorc"
fi

# Apps GTK sem o aviso de acessibilidade (nao ha leitor de tela na sessao)
export NO_AT_BRIDGE=1

xrdb -merge "$HOME/.Xresources"

# Retro resolution: if the screen is narrower than 1024 px (common in VMs), go to 1024x768
if command -v xrandr >/dev/null 2>&1; then
	largura=$(xrandr 2>/dev/null | sed -n 's/.*current \([0-9]*\) x.*/\1/p' | head -n 1)
	if [ -n "$largura" ] && [ "$largura" -lt 1024 ]; then
		saida=$(xrandr | awk '/ connected/ {print $1; exit}')
		[ -n "$saida" ] && xrandr --output "$saida" --mode 1024x768 2>/dev/null
	fi
fi

xset s off -dpms 2>/dev/null
xset b off 2>/dev/null

# User settings (keyboard, mouse, resolution) + startup sound
marsos-aplicar-config
xsetroot -cursor_name left_ptr -fg '#ff8933' -bg '#1a1117'
marsos-papel-de-parede --restaurar &

# Mail to Mars: deliver the arrivals and replies still pending from earlier sessions
# (exits right away when there are none). Waits for the desktop and the startup sound.
(sleep 6; exec marsos-missao --vigiar) &

if command -v fvwm >/dev/null 2>&1; then
	exec fvwm
else
	exec fvwm3
fi
