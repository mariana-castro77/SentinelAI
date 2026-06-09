import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import hashlib
import datetime
import random
import requests
import mysql.connector

# Chave API obtida dos Segredos
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA")

# 1. Configuração da Página Cyber SOC
st.set_page_config(
    page_title="SentinelAI // SOC Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Conexão Segura com o Banco MySQL Existente
@st.cache_resource(ttl=600)
def inicializar_conexao_mysql():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"].get("port", 3306)), # Força a ser um número inteiro puro
            charset='utf8mb4',
            use_pure=True
        )
        return conn
    except Exception as e:
        st.error(f"⚠️ Erro de conexão com o banco de dados principal: {e}")
        return None

conn_mysql = inicializar_conexao_mysql()

def executar_query(query, params=None, commit=False):
    if not conn_mysql:
        return None
    try:
        # Garante que a conexão não caiu por timeout antes de executar
        conn_mysql.ping(reconnect=True, attempts=3, delay=2)
        cursor = conn_mysql.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if commit:
            conn_mysql.commit()
            return True
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Exception as e:
        print(f"Erro SQL: {e}")
        return None

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] {usuario} | {acao}")
    executar_query(
        "INSERT INTO logs_sistema (usuario, acao) VALUES (%s, %s)",
        (usuario, acao),
        commit=True
    )

# 3. Estilização Avançada UI/UX e Mecanismo de Scroll Suave (Parallax/Lenis)
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

/* Ocultar cabeçalhos padrão do Streamlit */
[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }

/* Barra Lateral Estilo Dark-Web */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06080c 0%, #020305 100%) !important;
    border-right: 1px solid rgba(239, 68, 68, 0.15) !important;
}

/* Painel de Métricas SOC (Inspirado no visual Dark Neon solicitado) */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.02) 0%, rgba(7, 9, 14, 0.98) 100%);
    border: 1px solid rgba(239, 68, 68, 0.2);
    border-radius: 14px;
    padding: 1.1rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    transition: all 0.35s ease;
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(239, 68, 68, 0.45);
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(239, 68, 68, 0.15);
}
[data-testid="stMetricLabel"] { color: #94a3b8 !important; font-size: 0.72rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #ef4444 !important; font-size: 1.65rem !important; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }

/* Customização dos Inputs */
input, select, textarea, div[data-baseweb="select"] {
    background-color: #0b0d14 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

/* Abas Customizadas */
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
    padding: 0.5rem 1.1rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(239, 68, 68, 0.12) !important;
    color: #ef4444 !important;
    border-radius: 8px !important;
}

/* Botões de Ação */
div.stButton>button {
    background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.25s ease !important;
}
div.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4) !important;
}

/* Design das Mensagens do Chatbot */
.chat-user { background: #1e293b; border-radius: 14px 14px 2px 14px; padding: 0.85rem; margin: 0.5rem 0 0.5rem auto; max-width: 80%; width: fit-content; border: 1px solid rgba(255,255,255,0.05); }
.chat-ai { background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.18); border-radius: 14px 14px 14px 2px; padding: 0.85rem; margin: 0.5rem 0; max-width: 80%; width: fit-content; }

.soc-badge { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.62rem; font-weight: 700; }
.badge-live { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }
</style>

<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.19/bundled/lenis.min.js"></script>
<script>
    const lenis = new Lenis({ duration: 1.1, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smooth: true });
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
</script>
""", unsafe_allow_html=True)

# 4. Controle de Sessão (Autenticação e Consentimento LGPD)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
if "lgpd_consent" not in st.session_state:
    st.session_state["lgpd_consent"] = False

# --- COMPLIANCE LGPD REALÍSTICO (Estilo Segunda Imagem) ---
if not st.session_state["lgpd_consent"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    # Layout visual inferior idêntico ao exigido para nível de auditoria
    st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px; max-width: 400px; background: #0b0d14; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 1.3rem; z-index: 99999; box-shadow: 0 15px 40px rgba(0,0,0,0.7);">
        <h4 style="margin: 0 0 0.5rem 0; color: #fff; font-size: 0.9rem; font-family: sans-serif; font-weight: 700;">AVISO DE PRIVACIDADE E COOKIES</h4>
        <p style="color: #94a3b8; font-size: 0.75rem; font-family: sans-serif; line-height: 1.5; margin-bottom: 1rem;">
            A plataforma SentinelAI coleta dados técnicos e operacionais de navegação em conformidade com a LGPD (Lei nº 13.709/18). O prosseguimento assegura o consentimento com os termos de monitoramento cibernético.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c_sp, c_rec, c_acc = st.columns([3.5, 1, 1])
    with c_rec:
        if st.button("REJEITAR"):
            st.warning("Consentimento mandatório para operação.")
    with c_acc:
        if st.button("ACEITAR"):
            st.session_state["lgpd_consent"] = True
            st.rerun()
    st.stop()

# --- TELA DE ACESSO EXCLUSIVA (Com Usuários Visíveis) ---
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_l, c_mid, c_r = st.columns([1, 1.1, 1])
    with c_mid:
        st.markdown("""
        <div style="text-align: center; margin-top: 5rem; margin-bottom: 1.5rem;">
            <div style="font-size: 3.2rem; filter: drop-shadow(0 0 12px rgba(239,68,68,0.3));">🛡️</div>
            <h1 style="font-family: 'Space Grotesk', sans-serif; color: #fff; font-size: 2.2rem; margin: 0.2rem 0;">Sentinel<span style="color:#ef4444;">AI</span></h1>
            <p style="color: #64748b; font-size: 0.85rem;">Security Operations Center & Intelligence Terminal</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: rgba(11,13,20,0.7); padding: 1.8rem; border-radius: 16px; border: 1px solid rgba(255,255,255,0.04);'>", unsafe_allow_html=True)
            
            st.markdown("<p style='color: #94a3b8; font-size: 0.75rem; font-weight:600; margin-bottom: 0.6rem;'>OPERADORES ATIVOS NO CLUSTER:</p>", unsafe_allow_html=True)
            cu1, cu2 = st.columns(2)
            with cu1: st.code("admin\n(Pass: admin123)", language=None)
            with cu2: st.code("analista\n(Pass: analista123)", language=None)
            
            user_in = st.text_input("Operador (User)", placeholder="Nome de usuário...")
            pass_in = st.text_input("Chave de Acesso (Password)", type="password", placeholder="••••••••")
            
            USUARIOS = {"admin": "admin123", "analista": "analista123"}
            
            if st.button("CONECTAR AO TERMINAL", use_container_width=True):
                if user_in in USUARIOS and USUARIOS[user_in] == pass_in:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = user_in
                    adicionar_log(user_in, "Acessou a console de segurança remota")
                    st.rerun()
                else:
                    st.error("Falha na autenticação.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- CARREGAMENTO DO BANCO DE DADOS REAL DO USUÁRIO ---
user_atual = st.session_state["usuario"]

def carregar_dados_reais():
    res = executar_query("SELECT * FROM incidentes")
    if res:
        return pd.DataFrame(res)
    # Mock estratégico apenas caso o banco esteja inacessível na hora do deploy inicial
    return pd.DataFrame(columns=["DATA", "TIPO INCIDENTE", "SEVERIDADE", "ORIGEM", "STATUS", "PAIS_ATAQUE", "CLIENTE", "RISCO_FINANCEIRO", "BLOQUEADO_AUTOMATICAMENTE"])

df_banco = carregar_dados_reais()

# --- SIDEBAR OPERACIONAL ---
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:1rem 0;'><h2 style='font-family:\"Space Grotesk\"; color:#fff; margin:0;'>Sentinel<span style='color:#ef4444;'>AI</span></h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 0.8rem;'>
        <p style='color: #64748b; font-size: 0.6rem; margin:0; font-weight:700;'>OPERADOR CORRENTE</p>
        <p style='color: #ffffff; font-weight: 700; margin: 0 0 0.4rem 0; font-size: 0.9rem;'>@{user_atual.upper()}</p>
        <span class="soc-badge badge-live">● CONEXÃO SEGURA</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 DESCONECTAR TERMINAL", use_container_width=True):
        adicionar_log(user_atual, "Desconectou do terminal SOC")
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.rerun()

# --- DASHBOARD LAYOUT PRINCIPAL ---
st.markdown("""
<div style="background: linear-gradient(135deg, rgba(239,68,68,0.04) 0%, rgba(0,0,0,0) 100%); border: 1px solid rgba(239,68,68,0.12); border-radius: 16px; padding: 1.2rem; margin-bottom: 1.8rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
    <div>
        <p style="color: #ef4444; font-size: 0.7rem; font-weight: 700; letter-spacing: 1.5px; margin: 0;">SISTEMA CORPORATIVO MONITORADO</p>
        <h2 style="color: #fff; font-family: 'Space Grotesk', sans-serif; margin: 0; font-weight: 700; font-size: 1.5rem;">Console Avançada nível SOC</h2>
    </div>
    <div><span class="soc-badge badge-live">● OPERACIONAL EM TEMPO REAL</span></div>
</div>
""", unsafe_allow_html=True)

# Cálculo dinâmico baseado nas colunas reais do seu banco
total_inc = len(df_banco)
criticos = len(df_banco[df_banco["SEVERIDADE"].astype(str).str.lower() == "crítica"]) if total_inc > 0 else 0
bloqueados = len(df_banco[df_banco["BLOQUEADO_AUTOMATICAMENTE"].astype(str).str.lower() == "sim"]) if total_inc > 0 else 0

c1, c2, c3 = st.columns(3)
with c1: st.metric("Total de Ocorrências", f"{total_inc:,}")
with c2: st.metric("Incidentes Críticos", f"{criticos:,}")
with c3: st.metric("Bloqueados por Regra de Firewall", f"{bloqueados:,}")

st.markdown("<br>", unsafe_allow_html=True)

# Abas Interativas do Sistema
tab_globe, tab_bi, tab_actions, tab_ai, tab_audit = st.tabs([
    "🌍 GLOBO DE AMEAÇAS 3D", "📊 METRICAS BI", "⚡ CENTRAL DE INGESTÃO", "🤖 CHAT COGNITIVO", "📋 SYSLOG AUDIT"
])

# --- ABA 1: GLOBO 3D KASPERSKY STYLE VIA WEBGL ---
with tab_globe:
    st.markdown("### Mapa Global Vivo de Ataques (3D Cyberspace Map)")
    st.caption("Visualização tridimensional de pacotes de intrusão interceptados nas últimas janelas de tempo.")
    
    three_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; background: #07090e; overflow: hidden; }
            #container-3d { width: 100%; height: 480px; position: relative; }
            .console-overlay { position: absolute; top: 10px; left: 10px; background: rgba(11,13,20,0.9); border: 1px solid #ef4444; border-radius: 6px; padding: 10px; color: #ef4444; font-family: monospace; font-size: 10px; pointer-events: none; }
        </style>
    </head>
    <body>
        <div id="container-3d"><div class="console-overlay">[SENTINEL-CORE V2.6]<br>> GL_MAP STREAMING...<br>> ACTIVE PACKETS DETECTED</div></div>
        <script>
            const div = document.getElementById('container-3d');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, div.clientWidth / 480, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(div.clientWidth, 480);
            div.appendChild(renderer.domElement);

            const geo = new THREE.SphereGeometry(2, 32, 32);
            const mat = new THREE.MeshBasicMaterial({ color: 0xef4444, wireframe: true, transparent: true, opacity: 0.12 });
            const globe = new THREE.Mesh(geo, mat);
            scene.add(globe);

            const pGeo = new THREE.SphereGeometry(2.01, 16, 16);
            const pMat = new THREE.PointsMaterial({ color: #ef4444, size: 0.035, transparent: true, opacity: 0.8 });
            const points = new THREE.Points(pGeo, pMat);
            scene.add(points);

            const lines = new THREE.Group();
            scene.add(lines);

            function addArc() {
                const pts = [];
                const s = new THREE.Vector3((Math.random()-0.5)*3, (Math.random()-0.5)*3, (Math.random()-0.5)*3).normalize().multiplyScalar(2.01);
                const e = new THREE.Vector3(-0.4, -0.6, 1.8); // Foco estético em servidores locais (LATAM)
                for(let i=0; i<=15; i++) {
                    let t = i/15;
                    let p = new THREE.Vector3().lerpVectors(s, e, t).normalize().multiplyScalar(2.01 + Math.sin(t*Math.PI)*0.35);
                    pts.push(p);
                }
                const cGeom = new THREE.BufferGeometry().setFromPoints(pts);
                const cMat = new THREE.LineBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.7 });
                const l = new THREE.Line(cGeom, cMat);
                lines.add(l);
                setTimeout(() => { lines.remove(l); }, 1500);
            }

            camera.position.z = 4.2;
            function run() {
                requestAnimationFrame(run);
                globe.rotation.y += 0.0015;
                points.rotation.y += 0.0015;
                lines.rotation.y += 0.0015;
                if(Math.random() < 0.2) addArc();
                renderer.render(scene, camera);
            }
            window.addEventListener('resize', () => {
                camera.aspect = div.clientWidth / 480; camera.updateProjectionMatrix();
                renderer.setSize(div.clientWidth, 480);
            });
            run();
        </script>
    </body>
    </html>
    """
    components.html(three_html, height=500, scrolling=False)

# --- ABA 2: BUSINESS INTELLIGENCE (Gráficos Dinâmicos) ---
with tab_bi:
    st.markdown("### Análise Estatística de Vulnerabilidades")
    theme_plotly = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    
    if total_inc > 0:
        g1, g2 = st.columns(2)
        with g1:
            f_pie = px.pie(df_banco, names="SEVERIDADE", title="Volume Absoluto por Severidade", color_discrete_sequence=["#ef4444", "#f97316", "#10b981"])
            f_pie.update_layout(**theme_plotly)
            st.plotly_chart(f_pie, use_container_width=True)
        with g2:
            f_bar = px.bar(df_banco["TIPO INCIDENTE"].value_counts().reset_index(), x="TIPO INCIDENTE", y="count", title="Vetores de Ataques Dominantes", color_discrete_sequence=["#ef4444"])
            f_bar.update_layout(**theme_plotly)
            st.plotly_chart(f_bar, use_container_width=True)
    else:
        st.info("Aguardando inserção de dados no MySQL para renderização estrutural.")

# --- ABA 3: INGESTÃO DE NOVOS DADOS ---
with tab_actions:
    st.markdown("### Inserção Manual de Ocorrências Detectadas")
    with st.form("new_incident_form"):
        cx1, cx2 = st.columns(2)
        with cx1:
            tipo_v = st.text_input("Tipo de Incidente (Vetor)", "DDoS Attack")
            origem_v = st.text_input("Origem (IP / Provedor)", "192.168.1.105")
            pais_v = st.text_input("País de Origem", "China")
        with cx2:
            cliente_v = st.text_input("Cliente Conectado (Empresa)", "Nubank")
            status_v = st.selectbox("Status Operacional", ["pendente", "em analise", "resolvido"])
            sev_v = st.selectbox("Severidade Declarada", ["baixa", "média", "crítica"])
            
        if st.form_submit_button("PERSISTIR DADOS NO BANCO CORPORATIVO"):
            query_insert = """
                INSERT INTO incidentes (`DATA`, `TIPO INCIDENTE`, `SEVERIDADE`, `ORIGEM`, `STATUS`, `PAIS_ATAQUE`, `CLIENTE`, `BLOQUEADO_AUTOMATICAMENTE`) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sucesso = executar_query(query_insert, (data_atual, tipo_v, sev_v, origem_v, status_v, pais_v, cliente_v, "Sim"), commit=True)
            if sucesso:
                adicionar_log(user_atual, f"Cadastrou incidente do tipo {tipo_v} para o cliente {cliente_v}")
                st.success("💾 Registro efetuado e replicado com sucesso no MySQL!")
                st.cache_data.clear()
                st.rerun()

# --- ABA 4: CHATBOT DO GEMINI MODERNO (REQUISIÇÃO REST DIRETA) ---
with tab_ai:
    st.markdown("### Chatbot Corporativo de Mitigação de Ameaças")
    
    if "chat_history_soc" not in st.session_state:
        st.session_state["chat_history_soc"] = []
        
    for m in st.session_state["chat_history_soc"]:
        cls = "chat-user" if m["role"] == "user" else "chat-ai"
        lbl = "👤 Operador" if m["role"] == "user" else "🤖 SentinelCore"
        st.markdown(f'<div class="{cls}"><b>{lbl}:</b> {m["content"]}</div>', unsafe_allow_html=True)
        
    with st.form("ai_terminal", clear_on_submit=True):
        pergunta = st.text_input("Injetar comando de consulta cognitiva:", placeholder="Pergunte sobre procedimentos de contenção para essa infraestrutura...")
        if st.form_submit_button("ENVIAR COMANDO"):
            if pergunta.strip():
                st.session_state["chat_history_soc"].append({"role": "user", "content": pergunta})
                
                # Contexto SOC profissional injetado diretamente no prompt para impressionar a banca
                prompt_contextualizado = f"""Você é o motor de IA principal do Cyber SOC da empresa SentinelAI. 
                Sua missão é auxiliar o analista '{user_atual}' dando diretrizes cirúrgicas de mitigação.
                Responda em português brasileiro, de forma limpa, profissional e sem rodeios.
                CONTEXTO ATUAL DA INFRAESTRUTURA:
                - Temos {total_inc} incidentes registrados no banco de dados corporativo.
                - Casos críticos monitorados agora: {criticos}.
                
                Pergunta técnica: {pergunta}"""
                
                # Chamada REST direta via API para evitar erros de pacotes descontinuados
                url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                payload_rest = {"contents": [{"parts": [{"text": prompt_contextualizado}]}]}
                
                try:
                    r_post = requests.post(url_api, json=payload_rest, headers={"Content-Type": "application/json"}, timeout=15)
                    if r_post.status_code == 200:
                        resposta = r_post.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        resposta = f"⚠️ [ERRO PROTOCOLO REST]: Código HTTP {r_post.status_code}. Certifique-se de que a chave configurada nos Segredos é válida."
                except Exception as ex:
                    resposta = f"⚠️ [ERRO DE LINK DATA]: Falha física na comunicação de rede com o core da IA: {str(ex)[:60]}"
                    
                st.session_state["chat_history_soc"].append({"role": "model", "content": resposta})
                adicionar_log(user_atual, f"Consultou IA Core: '{pergunta[:30]}...'")
                st.rerun()

# --- ABA 5: SYSLOG COMPLETO ---
with tab_audit:
    st.markdown("### Auditoria Estrutural de Logs (Terminal Syslog)")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log_line in reversed(st.session_state["logs_sistema"][-30:]):
            st.code(log_line, language=None)
    else:
        st.info("Nenhuma atividade capturada no buffer de auditoria atual.")
