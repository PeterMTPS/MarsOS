#!/bin/bash
# MarsOS - gera a ISO. Rode numa maquina Debian 13 com live-build:  sudo ./build.sh
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
[ "$(id -u)" -eq 0 ] || exec sudo "$0" "$@"
export LC_ALL=C.UTF-8

command -v lb >/dev/null || apt-get install -y live-build

echo ">> Normalizando arquivos (fim de linha e permissoes)"
grep -rIlZ $'\r' auto build.sh tools config/includes.chroot config/hooks config/package-lists assets/boot 2>/dev/null \
	| xargs -0 -r sed -i 's/\r$//'
chown -R root:root auto config assets tools build.sh
chmod 755 auto/* build.sh tools/*.sh config/hooks/live/*.hook.chroot
find config/includes.chroot -type d -exec chmod 755 {} +
find config/includes.chroot -type f -exec chmod 644 {} +
find config/includes.chroot/usr/local/bin config/includes.chroot/usr/lib/marsos -type f -exec chmod 755 {} +

echo ">> Preparando menus de boot com o logo"
./tools/preparar-bootloaders.sh

echo ">> Gerando a ISO (pode levar 20-40 min)"
rm -f .lock
lb clean
lb config
lb build

ISO=marsos-1.0-amd64.hybrid.iso
[ -f "$ISO" ] || { echo "!! A ISO nao foi gerada - veja build.log"; exit 1; }
sha256sum "$ISO" > "$ISO.sha256"
ls -lh "$ISO"
echo ">> Pronto: $ISO"
