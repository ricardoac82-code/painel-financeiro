"""
Roda uma única vez para criar as tabelas no banco Neon.

Antes de rodar:
1. Copie .streamlit/secrets.toml.example para .streamlit/secrets.toml
2. Preencha com a connection string real do seu projeto Neon

Uso:
    python scripts/init_db.py
"""

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from db.connection import get_engine
from sqlalchemy import text


def main():
    schema_path = pathlib.Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")

    engine = get_engine()
    with engine.begin() as conn:
        for comando in sql.split(";"):
            comando = comando.strip()
            if comando:
                conn.execute(text(comando))

    print("Schema aplicado com sucesso no Neon.")


if __name__ == "__main__":
    main()
