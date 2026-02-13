# Orquestrador do pipeline ETL.
# Coordena todo o fluxo: lê o CSV, transforma os dados e carrega no banco.
# Também registra cada execução na tabela etl_execucoes.

import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.api.db import SessionLocal
from app.etl.extract import read_csv
from app.etl.transform import transform
from app.etl.load import upsert_stores, upsert_products, insert_facts

# Caminho padrão do CSV de dados
DEFAULT_CSV = Path(__file__).resolve().parent.parent.parent / "data" / "sample_sales.csv"


def run(csv_path: str | Path | None = None) -> None:
    """Executa o pipeline ETL completo:
    1. Registra a execução no banco
    2. Lê e transforma o CSV
    3. Insere lojas, produtos e vendas
    4. Atualiza o registro com o resultado"""

    csv_path = Path(csv_path) if csv_path else DEFAULT_CSV
    source_name = csv_path.name

    session = SessionLocal()
    run_id: int | None = None

    try:
        # Registra o início da execução
        result = session.execute(
            text("""
                INSERT INTO etl_execucoes (nome_origem, iniciado_em, status)
                VALUES (:nome_origem, :iniciado_em, 'executando')
                RETURNING execucao_id;
            """),
            {"nome_origem": source_name, "iniciado_em": datetime.now(timezone.utc)},
        )
        run_id = result.fetchone()[0]
        session.commit()

        # Lê o CSV de entrada
        df = read_csv(csv_path)
        rows_read = len(df)

        # Aplica as transformações (validação, limpeza, hash)
        df = transform(df)

        # Carrega os dados no banco
        store_map = upsert_stores(session, df)
        product_map = upsert_products(session, df)
        inserted, skipped = insert_facts(session, df, store_map, product_map)

        # Atualiza o registro com o resultado da execução
        session.execute(
            text("""
                UPDATE etl_execucoes
                SET finalizado_em    = :finalizado_em,
                    linhas_lidas     = :linhas_lidas,
                    linhas_inseridas = :linhas_inseridas,
                    linhas_ignoradas = :linhas_ignoradas,
                    status           = 'sucesso'
                WHERE execucao_id = :execucao_id;
            """),
            {
                "finalizado_em": datetime.now(timezone.utc),
                "linhas_lidas": rows_read,
                "linhas_inseridas": inserted,
                "linhas_ignoradas": skipped,
                "execucao_id": run_id,
            },
        )
        session.commit()

        print(f"ETL concluido! Lidas={rows_read}  Inseridas={inserted}  Ignoradas={skipped}")

    except Exception as exc:
        session.rollback()

        # Se já tínhamos um ID de execução, registra o erro no banco
        if run_id is not None:
            session.execute(
                text("""
                    UPDATE etl_execucoes
                    SET finalizado_em = :finalizado_em,
                        status        = 'erro',
                        mensagem_erro = :mensagem_erro
                    WHERE execucao_id = :execucao_id;
                """),
                {
                    "finalizado_em": datetime.now(timezone.utc),
                    "mensagem_erro": str(exc),
                    "execucao_id": run_id,
                },
            )
            session.commit()

        print(f"ETL falhou: {exc}", file=sys.stderr)
        raise

    finally:
        session.close()


# Permite executar direto: python -m app.etl.run_etl [caminho_csv]
if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(csv_arg)
