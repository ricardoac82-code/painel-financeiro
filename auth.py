"""
Autenticação própria da aplicação: sem serviço externo.
Senhas ficam com hash bcrypt no banco; a sessão é controlada
pelo st.session_state do próprio Streamlit.
"""

import bcrypt
import streamlit as st
from sqlalchemy import text

from db.connection import get_engine
from db.queries import semear_categorias_padrao


def cadastrar_usuario(nome: str, email: str, senha: str):
    engine = get_engine()
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        existe = conn.execute(
            text("SELECT 1 FROM usuarios WHERE email = :email"),
            {"email": email.lower().strip()},
        ).first()
        if existe:
            return None  # e-mail já cadastrado

        usuario_id = conn.execute(
            text(
                """
                INSERT INTO usuarios (nome, email, senha_hash)
                VALUES (:nome, :email, :senha_hash)
                RETURNING id
                """
            ),
            {"nome": nome.strip(), "email": email.lower().strip(), "senha_hash": senha_hash},
        ).scalar_one()

    semear_categorias_padrao(usuario_id)
    return usuario_id


def autenticar(email: str, senha: str):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT id, nome, senha_hash FROM usuarios WHERE email = :email"),
            {"email": email.lower().strip()},
        ).mappings().first()

    if row is None:
        return None
    if bcrypt.checkpw(senha.encode("utf-8"), row["senha_hash"].encode("utf-8")):
        return {"id": row["id"], "nome": row["nome"]}
    return None


def login_realizado() -> bool:
    return "usuario" in st.session_state


def exigir_login():
    """Chame no topo de cada página. Se não estiver logado, manda de volta pro app.py."""
    if not login_realizado():
        st.switch_page("app.py")
    return st.session_state["usuario"]


def fazer_logout() -> None:
    st.session_state.pop("usuario", None)
