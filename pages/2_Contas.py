import streamlit as st

from auth import exigir_login, fazer_logout
from db.queries import criar_conta, excluir_conta, listar_contas
from utils import formatar_moeda

usuario = exigir_login()
st.set_page_config(page_title="Contas", page_icon="🏦", layout="wide")

with st.sidebar:
    st.write(f"Olá, **{usuario['nome']}**")
    if st.button("Sair"):
        fazer_logout()
        st.switch_page("app.py")

st.title("🏦 Contas e Carteiras")

with st.expander("➕ Adicionar conta"):
    with st.form("form_conta"):
        nome = st.text_input("Nome da conta")
        tipo = st.selectbox("Tipo", ["pessoal", "casa", "reserva"])
        banco = st.text_input("Banco (opcional)")
        saldo_inicial = st.number_input("Saldo inicial (R$)", value=0.0, step=100.0, format="%.2f")
        salvar = st.form_submit_button("Salvar")

    if salvar:
        if not nome:
            st.error("Dê um nome para a conta.")
        else:
            criar_conta(usuario["id"], nome, tipo, banco, saldo_inicial)
            st.success("Conta criada.")
            st.rerun()

contas = listar_contas(usuario["id"])

if not contas:
    st.info("Nenhuma conta cadastrada ainda.")
else:
    for conta in contas:
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(f"**{conta['nome']}** · {conta['tipo']} · {conta['banco'] or '—'}")
        col2.write(formatar_moeda(float(conta["saldo_atual"])))
        if col3.button("Excluir", key=f"excluir_{conta['id']}"):
            excluir_conta(usuario["id"], conta["id"])
            st.rerun()
