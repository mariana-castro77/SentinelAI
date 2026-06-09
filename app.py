import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import requests
import time
import os
import random

# ==============================================================================
# 1. CONFIGURAÇÃO ANCORADA DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="SentinelAI // Cyber Security Enterprise Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==============================================================================
# 2. SISTEMA DE DADOS (DATASET)
# ==============================================================================
@st.cache_data
def carregar_dados_sistema():
    caminho_arquivo = "dataset_final.csv" if os.path.exists("dataset_final.csv") else "dataset_mysql.csv"
    if os.path.exists(caminho_arquivo):
        df = pd.read_csv(caminho_arquivo)
    else:
        dados_reserva = {
            "ID": range(1, 6),
            "DATA": ["2026-03-11", "2026-03-27", "2026-04-05", "2026-04-03", "2026-03-07"],
            "TIPO INCIDENTE": ["ataque", "lentidão", "ataque", "lentidão", "lentidão"],
            "SEVERIDADE": ["crítica", "crítica", "crítica", "média", "baixa"],
            "TEMPO RESOLUÇÃO": [24, 24, 78, 58, 49],
            "ORIGEM": ["aplicação", "rede", "servidor", "banco de dados", "aplicação"],
            "STATUS": ["pendente", "pendente", "resolvido", "pendente", "resolvido"],
            "PAIS_ATAQUE": ["China", "Interno", "Alemanha", "Rússia", "Estados Unidos"],
            "PREJUIZO_ESTIMADO": [13016, 18187, 15719, 4486, 1173],
            "CLIENTE": ["Nubank", "Santander", "Mercado Livre", "XP Investimentos", "iFood"],
            "IP_SUSPEITO": ["129.211.51.50", "Nenhum", "202.202.156.53", "185.220.101.5", "Nenhum"],
            "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Não", "Não"],
            "RISCO_FINANCEIRO": ["médio", "alto", "alto", "médio", "baixo"]
        }
        df = pd.DataFrame(dados_reserva)
        
    df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str).str.lower()
    df["ORIGEM"] = df["ORIGEM"].astype(str).str.lower()
    df["STATUS"] = df["STATUS"].astype(str).str.lower()
    df["CLIENTE"] = df["CLIENTE"].astype(str)
    return df

df_soc = carregar_dados_sistema()

# ==============================================================================
# 3. ESTILIZAÇÃO CSS: PARALLAX SUAVE + ESCOPO EXPANDIDO (IGUAL À REFERÊNCIA)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* Scroll Suave nativo no Navegador */
html {
    scroll-behavior: smooth;
}

/* Background Dinâmico (Efeito Parallax reativo ao focar/carregar a página) */
.stApp {
    background: radial-gradient(circle at center, rgba(125,10,10,1) 0%, rgba(18,3,3,1) 60%, rgba(0,0,0,1) 100%) !important;
    background-attachment: fixed !important;
    background-size: 100% 100%;
    animation: parallaxEfect 12s ease-in-out infinite alternate;
}

@keyframes parallaxEfect {
    0% { background-size: 100% 100%; background-position: center; }
    100% { background-size: 112% 112%; background-position: top center; }
}

/* Força abas a serem transparentes para não quebrar o tema */
#tabs-bgbnd-tab-0, #tabs-bgbnd-tab-1, #tabs-bgbnd-tab-2, #tabs-bgbnd-tab-3 {
    background: transparent !important;
}

/* Card customizado: laterais largas e topo jogado para cima */
.hud-container-soc {
    background: rgba(6, 1, 1, 0.93);
    border: 1.8px solid rgba(255, 45, 45, 0.65);
    border-radius: 16px;
    padding: 3.5rem 5rem !important; /* Laterais bem abertas para o texto respirar */
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.98), 0 0 60px rgba(255, 45, 45, 0.18);
    margin-top: -55px !important; /* Puxa o card agressivamente para o topo */
}

.titulo-holografico {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# Estados globais de persistência
if "termo_aceito" not in st.session_state:
    st.session_state["termo_aceito"] = False
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["perfil_usuario"] = None
    st.session_state["cliente_usuario"] = None

# ==============================================================================
# TELA 1: COMPONENTE DO TERMO COM EMED DO SPLINE 3D
# ==============================================================================
if not st.session_state["termo_aceito"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    # Colunas laterais reduzidas (0.1) para garantir o máximo de largura ao centro
    c_left, c_main, c_right = st.columns([0.1, 3.8, 0.1])
    with c_main:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Início do Bloco Estrutural
        st.markdown('<div class="hud-container-soc">', unsafe_allow_html=True)
        
        # Injeção controlada do visualizador Spline 3D com fallback seguro
        spline_html_code = """
        <style>body { margin: 0; padding: 0; overflow: hidden; background: transparent; }</style>
        <script type="module" src="https://unpkg.com/@splinetool/viewer@1.12.97/build/spline-viewer.js"></script>
        <spline-viewer url="https://prod.spline.design/6Wq1Q7YAncaRPOuX/scene.splinecode"></spline-viewer>
        """
        components.html(spline_html_code, height=220, scrolling=False)
        
        st.markdown("""
            <h2 class="titulo-holografico" style="font-size: 1.95rem; text-align: center; margin-bottom: 1.8rem; color: #ffffff;">
                TERMO DE CONFORMIDADE E PRIVACIDADE DE DADOS
            </h2>
            <p style="color: #f1f5f9; font-size: 1.05rem; line-height: 1.75; text-align: justify; margin-bottom: 2rem; font-family: 'Plus Jakarta Sans', sans-serif;">
                Em conformidade estrita com a <b>Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018</b>, informamos que este ecossistema corporativo armazena cookies temporários e processa telemetrias perimetrais críticas em tempo real para garantir a estabilidade das aplicações. Ao avançar, você autoriza explicitamente a coleta de logs de auditoria e assume a responsabilidade de manter o sigilo absoluto sobre quaisquer dados e faturamentos de clientes exibidos neste centro de comando.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de Ação
        st.markdown("<br>", unsafe_allow_html=True)
        col_ok, col_fail = st.columns(2)
        with col_ok:
            if st.button("✓ ACEITAR E PROSSEGUIR", use_container_width=True, type="primary"):
                st.session_state["termo_aceito"] = True
                st.toast("Termo aceito!", icon="🔓")
                time.sleep(0.3)
                st.rerun()
        with col_fail:
            if st.button("✕ RECUSAR ACESSO", use_container_width=True):
                st.error("Terminal bloqueado preventivamente.")
                st.stop()
                
    st.stop()

# ==============================================================================
# TELA 2: AUTENTICAÇÃO / LOGIN
# ==============================================================================
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_l1, c_login, c_l2 = st.columns([1, 1.8, 1])
    with c_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="hud-container-soc" style="text-align: center; margin-bottom: 1.5rem; padding: 1.5rem !important;">
            <span style="color: #ff3333; font-weight:700; font-size:0.75rem; letter-spacing:3px;">SENTINELAI SECURITY ENTERPRISE</span>
            <h2 class="titulo-holografico" style="margin-top:5px; font-size:1.7rem;">Autenticação de Perfil</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <table style="width:100%; font-size:11px; background:rgba(10,2,2,0.7); border:1px solid rgba(255,51,51,0.3); color:#cbd5e1; margin-bottom:15px; border-collapse:collapse; text-align:left;">
            <thead>
                <tr style="border-bottom:1px solid rgba(255,51,51,0.4); color:#fff; background: rgba(239,68,68,0.2);">
                    <th style="padding:6px;">User</th><th style="padding:6px;">Password</th><th style="padding:6px;">Perfil</th><th style="padding:6px;">Escopo</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">admin</td><td style="padding:5px;">root99</td><td style="padding:5px;">Administrador</td><td style="padding:5px;">Global</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">analista</td><td style="padding:5px;">soc123</td><td style="padding:5px;">Analista SOC</td><td style="padding:5px;">Global</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">nubank_view</td><td style="padding:5px;">nu2026</td><td style="padding:5px;">Viewer</td><td style="padding:5px; color:#ff7733;">Nubank</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">ifood_view</td><td style="padding:5px;">ifood77</td><td style="padding:5px;">Viewer</td><td style="padding:5px; color:#ff7733;">iFood</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        with st.form("form_login_sistema"):
            usuario = st.text_input("Credencial", placeholder="Ex: admin")
            senha = st.text_input("Assinatura", type="password", placeholder="••••••••")
            if st.form_submit_button("AUTENTICAR NO DASHBOARD"):
                if usuario == "admin" and senha == "root99":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Administrador"
                    st.rerun()
                elif usuario == "analista" and senha == "soc123":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Analista"
                    st.rerun()
                elif usuario == "nubank_view" and senha == "nu2026":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Viewer"
                    st.session_state["cliente_usuario"] = "Nubank"
                    st.rerun()
                elif usuario == "ifood_view" and senha == "ifood77":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Viewer"
                    st.session_state["cliente_usuario"] = "iFood"
                    st.rerun()
                else:
                    st.error("Chaves inválidas.")
    st.stop()

# ==============================================================================
# TELA 3: PAINEL PRINCIPAL (SIDEBAR E ABAS)
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0;">
        <h2 class="titulo-holografico" style="font-size:1.6rem; margin:0;">Sentinel<span style="color:#ff3333;">AI</span></h2>
        <small style="color:#ff3333; font-weight:700;">{st.session_state['perfil_usuario'].upper()} MODE</small>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state["perfil_usuario"] == "Viewer":
        df_soc = df_soc[df_soc["CLIENTE"].str.lower() == st.session_state["cliente_usuario"].lower()]
        
    if st.button("🚪 LOGOUT"):
        st.session_state["autenticado"] = False
        st.session_state["perfil_usuario"] = None
        st.session_state["cliente_usuario"] = None
        st.rerun()

st.markdown("""
<div class="hud-container-soc" style="padding: 1.2rem !important; margin-bottom: 1.5rem; background: linear-gradient(90deg, rgba(239,68,68,0.2) 0%, rgba(0,0,0,0) 100%); border-radius:8px; margin-top: 0px !important;">
    <h1 class="titulo-holografico" style="margin: 0; font-size: 1.8rem;">Cyber Command Center Live Dashboard</h1>
</div>
""", unsafe_allow_html=True)

tab_analise, tab_mapa, tab_bi, tab_ia = st.tabs([
    "🔍 TRIAGEM FORENSE", "🌍 GLOBO LIVE KASPERSKY", "📊 TELEMETRIA", "🤖 ASSISTENTE COGNITIVO"
])

# ABA 1: TRIAGEM FORENSE
with tab_analise:
    st.markdown("### Motores de Triagem")
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        tipo_sel = st.selectbox("Tipo de Incidente", sorted(df_soc["TIPO INCIDENTE"].unique()))
    with c_f2:
        origem_sel = st.selectbox("Origem Asset", sorted(df_soc["ORIGEM"].unique()))
    with c_f3:
        lista_c = [st.session_state["cliente_usuario"]] if st.session_state["perfil_usuario"] == "Viewer" else sorted(df_soc["CLIENTE"].unique())
        cliente_sel = st.selectbox("Cliente", lista_c)

    if st.button("🚀 DISPARAR INVESTIGAÇÃO", use_container_width=True):
        res = df_soc[(df_soc["TIPO INCIDENTE"] == tipo_sel) & (df_soc["ORIGEM"] == origem_sel) & (df_soc["CLIENTE"] == cliente_sel)]
        match = res.iloc[0] if not res.empty else df_soc.iloc[0]

        st.markdown("---")
        st.markdown(f"<div style='background:rgba(239,68,68,0.2); border:1px solid #ff3333; padding:12px; border-radius:6px; color:#fff;'><b>🔴 Alerta: Severidade {match['SEVERIDADE'].upper()}</b></div>", unsafe_allow_html=True)
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Risco Financeiro", str(match['RISCO_FINANCEIRO']).upper())
        k2.metric("Prejuízo Estimado", f"R$ {match['PREJUIZO_ESTIMADO']:,.2f}")
        k3.metric("Tempo Resolução", f"{match['TEMPO RESOLUÇÃO']} min")

# ABA 2: GLOBO 3D KASPERSKY
with tab_mapa:
    st.markdown("### Monitor Global de Ameaças")
    kaspersky_globe_html = """
    <iframe src="https://cybermap.kaspersky.com/en/widget/threed" width="100%" height="550px" frameborder="0"></iframe>
    """
    components.html(kaspersky_globe_html, height=560)

# ABA 3: TELEMETRIA
with tab_bi:
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        fig1 = px.pie(df_soc, names="RISCO_FINANCEIRO", title="Distribuição de Risco", color_discrete_sequence=["#ff3333", "#ff7733"])
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig1, use_container_width=True)
    with c_g2:
        fig2 = px.bar(df_soc, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="Prejuízo por Carteira", color_discrete_sequence=["#ff3333"])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig2, use_container_width=True)

# ABA 4: ASSISTENTE COGNITIVO VIA API
with tab_ia:
    st.markdown("### Assistente Cognitivo SentinelCore")
    if "messages_v4" not in st.session_state:
        st.session_state["messages_v4"] = [{"role": "model", "content": "Sistema pronto para auditoria."}]

    for msg in st.session_state["messages_v4"]:
        st.write(f"**{msg['role'].upper()}:** {msg['content']}")

    with st.form("chat_v4", clear_on_submit=True):
        user_in = st.text_input("Prompt de auditoria:")
        if st.form_submit_button("ENVIAR"):
            st.session_state["messages_v4"].append({"role": "user", "content": user_in})
            if not GEMINI_API_KEY:
                ans = "⚠️ Chave de API indisponível."
            else:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                try:
                    r = requests.post(url, json={"contents": [{"parts": [{"text": user_in}]}]}, timeout=10)
                    ans = r.json()["candidates"][0]["content"]["parts"][0]["text"] if r.status_code == 200 else "Erro de conexão."
                except:
                    ans = "Timeout de resposta."
            st.session_state["messages_v4"].append({"role": "model", "content": ans})
            st.rerun()
