from pathlib import Path
from types import SimpleNamespace

from checklist import Documento, analisar, carregar_exigencias, extrair_texto, montar_prompt
from gerar_exemplos import gerar

EXIG = carregar_exigencias(Path(__file__).parent.parent / "exigencias.json")


class ClienteFalso:
    """Simula a API sem rede: devolve uma chamada de ferramenta pronta."""

    def __init__(self, itens):
        self.itens = itens
        self.messages = self
        self.ultima_chamada = None

    def create(self, **kwargs):
        self.ultima_chamada = kwargs
        bloco = SimpleNamespace(type="tool_use", name="registrar_analise",
                                input={"itens": self.itens, "resumo": "ok"})
        return SimpleNamespace(content=[bloco])


def test_extrai_texto_dos_exemplos(tmp_path):
    gerar(tmp_path)
    doc = extrair_texto("rg", tmp_path / "processo_completo" / "01_rg.pdf")
    assert "Maria Exemplo da Silva" in doc.texto


def test_prompt_traz_todas_as_exigencias_e_documentos():
    prompt = montar_prompt(EXIG, [Documento("a.pdf", "conteúdo A")])
    for ex in EXIG["exigencias"]:
        assert ex["id"] in prompt
    assert 'nome="a.pdf"' in prompt and "conteúdo A" in prompt


def test_item_nao_analisado_vira_verificar_e_status_invalido_e_corrigido():
    cliente = ClienteFalso([{"id": "R1", "status": "Atendido", "evidencia": "01_rg.pdf"},
                            {"id": "R2", "status": "Talvez", "evidencia": "?"}])
    resultado = analisar([Documento("x.pdf", "x")], EXIG, cliente=cliente)
    por_id = {l["id"]: l for l in resultado["linhas"]}
    assert len(resultado["linhas"]) == len(EXIG["exigencias"])
    assert por_id["R1"]["status"] == "Atendido"
    assert por_id["R2"]["status"] == "Verificar"
    assert por_id["R8"]["status"] == "Verificar"
    assert cliente.ultima_chamada["tool_choice"]["name"] == "registrar_analise"
