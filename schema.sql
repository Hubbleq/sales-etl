-- Schema do banco de dados em portugues.
-- Usa modelo dimensional (star schema) com tabelas de dimensao e fato.

-- Dimensao: Lojas
-- Armazena informacoes sobre cada ponto de venda
CREATE TABLE IF NOT EXISTS dim_loja (
    loja_id    BIGSERIAL PRIMARY KEY,
    nome_loja  TEXT NOT NULL UNIQUE,
    cidade     TEXT,
    estado     TEXT
);

-- Dimensao: Produtos
-- Catalogo de todos os produtos vendidos
CREATE TABLE IF NOT EXISTS dim_produto (
    produto_id   BIGSERIAL PRIMARY KEY,
    sku          TEXT NOT NULL UNIQUE,
    nome_produto TEXT,
    categoria    TEXT
);

-- Tabela Fato: Vendas
-- Cada linha representa uma transacao de venda
-- Referencia as dimensoes loja e produto por chave estrangeira
CREATE TABLE IF NOT EXISTS fato_vendas (
    venda_id       BIGSERIAL PRIMARY KEY,
    data_venda     DATE NOT NULL,
    loja_id        BIGINT NOT NULL REFERENCES dim_loja (loja_id),
    produto_id     BIGINT NOT NULL REFERENCES dim_produto (produto_id),
    quantidade     INTEGER NOT NULL,
    preco_unitario NUMERIC(12, 2) NOT NULL,
    desconto       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    valor_total    NUMERIC(14, 2) NOT NULL,
    hash_origem    TEXT NOT NULL UNIQUE,
    inserido_em    TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Controle de execucoes do ETL
-- Registra cada vez que o pipeline roda, com status e contadores
CREATE TABLE IF NOT EXISTS etl_execucoes (
    execucao_id        BIGSERIAL PRIMARY KEY,
    nome_origem        TEXT NOT NULL,
    iniciado_em        TIMESTAMP NOT NULL DEFAULT NOW(),
    finalizado_em      TIMESTAMP,
    linhas_lidas       INTEGER DEFAULT 0,
    linhas_inseridas   INTEGER DEFAULT 0,
    linhas_ignoradas   INTEGER DEFAULT 0,
    status             TEXT NOT NULL DEFAULT 'executando',
    mensagem_erro      TEXT
);