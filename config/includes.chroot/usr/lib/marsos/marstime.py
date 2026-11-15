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

try:
    from marsi18n import _, milhar  # noqa: F401  (milhar e reexportado)
except ImportError:  # usado fora do MarsOS
    def _(t):
        return t

    def milhar(n):
        return f"{n:,}".replace(",", ".")

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
        return _(("Primavera", "Verão", "Outono", "Inverno")[int(self.ls // 90) % 4])

    @property
    def estacao_sul(self) -> str:
        return _(("Outono", "Inverno", "Primavera", "Verão")[int(self.ls // 90) % 4])


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


# ---------------------------------------------------------------- Terra <-> Marte
# Distancia e atraso do sinal de radio, com as posicoes dos planetas calculadas pelos
# elementos orbitais do JPL ("Approximate Positions of the Planets", E. M. Standish,
# tabela 1, validos de 1800 a 2050). Erro tipico: alguns milhares de km (< 0,1 s de sinal).
#                a (UA)                     e                          I (graus)
#                L (graus)                  long. do perielio          long. do nodo
_ELEMENTOS = {
    "terra": ((1.00000261, 0.00000562), (0.01671123, -0.00004392), (-0.00001531, -0.01294668),
              (100.46457166, 35999.37244981), (102.93768193, 0.32327364), (0.0, 0.0)),
    "marte": ((1.52371034, 0.00001847), (0.09339410, 0.00007882), (1.84969142, -0.00813131),
              (-4.55343205, 19140.30268499), (-23.94362959, 0.44441088), (49.55953891, -0.29257343)),
}
UA_KM = 149597870.7
LUZ_KM_S = 299792.458


def _posicao(planeta: str, t: float) -> tuple[float, float, float]:
    """Posicao heliocentrica eclitica (UA); t = seculos julianos desde J2000."""
    (a0, a1), (e0, e1), (i0, i1), (l0, l1), (w0, w1), (n0, n1) = _ELEMENTOS[planeta]
    a, e = a0 + a1 * t, e0 + e1 * t
    inc = math.radians(i0 + i1 * t)
    longitude, perielio, nodo = l0 + l1 * t, w0 + w1 * t, n0 + n1 * t
    arg = math.radians(perielio - nodo)
    no = math.radians(nodo)
    m = math.radians((longitude - perielio) % 360.0)
    ex = m + e * math.sin(m)                       # equacao de Kepler (Newton)
    for _i in range(10):
        ex -= (ex - e * math.sin(ex) - m) / (1 - e * math.cos(ex))
    xp, yp = a * (math.cos(ex) - e), a * math.sqrt(1 - e * e) * math.sin(ex)
    ca, sa, cn, sn, ci, si = (math.cos(arg), math.sin(arg), math.cos(no), math.sin(no),
                              math.cos(inc), math.sin(inc))
    return ((ca * cn - sa * sn * ci) * xp + (-sa * cn - ca * sn * ci) * yp,
            (ca * sn + sa * cn * ci) * xp + (-sa * sn + ca * cn * ci) * yp,
            (sa * si) * xp + (ca * si) * yp)


@dataclass
class Sinal:
    ua: float           # distancia Terra-Marte
    elongacao: float    # angulo entre o Sol e Marte, visto da Terra (graus)

    @property
    def km(self) -> float:
        return self.ua * UA_KM

    @property
    def segundos(self) -> float:
        """Tempo de uma mensagem de radio (ou da luz) entre a Terra e Marte."""
        return self.km / LUZ_KM_S

    @property
    def conjuncao(self) -> bool:
        """Marte quase atras do Sol: o radio fica ruidoso e a NASA suspende os comandos."""
        return self.elongacao < 3.0

    @staticmethod
    def duracao(segundos: float) -> str:
        s = int(round(segundos))
        return f"{s // 60} min {s % 60:02d} s"


def sinal(unix: float | None = None) -> Sinal:
    if unix is None:
        unix = time.time()
    t = (2440587.5 + (unix + TT_MENOS_UTC) / 86400.0 - 2451545.0) / 36525.0
    terra, marte = _posicao("terra", t), _posicao("marte", t)
    d = [m - e for m, e in zip(marte, terra)]
    dist = math.sqrt(sum(v * v for v in d))
    r = math.sqrt(sum(v * v for v in terra))
    cos_el = sum(-e * v for e, v in zip(terra, d)) / (r * dist)
    return Sinal(ua=dist, elongacao=math.degrees(math.acos(max(-1.0, min(1.0, cos_el)))))


if __name__ == "__main__":
    h = calcular()
    s = sinal()
    print(f"MSD {h.msd:.5f}  MTC {h.mtc_hms}  Ls {h.ls:.2f}  MY {h.ano}")
    print(f"Terra-Marte {s.km:,.0f} km ({s.ua:.4f} UA)  sinal {s.duracao(s.segundos)}  elongacao {s.elongacao:.1f}")
