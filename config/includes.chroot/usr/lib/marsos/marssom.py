#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""marssom - controle de som do MarsOS (PipeWire via wpctl)."""
from __future__ import annotations

import re
import shutil
import subprocess

SONS = "/usr/share/marsos/sons"
SAIDA = "@DEFAULT_AUDIO_SINK@"


def _wpctl(*args):
    try:
        return subprocess.run(["wpctl", *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None


def volume():
    """(porcentagem, mudo) ou (None, False) se nao houver saida de som."""
    r = _wpctl("get-volume", SAIDA)
    if not r or r.returncode != 0:
        return None, False
    m = re.search(r"Volume:\s*([\d.]+)", r.stdout)
    if not m:
        return None, False
    return int(round(float(m.group(1)) * 100)), "MUTED" in r.stdout


def definir_volume(porcentagem: int):
    porcentagem = max(0, min(100, int(porcentagem)))
    _wpctl("set-volume", "-l", "1.0", SAIDA, f"{porcentagem / 100:.2f}")


def mudo(ligado: bool):
    _wpctl("set-mute", SAIDA, "1" if ligado else "0")


def nome_saida():
    """Nome da placa/saida de som padrao, ou None."""
    r = _wpctl("inspect", SAIDA)
    if not r or r.returncode != 0:
        return None
    m = re.search(r'node\.description = "([^"]+)"', r.stdout) or re.search(r'node\.nick = "([^"]+)"', r.stdout)
    return m.group(1) if m else "Saída padrão"


def tocar(nome: str, atraso: float = 0.0) -> bool:
    """Toca /usr/share/marsos/sons/<nome>.wav em segundo plano."""
    arquivo = f"{SONS}/{nome}.wav"
    for prog, extra in (("pw-play", []), ("paplay", []), ("aplay", ["-q"])):
        if shutil.which(prog):
            cmd = [prog, *extra, arquivo]
            if atraso:
                cmd = ["sh", "-c", f"sleep {atraso}; exec {' '.join(cmd)}"]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return True
    return False
