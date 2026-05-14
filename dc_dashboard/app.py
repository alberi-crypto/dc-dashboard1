"""
DC Distribuidora — Dashboard Gerencial Executivo
Aplicativo Streamlit para análise financeira mensal.

Como rodar:
    pip install -r requirements.txt
    streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import hmac

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================
st.set_page_config(
    page_title="DC Distribuidora — Dashboard Gerencial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# AUTENTICAÇÃO POR SENHA
# ============================================================
def check_password() -> bool:
    """Tela de login com senha. Retorna True se autenticado."""

    def password_entered():
        senha_correta = ""
        # 1) tenta ler de st.secrets (modo cloud)
        try:
            senha_correta = st.secrets.get("password", "")
        except Exception:
            pass
        # 2) fallback para variável de ambiente (modo local)
        if not senha_correta:
            senha_correta = os.environ.get("DC_PASSWORD", "dc2026")  # default local

        if hmac.compare_digest(st.session_state.get("password_input", ""), senha_correta):
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Tela de login estilizada
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none; }
            .login-card {
                max-width: 420px; margin: 4rem auto 1rem auto;
                background: white; padding: 2rem 2rem 1.5rem 2rem;
                border-radius: 12px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);
                border-top: 5px solid #0B2D5B;
            }
            .login-title { color: #0B2D5B; font-size: 1.6rem; font-weight: 700; text-align: center; margin: 0; }
            .login-sub { color: #5D6D7E; text-align: center; margin: 0.2rem 0 1rem 0; }
        </style>
        <div class="login-card">
            <p class="login-title">DC Distribuidora</p>
            <p class="login-sub">Dashboard Gerencial Executivo</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "🔐 Senha de acesso",
            type="password",
            key="password_input",
            on_change=password_entered,
            placeholder="Digite a senha e pressione Enter",
        )
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Senha incorreta. Tente novamente.")
        st.caption("Acesso restrito · Em caso de dúvida, contate a Controladoria.")
    return False


if not check_password():
    st.stop()

NAVY = "#0B2D5B"
BLUE = "#1F77B4"
GOLD = "#D4A017"
GREEN = "#2E8B57"
RED = "#C0392B"
GREY = "#7F8C8D"
LIGHT = "#EAF1F8"

# CSS customizado
st.markdown(
    f"""
    <style>
        .main-header {{
            background: linear-gradient(90deg, {NAVY} 0%, #173B7A 100%);
            padding: 1.2rem 1.5rem;
            border-radius: 8px;
            color: white;
            margin-bottom: 1rem;
        }}
        .main-header h1 {{ color: white; margin: 0; font-size: 1.8rem; }}
        .main-header p {{ color: #D4A017; margin: 0; font-weight: 600; }}
        .kpi-card {{
            background: white;
            border-left: 4px solid {NAVY};
            padding: 0.8rem 1rem;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}
        .kpi-label {{ color: {GREY}; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ color: {NAVY}; font-size: 1.5rem; font-weight: 700; margin: 0.2rem 0; }}
        .kpi-delta-pos {{ color: {GREEN}; font-size: 0.85rem; font-weight: 600; }}
        .kpi-delta-neg {{ color: {RED}; font-size: 0.85rem; font-weight: 600; }}
        .insight-box {{
            background: {LIGHT};
            border-left: 4px solid {GOLD};
            padding: 0.8rem 1rem;
            border-radius: 4px;
            margin: 0.8rem 0;
            color: {NAVY};
            font-style: italic;
        }}
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
        .stTabs [data-baseweb="tab"] {{
            background: {LIGHT}; padding: 8px 16px; border-radius: 6px 6px 0 0;
        }}
        .stTabs [aria-selected="true"] {{ background: {NAVY} !important; color: white !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================
@st.cache_data
def carregar_dados(caminho: str):
    dre = pd.read_excel(caminho, sheet_name="DRE")
    bal = pd.read_excel(caminho, sheet_name="Balanco")
    ind = pd.read_excel(caminho, sheet_name="Indicadores")
    return dre, bal, ind


def obter_colunas_meses(df, exclude=("Conta", "Bloco", "Grupo", "Indicador")):
    return [c for c in df.columns if c not in exclude]


def formatar_real(v, decimais=2):
    """Formata sempre como R$ inteiro (sem K/M), padrão BR (1.234.567,89)."""
    if pd.isna(v):
        return "-"
    sinal = "-" if v < 0 else ""
    s = f"{abs(v):,.{decimais}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {sinal}{s}"


def num_curto(v):
    """Texto compacto apenas para rótulos de gráficos: número inteiro com separador BR (sem R$)."""
    if pd.isna(v):
        return "-"
    sinal = "-" if v < 0 else ""
    s = f"{abs(v):,.0f}".replace(",", ".")
    return f"{sinal}{s}"


def formatar_pct(v, decimals=2):
    if pd.isna(v):
        return "-"
    return f"{v:.{decimals}f}%".replace(".", ",")


def var_pct(novo, ant):
    if ant is None or ant == 0 or pd.isna(ant):
        return None
    return (novo - ant) / abs(ant) * 100


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(f"### 📊 DC Distribuidora")
st.sidebar.caption("Dashboard Gerencial Executivo")
st.sidebar.markdown("---")

caminho_default = os.path.join(os.path.dirname(__file__), "dados", "dados_mensais.xlsx")
arquivo_upload = st.sidebar.file_uploader(
    "📁 Carregar planilha de dados (.xlsx)",
    type=["xlsx"],
    help="Use o template em ./dados/dados_mensais.xlsx",
)
if arquivo_upload is not None:
    dre_df, bal_df, ind_df = carregar_dados(arquivo_upload)
    st.sidebar.success("✓ Arquivo carregado")
else:
    if not os.path.exists(caminho_default):
        st.sidebar.error(f"Arquivo padrão não encontrado em {caminho_default}")
        st.stop()
    dre_df, bal_df, ind_df = carregar_dados(caminho_default)
    st.sidebar.info("Usando dados/dados_mensais.xlsx")

meses = obter_colunas_meses(dre_df)
if not meses:
    st.error("Nenhuma coluna de mês encontrada na aba DRE.")
    st.stop()

meses_sel = st.sidebar.multiselect(
    "📅 Período de análise", meses, default=meses
)
if len(meses_sel) < 1:
    st.warning("Selecione pelo menos um mês na barra lateral.")
    st.stop()

mes_ref = st.sidebar.selectbox(
    "🎯 Mês de referência (KPIs)",
    meses_sel,
    index=len(meses_sel) - 1,
)
mes_ant_idx = meses_sel.index(mes_ref) - 1
mes_ant = meses_sel[mes_ant_idx] if mes_ant_idx >= 0 else None

st.sidebar.markdown("---")
st.sidebar.caption("**Como adicionar novo mês:**\n\n1. Abra a planilha em dados/dados_mensais.xlsx\n2. Adicione uma nova coluna (ex: mai/26)\n3. Preencha as 3 abas\n4. Salve e recarregue o app (F5)")
st.sidebar.markdown("---")
st.sidebar.caption("Controladoria Estratégica · Cowork")
if st.sidebar.button("🚪 Sair (logout)"):
    st.session_state["password_correct"] = False
    st.rerun()

# ============================================================
# HEADER
# ============================================================
st.markdown(
    f"""
    <div class="main-header">
        <h1>DC Distribuidora — Painel Gerencial Executivo</h1>
        <p>Análise financeira · Mês de referência: {mes_ref}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS DE LINHA
# ============================================================
def linha_dre(bloco):
    res = dre_df[dre_df["Bloco"] == bloco]
    if res.empty:
        return None
    return res.iloc[0]


def serie_dre(bloco, meses):
    row = linha_dre(bloco)
    if row is None:
        return [0] * len(meses)
    return [row.get(m, 0) for m in meses]


def total_balanco(grupo, mes):
    sub = bal_df[bal_df["Grupo"] == grupo]
    return sub[mes].sum() if not sub.empty else 0


def serie_indicador(nome, meses):
    row = ind_df[ind_df["Indicador"] == nome]
    if row.empty:
        return [None] * len(meses)
    return [row.iloc[0].get(m, None) for m in meses]


# ============================================================
# DADOS DERIVADOS
# ============================================================
rec_bruta = serie_dre("TOPLINE", meses_sel)
rec_liq = serie_dre("LIQUIDA", meses_sel)
margem1 = serie_dre("MG1", meses_sel)
res_bruto = serie_dre("RES_BRUTO", meses_sel)
ebitda = serie_dre("EBITDA", meses_sel)
lucro = serie_dre("LUCRO", meses_sel)
desp_com = [abs(v) for v in serie_dre("COMERCIAL", meses_sel)]
desp_log = [abs(v) for v in serie_dre("LOGISTICA", meses_sel)]
desp_adm = [abs(v) for v in serie_dre("ADM", meses_sel)]

mg1_pct = [(m / r * 100) if r else None for m, r in zip(margem1, rec_liq)]
mgB_pct = [(m / r * 100) if r else None for m, r in zip(res_bruto, rec_liq)]
mgE_pct = [(m / r * 100) if r else None for m, r in zip(ebitda, rec_liq)]
mgL_pct = [(m / r * 100) if r else None for m, r in zip(lucro, rec_liq)]

idx_ref = meses_sel.index(mes_ref)
idx_ant = idx_ref - 1 if idx_ref > 0 else None

# ============================================================
# KPIs
# ============================================================
def kpi_card(label, value_str, delta=None, suffix=""):
    if delta is None:
        delta_html = ""
    else:
        cor = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        seta = "▲" if delta >= 0 else "▼"
        delta_html = f"<div class='{cor}'>{seta} {delta:+.2f}%{suffix}</div>"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value_str}</div>
        {delta_html}
    </div>
    """


c1, c2, c3, c4, c5 = st.columns(5)
delta_rec = var_pct(rec_bruta[idx_ref], rec_bruta[idx_ant]) if idx_ant is not None else None
delta_mg1 = (mg1_pct[idx_ref] - mg1_pct[idx_ant]) if idx_ant is not None and mg1_pct[idx_ref] and mg1_pct[idx_ant] else None
delta_ebitda = var_pct(ebitda[idx_ref], ebitda[idx_ant]) if idx_ant is not None else None
delta_lucro = var_pct(lucro[idx_ref], lucro[idx_ant]) if idx_ant is not None else None

with c1:
    st.markdown(kpi_card("Receita Bruta", formatar_real(rec_bruta[idx_ref]), delta_rec), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Margem 1", formatar_real(margem1[idx_ref]),
                          delta_mg1, suffix=" p.p." if delta_mg1 else ""), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("EBITDA", formatar_real(ebitda[idx_ref]), delta_ebitda), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Resultado Líquido", formatar_real(lucro[idx_ref]), delta_lucro), unsafe_allow_html=True)
with c5:
    liq_cor_vals = serie_indicador("Liquidez Corrente", meses_sel)
    st.markdown(kpi_card("Liquidez Corrente", f"{liq_cor_vals[idx_ref]:.2f}",
                          var_pct(liq_cor_vals[idx_ref], liq_cor_vals[idx_ant]) if idx_ant is not None else None),
                          unsafe_allow_html=True)

st.markdown(" ")

# ============================================================
# ABAS
# ============================================================
tabs = st.tabs([
    "📈 Faturamento & Margens",
    "💰 Resultado & EBITDA",
    "📊 Despesas",
    "🏦 Balanço",
    "💧 Liquidez & Endividamento",
    "🔄 Ciclo Financeiro",
    "📋 DRE Completa",
])

# ========== ABA 1: FATURAMENTO & MARGENS ==========
with tabs[0]:
    st.subheader("Faturamento e Margens")
    col1, col2 = st.columns([3, 2])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses_sel, y=rec_bruta, name="Receita Bruta",
                              marker_color=NAVY,
                              text=[num_curto(v) for v in rec_bruta], textposition="outside",
                              hovertemplate="%{x}<br>Receita Bruta: R$ %{y:,.2f}<extra></extra>"))
        fig.add_trace(go.Bar(x=meses_sel, y=rec_liq, name="Receita Líquida",
                              marker_color=BLUE,
                              text=[num_curto(v) for v in rec_liq], textposition="outside",
                              hovertemplate="%{x}<br>Receita Líquida: R$ %{y:,.2f}<extra></extra>"))
        fig.update_layout(barmode="group", height=400, title="Evolução do Faturamento",
                          legend=dict(orientation="h", y=-0.15),
                          margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses_sel, y=margem1, name="Margem 1 (R$)",
                              marker_color=NAVY, yaxis="y",
                              text=[num_curto(v) for v in margem1], textposition="outside",
                              hovertemplate="%{x}<br>Margem 1: R$ %{y:,.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=meses_sel, y=mg1_pct, name="Margem 1 %",
                                  mode="lines+markers+text", line=dict(color=GOLD, width=3),
                                  marker=dict(size=10), yaxis="y2",
                                  text=[f"{v:.2f}%" for v in mg1_pct], textposition="top center"))
        fig.update_layout(height=400, title="Margem 1 — Valor e %",
                          yaxis=dict(title="R$"),
                          yaxis2=dict(title="%", overlaying="y", side="right"),
                          legend=dict(orientation="h", y=-0.15),
                          margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Margens consolidadas (% sobre Receita Líquida — base Excel)")
    margens_df = pd.DataFrame({
        "Mês": meses_sel,
        "Margem 1 %": [f"{v:.2f}%" if v else "-" for v in mg1_pct],
        "Margem Bruta %": [f"{v:.2f}%" if v else "-" for v in mgB_pct],
        "Margem EBITDA %": [f"{v:.2f}%" if v else "-" for v in mgE_pct],
        "Margem Líquida %": [f"{v:.2f}%" if v else "-" for v in mgL_pct],
    })
    st.dataframe(margens_df, use_container_width=True, hide_index=True)

    if idx_ant is not None and mg1_pct[idx_ref] is not None and mg1_pct[idx_ant] is not None:
        var_p = mg1_pct[idx_ref] - mg1_pct[idx_ant]
        sinal = "queda" if var_p < 0 else "alta"
        st.markdown(
            f"<div class='insight-box'><b>Insight:</b> Margem 1 em {mes_ref} = {mg1_pct[idx_ref]:.2f}% — "
            f"<b>{sinal} de {abs(var_p):.2f} p.p.</b> vs. {mes_ant}. "
            f"Cada 1 p.p. de Margem 1 ≈ {formatar_real(rec_liq[idx_ref]/100)} no período.</div>",
            unsafe_allow_html=True,
        )

# ========== ABA 2: RESULTADO & EBITDA ==========
with tabs[1]:
    st.subheader("Resultado Bruto, EBITDA e Resultado Líquido")
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        cores = [GREEN if v >= 0 else RED for v in ebitda]
        fig.add_trace(go.Bar(x=meses_sel, y=ebitda, marker_color=cores,
                              text=[num_curto(v) for v in ebitda], textposition="outside",
                              hovertemplate="%{x}<br>EBITDA: R$ %{y:,.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=meses_sel, y=mgE_pct, name="Margem EBITDA %",
                                  mode="lines+markers", line=dict(color=GOLD, width=2.5),
                                  yaxis="y2"))
        fig.update_layout(height=400, title="EBITDA e Margem EBITDA",
                          yaxis=dict(title="R$"),
                          yaxis2=dict(title="%", overlaying="y", side="right"),
                          showlegend=False,
                          margin=dict(l=20, r=20, t=50, b=20))
        fig.add_hline(y=0, line_dash="solid", line_color="#555")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        cores = [GREEN if v >= 0 else RED for v in lucro]
        fig.add_trace(go.Bar(x=meses_sel, y=lucro, marker_color=cores,
                              text=[num_curto(v) for v in lucro], textposition="outside",
                              hovertemplate="%{x}<br>Resultado Líquido: R$ %{y:,.2f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=meses_sel, y=mgL_pct, name="Margem Líquida %",
                                  mode="lines+markers", line=dict(color=GOLD, width=2.5),
                                  yaxis="y2"))
        fig.update_layout(height=400, title="Resultado Líquido e Margem Líquida",
                          yaxis=dict(title="R$"),
                          yaxis2=dict(title="%", overlaying="y", side="right"),
                          showlegend=False,
                          margin=dict(l=20, r=20, t=50, b=20))
        fig.add_hline(y=0, line_dash="solid", line_color="#555")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Acumulado do período selecionado")
    acum_data = {
        "Linha": ["Receita Bruta", "Receita Líquida", "Margem 1", "Resultado Bruto", "EBITDA", "Resultado Líquido"],
        "Acumulado (R$)": [
            formatar_real(sum(rec_bruta)),
            formatar_real(sum(rec_liq)),
            formatar_real(sum(margem1)),
            formatar_real(sum(res_bruto)),
            formatar_real(sum(ebitda)),
            formatar_real(sum(lucro)),
        ],
    }
    st.dataframe(pd.DataFrame(acum_data), use_container_width=True, hide_index=True)

# ========== ABA 3: DESPESAS ==========
with tabs[2]:
    st.subheader("Análise de Despesas Operacionais")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses_sel, y=desp_com, name="Comerciais", marker_color=NAVY))
    fig.add_trace(go.Bar(x=meses_sel, y=desp_log, name="Logística", marker_color=BLUE))
    fig.add_trace(go.Bar(x=meses_sel, y=desp_adm, name="Administrativas", marker_color=GOLD))
    fig.update_layout(barmode="stack", height=450, title="Evolução das Despesas Operacionais (R$)",
                      legend=dict(orientation="h", y=-0.12),
                      margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

    despesas_df = pd.DataFrame({
        "Bloco": ["Comerciais", "Logística", "Administrativas", "TOTAL"],
        **{m: [formatar_real(desp_com[i]), formatar_real(desp_log[i]),
                 formatar_real(desp_adm[i]),
                 formatar_real(desp_com[i]+desp_log[i]+desp_adm[i])]
            for i, m in enumerate(meses_sel)},
        f"% RL ({mes_ref})": [
            formatar_pct(desp_com[idx_ref]/rec_liq[idx_ref]*100) if rec_liq[idx_ref] else "-",
            formatar_pct(desp_log[idx_ref]/rec_liq[idx_ref]*100) if rec_liq[idx_ref] else "-",
            formatar_pct(desp_adm[idx_ref]/rec_liq[idx_ref]*100) if rec_liq[idx_ref] else "-",
            formatar_pct((desp_com[idx_ref]+desp_log[idx_ref]+desp_adm[idx_ref])/rec_liq[idx_ref]*100) if rec_liq[idx_ref] else "-",
        ],
    })
    st.dataframe(despesas_df, use_container_width=True, hide_index=True)

    total_op_ref = desp_com[idx_ref] + desp_log[idx_ref] + desp_adm[idx_ref]
    pct_rl = total_op_ref / rec_liq[idx_ref] * 100 if rec_liq[idx_ref] else 0
    st.markdown(
        f"<div class='insight-box'><b>Despesa total / Receita Líquida em {mes_ref}: {pct_rl:.2f}%</b>. "
        f"Banda recomendada para distribuição: 15%–20%. Cada 1 p.p. de eficiência ≈ "
        f"{formatar_real(rec_liq[idx_ref]/100)}/mês.</div>",
        unsafe_allow_html=True,
    )

# ========== ABA 4: BALANÇO ==========
with tabs[3]:
    st.subheader(f"Balanço Patrimonial — {mes_ref}")

    ac = total_balanco("AC", mes_ref)
    anc = total_balanco("ANC", mes_ref)
    pc = total_balanco("PC", mes_ref)
    pnc = total_balanco("PNC", mes_ref)
    pl_val = total_balanco("PL", mes_ref)
    ativo_total = ac + anc
    pas_total = pc + pnc + pl_val

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ativo Total", formatar_real(ativo_total))
    c2.metric("Passivo + PL", formatar_real(pas_total))
    c3.metric("Patrimônio Líquido", formatar_real(pl_val))
    diff = pas_total - ativo_total
    c4.metric("Check (Pas+PL − Ativo)", formatar_real(diff),
               delta="OK" if abs(diff) < 1 else "Divergência")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(data=[go.Pie(
            labels=["Ativo Circulante", "Ativo Não Circulante"],
            values=[ac, anc],
            marker=dict(colors=[NAVY, GOLD]),
            hole=0.45,
            textinfo="label+percent",
        )])
        fig.update_layout(height=350, title="Composição do Ativo",
                          showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(data=[go.Pie(
            labels=["Passivo Circulante", "Passivo Não Circulante", "Patrimônio Líquido"],
            values=[pc, pnc, pl_val],
            marker=dict(colors=[NAVY, BLUE, GOLD]),
            hole=0.45,
            textinfo="label+percent",
        )])
        fig.update_layout(height=350, title="Composição Passivo + PL",
                          showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Detalhamento por conta")
    bal_show = bal_df.copy()
    for m in meses_sel:
        bal_show[m] = bal_show[m].apply(lambda x: formatar_real(x))
    st.dataframe(bal_show, use_container_width=True, hide_index=True)

# ========== ABA 5: LIQUIDEZ & ENDIVIDAMENTO ==========
with tabs[4]:
    st.subheader("Indicadores de Liquidez e Endividamento")

    liq_im = serie_indicador("Liquidez Imediata", meses_sel)
    liq_cor = serie_indicador("Liquidez Corrente", meses_sel)
    liq_ger = serie_indicador("Liquidez Geral", meses_sel)
    end = serie_indicador("Grau de Endividamento", meses_sel)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=meses_sel, y=liq_cor, name="Liquidez Corrente",
                                  mode="lines+markers+text", line=dict(color=NAVY, width=3),
                                  text=[f"{v:.2f}" for v in liq_cor], textposition="top center"))
        fig.add_trace(go.Scatter(x=meses_sel, y=liq_ger, name="Liquidez Geral",
                                  mode="lines+markers+text", line=dict(color=BLUE, width=3),
                                  text=[f"{v:.2f}" for v in liq_ger], textposition="top center"))
        fig.add_trace(go.Scatter(x=meses_sel, y=liq_im, name="Liquidez Imediata",
                                  mode="lines+markers+text", line=dict(color=GOLD, width=3),
                                  text=[f"{v:.2f}" for v in liq_im], textposition="top center"))
        fig.add_hline(y=1.0, line_dash="dash", line_color=GREY, annotation_text="Referência 1,0")
        fig.update_layout(height=400, title="Indicadores de Liquidez",
                          legend=dict(orientation="h", y=-0.15),
                          margin=dict(l=20, r=20, t=50, b=20),
                          yaxis=dict(range=[0, max(filter(None, liq_cor+liq_ger+liq_im))*1.3]))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        end_pct = [v*100 if v else None for v in end]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=meses_sel, y=end_pct, marker_color=NAVY,
                              text=[f"{v:.2f}%" for v in end_pct], textposition="outside"))
        fig.update_layout(height=400, title="Grau de Endividamento (PC+PNC)/AT",
                          yaxis=dict(title="%"),
                          margin=dict(l=20, r=20, t=50, b=20),
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    ncg = serie_indicador("NCG", meses_sel)
    cdg = serie_indicador("CDG", meses_sel)
    st_caixa = [c-n if c and n else None for c, n in zip(cdg, ncg)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=meses_sel, y=ncg, name="NCG", marker_color=GOLD))
    fig.add_trace(go.Bar(x=meses_sel, y=cdg, name="CDG", marker_color=NAVY))
    fig.add_trace(go.Scatter(x=meses_sel, y=st_caixa, name="Saldo Tesouraria (CDG−NCG)",
                              mode="lines+markers", line=dict(color=GREEN, width=3)))
    fig.update_layout(barmode="group", height=380, title="NCG, CDG e Saldo de Tesouraria",
                      legend=dict(orientation="h", y=-0.15),
                      margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ========== ABA 6: CICLO FINANCEIRO ==========
with tabs[5]:
    st.subheader("Prazos e Ciclo Financeiro")

    pmr = serie_indicador("PMR (dias)", meses_sel)
    pmp = serie_indicador("PMP (dias)", meses_sel)
    pme = serie_indicador("PME (dias)", meses_sel)
    cop = serie_indicador("Ciclo Operacional (dias)", meses_sel)
    cf = serie_indicador("Ciclo Financeiro (dias)", meses_sel)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=meses_sel, y=pmr, name="PMR (Clientes)",
                              mode="lines+markers", line=dict(color=BLUE, width=2.5)))
    fig.add_trace(go.Scatter(x=meses_sel, y=pmp, name="PMP (Fornecedores)",
                              mode="lines+markers", line=dict(color=GOLD, width=2.5)))
    fig.add_trace(go.Scatter(x=meses_sel, y=pme, name="PME (Estoques)",
                              mode="lines+markers", line=dict(color=NAVY, width=2.5)))
    fig.add_trace(go.Scatter(x=meses_sel, y=cf, name="Ciclo Financeiro",
                              mode="lines+markers+text", line=dict(color=RED, width=3),
                              marker=dict(size=12),
                              text=[f"{v:.1f}" for v in cf], textposition="top center"))
    fig.update_layout(height=420, title="Prazos Médios e Ciclo Financeiro (dias)",
                      legend=dict(orientation="h", y=-0.15),
                      margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

    ciclo_df = pd.DataFrame({
        "Indicador": ["PMR (dias)", "PMP (dias)", "PME (dias)", "Ciclo Operacional", "Ciclo Financeiro"],
        **{m: [f"{pmr[i]:.1f}", f"{pmp[i]:.1f}", f"{pme[i]:.1f}", f"{cop[i]:.1f}", f"{cf[i]:.1f}"]
            for i, m in enumerate(meses_sel)},
    })
    st.dataframe(ciclo_df, use_container_width=True, hide_index=True)

    if idx_ant is not None:
        var_cf = cf[idx_ref] - cf[idx_ant]
        st.markdown(
            f"<div class='insight-box'><b>Insight:</b> Ciclo Financeiro de {mes_ref} = "
            f"<b>{cf[idx_ref]:.1f} dias</b> ({'+' if var_cf > 0 else ''}{var_cf:.1f} dias vs. {mes_ant}). "
            f"Quanto menor o ciclo, menor a necessidade de capital de giro.</div>",
            unsafe_allow_html=True,
        )

# ========== ABA 7: DRE COMPLETA ==========
with tabs[6]:
    st.subheader("DRE Completa — Período Selecionado")
    dre_show = dre_df.copy()
    for m in meses_sel:
        dre_show[m] = dre_show[m].apply(lambda x: formatar_real(x) if pd.notna(x) else "-")
    st.dataframe(dre_show[["Conta", "Bloco"] + meses_sel], use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Baixar DRE selecionada (CSV)",
        dre_df[["Conta", "Bloco"] + meses_sel].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"DRE_{'_'.join(meses_sel)}.csv",
        mime="text/csv",
    )
