#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""marsconf - configuracoes do usuario do MarsOS (~/.config/marsos/config.ini)."""
from __future__ import annotations

import configparser
import os
import re
import subprocess

PASTA = os.path.expanduser("~/.config/marsos")
ARQUIVO = os.path.join(PASTA, "config.ini")

PADRAO = {
    "teclado": {"layout": "", "variante": ""},
    "mouse": {"velocidade": "3", "canhoto": "nao"},
    "tela": {"modo": ""},
    "som": {"inicio": "sim"},
}

LAYOUTS = [
    ("br", "", "Português (Brasil) - ABNT2"),
    ("us", "", "Inglês (EUA)"),
    ("us", "intl", "Inglês (EUA) internacional, com acentos"),
    ("pt", "", "Português (Portugal)"),
    ("es", "", "Espanhol"),
]

ACELERACAO = {1: "1/2", 2: "1/1", 3: "2/1", 4: "3/1", 5: "4/1"}

FUSOS = [
    ("America/Sao_Paulo", "Brasília (São Paulo, Rio, Sul, Nordeste)"),
    ("America/Manaus", "Amazonas, Roraima, Rondônia, Mato Grosso"),
    ("America/Rio_Branco", "Acre"),
    ("America/Noronha", "Fernando de Noronha"),
    ("Europe/Lisbon", "Portugal (Lisboa)"),
    ("UTC", "UTC (tempo universal)"),
]


def ler() -> configparser.ConfigParser:
    c = configparser.ConfigParser()
    c.read_dict(PADRAO)
    c.read(ARQUIVO, encoding="utf-8")
    return c


def salvar(c: configparser.ConfigParser):
    os.makedirs(PASTA, exist_ok=True)
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        c.write(f)


def rodar(cmd) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return r.returncode, r.stdout
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def abrir(cmd):
    """Abre um programa sem esperar por ele."""
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError:
        pass


# ------------------------------------------------------------------ tela
def xrandr():
    """(saida, modo_atual, [modos]) do primeiro monitor conectado."""
    _, out = rodar(["xrandr"])
    saida, atual, modos, dentro = None, None, [], False
    for linha in out.splitlines():
        if not linha.startswith(" "):
            dentro = False
            if " connected" in linha and saida is None:
                saida, dentro = linha.split()[0], True
            continue
        if dentro:
            partes = linha.split()
            if partes and re.match(r"^\d+x\d+$", partes[0]):
                if partes[0] not in modos:
                    modos.append(partes[0])
                if "*" in linha:
                    atual = partes[0]
    return saida, atual, modos


def aplicar_modo(modo: str) -> bool:
    saida, _, modos = xrandr()
    if not saida or modo not in modos:
        return False
    return rodar(["xrandr", "--output", saida, "--mode", modo])[0] == 0


# ------------------------------------------------------------------ teclado / mouse
def aplicar_teclado(layout: str, variante: str = "") -> bool:
    cmd = ["setxkbmap", layout] + (["-variant", variante] if variante else [])
    return rodar(cmd)[0] == 0


def layout_atual() -> tuple[str, str]:
    _, out = rodar(["setxkbmap", "-query"])
    lay = re.search(r"^layout:\s*(\S+)", out, re.M)
    var = re.search(r"^variant:\s*(\S+)", out, re.M)
    return (lay.group(1) if lay else "br"), (var.group(1) if var else "")


def aplicar_mouse(velocidade: int, canhoto: bool):
    rodar(["xset", "m", ACELERACAO.get(int(velocidade), "2/1"), "4"])
    rodar(["xmodmap", "-e", "pointer = 3 2 1" if canhoto else "pointer = 1 2 3"])


# ------------------------------------------------------------------ hora
def fuso_atual() -> str:
    code, out = rodar(["timedatectl", "show", "-p", "Timezone", "--value"])
    if code == 0 and out.strip():
        return out.strip()
    try:
        return os.path.realpath("/etc/localtime").split("zoneinfo/")[1]
    except IndexError:
        return "UTC"


def aplicar_fuso(fuso: str) -> bool:
    for cmd in (["timedatectl", "set-timezone", fuso], ["sudo", "-n", "timedatectl", "set-timezone", fuso]):
        if rodar(cmd)[0] == 0:
            return True
    return False


# ------------------------------------------------------------------ FVWM
def reiniciar_fvwm():
    """Reinicia o FVWM (atalho Ctrl+Alt+Shift+R) para o painel se ajustar a tela."""
    abrir(["xdotool", "key", "--clearmodifiers", "ctrl+alt+shift+r"])
