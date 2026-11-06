"""Gera dois processos fictícios em PDF na pasta exemplos/ (dados inventados)."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DOCS = {
    "processo_completo": {
        "01_rg.pdf": ["REGISTRO GERAL (FICTÍCIO)", "Nome: Maria Exemplo da Silva", "RG: 00.000.000-0"],
        "02_cpf.pdf": ["CADASTRO DE PESSOAS FÍSICAS (FICTÍCIO)", "Nome: Maria Exemplo da Silva", "CPF: 000.000.000-00"],
        "03_residencia.pdf": ["CONTA DE ÁGUA (FICTÍCIA)", "Titular: Maria Exemplo da Silva", "Endereço: Rua das Flores, 10 - Cidade Exemplo", "Emissão: 05/10/2026"],
        "04_renda.pdf": ["DECLARAÇÃO DE RENDA (FICTÍCIA)", "Família de 3 pessoas.", "Renda total: R$ 900,00 por mês.", "Membros: Maria (R$ 900,00), João (sem renda), Ana (sem renda)."],
        "05_relatorio_social.pdf": ["RELATÓRIO SOCIAL (FICTÍCIO)", "A família foi desalojada após chuvas em setembro de 2026", "e encontra-se em situação de vulnerabilidade social."],
        "06_locacao.pdf": ["DECLARAÇÃO DO LOCADOR (FICTÍCIA)", "Imóvel: Rua do Porto, 55 - Cidade Exemplo", "Valor do aluguel: R$ 800,00 mensais."],
        "07_certidao.pdf": ["CERTIDÃO DE PROPRIEDADE (FICTÍCIA)", "Certidão positiva com efeito de negativa", "em nome de Maria Exemplo da Silva."],
    },
    "processo_com_pendencias": {
        "01_rg.pdf": ["REGISTRO GERAL (FICTÍCIO)", "Nome: José Teste Souza", "RG: 11.111.111-1"],
        "02_residencia.pdf": ["CONTA DE LUZ (FICTÍCIA)", "Titular: José Teste Souza", "Emissão: 10/01/2026"],
        "03_renda.pdf": ["HOLERITE (FICTÍCIO)", "José Teste Souza - salário R$ 4.500,00", "Família de 2 pessoas; renda da esposa não informada."],
        "04_locacao.pdf": ["CONTRATO DE LOCAÇÃO (FICTÍCIO)", "Valor do aluguel: R$ 1.200,00 mensais."],
    },
}


def gerar(pasta: Path = Path("exemplos")) -> None:
    for processo, arquivos in DOCS.items():
        destino = pasta / processo
        destino.mkdir(parents=True, exist_ok=True)
        for nome, linhas in arquivos.items():
            c = canvas.Canvas(str(destino / nome), pagesize=A4)
            y = 800
            for linha in linhas:
                c.drawString(60, y, linha)
                y -= 22
            c.save()


if __name__ == "__main__":
    gerar()
    print("Exemplos gerados em exemplos/")
