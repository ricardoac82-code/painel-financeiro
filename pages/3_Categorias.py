import streamlit as st

from auth import exigir_login, fazer_logout
from db.queries import (
    criar_categoria,
    criar_grupo,
    editar_categoria,
    excluir_categoria,
    excluir_grupo,
    listar_categorias,
    listar_grupos,
    renomear_grupo,
)

usuario = exigir_login()
st.set_page_config(page_title="Categorias", page_icon="🏷️", layout="wide")

with st.sidebar:
    st.write(f"Olá, **{usuario['nome']}**")
    if st.button("Sair"):
        fazer_logout()
        st.switch_page("app.py")

st.title("🏷️ Grupos e Categorias")
st.caption("Vêm com um modelo padrão, mas você pode editar, renomear ou excluir livremente.")

grupos = listar_grupos(usuario["id"])

with st.expander("➕ Novo grupo"):
    with st.form("form_grupo"):
        nome_grupo = st.text_input("Nome do grupo")
        criar = st.form_submit_button("Criar grupo")
    if criar and nome_grupo:
        criar_grupo(usuario["id"], nome_grupo)
        st.rerun()

for grupo in grupos:
    with st.expander(f"📁 {grupo['nome']}", expanded=False):
        col1, col2 = st.columns([3, 1])
        novo_nome_grupo = col1.text_input(
            "Renomear grupo", value=grupo["nome"], key=f"rename_{grupo['id']}"
        )
        if col1.button("Salvar novo nome", key=f"save_rename_{grupo['id']}"):
            renomear_grupo(usuario["id"], grupo["id"], novo_nome_grupo)
            st.rerun()
        if col2.button("Excluir grupo", key=f"del_grupo_{grupo['id']}"):
            excluir_grupo(usuario["id"], grupo["id"])
            st.rerun()

        st.divider()
        st.write("**Categorias deste grupo:**")

        categorias = listar_categorias(usuario["id"], grupo_id=grupo["id"])
        for cat in categorias:
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
            novo_nome_cat = c1.text_input(
                "Nome", value=cat["nome"], key=f"cat_nome_{cat['id']}", label_visibility="collapsed"
            )
            novo_teto = c2.number_input(
                "Teto (R$)", value=float(cat["teto_mensal"]), key=f"cat_teto_{cat['id']}",
                label_visibility="collapsed",
            )
            if c3.button("Salvar", key=f"cat_save_{cat['id']}"):
                editar_categoria(usuario["id"], cat["id"], novo_nome_cat, novo_teto)
                st.rerun()
            if c4.button("Excluir", key=f"cat_del_{cat['id']}"):
                excluir_categoria(usuario["id"], cat["id"])
                st.rerun()

        with st.form(f"nova_categoria_{grupo['id']}"):
            nome_nova_cat = st.text_input("Nova categoria")
            teto_nova_cat = st.number_input("Teto mensal (R$)", value=0.0, step=50.0)
            adicionar = st.form_submit_button("Adicionar categoria")
        if adicionar and nome_nova_cat:
            criar_categoria(usuario["id"], grupo["id"], nome_nova_cat, teto_nova_cat)
            st.rerun()
