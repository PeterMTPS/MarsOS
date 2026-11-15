#!/bin/bash
# MarsOS - builds the ISO. On a Debian 13 machine with live-build:
#   sudo ./build.sh        -> marsos-<version>-amd64.hybrid.iso (English and Portuguese, picked at boot)
# The same script runs in GitHub Actions (.github/workflows/build-iso.yml).
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
[ "$(id -u)" -eq 0 ] || exec sudo "$0" "$@"
export LC_ALL=C.UTF-8

command -v lb >/dev/null || apt-get install -y live-build
command -v rsync >/dev/null || apt-get install -y rsync

echo ">> Normalizing files (line endings and permissions)"
grep -rIlZ $'\r' auto build.sh tools config/includes.chroot config/includes.installer config/hooks \
	config/package-lists assets/boot 2>/dev/null | xargs -0 -r sed -i 's/\r$//'
chown -R root:root auto config assets tools build.sh
chmod 755 auto/* build.sh tools/*.sh config/hooks/live/*.hook.chroot
find config/includes.chroot config/includes.installer -type d -exec chmod 755 {} +
find config/includes.chroot config/includes.installer -type f -exec chmod 644 {} +
find config/includes.chroot/usr/local/bin config/includes.chroot/usr/lib/marsos -type f -exec chmod 755 {} +

echo ">> Preparing the boot menus with the logo"
./tools/preparar-bootloaders.sh

echo ">> Building the ISO - this can take 20-40 min"
rm -f .lock
lb clean
lb config
lb build

ISO=$(ls -t marsos-*amd64.hybrid.iso 2>/dev/null | head -n 1)
[ -n "$ISO" ] && [ -f "$ISO" ] || { echo "!! The ISO was not built - see build.log"; exit 1; }
sha256sum "$ISO" > "$ISO.sha256"
ls -lh "$ISO"
echo ">> Done: $ISO"
