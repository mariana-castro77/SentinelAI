import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px
import streamlit.components.v1 as components
import time

# ==============================================================================
# 1. CARREGAMENTO E CONFIGURAÇÃO (Obrigatório vir antes de tudo)
# ==============================================================================
st.set_page_config(page_title="SentinelAI // Command Center", page_icon="🛡️", layout="wide")

@st.cache_data
def carregar_dados():
    if os.path.exists("dataset_final.csv"):
        return pd.read_csv("dataset_final.csv")
    return pd.DataFrame(columns=["CLIENTE", "PREJUIZO_ESTIMADO", "SEVERIDADE", "IP"])

df_soc = carregar_dados()

def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except: return None

# Inicialização de Estado
if "termo_aceito" not in st.session_state: st.session_state["termo_aceito"] = False
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "perfil_usuario" not in st.session_state: st.session_state["perfil_usuario"] = None

# ==============================================================================
# 2. CSS GLOBAL E ANIMAÇÕES
# ==============================================================================
st.markdown("""
<style>
    @keyframes floating { 0% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(3deg); } 100% { transform: translateY(0px) rotate(0deg); } }
    .robo-animado { width: 250px; animation: floating 4s ease-in-out infinite; filter: drop-shadow(0 0 20px rgba(255, 30, 30, 0.6)); }
    .stApp { background: radial-gradient(circle at 50% 50%, #0f0505 0%, #000 100%); background-attachment: fixed; }
    .hud-card { background: rgba(10, 10, 10, 0.9); border: 1.5px solid #ff3333; padding: 2.5rem; border-radius: 15px; color: white; }
    .titulo-h { font-family: 'Space Grotesk', sans-serif; color: #fff; text-transform: uppercase; }
    .robo-lateral { position: fixed; bottom: 20px; right: 20px; width: 120px; animation: pulse 3s infinite; filter: drop-shadow(0 0 10px #ff3333); }
    @keyframes pulse { 0%, 100% { opacity: 0.8; transform: scale(1); } 50% { opacity: 1; transform: scale(1.05); } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. TELA DE TERMO E PRIVACIDADE
# ==============================================================================
if not st.session_state["termo_aceito"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{visibility:hidden;}</style>", unsafe_allow_html=True)
    _, col_main, _ = st.columns([0.2, 0.6, 0.2])
    with col_main:
        img_b64 = get_image_base64("robo.png")
        if img_b64:
            st.markdown(f'<div style="display: flex; justify-content: center; margin-bottom: 20px;"><img src="data:image/png;base64,{img_b64}" class="robo-animado"></div>', unsafe_allow_html=True)
        st.markdown('<div class="hud-card"><h2 class="titulo-h" style="text-align:center;">TERMO DE CONFORMIDADE</h2><p>Ao avançar, você autoriza a coleta de logs e assume a responsabilidade pelo sigilo absoluto.</p></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✓ ACEITAR"): st.session_state["termo_aceito"] = True; st.rerun()
        if c2.button("✕ RECUSAR"): st.stop()
    st.stop()

# ==============================================================================
# 4. TELA DE LOGIN
# ==============================================================================
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: white;'>AUTENTICAÇÃO DE OPERADOR</h2>", unsafe_allow_html=True)
    st.warning("Credenciais de Acesso:")
    st.table(pd.DataFrame({
        "Perfil": ["Admin", "Analista", "Nubank", "iFood", "M. Livre", "Magazine", "Santander", "Vivo", "XP"],
        "Usuário": ["admin", "analista", "nubank", "ifood", "mercadolivre", "magazine", "santander", "vivo", "xp"],
        "Senha": ["root99", "soc123", "nu2026", "ifood77", "ml2026", "magalu2026", "san99", "vivo2026", "xp2026"]
    }))
    with st.form("login_form"):
        u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            auth = {"admin": ("root99", "Administrador", "Todos"), "analista": ("soc123", "Analista", "Todos"), "nubank": ("nu2026", "Cliente", "Nubank"), "ifood": ("ifood77", "Cliente", "iFood"), "mercadolivre": ("ml2026", "Cliente", "Mercado Livre"), "magazine": ("magalu2026", "Cliente", "Magazine Luiza"), "santander": ("san99", "Cliente", "Santander"), "vivo": ("vivo2026", "Cliente", "Vivo"), "xp": ("xp2026", "Cliente", "XP Investimentos")}
            if u in auth and auth[u][0] == p:
                st.session_state.update({"autenticado": True, "perfil_usuario": auth[u][1], "cliente_usuario": auth[u][2]})
                st.rerun()
            else: st.error("Credenciais inválidas.")
    st.stop()

# ==============================================================================
# 5. DASHBOARD CENTRAL (O CÉREBRO)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 🛡️ OPERADOR: {st.session_state['perfil_usuario'].upper()}")
    st.markdown(f"**CLIENTE ATIVO:** {st.session_state['cliente_usuario']}")
    if st.button("LOGOUT SEGURO"): st.session_state.clear(); st.rerun()

df_view = df_soc if st.session_state["cliente_usuario"] == "Todos" else df_soc[df_soc["CLIENTE"] == st.session_state["cliente_usuario"]]
st.title("COMMAND CENTER // SENTINELAI")

tabs = st.tabs(["🔍 TRIAGEM", "🌍 MAPA", "📊 TELEMETRIA", "🤖 SENTINEL CORE"])
with tabs[0]:
    if st.session_state["perfil_usuario"] == "Analista" and "IP" in df_view.columns:
        df_m = df_view.copy(); df_m["IP"] = "HIDDEN_IP"; st.dataframe(df_m, use_container_width=True)
    else: st.dataframe(df_view, use_container_width=True)
with tabs[1]: components.html('<iframe src="https://cybermap.kaspersky.com/en/widget/threed" width="100%" height="500px"></iframe>', height=500)
with tabs[2]: st.plotly_chart(px.bar(df_view, x="CLIENTE", y="PREJUIZO_ESTIMADO", color="SEVERIDADE", template="plotly_dark"), use_container_width=True)
with tabs[3]: 
    if st.button("PROCESSAR INTELIGÊNCIA"): st.info("Auditoria concluída para: " + st.session_state["cliente_usuario"])

img_b64 = get_image_base64("robo.png")
if img_b64: st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="robo-lateral">', unsafe_allow_html=True)
