import streamlit as st
import pandas as pd
from motor_conciliacao import conciliar_lancamentos
import plotly.express as px

st.set_page_config(page_title="Ferreira Lima Contabilidade Digital", page_icon="📊", layout="wide")

# Estilo visual centralizado
st.markdown("""
    <style>
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
        }
        .logo-container img {
            width: 140px;
        }
        .logo-container .text-block {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="logo-container">
        <img src="https://copilot.microsoft.com/th/id/BCO.ce40fb3b-b861-4175-b43b-9f5108be73e1.png">
        <div class="text-block">
            <h2>Ferreira Lima Contabilidade Digital</h2>
            <h4>Sistema inteligente de conciliação de notas e duplicatas</h4>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Upload
uploaded_file = st.file_uploader("📤 Faça upload do relatório do Domínio (.xlsx)", type="xlsx")
if uploaded_file:
    relatorio = conciliar_lancamentos(uploaded_file)
    if not relatorio.empty:
        relatorio["Conciliado Manual"] = False

        # ✅ Editor interativo
        st.subheader("📄 Lançamentos Importados")
        relatorio_editado = st.data_editor(
            relatorio,
            column_config={
                "Conciliado Manual": st.column_config.CheckboxColumn(
                    "Conciliado Manual",
                    help="Marque se você considera este lançamento conciliado"
                )
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        # ✅ Gráficos e alertas reativos lado a lado
        st.markdown("---")
        col_grafico, col_alerta = st.columns(2)

        with col_grafico:
            st.markdown("### 📊 Conciliação Automática vs Manual")

            auto_data = relatorio_editado["Conciliado"].value_counts().rename_axis("Status").reset_index(name="Quantidade")
            fig_auto = px.pie(
                auto_data,
                names="Status",
                values="Quantidade",
                title="Conciliação Automática",
                color="Status",
                color_discrete_map={"Sim": "#2ECC71", "Não": "#E74C3C"}
            )
            fig_auto.update_traces(textinfo="percent+label", textposition="inside")
            fig_auto.update_layout(title_x=0.5)
            st.plotly_chart(fig_auto, use_container_width=True)

            manual_data = relatorio_editado["Conciliado Manual"].value_counts().rename_axis("Status").reset_index(name="Quantidade")
            manual_data["Status"] = manual_data["Status"].map({True: "Conciliado", False: "Não Conciliado"})
            fig_manual = px.pie(
                manual_data,
                names="Status",
                values="Quantidade",
                title="Conciliação Manual",
                color="Status",
                color_discrete_map={"Conciliado": "#3498DB", "Não Conciliado": "#E67E22"}
            )
            fig_manual.update_traces(textinfo="percent+label", textposition="inside")
            fig_manual.update_layout(title_x=0.5)
            st.plotly_chart(fig_manual, use_container_width=True)

        with col_alerta:
            st.markdown("### 🚨 Alertas de Conciliação")

            auto_sim = relatorio_editado[relatorio_editado["Conciliado"] == "Sim"]
            auto_nao = relatorio_editado[relatorio_editado["Conciliado"] == "Não"]
            manual_sim = relatorio_editado[relatorio_editado["Conciliado Manual"] == True]
            manual_nao = relatorio_editado[relatorio_editado["Conciliado Manual"] == False]

            st.markdown("**🔄 Conciliação Automática**")
            st.metric("Conciliados", len(auto_sim))
            st.metric("Não conciliados", len(auto_nao))

            st.markdown("**📝 Conciliação Manual**")
            st.metric("Marcados como conciliados", len(manual_sim))
            st.metric("Ainda não marcados", len(manual_nao))

        # ✅ Ocultar/exibir filtros
        st.markdown("---")
        mostrar_filtros = st.checkbox("🎛️ Exibir filtros avançados", value=True)

        if mostrar_filtros:
            st.subheader("🎛️ Filtros")

            relatorio_editado["Mês"] = pd.to_datetime(relatorio_editado["Data Pagamento"], format="%d/%m/%Y", errors="coerce").dt.to_period("M").astype(str)

            def format_mes(m):
                try:
                    return pd.to_datetime(m).strftime('%B/%Y')
                except:
                    return m

            confiabilidades = st.multiselect("Confiabilidade", relatorio_editado["Confiabilidade"].unique(), default=relatorio_editado["Confiabilidade"].unique())
            fornecedores = st.multiselect("Fornecedor", relatorio_editado["Fornecedor"].unique(), default=relatorio_editado["Fornecedor"].unique())
            meses = st.multiselect("Mês", relatorio_editado["Mês"].unique(), default=relatorio_editado["Mês"].unique(), format_func=format_mes)

            filtro_manual = st.selectbox("📝 Filtrar por conciliação manual", ["Todos", "Conciliados Manualmente", "Não Conciliados Manualmente"])

            relatorio_filtrado = relatorio_editado[
                (relatorio_editado["Confiabilidade"].isin(confiabilidades)) &
                (relatorio_editado["Fornecedor"].isin(fornecedores)) &
                (relatorio_editado["Mês"].isin(meses))
            ]

            if filtro_manual == "Conciliados Manualmente":
                relatorio_filtrado = relatorio_filtrado[relatorio_filtrado["Conciliado Manual"] == True]
            elif filtro_manual == "Não Conciliados Manualmente":
                relatorio_filtrado = relatorio_filtrado[relatorio_filtrado["Conciliado Manual"] == False]

            st.subheader("📄 Lançamentos Filtrados")
            st.dataframe(relatorio_filtrado, use_container_width=True)

            st.download_button(
                label="📥 Baixar relatório por mês",
                data=relatorio_filtrado.to_csv(index=False).encode("utf-8"),
                file_name=f"relatorio_{meses[0] if meses else 'mensal'}.csv",
                mime="text/csv"
            )
