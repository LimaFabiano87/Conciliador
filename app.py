import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos
from io import BytesIO

st.set_page_config(
    page_title="Ferreira Lima Contabilidade Digital",
    page_icon="📊",
    layout="wide"
)

# ✅ Cabeçalho com logo e nome
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://copilot.microsoft.com/th/id/BCO.ce40fb3b-b861-4175-b43b-9f5108be73e1.png", width=100)
with col2:
    st.markdown("## **Ferreira Lima Contabilidade Digital**")
    st.markdown("#### Sistema inteligente de conciliação de notas e duplicatas")

st.markdown("---")

uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    relatorio = conciliar_lancamentos(uploaded_file)

    if not relatorio.empty:
        st.subheader("🎛️ Filtros")

        # ✅ Filtros interativos
        tipos = st.multiselect("Tipo de lançamento", options=relatorio["Confiabilidade"].unique(), default=relatorio["Confiabilidade"].unique())
        confiabilidades = st.multiselect("Confiabilidade", options=relatorio["Confiabilidade"].unique(), default=relatorio["Confiabilidade"].unique())

        min_valor = st.number_input("Valor mínimo", min_value=0.0, value=0.0)
        max_valor = st.number_input("Valor máximo", min_value=0.0, value=float(relatorio["Valor Pago"].max()))

        datas = relatorio["Data Pagamento"].dropna()
        min_data = st.date_input("Data inicial", value=datas.min())
        max_data = st.date_input("Data final", value=datas.max())

      # ✅ Aplicar filtros
relatorio["Data Pagamento"] = pd.to_datetime(relatorio["Data Pagamento"], errors="coerce")

relatorio_filtrado = relatorio[
    (relatorio["Confiabilidade"].isin(confiabilidades)) &
    (relatorio["Valor Pago"] >= min_valor) &
    (relatorio["Valor Pago"] <= max_valor) &
    (relatorio["Data Pagamento"].notnull()) &
    (relatorio["Data Pagamento"] >= pd.to_datetime(min_data)) &
    (relatorio["Data Pagamento"] <= pd.to_datetime(max_data))
]
        st.subheader("📊 Relatório de Conciliação Filtrado")
        st.dataframe(relatorio_filtrado, use_container_width=True)

        # ✅ Exportar relatório filtrado
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            relatorio_filtrado.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Baixar relatório filtrado",
            data=output,
            file_name="relatorio_conciliacao_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum vínculo encontrado com os critérios atuais.")


