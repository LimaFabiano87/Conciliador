import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos

st.set_page_config(page_title="Conciliador Autotrac", layout="wide")
st.title("🔗 Conciliação de Notas e Duplicatas")

uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    relatorio = conciliar_lancamentos(uploaded_file)

    if not relatorio.empty:
        st.subheader("📊 Relatório de Conciliação")
        st.dataframe(relatorio)

        relatorio_excel = relatorio.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="📥 Baixar relatório em Excel",
            data=relatorio_excel,
            file_name="relatorio_conciliacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum vínculo encontrado com os critérios atuais.")