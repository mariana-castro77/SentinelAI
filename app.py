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
# 5. LÓGICA DE NAVEGAÇÃO: PÁGINA DE LOGIN (CONTROLE DE PERFIS)
# ==============================================================================

if not st.session_state["autenticado"]:
    # Mantém o sidebar oculto na tela de login
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{visibility:hidden;}</style>", unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1, 1.6, 1])
    
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('''
            <div class="hud-card" style="text-align: center; margin-bottom: 20px;">
                <span style="color: #ff3333; font-weight:700; font-size:0.8rem; letter-spacing:2px;">SISTEMA DE IDENTIDADE SENTINELAI</span>
                <h2 class="titulo-h" style="margin-top:10px;">Autenticação de Operador</h2>
            </div>
        ''', unsafe_allow_html=True)
        
        # TABELA DE REFERÊNCIA PARA VOCÊ NÃO ESQUECER OS USUÁRIOS (Opcional - pode apagar depois)
        st.info("💡 **DICA DO SISTEMA:** Admin: `admin` / `root99` | Analista: `analista` / `soc123` | Nubank: `nubank_user` / `nu2026`")

        with st.form("form_login"):
            usuario = st.text_input("👤 Credencial de Acesso", placeholder="Digite seu usuário")
            senha = st.text_input("🔑 Assinatura Criptográfica", type="password", placeholder="••••••••")
            
            botao_login = st.form_submit_button("AUTENTICAR NO DASHBOARD", use_container_width=True)
            
            if botao_login:
                # 1. PERFIL: ADMINISTRADOR (ACESSO TOTAL)
                if usuario == "admin" and senha == "root99":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Administrador",
                        "cliente_usuario": "Todos"
                    })
                    st.rerun()
                
                # 2. PERFIL: ANALISTA (IP MASCARADO)
                elif usuario == "analista" and senha == "soc123":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Analista",
                        "cliente_usuario": "Todos"
                    })
                    st.rerun()

                # 3. PERFIL: CLIENTE - NUBANK
                elif usuario == "nubank_user" and senha == "nu2026":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Viewer Cliente",
                        "cliente_usuario": "Nubank"
                    })
                    st.rerun()

                # 4. PERFIL: CLIENTE - IFOOD
                elif usuario == "ifood_user" and senha == "ifood77":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Viewer Cliente",
                        "cliente_usuario": "iFood"
                    })
                    st.rerun()

                # 5. PERFIL: CLIENTE - MERCADO LIVRE
                elif usuario == "mercado_user" and senha == "ml2026":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Viewer Cliente",
                        "cliente_usuario": "Mercado Livre"
                    })
                    st.rerun()

                # 6. PERFIL: CLIENTE - SANTANDER
                elif usuario == "santander_user" and senha == "san99":
                    st.session_state.update({
                        "autenticado": True,
                        "perfil_usuario": "Viewer Cliente",
                        "cliente_usuario": "Santander"
                    })
                    st.rerun()

                else:
                    st.error("❌ Falha na autenticação. Verifique as chaves de acesso.")

    st.stop()
