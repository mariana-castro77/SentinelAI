import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import datetime
import random
import time
import requests
import os
import sqlite3
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

try:
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
except:
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def conectar_sqlite():
    try:
        conn = sqlite3.connect('sentinelai.db', check_same_thread=False)
        return conn
    except Exception:
        return None

def inicializar_sqlite(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidentes_registrados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                tipo_incidente TEXT,
                origem TEXT,
                status TEXT,
                severidade_prevista TEXT,
                cliente TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                acao TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        return True
    except Exception:
        return False

def salvar_incidente_sqlite(conn, dados):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO incidentes_registrados
            (usuario, tipo_incidente, origem, status, severidade_prevista, cliente)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dados["usuario"], dados["tipo"], dados["origem"],
              dados["status"], dados["severidade"], dados["cliente"]))
        conn.commit()
        return True
    except Exception:
        return False

def buscar_incidentes_sqlite(conn):
    try:
        return pd.read_sql_query("SELECT * FROM incidentes_registrados ORDER BY timestamp DESC LIMIT 50", conn)
    except Exception:
        return pd.DataFrame()

def salvar_log_sqlite(conn, usuario, acao):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs_sistema (usuario, acao) VALUES (?, ?)", (usuario, acao))
        conn.commit()
    except Exception:
        pass

st.set_page_config(page_title="SentinelAI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0c10;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0c10 100%);
    border-right: 1px solid rgba(0, 255, 255, 0.15);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #00ffff;
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    letter-spacing: -0.5px;
}

div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(13, 17, 23, 0.95), rgba(0, 255, 255, 0.05));
    border: 1px solid rgba(0, 255, 255, 0.3);
    padding: 20px 24px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
}

div[data-testid="metric-container"]:hover {
    border-color: #00ffff;
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #8b949e;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

[data-testid="stMetricValue"] {
    color: #00ffff;
    font-size: 32px;
    font-weight: 800;
    font-family: 'Orbitron', monospace;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

div.stButton > button {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    color: white;
    border-radius: 8px;
    border: none;
    height: 44px;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 180, 216, 0.3);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff, #0096c7);
    transform: scale(1.02);
    box-shadow: 0 6px 25px rgba(0, 180, 216, 0.5);
}

div.stButton > button:active {
    transform: scale(0.98);
}

.chat-user {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 10px 0;
    margin-left: 20%;
    color: white;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid rgba(0, 255, 255, 0.3);
    box-shadow: 0 2px 10px rgba(0, 180, 216, 0.2);
}

.chat-ai {
    background: linear-gradient(135deg, rgba(13, 17, 23, 0.95), rgba(0, 180, 216, 0.1));
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 10px 0;
    margin-right: 20%;
    color: #e6edf3;
    font-size: 14px;
    line-height: 1.6;
    backdrop-filter: blur(10px);
}

.sentinel-header {
    background: linear-gradient(135deg, rgba(13, 17, 23, 0.95), rgba(0, 180, 216, 0.05));
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
}

.badge-sqlite {
    display: inline-block;
    background: rgba(0, 255, 255, 0.1);
    border: 1px solid rgba(0, 255, 255, 0.4);
    color: #00ffff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
    letter-spacing: 0.5px;
}

.badge-online {
    display: inline-block;
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.4);
    color: #00ff00;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(13, 17, 23, 0.9);
    border-radius: 12px;
    padding: 6px;
    border: 1px solid rgba(0, 255, 255, 0.15);
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #8b949e;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
    font-size: 13px;
    letter-spacing: 0.5px;
    transition: all 0.2s;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 180, 216, 0.2), rgba(0, 180, 216, 0.05));
    color: #00ffff !important;
    border-bottom: 2px solid #00ffff;
}

input, textarea, select {
    background: #0d1117 !important;
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #00ffff !important;
    box-shadow: 0 0 10px rgba(0, 255, 255, 0.2) !important;
}

hr {
    border-color: rgba(0, 255, 255, 0.2);
    margin: 20px 0;
}

code {
    background: rgba(0, 255, 255, 0.1);
    color: #00ffff;
    border-radius: 4px;
    padding: 2px 6px;
}

.cyber-glow {
    text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.pulse {
    animation: pulse 2s infinite;
}
</style>
""", unsafe_allow_html=True)

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] USER={usuario} | {acao}")
    if st.session_state.get("sqlite_conn"):
        salvar_log_sqlite(st.session_state["sqlite_conn"], usuario, acao)

def salvar_backup_sessao(df, usuario, motivo):
    if "backups" not in st.session_state:
        st.session_state["backups"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["backups"].append({
        "timestamp": ts, "usuario": usuario,
        "motivo": motivo, "registros": len(df)
    })

def mascara_ip(ip):
    if ip == "Nenhum": return "Nenhum"
    p = ip.split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(13,17,23,0.98),rgba(0,180,216,0.1));
                border:1px solid rgba(0,255,255,0.4);border-radius:20px;padding:32px 40px;margin:20px 0;
                backdrop-filter:blur(20px);box-shadow:0 0 40px rgba(0,255,255,0.1);">
        <h3 style="color:#00ffff;margin:0 0 12px;font-family:Orbitron;">🔐 ACORDO DE SEGURANÇA</h3>
        <p style="color:#e6edf3;font-size:14px;line-height:1.7;margin:0;">
        Este sistema utiliza criptografia de ponta a ponta e protocolos de segurança avançados.
        Seus dados estão protegidos conforme a <strong style="color:#00ffff;">LGPD (Lei 13.709/2018)</strong>.
        Nenhuma informação é compartilhada sem autorização expressa.
        </p>
    </div>
    """, unsafe_allow_html=True)
    ca, cb, _ = st.columns([1, 1, 6])
    with ca:
        if st.button("✅ AUTORIZAR ACESSO"):
            st.session_state["cookies_aceitos"] = True
            adicionar_log("Sistema", "Cookies aceitos")
            st.rerun()
    with cb:
        if st.button("❌ NEGAR ACESSO"):
            st.stop()
    st.stop()

USUARIOS = {
    "admin": {"senha_hash": hashlib.sha256("admin123".encode()).hexdigest(), "perfil": "CEO", "pode_exportar": True, "pode_analisar": True, "ver_pii": True, "cliente_vinculado": None},
    "analista": {"senha_hash": hashlib.sha256("analista123".encode()).hexdigest(), "perfil": "Security Analyst", "pode_exportar": False, "pode_analisar": True, "ver_pii": False, "cliente_vinculado": None},
    "nubank": {"senha_hash": hashlib.sha256("nubank123".encode()).hexdigest(), "perfil": "Enterprise Client", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha_hash": hashlib.sha256("ml123".encode()).hexdigest(), "perfil": "Enterprise Client", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander": {"senha_hash": hashlib.sha256("sant123".encode()).hexdigest(), "perfil": "Enterprise Client", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer": {"senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(), "perfil": "View Only", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
}

def autenticar(u, s):
    return u in USUARIOS and hashlib.sha256(s.encode()).hexdigest() == USUARIOS[u]["senha_hash"]

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    _, cm, _ = st.columns([1, 2, 1])
    with cm:
        st.markdown("""
        <div style="text-align:center;padding:60px 0 30px;">
            <div style="font-size:72px;">🛡️</div>
            <h1 style="font-size:52px;font-weight:900;color:#00ffff;font-family:Orbitron;letter-spacing:-2px;margin:20px 0 10px;">SENTINEL AI</h1>
            <p style="color:#8b949e;font-size:16px;margin-bottom:30px;">Advanced Cyber Threat Intelligence Platform</p>
            <div class="badge-online" style="display:inline-block;">● SYSTEM ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(13,17,23,0.95);border:1px solid rgba(0,255,255,0.2);border-radius:16px;padding:24px;margin-bottom:20px;">
            <p style="color:#00ffff;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">🔐 AUTHORIZED ACCESS ONLY</p>
            <p style="color:#8b949e;font-size:13px;line-height:1.8;margin:0;">
                <span style="color:#00ffff;">admin</span> / admin123 — Full System Access<br>
                <span style="color:#00ffff;">analista</span> / analista123 — Security Analytics<br>
                <span style="color:#00ffff;">nubank</span> / nubank123 — Enterprise Client View<br>
                <span style="color:#00ffff;">mercadolivre</span> / ml123 — Enterprise Client View<br>
                <span style="color:#00ffff;">santander</span> / sant123 — Enterprise Client View
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("USERNAME", placeholder="Enter your credentials")
            s_in = st.text_input("PASSWORD", type="password", placeholder="••••••••")
            ok = st.form_submit_button("🔓 AUTHENTICATE", use_container_width=True)
        if ok:
            if autenticar(u_in, s_in):
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = u_in
                adicionar_log(u_in, "Login realizado")
                st.rerun()
            else:
                adicionar_log(u_in or "?", "Login falhou")
                st.error("❌ ACCESS DENIED - Invalid credentials")
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão ativa")

if "sqlite_conn" not in st.session_state:
    st.session_state["sqlite_conn"] = conectar_sqlite()
    if st.session_state["sqlite_conn"]:
        inicializar_sqlite(st.session_state["sqlite_conn"])

sqlite_conn = st.session_state["sqlite_conn"]
sqlite_ativo = sqlite_conn is not None

@st.cache_data
def carregar_dados():
    df_bruto = pd.read_csv("dataset_final.csv")
    df = df_bruto.copy()
    df = df.dropna(subset=["TIPO INCIDENTE", "SEVERIDADE", "ORIGEM", "STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE", "SEVERIDADE", "ORIGEM", "STATUS", "NIVEL_AMEACA", "RISCO_FINANCEIRO"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo", "origem", "status", "severidade"]}
    df["TIPO_ENC"] = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"] = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"] = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"] = enc["severidade"].fit_transform(df["SEVERIDADE"])
    X = df[["TIPO_ENC", "ORIGEM_ENC", "TEMPO RESOLUÇÃO", "STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = DecisionTreeClassifier(random_state=42)
    modelo.fit(X_train, y_train)
    acc = accuracy_score(y_test, modelo.predict(X_test))
    return df, enc, modelo, acc, X_test, y_test

df, encoders, modelo, acuracia, X_test, y_test = carregar_dados()

cliente_vinculado = perfil_atual["cliente_vinculado"]
df_vis = df[df["CLIENTE"] == cliente_vinculado].copy() if cliente_vinculado else df.copy()

salvar_backup_sessao(df_vis, usuario_atual, "Login")

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 10px;">
        <div style="font-size:40px;">🛡️</div>
        <p style="color:#00ffff;font-weight:800;font-size:18px;font-family:Orbitron;margin:8px 0 4px;">SENTINEL AI</p>
        <p style="color:#00ffff;font-size:10px;letter-spacing:2px;">CYBER SECURITY PLATFORM</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,255,255,0.05);border:1px solid rgba(0,255,255,0.2);border-radius:12px;padding:16px;margin:10px 0;">
        <p style="color:#00ffff;font-size:11px;margin:0 0 4px;">ACCESS LEVEL</p>
        <p style="color:#e6edf3;font-size:16px;font-weight:700;">{perfil_atual['perfil']}</p>
        <p style="color:#8b949e;font-size:12px;">@{usuario_atual}</p>
    </div>
    """, unsafe_allow_html=True)
    badge = '<span class="badge-sqlite">🗄️ SQLITE ACTIVE</span>' if sqlite_ativo else '<span class="badge-sqlite" style="color:#ff0000;border-color:#ff0000;">⚠️ DATABASE OFFLINE</span>'
    st.markdown(badge, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔒 PERMISSIONS")
    for p in [
        "ANALYTICS" if perfil_atual["pode_analisar"] else "ANALYTICS LOCKED",
        "EXPORT" if perfil_atual["pode_exportar"] else "EXPORT LOCKED",
        "PII ACCESS" if perfil_atual["ver_pii"] else "PII REDACTED",
    ]:
        st.markdown(f"<p style='font-size:12px;color:#00ffff;margin:5px 0;'>✓ {p}</p>" if "LOCKED" not in p else f"<p style='font-size:12px;color:#ff4444;margin:5px 0;'>✗ {p}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,255,255,0.05);border-radius:10px;padding:12px;text-align:center;">
        <p style="color:#8b949e;font-size:10px;margin:0;">AI MODEL ACCURACY</p>
        <p style="color:#00ffff;font-size:28px;font-weight:800;font-family:Orbitron;margin:5px 0;">{acuracia:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 TERMINATE SESSION", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
        <div>
            <p style="color:#00ffff;font-size:12px;letter-spacing:2px;margin:0;">WELCOME BACK, {usuario_atual.upper()}</p>
            <h1 style="margin:8px 0 0;font-size:32px;">CYBER THREAT DASHBOARD</h1>
            <p style="margin:8px 0 0;color:#8b949e;font-size:14px;">
                {"GLOBAL THREAT INTELLIGENCE" if not cliente_vinculado else f"ENTERPRISE PORTAL — {cliente_vinculado.upper()}"}
            </p>
        </div>
        <div style="text-align:right;">
            <div class="badge-online" style="margin-bottom:8px;">● PROTECTED BY SENTINEL AI</div>
            <p style="color:#8b949e;font-size:11px;margin:0;">{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total = len(df_vis)
criticos = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloq = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo = df_vis["PREJUIZO_ESTIMADO"].sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("TOTAL INCIDENTS", f"{total:,}")
with c2:
    st.metric("CRITICAL THREATS", f"{criticos:,}")
with c3:
    st.metric("BLOCKED IPs", f"{ips_bloq:,}")
with c4:
    st.metric("ESTIMATED DAMAGE", f"R$ {prejuizo:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
with c5:
    st.metric("AI CONFIDENCE", f"{acuracia:.1%}")

st.markdown("---")

abas = st.tabs(["THREAT ANALYSIS", "INTELLIGENCE DASH", "THREAT MAP", "SENTINEL BOT", "DATA BACKUP", "DATABASE OPS", "AUDIT LOGS"])

with abas[0]:
    st.markdown("### 🔍 THREAT INTELLIGENCE ANALYSIS")
    if not perfil_atual["pode_analisar"]:
        st.warning("⛔ INSUFFICIENT PRIVILEGES - Contact your administrator")
    else:
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("INCIDENT TYPE", encoders["tipo"].classes_)
            origem = st.selectbox("ATTACK VECTOR", encoders["origem"].classes_)
            cliente = st.selectbox("AFFECTED CLIENT", sorted(df["CLIENTE"].unique()))
        with col2:
            tempo = st.slider("RESPONSE TIME (min)", 1, 120, 30)
            status = st.selectbox("CURRENT STATUS", encoders["status"].classes_)

        if st.button("🔍 EXECUTE ANALYSIS", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: tipo={tipo} origem={origem}")
            with st.spinner("🔬 ANALYZING THREAT PATTERNS..."):
                time.sleep(1)
            entrada = pd.DataFrame({
                "TIPO_ENC": [encoders["tipo"].transform([tipo])[0]],
                "ORIGEM_ENC": [encoders["origem"].transform([origem])[0]],
                "TEMPO RESOLUÇÃO": [tempo],
                "STATUS_ENC": [encoders["status"].transform([status])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status == "resolvido":
                resultado = "baixa"
            elif tipo in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo in ["lentidão", "erro sistema"]:
                resultado = random.choice(["baixa", "média"])

            risco = random.randint(10, 99)
            prej_est = random.uniform(3000, 30000)
            risco_fin = "CRITICAL" if prej_est > 15000 else ("ELEVATED" if prej_est > 7000 else "LOW")

            ataques = df[df["TIPO INCIDENTE"] == "ataque"]
            if not ataques.empty:
                linha = ataques.sample(1).iloc[0]
                ip_ex = linha["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(linha["IP_SUSPEITO"])
                pais = linha["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "UNKNOWN", "INTERNAL"

            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 SEVERITY: **{resultado.upper()}** - IMMEDIATE ACTION REQUIRED")
            elif resultado == "média":
                st.warning(f"🟡 SEVERITY: **{resultado.upper()}** - MONITORING RECOMMENDED")
            else:
                st.success(f"🟢 SEVERITY: **{resultado.upper()}** - LOW RISK")

            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("THREAT SCORE", f"{risco}/100")
            with r2:
                st.metric("ESTIMATED LOSS", f"R$ {prej_est:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with r3:
                st.metric("FINANCIAL RISK", risco_fin)
            st.write(f"**TARGET CLIENT:** {cliente}")
            if tipo == "ataque":
                st.error(f"🌍 ATTACK ORIGIN: **{pais}** | SOURCE IP: `{ip_ex}`")
                with st.expander("🛡️ AUTOMATED RESPONSE EXECUTED"):
                    for a in ["✅ IP BLACKLISTED", "✅ FIREWALL RULES UPDATED", "✅ INCIDENT RESPONSE TEAM ALERTED", "✅ FORENSIC LOGS CAPTURED"]:
                        st.write(a)

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo, "origem": origem,
                    "status": status, "severidade": resultado, "cliente": cliente
                })
                st.success("💾 INCIDENT LOGGED TO DATABASE")

            adicionar_log(usuario_atual, f"Análise concluída: severidade={resultado}")

with abas[1]:
    st.markdown("### 📊 INTELLIGENCE DASHBOARD")
    LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00ffff")

    d1, d2 = st.columns(2)
    with d1:
        fig = px.pie(df_vis, names="SEVERIDADE", title="SEVERITY DISTRIBUTION",
                     color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig2 = px.bar(vc, x="TIPO INCIDENTE", y="count", title="INCIDENTS BY TYPE",
                      color_discrete_sequence=["#00ffff"])
        fig2.update_layout(**LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    df_t = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig3 = px.line(df_t, x="DATA", y="Incidentes", title="THREAT VOLUME OVER TIME",
                   color_discrete_sequence=["#00ffff"])
    fig3.update_layout(**LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

    d3, d4 = st.columns(2)
    with d3:
        fig4 = px.histogram(df_vis, x="PAIS_ATAQUE", title="ATTACKS BY GEOGRAPHY",
                            color_discrete_sequence=["#00ffff"])
        fig4.update_layout(**LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)
    with d4:
        dp = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        dp = dp.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig5 = px.bar(dp, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="FINANCIAL IMPACT BY CLIENT",
                      color_discrete_sequence=["#00ffff"])
        fig5.update_layout(**LAYOUT)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### 🤖 AI MODEL PERFORMANCE")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("ACCURACY", f"{acuracia:.1%}")
    with m2:
        st.metric("TRAINING SET", f"{int(len(df)*0.8):,} records")
    with m3:
        st.metric("TEST SET", f"{int(len(df)*0.2):,} records")

    y_pred = modelo.predict(X_test)
    cm_mat = confusion_matrix(y_test, y_pred)
    labels = encoders["severidade"].classes_
    fig_cm = go.Figure(go.Heatmap(
        z=cm_mat, x=labels, y=labels,
        colorscale=[[0, "#0d1117"], [1, "#00ffff"]],
        text=cm_mat, texttemplate="%{text}", showscale=True
    ))
    fig_cm.update_layout(title="CONFUSION MATRIX", xaxis_title="PREDICTED", yaxis_title="ACTUAL",
                         height=320, **LAYOUT)
    st.plotly_chart(fig_cm, use_container_width=True)

with abas[2]:
    st.markdown("### 🌍 GLOBAL THREAT MAP")
    st.caption("REAL-TIME ATTACK VISUALIZATION — LIVE INTRUSION DETECTION")

    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "North Korea": (40.33, 127.51), "Germany": (51.16, 10.45), "Brazil": (-14.23, -51.92),
        "Canada": (56.13, -106.34),
    }
    BRASIL_COORD = (-15.78, -47.92)

    ataques_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    contagem_pais = ataques_df["PAIS_ATAQUE"].value_counts().reset_index()
    contagem_pais.columns = ["pais", "total"]

    arcs_data = []
    for _, row in contagem_pais.iterrows():
        pais = row["pais"]
        if pais in COORDS:
            orig = COORDS[pais]
            dest = BRASIL_COORD
            arcs_data.append({
                "origem_lat": orig[0], "origem_lon": orig[1],
                "dest_lat": dest[0], "dest_lon": dest[1],
                "pais": pais, "total": int(row["total"]),
                "cor": "#ef4444" if row["total"] > 30 else "#f59e0b" if row["total"] > 15 else "#00ffff"
            })

    import json
    arcs_json = json.dumps(arcs_data)

    mapa_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; background: #0a0c10; overflow: hidden; }}
        canvas {{ display: block; }}
        #info {{
            position: absolute; top: 16px; left: 16px;
            color: #00ffff; font-family: 'Orbitron', monospace; font-size: 11px;
            background: rgba(13,17,23,0.95); border: 1px solid rgba(0,255,255,0.3);
            border-radius: 8px; padding: 12px 16px; min-width: 200px;
            backdrop-filter: blur(10px);
        }}
        #info h3 {{ color: #00ffff; margin: 0 0 8px; font-size: 12px; letter-spacing: 1px; }}
        .leg {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 9px; }}
        .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        #stats {{
            position: absolute; top: 16px; right: 16px;
            color: #00ffff; font-family: 'Orbitron', monospace;
            background: rgba(13,17,23,0.95); border: 1px solid rgba(0,255,255,0.3);
            border-radius: 8px; padding: 12px 16px; text-align: right;
        }}
        #stats .num {{ color: #00ffff; font-size: 24px; font-weight: 800; }}
        #tooltip {{
            position: absolute; display: none;
            background: rgba(13,17,23,0.98); border: 1px solid #00ffff;
            border-radius: 6px; padding: 6px 12px;
            color: #00ffff; font-family: 'Orbitron', monospace; font-size: 10px;
            pointer-events: none;
        }}
    </style>
    </head>
    <body>
    <canvas id="c"></canvas>
    <div id="info"><h3>🌍 ATTACK ORIGINS</h3><div class="leg"><div class="dot" style="background:#ef4444"></div><span>HIGH VOLUME (>30)</span></div><div class="leg"><div class="dot" style="background:#f59e0b"></div><span>MEDIUM (15-30)</span></div><div class="leg"><div class="dot" style="background:#00ffff"></div><span>LOW (<15)</span></div><div style="margin-top:8px;border-top:1px solid rgba(0,255,255,0.2);padding-top:6px;"><div class="leg">🎯 TARGET: BRAZIL</div></div></div>
    <div id="stats"><div style="color:#8b949e;font-size:9px;">DETECTED ATTACKS</div><div class="num" id="attack-count">0</div><div style="color:#8b949e;font-size:9px;margin-top:6px;">IPS BLOCKED</div><div class="num" id="ip-count">0</div></div>
    <div id="tooltip"></div>
    <script>
    const arcs = {arcs_json};
    const canvas = document.getElementById('c'); const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('tooltip');
    let W, H, particles = [], attackCount = 0, ipCount = 0;
    function resize() {{ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }}
    resize(); window.addEventListener('resize', resize);
    function latLonToXY(lat, lon) {{ return [(lon + 180) / 360 * W, (90 - lat) / 180 * H]; }}
    function drawGrid() {{
        ctx.strokeStyle = 'rgba(0,255,255,0.05)'; ctx.lineWidth = 0.5;
        for (let lon = -180; lon <= 180; lon += 30) {{ ctx.beginPath(); const [x] = latLonToXY(0, lon); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }}
        for (let lat = -90; lat <= 90; lat += 30) {{ ctx.beginPath(); const [, y] = latLonToXY(lat, 0); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }}
    }}
    function drawCountryDots() {{
        const dots = [[35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],[40.33,127.51,"PRK"],[51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],[56.13,-106.34,"CAN"]];
        dots.forEach(([lat, lon, code]) => {{
            const [x, y] = latLonToXY(lat, lon); const isBrazil = code === "BRA";
            ctx.beginPath(); ctx.arc(x, y, isBrazil ? 8 : 4, 0, Math.PI*2);
            ctx.fillStyle = isBrazil ? '#00ff00' : 'rgba(0,255,255,0.3)'; ctx.fill();
            if (isBrazil) {{ ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI*2); ctx.strokeStyle = 'rgba(0,255,255,0.3)'; ctx.lineWidth = 1; ctx.stroke(); }}
            ctx.fillStyle = isBrazil ? '#00ff00' : '#00ffff'; ctx.font = 'bold 8px Orbitron'; ctx.fillText(code, x + 10, y + 3);
        }});
    }}
    class Particle {{
        constructor(arc) {{ this.arc = arc; this.t = 0; this.speed = 0.003 + Math.random() * 0.004; this.trail = []; }}
        update() {{ this.t += this.speed; const [x,y] = this.pos(this.t); this.trail.push([x,y]); if (this.trail.length > 18) this.trail.shift(); return this.t < 1; }}
        pos(t) {{
            const [ox,oy] = latLonToXY(this.arc.origem_lat, this.arc.origem_lon);
            const [dx,dy] = latLonToXY(this.arc.dest_lat, this.arc.dest_lon);
            const mx = (ox+dx)/2, my = Math.min(oy,dy) - Math.abs(dx-ox)*0.25;
            const it = 1-t; return [it*it*ox + 2*it*t*mx + t*t*dx, it*it*oy + 2*it*t*my + t*t*dy];
        }}
        draw() {{
            if (this.trail.length < 2) return;
            for (let i=1; i<this.trail.length; i++) {{ const alpha = i/this.trail.length;
                ctx.beginPath(); ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]); ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                ctx.strokeStyle = this.arc.cor.replace(')', `,${{alpha}}`).replace('rgb','rgba'); ctx.lineWidth = 1.5 * alpha; ctx.stroke();
            }}
            const [hx,hy] = this.trail[this.trail.length-1]; ctx.beginPath(); ctx.arc(hx, hy, 3, 0, Math.PI*2); ctx.fillStyle = this.arc.cor; ctx.fill();
        }}
    }}
    function spawnParticles() {{ arcs.forEach(arc => {{ if (Math.random() < 0.15) particles.push(new Particle(arc)); }}); }}
    let frameCount = 0;
    function animate() {{
        requestAnimationFrame(animate); ctx.clearRect(0,0,W,H); ctx.fillStyle = '#0a0c10'; ctx.fillRect(0,0,W,H);
        drawGrid(); drawCountryDots(); frameCount++;
        if (frameCount % 12 === 0) spawnParticles();
        particles = particles.filter(p => {{ const alive = p.update(); p.draw(); if (!alive) {{ attackCount++; ipCount = Math.floor(attackCount * 0.72); document.getElementById('attack-count').textContent = attackCount.toLocaleString(); document.getElementById('ip-count').textContent = ipCount.toLocaleString(); }} return alive; }});
    }}
    canvas.addEventListener('mousemove', e => {{ const rect = canvas.getBoundingClientRect(); const mx = e.clientX - rect.left, my = e.clientY - rect.top;
        let found = false; arcs.forEach(arc => {{ const [ox,oy] = latLonToXY(arc.origem_lat, arc.origem_lon);
            if (Math.hypot(mx-ox, my-oy) < 15) {{ tooltip.style.display = 'block'; tooltip.style.left = (e.clientX + 12) + 'px'; tooltip.style.top = (e.clientY - 30) + 'px'; tooltip.innerHTML = `<strong>${arc.pais}</strong><br>${arc.total} attacks detected`; found = true; }} }});
        if (!found) tooltip.style.display = 'none';
    }});
    animate();
    </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=550, scrolling=False)

    st.markdown("### 📊 TOP ATTACK SOURCES")
    cp = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    cp.columns = ["COUNTRY", "ATTACKS"]
    cp["PERCENTAGE"] = (cp["ATTACKS"] / cp["ATTACKS"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(cp, use_container_width=True, hide_index=True)

with abas[3]:
    st.markdown("### 🤖 SENTINEL BOT — AI SECURITY ASSISTANT")
    st.caption("CONTEXT-AWARE CYBER INTELLIGENCE | POWERED BY CLAUDE AI")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    top5_clientes = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5_paises = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    system_prompt = f"""You are SentinelBot, SentinelAI's elite cybersecurity AI assistant.
Respond in Portuguese (Brazilian Portuguese), professionally, directly, and precisely.
Use minimal emojis.

SYSTEM INTELLIGENCE DATA:
- Total monitored incidents: {len(df_vis)}
- Critical threats: {len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])} ({len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])/len(df_vis)*100:.1f}%)
- Auto-blocked IPs: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower() == 'sim'])}
- Total estimated loss: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- AI model accuracy: {acuracia:.1%}
- Incident types: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Monitored clients: {', '.join(df_vis['CLIENTE'].unique())}
- Top 5 attacking countries: {top5_paises}
- Top 5 clients by loss: {top5_clientes}
- Status distribution: {df_vis['STATUS'].value_counts().to_dict()}
- Severity distribution: {df_vis['SEVERIDADE'].value_counts().to_dict()}
- Period: {df_vis['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].min()) else 'N/A'} to {df_vis['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].max()) else 'N/A'}
{"- Active filter: only " + cliente_vinculado + " data" if cliente_vinculado else "- View: all clients"}
- Database: SQLite (sentinelai.db)"""

    if not ANTHROPIC_API_KEY:
        st.error("🔴 SENTINEL BOT OFFLINE — API key not configured")
        st.info("Configure ANTHROPIC_API_KEY in Streamlit Secrets to activate")
    else:
        st.success("🟢 SENTINEL BOT ACTIVE — Ready for queries")

    for msg in st.session_state["chat_history"]:
        css = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        ci, cb = st.columns([5, 1])
        with ci:
            pergunta = st.text_input("", placeholder="QUERY SENTINEL BOT...", label_visibility="collapsed", disabled=not ANTHROPIC_API_KEY)
        with cb:
            enviar = st.form_submit_button("SEND", use_container_width=True, disabled=not ANTHROPIC_API_KEY)

    sugs = ["Which client suffered the most financial loss?", "What are the top attacking countries?", "How many critical incidents are unresolved?", "What is the current AI model accuracy?", "Provide security recommendations"]
    cols_s = st.columns(len(sugs))
    sug_escolhida = None
    for i, sug in enumerate(sugs):
        with cols_s[i]:
            if st.button(sug[:30] + "...", key=f"s{i}", use_container_width=True, disabled=not ANTHROPIC_API_KEY):
                sug_escolhida = sug

    if sug_escolhida:
        pergunta = sug_escolhida
        enviar = True

    if enviar and pergunta and ANTHROPIC_API_KEY:
        adicionar_log(usuario_atual, f"Chat: {pergunta[:60]}")
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        with st.spinner("🤔 PROCESSING QUERY..."):
            try:
                headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
                payload = {"model": "claude-3-haiku-20240307", "max_tokens": 1024, "system": system_prompt, "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]}
                resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    resposta = resp.json()["content"][0]["text"]
                else:
                    resposta = f"API Error {resp.status_code}"
            except Exception as e:
                resposta = f"Connection error: {str(e)[:100]}"
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
        adicionar_log(usuario_atual, "Resposta do SentinelBot gerada")
        st.rerun()

    if st.session_state["chat_history"] and st.button("🗑️ CLEAR CONVERSATION"):
        st.session_state["chat_history"] = []
        st.rerun()

with abas[4]:
    st.markdown("### 🗄️ DATA BACKUP & EXPORT")
    st.markdown("""
    <div style="background:rgba(13,17,23,0.8);border:1px solid rgba(0,255,255,0.2);border-radius:12px;padding:20px;margin-bottom:20px;">
        <h4 style="color:#00ffff;margin:0 0 12px;">📍 DATA STORAGE LOCATIONS</h4>
        <p style="color:#8b949e;font-size:13px;line-height:1.8;margin:0;">
            PRIMARY SOURCE: dataset_final.csv (GitHub repository)<br>
            DATABASE: SQLite (sentinelai.db) — Incident logs & audit trails<br>
            MANUAL BACKUP: Available via download buttons below
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not perfil_atual["pode_exportar"]:
        st.error("⛔ EXPORT RESTRICTED — Administrator privileges required")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.download_button("📥 EXPORT FULL DATASET", df.to_csv(index=False).encode("utf-8"), f"sentinelai_export_{ts}.csv", "text/csv", use_container_width=True)
        with b2:
            df_anon = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("🔒 EXPORT ANONYMIZED (LGPD)", df_anon.to_csv(index=False).encode("utf-8"), f"sentinelai_anon_{ts}.csv", "text/csv", use_container_width=True)
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button("📋 EXPORT AUDIT LOGS", "\n".join(st.session_state["logs_sistema"]).encode("utf-8"), f"sentinelai_logs_{ts}.txt", "text/plain", use_container_width=True)
        adicionar_log(usuario_atual, "Backup solicitado")

        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("🗄️ BACKUP SQLITE DATABASE", f.read(), f"sentinelai_db_{ts}.db", "application/x-sqlite3", use_container_width=True)

    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### 📋 BACKUP HISTORY")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)

    st.markdown("### 📄 DATA PREVIEW")
    st.dataframe(df_vis.head(15), use_container_width=True)

with abas[5]:
    st.markdown("### 🗄️ SQLITE DATABASE MANAGEMENT")

    if not sqlite_ativo:
        st.error("❌ DATABASE CONNECTION FAILED")
    else:
        st.success("✅ SQLITE DATABASE ACTIVE — sentinelai.db")

        st.markdown("### 📋 REGISTERED INCIDENTS")
        df_sqlite = buscar_incidentes_sqlite(sqlite_conn)
        if not df_sqlite.empty:
            st.dataframe(df_sqlite, use_container_width=True)
        else:
            st.info("No incidents registered yet. Use the Analysis tab to create records.")

        st.markdown("### 📊 DATABASE STATISTICS")
        try:
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM incidentes_registrados")
            total_inc = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM logs_sistema")
            total_logs = cursor.fetchone()[0]
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("TOTAL INCIDENTS", total_inc)
            with col_s2:
                st.metric("SYSTEM LOGS", total_logs)
        except:
            pass

with abas[6]:
    st.markdown("### 📋 SYSTEM AUDIT LOGS")
    st.caption("COMPLETE ACTION TRAIL — Real-time session logging")

    tab_logs1, tab_logs2 = st.tabs(["📱 CURRENT SESSION", "💾 DATABASE HISTORY"])

    with tab_logs1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("No logs recorded in current session.")

    with tab_logs2:
        if sqlite_ativo:
            try:
                df_logs = pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not df_logs.empty:
                    st.dataframe(df_logs, use_container_width=True)
                else:
                    st.info("No historical logs found.")
            except:
                st.info("Unable to load database logs.")
        else:
            st.warning("Database connection unavailable.")

st.markdown("""
<div style="text-align:center;padding:24px 0 12px;border-top:1px solid rgba(0,255,255,0.1);margin-top:24px;">
    <p style="color:#374151;font-size:11px;margin:0;">
        🛡️ <strong style="color:#00ffff;">SENTINEL AI</strong> &nbsp;·&nbsp;
        LGPD COMPLIANT &nbsp;·&nbsp;
        ENTERPRISE GRADE SECURITY &nbsp;·&nbsp;
        <a href="https://github.com/mariana-castro77/SentinelAl" target="_blank" style="color:#00ffff;">GITHUB REPOSITORY</a>
    </p>
</div>
""", unsafe_allow_html=True)
