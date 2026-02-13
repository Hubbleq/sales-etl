# Funções de carga (load) do ETL.
# Responsáveis por inserir lojas, produtos e vendas no banco de dados.
# Usa upsert (INSERT ... ON CONFLICT) para evitar duplicatas.

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def upsert_stores(session: Session, df: pd.DataFrame) -> dict[str, int]:
    """Insere ou busca lojas no banco e retorna um mapa nome -> id.
    Se a loja já existir, apenas busca o ID dela."""
    stores = df[["store_name", "city", "state"]].drop_duplicates()
    mapping: dict[str, int] = {}

    for _, row in stores.iterrows():
        # Tenta inserir a loja; se já existir, ignora
        result = session.execute(
            text("""
                INSERT INTO dim_loja (nome_loja, cidade, estado)
                VALUES (:store_name, :city, :state)
                ON CONFLICT (nome_loja) DO NOTHING
                RETURNING loja_id;
            """),
            dict(row),
        )
        new = result.fetchone()

        if new:
            # Loja nova inserida com sucesso
            mapping[row["store_name"]] = new[0]
        else:
            # Loja já existia, precisamos buscar o ID
            existing = session.execute(
                text("SELECT loja_id FROM dim_loja WHERE nome_loja = :store_name"),
                {"store_name": row["store_name"]},
            ).fetchone()
            mapping[row["store_name"]] = existing[0]

    return mapping


def upsert_products(session: Session, df: pd.DataFrame) -> dict[str, int]:
    """Insere ou busca produtos no banco e retorna um mapa sku -> id.
    Se o produto já existir (mesmo SKU), apenas busca o ID."""
    products = df[["sku", "product_name", "category"]].drop_duplicates()
    mapping: dict[str, int] = {}

    for _, row in products.iterrows():
        # Tenta inserir o produto; se o SKU já existir, ignora
        result = session.execute(
            text("""
                INSERT INTO dim_produto (sku, nome_produto, categoria)
                VALUES (:sku, :product_name, :category)
                ON CONFLICT (sku) DO NOTHING
                RETURNING produto_id;
            """),
            dict(row),
        )
        new = result.fetchone()

        if new:
            # Produto novo inserido
            mapping[row["sku"]] = new[0]
        else:
            # Produto já existia, buscamos o ID
            existing = session.execute(
                text("SELECT produto_id FROM dim_produto WHERE sku = :sku"),
                {"sku": row["sku"]},
            ).fetchone()
            mapping[row["sku"]] = existing[0]

    return mapping


def insert_facts(
    session: Session,
    df: pd.DataFrame,
    store_map: dict[str, int],
    product_map: dict[str, int],
) -> tuple[int, int]:
    """Insere cada linha de venda na tabela fato_vendas.
    Usa o hash como chave única para evitar duplicatas.
    Retorna (inseridas, ignoradas)."""
    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        result = session.execute(
            text("""
                INSERT INTO fato_vendas
                    (data_venda, loja_id, produto_id, quantidade,
                     preco_unitario, desconto, valor_total, hash_origem)
                VALUES
                    (:sale_date, :store_id, :product_id, :quantity,
                     :unit_price, :discount, :total_amount, :source_row_hash)
                ON CONFLICT (hash_origem) DO NOTHING;
            """),
            {
                "sale_date": row["sale_date"],
                "store_id": store_map[row["store_name"]],
                "product_id": product_map[row["sku"]],
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
                "discount": float(row["discount"]),
                "total_amount": float(row["total_amount"]),
                "source_row_hash": row["source_row_hash"],
            },
        )

        if result.rowcount:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped
