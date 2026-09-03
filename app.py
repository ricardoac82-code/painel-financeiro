import streamlit as st

from auth import autenticar, cadastrar_usuario, login_realizado

st.set_page_config(page_title="Painel Financeiro", page_icon="💰", layout="centered")

if login_realizado():
    st.switch_page("pages/1_Dashboard.py")

st.title("💰 Painel Financeiro Pessoal")

aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

with aba_login:
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        usuario = autenticar(email, senha)
        if usuario:
            st.session_state["usuario"] = usuario
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("E-mail ou senha incorretos.")

with aba_cadastro:
    with st.form("form_cadastro"):
        nome = st.text_input("Nome")
        email_novo = st.text_input("E-mail", key="email_cadastro")
        senha_nova = st.text_input("Senha", type="password", key="senha_cadastro")
        senha_confirma = st.text_input("Confirme a senha", type="password")
        criar = st.form_submit_button("Criar conta")

    if criar:
        if not nome or not email_novo or not senha_nova:
            st.error("Preencha todos os campos.")
        elif senha_nova != senha_confirma:
            st.error("As senhas não coincidem.")
        elif len(senha_nova) < 8:
            st.error("Use uma senha com pelo menos 8 caracteres.")
        else:
            usuario_id = cadastrar_usuario(nome, email_novo, senha_nova)
            if usuario_id is None:
                st.error("Já existe uma conta com esse e-mail.")
            else:
                st.success("Conta criada! Categorias padrão já foram cadastradas. Agora faça login na aba ao lado.")
