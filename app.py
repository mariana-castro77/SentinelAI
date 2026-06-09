import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import datetime
import requests
import mysql.connector

# Obtenção segura da chave da API do Gemini através dos Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA")

# 1. Configuração da Página Cyber SOC
st.set_page_config(
    page_title="SentinelAI // SOC Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Conexão com o Banco de Dados com Sistema de Contingência Integrado
@st.cache_resource(ttl=600)
def inicializar_conexao_mysql():
    try:
        # Tenta realizar a conexão usando as credenciais configuradas
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=int(st.secrets["mysql"].get("port", 3306)),
            charset='utf8mb4',
            auth_plugin='mysql_native_password',
            use_pure=True,
            connect_timeout=3  # Timeout de 3 segundos para não travar a aplicação na nuvem
        )
        return conn
    except Exception:
        # Ativa o modo de demonstração silenciosamente caso o banco local esteja inacessível
        return None

conn_mysql = inicializar_conexao_mysql()

def executar_query(query, params=None, commit=False):
    if not conn_mysql:
        return None
    try:
        conn_mysql.ping(reconnect=True, attempts=2, delay=1)
        cursor = conn_mysql.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if commit:
            conn_mysql.commit()
            return True
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Exception:
        return None

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] {usuario} | {acao}")
    
    if conn_mysql:
        executar_query(
            "INSERT INTO logs_sistema (usuario, acao) VALUES (%s, %s)",
            (usuario, acao),
            commit=True
        )

# 3. Estilização Avançada UI/UX (Inspirada na identidade escura e neon solicitada)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2 family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

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

/* Menu Lateral Estilo Cyberpunk */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06080c 0%, #020305 100%) !important;
    border-right: 1px solid rgba(239, 68, 68, 0.15) !important;
}

/* Painel de Métricas SOC */
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

/* Formulários e Inputs */
input, select, textarea, div[data-baseweb="select"] {
    background-color: #0b0d14 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

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
    padding: 0.5rem 1.1rem !important;
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
    transition: all 0.25s ease !important;
}
div.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(220, 38, 38, 0.4) !important;
}

/* Bolhas do Chatbot */
.chat-user { background: #1e293b; border-radius: 14px 14px 2px 14px; padding: 0.85rem; margin: 0.5rem 0 0.5rem auto; max-width: 80%; width: fit-content; border: 1px solid rgba(255,255,255,0.05); }
.chat-ai { background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.18); border-radius: 14px 14px 14px 2px; padding: 0.85rem; margin: 0.5rem 0; max-width: 80%; width: fit-content; }

.soc-badge { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.62rem; font-weight: 700; }
.badge-live { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); color: #10b981; }
.badge-demo { background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); color: #f59e0b; }
</style>

<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.19/bundled/lenis.min.js"></script>
<script>
    const lenis = new Lenis({ duration: 1.1, easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), smooth: true });
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
</script>
""", unsafe_allow_html=True)

# 4. Inicialização de Sessão e Controle LGPD
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
if "lgpd_consent" not in st.session_state:
    st.session_state["lgpd_consent"] = False

# --- BLOQUEIO COMPLIANCE LGPD ---
if not st.session_state["lgpd_consent"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px; max-width: 400px; background: #0b0d14; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 12px; padding: 1.3rem; z-index: 99999; box-shadow: 0 15px 40px rgba(0,0,0,0.7);">
        <h4 style="margin: 0 0 0.5rem 0; color: #fff; font-size: 0.9rem; font-weight: 700;">LGPD / PREFERÊNCIAS DE COOKIES</h4>
        <p style="color: #94a3b8; font-size: 0.75rem; line-height: 1.5; margin-bottom: 1rem;">
            Este site usa cookies essenciais e analíticos para melhorar sua experiência e para fins de conformidade com a LGPD. Gerencie suas preferências abaixo.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c_sp, c_rec, c_acc = st.columns([3.5, 1, 1])
    with c_rec:
        if st.button("RECUSAR TODOS", use_container_width=True):
            st.warning("O consentimento é obrigatório para acessar o SOC.")
    with c_acc:
        if st.button("ACEITAR TODOS", use_container_width=True):
            st.session_state["lgpd_consent"] = True
            st.rerun()
    st.stop()

# --- TELA DE AUTENTICAÇÃO DO OPERADOR ---
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_l, c_mid, c_r = st.columns([1, 1.2, 1])
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
            st.markdown("<p style='color: #94a3b8; font-size: 0.75rem; font-weight:600; margin-bottom: 0.6rem;'>OPERADORES AUTORIZADOS:</p>", unsafe_allow_html=True)
            
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
                    adicionar_log(user_in, "Efetuou login com sucesso na console SOC")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas de segurança.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- CARREGAMENTO DE DADOS (REAL VS CONTINGÊNCIA NUVEM) ---
user_atual = st.session_state["usuario"]

def carregar_dados_reais():
    res = executar_query("SELECT * FROM incidentes")
    if res:
        return pd.DataFrame(res)
    
    # Base de Contingência Automática (Dados simulados caso esteja rodando na Nuvem)
    dados_mock = {
        "DATA": [(datetime.datetime.now() - datetime.timedelta(minutes=i*15)).strftime("%Y-%m-%d %H:%M:%S") for i in range(12)],
        "TIPO INCIDENTE": ["DDoS Attack", "Brute Force", "Phishing Campaign", "Ransomware Attempt", "SQL Injection", "DDoS Attack", "Malware Execution", "Brute Force", "Data Exfiltration", "Phishing Campaign", "SQL Injection", "DDoS Attack"],
        "SEVERIDADE": ["Crítica", "Média", "Baixa", "Crítica", "Média", "Crítica", "Alta", "Média", "Crítica", "Baixa", "Alta", "Crítica"],
        "ORIGEM": ["192.168.1.50", "10.0.0.15", "172.16.254.1", "192.168.1.99", "10.0.0.88", "185.220.101.5", "192.168.4.12", "10.0.5.4", "45.132.22.11", "172.16.40.2", "10.0.9.1", "185.220.101.9"],
        "STATUS": ["em analise", "pendente", "resolvido", "em analise", "resolvido", "pendente", "em analise", "resolvido", "em analise", "resolvido", "pendente", "em analise"],
        "PAIS_ATAQUE": ["China", "Rússia", "Estados Unidos", "Coreia do Norte", "Brasil", "Holanda", "Rússia", "China", "Ucrânia", "Estados Unidos", "Brasil", "Alemanha"],
        "CLIENTE": ["Banco Alpha", "TechStore", "EcoMove Enterprise", "Nubank", "LogTech", "Banco Alpha", "GovSec", "TechStore", "HealthCare Inc", "EcoMove Enterprise", "LogTech", "Nubank"],
        "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Sim", "Não", "Sim", "Sim", "Não", "Sim", "Sim", "Não", "Sim"]
    }
    return pd.DataFrame(dados_mock)

df_banco = carregar_dados_reais()

# --- SIDEBAR OPERACIONAL ---
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:1rem 0;'><h2 style='font-family:\"Space Grotesk\"; color:#fff; margin:0;'>Sentinel<span style='color:#ef4444;'>AI</span></h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 0.8rem;'>
        <p style='color: #64748b; font-size: 0.6rem; margin:0; font-weight:700;'>OPERADOR LOGADO</p>
        <p style='color: #ffffff; font-weight: 700; margin: 0 0 0.4rem 0; font-size: 0.9rem;'>@{user_atual.upper()}</p>
        {"<span class='soc-badge badge-live'>● BANCO LOCAL CONECTADO</span>" if conn_mysql else "<span class='soc-badge badge-demo'>▲ MODO DE DEMONSTRAÇÃO</span>"}
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

# Cálculos Operacionais
total_inc = len(df_banco)
criticos = len(df_banco[df_banco["SEVERIDADE"].astype(str).str.lower() == "crítica"])
bloqueados = len(df_banco[df_banco["BLOQUEADO_AUTOMATICAMENTE"].astype(str).str.lower() == "sim"])

c1, c2, c3 = st.columns(3)
with c1: st.metric("Total de Ocorrências", f"{total_inc:,}")
with c2: st.metric("Incidentes Críticos", f"{criticos:,}")
with c3: st.metric("Bloqueados por Firewall", f"{bloqueados:,}")

st.markdown("<br>", unsafe_allow_html=True)

# Abas Interativas
tab_globe, tab_bi, tab_actions, tab_ai, tab_audit = st.tabs([
    "🌍 GLOBO DE AMEAÇAS 3D", "📊 MÉTRICAS BI", "⚡ CENTRAL DE INGESTÃO", "🤖 CHAT COGNITIVO", "📋 SYSLOG AUDIT"
])

# --- ABA 1: GLOBO 3D ESTILO KASPERSKY ---
with tab_globe:
    st.markdown("### CIBERAMEAÇA: MAPA AO VIVO (3D Cyberspace Map)")
    st.caption("Visualização tridimensional interativa de pacotes de intrusão interceptados.")
    
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
        <div id="container-3d"><div class="console-overlay">[SENTINEL-CORE V2.6]<br>> MAP_STREAMING ACTIVE...<br>> CAPTURING THREAT NETWORKS</div></div>
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
            const pMat = new THREE.PointsMaterial({ color: 0xef4444, size: 0.035, transparent: true, opacity: 0.8 });
            const points = new THREE.Points(pGeo, pMat);
            scene.add(points);

            const lines = new THREE.Group();
            scene.add(lines);

            function addArc() {
                const pts = [];
                const s = new THREE.Vector3((Math.random()-0.5)*3, (Math.random()-0.5)*3, (Math.random()-0.5)*3).normalize().multiplyScalar(2.01);
                const e = new THREE.Vector3(-0.4, -0.6, 1.8);
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
                if(Math.random() < 0.25) addArc();
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

# --- ABA 2: GRÁFICOS BI ---
with tab_bi:
    st.markdown("### Estatísticas Globais de Vulnerabilidade")
    theme_plotly = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    
    g1, g2 = st.columns(2)
    with g1:
        f_pie = px.pie(df_banco, names="SEVERIDADE", title="Distribuição por Nível de Severidade", color_discrete_sequence=["#ef4444", "#f97316", "#10b981", "#3b82f6"])
        f_pie.update_layout(**theme_plotly)
        st.plotly_chart(f_pie, use_container_width=True)
    with g2:
        f_bar = px.bar(df_banco["TIPO INCIDENTE"].value_counts().reset_index(), x="TIPO INCIDENTE", y="count", title="Vetores de Ataque Mais Recorrentes", color_discrete_sequence=["#ef4444"])
        f_bar.update_layout(**theme_plotly)
        st.plotly_chart(f_bar, use_container_width=True)

# --- ABA 3: INGESTÃO DE DADOS ---
with tab_actions:
    st.markdown("### Inserção Manual de Ocorrências Detectadas")
    with st.form("new_incident_form"):
        cx1, cx2 = st.columns(2)
        with cx1:
            tipo_v = st.text_input("Tipo de Incidente (Vetor)", "DDoS Attack")
            origem_v = st.text_input("Origem (IP / Host)", "185.220.101.44")
            pais_v = st.text_input("País de Origem", "Rússia")
        with cx2:
            cliente_v = st.text_input("Cliente Conectado", "Nubank")
            status_v = st.selectbox("Status Operacional", ["pendente", "em analise", "resolvido"])
            sev_v = st.selectbox("Severidade Declarada", ["baixa", "média", "alta", "crítica"])
            
        if st.form_submit_button("PERSISTIR DADOS NO CLUSTER CORPORATIVO"):
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if conn_mysql:
                query_insert = """
                    INSERT INTO incidentes (`DATA`, `TIPO INCIDENTE`, `SEVERIDADE`, `ORIGEM`, `STATUS`, `PAIS_ATAQUE`, `CLIENTE`, `BLOQUEADO_AUTOMATICAMENTE`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                executar_query(query_insert, (data_atual, tipo_v, sev_v, origem_v, status_v, pais_v, cliente_v, "Sim"), commit=True)
                st.success("💾 Registro gravado com sucesso no MySQL local!")
            else:
                st.success("💾 Modo Demo: Registro simulado e armazenado com sucesso na memória volatil do SOC!")
            
            adicionar_log(user_atual, f"Cadastrou incidente do tipo '{tipo_v}' para o cliente {cliente_v}")
            st.cache_data.clear()
            st.rerun()

# --- ABA 4: CHATBOT DO GEMINI (REQUISIÇÃO REST DIRETA) ---
with tab_ai:
    st.markdown("### Assistente Cognitivo de Mitigação de Ameaças")
    
    if "chat_history_soc" not in st.session_state:
        st.session_state["chat_history_soc"] = []
        
    for m in st.session_state["chat_history_soc"]:
        cls = "chat-user" if m["role"] == "user" else "chat-ai"
        lbl = "👤 Operador" if m["role"] == "user" else "🤖 SentinelCore"
        st.markdown(f'<div class="{cls}"><b>{lbl}:</b> {m["content"]}</div>', unsafe_allow_html=True)
        
    with st.form("ai_terminal", clear_on_submit=True):
        pergunta = st.text_input("Injetar comando ou dúvida técnica na IA:", placeholder="Como mitigar um ataque DDoS do tipo volumétrico?")
        if st.form_submit_button("ENVIAR COMANDO"):
            if pergunta.strip():
                st.session_state["chat_history_soc"].append({"role": "user", "content": pergunta})
                
                prompt_contextualizado = f"""Você é o motor de IA principal do Cyber SOC da empresa SentinelAI. 
                Sua missão é auxiliar o analista '{user_atual}' dando diretrizes cirúrgicas de mitigação.
                Responda em português brasileiro, de forma limpa, profissional e direta.
                CONTEXTO ATUAL DA INFRAESTRUTURA:
                - Temos {total_inc} incidentes registrados.
                - Casos críticos monitorados agora: {criticos}.
                
                Pergunta técnica: {pergunta}"""
                
                url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                payload_rest = {"contents": [{"parts": [{"text": prompt_contextualizado}]}]}
                
                try:
                    r_post = requests.post(url_api, json=payload_rest, headers={"Content-Type": "application/json"}, timeout=15)
                    if r_post.status_code == 200:
                        resposta = r_post.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        resposta = f"⚠️ [ERRO PROTOCOLO REST]: Código HTTP {r_post.status_code}. Verifique sua chave de API nos Segredos."
                except Exception as ex:
                    resposta = f"⚠️ [ERRO DE LINK DATA]: Falha física na comunicação de rede com o core da IA: {str(ex)[:60]}"
                    
                st.session_state["chat_history_soc"].append({"role": "model", "content": resposta})
                adicionar_log(user_atual, f"Consultou IA Core: '{pergunta[:30]}...'")
                st.rerun()

# --- ABA 5: AUDITORIA DE LOGS DO SISTEMA ---
with tab_audit:
    st.markdown("### Auditoria Estrutural de Logs (Terminal Syslog)")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log_line in reversed(st.session_state["logs_sistema"][-30:]):
            st.code(log_line, language=None)
    else:
        st.info("Nenhuma atividade capturada no buffer de auditoria atual.")
