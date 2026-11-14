#!/bin/bash
# MarsOS - gera a ISO. Numa maquina Debian 13 com live-build:
#   sudo ./build.sh        -> ISO em portugues  (marsos-1.0-amd64.hybrid.iso)
#   sudo ./build.sh en     -> ISO em ingles     (marsos-1.0-en-amd64.hybrid.iso)
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
[ "$(id -u)" -eq 0 ] || exec sudo "$0" "$@"
export LC_ALL=C.UTF-8
IDIOMA="${1:-pt}"

command -v lb >/dev/null || apt-get install -y live-build
command -v rsync >/dev/null || apt-get install -y rsync

# Outros idiomas: monta uma copia do projeto em build-<idioma>/ com a camada
# idiomas/<idioma>/ por cima (o projeto em si nao e alterado) e gera la.
if [ "$IDIOMA" != "pt" ] && [ "${MARSOS_INTERNO:-}" != 1 ]; then
	[ -d "idiomas/$IDIOMA" ] || { echo "!! idioma desconhecido: $IDIOMA (veja a pasta idiomas/)"; exit 1; }
	echo ">> Montando a versao '$IDIOMA' em build-$IDIOMA/"
	mkdir -p "build-$IDIOMA" cache
	rsync -a --delete --exclude=/cache --exclude=/chroot --exclude=/binary --exclude=/.build \
		--exclude='/build-*' --exclude='/*.iso*' --exclude=/build.log --exclude=/saida \
		./ "build-$IDIOMA/"
	cp -a "idiomas/$IDIOMA/." "build-$IDIOMA/"
	ln -sfn ../cache "build-$IDIOMA/cache"      # reaproveita os pacotes ja baixados
	(cd "build-$IDIOMA" && MARSOS_INTERNO=1 bash ./build.sh "$IDIOMA")
	cp -f "build-$IDIOMA"/marsos-*amd64.hybrid.iso "build-$IDIOMA"/marsos-*amd64.hybrid.iso.sha256 .
	exit 0
fi

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

echo ">> Gerando a ISO ($IDIOMA) - pode levar 20-40 min"
rm -f .lock
lb clean
lb config
lb build

ISO=$(ls -t marsos-*amd64.hybrid.iso 2>/dev/null | head -n 1)
[ -n "$ISO" ] && [ -f "$ISO" ] || { echo "!! A ISO nao foi gerada - veja build.log"; exit 1; }
sha256sum "$ISO" > "$ISO.sha256"
ls -lh "$ISO"
echo ">> Pronto: $ISO"
