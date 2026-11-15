# MarsOS - testa o instalador numa VM com um disco vazio.
#
# Uso:  powershell -ExecutionPolicy Bypass -File tools\testar-instalacao.ps1 [-Uefi] [-Headless]
#         liga pelo DVD: escolha "Install MarsOS / Instalar" no menu de boot
#       ... -DoDisco     tira o DVD e liga pelo disco, para ver o MarsOS instalado
#       ... -Recriar     apaga a VM e o disco e comeca do zero
param(
    [string]$Iso      = (Join-Path (Split-Path -Parent $PSScriptRoot) "saida\marsos-1.1-amd64.hybrid.iso"),
    [string]$VmName   = "MarsOS-Instalacao",
    [int]$MemoryMB    = 1536,
    [int]$DiscoGB     = 10,
    [switch]$Uefi,
    [switch]$DoDisco,
    [switch]$Recriar,
    [switch]$Headless
)

$ErrorActionPreference = 'Stop'
$VB = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
function VB { & $VB @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage falhou: $args" } }
function Existe { [bool]((& $VB list vms) -match "`"$VmName`"") }

$raizVMs = (& $VB list systemproperties | Select-String 'Default machine folder:\s+(.*)').Matches[0].Groups[1].Value.Trim()
$disco = Join-Path $raizVMs "$VmName\$VmName.vdi"

if (Existe) {
    $estado = (& $VB showvminfo $VmName --machinereadable | Select-String '^VMState=').ToString()
    if ($estado -match 'running') { & $VB controlvm $VmName poweroff | Out-Null; Start-Sleep 3 }
    if ($Recriar) { VB unregistervm $VmName --delete-all }
}

if (-not (Existe)) {
    if (-not (Test-Path $Iso)) { throw "ISO nao encontrada: $Iso (rode tools\construir.ps1 antes)" }
    VB createvm --name $VmName --ostype Debian13_64 --register
    VB modifyvm $VmName --cpus 2 --ioapic on --graphicscontroller vmsvga --vram 32 `
        --nic1 nat --usb-ohci on --mouse usbtablet --boot1 dvd --boot2 disk --boot3 none --boot4 none
    VB storagectl $VmName --name SATA --add sata --portcount 2
    VB createmedium disk --filename $disco --size ($DiscoGB * 1024) --format VDI
    VB storageattach $VmName --storagectl SATA --port 0 --device 0 --type hdd --medium $disco
    VB storageattach $VmName --storagectl SATA --port 1 --device 0 --type dvddrive --medium (Resolve-Path $Iso).Path
}

VB modifyvm $VmName --memory $MemoryMB --firmware $(if ($Uefi) { "efi" } else { "bios" })
VB modifyvm $VmName --audio-enabled on --audio-driver default --audio-controller hda --audio-out on --audio-in off
if ($DoDisco) {
    VB storageattach $VmName --storagectl SATA --port 1 --device 0 --type dvddrive --medium emptydrive
} elseif (Test-Path $Iso) {
    VB storageattach $VmName --storagectl SATA --port 1 --device 0 --type dvddrive --medium (Resolve-Path $Iso).Path
}
VB startvm $VmName --type $(if ($Headless) { "headless" } else { "gui" })
