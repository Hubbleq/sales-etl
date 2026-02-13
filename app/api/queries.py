# Queries SQL usadas pela API.
# Atualizado para incluir análise por categoria e descontos.

from sqlalchemy import text

# Receita, unidades e descontos agrupados por mês
MONTHLY_REVENUE = text("""
    SELECT
        TO_CHAR(data_venda, 'YYYY-MM') AS month,
        SUM(valor_total)::FLOAT        AS revenue,
        SUM(quantidade)                AS units,
        SUM(desconto)::FLOAT           AS discount,
        COUNT(*)                       AS rows
    FROM fato_vendas
    WHERE data_venda BETWEEN :start AND :end
    GROUP BY 1
    ORDER BY 1;
""")

# Top N produtos por receita
TOP_PRODUCTS = text("""
    SELECT
        p.sku,
        p.nome_produto  AS product_name,
        p.categoria     AS category,
        SUM(f.quantidade)            AS units,
        SUM(f.valor_total)::FLOAT    AS revenue
    FROM fato_vendas f
    JOIN dim_produto p USING (produto_id)
    WHERE f.data_venda BETWEEN :start AND :end
    GROUP BY p.sku, p.nome_produto, p.categoria
    ORDER BY revenue DESC
    LIMIT :limit;
""")

# Desempenho por loja
STORE_PERFORMANCE = text("""
    SELECT
        l.nome_loja   AS store_name,
        SUM(f.valor_total)::FLOAT AS revenue,
        SUM(f.quantidade)         AS units,
        COUNT(*)                  AS transaction_count
    FROM fato_vendas f
    JOIN dim_loja l USING (loja_id)
    WHERE f.data_venda BETWEEN :start AND :end
    GROUP BY l.nome_loja
    ORDER BY revenue DESC;
""")

# Desempenho por Categoria (NOVO KPI)
CATEGORY_PERFORMANCE = text("""
    SELECT
        p.categoria               AS category,
        SUM(f.valor_total)::FLOAT AS revenue,
        SUM(f.quantidade)         AS units
    FROM fato_vendas f
    JOIN dim_produto p USING (produto_id)
    WHERE f.data_venda BETWEEN :start AND :end
    GROUP BY 1
    ORDER BY revenue DESC;
""")
