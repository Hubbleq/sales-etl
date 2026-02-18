import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from sqlalchemy import create_engine, text
import os

st.set_page_config(
    page_title="Sales Analytics",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Conexão com o banco: tenta st.secrets (Streamlit Cloud), senão usa .env local
try:
    DB_URL = st.secrets["DATABASE_URL"]
except Exception:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    DB_URL = os.environ.get("DATABASE_URL", "")

# Normaliza o driver pra psycopg2 (compatibilidade com a nuvem)
if "postgresql+psycopg://" in DB_URL:
    DB_URL = DB_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")
elif DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        DB_URL, pool_size=3, max_overflow=2,
        pool_pre_ping=True, connect_args={"sslmode": "require"},
    )


# Estilos

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }
    .stApp { background: #07070a !important; }
    .stDeployButton, #MainMenu, footer, header { display: none !important; }
    .block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1440px; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0f 0%, #0c0c12 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.03) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: rgba(255,255,255,0.35) !important;
        font-size: 0.68rem !important; font-weight: 600 !important;
        text-transform: uppercase !important; letter-spacing: 1.2px !important;
    }

    /* Header */
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 20px 28px; margin-bottom: 24px;
        background: linear-gradient(135deg, rgba(99,102,241,0.04), rgba(168,85,247,0.02));
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        backdrop-filter: blur(20px);
    }
    .topbar-brand { display: flex; align-items: center; gap: 16px; }
    .topbar-logo {
        width: 40px; height: 40px; border-radius: 12px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem;
        box-shadow: 0 4px 24px rgba(99,102,241,0.3), 0 0 0 1px rgba(255,255,255,0.06);
        animation: logoPulse 3s ease-in-out infinite;
    }
    @keyframes logoPulse {
        0%, 100% { box-shadow: 0 4px 24px rgba(99,102,241,0.3), 0 0 0 1px rgba(255,255,255,0.06); }
        50% { box-shadow: 0 6px 32px rgba(99,102,241,0.45), 0 0 0 1px rgba(255,255,255,0.08); }
    }
    .topbar-title { font-size: 1.05rem; font-weight: 700; color: #fafafa; letter-spacing: -0.3px; }
    .topbar-sub { font-size: 0.68rem; color: rgba(255,255,255,0.22); margin-top: 2px; letter-spacing: 0.2px; }
    .topbar-right { display: flex; align-items: center; gap: 24px; }
    .topbar-meta {
        font-size: 0.68rem; color: rgba(255,255,255,0.18);
        display: flex; align-items: center; gap: 7px;
    }
    .live-dot {
        width: 7px; height: 7px; border-radius: 50%; background: #34d399;
        box-shadow: 0 0 10px rgba(52,211,153,0.6); animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }

    /* Section labels */
    .section-label {
        font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 2px; color: rgba(255,255,255,0.18);
        padding: 32px 0 14px; margin-top: 12px;
        border-top: 1px solid rgba(255,255,255,0.03);
        position: relative;
    }
    .section-label::after {
        content: ''; position: absolute; left: 0; top: 0;
        width: 40px; height: 1px;
        background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
    }

    /* KPI cards */
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .kpi {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 16px; padding: 24px 24px 20px;
        position: relative; overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
    }
    .kpi:hover {
        background: rgba(255,255,255,0.035);
        border-color: rgba(255,255,255,0.08);
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .kpi::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent, #818cf8), transparent);
        opacity: 0.5;
    }
    .kpi:nth-child(1) { --accent: #818cf8; }
    .kpi:nth-child(2) { --accent: #34d399; }
    .kpi:nth-child(3) { --accent: #fbbf24; }
    .kpi:nth-child(4) { --accent: #f472b6; }
    .kpi-label {
        font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 1px; color: rgba(255,255,255,0.28); margin-bottom: 8px;
    }
    .kpi-number {
        font-size: 1.6rem; font-weight: 800; color: #fafafa;
        margin: 0 0 6px; letter-spacing: -0.5px;
    }
    .kpi-detail { font-size: 0.68rem; color: rgba(255,255,255,0.22); }
    .badge-up { color: #34d399; font-weight: 700; font-size: 0.76rem; }
    .badge-down { color: #f87171; font-weight: 700; font-size: 0.76rem; }
    .badge-neutral { color: rgba(255,255,255,0.2); font-size: 0.76rem; }

    /* Insight card */
    .insight {
        display: flex; align-items: center; gap: 12px;
        background: rgba(99,102,241,0.03);
        border: 1px solid rgba(99,102,241,0.08);
        border-left: 3px solid rgba(99,102,241,0.3);
        border-radius: 10px; padding: 14px 18px; margin: 8px 0;
        transition: all 0.2s ease;
    }
    .insight:hover { background: rgba(99,102,241,0.05); }
    .insight-text { font-size: 0.75rem; color: rgba(255,255,255,0.4); line-height: 1.5; }
    .insight-text strong { color: rgba(255,255,255,0.75); font-weight: 600; }

    /* Chart cards */
    .chart-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 16px; padding: 24px 26px 18px; margin-bottom: 18px;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .chart-card:hover {
        border-color: rgba(255,255,255,0.07);
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    }
    .chart-card-header {
        display: flex; justify-content: space-between; align-items: baseline;
        margin-bottom: 6px;
    }
    .chart-card-title { font-size: 0.8rem; font-weight: 600; color: rgba(255,255,255,0.7); }
    .chart-card-badge {
        font-size: 0.62rem; color: rgba(255,255,255,0.18); font-weight: 500;
        padding: 3px 10px; border-radius: 20px;
        background: rgba(255,255,255,0.03);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 4px; }

    /* Responsive */
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
        .kpi-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .kpi-number { font-size: 1.2rem; }
        .topbar { flex-direction: column; align-items: flex-start; gap: 10px; padding: 16px 20px; }
    }
</style>
""", unsafe_allow_html=True)


# Consultas ao banco

def _run(sql, params):
    """Executa uma query e retorna um DataFrame."""
    with get_engine().connect() as conn:
        return pd.DataFrame(conn.execute(text(sql), params).mappings().all())

def _in_clause(prefix, values, params):
    """Gera IN (:p0, :p1, ...) e adiciona os valores ao dict de params."""
    keys = [f"{prefix}{i}" for i in range(len(values))]
    for k, v in zip(keys, values):
        params[k] = v
    return "(" + ", ".join(f":{k}" for k in keys) + ")"

@st.cache_data(ttl=120, show_spinner=False)
def query_daily(start, end, categories=None, stores=None):
    joins, wheres, params = "", "", {"s": start, "e": end}
    if categories:
        joins += " JOIN dim_produto p USING (produto_id)"
        wheres += f" AND p.categoria IN {_in_clause('c', categories, params)}"
    if stores:
        joins += " JOIN dim_loja l USING (loja_id)"
        wheres += f" AND l.nome_loja IN {_in_clause('st', stores, params)}"
    return _run(
        f"SELECT data_venda AS date, SUM(valor_total)::FLOAT AS revenue, "
        f"SUM(quantidade) AS units, SUM(desconto)::FLOAT AS discount "
        f"FROM fato_vendas{joins} WHERE data_venda BETWEEN :s AND :e{wheres} GROUP BY 1 ORDER BY 1",
        params,
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_monthly(start, end, categories=None, stores=None):
    joins, wheres, params = "", "", {"s": start, "e": end}
    if categories:
        joins += " JOIN dim_produto p USING (produto_id)"
        wheres += f" AND p.categoria IN {_in_clause('c', categories, params)}"
    if stores:
        joins += " JOIN dim_loja l USING (loja_id)"
        wheres += f" AND l.nome_loja IN {_in_clause('st', stores, params)}"
    return _run(
        f"SELECT TO_CHAR(data_venda, 'YYYY-MM') AS month, SUM(valor_total)::FLOAT AS revenue, "
        f"SUM(quantidade) AS units, SUM(desconto)::FLOAT AS discount, COUNT(*) AS rows "
        f"FROM fato_vendas{joins} WHERE data_venda BETWEEN :s AND :e{wheres} GROUP BY 1 ORDER BY 1",
        params,
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_top_products(start, end, limit=500):
    return _run(
        "SELECT p.sku, p.nome_produto AS product_name, p.categoria AS category, "
        "SUM(f.quantidade) AS units, SUM(f.valor_total)::FLOAT AS revenue "
        "FROM fato_vendas f JOIN dim_produto p USING (produto_id) "
        "WHERE f.data_venda BETWEEN :s AND :e "
        "GROUP BY p.sku, p.nome_produto, p.categoria ORDER BY revenue DESC LIMIT :lim",
        {"s": start, "e": end, "lim": limit},
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_stores(start, end):
    return _run(
        "SELECT l.nome_loja AS store_name, SUM(f.valor_total)::FLOAT AS revenue, "
        "SUM(f.quantidade) AS units, COUNT(*) AS transaction_count "
        "FROM fato_vendas f JOIN dim_loja l USING (loja_id) "
        "WHERE f.data_venda BETWEEN :s AND :e GROUP BY l.nome_loja ORDER BY revenue DESC",
        {"s": start, "e": end},
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_categories(start, end):
    return _run(
        "SELECT p.categoria AS category, SUM(f.valor_total)::FLOAT AS revenue, "
        "SUM(f.quantidade) AS units "
        "FROM fato_vendas f JOIN dim_produto p USING (produto_id) "
        "WHERE f.data_venda BETWEEN :s AND :e GROUP BY 1 ORDER BY revenue DESC",
        {"s": start, "e": end},
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_stores_monthly(start, end):
    return _run(
        "SELECT TO_CHAR(f.data_venda, 'YYYY-MM') AS month, l.nome_loja AS store_name, "
        "SUM(f.valor_total)::FLOAT AS revenue "
        "FROM fato_vendas f JOIN dim_loja l USING (loja_id) "
        "WHERE f.data_venda BETWEEN :s AND :e GROUP BY 1, 2 ORDER BY 1, 2",
        {"s": start, "e": end},
    )


# Formatadores de valor

def brl(v):
    if pd.isna(v) or v is None:
        return "R$ 0,00"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def num(v):
    if pd.isna(v) or v is None:
        return "0"
    return f"{v:,.0f}".replace(",", ".")

def compact(v):
    if pd.isna(v) or v is None:
        return "0"
    if abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"R$ {v/1_000:.1f}K"
    return brl(v)


# Layout padrão dos gráficos

CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, sans-serif", color="rgba(255,255,255,0.5)", size=11),
    margin=dict(l=0, r=0, t=8, b=0),
)

PAL = {
    "primary":  "#818cf8",
    "accent":   "#a78bfa",
    "success":  "#34d399",
    "warning":  "#fbbf24",
    "danger":   "#f87171",
    "text":     "rgba(255,255,255,0.7)",
    "text_dim": "rgba(255,255,255,0.3)",
    "grid":     "rgba(255,255,255,0.04)",
}

STORE_COLORS = [
    '#818cf8', '#f472b6', '#34d399', '#fbbf24', '#fb923c',
    '#60a5fa', '#a78bfa', '#f87171', '#94a3b8', '#c084fc',
]

DONUT_COLORS = [
    '#818cf8', '#a78bfa', '#c084fc', '#f472b6', '#fb923c',
    '#34d399', '#60a5fa', '#fbbf24', '#f87171', '#94a3b8',
]


# Barra lateral com filtros

with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 4px; text-align:center;">
        <div style="width:40px;height:40px;margin:0 auto 10px;
            background:linear-gradient(135deg,#6366f1,#a855f7);
            border-radius:12px;display:flex;align-items:center;justify-content:center;
            font-size:1.1rem;box-shadow:0 4px 24px rgba(99,102,241,0.3);">✦</div>
        <div style="font-size:0.85rem;font-weight:700;color:#fafafa;">Sales Analytics</div>
        <div style="font-size:0.65rem;color:rgba(255,255,255,0.25);margin-top:2px;">Dashboard v8</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    period = st.selectbox(
        "PERÍODO",
        ["Ano Completo (2025)", "1º Semestre", "2º Semestre", "Personalizado"],
        index=0,
    )
    if period == "Ano Completo (2025)":
        s_date, e_date = date(2025, 1, 1), date(2025, 12, 31)
    elif period == "1º Semestre":
        s_date, e_date = date(2025, 1, 1), date(2025, 6, 30)
    elif period == "2º Semestre":
        s_date, e_date = date(2025, 7, 1), date(2025, 12, 31)
    else:
        s_date = st.date_input("Início", date(2025, 1, 1))
        e_date = st.date_input("Fim", date(2025, 12, 31))

    st.markdown("---")

    with st.spinner(""):
        ref_cats = query_categories(str(s_date), str(e_date))
        ref_stores = query_stores(str(s_date), str(e_date))

    sel_cats = st.multiselect(
        "CATEGORIAS",
        options=ref_cats["category"].unique().tolist() if not ref_cats.empty else [],
    )
    sel_stores = st.multiselect(
        "LOJAS",
        options=ref_stores["store_name"].unique().tolist() if not ref_stores.empty else [],
    )

    st.markdown("---")
    if st.button("⟳  Atualizar", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# Carregamento dos dados (com filtros aplicados na query)

sd, ed = str(s_date), str(e_date)
cats_filter = tuple(sel_cats) if sel_cats else None
stores_filter = tuple(sel_stores) if sel_stores else None

df_d  = query_daily(sd, ed, categories=cats_filter, stores=stores_filter)
df_m  = query_monthly(sd, ed, categories=cats_filter, stores=stores_filter)
df_p  = query_top_products(sd, ed)
df_s  = query_stores(sd, ed)
df_c  = query_categories(sd, ed)
df_sm = query_stores_monthly(sd, ed)

if df_d.empty:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:70vh;">
        <div style="font-size:2.5rem;margin-bottom:16px;">⏳</div>
        <div style="color:rgba(255,255,255,0.4);font-size:0.9rem;font-weight:500;">Sem dados no período…</div>
        <div style="color:rgba(255,255,255,0.2);font-size:0.75rem;margin-top:6px;">
            Verifique a conexão com o banco de dados ou ajuste o período.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# Preparação dos dados

df_d["date"] = pd.to_datetime(df_d["date"])
if not df_m.empty:
    df_m["month_dt"] = pd.to_datetime(df_m["month"] + "-01")

# Aplica filtros nos DataFrames que não recebem filtro via SQL
if sel_cats:
    if not df_p.empty: df_p = df_p[df_p["category"].isin(sel_cats)]
    if not df_c.empty: df_c = df_c[df_c["category"].isin(sel_cats)]
if sel_stores:
    if not df_s.empty: df_s = df_s[df_s["store_name"].isin(sel_stores)]
    if not df_sm.empty: df_sm = df_sm[df_sm["store_name"].isin(sel_stores)]

# Cálculo dos KPIs
revenue  = df_d["revenue"].sum()
units    = df_d["units"].sum()
discount = df_d["discount"].sum() if "discount" in df_d.columns else 0
ticket   = revenue / units if units > 0 else 0
n_days   = (df_d["date"].max() - df_d["date"].min()).days + 1
avg_daily = revenue / n_days if n_days > 0 else 0

# Variação mês a mês
mom_pct = None
mom_label = ""
if not df_m.empty and len(df_m) >= 2:
    last2 = df_m.sort_values("month").tail(2)
    if len(last2) == 2:
        prev, curr = last2.iloc[0]["revenue"], last2.iloc[1]["revenue"]
        if prev > 0:
            mom_pct = ((curr - prev) / prev) * 100
            mom_label = f"vs mês anterior ({last2.iloc[1]['month']})"

# Melhores desempenhos
best_store   = df_s.sort_values("revenue", ascending=False).iloc[0] if not df_s.empty else None
best_cat     = df_c.sort_values("revenue", ascending=False).iloc[0] if not df_c.empty else None
best_product = df_p.sort_values("revenue", ascending=False).iloc[0] if not df_p.empty else None
peak_day     = df_d.loc[df_d["revenue"].idxmax()] if not df_d.empty else None


# Cabeçalho do dashboard

period_str = f"{s_date.strftime('%d/%m/%Y')} — {e_date.strftime('%d/%m/%Y')}"
now_str = datetime.now().strftime("%d/%m/%Y %H:%M")

st.markdown(f"""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-logo">✦</div>
        <div>
            <div class="topbar-title">Sales Analytics</div>
            <div class="topbar-sub">{period_str}</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="topbar-meta"><span class="live-dot"></span>Conectado</div>
        <div class="topbar-meta">{now_str}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Visão geral

st.markdown('<div class="section-label">Visão Geral</div>', unsafe_allow_html=True)

if mom_pct is not None:
    arrow = "↑" if mom_pct >= 0 else "↓"
    cls = "badge-up" if mom_pct >= 0 else "badge-down"
    mom_html = f'<span class="{cls}">{arrow} {abs(mom_pct):.1f}%</span> <span class="kpi-detail">{mom_label}</span>'
else:
    mom_html = '<span class="badge-neutral">—</span>'

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi">
        <div class="kpi-label">Receita Total</div>
        <div class="kpi-number">{brl(revenue)}</div>
        <div class="kpi-detail" style="margin-top:10px;">{mom_html}</div>
    </div>
    <div class="kpi">
        <div class="kpi-label">Unidades Vendidas</div>
        <div class="kpi-number">{num(units)}</div>
        <div class="kpi-detail">≈ {num(units / n_days) if n_days else 0}/dia em média</div>
    </div>
    <div class="kpi">
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-number">{brl(ticket)}</div>
        <div class="kpi-detail">Receita média por unidade</div>
    </div>
    <div class="kpi">
        <div class="kpi-label">Receita Diária Média</div>
        <div class="kpi-number">{brl(avg_daily)}</div>
        <div class="kpi-detail">{n_days} dias no período</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Insight narrativo (compacto)
if best_store is not None and peak_day is not None:
    peak_dt = peak_day["date"].strftime("%d/%m")
    st.markdown(f"""
    <div class="insight">
        <div class="insight-text">
            Loja líder: <strong>{best_store["store_name"]}</strong> ({brl(best_store["revenue"])})
            &nbsp;·&nbsp; Pico em <strong>{peak_dt}</strong> com <strong>{brl(peak_day["revenue"])}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Tendências

st.markdown('<div class="section-label">Tendências</div>', unsafe_allow_html=True)

col_trend, col_cat = st.columns([2.5, 1])

with col_trend:
    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Receita Diária</div>
        <div class="chart-card-badge">Média móvel 7 dias</div>
    </div></div>""", unsafe_allow_html=True)

    if not df_d.empty:
        df_d_sorted = df_d.sort_values("date")
        df_d_sorted["ma7"] = df_d_sorted["revenue"].rolling(7, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_d_sorted["date"], y=df_d_sorted["revenue"],
            mode='lines', name='Receita',
            line=dict(color=PAL["primary"], width=1.5),
            fill='tozeroy', fillcolor='rgba(129,140,248,0.06)',
            hovertemplate='%{x|%d/%m}<br>R$ %{y:,.2f}<extra></extra>',
        ))
        fig.add_trace(go.Scatter(
            x=df_d_sorted["date"], y=df_d_sorted["ma7"],
            mode='lines', name='Tendência',
            line=dict(color='rgba(255,255,255,0.3)', width=1.5, dash='dot'),
            hovertemplate='MA7: R$ %{y:,.2f}<extra></extra>',
        ))
        fig.update_layout(
            **CHART_LAYOUT, height=320,
            yaxis=dict(showgrid=True, gridcolor=PAL["grid"], zeroline=False),
            xaxis=dict(showgrid=False),
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right",
                        font=dict(size=10, color=PAL["text_dim"])),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

with col_cat:
    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Categorias</div>
        <div class="chart-card-badge">% da receita</div>
    </div></div>""", unsafe_allow_html=True)

    if not df_c.empty:
        df_c_sorted = df_c.sort_values("revenue", ascending=False)

        fig_d = go.Figure(go.Pie(
            labels=df_c_sorted["category"],
            values=df_c_sorted["revenue"],
            hole=0.65,
            marker=dict(colors=DONUT_COLORS[:len(df_c_sorted)],
                        line=dict(color='#09090b', width=2.5)),
            textinfo='percent',
            textfont=dict(size=10, color='rgba(255,255,255,0.6)'),
            hovertemplate='<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>',
            sort=False,
        ))
        total_cat = df_c_sorted["revenue"].sum()
        fig_d.update_layout(
            **CHART_LAYOUT, height=320, showlegend=False,
            annotations=[dict(
                text=f"<b>{compact(total_cat)}</b>",
                x=0.5, y=0.5, font_size=15,
                font_color="rgba(255,255,255,0.5)", showarrow=False,
            )],
        )
        st.plotly_chart(fig_d, use_container_width=True)

        # Legenda abaixo do donut
        legend_html = ""
        for i, (_, row) in enumerate(df_c_sorted.iterrows()):
            pct = (row["revenue"] / total_cat * 100) if total_cat > 0 else 0
            c = DONUT_COLORS[i % len(DONUT_COLORS)]
            legend_html += f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <div style="width:8px;height:8px;border-radius:50%;background:{c};flex-shrink:0;"></div>
                <div style="font-size:0.72rem;color:rgba(255,255,255,0.45);flex:1;">{row["category"]}</div>
                <div style="font-size:0.72rem;font-weight:600;color:rgba(255,255,255,0.55);">{pct:.0f}%</div>
            </div>"""
        st.markdown(f'<div style="padding:0 8px;">{legend_html}</div>', unsafe_allow_html=True)


# Rankings

st.markdown('<div class="section-label">Rankings</div>', unsafe_allow_html=True)

col_prod, col_store = st.columns(2)

def render_bar_chart(df, name_col, value_col, colors=None):
    """Renderiza um gráfico de barras horizontal em HTML."""
    if df.empty:
        return
    max_val = df[value_col].max()
    html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        pct = (row[value_col] / max_val * 100) if max_val > 0 else 0
        bg = colors[i % len(colors)] if colors else "linear-gradient(90deg, #6366f1, #a78bfa)"
        if not colors:
            bg_style = f"background:{bg};"
        else:
            bg_style = f"background:{bg};opacity:0.7;"
        html += f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
            <div style="width:120px;flex-shrink:0;font-size:0.72rem;color:rgba(255,255,255,0.5);
                text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                title="{row[name_col]}">{row[name_col]}</div>
            <div style="flex:1;height:26px;background:rgba(255,255,255,0.03);border-radius:6px;overflow:hidden;">
                <div style="height:100%;width:{pct}%;{bg_style}
                    border-radius:6px;transition:width 0.6s ease;"></div>
            </div>
            <div style="width:95px;flex-shrink:0;font-size:0.72rem;font-weight:600;
                color:rgba(255,255,255,0.6);text-align:right;">{brl(row[value_col])}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)

with col_prod:
    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Top 10 Produtos</div>
        <div class="chart-card-badge">por receita</div>
    </div></div>""", unsafe_allow_html=True)

    if not df_p.empty:
        render_bar_chart(df_p.sort_values("revenue", ascending=False).head(10),
                         "product_name", "revenue")

with col_store:
    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Performance por Loja</div>
        <div class="chart-card-badge">receita total</div>
    </div></div>""", unsafe_allow_html=True)

    if not df_s.empty:
        df_s_sort = df_s.sort_values("revenue", ascending=False)
        render_bar_chart(df_s_sort, "store_name", "revenue", colors=STORE_COLORS)


# Comparativo mensal

if not df_sm.empty:
    st.markdown('<div class="section-label">Evolução Mensal</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Receita Mensal por Loja</div>
        <div class="chart-card-badge">comparativo</div>
    </div></div>""", unsafe_allow_html=True)

    df_sm["month_dt"] = pd.to_datetime(df_sm["month"] + "-01")

    fig_m = go.Figure()
    for i, store in enumerate(df_sm["store_name"].unique()):
        store_data = df_sm[df_sm["store_name"] == store].sort_values("month_dt")
        fig_m.add_trace(go.Scatter(
            x=store_data["month_dt"], y=store_data["revenue"],
            mode='lines+markers', name=store,
            line=dict(color=STORE_COLORS[i % len(STORE_COLORS)], width=2),
            marker=dict(size=5),
            hovertemplate=f'{store}<br>%{{x|%b %Y}}: R$ %{{y:,.2f}}<extra></extra>',
        ))

    fig_m.update_layout(
        **CHART_LAYOUT, height=320,
        yaxis=dict(showgrid=True, gridcolor=PAL["grid"], zeroline=False),
        xaxis=dict(showgrid=False, dtick="M1", tickformat="%b"),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center",
                    font=dict(size=10, color=PAL["text_dim"])),
        hovermode="x unified",
    )
    st.plotly_chart(fig_m, use_container_width=True)


# Tabela detalhada

if not df_p.empty:
    st.markdown('<div class="section-label">Dados Detalhados</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="chart-card"><div class="chart-card-header">
        <div class="chart-card-title">Produtos</div>
        <div class="chart-card-badge">ordenável por qualquer coluna</div>
    </div></div>""", unsafe_allow_html=True)

    st.dataframe(
        df_p,
        column_config={
            "product_name": st.column_config.TextColumn("Produto", width="large"),
            "category": st.column_config.TextColumn("Categoria"),
            "sku": st.column_config.TextColumn("SKU"),
            "units": st.column_config.NumberColumn("Unidades", format="%d"),
            "revenue": st.column_config.ProgressColumn(
                "Receita", format="R$ %.2f",
                max_value=float(df_p["revenue"].max()) if not df_p.empty else 1,
            ),
        },
        use_container_width=True, hide_index=True, height=380,
    )


# Rodapé

st.markdown(f"""
<div style="text-align:center;padding:48px 0 12px;margin-top:32px;">
    <div style="width:32px;height:2px;
        background:linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
        margin:0 auto 18px;"></div>
    <div style="font-size: 0.62rem; color: rgba(255,255,255,0.1); font-weight: 500;
        letter-spacing: 1px; text-transform: uppercase;">
        Sales Analytics &middot; {now_str}
    </div>
</div>
""", unsafe_allow_html=True)
