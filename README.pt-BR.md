<div align="center">

<img src="docs/img/marte-girando.gif" width="160" alt="Marte girando">

# MarsOS 1.1 "Olympus"

**Um Linux retrô com a poeira vermelha de Marte.**

🇺🇸 [English](README.md) · 🇧🇷 Português

[![Baixar a ISO](https://img.shields.io/badge/baixar-ISO-e54438?style=for-the-badge&labelColor=3d2836)](https://github.com/PeterMTPS/MarsOS/releases/latest/download/marsos-1.1-amd64.hybrid.iso)
[![Site](https://img.shields.io/badge/site-MarsOS-ff8933?style=for-the-badge&labelColor=3d2836)](https://petermtps.github.io/MarsOS/pt/)

![Debian 13](https://img.shields.io/badge/base-Debian%2013%20trixie-ac2f44?labelColor=1a1117)
![FVWM](https://img.shields.io/badge/janelas-FVWM%202.7-ac2f44?labelColor=1a1117)
![BIOS e UEFI](https://img.shields.io/badge/boot-BIOS%20%2B%20UEFI-ac2f44?labelColor=1a1117)
![amd64](https://img.shields.io/badge/arquitetura-amd64-ac2f44?labelColor=1a1117)
[![Licença: GPL 3.0](https://img.shields.io/badge/licen%C3%A7a-GPL%203.0-ac2f44?labelColor=1a1117)](LICENSE)

<img src="docs/img/desktop.png" width="820" alt="Área de trabalho do MarsOS">

</div>

---

O MarsOS é uma distribuição baseada no **Debian GNU/Linux 13** com a cara dos Linux dos
anos 90: boot em texto, janelas **FVWM**, fontes bitmap, apps Athena e Tk. Tudo pintado com
as cinco cores do planeta do logo:

![](https://img.shields.io/badge/-%233d2836-3d2836)
![](https://img.shields.io/badge/-%2351323e-51323e)
![](https://img.shields.io/badge/-%23ac2f44-ac2f44)
![](https://img.shields.io/badge/-%23e54438-e54438)
![](https://img.shields.io/badge/-%23ff8933-ff8933)

Uma ISO só, em dois idiomas: escolha **English** ou **Português** no menu de boot. Use direto
do pendrive (live) ou instale no disco.

## Telas

| Menu de boot | Pouso Marciano (jogo) |
|---|---|
| <img src="docs/img/boot.png" alt="Menu de boot"> | <img src="docs/img/jogo.png" alt="Pouso Marciano"> |
| **Menu do MarsOS** | **Relógio marciano, globo e Sobre** |
| <img src="docs/img/menu.png" alt="Menu do MarsOS"> | <img src="docs/img/apps.png" alt="Apps marcianos"> |
| **Configurações: aparência** | **Instalador** |
| <img src="docs/img/config-aparencia.png" alt="Configurações - aparência"> | <img src="docs/img/instalador.png" alt="Instalador"> |

## O que vem no sistema

| | |
|---|---|
| 🚀 **Boot** | Menu com o planeta (BIOS e UEFI) e a escolha do idioma, mensagens do kernel em texto e console com paleta marciana de 16 cores |
| 💽 **Instalador** | Instalador em modo texto com as cores de Marte (*Install MarsOS / Instalar* no menu de boot): copia o sistema para o disco, com o seu usuário |
| 🪟 **Janelas** | FVWM 2.7 com painel **MarsBar** (menu, atalhos, pager, tarefas, rede e bateria, relógio marciano e volume) e 4 áreas de trabalho: Olympus, Valles, Gale e Jezero |
| 🕰️ **Hora em Marte** | `sol`, `marsclock` e o relógio do painel: sol marciano, MTC, estação e hora local em Gale e Jezero (algoritmo Mars24 da NASA GISS) |
| 📡 **Atraso do sinal** | Distância até a Terra e quanto tempo leva uma mensagem de rádio (de 3 a 22 minutos), pelas órbitas do JPL, com aviso na conjunção solar |
| 🎮 **Pouso Marciano** | Um jogo original: pouse uma sonda em Jezero, Gale, Elysium, Valles Marineris e Olympus Mons, contra a gravidade de Marte, pouco combustível e o vento das tempestades de poeira |
| 🔊 **Som** | PipeWire, volume no painel (a rodinha do mouse ajusta), teclas de volume, som de inicialização chiptune e sons de eventos (janelas, áreas de trabalho, capturas, desligar) |
| 📸 **Captura de tela** | `Print Screen` (tela inteira), `Alt+Print` (janela), `Shift+Print` (escolher área), salvas em `~/Imagens` |
| 🔋 **Rede e bateria** | Indicador no painel de cabo / sinal do Wi-Fi / sem rede e da bateria, com avisos quando a rede cai ou a bateria fica fraca |
| ⚙️ **Configurações** | `marsos-config`: papel de parede, resolução, som, teclado, mouse, fuso horário, rede, idioma e sistema |
| 🌐 **Internet** | Firefox ESR (em português ou inglês, conforme o idioma) e o Dillo como navegador retrô; downloads em `~/Downloads` |
| 💾 **Persistência** | Opção "Persistência" no boot: arquivos e programas sobrevivem ao reinício sem instalar |
| 🖥️ **Apps** | XTerm, Xfe, Xfw, Midnight Commander, htop, vim, xcalc, xclock, xeyes, `marsfetch`, `marsos-globo` |

## Baixar e usar

1. Baixe a ISO na [página de releases](https://github.com/PeterMTPS/MarsOS/releases/latest).
2. Grave num pendrive com o [Rufus](https://rufus.ie) (modo DD) ou o [balenaEtcher](https://etcher.balena.io), ou use uma máquina virtual (VirtualBox: Debian 64-bit, 2 GB de RAM, VMSVGA, áudio HDA).
3. Dê boot e escolha **Iniciar o MarsOS - Portugues**. O login é automático como `astronauta` (senha `live`).
4. Para ficar com o MarsOS, escolha **Install MarsOS / Instalar** no menu de boot.

**Requisitos:** PC 64 bits, 1,5 GB de RAM (2 GB recomendado) e 8 GB de disco para instalar.

### Atalhos

| Tecla | Ação |
|---|---|
| Clique no fundo ou `Alt+F1` | Menu do MarsOS |
| `Alt+Tab` / `Alt+F4` | Trocar / fechar janela |
| `Ctrl+Alt+T` | Terminal |
| `Ctrl+Alt+←` / `→` | Trocar de área de trabalho |
| `Print` / `Alt+Print` / `Shift+Print` | Captura: tela / janela / área |
| `Alt` + arrastar | Mover janela |

## Gerar a ISO

### No GitHub (automático)

O workflow [Build ISO](.github/workflows/build-iso.yml) gera a ISO num contêiner Debian 13.
Criar uma tag como `v1.1` gera e publica a ISO na release; o botão **Run workflow** da aba
Actions gera e guarda a ISO para download por 7 dias.

### Numa máquina Debian 13

```bash
sudo apt install live-build
sudo ./build.sh
```

### No Windows (com VirtualBox)

```powershell
# 1. VM construtora (Debian 13 mínimo, instalado sozinho). Só uma vez:
powershell -ExecutionPolicy Bypass -File tools\construtora\criar-vm-construtora.ps1
# 2. Gera a ISO dentro da VM e traz para saida\
powershell -ExecutionPolicy Bypass -File tools\construir.ps1
# 3. Testa numa VM (use -Uefi para testar UEFI)
powershell -ExecutionPolicy Bypass -File tools\testar.ps1
# 4. (Opcional) disco de persistência para a VM de teste
powershell -ExecutionPolicy Bypass -File tools\criar-disco-persistente.ps1
```

### Persistência num pendrive

Depois de gravar a ISO, crie no espaço livre do pendrive uma partição ext4 com o rótulo
`persistence` e coloque nela um arquivo `persistence.conf` com o conteúdo `/ union`.
Inicie com **Persistencia - Portugues**.

## Estrutura do projeto

```
auto/config                  opções do live-build (Debian 13, instalador, paleta do console)
build.sh                     gera a ISO
.github/workflows/           build automático da ISO no GitHub Actions
config/package-lists/        pacotes do sistema
config/hooks/live/           ajustes finais dentro do sistema
config/includes.chroot/      arquivos copiados para o sistema
  etc/skel/                  FVWM (menus em textos.en e textos.pt), XTerm, bash e Xfe do usuário
  usr/local/bin/             apps marcianos (sol, marsfetch, marsclock, marsos-config, marsos-pouso...)
  usr/lib/marsos/            marstime, marssom, marsconf, marstk e marsi18n (traduções)
  usr/share/marsos/          papéis de parede, ícones, sons, logo e quadros da animação
config/includes.installer/   respostas padrão do instalador (preseed)
assets/logo/                 o logo (PNG, GIF girando e sprites)
assets/gerar_arte.py         gera papéis de parede, splash, ícones e o /etc/issue a partir do logo
assets/gerar_som.py          sintetiza os sons do sistema e do jogo
assets/boot/                 menus de boot (isolinux e GRUB)
docs/                        site de download (GitHub Pages)
tools/                       scripts do Windows (VM construtora, build, teste)
```

## Licença

O código, os menus, a arte e os sons do MarsOS são software livre sob a
[GNU General Public License 3.0](LICENSE) (ou qualquer versão posterior). Os pacotes que vêm
do Debian mantêm as licenças deles.

---

<div align="center">
<img src="docs/img/marte.png" width="48" alt=""><br>
Feito por <a href="https://github.com/PeterMTPS">Pedro</a> · baseado no Debian GNU/Linux · GPL 3.0
</div>
