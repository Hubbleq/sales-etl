# Dashboard de Análise de Vendas
# Interface minimalista e profissional, sem emojis.
# Foco em clareza, hierarquia visual e novos KPIs de negócio.

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# Configuração da página
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# URL da API
API_URL = "http://localhost:8000"

# CSS Minimalista e Profissional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #0e1117;
        color: #fafafa;
    }

    /* Cartões de KPI */
    .metric-card {
        background-color: #1e2130;
        border: 1px solid #2e3b4e;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        border-color: #4e5d6c;
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a0aab5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 4px;
    }
    .positive { color: #00e676; }
    .negative { color: #ff5252; }

    /* Cabeçalhos de Seção */
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 20px;
        color: #e0e0e0;
        border-left: 4px solid #3b82f6;
        padding-left: 12px;
    }

    /* Ajustes gerais */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
</style>
""", unsafe_allow_html=True)


# Sidebar de Filtros
with st.sidebar:
    st.header("Filtros")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Início", date(2025, 1, 1), format="DD/MM/YYYY")
    with col2:
        end_date = st.date_input("Fim", date(2025, 12, 31), format="DD/MM/YYYY")

    st.divider()
    top_n = st.number_input("Top Produtos", min_value=3, max_value=20, value=7)
    
    if st.button("Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.experimental_rerun()


# Função de busca de dados
@st.cache_data(ttl=60)
def fetch_data(endpoint, params):
    try:
        r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Erro ao conectar com API ({endpoint}): {e}")
        return []

params = {"start": str(start_date), "end": str(end_date)}

# Carregamento de dados (paralelo na teoria, sequencial aqui)
data_monthly = fetch_data("/sales/monthly", params)
data_products = fetch_data("/products/top", {**params, "limit": top_n})
data_stores = fetch_data("/stores/performance", params)
data_categories = fetch_data("/products/categories", params)

# DataFrames
df_m = pd.DataFrame(data_monthly)
df_p = pd.DataFrame(data_products)
df_s = pd.DataFrame(data_stores)
df_c = pd.DataFrame(data_categories)

if df_m.empty:
    st.warning("Sem dados para o período selecionado.")
    st.stop()

# ==============================================================================
# CÁLCULO DE KPIS
# ==============================================================================
total_rev = df_m["revenue"].sum()
total_units = df_m["units"].sum()
total_disc = df_m["discount"].sum() if "discount" in df_m.columns else 0
avg_ticket = total_rev / total_units if total_units else 0

# Melhor Loja e Melhor Categoria
best_store = df_s.iloc[0]["store_name"] if not df_s.empty else "N/A"
best_cat = df_c.iloc[0]["category"] if not df_c.empty else "N/A"

# Margem bruta aproximada (Impacto dos descontos)
discount_impact = (total_disc / (total_rev + total_disc) * 100) if (total_rev + total_disc) else 0

# Layout Principal

st.title("Sales Analytics")
st.markdown("Visão consolidade de desempenho comercial")

# Linha 1: KPIs Financeiros
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Receita Total</div>
        <div class="metric-value">R$ {total_rev:,.0f}</div>
        <div class="metric-sub">Faturamento bruto</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Volume de Vendas</div>
        <div class="metric-value">{total_units:,.0f}</div>
        <div class="metric-sub">Unidades vendidas</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ticket Médio</div>
        <div class="metric-value">R$ {avg_ticket:,.2f}</div>
        <div class="metric-sub">Por unidade</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Descontos Concedidos</div>
        <div class="metric-value">R$ {total_disc:,.0f}</div>
        <div class="metric-sub">{discount_impact:.1f}% sobre o bruto</div>
    </div>
    """, unsafe_allow_html=True)


# Linha 2: KPIs de Destaque
c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #8b5cf6;">
        <div class="metric-label">Melhor Loja</div>
        <div class="metric-value">{best_store}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid #10b981;">
        <div class="metric-label">Categoria Principal</div>
        <div class="metric-value">{best_cat}</div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# GRÁFICOS
# ==============================================================================

# Seção 1: Evolução
st.markdown('<div class="section-title">Evolução Mensal</div>', unsafe_allow_html=True)

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=df_m["month"], 
    y=df_m["revenue"],
    mode='lines+markers',
    name='Receita',
    line=dict(color='#3b82f6', width=3),
    fill='tozeroy',
    fillcolor='rgba(59, 130, 246, 0.1)'
))
fig_trend.add_trace(go.Bar(
    x=df_m["month"],
    y=df_m["discount"],
    name='Descontos',
    marker_color='rgba(239, 68, 68, 0.5)'
))
fig_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=0, b=0),
    height=350,
    legend=dict(orientation="h", y=1.1)
)
st.plotly_chart(fig_trend, use_container_width=True)


# Seção 2: Categorias e Lojas
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-title">Performance por Categoria</div>', unsafe_allow_html=True)
    if not df_c.empty:
        fig_cat = px.pie(
            df_c, 
            names='category', 
            values='revenue',
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            showlegend=True 
        )
        st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    st.markdown('<div class="section-title">Top Lojas</div>', unsafe_allow_html=True)
    if not df_s.empty:
        df_s_sorted = df_s.sort_values("revenue", ascending=True)
        fig_store = px.bar(
            df_s_sorted,
            x="revenue",
            y="store_name",
            orientation='h',
            text="revenue",
            color="revenue",
            color_continuous_scale="Blues"
        )
        fig_store.update_traces(texttemplate='R$ %{text:,.0f}', textposition='inside')
        fig_store.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            xaxis=dict(showgrid=False, showticklabels=False, title=None),
            yaxis=dict(title=None),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_store, use_container_width=True)


# Seção 3: Detalhe de Produtos
st.markdown('<div class="section-title">Ranking de Produtos</div>', unsafe_allow_html=True)

if not df_p.empty:
    # Tabela estilizada via CSS/HTML seria ideal, mas st.dataframe é funcional
    # Vamos limpar o dataframe para exibição
    df_show = df_p[["product_name", "category", "units", "revenue"]].copy()
    df_show.columns = ["Produto", "Categoria", "Unidades", "Receita"]
    
    st.dataframe(
        df_show.style.format({
            "Receita": "R$ {:,.2f}",
            "Unidades": "{:,.0f}"
        }).background_gradient(subset=["Receita"], cmap="Blues"),
        use_container_width=True,
        hide_index=True
    )
