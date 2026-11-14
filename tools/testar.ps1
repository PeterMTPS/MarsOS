# MarsOS - liga a ISO numa VM de teste do VirtualBox.
# Uso:  powershell -ExecutionPolicy Bypass -File tools\testar.ps1 [-Uefi] [-Headless]
param(
    [string]$Iso      = (Join-Path (Split-Path -Parent $PSScriptRoot) "saida\marsos-1.0-amd64.hybrid.iso"),
    [string]$VmName   = "MarsOS-Teste",
    [int]$MemoryMB    = 1536,
    [switch]$Uefi,
    [switch]$Headless
)

$ErrorActionPreference = 'Stop'
$VB = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
function VB { & $VB @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage falhou: $args" } }

if (-not (Test-Path $Iso)) { throw "ISO nao encontrada: $Iso (rode tools\construir.ps1 antes)" }
$Iso = (Resolve-Path $Iso).Path

$existe = (& $VB list vms) -match "`"$VmName`""
if (-not $existe) {
    VB createvm --name $VmName --ostype Debian13_64 --register
    VB modifyvm $VmName --cpus 2 --ioapic on --graphicscontroller vmsvga --vram 32 `
        --nic1 nat --audio-enabled off --usb-ohci on --mouse usbtablet `
        --boot1 dvd --boot2 none --boot3 none --boot4 none
    VB storagectl $VmName --name IDE --add ide
} else {
    $estado = (& $VB showvminfo $VmName --machinereadable | Select-String '^VMState=').ToString()
    if ($estado -match 'running') { & $VB controlvm $VmName poweroff | Out-Null; Start-Sleep 2 }
}

VB modifyvm $VmName --memory $MemoryMB --firmware $(if ($Uefi) { "efi" } else { "bios" })
# Som: placa Intel HDA ligada na saida padrao do Windows
VB modifyvm $VmName --audio-enabled on --audio-driver default --audio-controller hda --audio-out on --audio-in off
VB storageattach $VmName --storagectl IDE --port 0 --device 0 --type dvddrive --medium $Iso
VB startvm $VmName --type $(if ($Headless) { "headless" } else { "gui" })
