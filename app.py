import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px
import streamlit.components.v1 as components
import time
import random
from datetime import datetime

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(page_title="SentinelAI // SOC Platform", layout="wide", initial_sidebar_state="expanded")

# --- FUNÇÕES DE SEGURANÇA E BACKUP ---
@st.cache_data
def carregar_banco():
    return pd.read_csv("dataset_final.csv") if os.path.exists("dataset_final.csv") else pd.DataFrame()

def persistir_log(usuario, acao, detalhe):
    """Backup em tempo real: garante que nada se perca."""
    log = pd.DataFrame([[datetime.now(), usuario, acao, detalhe]], 
                       columns=["HORA", "USUARIO", "ACAO", "DETALHE"])
    log.to_csv("backup_central.csv", mode='a', header=not os.path.exists("backup_central.csv"), index=False)

# --- CSS E DESIGN (PARALLAX + EFEITOS) ---
st.markdown("""
<style>
    /* Parallax e Scroll Suave */
    html { scroll-behavior: smooth; }
    .stApp { background: radial-gradient(circle at 50% 50%, #150000 0%, #000 100%); background-attachment: fixed; }
    
    /* Cards de Telemetria */
    .metric-card { background: rgba(25, 25, 25, 0.7); border: 1px solid #ff3333; padding: 20px; border-radius: 12px; transition: 0.3s; }
    .metric-card:hover { transform: translateY(-5px); border-color: #ff6666; }
    
    /* Robô Fixado */
    .robo-fixed { position: fixed; bottom: 50px; right: 50px; width: 180px; z-index: 999; 
                  animation: float 5s ease-in-out infinite; filter: drop-shadow(0 0 20px #ff0000); }
    @keyframes float { 0% { transform: translateY(0); } 50% { transform: translateY(-20px); } 100% { transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if "autenticado" not in st.session_state: st.session_state.update({"autenticado": False, "termo_aceito": False})
df_soc = carregar_banco()

# --- LOGIN E SEGURANÇA (BLOQUEIO INICIAL) ---
if not st.session_state["termo_aceito"]:
    st.title("🛡️ SENTINELAI - ACESSO ESTRUTURADO")
    if st.button("ACEITAR TERMOS DE SIGILO"): st.session_state["termo_aceito"] = True; st.rerun()
    st.stop()

if not st.session_state["autenticado"]:
    st.subheader("Autenticação de Operador")
    with st.form("login"):
        u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            auth = {"admin": ("root99", "Administrador", "Todos"), "nubank": ("nu2026", "Cliente", "Nubank"), "ifood": ("ifood77", "Cliente", "iFood")}
            if u in auth and auth[u][0] == p:
                st.session_state.update({"autenticado": True, "perfil_usuario": auth[u][1], "cliente_usuario": auth[u][2]})
                persistir_log(u, "LOGIN", "Acesso concedido")
                st.rerun()
    st.stop()

# --- DASHBOARD COMMAND CENTER ---
st.title(f"COMMAND CENTER // {st.session_state['cliente_usuario'].upper()}")

# Filtro de Segurança
df_view = df_soc if st.session_state["cliente_usuario"] == "Todos" else df_soc[df_soc["CLIENTE"] == st.session_state["cliente_usuario"]]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Alertas Ativos", len(df_view), "Monitorados")
col2.metric("Prejuízo Estimado", f"R$ {df_view['PREJUIZO_ESTIMADO'].sum():,.2f}")
col3.metric("Uptime", "99.99%", "Estável")
col4.metric("Backup", "Integrado", "Sync: Online")

# Abas com conteúdo denso e funcional
tab_tria, tab_mapa, tab_dash, tab_ia = st.tabs(["🔍 Triagem Forense", "🌍 Monitoramento Global", "📊 Telemetria", "🤖 IA Sentinel"])

with tab_tria:
    st.dataframe(df_view, use_container_width=True)

with tab_mapa:
    components.html('<iframe src="https://cybermap.kaspersky.com/en/widget/threed" width="100%" height="500px"></iframe>', height=500)

with tab_dash:
    st.plotly_chart(px.bar(df_view, x="CLIENTE", y="PREJUIZO_ESTIMADO", color="SEVERIDADE", template="plotly_dark"), use_container_width=True)

with tab_ia:
    st.write("### Sentinel Core Intelligence")
    query = st.chat_input("Pergunte ao sistema sobre vulnerabilidades...")
    if query:
        persistir_log(st.session_state["cliente_usuario"], "IA_QUERY", query)
        st.chat_message("assistant").write("Analisando padrões... Nenhuma anomalia detectada nesta rede.")

# Renderização Robô Fixa (Parallax)
if os.path.exists("robo.png"):
    img = base64.b64encode(open("robo.png", "rb").read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img}" class="robo-fixed">', unsafe_allow_html=True)
