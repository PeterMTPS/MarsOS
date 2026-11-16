#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
marsi18n - traducao dos apps do MarsOS (portugues <-> ingles).

O idioma vem do LANG da sessao (en_* = ingles; o resto = portugues).
Uso:  from marsi18n import _, num   ->   _("Fechar")  /  num(21.8, 1)
"""
import os


def _detectar():
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        valor = os.environ.get(var, "")
        if valor and valor not in ("C", "POSIX", "C.UTF-8"):
            return "en" if valor.lower().startswith("en") else "pt"
    try:
        with open("/etc/marsos/idioma", encoding="ascii") as f:
            return "en" if f.read().strip() == "en" else "pt"
    except OSError:
        return "pt"


IDIOMA = _detectar()

EN = {
    # estacoes
    "Primavera": "Spring", "Verão": "Summer", "Outono": "Autumn", "Inverno": "Winter",
    # sol / relogio
    "MarsOS · Relógio Marciano": "MarsOS · Mars Clock",
    "Sol marciano (MSD) ": "Mars Sol Date (MSD) ",
    "Hora coordenada (MTC) ": "Coordinated Mars Time ",
    "Ano marciano ": "Mars year ",
    "Longitude solar (Ls) ": "Solar longitude (Ls) ",
    "Estação ": "Season ",
    "{n} no norte · {s} no sul": "{n} in the north · {s} in the south",
    "{h} (hora local)": "{h} (local time)",
    "Terra (UTC) ": "Earth (UTC) ",
    "Sol {sol} · {mtc} MTC · Ano {ano} · {est} no norte": "Sol {sol} · {mtc} MTC · Year {ano} · {est} in the north",
    "HORA EM MARTE": "TIME ON MARS",
    "Relógio Marciano": "Mars Clock",
    "Sol marciano (MSD)": "Mars Sol Date (MSD)",
    "Ano marciano": "Mars year",
    "Longitude solar (Ls)": "Solar longitude (Ls)",
    "Estação (norte / sul)": "Season (north / south)",
    "Terra (UTC)": "Earth (UTC)",
    "%d/%m/%Y %H:%M:%S": "%Y-%m-%d %H:%M:%S",
    "Fechar": "Close",
    # marsfetch
    "Sistema": "System", "Ligado há": "Uptime", "Pacotes": "Packages", "Janelas": "Windows",
    "Memória": "Memory", "Disco (/)": "Disk (/)", "Estação": "Season",
    "console (digite startx)": "console (type startx)",
    "{sol} · {mtc} MTC · ano {ano}": "{sol} · {mtc} MTC · year {ano}",
    "{est} no norte": "{est} in the north",
    # globo
    "M A R T E": "M A R S", "Globo de Marte": "Mars Globe",
    "Sol {sol}  ·  {mtc} MTC\nAno marciano {ano}  ·  {est} (norte)":
        "Sol {sol}  ·  {mtc} MTC\nMars year {ano}  ·  {est} (north)",
    # sobre
    "Sobre o MarsOS": "About MarsOS",
    "Um Linux retrô com a\npoeira vermelha de Marte.": "A retro Linux covered\nin red Martian dust.",
    "Arquivos": "Files", "Navegador": "Browser",
    "Feito com software livre.": "Made with free software.",
    # energia
    "Desligar": "Shut down", "Reiniciar": "Restart",
    "Desligar o MarsOS agora?": "Shut down MarsOS now?",
    "Reiniciar o MarsOS agora?": "Restart MarsOS now?",
    "Na sessão live, o que não foi salvo\nnum disco será perdido.":
        "In the live session, anything not saved\nto a disk will be lost.",
    "Cancelar": "Cancel",
    # volume
    "Nenhuma saída\nde som": "No sound\noutput", "Mudo": "Mute", "Mais...": "More...",
    # configuracoes
    "Configurações do MarsOS": "MarsOS Settings",
    "Aparência": "Appearance", "Tela": "Display", "Som": "Sound", "Teclado": "Keyboard",
    "Data e hora": "Date & time", "Rede": "Network",
    "Órbita": "Orbit", "Crepúsculo em Gale": "Dusk at Gale", "Meio-dia em Jezero": "Noon at Jezero",
    "Noite em Olympus": "Night at Olympus",
    "Papel de parede": "Wallpaper",
    "O papel de parede escolhido fica salvo para as próximas vezes.": "Your wallpaper choice is saved for next time.",
    "Não consegui ler as informações da tela.": "Could not read the display information.",
    "Resolução atual: {r}": "Current resolution: {r}",
    "Escolha a resolução": "Choose a resolution",
    "Resolução {r} aplicada e salva.": "Resolution {r} applied and saved.",
    "Não foi possível usar essa resolução.": "Could not use that resolution.",
    "Pronto: na próxima vez o MarsOS escolhe a resolução sozinho.":
        "Done: next time MarsOS picks the resolution automatically.",
    "Aplicar resolução": "Apply resolution", "Voltar ao automático": "Back to automatic",
    "Saída de som: {s}": "Sound output: {s}",
    "Nenhuma saída de som encontrada. Numa máquina virtual, ligue o áudio nas configurações da VM.":
        "No sound output found. In a virtual machine, enable audio in the VM settings.",
    "Volume": "Volume", "Sem som (mudo)": "Mute", "Testar som": "Test sound",
    "Ouvir o som de inicialização": "Play the startup sound", "Sons do sistema": "System sounds",
    "Som de inicialização ligado.": "Startup sound on.", "Som de inicialização desligado.": "Startup sound off.",
    "Tocar o som de inicialização do MarsOS": "Play the MarsOS startup sound",
    "Mixer avançado (alsamixer)": "Advanced mixer (alsamixer)", "Mixer de som": "Sound mixer",
    "Layout do teclado": "Keyboard layout", "Teclado: {t}.": "Keyboard: {t}.",
    "Não foi possível trocar o teclado.": "Could not change the keyboard layout.",
    "Teste aqui": "Try it here",
    "Ação, coração, pão e maçã em Marte": "The quick brown fox jumps over Mars",
    "Português (Brasil) - ABNT2": "Portuguese (Brazil) - ABNT2", "Inglês (EUA)": "English (US)",
    "Inglês (EUA) internacional, com acentos": "English (US) international, with dead keys",
    "Português (Portugal)": "Portuguese (Portugal)", "Espanhol": "Spanish",
    "Velocidade do ponteiro": "Pointer speed", "Mouse ajustado.": "Mouse updated.",
    "1 = devagar     3 = normal     5 = rápido": "1 = slow     3 = normal     5 = fast",
    "Botões": "Buttons", "Mouse para canhotos (troca os botões)": "Left-handed mouse (swap buttons)",
    "Dicas": "Tips",
    "• Segure Alt e arraste qualquer parte de uma janela para movê-la.":
        "• Hold Alt and drag any part of a window to move it.",
    "• Clique duas vezes no título para maximizar.": "• Double-click the title bar to maximize.",
    "• Clique no fundo da tela para abrir o menu do MarsOS.": "• Click the desktop to open the MarsOS menu.",
    "Em Marte: sol {sol}, {mtc} MTC, ano marciano {ano}": "On Mars: sol {sol}, {mtc} MTC, Mars year {ano}",
    "Fuso horário": "Time zone", "Fuso atual: {f}": "Current time zone: {f}",
    "Fuso horário: {f}.": "Time zone: {f}.",
    "Não foi possível mudar o fuso (precisa de permissão de administrador).":
        "Could not change the time zone (administrator permission needed).",
    "Aplicar fuso horário": "Apply time zone",
    "Brasília (São Paulo, Rio, Sul, Nordeste)": "Brasília (São Paulo, Rio, South, Northeast)",
    "Portugal (Lisboa)": "Portugal (Lisbon)", "UTC (tempo universal)": "UTC (universal time)",
    "Nova York (EUA, leste)": "New York (US Eastern)", "Chicago (EUA, centro)": "Chicago (US Central)",
    "Los Angeles (EUA, Pacífico)": "Los Angeles (US Pacific)", "Londres (Reino Unido)": "London (UK)",
    "Conexões": "Connections", "conectado": "connected", "desconectado": "disconnected",
    "indisponível": "unavailable", "não gerenciado": "unmanaged", "conectando...": "connecting...",
    "cabo": "wired", "interno": "internal",
    "Nenhuma placa de rede encontrada.": "No network adapter found.",
    "O NetworkManager não respondeu.": "NetworkManager did not respond.",
    "Ações": "Actions", "Configurar rede e Wi-Fi (nmtui)": "Set up network and Wi-Fi (nmtui)",
    "Atualizar": "Refresh",
    "Este computador": "This computer",
    "{u} de {t} MiB em uso": "{u} of {t} MiB in use",
    "{u} de {t} GiB usados": "{u} of {t} GiB used",
    "Sistema:  {v}": "System:   {v}", "Base:     {v}": "Base:     {v}", "Kernel:   {v}": "Kernel:   {v}",
    "Memória:  {v}": "Memory:   {v}", "Espaço:   {v}": "Disk:     {v}",
    "Persistência: LIGADA — seus arquivos e programas ficam salvos.":
        "Persistence: ON — your files and programs are kept.",
    "Persistência: desligada — tudo some ao desligar. Use \"MarsOS com persistência\" no menu de boot para salvar.":
        "Persistence: off — everything is lost at shutdown. Choose \"MarsOS with persistence\" in the boot menu to keep your files.",
    "Ferramentas": "Tools", "Monitor do sistema": "System monitor", "Terminal de root": "Root terminal",
    "Atualizar lista de programas": "Update package lists",
    "Sons de eventos (abrir e fechar janelas, avisos, capturas de tela)":
        "Event sounds (opening and closing windows, alerts, screenshots)",
    "Sons de eventos ligados.": "Event sounds on.", "Sons de eventos desligados.": "Event sounds off.",
    "Idioma / Language": "Language / Idioma",
    "Este já é o idioma da sessão.": "This is already the session language.",
    "Idioma salvo. Reinicie a sessão para usar o novo idioma.":
        "Language saved. Restart the session to use it.",
    "Reiniciar a sessão": "Restart session",
    "Reiniciar a sessão fecha todos os programas abertos.": "Restarting the session closes all open programs.",
    "Instalado no disco — seus arquivos e programas ficam salvos.":
        "Installed on disk — your files and programs are kept.",
    "Licença": "License",
    "Digite sua senha no terminal para mudar o fuso.": "Type your password in the terminal to change the time zone.",
    # sinal Terra-Marte
    "Distância da Terra ": "Distance from Earth ", "Distância da Terra": "Distance from Earth",
    "Atraso do sinal ": "Signal delay ", "Atraso do sinal": "Signal delay", "UA": "AU",
    "(ida e volta: {d})": "(round trip: {d})", "Sinal": "Signal", "{d} até a Terra": "{d} to Earth",
    "Conjunção solar: o Sol está entre a Terra e Marte e atrapalha o rádio.":
        "Solar conjunction: the Sun is between Earth and Mars and disrupts the radio.",
    # bandeja (rede e bateria)
    "Rede: desconectada": "Network: disconnected", "Rede: {t}": "Network: {t}", "LAN": "LAN",
    "Configurações de rede": "Network settings", "A conexão de rede caiu.": "The network connection dropped.",
    "Conectado à rede ({t}).": "Connected to the network ({t}).",
    "Bateria: {p}%": "Battery: {p}%", "Bateria fraca": "Low battery",
    "Restam {p}%. Ligue o carregador.": "{p}% left. Plug in the charger.",
    "{t} para encher": "{t} until full", "{t} restantes": "{t} left",
    "carregando": "charging", "descarregando": "discharging", "cheia": "full",
    "Volume: sem saída de som": "Volume: no sound output", "Volume: {p}%": "Volume: {p}%", "mudo": "mute",
    "Configurações de som": "Sound settings",
    # controle da missao e correio para Marte
    "Controle da Missão": "Mission Control", "CONTROLE DA MISSÃO": "MISSION CONTROL",
    "Missões ativas": "Active missions", "Correio para Marte": "Mail to Mars",
    "amanhecer": "dawn", "dia": "day", "entardecer": "dusk", "noite": "night",
    "%d/%m/%Y": "%Y-%m-%d", "Para:": "To:", "Transmitir": "Transmit", "Ler": "Read", "você": "you",
    "Cratera {local} · pousou em {data}": "{local} crater · landed {data}",
    "Hora local {h} · {parte}": "Local time {h} · {parte}",
    "Atraso do sinal Terra → Marte: {d}": "Earth → Mars signal delay: {d}",
    "Distância: {km} milhões de km · ida e volta: {d}": "Distance: {km} million km · round trip: {d}",
    "Conjunção solar: o Sol atrapalha o rádio, os comandos estão suspensos.":
        "Solar conjunction: the Sun disrupts the radio, commands are on hold.",
    "Escreva uma mensagem primeiro.": "Write a message first.",
    "Transmitindo para {rover}: chega em {d}.": "Transmitting to {rover}: arrives in {d}.",
    "a caminho, chega em {t}": "on its way, arrives in {t}",
    "entregue, resposta em {t}": "delivered, reply in {t}", "resposta recebida": "reply received",
    "Nenhuma mensagem ainda. Escreva acima e clique em Transmitir.":
        "No messages yet. Write one above and click Transmit.",
    "Você → {rover} ({hora}): «{texto}»": "You → {rover} ({hora}): «{texto}»",
    "A resposta ainda está a caminho...": "The reply is still on its way...",
    "Mensagem entregue em Marte": "Message delivered on Mars",
    "Chegou a {rover} ({local}, sol {sol}, {hora}). A resposta volta em {d}.":
        "It reached {rover} ({local}, sol {sol}, {hora}). The reply comes back in {d}.",
    "Resposta de {rover}": "Reply from {rover}",
    "Uso: correio-marte [perseverance|curiosity] MENSAGEM": "Usage: correio-marte [perseverance|curiosity] MESSAGE",
    "Nenhuma mensagem ainda. Mande uma: correio-marte \"olá, Marte!\"":
        "No messages yet. Send one: correio-marte \"hello, Mars!\"",
    "Transmitindo para {rover}... a mensagem chega em {d} (às {hora}).":
        "Transmitting to {rover}... the message arrives in {d} (at {hora}).",
    "A resposta volta {d} depois. Você recebe um aviso na tela.":
        "The reply comes back {d} later. You'll get a notice on screen.",
    "a caminho de Marte — chega em {t}": "on its way to Mars — arrives in {t}",
    "entregue — a resposta chega em {t}": "delivered — the reply arrives in {t}",
    "Mensagem recebida no sol {sol}, às {hora} em {local}.": "Message received on sol {sol}, at {hora} in {local}.",
    "Bom dia de Marte: o Sol nasceu há pouco e estou aquecendo os instrumentos.":
        "Good morning from Mars: the Sun just rose and I'm warming up my instruments.",
    "É tarde em {local} e estou {atividade}.": "It's afternoon in {local} and I'm {atividade}.",
    "O Sol está se pondo — em Marte o pôr do sol é azul.": "The Sun is setting — on Mars, sunsets are blue.",
    "Aqui é noite: estou guardando energia até o amanhecer.": "It's night here: I'm saving energy until dawn.",
    "Sua mensagem viajou {km} milhões de km em {d}.": "Your message travelled {km} million km in {d}.",
    "Abraços de Marte! — {rover}": "Greetings from Mars! — {rover}",
    "Tocar vídeo ou música": "Play a video or music", "Vídeos e músicas": "Videos and music",
    "Todos os arquivos": "All files",
    "Tema de sons": "Sound theme", "Tema de sons: {t}.": "Sound theme: {t}.",
    "Marte de verdade": "Real Mars", "Clássico": "Classic",
    "Clássico (chiptune feito para o MarsOS)": "Classic (chiptune made for MarsOS)",
    "Marte de verdade (gravações da NASA: vento, laser do Perseverance, Ingenuity)":
        "Real Mars (NASA recordings: wind, Perseverance's laser, Ingenuity)",
    # jogo
    "Pouso Marciano": "Mars Touchdown",
    "Pouse a sonda em Marte sem fazer uma cratera nova.": "Land the probe on Mars without making a new crater.",
    "←  →    girar a sonda": "←  →    rotate the probe", "↑ ou Espaço    motor": "↑ or Space    engine",
    "P  pausa      M  som      Esc  sair": "P  pause      M  sound      Esc  quit",
    "Pouse com menos de {vy} m/s na vertical, {vx} m/s de lado e {a}° de inclinação.":
        "Touch down under {vy} m/s vertically, {vx} m/s sideways and {a}° of tilt.",
    "Recorde: {p} pontos": "High score: {p} points", "ENTER para começar": "ENTER to start",
    "ALTITUDE": "ALTITUDE", "VEL. VERT.": "VERT. SPEED", "VEL. HORIZ.": "HORIZ. SPEED",
    "ÂNGULO": "ANGLE", "COMBUSTÍVEL": "FUEL", "PONTOS  {p}": "SCORE  {p}", "Local {n}: {nome}": "Site {n}: {nome}",
    "Vento {s} {v} m/s²": "Wind {s} {v} m/s²", "Sem vento": "No wind", "Sondas  ": "Probes  ",
    "Recorde {p}": "Best   {p}", "Terra": "Earth",
    "Pouse numa plataforma: devagar e reto.": "Land on a pad: slow and level.",
    "POUSO CONFIRMADO": "TOUCHDOWN CONFIRMED", "{local} · sol {sol} · {mtc} MTC": "{local} · sol {sol} · {mtc} MTC",
    "+{g} pontos (plataforma x{m}, {c}% de combustível)": "+{g} points (x{m} pad, {c}% fuel left)",
    "A notícia chega à Terra em {d}.": "The news reaches Earth in {d}.",
    "ENTER: próximo local": "ENTER: next site", "CRATERA NOVA": "NEW CRATER",
    "A sonda tombou e bateu o casco.": "The probe tipped over and hit its hull.",
    "Torta demais: mais de {a}°.": "Too tilted: more than {a}°.",
    "Rápido demais: {v} m/s na vertical.": "Too fast: {v} m/s vertically.",
    "Andando de lado: {v} m/s.": "Drifting sideways: {v} m/s.",
    "Fora da plataforma: o terreno é irregular.": "Missed the pad: the ground is too rough.",
    "Sondas restantes: {n}": "Probes left: {n}", "ENTER: tentar de novo": "ENTER: try again",
    "FIM DE JOGO": "GAME OVER", "Pontos: {p}": "Score: {p}", "NOVO RECORDE!": "NEW HIGH SCORE!",
    "Recorde: {p}": "High score: {p}", "ENTER: voltar ao início": "ENTER: back to the start", "PAUSA": "PAUSED",
}

DIAS = {"pt": ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"],
        "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
MESES = {"pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
                "outubro", "novembro", "dezembro"],
         "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                "October", "November", "December"]}


def _(texto: str) -> str:
    return EN.get(texto, texto) if IDIOMA == "en" else texto


def num(valor: float, casas: int = 1) -> str:
    """Numero decimal no formato do idioma (21,8 / 21.8)."""
    s = f"{valor:.{casas}f}"
    return s if IDIOMA == "en" else s.replace(".", ",")


def milhar(n: int) -> str:
    """Separador de milhar do idioma (54.343 / 54,343)."""
    s = f"{n:,}"
    return s if IDIOMA == "en" else s.replace(",", ".")


def data_extenso(t) -> str:
    """t = time.struct_time  ->  'sábado, 14 de novembro de 2026' / 'Saturday, November 14, 2026'."""
    dia = DIAS[IDIOMA][t.tm_wday]
    mes = MESES[IDIOMA][t.tm_mon - 1]
    if IDIOMA == "en":
        return f"{dia}, {mes} {t.tm_mday}, {t.tm_year}"
    return f"{dia}, {t.tm_mday} de {mes} de {t.tm_year}"
