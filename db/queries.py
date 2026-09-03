"""
Funções de acesso a dados. Todas as queries são parametrizadas
(nunca concatenar string em SQL) e sempre filtradas por usuario_id,
já que aqui não usamos Row Level Security — quem garante o isolamento
entre usuários é o código Python, não o banco.
"""

from db.connection import get_engine
from sqlalchemy import text

# ---------- Categorias padrão (semeadas no cadastro do usuário) ----------

GRUPOS_PADRAO = {
    "Casa/Moradia": ["Aluguel/Financiamento", "Condomínio", "IPTU", "Água", "Luz", "Gás", "Internet", "Manutenção"],
    "Alimentação": ["Mercado", "Delivery", "Restaurante"],
    "Saúde": ["Plano de saúde", "Farmácia", "Consultas", "Academia"],
    "Transporte": ["Combustível", "App de transporte", "Manutenção veículo", "Seguro"],
    "Lazer": ["Viagens", "Streaming", "Cinema/Eventos", "Hobbies"],
    "Educação": ["Cursos", "Livros", "Mensalidades"],
    "Vestuário": ["Geral"],
    "Pets": ["Geral"],
    "Dívidas/Empréstimos": ["Geral"],
    "Investimentos/Reserva": ["Geral"],
    "Presentes/Doações": ["Geral"],
    "Outros": ["Geral"],
}


def semear_categorias_padrao(usuario_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        ja_tem = conn.execute(
            text("SELECT COUNT(*) FROM grupos_categorias WHERE usuario_id = :uid"),
            {"uid": usuario_id},
        ).scalar_one()
        if ja_tem > 0:
            return  # não duplica se o usuário já tem categorias

        for grupo_nome, categorias in GRUPOS_PADRAO.items():
            grupo_id = conn.execute(
                text(
                    """
                    INSERT INTO grupos_categorias (usuario_id, nome)
                    VALUES (:uid, :nome)
                    RETURNING id
                    """
                ),
                {"uid": usuario_id, "nome": grupo_nome},
            ).scalar_one()

            for cat_nome in categorias:
                conn.execute(
                    text(
                        """
                        INSERT INTO categorias (usuario_id, grupo_id, nome, teto_mensal)
                        VALUES (:uid, :gid, :nome, 0)
                        """
                    ),
                    {"uid": usuario_id, "gid": grupo_id, "nome": cat_nome},
                )


# ---------- Grupos e categorias (CRUD) ----------

def listar_grupos(usuario_id: int):
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT id, nome FROM grupos_categorias WHERE usuario_id = :uid ORDER BY nome"),
            {"uid": usuario_id},
        ).mappings().all()


def criar_grupo(usuario_id: int, nome: str) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        return conn.execute(
            text(
                """
                INSERT INTO grupos_categorias (usuario_id, nome)
                VALUES (:uid, :nome) RETURNING id
                """
            ),
            {"uid": usuario_id, "nome": nome.strip()},
        ).scalar_one()


def renomear_grupo(usuario_id: int, grupo_id: int, novo_nome: str) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE grupos_categorias SET nome = :nome
                WHERE id = :gid AND usuario_id = :uid
                """
            ),
            {"nome": novo_nome.strip(), "gid": grupo_id, "uid": usuario_id},
        )


def excluir_grupo(usuario_id: int, grupo_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM grupos_categorias WHERE id = :gid AND usuario_id = :uid"),
            {"gid": grupo_id, "uid": usuario_id},
        )


def listar_categorias(usuario_id: int, grupo_id: int | None = None):
    engine = get_engine()
    query = """
        SELECT c.id, c.nome, c.teto_mensal, c.grupo_id, g.nome AS grupo_nome
        FROM categorias c
        JOIN grupos_categorias g ON g.id = c.grupo_id
        WHERE c.usuario_id = :uid
    """
    params = {"uid": usuario_id}
    if grupo_id is not None:
        query += " AND c.grupo_id = :gid"
        params["gid"] = grupo_id
    query += " ORDER BY g.nome, c.nome"

    with engine.connect() as conn:
        return conn.execute(text(query), params).mappings().all()


def criar_categoria(usuario_id: int, grupo_id: int, nome: str, teto_mensal: float) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        return conn.execute(
            text(
                """
                INSERT INTO categorias (usuario_id, grupo_id, nome, teto_mensal)
                VALUES (:uid, :gid, :nome, :teto) RETURNING id
                """
            ),
            {"uid": usuario_id, "gid": grupo_id, "nome": nome.strip(), "teto": teto_mensal},
        ).scalar_one()


def editar_categoria(usuario_id: int, categoria_id: int, nome: str, teto_mensal: float) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE categorias SET nome = :nome, teto_mensal = :teto
                WHERE id = :cid AND usuario_id = :uid
                """
            ),
            {"nome": nome.strip(), "teto": teto_mensal, "cid": categoria_id, "uid": usuario_id},
        )


def excluir_categoria(usuario_id: int, categoria_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM categorias WHERE id = :cid AND usuario_id = :uid"),
            {"cid": categoria_id, "uid": usuario_id},
        )


# ---------- Contas ----------

def listar_contas(usuario_id: int):
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text(
                """
                SELECT c.id, c.nome, c.tipo, c.banco, c.saldo_inicial,
                       c.saldo_inicial
                       + COALESCE(SUM(CASE WHEN l.tipo = 'receita' AND l.status = 'pago' THEN l.valor ELSE 0 END), 0)
                       - COALESCE(SUM(CASE WHEN l.tipo = 'despesa' AND l.status = 'pago' THEN l.valor ELSE 0 END), 0)
                       AS saldo_atual
                FROM contas c
                LEFT JOIN lancamentos l ON l.conta_id = c.id
                WHERE c.usuario_id = :uid
                GROUP BY c.id
                ORDER BY c.nome
                """
            ),
            {"uid": usuario_id},
        ).mappings().all()


def criar_conta(usuario_id: int, nome: str, tipo: str, banco: str, saldo_inicial: float) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        return conn.execute(
            text(
                """
                INSERT INTO contas (usuario_id, nome, tipo, banco, saldo_inicial)
                VALUES (:uid, :nome, :tipo, :banco, :saldo) RETURNING id
                """
            ),
            {"uid": usuario_id, "nome": nome.strip(), "tipo": tipo, "banco": (banco or "").strip(), "saldo": saldo_inicial},
        ).scalar_one()


def excluir_conta(usuario_id: int, conta_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM contas WHERE id = :cid AND usuario_id = :uid"),
            {"cid": conta_id, "uid": usuario_id},
        )


# ---------- Lançamentos ----------

def criar_lancamento(usuario_id, conta_id, categoria_id, data_lanc, descricao, tipo, valor, forma_pagamento, status):
    engine = get_engine()
    with engine.begin() as conn:
        return conn.execute(
            text(
                """
                INSERT INTO lancamentos
                    (usuario_id, conta_id, categoria_id, data, descricao, tipo, valor, forma_pagamento, status)
                VALUES
                    (:uid, :conta_id, :categoria_id, :data, :descricao, :tipo, :valor, :forma, :status)
                RETURNING id
                """
            ),
            {
                "uid": usuario_id, "conta_id": conta_id, "categoria_id": categoria_id,
                "data": data_lanc, "descricao": descricao, "tipo": tipo,
                "valor": valor, "forma": forma_pagamento, "status": status,
            },
        ).scalar_one()


def listar_lancamentos(usuario_id: int, ano: int, mes: int, grupo_id: int | None = None):
    engine = get_engine()
    query = """
        SELECT l.id, l.data, l.descricao, l.tipo, l.valor, l.status,
               c.nome AS conta_nome, cat.nome AS categoria_nome, g.nome AS grupo_nome
        FROM lancamentos l
        JOIN contas c ON c.id = l.conta_id
        LEFT JOIN categorias cat ON cat.id = l.categoria_id
        LEFT JOIN grupos_categorias g ON g.id = cat.grupo_id
        WHERE l.usuario_id = :uid
          AND EXTRACT(YEAR FROM l.data) = :ano
          AND EXTRACT(MONTH FROM l.data) = :mes
    """
    params = {"uid": usuario_id, "ano": ano, "mes": mes}
    if grupo_id is not None:
        query += " AND g.id = :gid"
        params["gid"] = grupo_id
    query += " ORDER BY l.data DESC, l.id DESC"

    with engine.connect() as conn:
        return conn.execute(text(query), params).mappings().all()


def excluir_lancamento(usuario_id: int, lancamento_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM lancamentos WHERE id = :lid AND usuario_id = :uid"),
            {"lid": lancamento_id, "uid": usuario_id},
        )


def alternar_status_lancamento(usuario_id: int, lancamento_id: int) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE lancamentos
                SET status = CASE WHEN status = 'pago' THEN 'pendente' ELSE 'pago' END
                WHERE id = :lid AND usuario_id = :uid
                """
            ),
            {"lid": lancamento_id, "uid": usuario_id},
        )


# ---------- Orçamento (para o Dashboard) ----------

def gasto_por_categoria_mes(usuario_id: int, ano: int, mes: int):
    """Retorna, por categoria, o teto definido e o quanto já foi gasto no mês (só despesas pagas)."""
    engine = get_engine()
    with engine.connect() as conn:
        return conn.execute(
            text(
                """
                SELECT
                    cat.id AS categoria_id,
                    cat.nome AS categoria_nome,
                    g.id AS grupo_id,
                    g.nome AS grupo_nome,
                    cat.teto_mensal,
                    COALESCE(SUM(l.valor), 0) AS gasto
                FROM categorias cat
                JOIN grupos_categorias g ON g.id = cat.grupo_id
                LEFT JOIN lancamentos l
                    ON l.categoria_id = cat.id
                    AND l.tipo = 'despesa'
                    AND l.status = 'pago'
                    AND EXTRACT(YEAR FROM l.data) = :ano
                    AND EXTRACT(MONTH FROM l.data) = :mes
                WHERE cat.usuario_id = :uid
                GROUP BY cat.id, cat.nome, g.id, g.nome, cat.teto_mensal
                ORDER BY g.nome, cat.nome
                """
            ),
            {"uid": usuario_id, "ano": ano, "mes": mes},
        ).mappings().all()
