# 📊 Sales Analytics Pipeline

Pipeline completo de análise de vendas com ETL, API REST e dashboard interativo.

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
│   │   ├── main.py          # Endpoints da API
│   │   └── queries.py       # Queries SQL
│   ├── etl/
│   │   ├── extract.py       # Leitura do CSV
│   │   ├── transform.py     # Validação e limpeza
│   │   ├── load.py          # Carga no banco
│   │   └── run_etl.py       # Orquestrador do ETL
│   └── config.py            # Variáveis de ambiente
├── dashboard/
│   └── streamlit_app.py     # Painel interativo
├── data/
│   └── sample_sales.csv     # Dados de vendas
├── generate_data.py         # Gerador de dados realistas

├── schema.sql               # Schema do banco (português)
├── requirements.txt         # Dependências Python
├── .env.example             # Modelo de variáveis de ambiente
└── README.md
```

## Como Usar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/etl-sales.git
cd etl-sales
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

### 3. Configure o banco de dados

Copie o arquivo de exemplo e preencha com suas credenciais do Supabase:

```bash
copy .env.example .env
```

Edite o `.env` com a URL do seu banco PostgreSQL:

```
DATABASE_URL=postgresql+psycopg://postgres:SUA_SENHA@db.SEU_PROJETO.supabase.co:5432/postgres
```

### 4. Prepare o Banco de Dados

1. Executa o script SQL para criar as tabelas:
   - Use um cliente SQL (DBeaver, pgAdmin) para rodar o arquivo `schema.sql` no seu banco.

2. Gere os dados e rode o ETL:

```bash
python generate_data.py
python -m app.etl.run_etl
```

### 5. Inicie a API

```bash
python -m uvicorn app.api.main:app --reload --port 8000
```

### 6. Inicie o dashboard

Em outro terminal:

```bash
streamlit run dashboard/streamlit_app.py --server.port 8501
```

Acesse em [http://localhost:8501](http://localhost:8501)

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Status da API |
| GET | `/sales/monthly?start=YYYY-MM-DD&end=YYYY-MM-DD` | Receita mensal |
| GET | `/products/top?start=...&end=...&limit=N` | Top N produtos |
| GET | `/stores/performance?start=...&end=...` | Performance por loja |

## Schema do Banco (Português)

- `dim_loja` — Dimensão de lojas (nome, cidade, estado)
- `dim_produto` — Dimensão de produtos (SKU, nome, categoria)
- `fato_vendas` — Fato de vendas (data, quantidade, preço, desconto, total)
- `etl_execucoes` — Log de execuções do ETL

## Dashboard

O painel usa storytelling com dados e é dividido em seções:

1. **Visão Geral** — KPIs: Receita, Volume, Ticket Médio, Descontos Concedidos (+ % Margem aproximada)
2. **Evolução** — Gráfico de área (Receita) overlay com barras de Descontos
3. **Categorias** — Gráfico de Pizza (novidade!)
4. **Lojas** — Gráfico de Barras horizontais
5. **Ranking** — Tabela detalhada de produtos com formatação condicional

## Licença

MIT
