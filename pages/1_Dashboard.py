from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from auth import exigir_login, fazer_logout
from db.queries import gasto_por_categoria_mes, listar_grupos
from utils import formatar_moeda

usuario = exigir_login()

st.set_page_config(page_title="Dashboard", page_icon="💰", layout="wide")

with st.sidebar:
    st.write(f"Olá, **{usuario['nome']}**")
    if st.button("Sair"):
        fazer_logout()
        st.switch_page("app.py")

st.title("📊 Dashboard")

hoje = date.today()
col_ano, col_mes = st.columns(2)
ano = col_ano.number_input("Ano", value=hoje.year, step=1)
meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes = col_mes.selectbox("Mês", range(1, 13), index=hoje.month - 1, format_func=lambda m: meses_nomes[m - 1])

grupos = listar_grupos(usuario["id"])
nomes_grupos = ["Todos"] + [g["nome"] for g in grupos]
grupo_selecionado = st.selectbox("Filtrar por grupo", nomes_grupos)

dados = gasto_por_categoria_mes(usuario["id"], ano, mes)
if grupo_selecionado != "Todos":
    dados = [d for d in dados if d["grupo_nome"] == grupo_selecionado]

if not dados:
    st.info("Nenhuma categoria cadastrada ainda. Vá em Categorias para conferir o modelo padrão.")
else:
    df = pd.DataFrame(dados)
    df["gasto"] = df["gasto"].astype(float)
    df["teto_mensal"] = df["teto_mensal"].astype(float)
    df["percentual"] = df.apply(
        lambda r: (r["gasto"] / r["teto_mensal"] * 100) if r["teto_mensal"] else 0, axis=1
    )

    def status_categoria(pct, teto):
        if teto == 0:
            return "sem teto definido"
        if pct >= 100:
            return "🔴 estourou o teto"
        if pct >= 80:
            return "🟡 perto do teto"
        return "🟢 dentro do teto"

    df["status"] = df.apply(lambda r: status_categoria(r["percentual"], r["teto_mensal"]), axis=1)

    total_gasto = df["gasto"].sum()
    total_teto = df["teto_mensal"].sum()

    col1, col2 = st.columns(2)
    col1.metric("Gasto no mês (categorias filtradas)", formatar_moeda(total_gasto))
    col2.metric("Orçamento definido", formatar_moeda(total_teto))

    fig = px.bar(
        df, x="categoria_nome", y=["gasto", "teto_mensal"],
        barmode="group", labels={"value": "R$", "categoria_nome": "Categoria", "variable": ""},
        title="Gasto x Teto por categoria",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        df[["grupo_nome", "categoria_nome", "gasto", "teto_mensal", "status"]].rename(
            columns={
                "grupo_nome": "Grupo",
                "categoria_nome": "Categoria",
                "gasto": "Gasto",
                "teto_mensal": "Teto",
                "status": "Status",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
