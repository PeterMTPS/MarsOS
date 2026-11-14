#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_som.py - sintetiza os sons do MarsOS (estilo chiptune, sem bibliotecas externas).

  inicio.wav  - som de inicializacao (~3,5 s): zumbido grave + arpejo em la menor com eco
  teste.wav   - "plim" curto para testar a saida de som
  aviso.wav   - dois toques descendentes

Uso:  python3 assets/gerar_som.py
"""
import math
import struct
import wave
from pathlib import Path

TAXA = 22050
DESTINO = Path(__file__).resolve().parent.parent / "config" / "includes.chroot" / "usr" / "share" / "marsos" / "sons"


def nota(nome):
    """'A4' -> frequencia em Hz."""
    idx = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}[nome[0]]
    if "#" in nome:
        idx += 1
    oitava = int(nome[-1])
    return 440.0 * 2 ** ((idx + 12 * (oitava - 4)) / 12)


def pulso(f, t, duty=0.25):
    """Onda quadrada com bordas suavizadas (menos aspera)."""
    fase = (f * t) % 1.0
    v = 1.0 if fase < duty else -1.0
    return v * 0.6 + 0.4 * math.sin(2 * math.pi * f * t)


def triangulo(f, t):
    fase = (f * t) % 1.0
    return 4 * abs(fase - 0.5) - 1


def renderizar(dur, eventos, drone=None, eco=(0.0, 0.0)):
    n = int(dur * TAXA)
    buf = [0.0] * n
    if drone:
        f0, amp = drone
        for i in range(n):
            t = i / TAXA
            env = min(1.0, t / 0.8) * min(1.0, (dur - t) / 1.2)
            vib = 1 + 0.003 * math.sin(2 * math.pi * 5 * t)
            buf[i] += amp * env * (math.sin(2 * math.pi * f0 * vib * t)
                                   + 0.5 * math.sin(2 * math.pi * (f0 * 1.005) * t)
                                   + 0.25 * math.sin(2 * math.pi * f0 * 2 * t))
    for inicio, f, d, amp, forma in eventos:
        a = int(inicio * TAXA)
        for j in range(int(d * TAXA)):
            if a + j >= n:
                break
            t = j / TAXA
            env = min(1.0, t / 0.005) * math.exp(-t * 6.0 / d)
            onda = pulso(f, t) if forma == "p" else triangulo(f, t) if forma == "t" else math.sin(2 * math.pi * f * t)
            buf[a + j] += amp * env * onda
    atraso, ganho = eco
    if ganho:
        k = int(atraso * TAXA)
        for i in range(k, n):
            buf[i] += buf[i - k] * ganho
    # passa-baixa simples para tirar a aspereza
    saida, ant = [], 0.0
    for v in buf:
        ant = ant + 0.35 * (v - ant)
        saida.append(ant)
    pico = max(1e-6, max(abs(v) for v in saida))
    return [v / pico * 0.7 for v in saida]


def salvar(nome, amostras):
    DESTINO.mkdir(parents=True, exist_ok=True)
    with wave.open(str(DESTINO / f"{nome}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in amostras))
    print(f"  {nome}.wav ({len(amostras) / TAXA:.1f} s)")


def main():
    print("Gerando sons do MarsOS...")
    # Inicializacao: arpejo subindo em la menor, resolve num acorde com brilho
    seq = ["A3", "C4", "E4", "A4", "G4", "E4", "C5", "B4", "A4"]
    ev = [(0.25 + i * 0.17, nota(n), 0.45, 0.32, "p") for i, n in enumerate(seq)]
    fim = 0.25 + len(seq) * 0.17
    ev += [(fim, nota("A4"), 1.6, 0.30, "t"), (fim, nota("E5"), 1.6, 0.22, "t"),
           (fim, nota("A5"), 1.6, 0.14, "s"), (fim + 0.35, nota("E6"), 0.8, 0.08, "s")]
    salvar("inicio", renderizar(fim + 1.9, ev, drone=(nota("A2"), 0.22), eco=(0.27, 0.35)))
    salvar("teste", renderizar(0.7, [(0.0, nota("E5"), 0.3, 0.5, "t"), (0.12, nota("A5"), 0.5, 0.5, "t")],
                               eco=(0.11, 0.25)))
    salvar("aviso", renderizar(0.6, [(0.0, nota("A5"), 0.25, 0.5, "p"), (0.16, nota("E5"), 0.35, 0.5, "p")]))
    print("Pronto.")


if __name__ == "__main__":
    main()
