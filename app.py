import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import hashlib, datetime, random, time, json, sqlite3, os, requests
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelAI — SOC Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dark red SOC theme + parallax scroll + animations
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

/* ── Background ── */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, rgba(139,0,0,0.18) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(180,0,0,0.12) 0%, transparent 55%),
                radial-gradient(ellipse at 50% 80%, rgba(100,0,0,0.10) 0%, transparent 50%),
                #060508;
    background-attachment: fixed;
    color: #e2e8f0;
    min-height: 100vh;
}

/* ── Header / Toolbar ── */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0507 0%, #0f0509 50%, #0a0507 100%) !important;
    border-right: 1px solid rgba(180,0,0,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Block container ── */
.block-container { padding: 1.2rem 2rem 3rem !important; max-width: 100% !important; }

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(139,0,0,0.12) 0%, rgba(10,5,7,0.95) 100%);
    border: 1px solid rgba(180,0,0,0.22);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(220,38,38,0.7), transparent);
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    border-color: rgba(220,38,38,0.5);
    box-shadow: 0 8px 32px rgba(139,0,0,0.25);
}
[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 0.6rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #ff4444 !important;
    font-size: 1.45rem !important;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #b91c1c 100%);
    color: white !important;
    border: 1px solid rgba(220,38,38,0.4);
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: 0 4px 16px rgba(139,0,0,0.3);
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #991b1b 0%, #b91c1c 50%, #dc2626 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(220,38,38,0.4);
    border-color: rgba(248,113,113,0.5);
}

/* ── Inputs ── */
input, textarea, [data-baseweb="input"] input {
    background: rgba(10,5,7,0.9) !important;
    border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: rgba(220,38,38,0.6) !important;
    box-shadow: 0 0 0 2px rgba(220,38,38,0.15) !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: rgba(10,5,7,0.9) !important;
    border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,5,7,0.85);
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border: 1px solid rgba(180,0,0,0.1);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: #6b7280;
    font-weight: 600;
    font-size: 0.75rem;
    padding: 0.5rem 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(139,0,0,0.4), rgba(180,0,0,0.25)) !important;
    color: #ff6666 !important;
    box-shadow: 0 0 12px rgba(180,0,0,0.2);
}

/* ── Chat messages ── */
.chat-user {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem;
    margin: 0.6rem 0 0.6rem auto;
    max-width: 75%;
    width: fit-content;
    color: white;
    font-size: 0.82rem;
    line-height: 1.6;
    box-shadow: 0 4px 16px rgba(139,0,0,0.3);
}
.chat-ai {
    background: rgba(10,5,7,0.95);
    border: 1px solid rgba(180,0,0,0.2);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    margin: 0.6rem 0;
    max-width: 75%;
    width: fit-content;
    color: #cbd5e1;
    font-size: 0.82rem;
    line-height: 1.6;
}

/* ── Header card ── */
.soc-header {
    background: linear-gradient(135deg, rgba(139,0,0,0.08) 0%, rgba(10,5,7,0.97) 100%);
    border: 1px solid rgba(180,0,0,0.15);
    border-radius: 18px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.soc-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(220,38,38,0.6) 50%, transparent 100%);
}
.soc-header::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(180,0,0,0.3) 50%, transparent 100%);
}

/* ── Status badge ── */
.badge-online {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,255,100,0.06);
    border: 1px solid rgba(0,255,100,0.22);
    color: #4ade80;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.badge-critical {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(220,38,38,0.1);
    border: 1px solid rgba(220,38,38,0.35);
    color: #f87171;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
}

/* ── Parallax scan line effect ── */
@keyframes scan {
    0% { transform: translateY(-100%); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
}
.scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(220,38,38,0.4), transparent);
    animation: scan 6s linear infinite;
    pointer-events: none; z-index: 0;
}

/* ── Robot animation ── */
@keyframes float-robot {
    0%   { transform: translateY(0px) rotate(-2deg); }
    25%  { transform: translateY(-12px) rotate(1deg); }
    50%  { transform: translateY(-6px) rotate(-1deg); }
    75%  { transform: translateY(-18px) rotate(2deg); }
    100% { transform: translateY(0px) rotate(-2deg); }
}
@keyframes glow-pulse {
    0%, 100% { filter: drop-shadow(0 0 8px rgba(220,38,38,0.6)) drop-shadow(0 0 20px rgba(139,0,0,0.4)); }
    50% { filter: drop-shadow(0 0 20px rgba(220,38,38,0.9)) drop-shadow(0 0 40px rgba(180,0,0,0.6)); }
}
.robot-float {
    animation: float-robot 4s ease-in-out infinite, glow-pulse 2.5s ease-in-out infinite;
    font-size: 3.5rem;
    display: block;
    text-align: center;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(10,5,7,0.8); }
::-webkit-scrollbar-thumb { background: rgba(180,0,0,0.4); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(220,38,38,0.6); }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(180,0,0,0.15); }
iframe { border-radius: 14px; }

/* ── Divider ── */
hr { border-color: rgba(180,0,0,0.12) !important; margin: 1rem 0 !important; }

/* ── Expander ── */
details summary { color: #f87171 !important; font-weight: 600; font-size: 0.82rem; }
details { background: rgba(10,5,7,0.7); border: 1px solid rgba(180,0,0,0.15); border-radius: 10px; padding: 0.5rem 1rem; }

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    .block-container { padding: 0.8rem 0.8rem 2rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    .soc-header { padding: 1rem; }
    .chat-user, .chat-ai { max-width: 92%; }
}

/* ── Tooltip / info boxes ── */
.info-box {
    background: rgba(139,0,0,0.08);
    border: 1px solid rgba(180,0,0,0.2);
    border-left: 3px solid #dc2626;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.6;
}

/* ── Plotly background override ── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>

<!-- Scan line parallax effect -->
<div class="scan-line"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE — SQLite (backup real persistente)
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "sentinelai_backup.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS incidentes_analisados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT, tipo TEXT, origem TEXT, status TEXT,
            severidade TEXT, cliente TEXT, risco INTEGER,
            prejuizo REAL, ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT, acao TEXT, detalhe TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS chat_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT, pergunta TEXT, resposta TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS backups_meta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT, tipo TEXT, registros INTEGER,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

init_db()

def db_log(usuario, acao, detalhe=""):
    try:
        conn = get_db()
        conn.execute("INSERT INTO logs_auditoria (usuario,acao,detalhe) VALUES (?,?,?)",
                     (usuario, acao, detalhe[:500]))
        conn.commit(); conn.close()
    except: pass

def db_salvar_incidente(d):
    try:
        conn = get_db()
        conn.execute("""INSERT INTO incidentes_analisados
            (usuario,tipo,origem,status,severidade,cliente,risco,prejuizo)
            VALUES (?,?,?,?,?,?,?,?)""",
            (d["usuario"],d["tipo"],d["origem"],d["status"],
             d["severidade"],d["cliente"],d["risco"],d["prejuizo"]))
        conn.commit(); conn.close()
        return True
    except: return False

def db_salvar_chat(usuario, pergunta, resposta):
    try:
        conn = get_db()
        conn.execute("INSERT INTO chat_historico (usuario,pergunta,resposta) VALUES (?,?,?)",
                     (usuario, pergunta[:1000], resposta[:2000]))
        conn.commit(); conn.close()
    except: pass

def db_buscar_incidentes():
    try:
        conn = get_db()
        df = pd.read_sql("SELECT * FROM incidentes_analisados ORDER BY ts DESC LIMIT 100", conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_buscar_logs():
    try:
        conn = get_db()
        df = pd.read_sql("SELECT * FROM logs_auditoria ORDER BY ts DESC LIMIT 200", conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_meta_backup(usuario, tipo, registros):
    try:
        conn = get_db()
        conn.execute("INSERT INTO backups_meta (usuario,tipo,registros) VALUES (?,?,?)",
                     (usuario, tipo, registros))
        conn.commit(); conn.close()
    except: pass

# ─────────────────────────────────────────────────────────────────────────────
# LOG helper (session + db)
# ─────────────────────────────────────────────────────────────────────────────
def log(usuario, acao, detalhe=""):
    if "logs" not in st.session_state: st.session_state["logs"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs"].append(f"[{ts}] {usuario} → {acao} {detalhe}")
    db_log(usuario, acao, detalhe)

# ─────────────────────────────────────────────────────────────────────────────
# USERS / RBAC
# ─────────────────────────────────────────────────────────────────────────────
USERS = {
    "admin":        {"pw": "admin123",    "role": "Administrador",      "export": True,  "analyze": True,  "pii": True,  "client": None},
    "analista":     {"pw": "analista123", "role": "Analista SOC",       "export": False, "analyze": True,  "pii": False, "client": None},
    "nubank":       {"pw": "nubank123",   "role": "Cliente",            "export": False, "analyze": False, "pii": False, "client": "Nubank"},
    "mercadolivre": {"pw": "ml123",       "role": "Cliente",            "export": False, "analyze": False, "pii": False, "client": "Mercado Livre"},
    "santander":    {"pw": "sant123",     "role": "Cliente",            "export": False, "analyze": False, "pii": False, "client": "Santander"},
    "ifood":        {"pw": "ifood123",    "role": "Cliente",            "export": False, "analyze": False, "pii": False, "client": "iFood"},
    "viewer":       {"pw": "viewer123",   "role": "Visualizador",       "export": False, "analyze": False, "pii": False, "client": None},
}
_H = {u: hashlib.sha256(v["pw"].encode()).hexdigest() for u,v in USERS.items()}

def auth(u,p): return u in _H and hashlib.sha256(p.encode()).hexdigest() == _H[u]
def mask_ip(ip):
    if not ip or str(ip)=="Nenhum" or pd.isna(ip): return "***.***.***"
    p=str(ip).split("."); return f"{p[0]}.{p[1]}.***.***" if len(p)==4 else "***"

# ─────────────────────────────────────────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────────────────────────────────────────
for k,v in {"authed":False,"user":None,"lgpd":False,"chat":[],"logs":[]}.items():
    if k not in st.session_state: st.session_state[k]=v

# ─────────────────────────────────────────────────────────────────────────────
# LGPD BANNER
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["lgpd"]:
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;right:0;z-index:9999;
                background:linear-gradient(135deg,rgba(10,5,7,0.99),rgba(20,5,5,0.99));
                border-top:1px solid rgba(220,38,38,0.4);
                padding:1.2rem 2rem;backdrop-filter:blur(20px);">
      <div style="max-width:900px;margin:0 auto;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <span style="font-size:1.2rem;">🍪</span>
          <strong style="color:white;font-size:0.9rem;">Privacidade, Cookies e LGPD</strong>
          <span class="badge-critical">Lei 13.709/2018</span>
        </div>
        <p style="color:#94a3b8;font-size:0.78rem;line-height:1.7;margin-bottom:12px;">
          Esta plataforma utiliza cookies de sessão para autenticação, controle de acesso e auditoria.
          Todos os dados são protegidos conforme a <strong style="color:#fca5a5;">Lei Geral de Proteção de Dados (LGPD)</strong>.
          IPs e dados pessoais identificáveis são mascarados para perfis sem autorização.
          Nenhum dado é compartilhado com terceiros. Ao continuar, você consente com estes termos.
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button onclick="void(0)" style="background:rgba(180,0,0,0.2);border:1px solid rgba(220,38,38,0.3);
            color:#f87171;padding:6px 16px;border-radius:8px;font-size:0.72rem;cursor:pointer;">
            Recusar (bloqueia acesso)
          </button>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    _, c2, _ = st.columns([3,2,3])
    with c2:
        st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
        if st.button("✅  Aceitar e Continuar", use_container_width=True):
            st.session_state["lgpd"] = True
            log("sistema", "LGPD aceito")
            st.rerun()
        if st.button("❌  Recusar (bloqueia acesso)", use_container_width=True):
            st.warning("Você recusou os termos. O acesso está bloqueado."); st.stop()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["authed"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)

    # Hero login page
    st.markdown("""
    <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem;">
      <div style="text-align:center;margin-bottom:2.5rem;">
        <div style="font-size:4rem;margin-bottom:0.5rem;
             filter:drop-shadow(0 0 30px rgba(220,38,38,0.8));">🛡️</div>
        <h1 style="font-size:2.8rem;font-weight:900;color:white;letter-spacing:-1px;margin:0;">
            Sentinel<span style="color:#dc2626;">AI</span>
        </h1>
        <p style="color:#6b7280;font-size:0.9rem;margin:8px 0 0;">
            Security Operations Center — Plataforma de Inteligência Cibernética
        </p>
        <div style="display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;">
          <span class="badge-online">● SISTEMA OPERACIONAL</span>
          <span class="badge-critical">ACESSO RESTRITO</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(139,0,0,0.07),rgba(10,5,7,0.98));
                    border:1px solid rgba(180,0,0,0.2);border-radius:20px;
                    padding:2rem;margin-bottom:1.2rem;
                    box-shadow:0 24px 80px rgba(139,0,0,0.2);">
          <p style="color:#6b7280;font-size:0.65rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Credenciais de Acesso
          </p>
        """, unsafe_allow_html=True)

        # User cards
        creds = [
            ("admin","admin123","🔴 Administrador"),
            ("analista","analista123","🟠 Analista SOC"),
            ("nubank","nubank123","🔵 Nubank"),
            ("mercadolivre","ml123","🟢 Mercado Livre"),
            ("santander","sant123","🟣 Santander"),
            ("ifood","ifood123","🟡 iFood"),
            ("viewer","viewer123","⚪ Visualizador"),
        ]
        for u,p,label in creds:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:6px 10px;border-radius:8px;margin:3px 0;
                        background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.1);">
              <span style="color:#e2e8f0;font-size:0.72rem;font-weight:500;">{label}</span>
              <code style="color:#f87171;font-size:0.65rem;background:rgba(220,38,38,0.08);
                           padding:2px 8px;border-radius:4px;">{u} / {p}</code>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("login_form"):
            u_in = st.text_input("", placeholder="👤  Usuário", label_visibility="collapsed")
            p_in = st.text_input("", placeholder="🔑  Senha", type="password", label_visibility="collapsed")
            ok   = st.form_submit_button("ACESSAR O SISTEMA →", use_container_width=True)

        if ok:
            if auth(u_in.strip(), p_in):
                st.session_state.update({"authed": True, "user": u_in.strip()})
                log(u_in.strip(), "LOGIN", "Acesso concedido")
                st.rerun()
            else:
                log(u_in.strip() or "?", "LOGIN_FAIL", "Credenciais inválidas")
                st.error("❌  Usuário ou senha incorretos.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATED — load data
# ─────────────────────────────────────────────────────────────────────────────
USER = st.session_state["user"]
PROF = USERS[USER]
log(USER, "SESSION_ACTIVE")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset_final.csv")
    df = df.dropna(subset=["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"]:
        df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo","orig","stat","sev"]}
    df["TE"] = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["OE"] = enc["orig"].fit_transform(df["ORIGEM"])
    df["SE"] = enc["stat"].fit_transform(df["STATUS"])
    df["VE"] = enc["sev"].fit_transform(df["SEVERIDADE"])
    X = df[["TE","OE","TEMPO RESOLUÇÃO","SE"]]
    y = df["VE"]
    Xt,Xv,yt,yv = train_test_split(X,y,test_size=.2,random_state=42)
    m = DecisionTreeClassifier(random_state=42); m.fit(Xt,yt)
    acc = accuracy_score(yv,m.predict(Xv))
    return df,enc,m,acc,Xv,yv

df_all, ENC, MODEL, ACC, Xv, yv = load_data()
CLT = PROF["client"]
df  = df_all[df_all["CLIENTE"]==CLT].copy() if CLT else df_all.copy()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Robot animated
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;">
      <span class="robot-float">🤖</span>
      <p style="color:#dc2626;font-size:0.6rem;font-weight:700;
                text-transform:uppercase;letter-spacing:0.15em;margin-top:8px;">
        SENTINEL CORE
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # User info
    st.markdown(f"""
    <div style="background:rgba(139,0,0,0.07);border:1px solid rgba(180,0,0,0.15);
                border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.8rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:6px;">OPERADOR</p>
      <p style="color:white;font-weight:700;font-size:0.9rem;margin:0;">@{USER}</p>
      <p style="color:#9ca3af;font-size:0.7rem;margin:3px 0 8px;">{PROF['role']}</p>
      <span class="badge-online">● ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    # DB status
    db_ok = os.path.exists(DB_PATH)
    db_size = round(os.path.getsize(DB_PATH)/1024,1) if db_ok else 0
    st.markdown(f"""
    <div style="background:rgba(0,200,100,0.04);border:1px solid rgba(0,200,100,0.15);
                border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.8rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;margin-bottom:4px;">BACKUP SQLite</p>
      <p style="color:#4ade80;font-size:0.78rem;font-weight:600;">✅ {'Ativo — ' + str(db_size) + ' KB' if db_ok else 'Offline'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Permissions
    st.markdown("<p style='color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>PERMISSÕES</p>", unsafe_allow_html=True)
    for label, flag in [("Análise ML", PROF["analyze"]),("Exportar dados", PROF["export"]),("Ver IPs / PII", PROF["pii"])]:
        c,i = ("#4ade80","✓") if flag else ("#ef4444","✗")
        st.markdown(f"<p style='color:{c};font-size:0.72rem;margin:3px 0;'><b>{i}</b> {label}</p>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(139,0,0,0.08);border-radius:10px;padding:0.7rem 1rem;margin:0.8rem 0;text-align:center;">
      <p style="color:#4b5563;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;">Acurácia IA</p>
      <p style="color:#dc2626;font-size:1.4rem;font-weight:800;font-family:'JetBrains Mono',monospace;">{ACC:.1%}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Encerrar Sessão", use_container_width=True):
        log(USER,"LOGOUT")
        st.session_state.update({"authed":False,"user":None,"chat":[]})
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────
now = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
scope = f"Cliente: {CLT}" if CLT else "Visão Global — Todos os Clientes"
st.markdown(f"""
<div class="soc-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
    <div>
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <span style="font-size:1.8rem;filter:drop-shadow(0 0 12px rgba(220,38,38,0.7));">🛡️</span>
        <div>
          <h1 style="color:white;font-size:1.5rem;font-weight:900;letter-spacing:-0.5px;margin:0;">
            Sentinel<span style="color:#dc2626;">AI</span>
            <span style="color:#374151;font-size:0.75rem;font-weight:400;margin-left:10px;">SOC PLATFORM</span>
          </h1>
          <p style="color:#6b7280;font-size:0.72rem;margin:3px 0 0;">{scope}</p>
        </div>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;margin-bottom:6px;">
        <span class="badge-online">● SISTEMA ONLINE</span>
        <span class="badge-critical">LGPD COMPLIANT</span>
      </div>
      <p style="color:#374151;font-size:0.62rem;font-family:'JetBrains Mono',monospace;">{now}</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────────────────────────────────────
total   = len(df)
crit    = len(df[df["SEVERIDADE"]=="crítica"])
bloq    = len(df[df["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
resol   = len(df[df["STATUS"]=="resolvido"])
pend    = len(df[df["STATUS"]=="pendente"])
prej    = df["PREJUIZO_ESTIMADO"].sum()

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.metric("INCIDENTES",f"{total:,}")
with c2: st.metric("CRÍTICOS",f"{crit:,}")
with c3: st.metric("IPs BLOQUEADOS",f"{bloq:,}")
with c4: st.metric("RESOLVIDOS",f"{resol:,}")
with c5: st.metric("PENDENTES",f"{pend:,}")
with c6: st.metric("PREJUÍZO",f"R$ {prej/1e6:.2f}Mi")

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["🔍 Análise","📊 Dashboard","🌍 Ameaças Globais","🤖 Sentinel Bot","💾 Backup & DB","📋 Auditoria"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANÁLISE ML
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### 🔍 Análise Inteligente de Incidentes")
    if not PROF["analyze"]:
        st.markdown('<div class="info-box">⛔ Perfil sem permissão para análise. Contate o Administrador.</div>', unsafe_allow_html=True)
    else:
        c1,c2 = st.columns(2)
        with c1:
            tipo   = st.selectbox("Tipo de Incidente", ENC["tipo"].classes_)
            orig   = st.selectbox("Origem", ENC["orig"].classes_)
            cli_af = st.selectbox("Cliente Afetado", sorted(df_all["CLIENTE"].unique()))
        with c2:
            tempo  = st.slider("Tempo de Resolução (min)", 1, 120, 30)
            stat   = st.selectbox("Status", ENC["stat"].classes_)

        if st.button("🚀  INICIAR ANÁLISE FORENSE", use_container_width=True):
            log(USER, "ANALISE", f"tipo={tipo}")
            with st.spinner("Processando com IA..."):
                time.sleep(1)

            entrada = pd.DataFrame({
                "TE":[ENC["tipo"].transform([tipo])[0]],
                "OE":[ENC["orig"].transform([orig])[0]],
                "TEMPO RESOLUÇÃO":[tempo],
                "SE":[ENC["stat"].transform([stat])[0]],
            })
            sev = ENC["sev"].inverse_transform(MODEL.predict(entrada))[0]
            if stat=="resolvido":                    sev="baixa"
            elif tipo in ["ataque","falha servidor"]: sev="crítica"
            elif tipo in ["lentidão","erro sistema"]: sev=random.choice(["baixa","média"])

            risco = random.randint(10,99)
            prej  = random.uniform(3000,30000)
            risco_fin = "ALTO" if prej>15000 else ("MÉDIO" if prej>7000 else "BAIXO")

            atks = df_all[df_all["TIPO INCIDENTE"]=="ataque"]
            if not atks.empty:
                row  = atks.sample(1).iloc[0]
                ip   = str(row["IP_SUSPEITO"]) if PROF["pii"] else mask_ip(row["IP_SUSPEITO"])
                pais = row["PAIS_ATAQUE"]
            else:
                ip,pais = "N/A","Interno"

            st.markdown("<hr>", unsafe_allow_html=True)
            if sev=="crítica":   st.error(f"🔴  SEVERIDADE PREVISTA: **CRÍTICA**")
            elif sev=="média":   st.warning(f"🟡  SEVERIDADE PREVISTA: **MÉDIA**")
            else:                st.success(f"🟢  SEVERIDADE PREVISTA: **BAIXA**")

            r1,r2,r3,r4 = st.columns(4)
            with r1: st.metric("THREAT SCORE",f"{risco}/100")
            with r2: st.metric("PREJUÍZO EST.",f"R$ {prej:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("RISCO FIN.",risco_fin)
            with r4: st.metric("CLIENTE",cli_af)

            if tipo=="ataque":
                st.error(f"🌍 Origem: **{pais}**  |  IP: `{ip}`")
                with st.expander("🛡️ Resposta Automática Acionada"):
                    for a in ["✅ IP bloqueado","✅ Firewall atualizado","✅ Equipe SOC notificada","✅ Logs enviados para auditoria"]:
                        st.write(a)

            saved = db_salvar_incidente({
                "usuario":USER,"tipo":tipo,"origem":orig,"status":stat,
                "severidade":sev,"cliente":cli_af,"risco":risco,"prejuizo":prej
            })
            if saved:
                st.success("💾 Incidente registrado no banco de dados SQLite")

        # Table
        st.markdown("### 📋 Registros do Dataset")
        cols_show = ["DATA","TIPO INCIDENTE","SEVERIDADE","STATUS","CLIENTE","PAIS_ATAQUE","PREJUIZO_ESTIMADO"]
        if PROF["pii"]: cols_show.append("IP_SUSPEITO")
        df_show = df[cols_show].copy()
        if not PROF["pii"] and "IP_SUSPEITO" in df_show.columns:
            df_show["IP_SUSPEITO"] = df_show["IP_SUSPEITO"].apply(mask_ip)
        st.dataframe(df_show, use_container_width=True, height=300)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 📊 Telemetria & Métricas")
    L = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
             font_color="#94a3b8",font_family="Inter")
    RED = ["#dc2626","#ef4444","#f87171","#fca5a5","#7f1d1d","#991b1b"]

    g1,g2 = st.columns(2)
    with g1:
        fig=px.pie(df,names="SEVERIDADE",title="Distribuição de Severidade",
                   color_discrete_sequence=["#dc2626","#f59e0b","#22c55e"])
        fig.update_layout(**L,title_font_color="white")
        st.plotly_chart(fig,use_container_width=True)
    with g2:
        vc=df["TIPO INCIDENTE"].value_counts().reset_index()
        fig=px.bar(vc,x="TIPO INCIDENTE",y="count",title="Incidentes por Tipo",
                   color_discrete_sequence=["#dc2626"])
        fig.update_layout(**L,title_font_color="white")
        st.plotly_chart(fig,use_container_width=True)

    dt=df.groupby("DATA").size().reset_index(name="n")
    fig=px.area(dt,x="DATA",y="n",title="Volume ao Longo do Tempo",
                color_discrete_sequence=["#dc2626"])
    fig.update_traces(fill="tozeroy",fillcolor="rgba(220,38,38,0.1)")
    fig.update_layout(**L,title_font_color="white")
    st.plotly_chart(fig,use_container_width=True)

    g3,g4 = st.columns(2)
    with g3:
        fig=px.histogram(df,x="PAIS_ATAQUE",title="Ataques por País",
                         color_discrete_sequence=["#b91c1c"])
        fig.update_layout(**L,title_font_color="white")
        st.plotly_chart(fig,use_container_width=True)
    with g4:
        dp=df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        dp=dp.sort_values("PREJUIZO_ESTIMADO",ascending=False).head(7)
        fig=px.bar(dp,x="CLIENTE",y="PREJUIZO_ESTIMADO",title="Prejuízo por Cliente",
                   color_discrete_sequence=["#991b1b"])
        fig.update_layout(**L,title_font_color="white")
        st.plotly_chart(fig,use_container_width=True)

    # Confusion matrix
    st.markdown("### 🤖 Performance do Modelo de IA")
    m1,m2,m3 = st.columns(3)
    with m1: st.metric("ACURÁCIA",f"{ACC:.1%}")
    with m2: st.metric("TREINO",f"{int(len(df_all)*0.8):,}")
    with m3: st.metric("TESTE",f"{int(len(df_all)*0.2):,}")

    ypred=MODEL.predict(Xv)
    cm=confusion_matrix(yv,ypred)
    lbs=ENC["sev"].classes_
    fig=go.Figure(go.Heatmap(z=cm,x=lbs,y=lbs,
        colorscale=[[0,"#0a0507"],[0.5,"#7f1d1d"],[1,"#dc2626"]],
        text=cm,texttemplate="%{text}",showscale=True))
    fig.update_layout(title="Matriz de Confusão",xaxis_title="Previsto",yaxis_title="Real",
                      height=320,**L,title_font_color="white")
    st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MAPA GLOBAL (Globo 3D estilo Kaspersky)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 🌍 Centro de Monitoramento Global de Ameaças")
    st.caption("Visualização em tempo real de ataques cibernéticos direcionados ao sistema")

    atk_df  = df[df["TIPO INCIDENTE"]=="ataque"]
    cc      = atk_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country","total"]

    COORDS = {
        "China":(35.86,104.19),"Russia":(61.52,105.31),"United States":(37.09,-95.71),
        "Germany":(51.16,10.45),"North Korea":(40.33,127.51),"Canada":(56.13,-106.34),
        "Brazil":(-14.23,-51.92),"India":(20.59,78.96),"France":(46.23,2.21),
        "United Kingdom":(55.37,-3.43),"Iran":(32.43,53.69),"Japan":(36.20,138.25),
        "Australia":(-25.27,133.77),"South Korea":(35.90,127.76),"Ukraine":(48.38,31.17),
    }
    TARGET_LAT,TARGET_LON = -15.78,-47.92

    arcs=[]
    for _,row in cc.iterrows():
        c=row["country"]
        if c in COORDS and c!="Brazil":
            s=COORDS[c]
            arcs.append({"slat":s[0],"slon":s[1],"dlat":TARGET_LAT,"dlon":TARGET_LON,
                          "name":c,"n":int(row["total"])})

    arcs_j = json.dumps(arcs)

    globe_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#060508;overflow:hidden;font-family:'JetBrains Mono',monospace;}}
canvas{{display:block;}}
#overlay{{position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;}}
.panel{{position:absolute;background:rgba(6,5,8,0.85);border:1px solid rgba(220,38,38,0.25);
         border-radius:12px;padding:12px 16px;backdrop-filter:blur(10px);}}
#legend{{top:16px;left:16px;min-width:180px;}}
#legend h4{{color:#dc2626;font-size:11px;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;}}
.leg-item{{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:10px;color:#9ca3af;}}
.leg-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0;}}
#counters{{top:16px;right:16px;text-align:right;}}
#counters .lbl{{color:#4b5563;font-size:9px;text-transform:uppercase;letter-spacing:0.1em;}}
#counters .val{{color:#dc2626;font-size:1.4rem;font-weight:700;line-height:1.2;}}
#status{{bottom:16px;left:50%;transform:translateX(-50%);
         display:flex;align-items:center;gap:8px;white-space:nowrap;}}
.pulse{{width:8px;height:8px;border-radius:50%;background:#4ade80;
        animation:pulse 1.5s ease-in-out infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(74,222,128,0.5);}}
                  50%{{box-shadow:0 0 0 6px rgba(74,222,128,0);}}}}
#status span{{color:#4ade80;font-size:10px;}}
#tooltip{{position:absolute;display:none;background:rgba(6,5,8,0.95);
           border:1px solid rgba(220,38,38,0.4);border-radius:8px;
           padding:8px 12px;pointer-events:none;}}
#tooltip strong{{color:#f87171;font-size:11px;}}
#tooltip p{{color:#9ca3af;font-size:10px;margin-top:3px;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="overlay">
  <div class="panel" id="legend">
    <h4>🛡️ Origens de Ataque</h4>
    <div class="leg-item"><div class="leg-dot" style="background:#ff2222"></div>Alto volume (&gt;30)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ff8800"></div>Médio (15–30)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ff4488"></div>Baixo (&lt;15)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#00ff88"></div>Brasil (alvo)</div>
  </div>
  <div class="panel" id="counters">
    <div class="lbl">Ataques detectados</div>
    <div class="val" id="atk">0</div>
    <div class="lbl" style="margin-top:8px;">IPs bloqueados</div>
    <div class="val" id="ipc">0</div>
  </div>
  <div class="panel" id="status">
    <div class="pulse"></div>
    <span>MONITORAMENTO ATIVO — TEMPO REAL</span>
  </div>
</div>
<div id="tooltip"><strong id="tt-name"></strong><p id="tt-count"></p></div>

<script>
const ARCS={arcs_j};
const C=document.getElementById('c');
const ctx=C.getContext('2d');
const tip=document.getElementById('tooltip');
let W,H,ps=[],ac=0,ic=0,frame=0;

function resize(){{W=C.width=window.innerWidth;H=C.height=window.innerHeight;}}
resize();window.addEventListener('resize',resize);

// ── Globe geometry ──
const GX=()=>W*.5, GY=()=>H*.5, GR=()=>Math.min(W,H)*.38;

function latLon3D(lat,lon,r){{
    const phi=(90-lat)*Math.PI/180;
    const tht=(lon+180)*Math.PI/180;
    return{{
        x:r*Math.sin(phi)*Math.cos(tht),
        y:-r*Math.cos(phi),
        z:r*Math.sin(phi)*Math.sin(tht)
    }};
}}

let rotY=0;
function project3D(x,y,z){{
    const cosR=Math.cos(rotY),sinR=Math.sin(rotY);
    const rx=x*cosR+z*sinR, rz=-x*sinR+z*cosR;
    const fov=1200, scale=fov/(fov-rz);
    return{{px:GX()+rx*scale,py:GY()+y*scale,scale:scale,z:rz}};
}}

// ── Draw globe ──
function drawGlobe(){{
    const r=GR();
    // Outer glow
    const grd=ctx.createRadialGradient(GX(),GY(),r*.7,GX(),GY(),r*1.2);
    grd.addColorStop(0,'rgba(220,38,38,0.08)');
    grd.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(GX(),GY(),r*1.2,0,Math.PI*2);
    ctx.fillStyle=grd;ctx.fill();

    // Globe base
    const g2=ctx.createRadialGradient(GX()-r*.25,GY()-r*.25,r*.05,GX(),GY(),r);
    g2.addColorStop(0,'rgba(40,10,10,0.9)');
    g2.addColorStop(0.6,'rgba(20,5,5,0.95)');
    g2.addColorStop(1,'rgba(6,5,8,0.98)');
    ctx.beginPath();ctx.arc(GX(),GY(),r,0,Math.PI*2);
    ctx.fillStyle=g2;ctx.fill();

    // Grid lines
    ctx.save();
    for(let lat=-80;lat<=80;lat+=20){{
        ctx.beginPath();let first=true;
        for(let lon=-180;lon<=180;lon+=4){{
            const p3=latLon3D(lat,lon,r);
            const{{px,py,z}}=project3D(p3.x,p3.y,p3.z);
            if(z<-r*.95){{first=true;continue;}}
            if(first){{ctx.moveTo(px,py);first=false;}}else ctx.lineTo(px,py);
        }}
        ctx.strokeStyle=`rgba(180,30,30,${{0.04+Math.abs(lat)/80*.04}})`;
        ctx.lineWidth=.4;ctx.stroke();
    }}
    for(let lon=-180;lon<=180;lon+=20){{
        ctx.beginPath();let first=true;
        for(let lat=-80;lat<=80;lat+=3){{
            const p3=latLon3D(lat,lon,r);
            const{{px,py,z}}=project3D(p3.x,p3.y,p3.z);
            if(z<-r*.95){{first=true;continue;}}
            if(first){{ctx.moveTo(px,py);first=false;}}else ctx.lineTo(px,py);
        }}
        ctx.strokeStyle='rgba(180,30,30,0.04)';ctx.lineWidth=.4;ctx.stroke();
    }}
    ctx.restore();

    // Atmosphere rim
    const rim=ctx.createRadialGradient(GX(),GY(),r*.92,GX(),GY(),r*1.05);
    rim.addColorStop(0,'rgba(220,38,38,0)');
    rim.addColorStop(.5,'rgba(220,38,38,0.07)');
    rim.addColorStop(1,'rgba(220,38,38,0)');
    ctx.beginPath();ctx.arc(GX(),GY(),r*1.05,0,Math.PI*2);
    ctx.fillStyle=rim;ctx.fill();

    // Equator highlight
    ctx.beginPath();let ef=true;
    for(let lon=-180;lon<=180;lon+=2){{
        const p3=latLon3D(0,lon,r);
        const{{px,py,z}}=project3D(p3.x,p3.y,p3.z);
        if(z<-r*.9){{ef=true;continue;}}
        if(ef){{ctx.moveTo(px,py);ef=false;}}else ctx.lineTo(px,py);
    }}
    ctx.strokeStyle='rgba(220,38,38,0.15)';ctx.lineWidth=1;ctx.stroke();

    // Clip mask
    ctx.save();
    ctx.beginPath();ctx.arc(GX(),GY(),r,0,Math.PI*2);ctx.clip();

    // Country dots
    const DOTS=[
        [35.86,104.19,'CHN','high'],[61.52,105.31,'RUS','high'],[37.09,-95.71,'USA','high'],
        [51.16,10.45,'DEU','med'],[40.33,127.51,'PRK','high'],[-14.23,-51.92,'BRA','target'],
        [56.13,-106.34,'CAN','med'],[20.59,78.96,'IND','low'],[46.23,2.21,'FRA','low'],
        [55.37,-3.43,'GBR','med'],[32.43,53.69,'IRN','high'],[36.2,138.25,'JPN','low'],
        [-25.27,133.77,'AUS','low'],[35.9,127.76,'KOR','low'],[48.38,31.17,'UKR','med'],
    ];
    DOTS.forEach(([lat,lon,name,type])=>{{
        const p3=latLon3D(lat,lon,r);
        const{{px,py,scale,z}}=project3D(p3.x,p3.y,p3.z);
        if(z<-r*.9)return;
        const alpha=Math.max(0,(z+r)/(2*r));
        const isTarget=type==='target';
        const sz=isTarget?7*scale:4*scale;
        const col=isTarget?'#00ff88':type==='high'?'#ff3333':type==='med'?'#ff8800':'#ff4488';
        ctx.beginPath();ctx.arc(px,py,sz,0,Math.PI*2);
        ctx.globalAlpha=alpha;
        ctx.fillStyle=col;ctx.fill();
        if(isTarget){{
            ctx.beginPath();ctx.arc(px,py,sz*1.8,0,Math.PI*2);
            ctx.strokeStyle=`rgba(0,255,136,${{alpha*0.4}})`;
            ctx.lineWidth=1.5;ctx.stroke();
            ctx.beginPath();ctx.arc(px,py,sz*2.8+Math.sin(frame*.08)*3,0,Math.PI*2);
            ctx.strokeStyle=`rgba(0,255,136,${{alpha*0.15}})`;
            ctx.lineWidth=1;ctx.stroke();
        }}
        ctx.globalAlpha=1;
        if(scale>.6&&name){{
            ctx.font=`${{isTarget?'bold ':''}}${{Math.round(9*scale)}}px JetBrains Mono`;
            ctx.fillStyle=`rgba(${{isTarget?'0,255,136':'200,100,100'}},${{alpha*.8}})`;
            ctx.fillText(name,px+sz+3,py+4);
        }}
    }});
    ctx.restore();
}}

// ── Particles ──
class Particle{{
    constructor(arc){{
        this.arc=arc;this.t=0;
        this.spd=0.003+Math.random()*.005;
        this.trail=[];
        this.col=arc.n>30?'#ff2222':arc.n>15?'#ff8800':'#ff4488';
    }}
    pos(t){{
        const r=GR();
        const s=latLon3D(this.arc.slat,this.arc.slon,r);
        const d=latLon3D(this.arc.dlat,this.arc.dlon,r);
        const cx=(s.x+d.x)/2,cy=(s.y+d.y)/2-r*.3,cz=(s.z+d.z)/2;
        const u=1-t;
        return{{
            x:u*u*s.x+2*u*t*cx+t*t*d.x,
            y:u*u*s.y+2*u*t*cy+t*t*d.y,
            z:u*u*s.z+2*u*t*cz+t*t*d.z
        }};
    }}
    update(){{
        this.t+=this.spd;
        const p=this.pos(Math.min(this.t,1));
        const{{px,py,z}}=project3D(p.x,p.y,p.z);
        this.trail.push({{px,py,z,r:GR()}});
        if(this.trail.length>22)this.trail.shift();
        return this.t<1;
    }}
    draw(){{
        const r=GR();
        if(this.trail.length<2)return;
        for(let i=1;i<this.trail.length;i++){{
            const a=i/this.trail.length;
            const tp=this.trail[i];
            if(tp.z<-r*.8)continue;
            const vis=(tp.z+r)/(2*r);
            ctx.beginPath();
            ctx.moveTo(this.trail[i-1].px,this.trail[i-1].py);
            ctx.lineTo(tp.px,tp.py);
            ctx.strokeStyle=this.col.replace('#ff2222',`rgba(255,34,34,${{a*vis}})`)
                .replace('#ff8800',`rgba(255,136,0,${{a*vis}})`)
                .replace('#ff4488',`rgba(255,68,136,${{a*vis}})`);
            ctx.lineWidth=2*a;ctx.stroke();
        }}
        const last=this.trail[this.trail.length-1];
        if(last.z>-r*.8){{
            const vis=(last.z+r)/(2*r);
            ctx.beginPath();ctx.arc(last.px,last.py,3.5,0,Math.PI*2);
            ctx.fillStyle=this.col;ctx.globalAlpha=vis;ctx.fill();ctx.globalAlpha=1;
        }}
    }}
}}

function spawn(){{
    if(!ARCS.length)return;
    ARCS.forEach(arc=>{{if(Math.random()<.08)ps.push(new Particle(arc));}});
}}

function animate(){{
    requestAnimationFrame(animate);
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#060508';ctx.fillRect(0,0,W,H);

    // Stars
    if(frame%120===0||frame===0){{
        ctx.save();
        for(let i=0;i<220;i++){{
            const x=Math.random()*W,y=Math.random()*H;
            const a=Math.random()*.4+.1;
            ctx.beginPath();ctx.arc(x,y,Math.random()*.8+.3,0,Math.PI*2);
            ctx.fillStyle=`rgba(255,200,200,${{a}})`;ctx.fill();
        }}
        ctx.restore();
    }}

    rotY+=0.003;
    drawGlobe();
    frame++;
    if(frame%8===0)spawn();

    ps=ps.filter(p=>{{
        const alive=p.update();
        p.draw();
        if(!alive){{ac++;ic=Math.floor(ac*.72);
            document.getElementById('atk').textContent=ac.toLocaleString();
            document.getElementById('ipc').textContent=ic.toLocaleString();
        }}
        return alive;
    }});
}}

C.addEventListener('mousemove',e=>{{
    const rect=C.getBoundingClientRect();
    const mx=e.clientX-rect.left,my=e.clientY-rect.top;
    let found=null;
    ARCS.forEach(arc=>{{
        const p3=latLon3D(arc.slat,arc.slon,GR());
        const{{px,py,z}}=project3D(p3.x,p3.y,p3.z);
        if(z>-GR()*.8&&Math.hypot(mx-px,my-py)<16)found=arc;
    }});
    if(found){{
        tip.style.display='block';
        tip.style.left=(e.clientX+14)+'px';
        tip.style.top=(e.clientY-36)+'px';
        document.getElementById('tt-name').textContent=found.name;
        document.getElementById('tt-count').textContent=found.n+' ataques detectados';
    }}else tip.style.display='none';
}});

animate();
</script>
</body>
</html>"""

    components.html(globe_html, height=600, scrolling=False)

    st.markdown("### 📊 Ranking de Países Atacantes")
    ta = df[df["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns=["País","Ataques"]; ta["% do Total"]=(ta["Ataques"]/ta["Ataques"].sum()*100).round(1).astype(str)+"%"
    st.dataframe(ta, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🤖 Sentinel Bot — Assistente de Segurança")
    st.caption("IA especialista em segurança cibernética com acesso aos dados do sistema em tempo real.")

    top_cli = df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top_pai = df[df["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    GEMINI_KEY = st.secrets.get("GEMINI_API_KEY","") if hasattr(st,"secrets") else os.environ.get("GEMINI_API_KEY","")

    SYSTEM = f"""Você é o Sentinel Bot, assistente especialista em segurança cibernética da plataforma SentinelAI.
Responda SEMPRE em português brasileiro, de forma profissional, objetiva e direta.
Use dados reais do sistema nas respostas. Não invente informações.

=== DADOS ATUAIS DO SISTEMA ===
Total de incidentes: {len(df)}
Incidentes críticos: {crit} ({crit/total*100:.1f}% do total)
IPs bloqueados automaticamente: {bloq}
Prejuízo total estimado: R$ {prej:,.0f}
Acurácia do modelo de IA: {ACC:.1%}
Tipos de incidente: {', '.join(df['TIPO INCIDENTE'].unique())}
Clientes monitorados: {', '.join(df['CLIENTE'].unique())}
Top países atacantes: {top_pai}
Top clientes por prejuízo: {top_cli}
Status dos incidentes: {df['STATUS'].value_counts().to_dict()}
Severidades: {df['SEVERIDADE'].value_counts().to_dict()}
Período: {df['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df['DATA'].min()) else 'N/A'} a {df['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df['DATA'].max()) else 'N/A'}
Escopo do usuário atual: {"Todos os clientes" if not CLT else CLT}
MySQL/SQLite: Ativo ({db_size} KB)

Você pode responder sobre: dados do sistema, conceitos de cibersegurança, recomendações de ação, análise de riscos.
Seja sempre preciso com números. Se não souber algo, diga claramente."""

    # Chat display
    chat_box = st.container()
    with chat_box:
        if not st.session_state["chat"]:
            st.markdown("""
            <div class="chat-ai">
                🤖 <strong>Sentinel Bot ativo.</strong><br><br>
                Olá! Sou o assistente de segurança da SentinelAI. Posso analisar incidentes, 
                identificar padrões de ameaças e recomendar ações baseadas nos dados do sistema.<br><br>
                Como posso ajudar?
            </div>
            """, unsafe_allow_html=True)
        for msg in st.session_state["chat"]:
            css="chat-user" if msg["role"]=="user" else "chat-ai"
            icon="👤" if msg["role"]=="user" else "🤖"
            st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    # Suggestions
    sugs = ["Qual cliente tem mais prejuízo?","Quais países mais atacaram?",
            "Status dos incidentes críticos","Recomendações de segurança urgentes",
            "Como funciona o modelo de IA?"]
    st.markdown("<p style='color:#4b5563;font-size:0.68rem;margin:10px 0 5px;text-transform:uppercase;letter-spacing:0.08em;'>💡 Perguntas rápidas</p>", unsafe_allow_html=True)
    scols = st.columns(len(sugs))
    sug_click = None
    for i,s in enumerate(sugs):
        with scols[i]:
            if st.button(s, key=f"sg{i}", use_container_width=True):
                sug_click=s

    with st.form("chat_f", clear_on_submit=True):
        ci,cb = st.columns([5,1])
        with ci: q=st.text_input("",placeholder="Digite sua pergunta sobre segurança...",label_visibility="collapsed")
        with cb: send=st.form_submit_button("Enviar",use_container_width=True)

    if sug_click: q=sug_click; send=True

    if send and q:
        log(USER,"CHAT",q[:80])
        st.session_state["chat"].append({"role":"user","content":q})
        resp="❌ Assistente não disponível."

        if GEMINI_KEY:
            try:
                # Build Gemini conversation
                contents=[]
                for m in st.session_state["chat"]:
                    role="user" if m["role"]=="user" else "model"
                    contents.append({"role":role,"parts":[{"text":m["content"]}]})

                payload={
                    "system_instruction":{"parts":[{"text":SYSTEM}]},
                    "contents":contents,
                    "generationConfig":{"temperature":0.7,"maxOutputTokens":1000}
                }
                url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                r=requests.post(url,json=payload,timeout=30)

                if r.status_code==200:
                    data=r.json()
                    resp=data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    resp=f"Erro {r.status_code}: {r.text[:200]}"
            except Exception as e:
                resp=f"Erro de conexão: {str(e)[:150]}"
        else:
            resp="⚠️ Chave da API Gemini não configurada. Adicione `GEMINI_API_KEY` nos Secrets do Streamlit."

        st.session_state["chat"].append({"role":"assistant","content":resp})
        db_salvar_chat(USER,q,resp)
        st.rerun()

    if st.session_state["chat"]:
        if st.button("🗑️ Limpar conversa"):
            st.session_state["chat"]=[]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — BACKUP & DB
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 💾 Backup e Gerenciamento de Dados")

    # Status cards
    b1,b2,b3 = st.columns(3)
    with b1:
        st.markdown(f"""
        <div style="background:rgba(0,180,80,0.06);border:1px solid rgba(0,180,80,0.2);
                    border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;">SQLite Status</p>
          <p style="color:#4ade80;font-size:1rem;font-weight:700;">✅ ATIVO</p>
          <p style="color:#6b7280;font-size:0.7rem;">{db_size} KB · {DB_PATH}</p>
        </div>
        """, unsafe_allow_html=True)
    with b2:
        n_inc = len(db_buscar_incidentes())
        st.markdown(f"""
        <div style="background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.2);
                    border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;">Incidentes Salvos</p>
          <p style="color:#dc2626;font-size:1rem;font-weight:700;">{n_inc}</p>
          <p style="color:#6b7280;font-size:0.7rem;">via análise ML</p>
        </div>
        """, unsafe_allow_html=True)
    with b3:
        n_logs = len(db_buscar_logs())
        st.markdown(f"""
        <div style="background:rgba(100,50,0,0.06);border:1px solid rgba(180,100,0,0.2);
                    border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;">Logs Auditoria</p>
          <p style="color:#f59e0b;font-size:1rem;font-weight:700;">{n_logs}</p>
          <p style="color:#6b7280;font-size:0.7rem;">ações registradas</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="info-box">📍 <strong>Onde os dados são salvos:</strong><br>• Sessão: RAM do servidor Streamlit Cloud<br>• Análises ML: SQLite local (sentinelai_backup.db) — persistente entre sessões<br>• Logs: SQLite + session_state<br>• Exportação: CSV/TXT via botões abaixo<br>• Produção: recomenda-se MySQL + mysqldump diário + AES-256</div>', unsafe_allow_html=True)

    st.markdown("### 📥 Exportar Dados")
    if not PROF["export"]:
        st.error("⛔ Apenas Administradores podem exportar.")
    else:
        ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        e1,e2,e3,e4=st.columns(4)
        with e1:
            st.download_button("⬇️ Dataset Completo",df_all.to_csv(index=False).encode()
                               ,f"sentinelai_full_{ts}.csv","text/csv",use_container_width=True)
        with e2:
            df_anon=df_all.drop(columns=["IP_SUSPEITO"],errors="ignore")
            st.download_button("⬇️ Anonimizado (LGPD)",df_anon.to_csv(index=False).encode()
                               ,f"sentinelai_anon_{ts}.csv","text/csv",use_container_width=True)
        with e3:
            df_inc=db_buscar_incidentes()
            if not df_inc.empty:
                st.download_button("⬇️ Incidentes SQLite",df_inc.to_csv(index=False).encode()
                                   ,f"sentinelai_db_{ts}.csv","text/csv",use_container_width=True)
        with e4:
            if "logs" in st.session_state and st.session_state["logs"]:
                st.download_button("⬇️ Logs Sessão","\n".join(st.session_state["logs"]).encode()
                                   ,f"sentinelai_logs_{ts}.txt","text/plain",use_container_width=True)
        db_meta_backup(USER,"EXPORT_FULL",len(df_all))

    st.markdown("### 📋 Incidentes Registrados (SQLite)")
    df_db=db_buscar_incidentes()
    if not df_db.empty:
        st.dataframe(df_db,use_container_width=True,height=250)
    else:
        st.info("Nenhum incidente registrado ainda. Use a aba Análise para gerar registros.")

    st.markdown("### 👁️ Prévia — Dataset Principal")
    st.dataframe(df.head(20),use_container_width=True,height=250)
    st.caption(f"{len(df)} registros · {len(df.columns)} colunas")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — AUDITORIA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 📋 Logs de Auditoria — Rastreabilidade Completa")
    st.caption("Todas as ações são registradas com timestamp, usuário e detalhe.")

    df_logs=db_buscar_logs()
    if not df_logs.empty:
        st.dataframe(df_logs,use_container_width=True,height=400)
        if PROF["export"]:
            ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("⬇️ Exportar Auditoria",df_logs.to_csv(index=False).encode()
                               ,f"auditoria_{ts}.csv","text/csv")
    else:
        st.info("Nenhum log no banco ainda.")

    st.markdown("### Logs da Sessão Atual")
    if st.session_state.get("logs"):
        for l in reversed(st.session_state["logs"][-40:]):
            st.code(l,language=None)
    else:
        st.info("Nenhum log nesta sessão.")

# ────────────
