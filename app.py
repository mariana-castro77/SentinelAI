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

# --- 4. TELA DE TERMO E PRIVACIDADE ---
if not st.session_state["termo_aceito"]:
    # Oculta elementos padrões para dar foco na tela de boas-vindas
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{visibility:hidden;}</style>", unsafe_allow_html=True)
    
    _, col_main, _ = st.columns([0.2, 0.6, 0.2])
    
    with col_main:
        # Carregando o robô com efeito de brilho e animação
        img_b64 = get_image_base64("robo.png")
        if img_b64:
            st.markdown(f'''
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{img_b64}" class="robo-animado" style="max-width: 250px;">
                </div>
            ''', unsafe_allow_html=True)
        
        # Container do Termo (LGPD)
        st.markdown('''
            <div class="hud-card">
                <h2 class="titulo-h" style="text-align:center;">TERMO DE CONFORMIDADE E PRIVACIDADE</h2>
                <p style="color:#eee; line-height:1.6; text-align:justify;">
                    Em conformidade estrita com a <b>Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018</b>, 
                    informamos que este ecossistema armazena cookies e processa telemetrias perimetrais críticas em tempo real. 
                    Ao avançar, você autoriza a coleta de logs e assume a responsabilidade pelo sigilo absoluto dos dados exibidos.
                </p>
            </div>
        ''', unsafe_allow_html=True)
        
        st.write("") # Espaçamento
        
        # Botões de Ação
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✓ ACEITAR E PROSSEGUIR", use_container_width=True):
                st.session_state["termo_aceito"] = True
                st.rerun()
        with c2:
            if st.button("✕ RECUSAR ACESSO", use_container_width=True):
                st.error("Acesso negado. Por favor, feche esta janela.")
                st.stop()
    
    st.stop()

# ==============================================================================
# 5. LÓGICA DE NAVEGAÇÃO: TELA DE LOGIN (COMPLETA)
# ==============================================================================

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: white;'>AUTENTICAÇÃO DE OPERADOR</h2>", unsafe_allow_html=True)
    
    st.warning("Para acessar o sistema, utilize um dos usuários e senhas abaixo:")
    
    # Tabela com todos os clientes solicitados
    dados_acesso = {
        "Perfil": ["Admin", "Analista", "Nubank", "iFood", "Mercado Livre", "Magazine Luiza", "Santander", "Vivo", "XP Investimentos"],
        "Usuário": ["admin", "analista", "nubank", "ifood", "mercadolivre", "magazine", "santander", "vivo", "xp"],
        "Senha": ["root99", "soc123", "nu2026", "ifood77", "ml2026", "magalu2026", "san99", "vivo2026", "xp2026"]
    }
    st.table(pd.DataFrame(dados_acesso))

    # Formulário de Login
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("ACESSAR SISTEMA", use_container_width=True)
        
        if submit:
            auth_data = {
                "admin": {"pwd": "root99", "perfil": "Administrador", "cliente": "Todos"},
                "analista": {"pwd": "soc123", "perfil": "Analista", "cliente": "Todos"},
                "nubank": {"pwd": "nu2026", "perfil": "Cliente", "cliente": "Nubank"},
                "ifood": {"pwd": "ifood77", "perfil": "Cliente", "cliente": "iFood"},
                "mercadolivre": {"pwd": "ml2026", "perfil": "Cliente", "cliente": "Mercado Livre"},
                "magazine": {"pwd": "magalu2026", "perfil": "Cliente", "cliente": "Magazine Luiza"},
                "santander": {"pwd": "san99", "perfil": "Cliente", "cliente": "Santander"},
                "vivo": {"pwd": "vivo2026", "perfil": "Cliente", "cliente": "Vivo"},
                "xp": {"pwd": "xp2026", "perfil": "Cliente", "cliente": "XP Investimentos"}
            }
            
            if usuario in auth_data and auth_data[usuario]["pwd"] == senha:
                st.session_state.update({
                    "autenticado": True,
                    "perfil_usuario": auth_data[usuario]["perfil"],
                    "cliente_usuario": auth_data[usuario]["cliente"]
                })
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
    
    st.stop()
