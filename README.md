# Sales Analytics Pipeline

Pipeline completo de análise de vendas construído com Python. O CSV entra, o dashboard interativo sai.

O **ETL** extrai e transforma dados de vendas em um modelo dimensional no Supabase (PostgreSQL).
A **API** expõe tudo através de endpoints FastAPI para acesso programático.
O **Dashboard** visualiza os dados com uma interface Streamlit premium, com insights automáticos, análise de tendências e gráficos de ranking.

> O dashboard conecta direto ao banco de dados e pode ser publicado no Streamlit Community Cloud sem nenhuma infraestrutura de backend.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| ETL | Python, Pandas |
| API | FastAPI, Uvicorn |
| Dashboard | Streamlit, Plotly |
| Banco de Dados | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |

## Estrutura do Projeto

```
etl-sales/
├── app/
│   ├── api/
│   │   ├── db.py              # Pool de conexão
│   │   ├── main.py            # Endpoints FastAPI
│   │   └── queries.py         # SQL parametrizado
│   ├── etl/
│   │   ├── extract.py         # Leitura do CSV
│   │   ├── transform.py       # Validação e limpeza
│   │   ├── load.py            # Carga no banco
│   │   └── run_etl.py         # Orquestrador do ETL
│   └── config.py              # Configuração de ambiente
├── dashboard/
│   └── streamlit_app.py       # Dashboard interativo
├── data/
│   └── sample_sales.csv       # Dataset de vendas 2025
├── schema.sql                 # DDL do modelo dimensional
├── requirements.txt
├── .env.example
└── README.md
```

---

## Como Rodar

### Pré-requisitos

- Python 3.10+
- Git
- Um projeto Supabase com PostgreSQL

### 1. Clone e instale

```bash
git clone https://github.com/Hubbleq/sales-etl.git
cd sales-etl

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure o banco

```bash
copy .env.example .env
```

Edite o `.env` com suas credenciais do Supabase:

```
DATABASE_URL=postgresql+psycopg://postgres:<SENHA>@db.<PROJETO>.supabase.co:5432/postgres
```

Depois execute o `schema.sql` no SQL Editor do Supabase para criar as tabelas.

### 3. Carregue os dados

```bash
python -m app.etl.run_etl
```

Isso lê o `data/sample_sales.csv`, transforma e carrega no modelo dimensional.

### 4. Inicie

**Jeito rápido (Windows):** dois cliques no `run.bat` na raiz do projeto.

**Manual:**

```bash
# Terminal 1 - API
uvicorn app.api.main:app --reload --port 8001

# Terminal 2 - Dashboard
streamlit run dashboard/streamlit_app.py --server.port 8501
```

| Serviço | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API Docs (Swagger) | http://localhost:8001/docs |
| Health Check | http://localhost:8001/health |

---

## Deploy no Streamlit Cloud

O dashboard funciona sozinho — não precisa de backend FastAPI em produção.

1. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com o GitHub
2. Clique em **New app** e selecione:
   - Repository: `Hubbleq/sales-etl`
   - Branch: `main`
   - Main file path: `dashboard/streamlit_app.py`
3. Abra **Settings > Secrets** e adicione:
   ```toml
   DATABASE_URL = "postgresql+psycopg://postgres:<SENHA>@db.<PROJETO>.supabase.co:5432/postgres"
   ```
4. Deploy.

---

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Status da API |
| GET | `/sales/daily?start=...&end=...` | Receita diária |
| GET | `/sales/monthly?start=...&end=...` | Receita mensal |
| GET | `/products/top?start=...&end=...&limit=N` | Top N produtos |
| GET | `/products/categories?start=...&end=...` | Receita por categoria |
| GET | `/stores/performance?start=...&end=...` | Performance por loja |
| GET | `/stores/monthly?start=...&end=...` | Receita mensal por loja |

## Schema do Banco

Modelo dimensional em star schema:

- **dim_loja** — Dimensão de lojas (nome, cidade, estado)
- **dim_produto** — Dimensão de produtos (SKU, nome, categoria)
- **fato_vendas** — Tabela fato de vendas (data, quantidade, preço, desconto, total)
- **etl_execucoes** — Log de execuções do ETL

## Funcionalidades do Dashboard

- KPIs com variação mês a mês
- Insights narrativos gerados automaticamente
- Tendência de receita diária com média móvel de 7 dias
- Distribuição por categoria (gráfico donut)
- Rankings de produtos e lojas (barras HTML customizadas)
- Comparativo mensal multi-loja
- Tabela interativa com busca e ordenação
- Tema escuro responsivo com tipografia Inter

---

Licença MIT
