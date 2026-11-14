#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
marstime - hora e data em Marte para o MarsOS.

Implementa o algoritmo do Mars24 (NASA GISS, Allison & McEwen 2000):
Mars Sol Date (MSD), Coordinated Mars Time (MTC), longitude solar (Ls),
ano marciano e hora solar media local (LMST) em qualquer longitude.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

TT_MENOS_UTC = 69.184  # segundos (37 s de leap seconds + 32,184 s) - valido desde 2017

# Perturbacoes planetarias (Allison & McEwen 2000, tabela 5)
_PBS = (
    (0.0071, 2.2353, 49.409),
    (0.0057, 2.7543, 168.173),
    (0.0039, 1.1177, 191.837),
    (0.0037, 15.7866, 21.736),
    (0.0021, 2.1354, 15.704),
    (0.0020, 2.4694, 95.528),
    (0.0018, 32.8493, 49.095),
)

DIA_SOLAR_MARTE = 1.0274912517      # dias terrestres por sol
ANO_MARCIANO_SOLS = 668.5921
MSD_INICIO_MY36 = 52292.88          # Ls = 0 do ano marciano 36 (07/02/2021)

LOCAIS = (
    ("Gale (Curiosity)", 137.4417),
    ("Jezero (Perseverance)", 77.4509),
    ("Olympus Mons", 226.2),
)


@dataclass
class HoraMarciana:
    unix: float
    msd: float
    mtc: float          # horas decimais
    ls: float           # graus
    ano: int

    @property
    def sol(self) -> int:
        return int(self.msd)

    @staticmethod
    def hms(horas: float) -> str:
        s = int(round((horas % 24) * 3600)) % 86400
        return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"

    @property
    def mtc_hms(self) -> str:
        return self.hms(self.mtc)

    def lmst(self, longitude_leste: float) -> float:
        return (self.mtc + longitude_leste / 15.0) % 24

    @property
    def estacao_norte(self) -> str:
        return ("Primavera", "Verão", "Outono", "Inverno")[int(self.ls // 90) % 4]

    @property
    def estacao_sul(self) -> str:
        return ("Outono", "Inverno", "Primavera", "Verão")[int(self.ls // 90) % 4]


def calcular(unix: float | None = None) -> HoraMarciana:
    if unix is None:
        unix = time.time()
    jd_ut = 2440587.5 + unix / 86400.0
    jd_tt = jd_ut + TT_MENOS_UTC / 86400.0
    dt = jd_tt - 2451545.0

    m = math.radians((19.3871 + 0.52402073 * dt) % 360.0)
    alfa = (270.3871 + 0.524038496 * dt) % 360.0
    pbs = sum(a * math.cos(math.radians(0.985626 * dt / tau + phi)) for a, tau, phi in _PBS)
    eq_centro = ((10.691 + 3.0e-7 * dt) * math.sin(m) + 0.623 * math.sin(2 * m)
                 + 0.050 * math.sin(3 * m) + 0.005 * math.sin(4 * m)
                 + 0.0005 * math.sin(5 * m) + pbs)
    ls = (alfa + eq_centro) % 360.0

    msd = (jd_tt - 2405522.0028779) / DIA_SOLAR_MARTE
    mtc = (24.0 * msd) % 24.0
    ano = 36 + round(((msd - MSD_INICIO_MY36) - (ls / 360.0) * ANO_MARCIANO_SOLS) / ANO_MARCIANO_SOLS)
    return HoraMarciana(unix=unix, msd=msd, mtc=mtc, ls=ls, ano=int(ano))


def milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


if __name__ == "__main__":
    h = calcular()
    print(f"MSD {h.msd:.5f}  MTC {h.mtc_hms}  Ls {h.ls:.2f}  MY {h.ano}")
