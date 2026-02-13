# Leitura de arquivos CSV.
# Esse módulo é o ponto de entrada dos dados brutos no pipeline ETL.

from pathlib import Path
import pandas as pd


def read_csv(path: str | Path) -> pd.DataFrame:
    """Lê um arquivo CSV e converte a coluna sale_date para datetime."""
    df = pd.read_csv(path, parse_dates=["sale_date"])
    return df
