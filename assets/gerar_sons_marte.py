#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_sons_marte.py - tema de sons "Marte de verdade" do MarsOS.

Recorta trechos curtos de gravacoes reais feitas em Marte, publicadas pela NASA em
https://www.nasa.gov/sounds-from-beyond/ :
  * microfone do SuperCam, rover Perseverance: vento (sol 4) e disparos do laser (sol 12)
  * redemoinho de poeira passando sobre o Perseverance (PIA25657)
  * o helicoptero Ingenuity em voo, ouvido pelo Perseverance (30/04/2021)
Credito: NASA/JPL-Caltech/LANL/CNES/CNRS/ISAE-Supaero. Esses sons NAO sao GPL: seguem as
diretrizes de uso de midia da NASA (credito a NASA, sem sugerir endosso).

Uso:  python3 assets/gerar_sons_marte.py [pasta-cache]
      (baixa ~50 MB de WAVs da NASA na pasta-cache na primeira vez)
Saida: config/includes.chroot/usr/share/marsos/sons/marte/*.wav (22050 Hz, mono, 16 bits)
"""
import math
import pathlib
import struct
import sys
import urllib.request
import wave

TAXA = 22050
RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "config" / "includes.chroot" / "usr" / "share" / "marsos" / "sons" / "marte"
NASA = "https://www.nasa.gov/wp-content/uploads/2024/05/"
FONTES = {
    "vento": NASA + "scam-mic-sol004-run001.wav",
    "laser": NASA + "scam-mic-sol012-run001.wav",
    "redemoinho": NASA + "pia25657.wav",
    "ingenuity": NASA + "jpl-20210506-listen-to-nasas-ingenuity-helicopter-as-it-flies-on-mars.wav",
}

# som do MarsOS: (fonte, inicio s, fim s, entrada s, saida s, volume) ou lista de trechos encadeados
RECORTES = {
    "inicio": ("redemoinho", 9.0, 13.6, 0.6, 1.0, 0.75),       # redemoinho de poeira passando
    "desligar": ("vento", 19.6, 23.8, 0.8, 1.4, 0.70),         # rajada de vento em Jezero
    "teste": ("redemoinho", 11.4, 12.8, 0.1, 0.4, 0.60),
    # os disparos do laser acontecem a cada 1/3 s (0,01 / 0,345 / 0,68 s...); cada recorte pega um
    "abrir": ("laser", 1.995, 2.17, 0.002, 0.05, 0.45),        # disparo das 2,01 s
    "fechar": ("laser", 0.995, 1.17, 0.002, 0.05, 0.40),       # disparo das 1,01 s
    "minimizar": ("laser", 2.995, 3.17, 0.002, 0.05, 0.30),
    "restaurar": ("laser", 5.330, 5.505, 0.002, 0.05, 0.30),
    "captura": ("laser", 1.995, 2.52, 0.002, 0.06, 0.55),      # dois disparos seguidos
    "area": ("ingenuity", 33.0, 33.7, 0.15, 0.3, 0.40),        # o rotor do Ingenuity
    "mensagem": ("ingenuity", 30.0, 31.6, 0.3, 0.6, 0.55),     # chegou mensagem de Marte
}


def baixar(cache):
    cache.mkdir(parents=True, exist_ok=True)
    caminhos = {}
    for nome, url in FONTES.items():
        arq = cache / url.rsplit("/", 1)[1]
        if not arq.exists():
            print(f"  baixando {arq.name} da NASA...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(arq, "wb") as f:
                f.write(r.read())
        caminhos[nome] = arq
    return caminhos


def ler(caminho, ini, fim):
    """Trecho [ini, fim] em segundos -> amostras float mono na taxa original."""
    w = wave.open(str(caminho), "rb")
    ch, sw, fr = w.getnchannels(), w.getsampwidth(), w.getframerate()
    w.setpos(int(ini * fr))
    bruto = w.readframes(int((fim - ini) * fr))
    w.close()
    passo = sw * ch
    escala = float(1 << (8 * sw - 1))
    out = []
    for i in range(0, len(bruto) - passo + 1, passo):
        soma = sum(int.from_bytes(bruto[i + c * sw:i + (c + 1) * sw], "little", signed=True) for c in range(ch))
        out.append(soma / ch / escala)
    return out, fr


def reamostrar(a, de, para):
    if de == para:
        return a
    k = max(1, int(de / para))
    if k > 1:   # media em caixa como filtro anti-alias
        suav, acc = [], 0.0
        for i, v in enumerate(a):
            acc += v - (a[i - k] if i >= k else 0.0)
            suav.append(acc / min(k, i + 1))
        a = suav
    n = int(len(a) * para / de)
    out = []
    for j in range(n):
        x = j * de / para
        i = int(x)
        b = a[i + 1] if i + 1 < len(a) else a[i]
        out.append(a[i] + (b - a[i]) * (x - i))
    return out


def preparar(a, entrada, saida, volume):
    # tira o nivel DC, suaviza as pontas e normaliza
    media = sum(a) / len(a)
    a = [v - media for v in a]
    ne, ns = max(1, int(entrada * TAXA)), max(1, int(saida * TAXA))
    n = len(a)
    for i in range(min(ne, n)):
        a[i] *= 0.5 - 0.5 * math.cos(math.pi * i / ne)
    for i in range(min(ns, n)):
        a[n - 1 - i] *= 0.5 - 0.5 * math.cos(math.pi * i / ns)
    pico = max(1e-6, max(abs(v) for v in a))
    return [v / pico * volume for v in a]


def salvar(nome, amostras):
    DESTINO.mkdir(parents=True, exist_ok=True)
    with wave.open(str(DESTINO / f"{nome}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in amostras))
    print(f"  marte/{nome}.wav ({len(amostras) / TAXA:.2f} s)")


def main():
    cache = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / ".cache" / "marsos-nasa"
    print("Gerando o tema de sons 'Marte de verdade'...")
    fontes = baixar(cache)
    for nome, (fonte, ini, fim, entrada, saida, volume) in RECORTES.items():
        a, fr = ler(fontes[fonte], ini, fim)
        salvar(nome, preparar(reamostrar(a, fr, TAXA), entrada, saida, volume))
    (DESTINO / "CREDITOS").write_text(
        "Gravacoes reais feitas em Marte - NASA/JPL-Caltech/LANL/CNES/CNRS/ISAE-Supaero\n"
        "Fonte: https://www.nasa.gov/sounds-from-beyond/\n"
        "Trechos recortados por assets/gerar_sons_marte.py. Nao fazem parte da licenca GPL do MarsOS;\n"
        "seguem as diretrizes de uso de midia da NASA (credito a NASA, sem sugerir endosso).\n",
        encoding="utf-8")
    print("Pronto.")


if __name__ == "__main__":
    main()
