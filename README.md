# Sales Analytics Pipeline

Full-stack analytics pipeline built with Python. Raw CSV goes in, interactive dashboard comes out.

**ETL** extracts and transforms sales data into a dimensional model on Supabase (PostgreSQL).
**API** exposes everything through FastAPI endpoints for programmatic access.
**Dashboard** visualizes it all with a premium Streamlit interface featuring auto-generated insights, trend analysis, and ranking charts.

> The dashboard connects directly to the database and can be deployed to Streamlit Community Cloud with zero backend infrastructure.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ETL | Python, Pandas |
| API | FastAPI, Uvicorn |
| Dashboard | Streamlit, Plotly |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |

## Project Structure

```
etl-sales/
├── app/
│   ├── api/
│   │   ├── db.py              # Database connection pool
│   │   ├── main.py            # FastAPI endpoints
│   │   └── queries.py         # Parameterized SQL
│   ├── etl/
│   │   ├── extract.py         # CSV reader
│   │   ├── transform.py       # Validation and cleanup
│   │   ├── load.py            # Database loader
│   │   └── run_etl.py         # ETL orchestrator
│   └── config.py              # Environment config
├── dashboard/
│   └── streamlit_app.py       # Interactive dashboard
├── data/
│   └── sample_sales.csv       # 2025 sales dataset
├── schema.sql                 # Dimensional model DDL
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- A Supabase project with PostgreSQL

### 1. Clone and install

```bash
git clone https://github.com/Hubbleq/sales-etl.git
cd sales-etl

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure the database

```bash
copy .env.example .env
```

Edit `.env` with your Supabase credentials:

```
DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT>.supabase.co:5432/postgres
```

Then run the `schema.sql` file in Supabase SQL Editor to create the tables.

### 3. Load data

```bash
python -m app.etl.run_etl
```

This reads `data/sample_sales.csv`, transforms and loads it into the dimensional model.

### 4. Run

**Quick start (Windows):** double-click `run.bat` in the project root.

**Manual:**

```bash
# Terminal 1 - API
uvicorn app.api.main:app --reload --port 8001

# Terminal 2 - Dashboard
streamlit run dashboard/streamlit_app.py --server.port 8501
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API Docs (Swagger) | http://localhost:8001/docs |
| Health Check | http://localhost:8001/health |

---

## Deploy to Streamlit Cloud

The dashboard runs standalone — no FastAPI backend needed in production.

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **New app** and select:
   - Repository: `Hubbleq/sales-etl`
   - Branch: `main`
   - Main file path: `dashboard/streamlit_app.py`
3. Open **Settings > Secrets** and add:
   ```toml
   DATABASE_URL = "postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT>.supabase.co:5432/postgres"
   ```
4. Deploy.

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | API status |
| GET | `/sales/daily?start=...&end=...` | Daily revenue |
| GET | `/sales/monthly?start=...&end=...` | Monthly revenue |
| GET | `/products/top?start=...&end=...&limit=N` | Top N products |
| GET | `/products/categories?start=...&end=...` | Revenue by category |
| GET | `/stores/performance?start=...&end=...` | Store performance |
| GET | `/stores/monthly?start=...&end=...` | Monthly revenue by store |

## Database Schema

Dimensional model with star schema:

- **dim_loja** — Store dimension (name, city, state)
- **dim_produto** — Product dimension (SKU, name, category)
- **fato_vendas** — Sales fact table (date, quantity, price, discount, total)
- **etl_execucoes** — ETL run log

## Dashboard Features

- KPI cards with month-over-month variation
- Auto-generated narrative insights
- Daily revenue trend with 7-day moving average
- Category distribution (donut chart)
- Product and store rankings (custom HTML bars)
- Monthly multi-store comparison
- Interactive data table with sorting and search
- Responsive dark theme with Inter typography

---

MIT License
