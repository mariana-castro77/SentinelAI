import streamlit as st
import pandas as pd
import os
import base64
import requests                # Necessário para as chamadas de IA (Gemini)
import plotly.express as px    # Necessário para os gráficos de telemetria
import streamlit.components.v1 as components # Necessário para o mapa e Spline
import time                    # Necessário para efeitos de carregamento
import datetime                # Necessário para logs e carimbos de data
import random                  # Útil para simulação de pacotes em tempo real
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

# ==============================================================================
# 4. LÓGICA DE NAVEGAÇÃO: TELA DE TERMO (LEI E COOKIES)
# ==============================================================================

if not st.session_state["termo_aceito"]:
    # Esconde sidebar e header para foco total na tela de boas-vindas
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([0.2, 3.6, 0.2])
    
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Carregando o robô com a classe CSS que definimos na Parte 1
        img_data = get_image_base64("robo.png")
        if img_data:
            st.markdown(f'''
                <div style="display: flex; justify-content: center; margin-bottom: 30px;">
                    <img src="data:image/png;base64,{img_data}" class="robo-animado">
                </div>
            ''', unsafe_allow_html=True)
        
        # Container do Termo (Lei LGPD e Cookies)
        st.markdown('''
            <div class="hud-card">
                <h2 class="titulo-h" style="text-align:center;">TERMO DE CONFORMIDADE E PRIVACIDADE</h2>
                <p style="color:#eee; font-size:1.1rem; line-height:1.6; text-align:justify;">
                    Em conformidade com a <b>Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018</b>, informamos que este 
                    ecossistema de monitoramento armazena cookies técnicos essenciais para a sessão e processa telemetrias de rede 
                    em tempo real para garantir a estabilidade do Command Center. 
                    <br><br>
                    Ao clicar no botão abaixo, você autoriza explicitamente a coleta de logs de auditoria e assume a 
                    responsabilidade pelo sigilo absoluto das informações corporativas exibidas.
                </p>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão de aceite
        if st.button("✓ ACEITAR TERMOS E PROSSEGUIR PARA O LOGIN", use_container_width=True):
            st.session_state["termo_aceito"] = True
            st.rerun() # Recarrega o app para passar para a próxima etapa

    st.stop() # Para a execução aqui se o termo não foi aceito
