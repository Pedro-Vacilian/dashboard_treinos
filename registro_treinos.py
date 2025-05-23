import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Registro de Treinos", layout="wide")
st.title("📥 Registro e Análise de Treinos do Atleta")

CSV_PATH = "dados_treino.csv"

# Função para carregar dados
def carregar_dados():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, parse_dates=["Data"])
        return df
    else:
        return pd.DataFrame(columns=["Data", "Qualidade", "Tipo de Treino", "Exercícios"])

# Inicializa dados na sessão
if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_dados()

# Formulário para entrada de dados
with st.form("form_treino"):
    data = st.date_input("Data do Treino")
    qualidade = st.selectbox("Qualidade do Treino", ["Ruim", "Médio", "Bom", "Excelente"])
    tipo = st.text_input("Tipo de Treino (ex: Jiu Jitsu, Taekwondo, Cardio)")
    exercicios = st.text_area("Exercícios realizados (descrição)")

    enviar = st.form_submit_button("Adicionar Registro")

if enviar:
    if tipo.strip() == "" or exercicios.strip() == "":
        st.warning("Por favor, preencha Tipo de Treino e Exercícios.")
    else:
        novo = pd.DataFrame({
            "Data": [data],
            "Qualidade": [qualidade],
            "Tipo de Treino": [tipo],
            "Exercícios": [exercicios]
        })
        st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
        st.session_state["dados"].to_csv(CSV_PATH, index=False)
        st.success("✅ Registro adicionado!")

df = st.session_state["dados"]

st.subheader("📋 Histórico de Treinos")
st.dataframe(df.sort_values("Data", ascending=False), use_container_width=True)

# Só mostra gráficos se tiver dados
if not df.empty:
    st.subheader("📊 Análise dos Treinos")

    # Mapear Qualidade para numérico para gráfico
    qual_map = {"Ruim": 1, "Médio": 2, "Bom": 3, "Excelente": 4}
    df["Qualidade_Num"] = df["Qualidade"].map(qual_map)

    # Gráfico linha da qualidade ao longo do tempo
    fig1 = px.line(df.sort_values("Data"), x="Data", y="Qualidade_Num",
                   title="Evolução da Qualidade do Treino",
                   labels={"Qualidade_Num": "Qualidade", "Data": "Data"})
    fig1.update_yaxes(tickmode="array", tickvals=[1,2,3,4], ticktext=["Ruim", "Médio", "Bom", "Excelente"])
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de barras dos tipos de treino
    fig2 = px.histogram(df, x="Tipo de Treino", title="Frequência por Tipo de Treino")
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico de barras da qualidade média por tipo de treino
    qual_media = df.groupby("Tipo de Treino")["Qualidade_Num"].mean().reset_index()
    qual_media["Qualidade_Média"] = qual_media["Qualidade_Num"].round(2)
    fig3 = px.bar(qual_media, x="Tipo de Treino", y="Qualidade_Média",
                  title="Qualidade Média do Treino por Tipo",
                  labels={"Qualidade_Média": "Qualidade Média"})
    st.plotly_chart(fig3, use_container_width=True)
