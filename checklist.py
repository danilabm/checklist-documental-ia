"""Núcleo do agente: lê os PDFs de um processo e pede ao Claude uma análise
item a item contra a lista de exigências."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

from pypdf import PdfReader

MODELO_PADRAO = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
LIMITE_CARACTERES = 150_000

STATUS_VALIDOS = ("Atendido", "Pendente", "Verificar")

FERRAMENTA = {
    "name": "registrar_analise",
    "description": "Registra o resultado da análise documental, uma linha por exigência.",
    "input_schema": {
        "type": "object",
        "properties": {
            "itens": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "id da exigência, ex.: R1"},
                        "status": {"type": "string", "enum": list(STATUS_VALIDOS)},
                        "evidencia": {"type": "string", "description": "Arquivo e trecho que comprovam, ou o que falta."},
                    },
                    "required": ["id", "status", "evidencia"],
                },
            },
            "resumo": {"type": "string", "description": "Duas ou três frases para o analista."},
        },
        "required": ["itens", "resumo"],
    },
}


@dataclass
class Documento:
    nome: str
    texto: str


def extrair_texto(nome: str, arquivo: BinaryIO | str | Path) -> Documento:
    leitor = PdfReader(arquivo)
    paginas = [p.extract_text() or "" for p in leitor.pages]
    return Documento(nome=nome, texto="\n".join(paginas).strip())


def carregar_exigencias(caminho: str | Path = "exigencias.json") -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def montar_prompt(exigencias: dict, documentos: Iterable[Documento]) -> str:
    blocos = [f'<documento nome="{d.nome}">\n{d.texto or "[sem texto extraível — pode ser imagem escaneada]"}\n</documento>' for d in documentos]
    corpo = "\n\n".join(blocos)
    if len(corpo) > LIMITE_CARACTERES:
        corpo = corpo[:LIMITE_CARACTERES] + "\n[...texto truncado...]"
    return (
        f"Você é analista de controle interno. Programa: {exigencias['programa']}.\n"
        "Confira os documentos do processo contra CADA exigência abaixo e chame a ferramenta "
        "registrar_analise com uma linha por exigência.\n"
        "Regras: use 'Atendido' só com evidência clara no texto; 'Pendente' quando o documento falta "
        "ou contraria a regra; 'Verificar' quando há dúvida ou o texto não permite concluir. "
        "Nunca invente conteúdo que não está nos documentos.\n\n"
        f"<exigencias>\n{json.dumps(exigencias['exigencias'], ensure_ascii=False, indent=1)}\n</exigencias>\n\n"
        f"<processo>\n{corpo}\n</processo>"
    )


def interpretar_resposta(resposta, exigencias: dict) -> dict:
    """Extrai o resultado da chamada da ferramenta e junta com a lista de exigências."""
    entrada = next(
        (b.input for b in resposta.content if getattr(b, "type", "") == "tool_use" and b.name == "registrar_analise"),
        None,
    )
    if entrada is None:
        raise ValueError("O modelo não devolveu a análise estruturada.")
    por_id = {i["id"]: i for i in entrada.get("itens", [])}
    linhas = []
    for ex in exigencias["exigencias"]:
        item = por_id.get(ex["id"], {"status": "Verificar", "evidencia": "O modelo não analisou este item."})
        status = item["status"] if item["status"] in STATUS_VALIDOS else "Verificar"
        linhas.append({"id": ex["id"], "exigencia": ex["documento"], "regra": ex["regra"],
                       "status": status, "evidencia": item.get("evidencia", "")})
    return {"linhas": linhas, "resumo": entrada.get("resumo", "")}


def analisar(documentos: list[Documento], exigencias: dict, cliente=None, modelo: str = MODELO_PADRAO) -> dict:
    if cliente is None:
        import anthropic
        cliente = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente
    resposta = cliente.messages.create(
        model=modelo,
        max_tokens=4000,
        tools=[FERRAMENTA],
        tool_choice={"type": "tool", "name": "registrar_analise"},
        messages=[{"role": "user", "content": montar_prompt(exigencias, documentos)}],
    )
    return interpretar_resposta(resposta, exigencias)
