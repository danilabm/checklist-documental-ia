"""Interface Streamlit: envie os PDFs de um processo e receba a tabela de pendências."""
import time

import pandas as pd
import streamlit as st

from checklist import analisar, carregar_exigencias, extrair_texto

st.set_page_config(page_title="Checklist documental com IA", page_icon="📋", layout="wide")
st.title("📋 Checklist documental com IA")
st.caption("Demonstração com processos fictícios. Não envie documentos reais de cidadãos.")

exigencias = carregar_exigencias()
with st.expander(f"Exigências do programa: {exigencias['programa']}"):
    st.table(pd.DataFrame(exigencias["exigencias"]))

arquivos = st.file_uploader("PDFs do processo", type="pdf", accept_multiple_files=True)

if st.button("Analisar", type="primary", disabled=not arquivos):
    inicio = time.perf_counter()
    with st.spinner("Lendo documentos e analisando..."):
        documentos = [extrair_texto(a.name, a) for a in arquivos]
        resultado = analisar(documentos, exigencias)
    segundos = time.perf_counter() - inicio

    tabela = pd.DataFrame(resultado["linhas"])
    pendentes = (tabela["status"] != "Atendido").sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Exigências", len(tabela))
    c2.metric("Pendentes ou a verificar", int(pendentes))
    c3.metric("Tempo da análise", f"{segundos:.0f} s")

    st.subheader("Resultado")
    st.dataframe(tabela, use_container_width=True, hide_index=True)
    st.info(resultado["resumo"])
    st.download_button("Baixar CSV", tabela.to_csv(index=False).encode("utf-8-sig"),
                       "analise.csv", "text/csv")
    st.caption("A IA organiza a conferência; a decisão final é sempre do analista.")
