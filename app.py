import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos
from io import BytesIO

st.set_page_config(page_title="Conciliador Autotrac", layout="wide")
st.title("🔗 Conciliação de Notas e Duplicatas")

uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    relatorio = conciliar_lancamentos(uploaded_file)

    if not relatorio.empty:
        st.subheader("📊 Relatório de Conciliação")
        st.dataframe(relatorio)

        # Exporta para Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            relatorio.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Baixar relatório em Excel",
            data=output,
            file_name="relatorio_conciliacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum vínculo encontrado com os critérios atuais.")
