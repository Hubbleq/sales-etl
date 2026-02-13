# Configuração de conexão com o banco de dados.
# Usa SQLAlchemy para criar o engine e gerenciar sessões.
# A URL de conexão vem do arquivo .env via config.py.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import DATABASE_URL

# Cria o engine de conexão com o PostgreSQL (Supabase)
# pool_pre_ping=True garante que conexões inativas sejam testadas antes de usar
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)

# Fábrica de sessões que será usada em todos os endpoints
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    """Cria uma sessão do banco e garante que ela é fechada após o uso.
    Usada como dependência (Depends) nos endpoints do FastAPI."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
