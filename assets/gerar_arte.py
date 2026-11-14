#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_arte.py - gera toda a arte do MarsOS a partir do logo (assets/logo/):

  * papeis de parede pixel-art: orbita (padrao), crepusculo, dia, noite  (16:9 e 4:3)
  * splash 640x480 do menu de boot (isolinux e GRUB)
  * icones XPM 16x16 para o FVWM
  * quadros da animacao do planeta girando (Globo de Marte / Sobre)
  * logo em blocos para o marsfetch e para o /etc/issue

Uso:  python3 assets/gerar_arte.py
"""
from __future__ import annotations

import math
import random
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
LOGO = RAIZ / "assets" / "logo"
CHROOT = RAIZ / "config" / "includes.chroot"
SHARE = CHROOT / "usr" / "share" / "marsos"
BOOT = RAIZ / "assets" / "boot"


def hx(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# --------------------------------------------------------------------------
# Paleta (nucleo = as 5 cores do logo)
# --------------------------------------------------------------------------
LOGO_CORES = {
    "a": "#3d2836",  # sombra
    "b": "#51323e",  # rocha
    "c": "#ac2f44",  # carmim
    "d": "#e54438",  # vermelho marte
    "e": "#ff8933",  # laranja
}

PALETA = [hx(c) for c in (
    # espaco / noite
    "#07050a", "#0e0a12", "#1a1117", "#251820", "#3d2836", "#51323e",
    # crepusculo
    "#6e3a48", "#8e4a4e", "#ac2f44", "#c4543c", "#e54438", "#f06a3a", "#ff8933", "#ffb45e", "#ffd59a",
    # dia (ceu cor de caramelo)
    "#b4784e", "#d29a66", "#e8bd8a",
    # azuis do por do sol marciano
    "#26304a", "#3a4a6a", "#5a6f8c", "#8fb0d9", "#cfe0f0",
    # solo
    "#2e1a1e", "#5e2a2e", "#7a2e34", "#8a4a3a", "#c9845a", "#e8c9a8",
    "#fff1dc", "#ffffff",
)]

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def mul(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


def grad(stops, t):
    t = clamp(t)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            return mix(c0, c1, (t - p0) / (p1 - p0) if p1 > p0 else 0.0)
    return stops[-1][1]


def rampa(lista):
    return [(p, hx(c)) for p, c in lista]


_cache: dict = {}


def quantizar(c, x, y, spread=30.0):
    off = (BAYER[y & 3][x & 3] / 16.0 - 0.5) * spread
    r = int(clamp(c[0] + off, 0, 255))
    g = int(clamp(c[1] + off, 0, 255))
    b = int(clamp(c[2] + off, 0, 255))
    key = (r >> 2, g >> 2, b >> 2)
    hit = _cache.get(key)
    if hit is None:
        hit = min(PALETA, key=lambda p: 2 * (p[0] - r) ** 2 + 4 * (p[1] - g) ** 2 + 3 * (p[2] - b) ** 2)
        _cache[key] = hit
    return hit


def para_imagem(px, W, H):
    img = Image.new("RGB", (W, H))
    img.putdata([quantizar(px[y][x], x, y) for y in range(H) for x in range(W)])
    return img


class Ruido1D:
    def __init__(self, seed, n=1024):
        rnd = random.Random(seed)
        self.v = [rnd.random() for _ in range(n)]
        self.n = n

    def __call__(self, x):
        i = math.floor(x)
        f = x - i
        a = self.v[i % self.n]
        b = self.v[(i + 1) % self.n]
        return a + (b - a) * smooth(f)

    def fbm(self, x, octs=4):
        s = norm = 0.0
        amp, freq = 0.5, 1.0
        for _ in range(octs):
            s += amp * self(x * freq)
            norm += amp
            amp *= 0.5
            freq *= 2.0
        return s / norm


# --------------------------------------------------------------------------
# Fonte pixel 5x7 (so os caracteres que a arte usa)
# --------------------------------------------------------------------------
FONTE = {
    "M": ["X...X", "XX.XX", "X.X.X", "X.X.X", "X...X", "X...X", "X...X"],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    "Y": ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    "P": ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    "U": ["X...X", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "1": ["..X..", ".XX..", "..X..", "..X..", "..X..", "..X..", ".XXX."],
    "0": [".XXX.", "X...X", "X..XX", "X.X.X", "XX..X", "X...X", ".XXX."],
    ".": [".....", ".....", ".....", ".....", ".....", ".XX..", ".XX.."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}
for _g in FONTE.values():
    assert len(_g) == 7 and all(len(r) == 5 for r in _g)


def largura_texto(txt, esc):
    return len(txt) * 5 * esc + (len(txt) - 1) * esc


def desenhar_texto(img, txt, x0, y0, esc, cores, sombra=None):
    """cores: lista de 7 cores (uma por linha do glifo) - da o degrade."""
    d = ImageDraw.Draw(img)
    for passo, (dx, dy, usar_sombra) in enumerate(((esc, esc, True), (0, 0, False))):
        if usar_sombra and sombra is None:
            continue
        x = x0 + dx
        for ch in txt:
            g = FONTE[ch]
            for gy, linha in enumerate(g):
                for gx, p in enumerate(linha):
                    if p == "X":
                        cor = sombra if usar_sombra else cores[gy]
                        d.rectangle([x + gx * esc, y0 + dy + gy * esc,
                                     x + gx * esc + esc - 1, y0 + dy + gy * esc + esc - 1], fill=cor)
            x += 6 * esc


DEGRADE_LOGO = [hx(c) for c in ("#ffd59a", "#ffb45e", "#ff8933", "#ff8933", "#e54438", "#e54438", "#ac2f44")]


# --------------------------------------------------------------------------
# Logo: leitura e reducao preservando a paleta
# --------------------------------------------------------------------------
def carregar_logo():
    return Image.open(LOGO / "marte.png").convert("RGBA")


def reduzir_moda(img: Image.Image, W: int, H: int) -> Image.Image:
    """Reduz pixel-art escolhendo a cor mais frequente de cada bloco (sem cores novas)."""
    src = img.convert("RGBA")
    sw, sh = src.size
    px = src.load()
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    op = out.load()
    for ty in range(H):
        y0, y1 = int(ty * sh / H), max(int(ty * sh / H) + 1, int((ty + 1) * sh / H))
        for tx in range(W):
            x0, x1 = int(tx * sw / W), max(int(tx * sw / W) + 1, int((tx + 1) * sw / W))
            cont = Counter()
            transp = 0
            for y in range(y0, y1):
                for x in range(x0, x1):
                    p = px[x, y]
                    if p[3] < 128:
                        transp += 1
                    else:
                        cont[p[:3]] += 1
            total = transp + sum(cont.values())
            if not cont or transp > total * 0.5:
                continue
            op[tx, ty] = cont.most_common(1)[0][0] + (255,)
    return out


def logo_para_letras(img: Image.Image) -> list[str]:
    inv = {hx(v): k for k, v in LOGO_CORES.items()}
    px = img.load()
    linhas = []
    for y in range(img.size[1]):
        s = ""
        for x in range(img.size[0]):
            p = px[x, y]
            if p[3] < 128:
                s += "."
            else:
                cor = min(inv, key=lambda c: sum((a - b) ** 2 for a, b in zip(c, p[:3])))
                s += inv[cor]
        linhas.append(s)
    return linhas


# --------------------------------------------------------------------------
# Cenas
# --------------------------------------------------------------------------
PRESETS = {
    "crepusculo": dict(
        ceu=rampa([(0.0, "#0e0a12"), (0.30, "#251820"), (0.55, "#51323e"),
                   (0.75, "#8e4a4e"), (0.90, "#c4543c"), (1.0, "#ff8933")]),
        sol=(0.72, 0.565), sol_r=0.011, halo="#8fb0d9", halo_r=0.085, halo_k=0.80,
        estrelas=70, luz=0.80, tinta="#ffb45e", tinta_k=0.08, neblina="#8e4a4e",
        fobos=(0.20, 0.20), deimos=(0.40, 0.11), terra=None, rover=True, luz_dir=1),
    "dia": dict(
        ceu=rampa([(0.0, "#b4784e"), (0.55, "#d29a66"), (1.0, "#e8bd8a")]),
        sol=(0.26, 0.17), sol_r=0.012, halo="#fff1dc", halo_r=0.07, halo_k=0.55,
        estrelas=0, luz=1.15, tinta="#ffd59a", tinta_k=0.10, neblina="#d29a66",
        fobos=None, deimos=None, terra=None, rover=True, luz_dir=-1),
    "noite": dict(
        ceu=rampa([(0.0, "#07050a"), (0.65, "#0e0a12"), (0.92, "#1a1117"), (1.0, "#251820")]),
        sol=None, estrelas=480, luz=0.42, tinta="#5a6f8c", tinta_k=0.25, neblina="#1a1117",
        fobos=(0.66, 0.19), deimos=(0.31, 0.27), terra=(0.86, 0.38), rover=False, luz_dir=1),
}

ROVER = [
    "........kw..",
    "........kk..",
    ".........k..",
    "..kkkkkkkkk.",
    ".kpppppppppk",
    ".kssssssssk.",
    "kk.kk..kk.kk",
    "kk.kk..kk.kk",
]
ROVER_CORES = {"k": hx("#1a1117"), "p": hx("#51323e"), "s": hx("#8a4a3a"), "w": hx("#ffd59a")}
assert all(len(r) == 12 for r in ROVER)

HOR = 0.62


def desenhar_lua(px, W, H, cu, cv, rx, ry, luz_dir, crateras=()):
    cx, cy = cu * W, cv * H
    rxp, ryp = rx * H, ry * H
    rmp = rampa([(0.0, "#3d2836"), (0.5, "#8a4a3a"), (1.0, "#e8c9a8")])
    for y in range(int(cy - ryp) - 1, int(cy + ryp) + 2):
        for x in range(int(cx - rxp) - 1, int(cx + rxp) + 2):
            if not (0 <= x < W and 0 <= y < H):
                continue
            nx, ny = (x + 0.5 - cx) / max(rxp, 0.5), (y + 0.5 - cy) / max(ryp, 0.5)
            if nx * nx + ny * ny <= 1.0:
                lum = 0.5 + 0.5 * (nx * luz_dir * 0.8 - ny * 0.5)
                px[y][x] = grad(rmp, lum)
    for (dx, dy) in crateras:
        x, y = int(cx + dx * rxp), int(cy + dy * ryp)
        if 0 <= x < W and 0 <= y < H:
            px[y][x] = hx("#51323e")


def render_paisagem(W, H, nome, seed=7):
    P = PRESETS[nome]
    rnd = random.Random(seed)
    n1, n2, n3, n4 = (Ruido1D(seed + k) for k in range(1, 5))

    px = [[(0.0, 0.0, 0.0)] * W for _ in range(H)]
    # ceu
    for y in range(H):
        v = (y + 0.5) / H
        base = grad(P["ceu"], v / HOR)
        linha = px[y]
        for x in range(W):
            c = base
            if P["sol"]:
                su, sv = P["sol"]
                d = math.hypot(((x + 0.5) / W - su) * W / H, v - sv)
                c = mix(c, hx(P["halo"]), P["halo_k"] * math.exp(-(d / P["halo_r"]) ** 2))
                if d < P["sol_r"]:
                    c = hx("#fff8ee")
            linha[x] = c
    # estrelas
    for _ in range(int(P["estrelas"] * W * H / (480 * 270))):
        x, y = rnd.randrange(W), rnd.randrange(int(H * 0.55))
        cor = rnd.choice([hx("#fff1dc"), hx("#cfe0f0"), hx("#ffd59a")])
        px[y][x] = mix(px[y][x], cor, 0.30 + 0.70 * rnd.random() ** 2)
    if P["terra"]:
        tu, tv = P["terra"]
        x, y = int(tu * W), int(tv * H)
        for dx, dy, k in ((0, 0, 1.0), (1, 0, 0.6), (0, 1, 0.6), (-1, 0, 0.35), (0, -1, 0.35)):
            if 0 <= x + dx < W and 0 <= y + dy < H:
                px[y + dy][x + dx] = mix(px[y + dy][x + dx], hx("#cfe0f0"), k)
    if P["fobos"]:
        desenhar_lua(px, W, H, *P["fobos"], 0.020, 0.013, P["luz_dir"], crateras=((-0.3, -0.1), (0.2, 0.3)))
    if P["deimos"]:
        desenhar_lua(px, W, H, *P["deimos"], 0.006, 0.005, P["luz_dir"])

    luz, tinta, tk = P["luz"], hx(P["tinta"]), P["tinta_k"]
    neblina = hx(P["neblina"])
    ld = P["luz_dir"]

    def finalizar(c, haze=0.0):
        c = mul(c, luz)
        c = mix(c, tinta, tk)
        return mix(c, neblina, haze)

    def olympus(u):
        c, w = 0.33, 0.30
        d = abs(u - c) / w
        s = smooth(1.0 - d) ** 0.55 if d < 1 else 0.0
        if abs(u - c) < 0.022:
            s -= 0.10 * (1 - abs(u - c) / 0.022)
        return s

    mesas = [(0.06, 0.07, 0.7), (0.53, 0.10, 1.0), (0.71, 0.04, 0.55), (0.94, 0.08, 0.8)]

    def mesa(u):
        m = 0.0
        for c, w, h in mesas:
            m = max(m, h * smooth((w - abs(u - c)) / 0.015))
        return m

    def v_far(u):
        return HOR - 0.085 * olympus(u) - 0.012 * n1.fbm(u * 9) + 0.004

    def v_mid(u):
        return HOR + 0.045 - 0.065 * mesa(u) - 0.010 * n2.fbm(u * 14)

    def duna(u):
        f = u * 3.4 + 0.35 * n3.fbm(u * 3)
        crista = 1 - abs(math.sin(math.pi * f))
        return 0.6 * crista ** 1.5 + 0.4 * n3.fbm(u * 7)

    def v_dune(u):
        return 0.80 - 0.075 * duna(u)

    def v_fg(u):
        return 0.905 - 0.025 * n4.fbm(u * 3)

    r_far = rampa([(0, "#51323e"), (1, "#8e4a4e")])
    r_mid = rampa([(0, "#3d2836"), (0.5, "#5e2a2e"), (1, "#8a4a3a")])
    r_dune = rampa([(0, "#3d2836"), (0.30, "#7a2e34"), (0.55, "#ac2f44"), (0.82, "#e54438"), (1.0, "#ff8933")])
    r_fg = rampa([(0, "#251820"), (0.6, "#3d2836"), (1, "#5e2a2e")])

    # Camadas no estilo "parallax" pixel-art: cor base plana, borda superior
    # iluminada conforme a inclinacao (lado virado para o sol) e leve degrade.
    du = 3.0 / W
    camadas = (
        # funcao, rampa, neblina, ganho da inclinacao, tom base, largura da borda (px)
        (v_far, r_far, 0.55, 2.0, 0.55, 2.5),
        (v_mid, r_mid, 0.28, 3.0, 0.45, 3.0),
        (v_dune, r_dune, 0.0, 5.0, 0.42, 7.0),
        (v_fg, r_fg, 0.0, 2.0, 0.55, 2.0),
    )
    for x in range(W):
        u = (x + 0.5) / W
        for vf, rp, haze, k, base_t, borda in camadas:
            topo = vf(u)
            incl = (vf(u + du) - vf(u - du)) / (2 * du)
            lum = clamp(0.5 + incl * ld * k)
            y0 = max(0, int(topo * H))
            for y in range(y0, H):
                dpx = y + 0.5 - topo * H
                prof = clamp(dpx / (0.16 * H))
                t = base_t + (lum - 0.5) * 1.1 * math.exp(-dpx / borda)
                if dpx < 1.0 and lum > 0.5:
                    t += 0.18
                t *= 1.0 - 0.40 * prof
                if vf is v_fg:
                    t += (rnd.random() - 0.5) * 0.30
                px[y][x] = finalizar(grad(rp, clamp(t)), haze)

    # pedras no primeiro plano
    for _ in range(int(55 * W / 480)):
        u = rnd.random()
        v = v_fg(u) + 0.015 + rnd.random() * (0.99 - v_fg(u) - 0.015)
        r = 0.6 + (v - 0.9) * H * 0.045
        cx, cy = u * W, v * H
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r * 1.4), int(cx + r * 1.4) + 1):
                if 0 <= x < W and 0 <= y < H:
                    nx, ny = (x - cx) / (r * 1.4 + 0.01), (y - cy) / (r + 0.01)
                    if nx * nx + ny * ny <= 1:
                        lum = 0.55 + 0.45 * (nx * ld - ny)
                        px[y][x] = finalizar(grad(rampa([(0, "#1a1117"), (0.6, "#5e2a2e"), (1, "#8a4a3a")]), lum))

    # rover + trilhas
    if P["rover"]:
        ur = 0.80 if ld > 0 else 0.62
        cx = int(ur * W)
        base = int(v_dune(ur) * H) + 1
        for k in range(int(0.16 * W)):
            u = ur - (k + 8) / W
            y = int(v_dune(u) * H) + 2
            if k % 2 == 0 and 0 <= y < H - 2:
                for dy in (0, 2):
                    px[y + dy][int(u * W)] = mul(px[y + dy][int(u * W)], 0.55)
        for ry, linha in enumerate(ROVER):
            for rx, ch in enumerate(linha):
                if ch != ".":
                    x, y = cx - 6 + rx, base - len(ROVER) + ry
                    if 0 <= x < W and 0 <= y < H:
                        px[y][x] = mix(ROVER_CORES[ch], tinta, tk)
    return px


def render_espaco(W, H, seed=3, planeta=None, brilho=True):
    """Fundo de espaco com nebulosa, estrelas e brilho atmosferico em volta do planeta."""
    rnd = random.Random(seed)
    n1, n2 = Ruido1D(seed + 11), Ruido1D(seed + 12)
    fundo = rampa([(0, "#07050a"), (0.6, "#0e0a12"), (1, "#1a1117")])
    neb = hx("#3d2836")
    px = []
    for y in range(H):
        v = y / H
        linha = []
        for x in range(W):
            u = x / W
            c = grad(fundo, v)
            k = n1.fbm(u * 5 + v * 3) * n2.fbm(v * 6 - u * 2 + 4)
            c = mix(c, neb, clamp((k - 0.22) * 2.2) * 0.55)
            linha.append(c)
        px.append(linha)
    for _ in range(int(900 * W * H / (480 * 270))):
        x, y = rnd.randrange(W), rnd.randrange(H)
        cor = rnd.choice([hx("#fff1dc"), hx("#cfe0f0"), hx("#ffd59a"), hx("#ffb45e")])
        px[y][x] = mix(px[y][x], cor, 0.25 + 0.75 * rnd.random() ** 3)
    if planeta and brilho:
        pcx, pcy, pr = planeta
        for y in range(max(0, int(pcy - pr - 14)), min(H, int(pcy + pr + 14))):
            for x in range(max(0, int(pcx - pr - 14)), min(W, int(pcx + pr + 14))):
                d = math.hypot(x + 0.5 - pcx, y + 0.5 - pcy)
                if d > pr - 2:
                    px[y][x] = mix(px[y][x], hx("#ac2f44"), 0.55 * math.exp(-((d - pr) / 5.0) ** 2))
    return px


def ampliar(img, k):
    return img.resize((img.size[0] * k, img.size[1] * k), Image.NEAREST)


# --------------------------------------------------------------------------
# Saidas
# --------------------------------------------------------------------------
TAMANHOS = {"16x9": (480, 270), "4x3": (256, 192)}


def gerar_papeis_de_parede(logo):
    destino = SHARE / "wallpapers"
    destino.mkdir(parents=True, exist_ok=True)
    for prop, (W, H) in TAMANHOS.items():
        # orbita: o logo como planeta gigante
        lw = logo.size[0]
        cx, cy = int(W * (0.64 if prop == "16x9" else 0.58)), int(H * 0.44)
        img = para_imagem(render_espaco(W, H, planeta=(cx, cy, lw / 2 - 1)), W, H).convert("RGBA")
        img.alpha_composite(logo, (cx - lw // 2, cy - lw // 2))
        # Fobos passando
        fob = [[(0.0, 0.0, 0.0)] * 12 for _ in range(10)]
        desenhar_lua(fob, 12, 10, 0.5, 0.5, 0.42, 0.30, -1, crateras=((0.2, -0.1),))
        fx, fy = int(W * 0.18), int(H * 0.30)
        for y in range(10):
            for x in range(12):
                if fob[y][x] != (0.0, 0.0, 0.0):
                    img.putpixel((fx + x, fy + y), quantizar(fob[y][x], fx + x, fy + y) + (255,))
        cores = [hx("#51323e")] * 7
        txt = "MARSOS 1.0"
        # margem larga: em telas 16:10 o feh corta as laterais
        desenhar_texto(img, txt, W - largura_texto(txt, 1) - 30, H - 26, 1, cores)
        ampliar(img.convert("RGB"), 4).save(destino / f"orbita-{prop}.png", optimize=True)
        print("  wallpaper orbita", prop)
        for nome in PRESETS:
            ampliar(para_imagem(render_paisagem(W, H, nome), W, H), 4).save(
                destino / f"{nome}-{prop}.png", optimize=True)
            print("  wallpaper", nome, prop)


def _splash(W, H, px0, py0, tx, ty):
    logo = carregar_logo()
    lw = logo.size[0]
    cx, cy = px0 + lw // 2, py0 + lw // 2
    img = para_imagem(render_espaco(W, H, seed=21, planeta=(cx, cy, lw / 2 - 1)), W, H).convert("RGBA")
    img.alpha_composite(logo, (cx - lw // 2, cy - lw // 2))
    desenhar_texto(img, "MARSOS", tx, ty, 3, DEGRADE_LOGO, sombra=hx("#1a1117"))
    sub = "1.0 OLYMPUS"
    desenhar_texto(img, sub, tx + (largura_texto("MARSOS", 3) - largura_texto(sub, 1)) // 2,
                   ty + 30, 1, [hx("#e8c9a8")] * 7)
    return ampliar(img.convert("RGB"), 2)


def gerar_splash(logo):
    BOOT.mkdir(parents=True, exist_ok=True)
    # isolinux (BIOS): 640x480; menu fica a direita do planeta
    _splash(320, 240, 14, 58, 142, 30).save(BOOT / "splash.png", optimize=True)
    # GRUB (UEFI): 800x600
    _splash(400, 300, 18, 92, 178, 40).save(BOOT / "splash-grub.png", optimize=True)
    # caixa de selecao do menu do GRUB (9 pedacos lisos)
    tema = BOOT / "grub-pc" / "live-theme"
    tema.mkdir(parents=True, exist_ok=True)
    tamanhos = {"nw": (2, 2), "n": (1, 2), "ne": (2, 2), "w": (2, 1), "c": (1, 1),
                "e": (2, 1), "sw": (2, 2), "s": (1, 2), "se": (2, 2)}
    for nome, tam in tamanhos.items():
        Image.new("RGB", tam, hx("#e54438" if nome == "c" else "#ac2f44")).save(tema / f"select_{nome}.png")
    print("  splash 640x480 (isolinux) e 800x600 (GRUB)")


def salvar_xpm(img: Image.Image, caminho: Path, nome: str):
    img = img.convert("RGBA")
    w, h = img.size
    simbolos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*+-=@"
    cores: dict = {}
    linhas = []
    for y in range(h):
        s = ""
        for x in range(w):
            p = img.getpixel((x, y))
            k = None if p[3] < 128 else "#%02x%02x%02x" % p[:3]
            if k not in cores:
                cores[k] = "." if k is None else simbolos[len([c for c in cores if c is not None])]
            s += cores[k]
        linhas.append(s)
    out = ["/* XPM */", f"static char *{nome}[] = {{", f'"{w} {h} {len(cores)} 1",']
    for k, ch in cores.items():
        out.append(f'"{ch} c {"None" if k is None else k}",')
    out += [f'"{l}",' for l in linhas[:-1]] + [f'"{linhas[-1]}"', "};", ""]
    caminho.write_text("\n".join(out), encoding="ascii")


def gerar_icones(logo):
    destino = SHARE / "icons"
    destino.mkdir(parents=True, exist_ok=True)
    K, F, ROCHA = hx("#1a1117"), hx("#251820"), hx("#51323e")
    CARM, VERM, LAR, AREIA, CREME = hx("#ac2f44"), hx("#e54438"), hx("#ff8933"), hx("#e8c9a8"), hx("#fff1dc")

    def novo():
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        return im, ImageDraw.Draw(im)

    icones = {}
    icones["mini-marte"] = reduzir_moda(logo, 16, 16)

    im, d = novo()
    d.rectangle([0, 1, 15, 14], fill=F, outline=K)
    d.rectangle([1, 2, 14, 3], fill=ROCHA)
    d.rectangle([12, 2, 13, 3], fill=VERM)
    for p in ((3, 6), (4, 7), (5, 8), (4, 9), (3, 10)):
        d.point(p, fill=LAR)
    d.line([(7, 10), (10, 10)], fill=AREIA)
    icones["terminal"] = im

    im, d = novo()
    d.rectangle([1, 2, 6, 4], fill=hx("#c9845a"), outline=hx("#3d2836"))
    d.rectangle([1, 4, 14, 13], fill=hx("#c9845a"), outline=hx("#3d2836"))
    d.polygon([(2, 6), (15, 6), (14, 13), (1, 13)], fill=hx("#ffb45e"), outline=hx("#3d2836"))
    icones["pasta"] = im

    im, d = novo()
    d.ellipse([1, 1, 14, 14], fill=hx("#5a6f8c"), outline=K)
    d.ellipse([5, 1, 10, 14], outline=hx("#8fb0d9"))
    d.line([(2, 7), (13, 7)], fill=hx("#8fb0d9"))
    d.line([(3, 4), (12, 4)], fill=hx("#8fb0d9"))
    d.line([(3, 11), (12, 11)], fill=hx("#8fb0d9"))
    d.point((4, 3), fill=hx("#cfe0f0"))
    icones["globo"] = im

    im, d = novo()
    d.rectangle([3, 1, 12, 14], fill=CREME, outline=hx("#3d2836"))
    for y in (4, 6, 8, 10):
        d.line([(5, y), (10, y)], fill=hx("#8a4a3a"))
    d.line([(9, 13), (14, 8)], fill=LAR, width=2)
    d.point((9, 14), fill=K)
    icones["editor"] = im

    im, d = novo()
    d.arc([1, 1, 14, 14], start=300, end=240, fill=VERM, width=2)
    d.rectangle([7, 1, 8, 8], fill=LAR)
    icones["desligar"] = im

    im, d = novo()
    d.ellipse([0, 0, 15, 15], fill=ROCHA, outline=K)
    d.rectangle([7, 3, 8, 4], fill=CREME)
    d.rectangle([7, 6, 8, 12], fill=CREME)
    icones["sobre"] = im

    im, d = novo()
    d.ellipse([0, 0, 15, 15], fill=AREIA, outline=hx("#3d2836"))
    d.line([(7, 7), (7, 3)], fill=K)
    d.line([(8, 8), (11, 8)], fill=K)
    d.point((7, 8), fill=VERM)
    icones["relogio"] = im

    im, d = novo()
    d.rectangle([1, 2, 14, 11], fill=F, outline=K)
    for i, h in enumerate((5, 3, 6, 2, 4)):
        d.line([(3 + i * 2, 10 - h), (3 + i * 2, 10)], fill=VERM if i % 2 else LAR)
    d.rectangle([6, 12, 9, 13], fill=ROCHA)
    d.line([(4, 14), (11, 14)], fill=ROCHA)
    icones["sistema"] = im

    im, d = novo()
    d.rectangle([2, 4, 13, 13], fill=ROCHA, outline=K)
    d.rectangle([4, 6, 11, 11], fill=hx("#5a6f8c"))
    d.line([(7, 1), (7, 4)], fill=K)
    d.line([(4, 1), (11, 1)], fill=CARM)
    icones["rede"] = im

    im, d = novo()
    for caixa in ([6, 0, 9, 3], [6, 12, 9, 15], [0, 6, 3, 9], [12, 6, 15, 9],
                  [2, 2, 4, 4], [11, 2, 13, 4], [2, 11, 4, 13], [11, 11, 13, 13]):
        d.rectangle(caixa, fill=AREIA, outline=K)
    d.ellipse([2, 2, 13, 13], fill=AREIA, outline=K)
    d.ellipse([5, 5, 10, 10], fill=F, outline=hx("#8a4a3a"))
    d.point((4, 4), fill=CREME)
    icones["engrenagem"] = im

    im, d = novo()
    d.rectangle([1, 6, 4, 9], fill=AREIA, outline=K)
    d.polygon([(4, 6), (8, 2), (8, 13), (4, 9)], fill=AREIA, outline=K)
    d.arc([7, 4, 12, 11], start=300, end=60, fill=LAR)
    d.arc([8, 1, 15, 14], start=300, end=60, fill=VERM)
    icones["som"] = im

    im, d = novo()
    d.line([(7, 0), (7, 2)], fill=K)
    d.ellipse([3, 2, 12, 15], fill=AREIA, outline=K)
    d.line([(4, 7), (11, 7)], fill=K)
    d.line([(7, 3), (7, 7)], fill=K)
    d.rectangle([4, 4, 6, 6], fill=VERM)
    icones["mouse"] = im

    im, d = novo()
    d.rectangle([0, 4, 15, 12], fill=ROCHA, outline=K)
    for y in (6, 8):
        for x in range(2, 14, 2):
            d.point((x, y), fill=AREIA)
    d.line([(4, 10), (11, 10)], fill=AREIA)
    d.point((13, 10), fill=LAR)
    icones["teclado"] = im

    for nome, im in icones.items():
        salvar_xpm(im, destino / f"{nome}.xpm", nome.replace("-", "_"))
        im.save(destino / f"{nome}.png")   # versao PNG para os apps Tk
    print("  icones:", ", ".join(icones))


def gerar_logo_assets(logo):
    destino = SHARE / "logo"
    (destino / "quadros").mkdir(parents=True, exist_ok=True)
    logo.save(destino / "marte-100.png")
    reduzir_moda(logo, 32, 32).save(destino / "marte-32.png")
    reduzir_moda(logo, 48, 48).save(destino / "marte-48.png")
    # quadros da animacao (compostos, prontos para o Tk)
    gif = Image.open(LOGO / "marte-girando.gif")
    duracao = gif.info.get("duration", 170)
    for i in range(gif.n_frames):
        gif.seek(i)
        gif.convert("RGBA").save(destino / "quadros" / f"{i:03d}.png")
    (destino / "quadros" / "duracao").write_text(f"{duracao}\n")
    print(f"  {gif.n_frames} quadros da animacao ({duracao} ms)")
    # logo em letras (32x32) para o marsfetch
    letras = logo_para_letras(reduzir_moda(logo, 32, 32))
    (destino / "marte-32.txt").write_text("\n".join(letras) + "\n", encoding="ascii")


ANSI16 = {"a": "1;30", "b": "1;30", "c": "0;31", "d": "1;31", "e": "1;33"}


TEXTOS_ISSUE = {
    "pt": {
        2: r'\e[1;31mMarsOS 1.0 \e[0;33m"Olympus"\e[0m',
        4: r"\e[0;37mBase Debian GNU/Linux 13 - kernel \r (\m)\e[0m",
        5: r"\e[0;37mTerminal \l em \n\e[0m",
        7: r"\e[1;33mUsuário: astronauta    Senha: live\e[0m",
        8: r"\e[0;33mDepois do login digite startx para abrir as janelas.\e[0m",
    },
    "en": {
        2: r'\e[1;31mMarsOS 1.0 \e[0;33m"Olympus"\e[0m',
        4: r"\e[0;37mBased on Debian GNU/Linux 13 - kernel \r (\m)\e[0m",
        5: r"\e[0;37mTerminal \l on \n\e[0m",
        7: r"\e[1;33mUser: astronauta    Password: live\e[0m",
        8: r"\e[0;33mAfter logging in, type startx to start the windows.\e[0m",
    },
}


def gerar_issue(logo, idioma="pt"):
    """/etc/issue com o planeta em blocos (cores da paleta do console)."""
    letras = logo_para_letras(reduzir_moda(logo, 22, 11))
    texto = TEXTOS_ISSUE[idioma]
    linhas = [""]
    for i, l in enumerate(letras):
        s, atual = "  ", None
        for ch in l:
            if ch == ".":
                if atual is not None:
                    s += r"\e[0m"
                    atual = None
                s += " "
            else:
                if ANSI16[ch] != atual:
                    s += "\\e[" + ANSI16[ch] + "m"
                    atual = ANSI16[ch]
                s += "█"
        if atual is not None:
            s += r"\e[0m"
        if i in texto:
            s += "   " + texto[i]
        linhas.append(s)
    linhas += ["", ""]
    base = CHROOT if idioma == "pt" else RAIZ / "idiomas" / idioma / "config" / "includes.chroot"
    (base / "etc").mkdir(parents=True, exist_ok=True)
    (base / "etc" / "issue").write_text("\n".join(linhas), encoding="utf-8")
    print(f"  /etc/issue ({idioma})")


def main():
    logo = carregar_logo()
    print("Gerando arte do MarsOS...")
    gerar_logo_assets(logo)
    gerar_icones(logo)
    gerar_issue(logo, "pt")
    gerar_issue(logo, "en")
    gerar_splash(logo)
    gerar_papeis_de_parede(logo)
    print("Pronto.")


if __name__ == "__main__":
    main()
