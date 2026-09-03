from datetime import date

import streamlit as st

from auth import exigir_login, fazer_logout
from db.queries import (
    alternar_status_lancamento,
    criar_lancamento,
    excluir_lancamento,
    listar_categorias,
    listar_contas,
    listar_lancamentos,
)
from utils import formatar_moeda

usuario = exigir_login()
st.set_page_config(page_title="Lançamentos", page_icon="📝", layout="wide")

with st.sidebar:
    st.write(f"Olá, **{usuario['nome']}**")
    if st.button("Sair"):
        fazer_logout()
        st.switch_page("app.py")

st.title("📝 Lançamentos")

contas = listar_contas(usuario["id"])
categorias = listar_categorias(usuario["id"])

if not contas:
    st.warning("Cadastre pelo menos uma conta antes de lançar algo.")
    st.stop()

with st.expander("➕ Novo lançamento", expanded=True):
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)
        data_lanc = col1.date_input("Data", value=date.today())
        tipo = col2.selectbox("Tipo", ["despesa", "receita"])

        conta_opcoes = {c["nome"]: c["id"] for c in contas}
        conta_nome = st.selectbox("Conta", list(conta_opcoes.keys()))

        categoria_opcoes = {f"{c['grupo_nome']} / {c['nome']}": c["id"] for c in categorias}
        categoria_nome = st.selectbox("Categoria", list(categoria_opcoes.keys())) if categoria_opcoes else None

        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0, format="%.2f")
        forma_pagamento = st.text_input("Forma de pagamento (opcional)")
        status = st.selectbox("Status", ["pago", "pendente"])

        salvar = st.form_submit_button("Salvar lançamento")

    if salvar:
        criar_lancamento(
            usuario["id"],
            conta_opcoes[conta_nome],
            categoria_opcoes[categoria_nome] if categoria_nome else None,
            data_lanc,
            descricao,
            tipo,
            valor,
            forma_pagamento,
            status,
        )
        st.success("Lançamento salvo.")
        st.rerun()

st.divider()

hoje = date.today()
col_ano, col_mes = st.columns(2)
ano = col_ano.number_input("Ano", value=hoje.year, step=1)
mes = col_mes.selectbox("Mês", range(1, 13), index=hoje.month - 1)

lancamentos = listar_lancamentos(usuario["id"], ano, mes)

if not lancamentos:
    st.info("Nenhum lançamento neste mês.")
else:
    for l in lancamentos:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
        col1.write(l["data"].strftime("%d/%m"))
        col2.write(f"{l['descricao'] or '(sem descrição)'} · {l['categoria_nome'] or '—'}")
        cor = "🟢" if l["tipo"] == "receita" else "🔴"
        col3.write(f"{cor} {formatar_moeda(float(l['valor']))} · {l['status']}")
        if col4.button("Alternar status", key=f"status_{l['id']}"):
            alternar_status_lancamento(usuario["id"], l["id"])
            st.rerun()
        if col5.button("Excluir", key=f"del_{l['id']}"):
            excluir_lancamento(usuario["id"], l["id"])
            st.rerun()
