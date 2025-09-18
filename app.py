import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos
from io import BytesIO
import plotly.express as px

st.set_page_config(
    page_title="Ferreira Lima Contabilidade Digital",
    page_icon="📊",
    layout="wide"
)

# Cabeçalho
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://copilot.microsoft.com/th/id/BCO.ce40fb3b-b861-4175-b43b-9f5108be73e1.png", width=100)
with col2:
    st.markdown("## **Ferreira Lima Contabilidade Digital**")
    st.markdown("#### Sistema inteligente de conciliação de notas e duplicatas")

st.markdown("---")

# Upload + gráfico
col_upload, col_grafico = st.columns([2, 3])
with col_upload:
    uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")
    if uploaded_file:
        st.success("Arquivo carregado com sucesso!")

with col_grafico:
    if uploaded_file:
        relatorio = conciliar_lancamentos(uploaded_file)
        if not relatorio.empty:
            totais = relatorio["Conciliado"].value_counts().reset_index()
            totais.columns = ["Status", "Quantidade"]
            tipo_grafico = st.radio("📈 Escolha o tipo de gráfico", ["Barras", "Pizza"])
            if tipo_grafico == "Barras":
                fig = px.bar(totais, x="Status", y="Quantidade", color="Status", text="Quantidade",
                             color_discrete_map={"Sim": "#2ECC71", "Não": "#E74C3C"},
                             title="Totais Conciliados vs Não Conciliados")
                fig.update_layout(title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.pie(totais, names="Status", values="Quantidade", color="Status",
                             color_discrete_map={"Sim": "#2ECC71", "Não": "#E74C3C"},
                             title="Distribuição de Conciliação")
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(title_x=0.5)
                st.plotly_chart(fig, use_container_width=True)

# Filtros
if uploaded_file and not relatorio.empty:
    st.markdown("---")
    st.subheader("🎛️ Filtros")

    relatorio["Data Pagamento"] = pd.to_datetime(relatorio["Data Pagamento"], errors="coerce")
    relatorio["Mês"] = relatorio["Data Pagamento"].dt.to_period("M").astype(str)

    confiabilidades = st.multiselect("Confiabilidade", relatorio["Confiabilidade"].unique(), default=relatorio["Confiabilidade"].unique())
    fornecedores = st.multiselect("Fornecedor", relatorio["Fornecedor"].unique(), default=relatorio["Fornecedor"].unique())
    meses = st.multiselect("Mês", relatorio["Mês"].unique(), default=relatorio["Mês"].unique())

    mostrar_nao_conciliados = st.checkbox("🔍 Mostrar apenas os que faltam conciliar", value=False)

    relatorio_filtrado = relatorio[
        (relatorio["Confiabilidade"].isin(confiabilidades)) &
        (relatorio["Fornecedor"].isin(fornecedores)) &
        (relatorio["Mês"].isin(meses))
    ]

    if mostrar_nao_conciliados:
        relatorio_filtrado = relatorio_filtrado[relatorio_filtrado["Conciliado"] == "Não"]

    st.subheader("📊 Relatório Filtrado")
    st.dataframe(relatorio_filtrado, use_container_width=True)

    # Exportação por mês
    st.download_button(
        label="📥 Baixar relatório por mês",
        data=relatorio_filtrado.to_csv(index=False).encode("utf-8"),
        file_name=f"relatorio_{meses[0] if meses else 'mensal'}.csv",
        mime="text/csv"
    )

    # Alertas automáticos
    st.markdown("---")
    st.subheader("🚨 Alertas Automáticos")

    alertas = relatorio_filtrado[
        (relatorio_filtrado["Conciliado"] == "Não") &
        (relatorio_filtrado["Valor Pago"] > 10000)
    ]

    if not alertas.empty:
        st.error(f"⚠️ {len(alertas)} lançamentos não conciliados acima de R$ 10.000 detectados.")
        st.dataframe(alertas, use_container_width=True)
    else:
        st.success("✅ Nenhum lançamento não conciliado acima de R$ 10.000.")


