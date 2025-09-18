import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos
from io import BytesIO

# ✅ Configuração da página
st.set_page_config(
    page_title="Ferreira Lima Contabilidade Digital",
    page_icon="📊",
    layout="centered"
)

# ✅ Cabeçalho com logo e nome
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://copilot.microsoft.com/th/id/BCO.ce40fb3b-b861-4175-b43b-9f5108be73e1.png", width=100)
with col2:
    st.markdown("## **Ferreira Lima Contabilidade Digital**")
    st.markdown("#### Sistema inteligente de conciliação de notas e duplicatas")

st.markdown("---")

# ✅ Upload do arquivo
uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    relatorio = conciliar_lancamentos(uploaded_file)

    if not relatorio.empty:
        st.subheader("📊 Relatório de Conciliação")
        st.dataframe(relatorio)

        # ✅ Exporta para Excel em memória
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
