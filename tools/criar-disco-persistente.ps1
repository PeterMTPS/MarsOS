# MarsOS - cria um disco de persistencia para a VM de teste.
# Com ele, ao escolher "MarsOS com persistencia" no boot, downloads, arquivos e
# programas instalados continuam la depois de reiniciar.
#
# Usa a VM construtora para formatar o disco (ext4 com o rotulo "persistence").
# As duas VMs precisam estar desligadas.
#
# Uso:  powershell -ExecutionPolicy Bypass -File tools\criar-disco-persistente.ps1 [-TamanhoMB 8192]
param([int]$TamanhoMB = 8192, [string]$VmTeste = "MarsOS-Teste", [int]$Port = 2222)

$ErrorActionPreference = 'Continue'
$VB  = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$Vc  = "MarsOS-Construtora"
$ssh = "$env:WINDIR\System32\OpenSSH\ssh.exe"
$opt = @("-i", "$env:USERPROFILE\.ssh\marsos_builder",
         "-o", "UserKnownHostsFile=$env:USERPROFILE\.ssh\marsos_known_hosts",
         "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes", "-p", "$Port")

function Estado($vm) { (& $VB showvminfo $vm --machinereadable | Select-String '^VMState=').ToString() }
function VB { & $VB @args; if ($LASTEXITCODE -ne 0) { throw "VBoxManage falhou: $args" } }

foreach ($vm in $Vc, $VmTeste) {
    if ((Estado $vm) -match 'running|paused|starting') { throw "Desligue a VM $vm antes de rodar este script." }
}

$raizVMs = (& $VB list systemproperties | Select-String 'Default machine folder:\s+(.*)').Matches[0].Groups[1].Value.Trim()
$disco = Join-Path $raizVMs "MarsOS-Persistencia.vdi"
if (Test-Path $disco) { throw "O disco ja existe: $disco" }

Write-Host ">> Criando o disco de $TamanhoMB MB"
VB createmedium disk --filename $disco --size $TamanhoMB --format VDI
VB storageattach $Vc --storagectl SATA --port 1 --device 0 --type hdd --medium $disco

Write-Host ">> Formatando pela VM construtora"
VB startvm $Vc --type headless
for ($i = 0; $i -lt 60; $i++) {
    & $ssh @opt -o ConnectTimeout=5 mars@127.0.0.1 true 2>$null
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 5
}
$bytes = [int64]$TamanhoMB * 1MB
# Confere o tamanho de /dev/sdb antes de formatar, para nunca tocar no disco errado
# (sem aspas duplas: o PowerShell 5.1 as estraga ao passar argumentos para o ssh.exe)
$cmd = 'set -e; [ $(lsblk -dnbo SIZE /dev/sdb) = ' + $bytes + ' ] || { echo DISCO_ERRADO; exit 3; }; ' +
       'echo , | sudo sfdisk -q /dev/sdb; sleep 2; ' +
       'sudo mkfs.ext4 -q -F -L persistence /dev/sdb1; sudo mkdir -p /mnt/p; sudo mount /dev/sdb1 /mnt/p; ' +
       'echo / union | sudo tee /mnt/p/persistence.conf; sudo umount /mnt/p; sudo systemctl poweroff'
& $ssh @opt mars@127.0.0.1 $cmd
$ok = ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 255)   # 255 = conexao fechada pelo poweroff

for ($i = 0; $i -lt 30 -and (Estado $Vc) -match 'running'; $i++) { Start-Sleep -Seconds 2 }
if ((Estado $Vc) -match 'running') { & $VB controlvm $Vc poweroff | Out-Null; Start-Sleep 2 }
VB storageattach $Vc --storagectl SATA --port 1 --device 0 --medium none
if (-not $ok) { throw "A formatacao falhou; o disco foi desanexado da construtora: $disco" }

Write-Host ">> Ligando o disco na VM de teste"
& $VB storagectl $VmTeste --name SATA --add sata --controller IntelAhci --portcount 1 2>$null | Out-Null
VB storageattach $VmTeste --storagectl SATA --port 0 --device 0 --type hdd --medium $disco
Write-Host ">> Pronto. No menu de boot da VM escolha: MarsOS com persistencia"
