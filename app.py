import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import datetime
import requests
import os

# Configuração da Chave da API do Gemini via Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA")

# 1. Configuração da Página Cyber SOC
st.set_page_config(
    page_title="SentinelAI // SOC Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Carregamento do Dataset Oficial (CSV) com Fallback Seguro
@st.cache_data
def carregar_dataset_oficial():
    # Procura pelo arquivo enviado no diretório atual
    if os.path.exists("dataset_final.csv"):
        df = pd.read_csv("dataset_final.csv")
    elif os.path.exists("dataset_mysql.csv"):
        df = pd.read_csv("dataset_mysql.csv")
    else:
        # Cria estrutura idêntica caso falte no deploy temporário
        st.error("⚠️ Arquivo 'dataset_final.csv' não encontrado! Criando dados temporários...")
        dados_mock = {
            "ID": range(1, 6),
            "DATA": ["2026-03-11", "2026-03-27", "2026-04-05", "2026-04-03", "2026-03-07"],
            "TIPO INCIDENTE": ["ataque", "lentidão", "ataque", "lentidão", "lentidão"],
            "SEVERIDADE": ["crítica", "crítica", "crítica", "média", "baixa"],
            "TEMPO RESOLUÇÃO": [24, 24, 78, 58, 49],
            "ORIGEM": ["aplicação", "aplicação", "servidor", "banco de dados", "aplicação"],
            "STATUS": ["pendente", "pendente", "resolvido", "pendente", "resolvido"],
            "PAIS_ATAQUE": ["China", "Interno", "Alemanha", "Interno", "Interno"],
            "PREJUIZO_ESTIMADO": [13016, 18187, 15719, 4486, 1173],
            "RECEITA_CLIENTE": [88516, 55707, 78030, 92356, 66453],
            "CLIENTE": ["Nubank", "Santander", "Mercado Livre", "XP Investimentos", "iFood"],
            "NIVEL_AMEACA": ["crítico", "crítico", "crítico", "médio", "baixo"],
            "IP_SUSPEITO": ["129.211.51.50", "Nenhum", "202.202.156.53", "Nenhum", "Nenhum"],
            "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Não", "Não"]
        }
        df = pd.DataFrame(dados_mock)
    
    # Padronização de strings para evitar erros de busca/filtros
    df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str).str.title()
    df["SEVERIDADE"] = df["SEVERIDADE"].astype(str).str.title()
    df["CLIENTE"] = df["CLIENTE"].astype(str)
    return df

df_soc = carregar_dataset_oficial()

# 3. Funções Utilitárias para o Buffer de Auditoria Local (Syslog)
def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] {usuario} | {acao}")

# 4. Estilização Avançada Baseada na Identidade Visual (Escuro e Red Neon)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #1a0808 0%, #07090e 60%, #020305 100%);
}

[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }

/* Menu Lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06080c 0%, #020305 100%) !important;
    border-right: 1px solid rgba(239, 68, 68, 0.15) !important;
}

/* Painel de Métricas */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.02) 0%, rgba(7, 9, 14, 0.98) 100%);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 14px;
    padding: 1.1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.72rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #ef4444 !important; font-size: 1.65rem !important; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }

/* Abas de Navegação */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(11, 13, 20, 0.8) !important;
    border-radius: 12px !important;
    padding: 0.3rem !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(239, 68, 68, 0.12) !important;
    color: #ef4444 !important;
    border-radius: 8px !important;
}

/* Botões Modernos */
div.stButton>button {
    background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

/* Caixa de Resposta Automática SOC Playbook */
.playbook-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.03) 0%, rgba(7, 9, 14, 0.95) 100%);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin-top: 1rem;
}

/* Bolhas de Chat */
.chat-user { background: #1e293b; border-radius: 14px 14px 2px 14px; padding: 0.85rem; margin: 0.5rem 0 0.5rem auto; max-width: 80%; width: fit-content; }
.chat-ai { background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.18); border-radius: 14px 14px 14px 2px; padding: 0.85rem; margin: 0.5rem 0; max-width: 80%; width: fit-content; }
.soc-badge { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.62rem; font-weight: 700; }
.badge-live { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }

/* MODAL DE PRIVACIDADE CENTRALIZADO NO CENTRO DA TELA */
.cookie-blur-bg {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(4, 5, 9, 0.85); backdrop-filter: blur(8px);
    z-index: 99998; display: flex; align-items: center; justify-content: center;
}
.cookie-modal-center {
    background: #0b0d14; border: 2px solid #ef4444; border-radius: 16px;
    padding: 2.5rem; max-width: 520px; width: 90%; text-align: center;
    box-shadow: 0 20px 50px rgba(239, 68, 68, 0.2); z-index: 99999;
}
</style>
""", unsafe_allow_html=True)

# 5. Gerenciamento Globais de Estado de Sessão
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
if "lgpd_consent" not in st.session_state:
    st.session_state["lgpd_consent"] = False

# --- COMPLIANCE LGPD CENTRALIZADO NA TELA ---
if not st.session_state["lgpd_consent"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    # Renderização HTML/CSS nativa injetando o modal no centro exato da tela
    st.markdown("""
    <div class="cookie-blur-bg">
        <div class="cookie-modal-center">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🍪</div>
            <h3 style="color: #fff; font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; margin: 0 0 0.8rem 0; font-weight:700;">LGPD & POLÍTICA DE PRIVACIDADE</h3>
            <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.6; margin-bottom: 2rem;">
                Este terminal corporativo processa dados de inteligência contra ameaças cibernéticas. Para estar em total conformidade com a Lei Geral de Proteção de Dados (LGPD), solicitamos autorização para carregar os logs e buffers em cache nesta sessão.
            </p>
            <div id="modal-placeholder"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botões do Streamlit acoplados abaixo do modal para manipulação de estado do Python
    cm_sp, cm_btn1, cm_btn2, cm_sp2 = st.columns([1, 1.5, 1.5, 1])
    with cm_btn1:
        if st.button("RECUSAR TUDO", use_container_width=True):
            st.warning("Acesso negado sem consentimento.")
    with cm_btn2:
        if st.button("ACEITAR E ENTRAR", use_container_width=True):
            st.session_state["lgpd_consent"] = True
            st.rerun()
    st.stop()

# --- FORMULÁRIO DE LOGIN COM MÚLTIPLOS OPERADORES ---
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_l, c_mid, c_r = st.columns([1, 1.2, 1])
    with c_mid:
        st.markdown("""
        <div style="text-align: center; margin-top: 4rem; margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(239,68,68,0.3));">🛡️</div>
            <h1 style="font-family: 'Space Grotesk', sans-serif; color: #fff; font-size: 2rem; margin: 0.2rem 0;">Sentinel<span style="color:#ef4444;">AI</span></h1>
            <p style="color: #64748b; font-size: 0.8rem;">SOC Multi-Operator Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: rgba(11,13,20,0.8); padding: 1.8rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.04);'>", unsafe_allow_html=True)
            
            # Base de credenciais de operadores expandida
            OPERADORES_PERMITIDOS = {
                "admin": "admin123",
                "analista": "analista123",
                "supervisor": "superSOC99",
                "professor": "ecomove2026"
            }
            
            user_in = st.text_input("Credencial do Operador (User)", placeholder="Ex: analista")
            pass_in = st.text_input("Chave Criptográfica (Password)", type="password", placeholder="••••••••")
            
            if st.button("AUTENTICAR NO CLUSTER", use_container_width=True):
                if user_in in OPERADORES_PERMITIDOS and OPERADORES_PERMITIDOS[user_in] == pass_in:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = user_in
                    adicionar_log(user_in, "Realizou login na console de comando SOC")
                    st.rerun()
                else:
                    st.error("Falha na validação do token. Acesso negado.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

user_atual = st.session_state["usuario"]

# --- SIDEBAR OPERACIONAL ---
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:1rem 0;'><h2 style='font-family:\"Space Grotesk\"; color:#fff; margin:0;'>Sentinel<span style='color:#ef4444;'>AI</span></h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 0.8rem;'>
        <p style='color: #64748b; font-size: 0.6rem; margin:0; font-weight:700;'>OPERADOR AUTENTICADO</p>
        <p style='color: #ffffff; font-weight: 700; margin: 0 0 0.4rem 0; font-size: 0.9rem;'>@{user_atual.upper()}</p>
        <span class='soc-badge badge-live'>● ARQUIVO DATASET_FINAL CONECTADO</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 LOGOUT", use_container_width=True):
        adicionar_log(user_atual, "Encerrou a sessão do terminal")
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.rerun()

# --- ESTRUTURA PRINCIPAL DO PAINEL ---
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(239,68,68,0.04) 0%, rgba(0,0,0,0) 100%); border: 1px solid rgba(239,68,68,0.12); border-radius: 16px; padding: 1.2rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
    <div>
        <p style="color: #ef4444; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; margin: 0;">SISTEMA BASEADO EM INTELIGÊNCIA DATASET</p>
        <h2 style="color: #fff; font-family: 'Space Grotesk', sans-serif; margin: 0; font-weight: 700; font-size: 1.5rem;">Console Avançada de Resolução de Incidentes</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# Cálculo de Métricas Inteligentes com base no seu CSV real
tot_ocorrências = len(df_soc)
criticos_count = len(df_soc[df_soc["SEVERIDADE"].str.lower().str.contains("crítica|alto|alta", na=False)])
preju_acumulado = df_soc["PREJUIZO_ESTIMADO"].sum()

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1: st.metric("Ocorrências Carregadas (CSV)", f"{tot_ocorrências:,}")
with col_m2: st.metric("Eventos de Alta Severidade", f"{criticos_count:,}")
with col_m3: st.metric("Prejuízo Mitigado Estimado", f"R$ {preju_acumulado:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Definição das Abas Corrigidas
tab_analise, tab_globe, tab_bi, tab_ai, tab_audit = st.tabs([
    "🔍 ANÁLISE DE INCIDENTES", "🌍 GLOBO DE AMEAÇAS 3D", "📊 DASHBOARD CORPORATIVO", "🤖 ASSISTENTE COGNITIVO", "📋 AUDITORIA SYSLOG"
])

# --- ABA 1: ABA DE ANÁLISE SOLICITADA (TIPO, CLIENTE, IP, PAÍS E RESPOSTA AUTOMÁTICA) ---
with tab_analise:
    st.markdown("### Investigação de Vetores e Mitigação Automatizada")
    st.caption("Selecione os parâmetros do incidente em andamento para inspecionar os detalhes técnicos e acionar a resposta automática de proteção.")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        # Puxa dinamicamente os tipos de incidentes únicos gravados no seu CSV
        lista_tipos = sorted(df_soc["TIPO INCIDENTE"].unique())
        tipo_selecionado = st.selectbox("Selecione o Tipo de Incidente:", lista_tipos)
        
    with col_sel2:
        # Filtra os clientes afetados por esse tipo de incidente no CSV
        clientes_filtrados = sorted(df_soc[df_soc["TIPO INCIDENTE"] == tipo_selecionado]["CLIENTE"].unique())
        cliente_selecionado = st.selectbox("Selecione o Cliente Afetado:", clientes_filtrados)
        
    # Extração da linha correspondente aos filtros
    dados_filtrados = df_soc[
        (df_soc["TIPO INCIDENTE"] == tipo_selecionado) & 
        (df_soc["CLIENTE"] == cliente_selecionado)
    ]
    
    if not dados_filtrados.empty:
        linha_incidente = dados_filtrados.iloc[0]
        
        # Painel Informativo dos Dados Solicitados (País, IP, Severidade, etc.)
        st.markdown("<br>", unsafe_allow_html=True)
        ca_1, ca_2, ca_3, ca_4 = st.columns(4)
        with ca_1:
            st.markdown(f"**🌐 País de Origem:**<br><span style='color:#fff; font-size:1.1rem;'>{linha_incidente.get('PAIS_ATAQUE', 'Desconhecido')}</span>", unsafe_allow_html=True)
        with ca_2:
            st.markdown(f"**🚨 IP Suspeito Detectado:**<br><span style='color:#ef4444; font-family:monospace; font-size:1.1rem;'>{linha_incidente.get('IP_SUSPEITO', 'Nenhum')}</span>", unsafe_allow_html=True)
        with ca_3:
            st.markdown(f"**⚡ Grau de Severidade:**<br><span style='color:#f59e0b; font-size:1.1rem;'>{linha_incidente.get('SEVERIDADE', 'Média')}</span>", unsafe_allow_html=True)
        with ca_4:
            prej_val = linha_incidente.get('PREJUIZO_ESTIMADO', 0)
            st.markdown(f"**📉 Impacto Financeiro:**<br><span style='color:#ef4444; font-size:1.1rem;'>R$ {prej_val:,.2f}</span>", unsafe_allow_html=True)
            
        # Geração da Resposta Automática Inteligente baseada no Tipo
        st.markdown("---")
        st.markdown("#### ⚡ Resposta Automática do Sistema (SOC Playbook Engine)")
        
        ip_alvo = linha_incidente.get('IP_SUSPEITO', 'Nenhum')
        pais_alvo = linha_incidente.get('PAIS_ATAQUE', 'Interno')
        
        # Lógica de Playbooks Automáticos baseados na engenharia do seu Dataset
        if "ataque" in tipo_selecionado.lower() or "ddos" in tipo_selecionado.lower():
            comando_playbook = f"RESTRIC_IP_DROP_INBOUND [{ip_alvo}]"
            descricao_playbook = f"Ataque volumétrico externo detectado originando do país: **{pais_alvo}**. O firewall perimetral acionou regras de mitigação via Null-Routing na borda da aplicação do cliente {cliente_selecionado}."
        elif "lentidão" in tipo_selecionado.lower() or "banco" in tipo_selecionado.lower():
            comando_playbook = f"REPLICATE_CLUSTER_REBALANCE"
            descricao_playbook = f"Lentidão ou gargalo estrutural identificado na infraestrutura interna do cliente {cliente_selecionado}. O gatilho de auto-scaling foi ativado para rebalanceamento e limpeza dos buffers de requisição."
        else:
            comando_playbook = f"ISOLATE_HOST_CONTAINER"
            descricao_playbook = f"Comportamento anômalo registrado. O container afetado foi colocado em quarentena de rede isolada para análise forense complementar pelo analista @{user_atual.upper()}."

        st.markdown(f"""
        <div class="playbook-card">
            <p style="color:#10b981; font-weight:700; font-family:'Space Grotesk', sans-serif; margin:0 0 0.4rem 0; font-size:0.85rem;">✔ PLAYBOOK EXECUTADO COM SUCESSO:</p>
            <code style="background:rgba(16,185,129,0.12); color:#10b981; padding:0.3rem 0.6rem; border-radius:4px; font-size:0.9rem;">{comando_playbook}</code>
            <p style="color:#94a3b8; font-size:0.85rem; margin-top:0.8rem; line-height:1.6;">{descricao_playbook}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("AUTENTICAR E CONFIRMAR RESOLUÇÃO MANUAL"):
            adicionar_log(user_atual, f"Validou manualmente a mitigação do incidente '{tipo_selecionado}' no cliente {cliente_selecionado}")
            st.toast("Playbook e logs auditados sincronizados!", icon="✔")
    else:
        st.info("Nenhuma ocorrência encontrada combinando o tipo e cliente selecionados no CSV atual.")

# --- ABA 2: GLOBO DE AMEAÇAS COM NOMES DOS PAÍSES EXPLICITADOS ---
with tab_globe:
    st.markdown("### Globo Geopolítico de Ameaças Interceptadas")
    st.caption("Visualização tridimensional orientada por coordenadas geográficas reais de pacotes maliciosos.")
    
    # Injeção de tags dinâmicas no script Three.js para plotar nomes de países na interface do canvas
    mapa_dados_paises = df_soc["PAIS_ATAQUE"].value_counts().to_dict()
    string_paises_js = ", ".join([f"'{k}'" for k in mapa_dados_paises.keys() if k != 'Interno'])
    
    three_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body {{ margin: 0; background: #07090e; overflow: hidden; font-family: monospace; }}
            #container-3d {{ width: 100%; height: 460px; position: relative; }}
            .console-overlay {{ position: absolute; top: 15px; left: 15px; background: rgba(11,13,20,0.95); border: 1px solid #ef4444; border-radius: 6px; padding: 12px; color: #ef4444; font-size: 11px; max-width:280px; box-shadow:0 0 15px rgba(239,68,68,0.2); }}
        </style>
    </head>
    <body>
        <div id="container-3d">
            <div class="console-overlay">
                <b>[GEOPOLITICAL SENTINEL CORE]</b><br>
                > MONITORING VECTOR TARGETS:<br>
                <span style="color:#fff;">[{string_paises_js}]</span>
            </div>
        </div>
        <script>
            const div = document.getElementById('container-3d');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, div.clientWidth / 460, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(div.clientWidth, 460);
            div.appendChild(renderer.domElement);

            const geo = new THREE.SphereGeometry(2, 28, 28);
            const mat = new THREE.MeshBasicMaterial({ color: 0xef4444, wireframe: true, transparent: true, opacity: 0.1 });
            const globe = new THREE.Mesh(geo, mat);
            scene.add(globe);

            const pGeo = new THREE.SphereGeometry(2.01, 16, 16);
            const pMat = new THREE.PointsMaterial({ color: 0xef4444, size: 0.04, transparent: true, opacity: 0.7 });
            const points = new THREE.Points(pGeo, pMat);
            scene.add(points);

            camera.position.z = 4.0;
            function run() {{
                requestAnimationFrame(run);
                globe.rotation.y += 0.002;
                points.rotation.y += 0.002;
                renderer.render(scene, camera);
            }}
            window.addEventListener('resize', () => {{
                camera.aspect = div.clientWidth / 460; camera.updateProjectionMatrix();
                renderer.setSize(div.clientWidth, 460);
            }});
            run();
        </script>
    </body>
    </html>
    """
    components.html(three_html, height=480, scrolling=False)

# --- ABA 3: DASHBOARD BI RECONSTRUÍDO ---
with tab_bi:
    st.markdown("### Métricas Avançadas de Performance Corporativa")
    theme_plotly = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    
    gb1, gb2 = st.columns(2)
    with gb1:
        f_pie = px.pie(df_soc, names="TIPO INCIDENTE", title="Percentual por Tipologia de Risco", color_discrete_sequence=["#ef4444", "#f97316", "#3b82f6"])
        f_pie.update_layout(**theme_plotly)
        st.plotly_chart(f_pie, use_container_width=True)
    with gb2:
        f_bar = px.bar(df_soc, x="CLIENTE", y="PREJUIZO_ESTIMADO", color="SEVERIDADE", title="Prejuízo por Cliente e Severidade", color_discrete_map={"Crítica": "#ef4444", "Média": "#f97316", "Baixa": "#3b82f6"})
        f_bar.update_layout(**theme_plotly)
        st.plotly_chart(f_bar, use_container_width=True)

# --- ABA 4: CHATBOT COGNITIVO COM COMANDOS RÁPIDOS PRONTOS ---
with tab_ai:
    st.markdown("### Assistente de Mitigação Cognitiva Core")
    st.caption("Utilize os botões de atalho rápidos ou escreva um comando customizado para obter diagnóstico cirúrgico da inteligência do SOC.")
    
    if "chat_history_soc" not in st.session_state:
        st.session_state["chat_history_soc"] = []
        
    # Renderização do histórico
    for m in st.session_state["chat_history_soc"]:
        cls = "chat-user" if m["role"] == "user" else "chat-ai"
        lbl = "👤 Operador" if m["role"] == "user" else "🤖 SentinelCore AI"
        st.markdown(f'<div class="{cls}"><b>{lbl}:</b> {m["content"]}</div>', unsafe_allow_html=True)
    
    # SISTEMA DE COMANDOS AUTOMÁTICOS COM CLIQUES RÁPIDOS
    st.markdown("<p style='color:#64748b; font-size:0.75rem; font-weight:600; margin-bottom:0.4rem;'>COMANDOS RÁPIDOS DISPONÍVEIS:</p>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns(3)
    comando_acionado = ""
    
    with bc1:
        if st.button("📋 Rodar Análise de Riscos Gerais", use_container_width=True):
            comando_acionado = "Gere um relatório macro consolidado resumindo o nível das ameaças e quais clientes demandam atenção imediata."
    with bc2:
        if st.button("🛑 Rodar Protocolo Contra DDoS", use_container_width=True):
            comando_acionado = "Quais as melhores práticas imediatas para conter um ataque DDoS do tipo volumétrico e mitigar falsos positivos?"
    with bc3:
        if st.button("🔒 Rodar Guia de Compliance LGPD", use_container_width=True):
            comando_acionado = "Como nosso SOC garante conformidade e segurança na guarda de IPs suspeitos de ataques perante as regras da LGPD?"
            
    # Formulário clássico de envio de perguntas por texto
    with st.form("ai_terminal", clear_on_submit=True):
        pergunta_texto = st.text_input("Injetar comando customizado na IA:", placeholder="Escreva sua dúvida técnica...")
        botao_enviar = st.form_submit_button("DISPARAR PROMPT")
        
    # Aglutinação lógica de gatilhos (Texto ou Botão de comando)
    pergunta_final = pergunta_texto if botao_enviar else comando_acionado
    
    if pergunta_final.strip():
        st.session_state["chat_history_soc"].append({"role": "user", "content": pergunta_final})
        
        # Criação de um super prompt de contexto enriquecido com seus dados reais do CSV
        prompt_contextualizado = f"""Você é o motor cognitivo principal do Cyber SOC da empresa SentinelAI.
        Seu operador logado é o analista '{user_atual}'. 
        
        DADOS ESTATÍSTICOS EM TEMPO REAL EXTRAÍDOS DO DATASET DO PROJETO:
        - Total de incidentes mapeados no CSV: {tot_ocorrências}
        - Incidentes de alta severidade pendentes: {criticos_count}
        
        Instruções de Resposta:
        Dê diretrizes cirúrgicas e altamente técnicas em português. Responda diretamente, sem enrolação.
        
        Pergunta/Comando do Operador: {pergunta_final}"""
        
        url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload_rest = {"contents": [{"parts": [{"text": prompt_contextualizado}]}]}
        
        try:
            r_post = requests.post(url_api, json=payload_rest, headers={"Content-Type": "application/json"}, timeout=15)
            if r_post.status_code == 200:
                resposta = r_post.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                resposta = f"⚠️ [ERRO REST]: Código HTTP {r_post.status_code}. Valide as chaves nos Segredos do Streamlit Cloud."
        except Exception as ex:
            resposta = f"⚠️ [FALHA DE LINK]: Erro de rede na comunicação com o Core Cognitivo: {str(ex)[:50]}"
            
        st.session_state["chat_history_soc"].append({"role": "model", "content": resposta})
        adicionar_log(user_atual, f"Consultou Assistente Cognitivo: '{pergunta_final[:35]}...'")
        st.rerun()

# --- ABA 5: AUDITORIA DE LOGS DO SISTEMA ---
with tab_audit:
    st.markdown("### Auditoria Estrutural de Logs (Terminal Syslog)")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log_line in reversed(st.session_state["logs_sistema"][-30:]):
            st.code(log_line, language=None)
    else:
        st.info("Nenhuma atividade capturada no buffer de auditoria atual.")
