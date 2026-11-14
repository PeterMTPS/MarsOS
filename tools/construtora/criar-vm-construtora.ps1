# MarsOS - cria a VM "construtora" (Debian 13 minimo) no VirtualBox, sem interacao.
# Depois de pronta, acesse com:  ssh -p 2222 -i ~/.ssh/marsos_builder mars@127.0.0.1
#
# Uso:  powershell -ExecutionPolicy Bypass -File tools\construtora\criar-vm-construtora.ps1

param(
    [string]$Iso    = "$env:USERPROFILE\VirtualBox VMs\_isos\debian-13.7.0-amd64-netinst.iso",
    [string]$VmName = "MarsOS-Construtora",
    [int]$MemoryMB  = 1536,
    [int]$Cpus      = 4,
    [int]$DiskMB    = 30720,
    [int]$SshPort   = 2222
)

$ErrorActionPreference = 'Stop'
$VB  = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$Key = "$env:USERPROFILE\.ssh\marsos_builder"

function VB { & $VB @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage falhou: $args" } }

if (-not (Test-Path $Iso)) { throw "ISO do Debian nao encontrada: $Iso" }
if (-not (Test-Path $Key)) {
    & "$env:WINDIR\System32\OpenSSH\ssh-keygen.exe" -t ed25519 -N '""' -C "marsos-builder" -f $Key | Out-Null
}
$pub = (Get-Content "$Key.pub" -Raw).Trim()

# Gera o preseed final com a chave publica
$vmRoot  = (& $VB list systemproperties | Select-String 'Default machine folder:\s+(.*)').Matches[0].Groups[1].Value.Trim()
$vmDir   = Join-Path $vmRoot $VmName
$work    = Join-Path $vmRoot "_construtora"
New-Item -ItemType Directory -Force $work | Out-Null
$preseed = Join-Path $work "preseed.cfg"
(Get-Content (Join-Path $PSScriptRoot "preseed.cfg") -Raw).Replace('__SSH_PUBKEY__', $pub) |
    Set-Content -Encoding ascii -NoNewline $preseed

VB createvm --name $VmName --ostype Debian13_64 --register
VB modifyvm $VmName --memory $MemoryMB --cpus $Cpus --ioapic on --graphicscontroller vmsvga --vram 16 `
    --nic1 nat --audio-enabled off --usb off --boot1 dvd --boot2 disk --boot3 none --boot4 none
VB modifyvm $VmName --natpf1 "ssh,tcp,127.0.0.1,$SshPort,,22"

$disk = Join-Path $vmDir "$VmName.vdi"
VB createmedium disk --filename $disk --size $DiskMB --format VDI
VB storagectl $VmName --name SATA --add sata --controller IntelAhci --portcount 2
VB storageattach $VmName --storagectl SATA --port 0 --device 0 --type hdd --medium $disk
VB storagectl $VmName --name IDE --add ide

VB unattended install $VmName --iso=$Iso --user=mars --password=marte `
    --full-user-name="Construtor MarsOS" --hostname=construtora.marsos.local `
    --locale=en_US --country=US --time-zone=UTC `
    --script-template=$preseed --start-vm=headless

Write-Host ""
Write-Host "Instalacao do Debian iniciada (headless). Leva ~10-20 min."
Write-Host "Teste quando terminar:  ssh -p $SshPort -i `"$Key`" mars@127.0.0.1 uname -a"
