# Painel Financeiro Pessoal — Fase 1

Esqueleto inicial gerado como ponto de partida. Leve isso pro Claude Code
pra rodar, testar e evoluir — o código segue a arquitetura combinada, mas
ainda **não foi testado contra um banco Neon real** nem contra um
Streamlit rodando de verdade.

## Estrutura

- `app.py` — tela de login/cadastro (porta de entrada)
- `pages/` — Dashboard, Contas, Categorias, Lançamentos (multipage nativo do Streamlit)
- `db/schema.sql` — tabelas do Postgres (Fase 1: usuarios, contas, grupos_categorias, categorias, lancamentos)
- `db/connection.py` — engine do SQLAlchemy conectando no Neon
- `db/queries.py` — todas as consultas SQL, sempre parametrizadas, sempre filtradas por usuario_id
- `auth.py` — cadastro/login com senha em bcrypt, sem serviço externo (sem RLS necessário — ver prompt original)
- `scripts/init_db.py` — roda uma vez pra criar as tabelas no Neon
- `utils.py` — formatação de moeda em R$

## Como rodar local (via Claude Code)

1. `pip install -r requirements.txt`
2. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml`
   e cole a connection string real do seu projeto Neon.
3. `python scripts/init_db.py` (cria as tabelas — rodar uma única vez)
4. `streamlit run app.py`
5. Crie uma conta pela aba "Criar conta" — as categorias padrão (Casa,
   Alimentação, Saúde, Lazer, Transporte, Educação etc.) são cadastradas
   automaticamente nesse momento.

## O que peço pra revisar/testar primeiro

- [ ] Rodar de ponta a ponta pelo menos uma vez (cadastro → login → criar
      conta → criar lançamento → ver no Dashboard)
- [ ] Conferir se o cálculo de saldo da conta bate com o esperado
- [ ] Conferir se o alerta de teto (verde/amarelo/vermelho) aparece certo

## Fora do escopo desta Fase 1 (de propósito)

- Editar um lançamento já criado (hoje só dá pra excluir ou alternar status pago/pendente)
- Cartões de crédito, contas recorrentes, upload de comprovante → **Fase 2**
- Investimentos, importação OFX/CSV → **Fase 3**
- Relatórios, benchmark, apuração fiscal estimada → **Fase 4**

Peça a próxima fase (pro Claude Code, ou de volta aqui no chat) só depois
que esta estiver rodando de verdade.
