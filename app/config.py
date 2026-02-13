# Carrega variáveis de ambiente do arquivo .env
# e disponibiliza as configurações para o resto da aplicação.

from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega o .env que fica na raiz do projeto
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# URL de conexão com o PostgreSQL (Supabase)
DATABASE_URL: str = os.environ["DATABASE_URL"]

# URL base da API (usada internamente)
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
