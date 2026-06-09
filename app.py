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
# 1. CONFIGURAÇÃO AVANÇADA DA PLATAFORMA DE SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="SentinelAI // Enterprise Cyber Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chave de contingência para o modelo cognitivo via Secrets do Streamlit
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA")

# ==============================================================================
# 2. CARREGAMENTO E ENRIQUECIMENTO ESTRUTURAL DO DATASET REAL (CSV)
# ==============================================================================
@st.cache_data
def carregar_dados_sistema():
    # Tenta ler o arquivo real fornecido pelo usuário
    caminho_arquivo = "dataset_final.csv" if os.path.exists("dataset_final.csv") else "dataset_mysql.csv"
    
    if os.path.exists(caminho_arquivo):
        df = pd.read_csv(caminho_arquivo)
    else:
        # Fallback de segurança com dados estruturados caso o arquivo suma no servidor
        dados_reserva = {
            "ID": range(1, 6),
            "DATA": ["2026-03-11", "2026-03-27", "2026-04-05", "2026-04-03", "2026-03-07"],
            "TIPO INCIDENTE": ["Ataque", "Lentidão", "Ataque", "Lentidão", "Lentidão"],
            "SEVERIDADE": ["Crítica", "Crítica", "Crítica", "Média", "Baixa"],
            "TEMPO RESOLUÇÃO": [24, 24, 78, 58, 49],
            "ORIGEM": ["aplicação", "aplicação", "servidor", "banco de dados", "aplicação"],
            "STATUS": ["Pendente", "Pendente", "Resolvido", "Pendente", "Resolvido"],
            "PAIS_ATAQUE": ["China", "Interno", "Alemanha", "Rússia", "Estados Unidos"],
            "PREJUIZO_ESTIMADO": [13016, 18187, 15719, 4486, 1173],
            "RECEITA_CLIENTE": [88516, 55707, 78030, 92356, 66453],
            "CLIENTE": ["Nubank", "Santander", "Mercado Livre", "XP Investimentos", "iFood"],
            "NIVEL_AMEACA": ["crítico", "crítico", "crítico", "médio", "baixo"],
            "IP_SUSPEITO": ["129.211.51.50", "Nenhum", "202.202.156.53", "185.220.101.5", "Nenhum"],
            "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Não", "Não"],
            "RISCO_FINANCEIRO": ["Alto", "Crítico", "Alto", "Médio", "Baixo"]
        }
        df = pd.DataFrame(dados_reserva)
        
    # Padronização e limpeza estrita para evitar quebras visuais na apresentação
    df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str).str.title()
    df["SEVERIDADE"] = df["SEVERIDADE"].astype(str).str.title()
    df["STATUS"] = df["STATUS"].astype(str).str.title()
    df["CLIENTE"] = df["CLIENTE"].astype(str)
    df["PAIS_ATAQUE"] = df["PAIS_ATAQUE"].astype(str)
    
    # Adicionando campos estratégicos ausentes para enriquecimento de IA e Auditoria
    if "RISCO_FINANCEIRO" not in df.columns:
        df["RISCO_FINANCEIRO"] = df["SEVERIDADE"].map({"Crítica": "CRÍTICO", "Média": "MÉDIO", "Baixa": "BAIXO"})
    
    return df

df_soc = carregar_dados_sistema()

# Dicionários Dinâmicos de Playbooks de Resposta C-Level (Para enriquecer os detalhes técnicos)
MAPPING_SOLUCOES = {
    "Ataque": {
        "solucao": "Implementação imediata de borda via Web Application Firewall (WAF) corporativo e mitigação Anycast de pacotes volumétricos volumosos.",
        "feito": "O tráfego anômalo foi desviado para sandboxes de mitigação ativas, aplicando regras de drop imediato para assinaturas de pacotes TCP/UDP suspeitas.",
        "automatico": "A engine de automação SOC isolou o IP no Security Group da infraestrutura de nuvem afetada e escalou o chamado de severidade 1."
    },
    "Lentidão": {
        "solucao": "Escalonamento horizontal automatizado dos clusters de containers, otimização de queries de banco de dados e ativação de cache em memória.",
        "feito": "Foi realizada a purga de conexões zumbis nos pools de banco de dados e redistribuição de carga através de load balancers globais.",
        "automatico": "O microsserviço afetado recebeu alocação emergencial de memória física e recursos de CPU pelo orquestrador de orquestração automatizada."
    }
}

# ==============================================================================
# 3. INTERFACE VISUAL AVANÇADA, PARALLAX EXTREMO E ESTILIZAÇÃO NEON
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

/* --- INTENSIFICAÇÃO RADICAL DO EFEITO PARALLAX NO SCROLL --- */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}

.stApp {
    background-image: 
        linear-gradient(180deg, rgba(21, 5, 5, 0.85) 0%, rgba(5, 7, 10, 0.95) 50%, rgba(0, 0, 0, 1) 100%),
        url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1920&auto=format&fit=crop');
    background-attachment: fixed;
    background-size: cover;
    background-position: center top;
    transition: background-position 0.1s ease-out;
}

/* Customização Avançada das Scrollbars */
::-webkit-scrollbar { width: 10px; background: #020406; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #ff3333 0%, #7f0000 100%); border-radius: 5px; }

/* Envoltórios de Painéis Corporativos (Enterprise HUD Cards) */
.hud-container-soc {
    background: rgba(6, 10, 18, 0.9);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 12px;
    padding: 1.8rem;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.8), inset 0 0 20px rgba(239, 68, 68, 0.05);
    margin-bottom: 1.5rem;
}

.metric-box-soc {
    background: rgba(3, 5, 8, 0.85);
    border-left: 4px solid #ff3333;
    border-radius: 0 8px 8px 0;
    padding: 1.2rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.4);
}

.titulo-holografico {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    background: linear-gradient(90deg, #ffffff 0%, #ff6666 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

/* Tabs Estilizadas para Apresentação C-Level */
.stTabs [data-baseweb="tab-list"] {
    background: #04070c !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    padding: 8px !important;
    border-radius: 10px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, rgba(239, 68, 68, 0.25) 0%, rgba(239, 68, 68, 0.05) 100%) !important;
    color: #ff3333 !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #ff3333 !important;
}

/* Caixas do Chatbot de Cibersegurança */
.chat-bubble-operator {
    background: rgba(255, 119, 51, 0.05);
    border: 1px solid rgba(255, 119, 51, 0.2);
    border-left: 4px solid #ff7733;
    padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;
}
.chat-bubble-core {
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-left: 4px solid #ff3333;
    padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. CONTROLE DE ACESSO E CONFORMIDADE DE DADOS (LGPD/AUDITORIA)
# ==============================================================================
if "termo_aceito" not in st.session_state:
    st.session_state["termo_aceito"] = False

if not st.session_state["termo_aceito"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    c_c1, c_center, c_c2 = st.columns([1, 1.8, 1])
    with c_center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="hud-container-soc" style="text-align: center; border: 2px solid #ff3333;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🛡️</div>
            <h2 class="titulo-holografico" style="font-size: 1.6rem;">TERMO DE CONFORMIDADE E SEGURANÇA DA INFORMAÇÃO</h2>
            <p style="color: #8a99ad; font-size: 0.88rem; line-height: 1.6; text-align: justify; margin: 1.5rem 0;">
                O painel a seguir manipula telemetrias críticas corporativas, logs perimetrais de borda e análises de impacto financeiro em tempo real. Em conformidade estrita com as regulamentações da LGPD e políticas corporativas, garanta a confidencialidade durante a exibição desta seção de inteligência.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✕ RECUSAR ACESSO", use_container_width=True):
                st.error("Terminal Bloqueado.")
        with col_btn2:
            if st.button("✓ AUTORIZAR E INGRESSAR", use_container_width=True):
                st.session_state["termo_aceito"] = True
                st.rerun()
    st.stop()

# SIDEBAR CORPORATIVA DE CONTROLE
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:1.2rem 0;'><h2 class='titulo-holografico' style='font-size:1.8rem; margin:0;'>Sentinel<span style='color:#ff3333;'>AI</span></h2><small style='color:#4f5e71; letter-spacing:1px;'>COMMAND SHELL v4.9</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 0.9rem;'>
        <p style='color: #ff3333; font-size: 0.65rem; margin:0; font-weight:700; letter-spacing:1px;'>OPERADOR DE RESPOSTA ATIVO</p>
        <p style='color: #ffffff; font-weight: 700; margin: 0 0 0.4rem 0; font-size: 0.95rem;'>@PRO_ANALIST_SOC</p>
        <span style="color:#10b981; font-size:0.7rem; font-weight:600;">● CONEXÃO CRIPTOGRAFADA TLS 1.3</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small style='color:#4f5e71;'>CONTROLES GLOBAIS DE SESSÃO</small>", unsafe_allow_html=True)
    if st.button("🚪 ENCERRAR TERMINAL", use_container_width=True):
        st.session_state["termo_aceito"] = False
        st.rerun()

# ==============================================================================
# 5. CABEÇALHO DO DASHBOARD PRINCIPAL
# ==============================================================================
st.markdown("""
<div class="hud-container-soc" style="background: linear-gradient(90deg, rgba(239,68,68,0.08) 0%, rgba(0,0,0,0) 100%); margin-bottom: 1.8rem; padding: 1.5rem;">
    <p style="color: #ff3333; font-size: 0.7rem; font-weight: 700; letter-spacing: 3px; margin:0;">CENTRAL INTEGRADA DE RESPOSTA INCIDENTES</p>
    <h1 class="titulo-holografico" style="margin: 0; font-size: 2.3rem;">Painel de Inteligência de Ameaças Globais</h1>
</div>
""", unsafe_allow_html=True)

# Métricas C-Level de Auto-Impacto
t_logs = len(df_soc)
t_financeiro = df_soc["PREJUIZO_ESTIMADO"].sum()
t_bloqueios = len(df_soc[df_soc["BLOQUEADO_AUTOMATICAMENTE"] == "Sim"])

m_c1, m_c2, m_c3 = st.columns(3)
with m_c1:
    st.markdown(f"<div class='metric-box-soc'><small style='color:#8a99ad; font-size:0.75rem; letter-spacing:1px;'>TOTAL LOGS PARALELOS</small><br><b style='color:#fff; font-size:1.8rem; font-family:\"Space Grotesk\";'>{t_logs:,} Eventos</b></div>", unsafe_allow_html=True)
with m_c2:
    st.markdown(f"<div class='metric-box-soc' style='border-left-color:#10b981;'><small style='color:#8a99ad; font-size:0.75rem; letter-spacing:1px;'>PREJUÍZO CORPORATIVO MITIGADO</small><br><b style='color:#10b981; font-size:1.8rem; font-family:\"Space Grotesk\";'>R$ {t_financeiro:,.2f}</b></div>", unsafe_allow_html=True)
with m_c3:
    st.markdown(f"<div class='metric-box-soc' style='border-left-color:#ffaa00;'><small style='color:#8a99ad; font-size:0.75rem; letter-spacing:1px;'>GATILHOS IPS AUTOMATIZADOS</small><br><b style='color:#ffaa00; font-size:1.8rem; font-family:\"Space Grotesk\";'>{t_bloqueios} Regras Ativas</b></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navegação Estrutural das Abas
tab_analise, tab_mapa, tab_bi, tab_ia = st.tabs([
    "🔍 TRIAGEM E ANÁLISE FORENSE", 
    "🌍 MAPA AO VIVO DO KASPERSKY CYBERTHREAT", 
    "📊 TELEMETRIA CORPORATIVA", 
    "🤖 AUDITORIA COGNITIVA CORE (IA)"
])

# ==============================================================================
# ABA 1: PAINEL DE ANÁLISE DETALHADO (OS 11 REQUISITOS EXPLICITADOS)
# ==============================================================================
with tab_analise:
    st.markdown("### Motores de Triagem Avançada")
    st.caption("Filtre as telemetrias operacionais para isolar as assinaturas de riscos no cluster corporativo.")
    
    # Grid de Filtros Ricos em Detalhes
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        tipo_sel = st.selectbox("Tipo de Incidente (Vetor)", sorted(df_soc["TIPO INCIDENTE"].unique()))
    with f_col2:
        cliente_sel = st.selectbox("Cliente Corporativo Afetado", sorted(df_soc["CLIENTE"].unique()))
    with f_col3:
        status_sel = st.selectbox("Status Operacional Atual", sorted(df_soc["STATUS"].unique()))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mecanismo Condicional Estrito por Estado de Sessão
    key_scan = f"scan_exec_{tipo_sel}_{cliente_sel}"
    if key_scan not in st.session_state:
        st.session_state[key_scan] = False
        
    if st.button("⚡ INICIAR TRATAMENTO DE ASSINATURA FORENSE", use_container_width=True):
        barra_scan = st.progress(0)
        for p in range(100):
            time.sleep(0.006)
            barra_scan.progress(p + 1)
        st.session_state[key_scan] = True
        st.toast("Rastreamento e decodificação estrutural finalizada!", icon="🛡️")

    # Renderização Rica de Dados Condicional (Só renderiza tudo após o Start)
    if st.session_state[key_scan]:
        # Localização do dado real ou geração inteligente estruturada
        dados_filtrados = df_soc[(df_soc["TIPO INCIDENTE"] == tipo_sel) & (df_soc["CLIENTE"] == cliente_sel)]
        if not dados_filtrados.empty:
            match_row = dados_filtrados.iloc[0]
        else:
            match_row = df_soc[df_soc["TIPO INCIDENTE"] == tipo_sel].iloc[0] if not df_soc[df_soc["TIPO INCIDENTE"] == tipo_sel].empty else df_soc.iloc[0]

        # Puxa resoluções dinâmicas estruturadas com base no tipo real para enriquecer os detalhes
        tipo_chave = "Ataque" if "ataque" in match_row["TIPO INCIDENTE"].lower() else "Lentidão"
        info_playbook = MAPPING_SOLUCOES[tipo_chave]

        st.markdown("---")
        st.markdown("<h3 style='color:#ff3333; font-family:\"Space Grotesk\";'>📋 Dossiê Forense de Evento de Segurança</h3>", unsafe_allow_html=True)
        
        # Bloco Inicial: Os 5 Parâmetros de Entrada / Identificação Básica
        c_p1, c_p2, c_p3, c_p4, c_p5 = st.columns(5)
        with c_p1:
            st.markdown(f"<div style='background:#050911; padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);'><small style='color:#8a99ad;'>TIPO INCIDENTE</small><br><b>{match_row['TIPO INCIDENTE']}</b></div>", unsafe_allow_html=True)
        with c_p2:
            st.markdown(f"<div style='background:#050911; padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);'><small style='color:#8a99ad;'>ORIGEM LOCAL</small><br><b>{match_row['ORIGEM'].upper()}</b></div>", unsafe_allow_html=True)
        with c_p3:
            st.markdown(f"<div style='background:#050911; padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);'><small style='color:#8a99ad;'>CLIENTE AFETADO</small><br><b style='color:#ff7733;'>{cliente_sel}</b></div>", unsafe_allow_html=True)
        with c_p4:
            st.markdown(f"<div style='background:#050911; padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);'><small style='color:#8a99ad;'>STATUS TRIAGEM</small><br><b style='color:#ff3333;'>{match_row['STATUS']}</b></div>", unsafe_allow_html=True)
        with c_p5:
            st.markdown(f"<div style='background:#050911; padding:10px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);'><small style='color:#8a99ad;'>TEMPO DE RESOLUÇÃO</small><br><b>{match_row['TEMPO RESOLUÇÃO']} min</b></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Bloco de Risco e Rastreamento Pós-Análise (Próximos Itens do Requisito)
        c_r1, c_r2, c_r3 = st.columns(3)
        with c_r1:
            st.markdown(f"""
            <div class="hud-container-soc" style="border-left: 4px solid #ff3333; margin-bottom:0;">
                <small style="color:#8a99ad; font-size:0.75rem;">IP SUSPEITO RASTREADO</small>
                <h3 style="margin:5px 0; font-family:monospace; color:#ff3333; font-size:1.4rem;">{match_row['IP_SUSPEITO']}</h3>
                <small style="color:#4f5e71;">Geolocalização Identificada: {match_row['PAIS_ATAQUE']}</small>
            </div>
            """, unsafe_allow_html=True)
        with c_r2:
            st.markdown(f"""
            <div class="hud-container-soc" style="border-left: 4px solid #ffaa00; margin-bottom:0;">
                <small style="color:#8a99ad; font-size:0.75rem;">RISCO FINANCEIRO ESTIMADO</small>
                <h3 style="margin:5px 0; font-family:'Space Grotesk'; color:#ffaa00; font-size:1.4rem;">{match_row['RISCO_FINANCEIRO'].upper()}</h3>
                <small style="color:#4f5e71;">Impacto nas Camadas de Faturamento</small>
            </div>
            """, unsafe_allow_html=True)
        with c_r3:
            st.markdown(f"""
            <div class="hud-container-soc" style="border-left: 4px solid #10b981; margin-bottom:0;">
                <small style="color:#8a99ad; font-size:0.75rem;">PREJUÍZO PATRIMONIAL CONSTATADO</small>
                <h3 style="margin:5px 0; font-family:'Space Grotesk'; color:#10b981; font-size:1.4rem;">R$ {match_row['PREJUIZO_ESTIMADO']:,.2f}</h3>
                <small style="color:#4f5e71;">Valores Contidos via Resposta Rápida</small>
            </div>
            """, unsafe_allow_html=True)

        # Planos Detalhados de Remediação Estratégica (Itens finais exigidos)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🛠️ Plano Preventivo e Ações Corretivas SOC Engine")
        
        st.markdown(f"**O que foi feito ou será feito para solucionar esse problema estrutural:**")
        st.info(match_row.get("O_QUE_FOI_FEITO", info_playbook["feito"]))
        
        st.markdown(f"**Solução de melhora de engenharia para mitigar novas ocorrências perimetrais:**")
        st.success(match_row.get("SOLUCAO_MELHORA", info_playbook["solucao"]))
        
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.07); border: 1px solid #10b981; padding: 15px; border-radius: 8px;">
            <span style="color:#10b981; font-weight:bold; font-size:0.85rem; letter-spacing:1px;">🛡️ RESPOSTA AUTOMÁTICA AUTOMATIZADA:</span><br>
            <p style="margin:5px 0 0 0; font-size:0.9rem; color:#e2e8f0;">{match_row.get('BLOQUEADO_AUTOMATICAMENTE', info_playbook['automatico'])} - Vetores de tráfego nocivos bloqueados nas camadas perimetrais do Firewall de Borda de maneira autônoma.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("<p style='color:#4f5e71; text-align:center; padding:5rem;'>Aguardando o comando de disparo do analista para processar e estruturar a telemetria forense do incidente.</p>", unsafe_allow_html=True)

# ==============================================================================
# ABA 2: GLOBO 3D MODELO KASPERSKY COM FLUXO E VETORES DIRECIONADOS
# ==============================================================================
with tab_mapa:
    st.markdown("### Mapa ao vivo do Kaspersky Cyberthreat")
    st.caption("Projeção tridimensional interativa mostrando a origem dos pacotes maliciosos contra o datacenter de operação central.")

    # Mapeando os dados reais do CSV para alimentar as coordenadas fictícias do Three.js
    lista_incidentes_reais = []
    for _, linha in df_soc.iterrows():
        if str(linha["PAIS_ATAQUE"]) != "Interno":
            lista_incidentes_reais.append(f"{{pais: '{linha['PAIS_ATAQUE']}', ip: '{linha['IP_SUSPEITO']}', tipo: '{linha['TIPO INCIDENTE']}'}}")
    
    js_array_incidentes = ", ".join(lista_incidentes_reais)

    # HTML/JS Avançado - Renderizador do Globo Escuro com Arcos Balísticos Neon de Entrada
    codigo_globo_kaspersky = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; background: #010408; overflow: hidden; font-family: 'Courier New', monospace; }
            #container-globo { width: 100%; height: 550px; position: relative; }
            .kaspersky-hud-lateral { 
                position: absolute; top: 20px; right: 20px; 
                background: rgba(3,7,15,0.96); width: 310px;
                padding: 18px; border: 1px solid #ff3333; 
                font-size: 11px; color: #fff; border-radius: 8px;
                box-shadow: 0 0 25px rgba(255,51,51,0.25);
            }
            .hud-header { color: #ff3333; font-weight: bold; font-size:12px; border-bottom: 1px solid rgba(255,51,51,0.3); padding-bottom: 6px; margin-bottom: 10px; letter-spacing:1px; }
            .log-item-linha { margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.04); padding-bottom: 6px; }
            .tag-origem { background: #ff3333; color: #fff; padding: 2px 5px; border-radius: 3px; font-size: 9px; font-weight:bold; }
        </style>
    </head>
    <body>
        <div id="container-globo">
            <div class="kaspersky-hud-lateral">
                <div class="hud-header">📡 LIVE ATTACK VECTOR ROUTING</div>
                <div id="log-dinamico-kaspersky"></div>
            </div>
        </div>
        <script>
            const logsAtaques = [__DATASET_JASCRIPT__];
            const logBox = document.getElementById('log-dinamico-kaspersky');

            function atualizarLogsFlutuantes() {
                logBox.innerHTML = "";
                // Seleciona itens aleatórios reais do seu CSV para simular o streaming dinâmico da Kaspersky
                for(let i=0; i<4; i++) {
                    let log = logsAtaques[Math.floor(Math.random() * logsAtaques.length)];
                    logBox.innerHTML += `
                        <div class="log-item-linha">
                            <span class="tag-origem">ORIGEM: ${log.pais.toUpperCase()}</span><br>
                            ⚔️ Vetor: ${log.tipo}<br>
                            📍 Destino: Infraestrutura Corporativa BR<br>
                            🌐 IP Origem: ${log.ip}
                        </div>
                    `;
                }
            }
            atualizarLogsFlutuantes();
            setInterval(atualizarLogsFlutuantes, 2400);

            // Setup de Renderização do Tridimensional Three.js
            const wrapper = document.getElementById('container-globo');
            const cena = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(55, wrapper.clientWidth / 550, 0.1, 1000);
            const renderizador = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderizador.setSize(wrapper.clientWidth, 550);
            wrapper.appendChild(renderizador.domElement);

            // Esfera Sólida Terrestre Escura
            const geometriaGlobo = new THREE.SphereGeometry(2.1, 40, 40);
            const materialGlobo = new THREE.MeshBasicMaterial({ color: 0x060b12, wireframe: false });
            const malhaGlobo = new THREE.Mesh(geometriaGlobo, materialGlobo);
            cena.add(malhaGlobo);

            // Malha de Redes do Planeta (Grid Neon Estilo Kaspersky)
            const materialGrid = new THREE.MeshBasicMaterial({ color: 0xff3333, wireframe: true, transparent: true, opacity: 0.14 });
            const malhaGrid = new THREE.Mesh(geometriaGlobo, materialGrid);
            cena.add(malhaGrid);

            // Grupo de Linhas de Ataques Balísticos
            const grupoArcos = new THREE.Group();
            cena.add(grupoArcos);

            function criarArcoProcedural() {
                if(grupoArcos.children.length > 12) grupoArcos.remove(grupoArcos.children[0]);
                
                const pontosArco = [];
                // Gera origem randômica representando os vetores externos globais detectados
                const xOrigem = (Math.random() - 0.5) * 3.6;
                const yOrigem = (Math.random() * 1.8) + 0.4; 
                const zOrigem = Math.sqrt(Math.abs(5.0 - xOrigem*xOrigem - yOrigem*yOrigem));

                // Destino Central Fixo (Representando o Centro de Dados Protegido)
                const xDestino = 0; const yDestino = -1.4; const zDestino = 1.5; 

                for (let i = 0; i <= 30; i++) {
                    let t = i / 30;
                    let p = new THREE.Vector3().lerpVectors(new THREE.Vector3(xOrigem, yOrigem, zOrigem), new THREE.Vector3(xDestino, yDestino, zDestino), t);
                    p.normalize().multiplyScalar(2.1 + Math.sin(t * Math.PI) * 0.55); // Elevação do arco balístico
                    pontosArco.push(p);
                }
                const curvaConstruida = new THREE.CatmullRomCurve3(pontosArco);
                const geometriaLinha = new THREE.BufferGeometry().setFromPoints(curvaConstruida.getPoints(50));
                const materialLinha = new THREE.LineBasicMaterial({ color: 0xff3333, transparent: true, opacity: 0.85 });
                const linhaFinal = new THREE.Line(geometriaLinha, materialLinha);
                grupoArcos.add(linhaFinal);
            }
            setInterval(criarArcoProcedural, 800);

            camera.position.z = 4.4;
            function loopAnimacao() {
                requestAnimationFrame(loopAnimacao);
                malhaGlobo.rotation.y += 0.002;
                malhaGrid.rotation.y += 0.002;
                grupoArcos.rotation.y += 0.002;
                renderizador.render(cena, camera);
            }
            window.addEventListener('resize', () => {
                camera.aspect = wrapper.clientWidth / 550; camera.updateProjectionMatrix();
                renderizador.setSize(wrapper.clientWidth, 550);
            });
            loopAnimacao();
        </script>
    </body>
    </html>
    """.replace("__DATASET_JASCRIPT__", js_array_incidentes)
    
    components.html(codigo_globo_kaspersky, height=560, scrolling=False)

# ==============================================================================
# ABA 3: GRAPHICS PERFORMANCE (BI E TELEMETRIA GERENCIAL)
# ==============================================================================
with tab_bi:
    st.markdown("### Telemetria e Indicadores Volumétricos")
    config_layout_estilo = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
    
    bg_col1, bg_col2 = st.columns(2)
    with bg_col1:
        fig_rosca = px.pie(
            df_soc, 
            names="RISCO_FINANCEIRO", 
            title="Exposição de Risco Crítico Financeiro (%)", 
            hole=0.4,
            color_discrete_sequence=["#ff3333", "#ff7733", "#22aa66"]
        )
        fig_rosca.update_layout(**config_layout_estilo)
        st.plotly_chart(fig_rosca, use_container_width=True)
        
    with bg_col2:
        fig_barras = px.bar(
            df_soc, 
            x="CLIENTE", 
            y="PREJUIZO_ESTIMADO", 
            color="TIPO INCIDENTE", 
            title="Prejuízo Histórico Mitigado por Cliente Ativo (R$)",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig_barras.update_layout(**config_layout_estilo)
        st.plotly_chart(fig_barras, use_container_width=True)

# ==============================================================================
# ABA 4: CHATBOT SEGURO, COMPLETO E COM MACROS DE ALTO NÍVEL
# ==============================================================================
with tab_ia:
    st.markdown("### Assistente de Mitigação Cognitiva Core")
    st.caption("Engine de inteligência estruturada para auditorias imediatas de vulnerabilidade e playbooks de remediação.")

    # Inicialização blindada do histórico do chat para evitar limpezas acidentais
    if "historico_chat_cyber" not in st.session_state:
        st.session_state["historico_chat_cyber"] = [
            {"role": "model", "content": "Terminal de IA Ativado. Pronto para auditar riscos de perímetro e apoiar respostas a incidentes baseadas em frameworks corporativos."}
        ]

    # Renderização visual rica do chat corporativo
    for mensagem in st.session_state["historico_chat_cyber"]:
        if mensagem["role"] == "user":
            st.markdown(f"""<div class='chat-bubble-operator'><b>👤 Operador Técnico:</b><br>{mensagem['content']}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='chat-bubble-core'><b>🤖 SentinelCore (LLM):</b><br>{mensagem['content']}</div>""", unsafe_allow_html=True)

    # Macros avançadas de alto nível de cibersegurança exigidas para a apresentação
    st.markdown("<p style='color:#ff3333; font-size:0.75rem; font-weight:700; margin-top:1.5rem;'>DISPARAR MACROS AUTOMATIZADAS DE SEGURANÇA:</p>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns(3)
    macro_prompt_selecionado = ""
    with b_col1:
        if st.button("🔴 Auditoria de Ataques DDoS por IPs Externos", use_container_width=True):
            macro_prompt_selecionado = "Gere um relatório forense detalhado e estruturado em tópicos explicando como mitigar ataques de IPs maliciosos externos usando regras automatizadas de Firewall de Borda e rate limiting."
    with b_col2:
        if st.button("🔒 Plano de Contenção de Vazamento de Credenciais", use_container_width=True):
            macro_prompt_selecionado = "Quais são as medidas corporativas imediatas de isolamento para conter riscos financeiros de nível Crítico causados por vazamento de tokens e credenciais em APIs de produção?"
    with b_col3:
        if st.button("🛡️ Playbook Contra Incidentes de Ransomware Ativo", use_container_width=True):
            macro_prompt_selecionado = "Estruture uma estratégia avançada de resiliência e resposta a incidentes baseada estritamente no framework NIST para isolar storages e blindar backups contra infecções por Ransomware."

    # Input manual do usuário
    with st.form("formulario_chat_ia", clear_on_submit=True):
        texto_digitado = st.text_input("Inserir prompt customizado de auditoria ou dúvida técnica:", placeholder="Ex: Como proteger microsserviços expostos contra OWASP Top 10?")
        gatilho_envio = st.form_submit_button("DISPARAR COMANDO COGNITIVO")

    prompt_final_ia = texto_digitado if gatilho_envio else macro_prompt_selecionado

    if prompt_final_ia.strip():
        # Registra o comando no histórico da sessão
        st.session_state["historico_chat_cyber"].append({"role": "user", "content": prompt_final_ia})
        
        # Conexão direta via requisição HTTPS robusta com a API do Gemini
        link_gemini_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        contexto_inteligencia = (
            "Você é o modelo de IA core do SOC SentinelAI. Sua função é responder a diretores, investidores e "
            "C-Levels com vocabulário técnico avançado (NIST, OWASP, ISO 27001, SIEM). Seja extremamente formal, "
            "responda em português e organize suas análises sempre em tópicos limpos."
        )
        
        corpo_payload = {"contents": [{"parts": [{"text": f"{contexto_inteligencia}\n\nComando Técnico: {prompt_final_ia}"}]}]}
        
        try:
            resposta_servidor = requests.post(link_gemini_api, json=corpo_payload, timeout=15)
            if resposta_servidor.status_code == 200:
                json_tratado = resposta_servidor.json()
                texto_resposta_ia = json_tratado["candidates"][0]["content"]["parts"][0]["text"]
            else:
                texto_resposta_ia = "⚠️ **Erro de Resolução de Link:** Falha ao validar autenticação do cluster de IA. Certifique-se de preencher a variável `GEMINI_API_KEY` nos Secrets do Streamlit."
        except Exception as erro_excecao:
            texto_resposta_ia = f"⚠️ **Timeout de Rede Perimetral:** Conexão interrompida com o gateway cognitivo externo. Detalhes: {str(erro_excecao)}"
            
        st.session_state["historico_chat_cyber"].append({"role": "model", "content": texto_resposta_ia})
        st.rerun()

# ==============================================================================
# 6. MONITORAMENTO EM TEMPO REAL (STREAMING VIVO COM GRÁFICO POR SEGUNDO)
# ==============================================================================
st.markdown("---")
st.markdown("#### 📡 Monitoramento de Fluxo em Tempo Real (Live Stream)")

# Geração de Gráfico contínuo simulando inspeção profunda de pacotes (DPI) ativos
momento_agora = datetime.datetime.now()
eixo_x_timestamps = [(momento_agora - datetime.timedelta(seconds=id_sec * 5)).strftime("%H:%M:%S") for id_sec in range(15)]
eixo_x_timestamps.reverse()
eixo_y_requisicoes = [random.randint(1400, 3900) for _ in range(15)]

fig_streaming_vivo = go.Figure()
fig_streaming_vivo.add_trace(go.Scatter(
    x=eixo_x_timestamps, 
    y=eixo_y_requisicoes, 
    mode='lines+markers', 
    line=dict(color='#ff3333', width=3),
    marker=dict(size=6, color='#ffffff'),
    fill='tozeroy',
    fillcolor='rgba(239, 68, 68, 0.04)'
))
fig_streaming_vivo.update_layout(
    title="Volume de Pacotes Inundantes Bloqueados por Segundo pelo Firewall Corporativo",
    paper_bgcolor="rgba(0,0,0,0)", 
    plot_bgcolor="rgba(5, 9, 16, 0.7)",
    font_color="#8a99ad",
    margin=dict(l=40, r=40, t=40, b=40),
    height=250,
    xaxis=dict(gridcolor="rgba(255,255,255,0.02)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.02)")
)
st.plotly_chart(fig_streaming_vivo, use_container_width=True)
