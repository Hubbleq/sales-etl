# Sales Analytics Dashboard (Cloud-Ready)
# Connects directly to Supabase via SQLAlchemy.
# Works on Streamlit Cloud (st.secrets) or locally (.env).

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

# Database — tries st.secrets first, then .env
try:
    DB_URL = st.secrets["DATABASE_URL"]
except Exception:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    DB_URL = os.environ.get("DATABASE_URL", "")

# Normalize to psycopg2 for cloud compatibility
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


# -- CSS ---------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }
    .stApp { background: #09090b !important; }
    .stDeployButton, #MainMenu, footer, header { display: none !important; }
    .block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1440px; }

    section[data-testid="stSidebar"] {
        background: #0c0c0f !important;
        border-right: 1px solid rgba(255,255,255,0.04) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: rgba(255,255,255,0.4) !important;
        font-size: 0.7rem !important; font-weight: 600 !important;
        text-transform: uppercase !important; letter-spacing: 1px !important;
    }

    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 18px 24px; margin-bottom: 20px;
        background: rgba(255,255,255,0.015);
        border: 1px solid rgba(255,255,255,0.04); border-radius: 14px;
    }
    .topbar-brand { display: flex; align-items: center; gap: 14px; }
    .topbar-logo {
        width: 36px; height: 36px; border-radius: 10px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; box-shadow: 0 4px 20px rgba(99,102,241,0.25);
    }
    .topbar-title { font-size: 1rem; font-weight: 700; color: #fafafa; }
    .topbar-sub { font-size: 0.7rem; color: rgba(255,255,255,0.25); margin-top: 1px; }
    .topbar-right { display: flex; align-items: center; gap: 20px; }
    .topbar-meta { font-size: 0.7rem; color: rgba(255,255,255,0.2); display: flex; align-items: center; gap: 6px; }
    .live-dot {
        width: 6px; height: 6px; border-radius: 50%; background: #34d399;
        box-shadow: 0 0 8px #34d399; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

    .section-label {
        font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 1.5px; color: rgba(255,255,255,0.2);
        padding: 28px 0 12px; border-top: 1px solid rgba(255,255,255,0.03);
        margin-top: 8px;
    }

    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
    .kpi {
        background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 14px; padding: 20px 22px; position: relative; overflow: hidden;
    }
    .kpi-accent { font-size: 1.2rem; margin-bottom: 10px; }
    .kpi-label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: rgba(255,255,255,0.3); }
    .kpi-number { font-size: 1.5rem; font-weight: 800; color: #fafafa; margin: 6px 0 4px; letter-spacing: -0.5px; }
    .kpi-detail { font-size: 0.7rem; color: rgba(255,255,255,0.25); }
    .badge-up { color: #34d399; font-weight: 700; font-size: 0.78rem; }
    .badge-down { color: #f87171; font-weight: 700; font-size: 0.78rem; }
    .badge-neutral { color: rgba(255,255,255,0.2); font-size: 0.78rem; }

    .insight {
        display: flex; align-items: flex-start; gap: 14px;
        background: rgba(99,102,241,0.04); border: 1px solid rgba(99,102,241,0.1);
        border-radius: 12px; padding: 16px 20px; margin: 12px 0 8px;
    }
    .insight-icon { font-size: 1.1rem; margin-top: 1px; }
    .insight-text { font-size: 0.78rem; color: rgba(255,255,255,0.45); line-height: 1.6; }
    .insight-text strong { color: rgba(255,255,255,0.8); font-weight: 600; }

    .chart-card {
        background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.04);
        border-radius: 14px; padding: 22px 24px 16px; margin-bottom: 16px;
    }
    .chart-card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
    .chart-card-title { font-size: 0.82rem; font-weight: 600; color: rgba(255,255,255,0.75); }
    .chart-card-badge { font-size: 0.65rem; color: rgba(255,255,255,0.2); font-weight: 500; }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); border-radius: 3px; }

    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
        .kpi-row { grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .kpi-number { font-size: 1.2rem; }
        .topbar { flex-direction: column; align-items: flex-start; gap: 8px; }
    }
</style>
""", unsafe_allow_html=True)


# -- Queries ------------------------------------------------------------------

def _run(sql, params):
    """Execute a query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.DataFrame(conn.execute(text(sql), params).mappings().all())

@st.cache_data(ttl=120, show_spinner=False)
def query_daily(start, end):
    return _run(
        "SELECT data_venda AS date, SUM(valor_total)::FLOAT AS revenue, "
        "SUM(quantidade) AS units, SUM(desconto)::FLOAT AS discount "
        "FROM fato_vendas WHERE data_venda BETWEEN :s AND :e GROUP BY 1 ORDER BY 1",
        {"s": start, "e": end},
    )

@st.cache_data(ttl=120, show_spinner=False)
def query_monthly(start, end):
    return _run(
        "SELECT TO_CHAR(data_venda, 'YYYY-MM') AS month, SUM(valor_total)::FLOAT AS revenue, "
        "SUM(quantidade) AS units, SUM(desconto)::FLOAT AS discount, COUNT(*) AS rows "
        "FROM fato_vendas WHERE data_venda BETWEEN :s AND :e GROUP BY 1 ORDER BY 1",
        {"s": start, "e": end},
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


# -- Formatters ---------------------------------------------------------------

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


# -- Chart defaults -----------------------------------------------------------

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


# -- Sidebar ------------------------------------------------------------------

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


# -- Data loading -------------------------------------------------------------

sd, ed = str(s_date), str(e_date)
df_d  = query_daily(sd, ed)
df_m  = query_monthly(sd, ed)
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


# -- Data prep ----------------------------------------------------------------

df_d["date"] = pd.to_datetime(df_d["date"])
if not df_m.empty:
    df_m["month_dt"] = pd.to_datetime(df_m["month"] + "-01")

# Apply filters
if sel_cats:
    if not df_p.empty: df_p = df_p[df_p["category"].isin(sel_cats)]
    if not df_c.empty: df_c = df_c[df_c["category"].isin(sel_cats)]
if sel_stores:
    if not df_s.empty: df_s = df_s[df_s["store_name"].isin(sel_stores)]
    if not df_sm.empty: df_sm = df_sm[df_sm["store_name"].isin(sel_stores)]

# KPIs
revenue  = df_d["revenue"].sum()
units    = df_d["units"].sum()
discount = df_d["discount"].sum() if "discount" in df_d.columns else 0
ticket   = revenue / units if units > 0 else 0
n_days   = (df_d["date"].max() - df_d["date"].min()).days + 1
avg_daily = revenue / n_days if n_days > 0 else 0

# Month-over-month
mom_pct = None
mom_label = ""
if not df_m.empty and len(df_m) >= 2:
    last2 = df_m.sort_values("month").tail(2)
    if len(last2) == 2:
        prev, curr = last2.iloc[0]["revenue"], last2.iloc[1]["revenue"]
        if prev > 0:
            mom_pct = ((curr - prev) / prev) * 100
            mom_label = f"vs mês anterior ({last2.iloc[1]['month']})"

# Best performers
best_store   = df_s.sort_values("revenue", ascending=False).iloc[0] if not df_s.empty else None
best_cat     = df_c.sort_values("revenue", ascending=False).iloc[0] if not df_c.empty else None
best_product = df_p.sort_values("revenue", ascending=False).iloc[0] if not df_p.empty else None
peak_day     = df_d.loc[df_d["revenue"].idxmax()] if not df_d.empty else None


# -- Header -------------------------------------------------------------------

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


# -- Section 1: Overview -----------------------------------------------------

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

# Narrative insight
if best_store is not None and best_cat is not None and peak_day is not None:
    peak_dt = peak_day["date"].strftime("%d/%m/%Y")
    st.markdown(f"""
    <div class="insight">
        <div class="insight-icon">💡</div>
        <div class="insight-text">
            No período selecionado, a loja <strong>{best_store["store_name"]}</strong> liderou em receita
            com <strong>{brl(best_store["revenue"])}</strong>.
            A categoria mais rentável foi <strong>{best_cat["category"]}</strong>
            ({brl(best_cat["revenue"])}).
            O dia de maior faturamento foi <strong>{peak_dt}</strong>
            com <strong>{brl(peak_day["revenue"])}</strong> em vendas.
        </div>
    </div>
    """, unsafe_allow_html=True)


# -- Section 2: Trends -------------------------------------------------------

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

        # Legend below donut
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


# -- Section 3: Rankings -----------------------------------------------------

st.markdown('<div class="section-label">Rankings</div>', unsafe_allow_html=True)

col_prod, col_store = st.columns(2)

def render_bar_chart(df, name_col, value_col, colors=None):
    """Render an HTML horizontal bar chart."""
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

        # Store insight
        if "units" in df_s_sort.columns:
            total_units = df_s_sort["units"].sum()
            top = df_s_sort.iloc[0]
            top_pct = (top["revenue"] / df_s_sort["revenue"].sum() * 100)
            st.markdown(f"""
            <div class="insight" style="margin-top:16px;">
                <div class="insight-icon">🏢</div>
                <div class="insight-text">
                    <strong>{top["store_name"]}</strong> concentra <strong>{top_pct:.0f}%</strong> da receita
                    com <strong>{num(top["units"])}</strong> unidades vendidas
                    de um total de <strong>{num(total_units)}</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)


# -- Section 4: Monthly comparison -------------------------------------------

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


# -- Section 5: Detail table -------------------------------------------------

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


# -- Footer -------------------------------------------------------------------

st.markdown(f"""
<div style="text-align:center;padding:40px 0 8px;margin-top:24px;">
    <div style="width:24px;height:1px;background:rgba(255,255,255,0.06);margin:0 auto 16px;"></div>
    <div style="font-size:0.65rem;color:rgba(255,255,255,0.12);font-weight:500;letter-spacing:0.5px;">
        Sales Analytics v8 · Supabase + Streamlit · {now_str}
    </div>
</div>
""", unsafe_allow_html=True)
