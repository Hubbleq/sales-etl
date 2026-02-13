# Transformações dos dados de vendas.
# Valida colunas obrigatórias, limpa os dados,
# calcula o valor total e gera um hash único por linha.

import hashlib
import pandas as pd

# Colunas que todo CSV de vendas precisa ter
REQUIRED_COLUMNS = [
    "sale_date", "store_name", "city", "state",
    "sku", "product_name", "category",
    "quantity", "unit_price", "discount",
]


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Verifica se todas as colunas obrigatórias existem no DataFrame."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Colunas faltando no CSV: {missing}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e padroniza os dados:
    - Remove espaços extras dos textos
    - Converte estado para maiúsculas
    - Preenche descontos vazios com zero
    - Calcula o valor total (quantidade * preço - desconto)"""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    # Remove espaços das colunas de texto
    df["store_name"] = df["store_name"].str.strip()
    df["sku"] = df["sku"].str.strip()
    df["product_name"] = df["product_name"].str.strip()
    df["category"] = df["category"].str.strip()
    df["city"] = df["city"].str.strip()
    df["state"] = df["state"].str.strip().str.upper()

    # Garante tipos numéricos corretos
    df["quantity"] = df["quantity"].astype(int)
    df["unit_price"] = df["unit_price"].astype(float)
    df["discount"] = df["discount"].fillna(0).astype(float)

    # Calcula o valor total da venda
    df["total_amount"] = (df["quantity"] * df["unit_price"]) - df["discount"]

    return df


def _row_hash(row: pd.Series) -> str:
    """Gera um hash SHA-256 único para cada linha baseado nas colunas-chave.
    Isso permite evitar duplicatas no banco de dados."""
    payload = "|".join(str(row[c]) for c in REQUIRED_COLUMNS)
    return hashlib.sha256(payload.encode()).hexdigest()


def add_hash(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona a coluna source_row_hash ao DataFrame."""
    df = df.copy()
    df["source_row_hash"] = df.apply(_row_hash, axis=1)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de transformação: validar -> limpar -> gerar hash."""
    df = validate(df)
    df = clean(df)
    df = add_hash(df)
    return df
