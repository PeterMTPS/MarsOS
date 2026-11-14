#!/bin/sh
# Copia os menus de boot padrao do live-build e aplica o tema do MarsOS por cima.
set -e
cd "$(dirname "$0")/.."
SRC=/usr/share/live/build/bootloaders

rm -rf config/bootloaders
mkdir -p config/bootloaders
for d in isolinux syslinux_common grub-pc; do
	cp -a "$SRC/$d" config/bootloaders/
	if [ -d "assets/boot/$d" ]; then
		cp -a "assets/boot/$d/." "config/bootloaders/$d/"
	fi
done
cp assets/boot/splash.png      config/bootloaders/syslinux_common/splash.png
cp assets/boot/splash-grub.png config/bootloaders/grub-pc/splash.png
echo "   menus de boot prontos em config/bootloaders/"
