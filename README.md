# ✦ Sales Analytics Pipeline

Pipeline completo de análise de vendas com **ETL**, **API REST** e **Dashboard interativo**.

## Tecnologias

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
│   │   ├── db.py            # Conexão com o banco
│   │   ├── main.py          # Endpoints da API (FastAPI)
│   │   └── queries.py       # Queries SQL parametrizadas
│   ├── etl/
│   │   ├── extract.py       # Leitura do CSV
│   │   ├── transform.py     # Validação e limpeza
│   │   ├── load.py          # Carga no banco
│   │   └── run_etl.py       # Orquestrador do ETL
│   └── config.py            # Variáveis de ambiente
├── dashboard/
│   └── streamlit_app.py     # Dashboard premium com storytelling
├── data/
│   └── sample_sales.csv     # Dados de vendas (2025)
├── generate_data.py         # Gerador de dados realistas
├── schema.sql               # Schema do banco (modelo dimensional)
├── requirements.txt         # Dependências Python
├── run.bat                  # Script para iniciar tudo (Windows)
├── .env.example             # Modelo de variáveis de ambiente
└── README.md
```

---

## 🚀 Passo a Passo para Rodar o Projeto

### Pré-requisitos

- **Python 3.10+** instalado ([python.org](https://python.org))
- **Git** instalado ([git-scm.com](https://git-scm.com))
- **Conta no Supabase** com um projeto PostgreSQL ([supabase.com](https://supabase.com))

### 1. Clone o repositório

```bash
git clone https://github.com/Hubbleq/sales-etl.git
cd sales-etl
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure o banco de dados

Copie o arquivo de exemplo e preencha com suas credenciais do Supabase:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux/Mac
```

Edite o `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres
```

### 4. Crie as tabelas no banco

Execute o script SQL no editor do Supabase (SQL Editor) ou via psql:

```bash
# O arquivo schema.sql contém as tabelas:
# dim_loja, dim_produto, fato_vendas, etl_execucoes
```

### 5. Execute o ETL (carga de dados)

```bash
python -m app.etl.run_etl
```

Isso irá ler o `data/sample_sales.csv`, transformar e carregar no banco.

### 6. Inicie o sistema

#### ⚡ Jeito Fácil (Windows)

Dê **dois cliques** no arquivo `run.bat` na raiz do projeto. Ele:
1. Fecha processos antigos nas portas
2. Inicia a **API** (backend) na porta 8001
3. Inicia o **Dashboard** (frontend) na porta 8501

#### Manual (qualquer OS)

Abra **dois terminais** na pasta do projeto:

**Terminal 1 — API:**
```bash
.venv\Scripts\activate
uvicorn app.api.main:app --reload --port 8001
```

**Terminal 2 — Dashboard:**
```bash
.venv\Scripts\activate
streamlit run dashboard/streamlit_app.py --server.port 8501
```

### 7. Acesse

| Serviço | URL |
|---------|-----|
| 📊 **Dashboard** | [http://localhost:8501](http://localhost:8501) |
| 🔧 **API Docs** (Swagger) | [http://localhost:8001/docs](http://localhost:8001/docs) |
| ❤️ **Health Check** | [http://localhost:8001/health](http://localhost:8001/health) |

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
| GET | `/analysis/heatmap?start=...&end=...` | Dados Loja x Categoria |

## Schema do Banco (Modelo Dimensional)

- `dim_loja` — Dimensão de lojas (nome, cidade, estado)
- `dim_produto` — Dimensão de produtos (SKU, nome, categoria)
- `fato_vendas` — Fato de vendas (data, quantidade, preço, desconto, total)
- `etl_execucoes` — Log de execuções do ETL

## Dashboard

Design minimalista premium com storytelling de dados:

1. **Visão Geral** — KPIs com variação mês-a-mês e insight narrativo automático
2. **Tendências** — Gráfico de evolução diária + média móvel 7 dias
3. **Categorias** — Donut chart com distribuição percentual
4. **Rankings** — Top 10 produtos e performance por loja (barras HTML)
5. **Evolução Mensal** — Comparativo multi-loja mês a mês
6. **Dados Detalhados** — Tabela com busca e ordenação

## Licença

MIT
