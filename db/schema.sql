-- Schema Fase 1: núcleo (login, contas, categorias, lançamentos)
-- Rode via scripts/init_db.py

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS contas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(120) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('pessoal', 'casa', 'reserva')),
    banco VARCHAR(80),
    saldo_inicial NUMERIC(14,2) NOT NULL DEFAULT 0,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS grupos_categorias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(80) NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(usuario_id, nome)
);

CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    grupo_id INTEGER NOT NULL REFERENCES grupos_categorias(id) ON DELETE CASCADE,
    nome VARCHAR(80) NOT NULL,
    teto_mensal NUMERIC(14,2) NOT NULL DEFAULT 0,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(usuario_id, grupo_id, nome)
);

CREATE TABLE IF NOT EXISTS lancamentos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    conta_id INTEGER NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    data DATE NOT NULL,
    descricao VARCHAR(200),
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    valor NUMERIC(14,2) NOT NULL CHECK (valor > 0),
    forma_pagamento VARCHAR(40),
    status VARCHAR(10) NOT NULL DEFAULT 'pago' CHECK (status IN ('pago', 'pendente')),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lancamentos_usuario_data ON lancamentos(usuario_id, data);
CREATE INDEX IF NOT EXISTS idx_lancamentos_categoria ON lancamentos(categoria_id);
