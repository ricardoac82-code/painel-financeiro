"""
Conexão única com o banco Neon, compartilhada por toda a aplicação.

Usamos st.cache_resource para criar o engine do SQLAlchemy uma única vez
por processo do servidor Streamlit (não a cada rerun de página).

pool_pre_ping=True é importante aqui especificamente por causa do Neon:
como o compute do Neon "dorme" após alguns minutos sem uso, uma conexão
que ficou ociosa no pool pode estar inválida quando reusada. O pre_ping
testa a conexão antes de cada uso e reconecta automaticamente se preciso.
"""

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@st.cache_resource(show_spinner=False)
def get_engine() -> Engine:
    db_url = st.secrets["NEON_CONNECTION_STRING"]

    # Neon exige SSL. Garantimos o parâmetro mesmo se a string colada não tiver.
    if "sslmode" not in db_url:
        separador = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separador}sslmode=require"

    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
    )
