# MarsOS - envia o projeto para a VM construtora, gera a ISO e traz de volta para saida\
# Uso:  powershell -ExecutionPolicy Bypass -File tools\construir.ps1
param([int]$Port = 2222)

# 'Continue': no PowerShell 5.1, qualquer texto do ssh.exe no stderr viraria erro fatal.
# Cada comando externo e conferido pelo $LASTEXITCODE.
$ErrorActionPreference = 'Continue'
$Raiz = Split-Path -Parent $PSScriptRoot
$ssh  = "$env:WINDIR\System32\OpenSSH\ssh.exe"
$scp  = "$env:WINDIR\System32\OpenSSH\scp.exe"
$opt  = @("-i", "$env:USERPROFILE\.ssh\marsos_builder",
          "-o", "UserKnownHostsFile=$env:USERPROFILE\.ssh\marsos_known_hosts",
          "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes",
          "-o", "ServerAliveInterval=30")

# Liga a VM construtora se estiver desligada
$VB = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$estado = (& $VB showvminfo "MarsOS-Construtora" --machinereadable | Select-String '^VMState=').ToString()
if ($estado -notmatch 'running') {
    Write-Host ">> Ligando a VM construtora..."
    & $VB startvm "MarsOS-Construtora" --type headless | Out-Null
    for ($i = 0; $i -lt 60; $i++) {
        & $ssh @opt -p $Port -o ConnectTimeout=5 mars@127.0.0.1 true 2>$null
        if ($LASTEXITCODE -eq 0) { break }
        Start-Sleep -Seconds 5
    }
}

Write-Host ">> Empacotando o projeto"
$tgz = Join-Path $env:TEMP "marsos-src.tgz"
tar -czf $tgz -C $Raiz auto config assets tools build.sh
if ($LASTEXITCODE -ne 0) { throw "tar falhou" }

Write-Host ">> Enviando para a VM"
& $scp @opt -P $Port $tgz "mars@127.0.0.1:/tmp/marsos-src.tgz"
if ($LASTEXITCODE -ne 0) { throw "scp falhou" }

Write-Host ">> Preparando a VM (swap de 2 GB para o mksquashfs)"
$swap = 'if ! swapon --show | grep -q /swapfile; then [ -f /swapfile ] || { sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null; }; sudo swapon /swapfile; fi; free -m | head -3'
& $ssh @opt -p $Port mars@127.0.0.1 $swap

Write-Host ">> Gerando a ISO dentro da VM (o build roda destacado; quedas de SSH nao o interrompem)"
$remoto = 'set -e; sudo mkdir -p /srv/marsos/build; sudo rm -rf /srv/marsos/src; sudo mkdir -p /srv/marsos/src; ' +
          'sudo tar -m -xzf /tmp/marsos-src.tgz -C /srv/marsos/src; ' +
          'sudo rsync -a --delete --exclude=/cache/ --exclude=/chroot/ --exclude=/binary/ --exclude=/.build/ ' +
          '--exclude=/*.iso* --exclude=/build.log /srv/marsos/src/ /srv/marsos/build/; ' +
          'cd /srv/marsos/build; sudo rm -f .marsos-status construir.out; ' +
          'sudo setsid nohup bash -c ''bash ./build.sh > construir.out 2>&1; echo $? > .marsos-status'' > /dev/null 2>&1 < /dev/null &'
& $ssh @opt -p $Port mars@127.0.0.1 $remoto
if ($LASTEXITCODE -ne 0) { throw "nao consegui iniciar o build na VM" }

$ultima = ""
while ($true) {
    Start-Sleep -Seconds 30
    $r = & $ssh @opt -p $Port -o ConnectTimeout=60 mars@127.0.0.1 'cat /srv/marsos/build/.marsos-status 2>/dev/null; echo ===; sudo grep -a -E ''^(P|E): '' /srv/marsos/build/construir.out | tail -n 1' 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Host "   (VM ocupada, tentando de novo...)"; continue }
    $partes = ($r -join "`n") -split "==="
    $status = $partes[0].Trim()
    $linha = if ($partes.Count -gt 1) { $partes[1].Trim() } else { "" }
    if ($linha -and $linha -ne $ultima) { Write-Host "   $linha"; $ultima = $linha }
    if ($status -ne "") {
        if ($status -ne "0") { throw "o build falhou (codigo $status) - veja /srv/marsos/build/build.log na VM" }
        Write-Host ">> Pronto: marsos-1.0-amd64.hybrid.iso"
        break
    }
}

Write-Host ">> Copiando a ISO para saida\"
$saida = Join-Path $Raiz "saida"
New-Item -ItemType Directory -Force $saida | Out-Null
& $scp @opt -P $Port "mars@127.0.0.1:/srv/marsos/build/marsos-1.0-amd64.hybrid.iso" $saida
& $scp @opt -P $Port "mars@127.0.0.1:/srv/marsos/build/marsos-1.0-amd64.hybrid.iso.sha256" $saida
Get-Item (Join-Path $saida "marsos-1.0-amd64.hybrid.iso") | Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB)}}
