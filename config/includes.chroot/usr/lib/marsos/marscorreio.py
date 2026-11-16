#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
marscorreio - "Correio para Marte" do MarsOS.

Uma mensagem para um rover viaja na velocidade da luz: chega a Marte depois do atraso
real do sinal naquele momento (marstime.sinal) e a "resposta" do rover volta depois do
mesmo tempo. A resposta usa o sol da missao e a hora local no rover quando a mensagem
chegou. As mensagens ficam em ~/.config/marsos/correio.json.
"""
from __future__ import annotations

import json
import os
import random
import time

import marstime

try:
    from marsi18n import IDIOMA, _, milhar
except ImportError:  # pragma: no cover
    IDIOMA = "pt"

    def _(t):
        return t

    def milhar(n):
        return f"{n:,}".replace(",", ".")

ARQUIVO = os.path.expanduser("~/.config/marsos/correio.json")
LIMITE = 140


def ler() -> list[dict]:
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
        return dados if isinstance(dados, list) else []
    except (OSError, ValueError):
        return []


def salvar(mensagens: list[dict]):
    os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
    temp = ARQUIVO + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=1)
    os.replace(temp, ARQUIVO)


def enviar(para: str, texto: str, agora: float | None = None) -> dict:
    agora = time.time() if agora is None else agora
    m = marstime.missao(para)
    msg = {"id": f"{int(agora * 1000)}", "para": m["nome"], "texto": texto.strip()[:LIMITE],
           "enviado": agora, "atraso": marstime.sinal(agora).segundos,
           "avisou_chegada": False, "avisou_resposta": False}
    lista = ler()
    lista.append(msg)
    salvar(lista[-50:])          # guarda as 50 mais recentes
    return msg


def chegada(msg: dict) -> float:
    return msg["enviado"] + msg["atraso"]


def retorno(msg: dict) -> float:
    return msg["enviado"] + 2 * msg["atraso"]


def estado(msg: dict, agora: float | None = None) -> str:
    agora = time.time() if agora is None else agora
    if agora < chegada(msg):
        return "a_caminho"
    if agora < retorno(msg):
        return "entregue"
    return "respondida"


def contexto(msg: dict) -> dict:
    """Sol da missao, hora local e parte do dia no rover quando a mensagem chegou."""
    m = marstime.missao(msg["para"])
    t = chegada(msg)
    h = marstime.calcular(t)
    hora = h.lmst(m["longitude"])
    return {"sol": marstime.sol_da_missao(m, t), "hora": h.hms(hora)[:5], "horas": hora,
            "local": m["local"], "km": marstime.sinal(msg["enviado"]).km}


ATIVIDADES = {
    "Perseverance": ["coletando uma amostra de rocha para trazer à Terra um dia",
                     "analisando uma rocha com o laser do SuperCam",
                     "dirigindo pela borda da cratera Jezero",
                     "fotografando o antigo delta do rio"],
    "Curiosity": ["subindo o Monte Sharp, devagar e sempre",
                  "fotografando as camadas de rocha da cratera Gale",
                  "perfurando uma rocha para analisar o pó",
                  "medindo a radiação e o clima"],
}
EN = {
    "coletando uma amostra de rocha para trazer à Terra um dia": "collecting a rock sample to bring back to Earth one day",
    "analisando uma rocha com o laser do SuperCam": "zapping a rock with SuperCam's laser",
    "dirigindo pela borda da cratera Jezero": "driving along the rim of Jezero crater",
    "fotografando o antigo delta do rio": "taking pictures of the ancient river delta",
    "subindo o Monte Sharp, devagar e sempre": "climbing Mount Sharp, slow and steady",
    "fotografando as camadas de rocha da cratera Gale": "taking pictures of the rock layers in Gale crater",
    "perfurando uma rocha para analisar o pó": "drilling into a rock to analyse the powder",
    "medindo a radiação e o clima": "measuring radiation and the weather",
}


def resposta(msg: dict) -> str:
    """Texto da resposta do rover (sempre o mesmo para a mesma mensagem)."""
    c = contexto(msg)
    rnd = random.Random(msg["id"])
    atividade = rnd.choice(ATIVIDADES.get(msg["para"], ATIVIDADES["Perseverance"]))
    if IDIOMA == "en":
        atividade = EN.get(atividade, atividade)
    hh = c["horas"]
    if 6 <= hh < 11:
        situacao = _("Bom dia de Marte: o Sol nasceu há pouco e estou aquecendo os instrumentos.")
    elif 11 <= hh < 17:
        situacao = _("É tarde em {local} e estou {atividade}.").format(local=c["local"], atividade=atividade)
    elif 17 <= hh < 19.5:
        situacao = _("O Sol está se pondo — em Marte o pôr do sol é azul.")
    else:
        situacao = _("Aqui é noite: estou guardando energia até o amanhecer.")
    viagem = _("Sua mensagem viajou {km} milhões de km em {d}.").format(
        km=milhar(round(c["km"] / 1e6)), d=marstime.Sinal.duracao(msg["atraso"]))
    return (_("Mensagem recebida no sol {sol}, às {hora} em {local}.").format(
        sol=milhar(c["sol"]), hora=c["hora"], local=c["local"]) + " " + situacao + " "
            + viagem + " " + _("Abraços de Marte! — {rover}").format(rover=msg["para"]))


def pendentes(mensagens: list[dict] | None = None) -> bool:
    """Ainda falta avisar alguma chegada ou resposta?"""
    return any(not m.get("avisou_resposta") for m in (ler() if mensagens is None else mensagens))
