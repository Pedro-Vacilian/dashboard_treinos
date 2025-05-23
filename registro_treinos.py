import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Registro de Treinos Avançado", layout="wide")
st.title("🏋️ Registro e Análise Avançada de Treinos")

CSV_PATH = "dados_treino_avancado.csv"

QUAL_MAP = {"Ruim": 1, "Médio": 2, "Bom": 3, "Excelente": 4}
INTENSIDADE_MAP = {"Baixa": 1, "Média": 2, "Alta": 3}

def carregar_dados():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH, parse_dates=["Data"])
    else:
        cols = ["Data", "Qualidade", "Tipo de Treino", "Duracao", "Intensidade", "Freq_Cardiaca", "Notas"]
        return pd.DataFrame(columns=cols)

def salvar_dados(df):
    df.to_csv(CSV_PATH, index=False)

def validar_entrada(tipo, duracao, freq_cardiaca):
    if not tipo.strip():
        st.warning("⚠️ O campo 'Tipo de Treino' é obrigatório.")
        return False
    if duracao <= 0:
        st.warning("⚠️ A duração deve ser maior que zero.")
        return False
    if not (30 <= freq_cardiaca <= 220):
        st.warning("⚠️ Frequência cardíaca deve estar entre 30 e 220 bpm.")
        return False
    return True

if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_dados()

with st.form("form_treino"):
    data = st.date_input("Data do Treino")
    qualidade = st.selectbox("Qualidade do Treino", list(QUAL_MAP.keys()))
    tipo = st.text_input("Tipo de Treino (ex: Cardio, Força, Jiu Jitsu)")
    duracao = st.number_input("Duração do Treino (minutos)", min_value=1, max_value=600, step=1)
    intensidade = st.selectbox("Intensidade Percebida", list(INTENSIDADE_MAP.keys()))
    freq_cardiaca = st.number_input("Frequência Cardíaca Média (bpm)", min_value=30, max_value=220, step=1)
    notas = st.text_area("Notas adicionais (opcional)")

    enviar = st.form_submit_button("Adicionar Registro")

if enviar and validar_entrada(tipo, duracao, freq_cardiaca):
    novo = pd.DataFrame({
        "Data": [data],
        "Qualidade": [qualidade],
        "Tipo de Treino": [tipo],
        "Duracao": [duracao],
        "Intensidade": [intensidade],
        "Freq_Cardiaca": [freq_cardiaca],
        "Notas": [notas]
    })
    st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
    salvar_dados(st.session_state["dados"])
    st.success("✅ Registro adicionado!")

df = st.session_state["dados"].copy()

if not df.empty:
    df["Qualidade_Num"] = df["Qualidade"].map(QUAL_MAP)
    df["Intensidade_Num"] = df["Intensidade"].map(INTENSIDADE_MAP)

    st.subheader("📋 Histórico de Treinos")
    df_display = df.copy()
    df_display["Data"] = df_display["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_display.drop(columns=["Qualidade_Num", "Intensidade_Num"]), use_container_width=True)

    st.subheader("📊 Estatísticas Gerais")
    st.write(f"📅 Total de treinos registrados: {len(df)}")
    st.write(f"⏳ Duração média: {df['Duracao'].mean():.1f} minutos")
    st.write(f"❤️ Frequência cardíaca média: {df['Freq_Cardiaca'].mean():.1f} bpm")

    st.subheader("📈 Análises")

    fig1 = px.line(df.sort_values("Data"), x="Data", y="Qualidade_Num",
                   title="Evolução da Qualidade do Treino",
                   labels={"Qualidade_Num": "Qualidade", "Data": "Data"})
    fig1.update_yaxes(tickmode="array", tickvals=[1,2,3,4], ticktext=list(QUAL_MAP.keys()))
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x="Duracao", y="Intensidade_Num", color="Tipo de Treino",
                      title="Duração x Intensidade Percebida",
                      labels={"Duracao": "Duração (min)", "Intensidade_Num": "Intensidade"})
    fig2.update_yaxes(tickmode="array", tickvals=[1,2,3], ticktext=list(INTENSIDADE_MAP.keys()))
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df, x="Tipo de Treino", y="Freq_Cardiaca",
                  title="Distribuição da Frequência Cardíaca Média por Tipo de Treino")
    st.plotly_chart(fig3, use_container_width=True)

    qual_media = df.groupby("Tipo de Treino")["Qualidade_Num"].mean().reset_index()
    qual_media["Qualidade_Média"] = qual_media["Qualidade_Num"].round(2)
    fig4 = px.bar(qual_media, x="Tipo de Treino", y="Qualidade_Média",
                  title="Qualidade Média do Treino por Tipo",
                  labels={"Qualidade_Média": "Qualidade Média"})
    st.plotly_chart(fig4, use_container_width=True)
