import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

st.set_page_config(page_title="Registro de Treinos", layout="wide")
st.title("🏋️ Registro e Análise de Treinos")

# CSS para melhorar visual
st.markdown("""
    <style>
        /* Esconde a coluna Qualidade_Num na tabela de dados */
        .css-1d391kg td:nth-child(5), .css-1d391kg th:nth-child(5) {
            display: none;
        }
        /* Estilo geral */
        .stApp {
            background-color: #f9fafb;
            color: #202020;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        header, footer {
            display: none;
        }
        .css-1aumxhk {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializa os dados na sessão se ainda não existir
if "dados" not in st.session_state:
    st.session_state["dados"] = pd.DataFrame(columns=["Data", "Qualidade", "Qualidade_Num", "Tipo de Treino", "Exercícios"])

# Sidebar com formulário
st.sidebar.header("📥 Preencha os dados do treino")

with st.sidebar.form("form_dados"):
    data = st.date_input("Data do Treino")
    qualidade = st.selectbox("Qualidade do Treino", options=["Ruim", "Médio", "Bom", "Excelente"])
    tipo = st.text_input("Tipo de Treino (ex: Resistência, Força, Cardio)")
    exercicios = st.text_area("Exercícios Realizados")
    enviar = st.form_submit_button("Adicionar")

if enviar:
    # Mapear qualidade para número para facilitar gráficos
    qual_num_map = {"Ruim": 1, "Médio": 2, "Bom": 3, "Excelente": 4}
    qual_num = qual_num_map[qualidade]

    novo = pd.DataFrame({
        "Data": [data],
        "Qualidade": [qualidade],
        "Qualidade_Num": [qual_num],
        "Tipo de Treino": [tipo],
        "Exercícios": [exercicios]
    })

    st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
    st.success("✅ Dados adicionados com sucesso!")

df = st.session_state["dados"]

st.subheader("📌 Histórico de Treinos")
st.dataframe(df.drop(columns=["Qualidade_Num"]), use_container_width=True)

if not df.empty:
    st.subheader("📊 Análises")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de linha da qualidade do treino ao longo do tempo
        fig1 = px.line(df, x="Data", y="Qualidade_Num", markers=True,
                       title="Qualidade do Treino ao Longo do Tempo",
                       labels={"Qualidade_Num": "Qualidade (1=Ruim, 4=Excelente)"})
        fig1.update_yaxes(tickvals=[1,2,3,4], ticktext=["Ruim", "Médio", "Bom", "Excelente"])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Gráfico de barras por tipo de treino
        tipo_count = df["Tipo de Treino"].value_counts().reset_index()
        tipo_count.columns = ["Tipo de Treino", "Contagem"]
        fig2 = px.bar(tipo_count, x="Tipo de Treino", y="Contagem",
                      title="Frequência dos Tipos de Treino",
                      labels={"Contagem": "Número de Treinos"})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📈 Evolução da Qualidade (linha) por Tipo de Treino")
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='Data:T',
        y='Qualidade_Num:Q',
        color='Tipo de Treino:N',
        tooltip=['Data', 'Qualidade', 'Tipo de Treino']
    ).properties(width=700)
    st.altair_chart(chart, use_container_width=True)
