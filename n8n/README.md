# Checklist documental com IA — versão n8n

Fluxo do n8n que recebe o PDF de um processo por formulário, extrai o texto, pede ao Claude a conferência item a item contra a lista de exigências e mostra as pendências na tela.

> Demonstração com programa e processos fictícios. Não envie documentos reais de cidadãos.

## Fluxo

1. **Formulário: enviar processo** — página pública do n8n para enviar o PDF.
2. **Preparar PDF** — pega o arquivo enviado e padroniza o nome.
3. **Extrair texto do PDF** — nó nativo do n8n.
4. **Montar pedido ao Claude** — junta as exigências e o texto e obriga a resposta em formato fixo (ferramenta `registrar_analise`).
5. **Chamar Claude (API Anthropic)** — requisição HTTP para a API.
6. **Interpretar e validar resposta** — item que o modelo pulou ou com status fora da lista vira "Verificar", nunca "Atendido".
7. **Mostrar resultado** — página final com a tabela de pendências e o resumo.

## Como usar

1. No n8n, menu **Workflows → Import from file** e escolha `checklist-documental-n8n.json`.
2. Crie uma credencial **Header Auth** com nome `x-api-key` e valor igual à sua chave da Anthropic, e selecione-a no nó **Chamar Claude**.
3. Abra o nó **Formulário**, copie a URL de teste e envie um PDF.

Para usar outro programa, edite a lista `EXIGENCIAS` no nó **Montar pedido ao Claude**.

Feito por Danila Moraes com o apoio do Claude.
