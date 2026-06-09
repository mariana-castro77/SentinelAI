import streamlit as st
import pandas as pd
import os
import base64

# ==============================================================================
# 1. INICIALIZAÇÃO SEGURA DO ESTADO (Obrigatório vir antes de tudo)
# ==============================================================================
if "termo_aceito" not in st.session_state: st.session_state["termo_aceito"] = False
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "perfil_usuario" not in st.session_state: st.session_state["perfil_usuario"] = None

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(page_title="SentinelAI // Command Center", page_icon="🛡️", layout="wide")

# Função auxiliar para carregar o robô
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except: return None

# ==============================================================================
# 3. CSS GLOBAL E ANIMAÇÕES (Parallax + Robô Flutuante)
# ==============================================================================
st.markdown("""
<style>
    @keyframes floating { 0% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(3deg); } 100% { transform: translateY(0px) rotate(0deg); } }
    .robo-animado { width: 250px; animation: floating 4s ease-in-out infinite; filter: drop-shadow(0 0 20px rgba(255, 30, 30, 0.6)); }
    .stApp { background: radial-gradient(circle at center, #1a0505 0%, #000 100%); background-attachment: fixed; }
    .hud-card { background: rgba(10, 10, 10, 0.9); border: 1.5px solid #ff3333; padding: 2.5rem; border-radius: 15px; color: white; margin-top: -30px; }
    .titulo-h { font-family: 'Space Grotesk', sans-serif; color: #fff; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)
