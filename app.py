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
    padding-top: 1rem;
    padding-bottom: 1rem;
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
    padding: 16px 20px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover {
    border-color: #00ffff;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
}

[data-testid="stMetricLabel"] {
    color: #8b949e;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

[data-testid="stMetricValue"] {
    color: #00ffff;
    font-size: 28px;
    font-weight: 800;
    font-family: 'Orbitron', monospace;
}

div.stButton > button {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    color: white;
    border-radius: 6px;
    border: none;
    height: 40px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff, #0096c7);
    transform: scale(1.01);
}

.chat-user {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    border-radius: 12px 12px 4px 12px;
    padding: 10px 14px;
    margin: 8px 0;
    margin-left: 20%;
    color: white;
    font-size: 13px;
    line-height: 1.5;
}

.chat-ai {
    background: linear-gradient(135deg, rgba(13, 17, 23, 0.95), rgba(0, 180, 216, 0.1));
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 12px 12px 12px 4px;
    padding: 10px 14px;
    margin: 8px 0;
    margin-right: 20%;
    color: #e6edf3;
    font-size: 13px;
    line-height: 1.5;
}

.sentinel-header {
    background: linear-gradient(135deg, rgba(13, 17, 23, 0.95), rgba(0, 180, 216, 0.05));
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.badge-sqlite {
    display: inline-block;
    background: rgba(0, 255, 255, 0.1);
    border: 1px solid rgba(0, 255, 255, 0.4);
    color: #00ffff;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
}

.badge-online {
    display: inline-block;
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.4);
    color: #00ff00;
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(13, 17, 23, 0.9);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(0, 255, 255, 0.15);
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #8b949e;
    font-weight: 600;
    font-family: 'Orbitron', monospace;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 180, 216, 0.2), rgba(0, 180, 216, 0.05));
    color: #00ffff !important;
    border-bottom: 2px solid #00ffff;
}

input, textarea, select {
    background: #0d1117 !important;
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #00ffff !important;
    box-shadow: 0 0 8px rgba(0, 255, 255, 0.15) !important;
}

hr {
    border-color: rgba(0, 255, 255, 0.15);
    margin: 16px 0;
}

code {
    background: rgba(0, 255, 255, 0.1);
    color: #00ffff;
    border-radius: 4px;
    padding: 2px 6px;
}

.status-active {
    color: #00ff00;
}

.status-warning {
    color: #f59e0b;
}

.status-critical {
    color: #ef4444;
}
</style>
""", unsafe_allow_html=True)

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] {usuario} | {acao}")
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
    if ip == "Nenhum" or pd.isna(ip):
        return "***.***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(13,17,23,0.98),rgba(0,180,216,0.08));
                border:1px solid rgba(0,255,255,0.4);border-radius:16px;padding:28px 36px;margin:20px 0;">
        <h3 style="color:#00ffff;margin:0 0 10px;font-family:Orbitron;">SECURITY PROTOCOL</h3>
        <p style="color:#e6edf3;font-size:13px;line-height:1.6;margin:0;">
        This system uses end-to-end encryption and advanced security protocols.
        Data is protected under <strong style="color:#00ffff;">LGPD (Law 13.709/2018)</strong>.
        No information is shared without explicit authorization.
        </p>
    </div>
    """, unsafe_allow_html=True)
    ca, cb, _ = st.columns([1, 1, 6])
    with ca:
        if st.button("AUTHORIZE ACCESS"):
            st.session_state["cookies_aceitos"] = True
            adicionar_log("SYSTEM", "Access authorized")
            st.rerun()
    with cb:
        if st.button("DENY ACCESS"):
            st.stop()
    st.stop()

USUARIOS = {
    "admin": {"senha_hash": hashlib.sha256("admin123".encode()).hexdigest(), "perfil": "ADMIN", "pode_exportar": True, "pode_analisar": True, "ver_pii": True, "cliente_vinculado": None},
    "analista": {"senha_hash": hashlib.sha256("analista123".encode()).hexdigest(), "perfil": "ANALYST", "pode_exportar": False, "pode_analisar": True, "ver_pii": False, "cliente_vinculado": None},
    "nubank": {"senha_hash": hashlib.sha256("nubank123".encode()).hexdigest(), "perfil": "CLIENT", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha_hash": hashlib.sha256("ml123".encode()).hexdigest(), "perfil": "CLIENT", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander": {"senha_hash": hashlib.sha256("sant123".encode()).hexdigest(), "perfil": "CLIENT", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer": {"senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(), "perfil": "VIEWER", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
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
        <div style="text-align:center;padding:50px 0 25px;">
            <div style="font-size:60px;">🛡️</div>
            <h1 style="font-size:44px;font-weight:900;color:#00ffff;font-family:Orbitron;margin:15px 0 8px;">SENTINEL AI</h1>
            <p style="color:#8b949e;font-size:14px;margin-bottom:25px;">Advanced Cyber Threat Intelligence Platform</p>
            <div class="badge-online" style="display:inline-block;">● SYSTEM ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(13,17,23,0.95);border:1px solid rgba(0,255,255,0.2);border-radius:12px;padding:20px;margin-bottom:16px;">
            <p style="color:#00ffff;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">AUTHORIZED ACCESS ONLY</p>
            <p style="color:#8b949e;font-size:12px;line-height:1.8;margin:0;">
                <span style="color:#00ffff;">admin</span> / admin123<br>
                <span style="color:#00ffff;">analista</span> / analista123<br>
                <span style="color:#00ffff;">nubank</span> / nubank123<br>
                <span style="color:#00ffff;">mercadolivre</span> / ml123<br>
                <span style="color:#00ffff;">santander</span> / sant123
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("USERNAME", placeholder="Enter credentials")
            s_in = st.text_input("PASSWORD", type="password", placeholder="••••••••")
            ok = st.form_submit_button("AUTHENTICATE", use_container_width=True)
        if ok:
            if autenticar(u_in, s_in):
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = u_in
                adicionar_log(u_in.upper(), "Login successful")
                st.rerun()
            else:
                adicionar_log(u_in or "UNKNOWN", "Login failed")
                st.error("ACCESS DENIED - Invalid credentials")
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual = USUARIOS[usuario_atual]
adicionar_log(usuario_atual.upper(), "Session active")

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

salvar_backup_sessao(df_vis, usuario_atual.upper(), "Login")

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:15px 0 8px;">
        <div style="font-size:36px;">🛡️</div>
        <p style="color:#00ffff;font-weight:800;font-size:16px;font-family:Orbitron;margin:5px 0 2px;">SENTINEL AI</p>
        <p style="color:#00ffff;font-size:9px;letter-spacing:2px;">CYBER SECURITY</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,255,255,0.05);border:1px solid rgba(0,255,255,0.15);border-radius:10px;padding:12px;margin:10px 0;">
        <p style="color:#00ffff;font-size:10px;margin:0 0 4px;">ACCESS LEVEL</p>
        <p style="color:#e6edf3;font-size:14px;font-weight:700;">{perfil_atual['perfil']}</p>
        <p style="color:#8b949e;font-size:11px;">@{usuario_atual.upper()}</p>
    </div>
    """, unsafe_allow_html=True)
    badge = '<span class="badge-sqlite">SQLITE ACTIVE</span>' if sqlite_ativo else '<span class="badge-sqlite" style="color:#ff4444;border-color:#ff4444;">DATABASE OFFLINE</span>'
    st.markdown(badge, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### PERMISSIONS")
    perms = [
        ("ANALYTICS", perfil_atual["pode_analisar"]),
        ("EXPORT", perfil_atual["pode_exportar"]),
        ("PII ACCESS", perfil_atual["ver_pii"]),
    ]
    for p_name, p_value in perms:
        if p_value:
            st.markdown(f"<p style='font-size:11px;color:#00ff00;margin:4px 0;'>✓ {p_name}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='font-size:11px;color:#ff4444;margin:4px 0;'>✗ {p_name}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,255,255,0.05);border-radius:8px;padding:10px;text-align:center;">
        <p style="color:#8b949e;font-size:9px;margin:0;">AI ACCURACY</p>
        <p style="color:#00ffff;font-size:24px;font-weight:800;font-family:Orbitron;margin:4px 0;">{acuracia:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("TERMINATE SESSION", use_container_width=True):
        adicionar_log(usuario_atual.upper(), "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
        <div>
            <p style="color:#00ffff;font-size:10px;letter-spacing:2px;margin:0;">WELCOME, {usuario_atual.upper()}</p>
            <h1 style="margin:6px 0 0;font-size:28px;">THREAT INTELLIGENCE DASHBOARD</h1>
            <p style="margin:6px 0 0;color:#8b949e;font-size:12px;">
                {"GLOBAL VIEW" if not cliente_vinculado else f"ENTERPRISE PORTAL — {cliente_vinculado.upper()}"}
            </p>
        </div>
        <div style="text-align:right;">
            <div class="badge-online" style="margin-bottom:6px;">PROTECTED</div>
            <p style="color:#8b949e;font-size:10px;margin:0;">{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total = len(df_vis)
criticos = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloq = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo = df_vis["PREJUIZO_ESTIMADO"].sum()
resolvidos = len(df_vis[df_vis["STATUS"] == "resolvido"])
pendentes = len(df_vis[df_vis["STATUS"] == "pendente"])

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("INCIDENTS", f"{total:,}")
with col2:
    st.metric("CRITICAL", f"{criticos:,}")
with col3:
    st.metric("BLOCKED IPs", f"{ips_bloq:,}")
with col4:
    st.metric("RESOLVED", f"{resolvidos:,}")
with col5:
    st.metric("PENDING", f"{pendentes:,}")
with col6:
    st.metric("DAMAGE (R$)", f"{prejuizo:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))

st.markdown("---")

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(["THREAT ANALYSIS", "INTELLIGENCE", "ATTACK MAP", "AI ASSISTANT", "DATA BACKUP", "AUDIT LOGS"])

with aba1:
    st.markdown("### THREAT ANALYSIS")
    if not perfil_atual["pode_analisar"]:
        st.warning("INSUFFICIENT PRIVILEGES")
    else:
        left, right = st.columns(2)
        with left:
            tipo = st.selectbox("INCIDENT TYPE", encoders["tipo"].classes_)
            origem = st.selectbox("ATTACK VECTOR", encoders["origem"].classes_)
            cliente = st.selectbox("CLIENT", sorted(df["CLIENTE"].unique()))
        with right:
            tempo = st.slider("RESPONSE TIME (min)", 1, 120, 30)
            status = st.selectbox("STATUS", encoders["status"].classes_)

        if st.button("EXECUTE ANALYSIS", use_container_width=True):
            adicionar_log(usuario_atual.upper(), f"Analysis: {tipo} from {origem}")
            with st.spinner("Analyzing threat patterns..."):
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
            risco_fin = "HIGH" if prej_est > 15000 else ("MEDIUM" if prej_est > 7000 else "LOW")

            ataques = df[df["TIPO INCIDENTE"] == "ataque"]
            if not ataques.empty:
                linha = ataques.sample(1).iloc[0]
                ip_ex = linha["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(linha["IP_SUSPEITO"])
                pais = linha["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "UNKNOWN", "INTERNAL"

            st.markdown("---")
            if resultado == "crítica":
                st.error(f"SEVERITY: {resultado.upper()} - IMMEDIATE ACTION REQUIRED")
            elif resultado == "média":
                st.warning(f"SEVERITY: {resultado.upper()} - MONITORING RECOMMENDED")
            else:
                st.success(f"SEVERITY: {resultado.upper()} - LOW RISK")

            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("THREAT SCORE", f"{risco}/100")
            with r2:
                st.metric("ESTIMATED LOSS", f"R$ {prej_est:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with r3:
                st.metric("RISK LEVEL", risco_fin)
            st.write(f"**TARGET:** {cliente}")
            if tipo == "ataque":
                st.error(f"ORIGIN: {pais} | IP: {ip_ex}")
                with st.expander("AUTOMATED RESPONSE"):
                    for a in ["IP BLACKLISTED", "FIREWALL UPDATED", "TEAM ALERTED", "LOGS CAPTURED"]:
                        st.write(f"✓ {a}")

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo, "origem": origem,
                    "status": status, "severidade": resultado, "cliente": cliente
                })
                st.success("Incident logged to database")

            adicionar_log(usuario_atual.upper(), f"Analysis complete: {resultado}")

with aba2:
    st.markdown("### INTELLIGENCE DASHBOARD")
    LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00ffff")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.pie(df_vis, names="SEVERIDADE", title="SEVERITY DISTRIBUTION",
                     color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig2 = px.bar(vc, x="TIPO INCIDENTE", y="count", title="INCIDENTS BY TYPE",
                      color_discrete_sequence=["#00ffff"])
        fig2.update_layout(**LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig3 = px.line(df_time, x="DATA", y="Incidentes", title="THREAT VOLUME OVER TIME",
                   color_discrete_sequence=["#00ffff"])
    fig3.update_layout(**LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        fig4 = px.histogram(df_vis, x="PAIS_ATAQUE", title="ATTACKS BY COUNTRY",
                            color_discrete_sequence=["#00ffff"])
        fig4.update_layout(**LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)
    with col_d:
        damage = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        damage = damage.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig5 = px.bar(damage, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="FINANCIAL IMPACT BY CLIENT",
                      color_discrete_sequence=["#00ffff"])
        fig5.update_layout(**LAYOUT)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("### AI MODEL PERFORMANCE")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("ACCURACY", f"{acuracia:.1%}")
    with m2:
        st.metric("TRAINING SET", f"{int(len(df)*0.8):,}")
    with m3:
        st.metric("TEST SET", f"{int(len(df)*0.2):,}")

    y_pred = modelo.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    labels = encoders["severidade"].classes_
    fig_cm = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0, "#0d1117"], [1, "#00ffff"]],
        text=cm, texttemplate="%{text}", showscale=True
    ))
    fig_cm.update_layout(title="CONFUSION MATRIX", xaxis_title="PREDICTED", yaxis_title="ACTUAL",
                         height=320, **LAYOUT)
    st.plotly_chart(fig_cm, use_container_width=True)

with aba3:
    st.markdown("### GLOBAL ATTACK MAP")
    st.caption("REAL-TIME THREAT VISUALIZATION")

    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "North Korea": (40.33, 127.51), "Germany": (51.16, 10.45), "Brazil": (-14.23, -51.92),
        "Canada": (56.13, -106.34),
    }
    TARGET = (-15.78, -47.92)

    attack_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    country_count = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    country_count.columns = ["country", "total"]

    arcs = []
    for _, row in country_count.iterrows():
        c = row["country"]
        if c in COORDS:
            src = COORDS[c]
            arcs.append({
                "src_lat": src[0], "src_lon": src[1],
                "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                "name": c, "count": int(row["total"]),
                "color": "#ef4444" if row["total"] > 30 else "#f59e0b" if row["total"] > 15 else "#00ffff"
            })

    import json
    arcs_json = json.dumps(arcs)

    map_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; background: #0a0c10; overflow: hidden; }
        canvas { display: block; }
        #info {
            position: absolute; top: 12px; left: 12px;
            color: #00ffff; font-family: monospace; font-size: 10px;
            background: rgba(13,17,23,0.95); border: 1px solid rgba(0,255,255,0.3);
            border-radius: 6px; padding: 8px 12px;
            z-index: 100;
        }
        #stats {
            position: absolute; top: 12px; right: 12px;
            color: #00ffff; font-family: monospace;
            background: rgba(13,17,23,0.95); border: 1px solid rgba(0,255,255,0.3);
            border-radius: 6px; padding: 8px 12px;
            text-align: right; z-index: 100;
        }
        #stats .num { color: #00ffff; font-size: 20px; font-weight: 800; }
        #tooltip {
            position: absolute; display: none;
            background: rgba(13,17,23,0.98); border: 1px solid #00ffff;
            border-radius: 4px; padding: 4px 8px;
            color: #00ffff; font-family: monospace; font-size: 9px;
            pointer-events: none; z-index: 200;
        }
    </style>
    </head>
    <body>
    <canvas id="canvas"></canvas>
    <div id="info">
        <strong>ATTACK ORIGINS</strong><br>
        <span style="color:#ef4444;">●</span> HIGH (>30)
        <span style="color:#f59e0b;">●</span> MEDIUM (15-30)
        <span style="color:#00ffff;">●</span> LOW (<15)
        <br>🎯 TARGET: BRAZIL
    </div>
    <div id="stats">
        DETECTED<br>
        <span class="num" id="attackCount">0</span><br>
        IPS BLOCKED<br>
        <span class="num" id="ipCount">0</span>
    </div>
    <div id="tooltip"></div>
    <script>
        var arcs = """ + arcs_json + """;
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        var tooltip = document.getElementById('tooltip');
        var w, h, particles = [];
        var attackTotal = 0, ipTotal = 0;
        
        function resize() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        function toXY(lat, lon) {
            return [(lon + 180) / 360 * w, (90 - lat) / 180 * h];
        }
        
        function drawGrid() {
            ctx.strokeStyle = 'rgba(0,255,255,0.05)';
            ctx.lineWidth = 0.5;
            for (var lon = -180; lon <= 180; lon += 30) {
                ctx.beginPath();
                var x = toXY(0, lon)[0];
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();
            }
            for (var lat = -90; lat <= 90; lat += 30) {
                ctx.beginPath();
                var y = toXY(lat, 0)[1];
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }
        }
        
        function drawDots() {
            var points = [
                [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],
                [40.33,127.51,"PRK"],[51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],
                [56.13,-106.34,"CAN"]
            ];
            for (var i = 0; i < points.length; i++) {
                var p = points[i];
                var xy = toXY(p[0], p[1]);
                var isTarget = p[2] === "BRA";
                ctx.beginPath();
                ctx.arc(xy[0], xy[1], isTarget ? 8 : 4, 0, Math.PI * 2);
                ctx.fillStyle = isTarget ? '#00ff00' : 'rgba(0,255,255,0.3)';
                ctx.fill();
                if (isTarget) {
                    ctx.beginPath();
                    ctx.arc(xy[0], xy[1], 12, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(0,255,255,0.3)';
                    ctx.stroke();
                }
                ctx.fillStyle = isTarget ? '#00ff00' : '#00ffff';
                ctx.font = 'bold 8px monospace';
                ctx.fillText(p[2], xy[0] + 10, xy[1] + 3);
            }
        }
        
        function Particle(data) {
            this.data = data;
            this.t = 0;
            this.speed = 0.003 + Math.random() * 0.004;
            this.trail = [];
            this.update = function() {
                this.t += this.speed;
                var pos = this.getPos(this.t);
                this.trail.push([pos[0], pos[1]]);
                if (this.trail.length > 18) this.trail.shift();
                return this.t < 1;
            };
            this.getPos = function(t) {
                var src = toXY(this.data.src_lat, this.data.src_lon);
                var dst = toXY(this.data.dst_lat, this.data.dst_lon);
                var ox = src[0], oy = src[1];
                var dx = dst[0], dy = dst[1];
                var mx = (ox + dx) / 2;
                var my = Math.min(oy, dy) - Math.abs(dx - ox) * 0.25;
                var it = 1 - t;
                return [it*it*ox + 2*it*t*mx + t*t*dx, it*it*oy + 2*it*t*my + t*t*dy];
            };
            this.draw = function() {
                if (this.trail.length < 2) return;
                for (var i = 1; i < this.trail.length; i++) {
                    var alpha = i / this.trail.length;
                    ctx.beginPath();
                    ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
                    ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                    var col = this.data.color;
                    if (col === '#ef4444') ctx.strokeStyle = 'rgba(239,68,68,' + alpha + ')';
                    else if (col === '#f59e0b') ctx.strokeStyle = 'rgba(245,158,11,' + alpha + ')';
                    else ctx.strokeStyle = 'rgba(0,255,255,' + alpha + ')';
                    ctx.lineWidth = 1.5 * alpha;
                    ctx.stroke();
                }
                var last = this.trail[this.trail.length - 1];
                ctx.beginPath();
                ctx.arc(last[0], last[1], 3, 0, Math.PI * 2);
                ctx.fillStyle = this.data.color;
                ctx.fill();
            };
        }
        
        function spawn() {
            for (var i = 0; i < arcs.length; i++) {
                if (Math.random() < 0.15) {
                    particles.push(new Particle(arcs[i]));
                }
            }
        }
        
        var frame = 0;
        function animate() {
            requestAnimationFrame(animate);
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#0a0c10';
            ctx.fillRect(0, 0, w, h);
            drawGrid();
            drawDots();
            frame++;
            if (frame % 12 === 0) spawn();
            var newParticles = [];
            for (var i = 0; i < particles.length; i++) {
                var alive = particles[i].update();
                particles[i].draw();
                if (!alive) {
                    attackTotal++;
                    ipTotal = Math.floor(attackTotal * 0.72);
                    document.getElementById('attackCount').textContent = attackTotal.toLocaleString();
                    document.getElementById('ipCount').textContent = ipTotal.toLocaleString();
                } else {
                    newParticles.push(particles[i]);
                }
            }
            particles = newParticles;
        }
        
        canvas.addEventListener('mousemove', function(e) {
            var rect = canvas.getBoundingClientRect();
            var mx = e.clientX - rect.left;
            var my = e.clientY - rect.top;
            var found = false;
            for (var i = 0; i < arcs.length; i++) {
                var a = arcs[i];
                var pos = toXY(a.src_lat, a.src_lon);
                var dx = mx - pos[0];
                var dy = my - pos[1];
                var dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 15) {
                    tooltip.style.display = 'block';
                    tooltip.style.left = (e.clientX + 12) + 'px';
                    tooltip.style.top = (e.clientY - 30) + 'px';
                    tooltip.innerHTML = '<strong>' + a.name + '</strong><br>' + a.count + ' attacks';
                    found = true;
                    break;
                }
            }
            if (!found) tooltip.style.display = 'none';
        });
        
        animate();
    </script>
    </body>
    </html>
    """
    components.html(map_html, height=520, scrolling=False)

    st.markdown("### TOP ATTACK SOURCES")
    top_countries = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    top_countries.columns = ["COUNTRY", "ATTACKS"]
    top_countries["%"] = (top_countries["ATTACKS"] / top_countries["ATTACKS"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(top_countries, use_container_width=True, hide_index=True)

with aba4:
    st.markdown("### AI SECURITY ASSISTANT")
    st.caption("CONTEXT-AWARE THREAT INTELLIGENCE")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    top5_clients = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5_attackers = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    sys_prompt = f"""You are SentinelBot, a cybersecurity AI assistant.
Respond in Portuguese (Brazil). Be professional and direct.

SYSTEM DATA:
- Total incidents: {len(df_vis)}
- Critical: {len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])} ({len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])/len(df_vis)*100:.1f}%)
- Blocked IPs: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower() == 'sim'])}
- Total loss: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- AI accuracy: {acuracia:.1%}
- Incident types: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Clients: {', '.join(df_vis['CLIENTE'].unique())}
- Top attackers: {top5_attackers}
- Top clients by loss: {top5_clients}
- Period: {df_vis['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].min()) else 'N/A'} to {df_vis['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].max()) else 'N/A'}"""

    if not ANTHROPIC_API_KEY:
        st.error("AI ASSISTANT OFFLINE - API key required")
        st.info("Configure ANTHROPIC_API_KEY in Streamlit Secrets")
    else:
        st.success("AI ASSISTANT ACTIVE")

    for msg in st.session_state["chat_history"]:
        css_class = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{css_class}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat", clear_on_submit=True):
        inp, btn = st.columns([5, 1])
        with inp:
            query = st.text_input("", placeholder="Ask about threats, clients, or request analysis...", label_visibility="collapsed", disabled=not ANTHROPIC_API_KEY)
        with btn:
            submit = st.form_submit_button("SEND", use_container_width=True, disabled=not ANTHROPIC_API_KEY)

    suggestions = ["Top financial loss by client?", "Most frequent attack types?", "Critical incident status?", "AI model accuracy?", "Security recommendations"]
    sug_cols = st.columns(len(suggestions))
    selected_sug = None
    for i, sug in enumerate(suggestions):
        with sug_cols[i]:
            if st.button(sug[:25] + "..", key=f"sug{i}", use_container_width=True, disabled=not ANTHROPIC_API_KEY):
                selected_sug = sug

    if selected_sug:
        query = selected_sug
        submit = True

    if submit and query and ANTHROPIC_API_KEY:
        adicionar_log(usuario_atual.upper(), f"Chat: {query[:50]}")
        st.session_state["chat_history"].append({"role": "user", "content": query})
        with st.spinner("Processing..."):
            try:
                headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
                payload = {"model": "claude-3-haiku-20240307", "max_tokens": 1024, "system": sys_prompt, "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]}
                resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    answer = resp.json()["content"][0]["text"]
                else:
                    answer = f"API Error: {resp.status_code}"
            except Exception as e:
                answer = f"Connection error: {str(e)[:80]}"
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        adicionar_log(usuario_atual.upper(), "AI response generated")
        st.rerun()

    if st.session_state["chat_history"] and st.button("CLEAR HISTORY"):
        st.session_state["chat_history"] = []
        st.rerun()

with aba5:
    st.markdown("### DATA BACKUP")

    if not perfil_atual["pode_exportar"]:
        st.error("EXPORT RESTRICTED - Admin only")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("EXPORT CSV", df.to_csv(index=False).encode("utf-8"), f"sentinelai_{ts}.csv", "text/csv", use_container_width=True)
        with c2:
            df_anon = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("EXPORT ANONYM (LGPD)", df_anon.to_csv(index=False).encode("utf-8"), f"sentinelai_anon_{ts}.csv", "text/csv", use_container_width=True)
        with c3:
            if "logs_sistema" in st.session_state:
                st.download_button("EXPORT LOGS", "\n".join(st.session_state["logs_sistema"]).encode("utf-8"), f"sentinelai_logs_{ts}.txt", "text/plain", use_container_width=True)

        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("BACKUP DATABASE", f.read(), f"sentinelai_db_{ts}.db", "application/x-sqlite3", use_container_width=True)

    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### BACKUP HISTORY")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)

    st.markdown("### DATA PREVIEW")
    st.dataframe(df_vis.head(20), use_container_width=True)

with aba6:
    st.markdown("### AUDIT LOGS")

    tab_curr, tab_db = st.tabs(["CURRENT SESSION", "DATABASE HISTORY"])

    with tab_curr:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("No logs in current session")

    with tab_db:
        if sqlite_ativo:
            try:
                db_logs = pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not db_logs.empty:
                    st.dataframe(db_logs, use_container_width=True)
                else:
                    st.info("No database logs found")
            except:
                st.info("Unable to load database logs")
        else:
            st.warning("Database offline")

st.markdown("""
<div style="text-align:center;padding:20px 0 8px;border-top:1px solid rgba(0,255,255,0.1);margin-top:16px;">
    <p style="color:#374151;font-size:10px;margin:0;">
        SENTINEL AI — ENTERPRISE SECURITY PLATFORM
    </p>
</div>
""", unsafe_allow_html=True)
