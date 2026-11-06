# Checklist documental com IA

Agente que confere os documentos de um processo de benefício social contra a lista de exigências do programa e devolve uma tabela de pendências, item a item, com a evidência e a regra de cada um.

> Demonstração com um programa e processos **fictícios**. Não use documentos reais de cidadãos.

## O problema

No Controle Interno, conferir se um processo de benefício tem todos os documentos exigidos é demorado e varia de analista para analista. Este projeto mostra, com dados inventados, a abordagem que uso no trabalho: a IA organiza a conferência e aponta o que falta; a decisão continua com o analista.

## Como funciona

1. O analista envia os PDFs do processo.
2. O texto de cada PDF é extraído com `pypdf`.
3. O Claude recebe as exigências (`exigencias.json`) e os documentos, e é obrigado a responder por uma ferramenta com esquema fixo: uma linha por exigência, com status **Atendido**, **Pendente** ou **Verificar** e a evidência encontrada.
4. O código confere a resposta: exigência que o modelo pulou ou status fora da lista vira **Verificar**, nunca "Atendido".
5. A tela mostra a tabela, um resumo e o tempo da análise, e permite baixar o CSV.

## Executar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
set ANTHROPIC_API_KEY=sua_chave   # Linux/Mac: export ANTHROPIC_API_KEY=sua_chave
python gerar_exemplos.py          # cria dois processos fictícios em exemplos/
streamlit run app.py
```

Envie os PDFs de `exemplos/processo_completo` e depois os de `exemplos/processo_com_pendencias` para comparar.

O modelo pode ser trocado pela variável `CLAUDE_MODEL`.

## Adaptar para outro programa

Edite `exigencias.json`: cada item tem `id`, `documento`, `regra` e, se necessário, `observacao` (por exemplo, "certidão positiva com efeito de negativa é aceita").

## Testes

```bash
pytest
```

Os testes simulam a API, então rodam sem chave e sem internet.

## Estrutura

```
app.py              # interface Streamlit
checklist.py        # extração de texto, prompt, chamada ao Claude e validação da resposta
exigencias.json     # exigências do programa fictício
gerar_exemplos.py   # gera os PDFs fictícios
tests/              # testes com cliente simulado
```

## Limitações

- PDFs escaneados (imagem) não têm texto extraível; o item aparece como **Verificar**.
- A ferramenta não substitui a análise: ela organiza a conferência para o analista decidir.

Feito por Danila Moraes com o apoio do Claude.
