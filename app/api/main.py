# Módulo principal da API FastAPI.
# Atualizado com novos endpoints de categoria.

import traceback
from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.db import get_session
from app.api.queries import (
    MONTHLY_REVENUE, TOP_PRODUCTS, STORE_PERFORMANCE, CATEGORY_PERFORMANCE
)

app = FastAPI(
    title="API de Análise de Vendas",
    version="2.1.0",
    description="API REST para dashboard de vendas.",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Captura erros e retorna log detalhado."""
    tb = traceback.format_exc()
    print(f"\n[ERRO] {request.url}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"erro": str(exc), "detalhes": tb},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sales/monthly")
def vendas_mensais(
    start: date = Query(..., description="Data inicial"),
    end: date = Query(..., description="Data final"),
    session: Session = Depends(get_session),
):
    """Receita, unidades e descontos por mês."""
    rows = session.execute(MONTHLY_REVENUE, {"start": start, "end": end})
    return [dict(r._mapping) for r in rows]


@app.get("/products/top")
def produtos_top(
    start: date = Query(..., description="Data inicial"),
    end: date = Query(..., description="Data final"),
    limit: Optional[int] = Query(10, description="Limite"),
    session: Session = Depends(get_session),
):
    """Ranking de produtos."""
    rows = session.execute(TOP_PRODUCTS, {"start": start, "end": end, "limit": limit})
    return [dict(r._mapping) for r in rows]


@app.get("/stores/performance")
def performance_lojas(
    start: date = Query(..., description="Data inicial"),
    end: date = Query(..., description="Data final"),
    session: Session = Depends(get_session),
):
    """Desempenho por loja."""
    rows = session.execute(STORE_PERFORMANCE, {"start": start, "end": end})
    return [dict(r._mapping) for r in rows]


@app.get("/products/categories")
def performance_categorias(
    start: date = Query(..., description="Data inicial"),
    end: date = Query(..., description="Data final"),
    session: Session = Depends(get_session),
):
    """[NOVO] Desempenho por categoria de produto."""
    rows = session.execute(CATEGORY_PERFORMANCE, {"start": start, "end": end})
    return [dict(r._mapping) for r in rows]
