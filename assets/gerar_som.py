#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_som.py - sintetiza os sons do MarsOS (estilo chiptune, sem bibliotecas externas).

  inicio.wav  - som de inicializacao (~3,5 s): zumbido grave + arpejo em la menor com eco
  teste.wav   - "plim" curto para testar a saida de som
  aviso.wav   - dois toques descendentes
  eventos     - abrir, fechar, minimizar, restaurar, area, captura, erro, bateria,
                conectado, desconectado, desligar (baixinhos, tocados pelo FvwmEvent e apps)
  jogo        - pouso-motor, pouso-sucesso, pouso-explosao, pouso-alerta, pouso-inicio

Uso:  python3 assets/gerar_som.py
"""
import math
import random
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
    for ev in eventos:
        inicio, f, d, amp, forma = ev[:5]
        f2 = ev[5] if len(ev) > 5 else None       # glissando ate f2
        a = int(inicio * TAXA)
        fase = 0.0
        for j in range(int(d * TAXA)):
            if a + j >= n:
                break
            t = j / TAXA
            env = min(1.0, t / 0.005) * math.exp(-t * 6.0 / d)
            if f2 is None:
                onda = pulso(f, t) if forma == "p" else triangulo(f, t) if forma == "t" else math.sin(2 * math.pi * f * t)
            else:
                fase += (f + (f2 - f) * t / d) / TAXA
                onda = (pulso(1.0, fase) if forma == "p" else triangulo(1.0, fase) if forma == "t"
                        else math.sin(2 * math.pi * fase))
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


def ruido(dur, ataque=0.005, queda=6.0, filtro=0.15, semente=1, pulsos=()):
    """Ruido filtrado (motor, explosao, obturador). pulsos = [(inicio, duracao), ...]."""
    rnd = random.Random(semente)
    n = int(dur * TAXA)
    buf = [0.0] * n
    for inicio, d in (pulsos or [(0.0, dur)]):
        a = int(inicio * TAXA)
        for j in range(int(d * TAXA)):
            if a + j >= n:
                break
            t = j / TAXA
            env = min(1.0, t / ataque) * math.exp(-t * queda / d) * min(1.0, (d - t) / 0.02)
            buf[a + j] += env * (rnd.random() * 2 - 1)
    saida, ant, ant2 = [], 0.0, 0.0
    for v in buf:
        ant = ant + filtro * (v - ant)
        ant2 = ant2 + filtro * (ant - ant2)
        saida.append(ant2)
    pico = max(1e-6, max(abs(v) for v in saida))
    return [v / pico * 0.7 for v in saida]


def volume(amostras, k):
    return [v * k for v in amostras]


def somar(*faixas):
    n = max(len(f) for f in faixas)
    return [sum(f[i] for f in faixas if i < len(f)) for i in range(n)]


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

    # --- Eventos do sistema (curtos e baixos, para nao cansar)
    salvar("abrir", volume(renderizar(0.16, [(0.0, nota("E5"), 0.14, 0.5, "t", nota("A5"))]), 0.45))
    salvar("fechar", volume(renderizar(0.16, [(0.0, nota("A5"), 0.14, 0.5, "t", nota("D5"))]), 0.45))
    salvar("minimizar", volume(renderizar(0.22, [(0.0, nota("C6"), 0.2, 0.5, "s", nota("C5"))]), 0.40))
    salvar("restaurar", volume(renderizar(0.22, [(0.0, nota("C5"), 0.2, 0.5, "s", nota("C6"))]), 0.40))
    salvar("area", volume(renderizar(0.3, [(0.0, nota("E4"), 0.12, 0.5, "t"), (0.07, nota("B4"), 0.12, 0.5, "t"),
                                           (0.14, nota("E5"), 0.16, 0.5, "t")], eco=(0.06, 0.2)), 0.40))
    salvar("captura", volume(ruido(0.22, queda=9.0, filtro=0.5, semente=7, pulsos=[(0.0, 0.05), (0.09, 0.09)]), 0.55))
    salvar("erro", volume(renderizar(0.35, [(0.0, nota("A2"), 0.32, 0.5, "p"), (0.0, nota("A#2"), 0.32, 0.3, "p")]), 0.55))
    salvar("bateria", volume(renderizar(0.9, [(0.0, nota("E5"), 0.18, 0.5, "p"), (0.22, nota("C5"), 0.18, 0.5, "p"),
                                              (0.5, nota("E5"), 0.18, 0.5, "p"), (0.72, nota("C5"), 0.18, 0.5, "p")]), 0.6))
    salvar("conectado", volume(renderizar(0.4, [(0.0, nota("C5"), 0.15, 0.5, "t"), (0.1, nota("G5"), 0.25, 0.5, "t")],
                                          eco=(0.08, 0.2)), 0.5))
    salvar("desconectado", volume(renderizar(0.4, [(0.0, nota("G4"), 0.15, 0.5, "t"), (0.1, nota("C4"), 0.25, 0.5, "t")]), 0.5))
    seq = ["E5", "C5", "A4", "E4", "A3"]
    ev = [(i * 0.14, nota(n), 0.4, 0.32, "p") for i, n in enumerate(seq)]
    salvar("desligar", volume(renderizar(1.6, ev, drone=(nota("A2"), 0.15), eco=(0.2, 0.3)), 0.8))
    bipes = renderizar(0.9, [(0.15, nota("E6"), 0.12, 0.5, "s"), (0.32, nota("E6"), 0.12, 0.5, "s"),
                             (0.49, nota("B6"), 0.25, 0.5, "s")], eco=(0.09, 0.25))
    salvar("mensagem", volume(somar(bipes, volume(ruido(0.9, ataque=0.01, queda=4.0, filtro=0.6, semente=9), 0.12)), 0.6))

    # --- Jogo "Pouso Marciano"
    salvar("pouso-motor", volume(ruido(0.42, ataque=0.06, queda=0.6, filtro=0.06, semente=3), 0.55))
    salvar("pouso-explosao", ruido(1.3, ataque=0.003, queda=5.0, filtro=0.09, semente=5))
    salvar("pouso-alerta", volume(renderizar(0.3, [(0.0, nota("B5"), 0.1, 0.5, "p"), (0.15, nota("B5"), 0.1, 0.5, "p")]), 0.5))
    salvar("pouso-inicio", volume(renderizar(0.5, [(0.0, nota("A4"), 0.12, 0.4, "p"), (0.1, nota("E5"), 0.12, 0.4, "p"),
                                                   (0.2, nota("A5"), 0.25, 0.4, "p")], eco=(0.1, 0.25)), 0.7))
    seq = ["C5", "E5", "G5", "C6"]
    ev = [(i * 0.12, nota(n), 0.3, 0.35, "p") for i, n in enumerate(seq)]
    ev += [(0.5, nota("C5"), 1.0, 0.3, "t"), (0.5, nota("E5"), 1.0, 0.25, "t"), (0.5, nota("G5"), 1.0, 0.2, "t")]
    salvar("pouso-sucesso", volume(renderizar(1.7, ev, eco=(0.15, 0.3)), 0.8))
    print("Pronto.")


if __name__ == "__main__":
    main()
