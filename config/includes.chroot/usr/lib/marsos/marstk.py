#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""marstk - pecas comuns dos apps Tk do MarsOS (cores, fontes, planeta girando)."""
from __future__ import annotations

import os
import tkinter as tk

FUNDO = "#1a1117"
NOITE = "#3d2836"
ROCHA = "#51323e"
CARMIM = "#ac2f44"
VERMELHO = "#e54438"
LARANJA = "#ff8933"
AMBAR = "#ffb45e"
AREIA = "#e8c9a8"
CREME = "#fff1dc"

FONTE = "xos4 Terminus"   # nome da familia no fontconfig (xfonts-terminus)
LOGO_DIR = "/usr/share/marsos/logo"


def janela(classe: str, titulo: str) -> tk.Tk:
    root = tk.Tk(className=classe)
    root.title(titulo)
    root.configure(bg=FUNDO)
    try:
        root.iconphoto(True, tk.PhotoImage(file=os.path.join(LOGO_DIR, "marte-48.png")))
    except tk.TclError:
        pass
    root.option_add("*Font", (FONTE, -16))
    root.option_add("*Background", FUNDO)
    root.option_add("*Foreground", AREIA)
    root.option_add("*Button.Background", ROCHA)
    root.option_add("*Button.activeBackground", VERMELHO)
    root.option_add("*Button.activeForeground", CREME)
    root.option_add("*Button.relief", "raised")
    root.option_add("*Button.borderWidth", 2)
    return root


class PlanetaGirando:
    """Anima os quadros do logo (o Marte girando) num Canvas."""

    def __init__(self, canvas: tk.Canvas, x: int, y: int, zoom: int = 2):
        self.canvas = canvas
        self.quadros = []
        pasta = os.path.join(LOGO_DIR, "quadros")
        try:
            nomes = sorted(n for n in os.listdir(pasta) if n.endswith(".png"))
            self.atraso = int(open(os.path.join(pasta, "duracao")).read().strip() or 170)
        except (OSError, ValueError):
            nomes, self.atraso = [], 170
        for n in nomes:
            img = tk.PhotoImage(file=os.path.join(pasta, n))
            self.quadros.append(img.zoom(zoom) if zoom > 1 else img)
        if not self.quadros:
            img = tk.PhotoImage(file=os.path.join(LOGO_DIR, "marte-100.png"))
            self.quadros.append(img.zoom(zoom) if zoom > 1 else img)
        self.item = canvas.create_image(x, y, image=self.quadros[0])
        self.i = 0
        self._passo()

    def _passo(self):
        self.i = (self.i + 1) % len(self.quadros)
        self.canvas.itemconfig(self.item, image=self.quadros[self.i])
        self.canvas.after(self.atraso, self._passo)


def estrelas(canvas: tk.Canvas, largura: int, altura: int, n: int = 70, semente: int = 4):
    import random
    rnd = random.Random(semente)
    for _ in range(n):
        x, y = rnd.randrange(largura), rnd.randrange(altura)
        cor = rnd.choice((CREME, AREIA, AMBAR, "#8fb0d9", ROCHA, ROCHA))
        canvas.create_rectangle(x, y, x + 1, y + 1, outline="", fill=cor)
