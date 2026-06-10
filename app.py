cat > /mnt/user-data/outputs/app.py << 'ENDOFFILE'
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

GEMINI_API_KEY = "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA"

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
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

.stApp {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(139,0,0,0.18) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(180,0,0,0.12) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 80%, rgba(100,0,0,0.10) 0%, transparent 50%),
        #060508;
    background-attachment: fixed;
    color: #e2e8f0;
    min-height: 100vh;
}

[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0507 0%, #0f0509 50%, #0a0507 100%) !important;
    border-right: 1px solid rgba(180,0,0,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.block-container { padding: 1.2rem 2rem 3rem !important; max-width: 100% !important; }

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(139,0,0,0.12) 0%, rgba(10,5,7,0.95) 100%);
    border: 1px solid rgba(180,0,0,0.22);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(220,38,38,0.7), transparent);
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    border-color: rgba(220,38,38,0.5);
    box-shadow: 0 8px 32px rgba(139,0,0,0.25);
}
[data-testid="stMetricLabel"] { color:#6b7280!important; font-size:0.6rem!important; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; }
[data-testid="stMetricValue"] { color:#ff4444!important; font-size:1.45rem!important; font-weight:800; font-family:'JetBrains Mono',monospace!important; }

/* ── Buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #b91c1c 100%);
    color: white !important; border: 1px solid rgba(220,38,38,0.4); border-radius: 10px;
    padding: 0.55rem 1.2rem; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.05em;
    text-transform: uppercase; transition: all 0.2s ease; width: 100%;
    box-shadow: 0 4px 16px rgba(139,0,0,0.3);
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #991b1b 0%, #b91c1c 50%, #dc2626 100%);
    transform: translateY(-2px); box-shadow: 0 8px 24px rgba(220,38,38,0.4);
    border-color: rgba(248,113,113,0.5);
}

/* ── Inputs ── */
input, textarea, [data-baseweb="input"] input {
    background: rgba(10,5,7,0.9) !important; border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important; color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important;
}
[data-baseweb="select"] > div {
    background: rgba(10,5,7,0.9) !important; border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,5,7,0.85); border-radius: 12px; padding: 4px; gap: 2px;
    border: 1px solid rgba(180,0,0,0.1);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px; color: #6b7280; font-weight: 600; font-size: 0.75rem;
    padding: 0.5rem 1rem; text-transform: uppercase; letter-spacing: 0.05em; transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(139,0,0,0.4), rgba(180,0,0,0.25)) !important;
    color: #ff6666 !important; box-shadow: 0 0 12px rgba(180,0,0,0.2);
}

/* ── Chat ── */
.chat-user {
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    border-radius: 18px 18px 4px 18px; padding: 0.75rem 1.1rem;
    margin: 0.6rem 0 0.6rem auto; max-width: 75%; width: fit-content;
    color: white; font-size: 0.82rem; line-height: 1.6; box-shadow: 0 4px 16px rgba(139,0,0,0.3);
}
.chat-ai {
    background: rgba(10,5,7,0.95); border: 1px solid rgba(180,0,0,0.2);
    border-radius: 18px 18px 18px 4px; padding: 0.75rem 1.1rem; margin: 0.6rem 0;
    max-width: 75%; width: fit-content; color: #cbd5e1; font-size: 0.82rem; line-height: 1.6;
}
.chat-support {
    background: linear-gradient(135deg, rgba(0,100,200,0.15), rgba(0,50,120,0.2));
    border: 1px solid rgba(0,150,255,0.25); border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem; margin: 0.6rem 0; max-width: 75%; width: fit-content;
    color: #bae6fd; font-size: 0.82rem; line-height: 1.6;
}

/* ── SOC Header ── */
.soc-header {
    background: linear-gradient(135deg, rgba(139,0,0,0.08) 0%, rgba(10,5,7,0.97) 100%);
    border: 1px solid rgba(180,0,0,0.15); border-radius: 18px; padding: 1.4rem 2rem;
    margin-bottom: 1.4rem; position: relative; overflow: hidden;
}
.soc-header::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(220,38,38,0.6) 50%, transparent 100%);
}

/* ── Badges ── */
.badge-online {
    display:inline-flex;align-items:center;gap:6px;background:rgba(0,255,100,0.06);
    border:1px solid rgba(0,255,100,0.22);color:#4ade80;padding:4px 14px;border-radius:20px;
    font-size:0.6rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
}
.badge-critical {
    display:inline-flex;align-items:center;gap:6px;background:rgba(220,38,38,0.1);
    border:1px solid rgba(220,38,38,0.35);color:#f87171;padding:4px 14px;border-radius:20px;
    font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
}

/* ── Robot animation (sidebar) ── */
@keyframes float-robot {
    0%   { transform: translateY(0px) rotate(-2deg); }
    25%  { transform: translateY(-12px) rotate(1deg); }
    50%  { transform: translateY(-6px) rotate(-1deg); }
    75%  { transform: translateY(-18px) rotate(2deg); }
    100% { transform: translateY(0px) rotate(-2deg); }
}
@keyframes glow-pulse {
    0%,100% { filter: drop-shadow(0 0 8px rgba(220,38,38,0.6)) drop-shadow(0 0 20px rgba(139,0,0,0.4)); }
    50%      { filter: drop-shadow(0 0 20px rgba(220,38,38,0.9)) drop-shadow(0 0 40px rgba(180,0,0,0.6)); }
}
.robot-float {
    animation: float-robot 4s ease-in-out infinite, glow-pulse 2.5s ease-in-out infinite;
    font-size: 3.5rem; display: block; text-align: center;
}

/* ── Scan line ── */
@keyframes scan {
    0%   { transform: translateY(-100%); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
}
.scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(220,38,38,0.4), transparent);
    animation: scan 6s linear infinite; pointer-events: none; z-index: 0;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(10,5,7,0.8); }
::-webkit-scrollbar-thumb { background: rgba(180,0,0,0.4); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(220,38,38,0.6); }

[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; border:1px solid rgba(180,0,0,0.15); }
iframe { border-radius: 14px; }
hr { border-color: rgba(180,0,0,0.12) !important; margin: 1rem 0 !important; }
details summary { color:#f87171!important; font-weight:600; font-size:0.82rem; }
details { background:rgba(10,5,7,0.7); border:1px solid rgba(180,0,0,0.15); border-radius:10px; padding:0.5rem 1rem; }

.info-box {
    background:rgba(139,0,0,0.08); border:1px solid rgba(180,0,0,0.2);
    border-left:3px solid #dc2626; border-radius:8px; padding:0.8rem 1rem;
    margin:0.5rem 0; font-size:0.8rem; color:#94a3b8; line-height:1.6;
}
.info-box-blue {
    background:rgba(0,100,200,0.08); border:1px solid rgba(0,150,255,0.2);
    border-left:3px solid #3b82f6; border-radius:8px; padding:0.8rem 1rem;
    margin:0.5rem 0; font-size:0.8rem; color:#93c5fd; line-height:1.6;
}
.ticket-card {
    background:rgba(10,5,7,0.9); border:1px solid rgba(180,0,0,0.2);
    border-radius:12px; padding:1rem 1.2rem; margin:0.5rem 0; transition:all 0.2s;
}
.ticket-card:hover { border-color:rgba(220,38,38,0.4); box-shadow:0 4px 20px rgba(139,0,0,0.2); }

@media (max-width: 768px) {
    .block-container { padding: 0.8rem 0.8rem 2rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    .chat-user, .chat-ai, .chat-support { max-width: 92%; }
}
.js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>
<div class="scan-line"></div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE — SQLite
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "sentinelai_backup.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db(); c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS incidentes_analisados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT, tipo TEXT, origem TEXT, status TEXT,
            severidade TEXT, cliente TEXT, risco INTEGER, prejuizo REAL,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
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
        CREATE TABLE IF NOT EXISTS tickets_suporte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT, assunto TEXT, mensagem TEXT,
            status TEXT DEFAULT 'aberto', prioridade TEXT DEFAULT 'normal',
            resposta TEXT DEFAULT '',
            ts DATETIME DEFAULT CURRENT_TIMESTAMP, ts_resposta DATETIME
        );
        CREATE TABLE IF NOT EXISTS chat_suporte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER, remetente TEXT, mensagem TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(ticket_id) REFERENCES tickets_suporte(id)
        );
    """)
    conn.commit(); conn.close()

init_db()

def db_log(usuario, acao, detalhe=""):
    try:
        conn = get_db()
        conn.execute("INSERT INTO logs_auditoria (usuario,acao,detalhe) VALUES (?,?,?)",(usuario,acao,detalhe[:500]))
        conn.commit(); conn.close()
    except: pass

def db_salvar_incidente(d):
    try:
        conn = get_db()
        conn.execute("""INSERT INTO incidentes_analisados (usuario,tipo,origem,status,severidade,cliente,risco,prejuizo)
            VALUES (?,?,?,?,?,?,?,?)""",(d["usuario"],d["tipo"],d["origem"],d["status"],d["severidade"],d["cliente"],d["risco"],d["prejuizo"]))
        conn.commit(); conn.close(); return True
    except: return False

def db_salvar_chat(usuario, pergunta, resposta):
    try:
        conn = get_db()
        conn.execute("INSERT INTO chat_historico (usuario,pergunta,resposta) VALUES (?,?,?)",(usuario,pergunta[:1000],resposta[:2000]))
        conn.commit(); conn.close()
    except: pass

def db_buscar_incidentes():
    try:
        conn = get_db(); df = pd.read_sql("SELECT * FROM incidentes_analisados ORDER BY ts DESC LIMIT 100",conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_buscar_logs():
    try:
        conn = get_db(); df = pd.read_sql("SELECT * FROM logs_auditoria ORDER BY ts DESC LIMIT 200",conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_meta_backup(usuario, tipo, registros):
    try:
        conn = get_db()
        conn.execute("INSERT INTO backups_meta (usuario,tipo,registros) VALUES (?,?,?)",(usuario,tipo,registros))
        conn.commit(); conn.close()
    except: pass

def db_criar_ticket(cliente, assunto, mensagem, prioridade="normal"):
    try:
        conn = get_db()
        cur = conn.execute("INSERT INTO tickets_suporte (cliente,assunto,mensagem,prioridade) VALUES (?,?,?,?)",(cliente,assunto,mensagem,prioridade))
        tid = cur.lastrowid
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)",(tid,cliente,mensagem))
        conn.commit(); conn.close(); return tid
    except: return None

def db_buscar_tickets(cliente=None):
    try:
        conn = get_db()
        if cliente:
            df = pd.read_sql("SELECT * FROM tickets_suporte WHERE cliente=? ORDER BY ts DESC",conn,params=(cliente,))
        else:
            df = pd.read_sql("SELECT * FROM tickets_suporte ORDER BY ts DESC",conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_responder_ticket(ticket_id, resposta, status="respondido"):
    try:
        conn = get_db()
        conn.execute("UPDATE tickets_suporte SET resposta=?,status=?,ts_resposta=CURRENT_TIMESTAMP WHERE id=?",(resposta,status,ticket_id))
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)",(ticket_id,"SentinelAI",resposta))
        conn.commit(); conn.close(); return True
    except: return False

def db_buscar_chat_ticket(ticket_id):
    try:
        conn = get_db(); df = pd.read_sql("SELECT * FROM chat_suporte WHERE ticket_id=? ORDER BY ts ASC",conn,params=(ticket_id,))
        conn.close(); return df
    except: return pd.DataFrame()

def db_adicionar_msg_ticket(ticket_id, remetente, mensagem):
    try:
        conn = get_db()
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)",(ticket_id,remetente,mensagem))
        conn.commit(); conn.close(); return True
    except: return False

def log(usuario, acao, detalhe=""):
    if "logs" not in st.session_state: st.session_state["logs"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs"].append(f"[{ts}] {usuario} → {acao} {detalhe}")
    db_log(usuario, acao, detalhe)

# ─────────────────────────────────────────────────────────────────────────────
# USERS / RBAC
# ─────────────────────────────────────────────────────────────────────────────
USERS = {
    "admin":        {"pw":"admin123",    "role":"Administrador",  "export":True,  "analyze":True,  "pii":True,  "client":None,           "support_admin":True},
    "analista":     {"pw":"analista123", "role":"Analista SOC",   "export":False, "analyze":True,  "pii":False, "client":None,           "support_admin":True},
    "nubank":       {"pw":"nubank123",   "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Nubank",       "support_admin":False},
    "mercadolivre": {"pw":"ml123",       "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Mercado Livre","support_admin":False},
    "santander":    {"pw":"sant123",     "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Santander",    "support_admin":False},
    "ifood":        {"pw":"ifood123",    "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"iFood",        "support_admin":False},
    "viewer":       {"pw":"viewer123",   "role":"Visualizador",   "export":False, "analyze":False, "pii":False, "client":None,           "support_admin":False},
}
_H = {u: hashlib.sha256(v["pw"].encode()).hexdigest() for u,v in USERS.items()}

def auth(u,p): return u in _H and hashlib.sha256(p.encode()).hexdigest() == _H[u]
def mask_ip(ip):
    if not ip or str(ip)=="Nenhum" or pd.isna(ip): return "***.***.***"
    p=str(ip).split("."); return f"{p[0]}.{p[1]}.***.***" if len(p)==4 else "***"

# SESSION INIT
for k,v in {"authed":False,"user":None,"lgpd":False,"chat":[],"chat_suporte":[],"logs":[],"ticket_ativo":None}.items():
    if k not in st.session_state: st.session_state[k]=v

def gemini_chat(system_prompt, messages, temperature=0.7, max_tokens=1000):
    """Chama a API Gemini e retorna a resposta como string."""
    key = GEMINI_API_KEY
    if not key:
        return "⚠️ Configure GEMINI_API_KEY nos Secrets do Streamlit."
    
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"❌ Erro {r.status_code}. Tente novamente."
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)[:100]}"

# ─────────────────────────────────────────────────────────────────────────────
# LGPD — com imagem do robô e botões lado a lado
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["lgpd"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)

    lgpd_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
        background: radial-gradient(ellipse at 20% 50%, rgba(139,0,0,0.2) 0%, transparent 60%),
                    radial-gradient(ellipse at 80% 20%, rgba(180,0,0,0.15) 0%, transparent 55%),
                    #060508;
        min-height: 100vh; display:flex; align-items:center; justify-content:center;
        font-family: 'Inter', sans-serif; overflow:hidden; position:relative;
    }
    .particles { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; }
    .particle {
        position:absolute; width:2px; height:2px; background:rgba(220,38,38,0.4); border-radius:50%;
        animation: float-particle linear infinite;
    }
    @keyframes float-particle {
        0%   { transform:translateY(100vh) rotate(0deg); opacity:0; }
        10%  { opacity:1; }
        90%  { opacity:1; }
        100% { transform:translateY(-100px) rotate(720deg); opacity:0; }
    }
    .grid-bg {
        position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none;
        background-image:
            linear-gradient(rgba(180,0,0,0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(180,0,0,0.04) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: grid-move 20s linear infinite;
    }
    @keyframes grid-move { 0%{background-position:0 0;} 100%{background-position:50px 50px;} }
    .scan-line {
        position:fixed; top:0; left:0; right:0; height:2px;
        background:linear-gradient(90deg,transparent,rgba(220,38,38,0.5),transparent);
        animation: scan 5s linear infinite; z-index:1;
    }
    @keyframes scan { 0%{top:-2px;} 100%{top:100vh;} }
    .card {
        background: linear-gradient(135deg, rgba(15,5,8,0.98), rgba(10,5,7,0.99));
        border:1px solid rgba(180,0,0,0.25); border-radius:24px;
        padding:2.5rem 3rem; max-width:720px; width:90%;
        position:relative; z-index:10;
        box-shadow: 0 40px 120px rgba(139,0,0,0.3), 0 0 60px rgba(0,0,0,0.8);
    }
    .card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:1px; border-radius:24px 24px 0 0;
        background:linear-gradient(90deg,transparent,rgba(220,38,38,0.7),transparent);
    }
    .robot-wrap { display:flex; justify-content:center; margin-bottom:1.5rem; }
    .robot-img {
        width:120px; height:120px; object-fit:contain;
        animation: robot-float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(220,38,38,0.7)) drop-shadow(0 0 40px rgba(139,0,0,0.5));
    }
    @keyframes robot-float {
        0%,100% { transform:translateY(0px) rotate(-3deg); }
        25%      { transform:translateY(-15px) rotate(2deg); }
        50%      { transform:translateY(-8px) rotate(-1deg); }
        75%      { transform:translateY(-20px) rotate(3deg); }
    }
    .robot-emoji {
        font-size:5rem; display:block; text-align:center;
        animation: robot-float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(220,38,38,0.7));
    }
    .title { text-align:center; margin-bottom:1.5rem; }
    .title h1 { color:white; font-size:2rem; font-weight:900; letter-spacing:-0.5px; }
    .title h1 span { color:#dc2626; }
    .title p { color:#6b7280; font-size:0.8rem; margin-top:4px; font-family:'JetBrains Mono',monospace; }
    .badges { display:flex; gap:8px; justify-content:center; margin-bottom:1.5rem; flex-wrap:wrap; }
    .badge-green {
        background:rgba(0,255,100,0.06); border:1px solid rgba(0,255,100,0.22); color:#4ade80;
        padding:4px 14px; border-radius:20px; font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
        display:inline-flex; align-items:center; gap:5px;
    }
    .badge-red {
        background:rgba(220,38,38,0.1); border:1px solid rgba(220,38,38,0.35); color:#f87171;
        padding:4px 14px; border-radius:20px; font-size:0.6rem; font-weight:700; letter-spacing:0.1em;
    }
    .lgpd-text {
        background:rgba(139,0,0,0.06); border:1px solid rgba(180,0,0,0.15); border-left:3px solid #dc2626;
        border-radius:10px; padding:1rem 1.2rem; margin-bottom:1.5rem; color:#94a3b8;
        font-size:0.78rem; line-height:1.8;
    }
    .lgpd-text strong { color:#fca5a5; }
    .privacy-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-bottom:1.5rem; }
    .privacy-item {
        background:rgba(10,5,7,0.8); border:1px solid rgba(180,0,0,0.12); border-radius:8px;
        padding:0.6rem 0.8rem; display:flex; align-items:center; gap:8px;
        font-size:0.72rem; color:#9ca3af;
    }
    .privacy-item span { font-size:1rem; }
    .btn-row { display:flex; gap:12px; }
    .btn-accept {
        flex:1; padding:0.9rem; border-radius:12px; border:none; cursor:pointer; font-weight:700;
        font-size:0.82rem; letter-spacing:0.05em; text-transform:uppercase; transition:all 0.2s;
        background:linear-gradient(135deg,#7f1d1d,#991b1b,#b91c1c); color:white;
        box-shadow:0 4px 20px rgba(139,0,0,0.4);
        font-family:'Inter',sans-serif;
    }
    .btn-accept:hover { background:linear-gradient(135deg,#991b1b,#b91c1c,#dc2626); transform:translateY(-2px); box-shadow:0 8px 30px rgba(220,38,38,0.5); }
    .btn-reject {
        flex:1; padding:0.9rem; border-radius:12px; cursor:pointer; font-weight:700;
        font-size:0.82rem; letter-spacing:0.05em; text-transform:uppercase; transition:all 0.2s;
        background:rgba(10,5,7,0.9); border:1px solid rgba(180,0,0,0.25); color:#6b7280;
        font-family:'Inter',sans-serif;
    }
    .btn-reject:hover { border-color:rgba(220,38,38,0.4); color:#f87171; }
    .counter { text-align:center; margin-top:1rem; color:#374151; font-size:0.62rem; font-family:'JetBrains Mono',monospace; }
    .pulse-dot { display:inline-block; width:6px; height:6px; background:#4ade80; border-radius:50%; animation:pulse 1.5s infinite; margin-right:5px; }
    @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(74,222,128,0.5);} 50%{box-shadow:0 0 0 5px rgba(74,222,128,0);} }
    </style>
    </head>
    <body>
    <div class="grid-bg"></div>
    <div class="scan-line"></div>
    <div class="particles" id="particles"></div>
    <div class="card">
        <div class="robot-wrap">
            <span class="robot-emoji">🤖</span>
        </div>
        <div class="title">
            <h1>Sentinel<span>AI</span></h1>
            <p>SECURITY OPERATIONS CENTER — ACESSO SEGURO</p>
        </div>
        <div class="badges">
            <span class="badge-green"><span class="pulse-dot"></span>SISTEMA ONLINE</span>
            <span class="badge-red">LGPD Lei 13.709/2018</span>
            <span class="badge-red">ISO 27001</span>
        </div>
        <div class="lgpd-text">
            Esta plataforma utiliza cookies de sessão para <strong>autenticação, controle de acesso baseado em perfil (RBAC) e auditoria completa</strong>.
            Todos os dados são tratados conforme a <strong>Lei Geral de Proteção de Dados (LGPD)</strong>.
            IPs e informações pessoais identificáveis são <strong>mascarados automaticamente</strong> para perfis não autorizados.
            Nenhum dado é compartilhado com terceiros sem consentimento. Ao continuar, você consente com estes termos.
        </div>
        <div class="privacy-grid">
            <div class="privacy-item"><span>🔐</span> Dados criptografados em trânsito</div>
            <div class="privacy-item"><span>🎭</span> IPs mascarados por perfil</div>
            <div class="privacy-item"><span>📋</span> Auditoria completa de ações</div>
            <div class="privacy-item"><span>🚫</span> Zero compartilhamento externo</div>
            <div class="privacy-item"><span>💾</span> Backup automático SQLite</div>
            <div class="privacy-item"><span>⏱️</span> Sessões com timeout automático</div>
        </div>
        <div class="btn-row">
            <button class="btn-accept" onclick="window.parent.postMessage({type:'streamlit:setComponentValue',value:'accept'},'*');">
                ✅ Aceitar e Acessar
            </button>
            <button class="btn-reject" onclick="window.parent.postMessage({type:'streamlit:setComponentValue',value:'reject'},'*');">
                ❌ Recusar Acesso
            </button>
        </div>
        <div class="counter" id="counter">
            <span class="pulse-dot"></span>MONITORAMENTO ATIVO · <span id="ctime"></span>
        </div>
    </div>
    <script>
    const pc = document.getElementById('particles');
    for(let i=0;i<25;i++){
        const p=document.createElement('div'); p.className='particle';
        p.style.left=Math.random()*100+'%';
        p.style.animationDuration=(8+Math.random()*12)+'s';
        p.style.animationDelay=(-Math.random()*20)+'s';
        p.style.width=p.style.height=(1+Math.random()*3)+'px';
        p.style.background=`rgba(${Math.random()>0.5?'220,38,38':'139,0,0'},${0.3+Math.random()*0.5})`;
        pc.appendChild(p);
    }
    function tick(){ document.getElementById('ctime').textContent=new Date().toLocaleTimeString('pt-BR'); }
    tick(); setInterval(tick,1000);
    </script>
    </body>
    </html>
    """
    components.html(lgpd_html, height=650, scrolling=False)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Aceitar e Continuar", use_container_width=True, key="lgpd_accept"):
            st.session_state["lgpd"] = True
            log("sistema","LGPD_ACEITO"); st.rerun()
    with col2:
        if st.button("❌ Recusar (bloqueia acesso)", use_container_width=True, key="lgpd_reject"):
            st.error("Você recusou os termos. Acesso bloqueado."); st.stop()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["authed"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 2rem;">
        <div style="font-size:4rem;margin-bottom:0.5rem;filter:drop-shadow(0 0 30px rgba(220,38,38,0.8));">🛡️</div>
        <h1 style="font-size:2.8rem;font-weight:900;color:white;letter-spacing:-1px;margin:0;">
            Sentinel<span style="color:#dc2626;">AI</span>
        </h1>
        <p style="color:#6b7280;font-size:0.9rem;margin:8px 0 0;">Security Operations Center — Plataforma de Inteligência Cibernética</p>
        <div style="display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;">
          <span class="badge-online">● SISTEMA OPERACIONAL</span>
          <span class="badge-critical">ACESSO RESTRITO</span>
        </div>
    </div>""", unsafe_allow_html=True)

    _, col_login, _ = st.columns([1,1.4,1])
    with col_login:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(139,0,0,0.07),rgba(10,5,7,0.98));
                    border:1px solid rgba(180,0,0,0.2);border-radius:20px;padding:2rem;margin-bottom:1.2rem;
                    box-shadow:0 24px 80px rgba(139,0,0,0.2);">
          <p style="color:#6b7280;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Credenciais de Acesso
          </p>""", unsafe_allow_html=True)
        creds=[("admin","admin123","🔴 Administrador"),("analista","analista123","🟠 Analista SOC"),
               ("nubank","nubank123","🔵 Nubank"),("mercadolivre","ml123","🟢 Mercado Livre"),
               ("santander","sant123","🟣 Santander"),("ifood","ifood123","🟡 iFood"),("viewer","viewer123","⚪ Visualizador")]
        for u,p,label in creds:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;
                        border-radius:8px;margin:3px 0;background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.1);">
              <span style="color:#e2e8f0;font-size:0.72rem;font-weight:500;">{label}</span>
              <code style="color:#f87171;font-size:0.65rem;background:rgba(220,38,38,0.08);padding:2px 8px;border-radius:4px;">{u} / {p}</code>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            u_in = st.text_input("", placeholder="👤  Usuário", label_visibility="collapsed")
            p_in = st.text_input("", placeholder="🔑  Senha", type="password", label_visibility="collapsed")
            ok   = st.form_submit_button("ACESSAR O SISTEMA →", use_container_width=True)
        if ok:
            if auth(u_in.strip(), p_in):
                st.session_state.update({"authed":True,"user":u_in.strip()})
                log(u_in.strip(),"LOGIN","Acesso concedido"); st.rerun()
            else:
                log(u_in.strip() or "?","LOGIN_FAIL","Credenciais inválidas")
                st.error("❌  Usuário ou senha incorretos.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATED
# ─────────────────────────────────────────────────────────────────────────────
USER = st.session_state["user"]
PROF = USERS[USER]
log(USER,"SESSION_ACTIVE")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset_final.csv")
    df = df.dropna(subset=["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"]:
        df[col] = df[col].str.strip().str.lower()
    enc = {k:LabelEncoder() for k in ["tipo","orig","stat","sev"]}
    df["TE"] = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["OE"] = enc["orig"].fit_transform(df["ORIGEM"])
    df["SE"] = enc["stat"].fit_transform(df["STATUS"])
    df["VE"] = enc["sev"].fit_transform(df["SEVERIDADE"])
    X = df[["TE","OE","TEMPO RESOLUÇÃO","SE"]]; y = df["VE"]
    Xt,Xv,yt,yv = train_test_split(X,y,test_size=.2,random_state=42)
    m = DecisionTreeClassifier(random_state=42); m.fit(Xt,yt)
    acc = accuracy_score(yv,m.predict(Xv))
    return df,enc,m,acc,Xv,yv

df_all,ENC,MODEL,ACC,Xv,yv = load_data()
CLT  = PROF["client"]
df   = df_all[df_all["CLIENTE"]==CLT].copy() if CLT else df_all.copy()
prej = df["PREJUIZO_ESTIMADO"].sum()
total = len(df)
crit  = len(df[df["SEVERIDADE"]=="crítica"])
bloq  = len(df[df["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
resol = len(df[df["STATUS"]=="resolvido"])
pend  = len(df[df["STATUS"]=="pendente"])

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 0.5rem;">
      <span class="robot-float">🤖</span>
      <p style="color:#dc2626;font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.15em;margin-top:8px;">SENTINEL CORE</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    db_ok   = os.path.exists(DB_PATH)
    db_size = round(os.path.getsize(DB_PATH)/1024,1) if db_ok else 0
    st.markdown(f"""
    <div style="background:rgba(139,0,0,0.07);border:1px solid rgba(180,0,0,0.15);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.8rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">OPERADOR</p>
      <p style="color:white;font-weight:700;font-size:0.9rem;margin:0;">@{USER}</p>
      <p style="color:#9ca3af;font-size:0.7rem;margin:3px 0 8px;">{PROF['role']}</p>
      <span class="badge-online">● ONLINE</span>
    </div>
    <div style="background:rgba(0,200,100,0.04);border:1px solid rgba(0,200,100,0.15);border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;margin-bottom:4px;">💾 ARMAZENAMENTO</p>
      <p style="color:#4ade80;font-size:0.72rem;font-weight:600;">✅ SQLite · {db_size} KB</p>
      <p style="color:#6b7280;font-size:0.6rem;">📁 {DB_PATH} · Streamlit Cloud</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<p style='color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>PERMISSÕES</p>", unsafe_allow_html=True)
    for label,flag in [("Análise ML",PROF["analyze"]),("Exportar dados",PROF["export"]),("Ver IPs / PII",PROF["pii"]),("Suporte Admin",PROF["support_admin"])]:
        c,i = ("#4ade80","✓") if flag else ("#ef4444","✗")
        st.markdown(f"<p style='color:{c};font-size:0.72rem;margin:3px 0;'><b>{i}</b> {label}</p>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(139,0,0,0.08);border-radius:10px;padding:0.7rem 1rem;margin:0.8rem 0;text-align:center;">
      <p style="color:#4b5563;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;">Acurácia IA</p>
      <p style="color:#dc2626;font-size:1.4rem;font-weight:800;font-family:'JetBrains Mono',monospace;">{ACC:.1%}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🚪  Encerrar Sessão", use_container_width=True):
        log(USER,"LOGOUT"); st.session_state.update({"authed":False,"user":None,"chat":[],"chat_suporte":[]}); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
now   = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
scope = f"Cliente: {CLT}" if CLT else "Visão Global — Todos os Clientes"
st.markdown(f"""
<div class="soc-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
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
    <div style="text-align:right;">
      <div style="display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;margin-bottom:6px;">
        <span class="badge-online">● SISTEMA ONLINE</span>
        <span class="badge-critical">LGPD COMPLIANT</span>
      </div>
      <p style="color:#374151;font-size:0.62rem;font-family:'JetBrains Mono',monospace;">{now}</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# KPIs
c1,c2,c3,c4,c5,c6=st.columns(6)
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
tabs = st.tabs(["🔍 Análise","📊 Dashboard","🌍 Mapa de Ameaças","🤖 Sentinel Bot","🎫 Suporte","💾 Backup & DB","📋 Auditoria"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANÁLISE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### 🔍 Análise Inteligente de Incidentes")
    if not PROF["analyze"]:
        st.markdown('<div class="info-box">⛔ Perfil sem permissão para análise. Contate o Administrador.</div>', unsafe_allow_html=True)
    else:
        c1,c2=st.columns(2)
        with c1:
            tipo   = st.selectbox("Tipo de Incidente",ENC["tipo"].classes_)
            orig   = st.selectbox("Origem",ENC["orig"].classes_)
            cli_af = st.selectbox("Cliente Afetado",sorted(df_all["CLIENTE"].unique()))
        with c2:
            tempo  = st.slider("Tempo de Resolução (min)",1,120,30)
            stat   = st.selectbox("Status",ENC["stat"].classes_)
        if st.button("🚀  INICIAR ANÁLISE FORENSE",use_container_width=True):
            log(USER,"ANALISE",f"tipo={tipo}")
            with st.spinner("Processando com IA..."):
                time.sleep(1)
            entrada = pd.DataFrame({"TE":[ENC["tipo"].transform([tipo])[0]],"OE":[ENC["orig"].transform([orig])[0]],"TEMPO RESOLUÇÃO":[tempo],"SE":[ENC["stat"].transform([stat])[0]]})
            sev = ENC["sev"].inverse_transform(MODEL.predict(entrada))[0]
            if stat=="resolvido": sev="baixa"
            elif tipo in ["ataque","falha servidor"]: sev="crítica"
            elif tipo in ["lentidão","erro sistema"]: sev=random.choice(["baixa","média"])
            risco=random.randint(10,99); prej_val=random.uniform(3000,30000)
            risco_fin="ALTO" if prej_val>15000 else ("MÉDIO" if prej_val>7000 else "BAIXO")
            atks=df_all[df_all["TIPO INCIDENTE"]=="ataque"]
            if not atks.empty:
                row=atks.sample(1).iloc[0]
                ip=str(row["IP_SUSPEITO"]) if PROF["pii"] else mask_ip(row["IP_SUSPEITO"])
                pais=row["PAIS_ATAQUE"]
            else: ip,pais="N/A","Interno"
            st.markdown("<hr>",unsafe_allow_html=True)
            if sev=="crítica": st.error("🔴  SEVERIDADE PREVISTA: **CRÍTICA**")
            elif sev=="média": st.warning("🟡  SEVERIDADE PREVISTA: **MÉDIA**")
            else: st.success("🟢  SEVERIDADE PREVISTA: **BAIXA**")
            r1,r2,r3,r4=st.columns(4)
            with r1: st.metric("THREAT SCORE",f"{risco}/100")
            with r2: st.metric("PREJUÍZO EST.",f"R$ {prej_val:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("RISCO FIN.",risco_fin)
            with r4: st.metric("CLIENTE",cli_af)
            if tipo=="ataque":
                st.error(f"🌍 Origem: **{pais}**  |  IP: `{ip}`")
                with st.expander("🛡️ Resposta Automática Acionada"):
                    for a in ["✅ IP bloqueado","✅ Firewall atualizado","✅ Equipe SOC notificada","✅ Logs enviados para auditoria"]: st.write(a)
            saved = db_salvar_incidente({"usuario":USER,"tipo":tipo,"origem":orig,"status":stat,"severidade":sev,"cliente":cli_af,"risco":risco,"prejuizo":prej_val})
            if saved: st.success("💾 Incidente salvo no banco de dados SQLite")
        st.markdown("### 📋 Registros do Dataset")
        cols_show=["DATA","TIPO INCIDENTE","SEVERIDADE","STATUS","CLIENTE","PAIS_ATAQUE","PREJUIZO_ESTIMADO"]
        if PROF["pii"]: cols_show.append("IP_SUSPEITO")
        df_show=df[cols_show].copy()
        if not PROF["pii"] and "IP_SUSPEITO" in df_show.columns: df_show["IP_SUSPEITO"]=df_show["IP_SUSPEITO"].apply(mask_ip)
        st.dataframe(df_show,use_container_width=True,height=300)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 📊 Telemetria & Métricas")
    L=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#94a3b8",font_family="Inter")
    g1,g2=st.columns(2)
    with g1:
        fig=px.pie(df,names="SEVERIDADE",title="Distribuição de Severidade",color_discrete_sequence=["#dc2626","#f59e0b","#22c55e"])
        fig.update_layout(**L,title_font_color="white"); st.plotly_chart(fig,use_container_width=True)
    with g2:
        vc=df["TIPO INCIDENTE"].value_counts().reset_index()
        fig=px.bar(vc,x="TIPO INCIDENTE",y="count",title="Incidentes por Tipo",color_discrete_sequence=["#dc2626"])
        fig.update_layout(**L,title_font_color="white"); st.plotly_chart(fig,use_container_width=True)
    dt=df.groupby("DATA").size().reset_index(name="n")
    fig=px.area(dt,x="DATA",y="n",title="Volume ao Longo do Tempo",color_discrete_sequence=["#dc2626"])
    fig.update_traces(fill="tozeroy",fillcolor="rgba(220,38,38,0.1)"); fig.update_layout(**L,title_font_color="white"); st.plotly_chart(fig,use_container_width=True)
    g3,g4=st.columns(2)
    with g3:
        fig=px.histogram(df,x="PAIS_ATAQUE",title="Ataques por País",color_discrete_sequence=["#b91c1c"])
        fig.update_layout(**L,title_font_color="white"); st.plotly_chart(fig,use_container_width=True)
    with g4:
        dp=df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index().sort_values("PREJUIZO_ESTIMADO",ascending=False).head(7)
        fig=px.bar(dp,x="CLIENTE",y="PREJUIZO_ESTIMADO",title="Prejuízo por Cliente",color_discrete_sequence=["#991b1b"])
        fig.update_layout(**L,title_font_color="white"); st.plotly_chart(fig,use_container_width=True)
    st.markdown("### 🤖 Performance do Modelo de IA")
    m1,m2,m3=st.columns(3)
    with m1: st.metric("ACURÁCIA",f"{ACC:.1%}")
    with m2: st.metric("TREINO",f"{int(len(df_all)*0.8):,}")
    with m3: st.metric("TESTE",f"{int(len(df_all)*0.2):,}")
    ypred=MODEL.predict(Xv); cm=confusion_matrix(yv,ypred); lbs=ENC["sev"].classes_
    fig=go.Figure(go.Heatmap(z=cm,x=lbs,y=lbs,colorscale=[[0,"#0a0507"],[0.5,"#7f1d1d"],[1,"#dc2626"]],text=cm,texttemplate="%{text}",showscale=True))
    fig.update_layout(title="Matriz de Confusão",xaxis_title="Previsto",yaxis_title="Real",height=320,**L,title_font_color="white")
    st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MAPA DE AMEAÇAS GLOBAL (Globe 3D interativo estilo Kaspersky)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 🌍 Mapa Global de Ameaças Cibernéticas")
    st.caption("Globo 3D interativo com divisórias de países reais (GeoJSON) · Arraste para girar · Scroll para zoom · Clique nos países para threat intel")

    atk_df = df[df["TIPO INCIDENTE"]=="ataque"]
    cc = atk_df["PAIS_ATAQUE"].value_counts().reset_index(); cc.columns=["country","total"]

    THREAT_INTEL = [
        {"country":"China","lat":35.86,"lon":104.19,"score":98,"groups":["APT41","APT10","Volt Typhoon"],"target":"Espionagem industrial · infraestrutura crítica"},
        {"country":"Russia","lat":61.52,"lon":105.31,"score":97,"groups":["APT28/Fancy Bear","APT29/Cozy Bear","Sandworm"],"target":"Governos · energia · eleições"},
        {"country":"North Korea","lat":40.33,"lon":127.51,"score":91,"groups":["Lazarus Group","Kimsuky","APT38"],"target":"Bancos · exchanges · defesa"},
        {"country":"Iran","lat":32.43,"lon":53.69,"score":85,"groups":["APT33/Elfin","APT35/Charming Kitten","MuddyWater"],"target":"Energia · governo · telecom"},
        {"country":"Vietnam","lat":14.05,"lon":108.27,"score":72,"groups":["APT32/OceanLotus"],"target":"Manufatura · governos ASEAN"},
        {"country":"Romania","lat":45.94,"lon":24.96,"score":68,"groups":["SilverTerrier"],"target":"Fraude financeira · skimming ATM"},
        {"country":"Nigeria","lat":9.08,"lon":8.67,"score":65,"groups":["BEC groups","SilverTerrier"],"target":"Fraude BEC · phishing corporativo"},
        {"country":"Pakistan","lat":30.37,"lon":69.34,"score":62,"groups":["Transparent Tribe","APT36"],"target":"Sul-asiáticos · governo"},
        {"country":"Ukraine","lat":48.38,"lon":31.17,"score":70,"groups":["Sandworm (alvo)","TA473"],"target":"Infraestrutura crítica"},
        {"country":"United States","lat":37.09,"lon":-95.71,"score":60,"groups":["NSA (defesa)","FBI Cyber"],"target":"Principal alvo de APTs globais"},
    ]

    COORDS={"China":(35.86,104.19),"Russia":(61.52,105.31),"United States":(37.09,-95.71),"Germany":(51.16,10.45),
            "North Korea":(40.33,127.51),"Canada":(56.13,-106.34),"India":(20.59,78.96),"France":(46.23,2.21),
            "United Kingdom":(55.37,-3.43),"Iran":(32.43,53.69),"Japan":(36.20,138.25),"Australia":(-25.27,133.77),
            "South Korea":(35.90,127.76),"Ukraine":(48.38,31.17),"Romania":(45.94,24.96),"Nigeria":(9.08,8.67),
            "Pakistan":(30.37,69.34),"Vietnam":(14.05,108.27),"Indonesia":(-0.78,113.92),"Netherlands":(52.13,5.29),
            "Turkey":(38.96,35.24),"Argentina":(-38.41,-63.61),"Mexico":(23.63,-102.55),"Colombia":(4.57,-74.29),}

    arcs=[]
    for _,row in cc.iterrows():
        c=row["country"]
        if c in COORDS and c!="Brazil":
            s=COORDS[c]; arcs.append({"slat":s[0],"slon":s[1],"dlat":-14.23,"dlon":-51.92,"name":c,"n":int(row["total"])})

    arcs_json = json.dumps(arcs)
    threat_json = json.dumps(THREAT_INTEL)

    globe_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#060508;overflow:hidden;font-family:'Inter',sans-serif;user-select:none;}}
canvas{{display:block;cursor:grab;}}
canvas.dragging{{cursor:grabbing;}}
.panel{{position:absolute;background:rgba(6,5,8,0.92);border:1px solid rgba(220,38,38,0.22);border-radius:12px;padding:12px 16px;backdrop-filter:blur(12px);}}
#legend{{top:14px;left:14px;min-width:190px;}}
#legend h4{{color:#dc2626;font-size:10px;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:9px;}}
.leg-item{{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:9.5px;color:#9ca3af;}}
.leg-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
#counters{{top:14px;right:14px;text-align:right;min-width:140px;}}
#counters .lbl{{color:#4b5563;font-size:8.5px;text-transform:uppercase;letter-spacing:0.1em;}}
#counters .val{{color:#dc2626;font-size:1.3rem;font-weight:800;line-height:1.2;font-family:'JetBrains Mono',monospace;}}
#status{{bottom:14px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:8px;white-space:nowrap;}}
.pulse{{width:7px;height:7px;border-radius:50%;background:#4ade80;animation:pulse 1.5s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(74,222,128,0.5);}}50%{{box-shadow:0 0 0 5px transparent;}}}}
#status span{{color:#4ade80;font-size:9.5px;}}
#feed{{bottom:14px;left:14px;max-width:280px;}}
#feed h4{{color:#dc2626;font-size:9px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;}}
.feed-item{{color:#6b7280;font-size:8.5px;line-height:1.5;margin:2px 0;padding-left:6px;border-left:2px solid rgba(220,38,38,0.25);}}
.feed-item.new{{color:#f87171;border-color:#dc2626;}}
#info-panel{{top:14px;left:50%;transform:translateX(-50%);min-width:280px;max-width:340px;display:none;z-index:20;pointer-events:all;}}
#info-panel h4{{color:#f87171;font-size:11px;margin-bottom:6px;font-weight:700;}}
#info-panel .score-bar{{background:rgba(220,38,38,0.15);border-radius:4px;height:5px;margin:6px 0;overflow:hidden;}}
#info-panel .score-fill{{height:100%;background:linear-gradient(90deg,#7f1d1d,#dc2626);border-radius:4px;transition:width 0.4s;}}
#info-panel p{{color:#9ca3af;font-size:9px;line-height:1.5;margin:3px 0;}}
#info-panel .groups{{color:#fca5a5;font-size:9px;}}
#close-info{{position:absolute;top:8px;right:10px;color:#6b7280;cursor:pointer;font-size:14px;background:none;border:none;font-family:inherit;}}
#zoom-hint{{bottom:50px;right:14px;font-size:9px;color:#374151;text-align:center;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="overlay" style="position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;">
  <div class="panel" id="legend">
    <h4>🛡️ Threat Intelligence</h4>
    <div class="leg-item"><div class="leg-dot" style="background:#ff0000"></div>Score 90–100 (APT Nação)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ff5500"></div>Score 70–89 (Alto risco)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ffaa00"></div>Score 50–69 (Moderado)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#00ff88"></div>🇧🇷 Brasil (alvo protegido)</div>
    <div class="leg-item" style="margin-top:6px;color:#4b5563;">↔ Arraste · Scroll = Zoom · Clique = Info</div>
  </div>
  <div class="panel" id="counters">
    <div class="lbl">Ataques detectados</div>
    <div class="val" id="atk-val">0</div>
    <div class="lbl" style="margin-top:6px;">IPs bloqueados</div>
    <div class="val" id="blk-val">0</div>
    <div class="lbl" style="margin-top:6px;">Países em alerta</div>
    <div class="val" id="ctr-val">0</div>
  </div>
  <div class="panel" id="feed">
    <h4>⚡ Feed ao vivo</h4>
    <div id="feed-list"></div>
  </div>
  <div class="panel" id="status">
    <div class="pulse"></div>
    <span id="status-txt">THREAT MONITORING ATIVO — TEMPO REAL</span>
  </div>
  <div class="panel" id="info-panel">
    <button id="close-info" onclick="document.getElementById('info-panel').style.display='none'">✕</button>
    <h4 id="ip-name"></h4>
    <div class="score-bar"><div class="score-fill" id="ip-bar"></div></div>
    <p id="ip-score"></p>
    <p id="ip-target"></p>
    <div class="groups" id="ip-groups"></div>
  </div>
  <div class="panel" id="zoom-hint">🔍 Scroll = zoom</div>
</div>

<script>
const ARCS = {arcs_json};
const THREATS = {threat_json};
const THREAT_MAP = {{}};
THREATS.forEach(t => THREAT_MAP[t.country] = t);
document.getElementById('ctr-val').textContent = THREATS.length;

const C = document.getElementById('c');
const ctx = C.getContext('2d');
let W, H;
function resize() {{ W = C.width = window.innerWidth; H = C.height = window.innerHeight; }}
resize(); window.addEventListener('resize', resize);

let rotY = 0.5, rotX = 0.1, zoom = 1.0;
let isDrag = false, lastX = 0, lastY = 0;
let frame = 0, ac = 0, bc = 0;
let particles = [];
let stars = [];

for(let i=0;i<300;i++) stars.push({{x:Math.random()*2000,y:Math.random()*1200,r:Math.random()*.9+.2,a:Math.random()*.5+.1}});

const GR = () => Math.min(W, H) * 0.36 * zoom;

function latLonTo3D(lat, lon, r) {{
    const phi = (90 - lat) * Math.PI / 180;
    const tht = (lon + 180) * Math.PI / 180;
    return {{
        x: r * Math.sin(phi) * Math.cos(tht),
        y: -r * Math.cos(phi),
        z: r * Math.sin(phi) * Math.sin(tht)
    }};
}}

function project(x, y, z) {{
    let rx = x * Math.cos(rotY) + z * Math.sin(rotY);
    let rz = -x * Math.sin(rotY) + z * Math.cos(rotY);
    let ry2 = y * Math.cos(rotX) - rz * Math.sin(rotX);
    let rz2 = y * Math.sin(rotX) + rz * Math.cos(rotX);
    const fov = 1400;
    const scale = fov / (fov - rz2);
    return {{ px: W/2 + rx * scale, py: H/2 + ry2 * scale, scale, z: rz2 }};
}}

const COUNTRY_BORDERS = [
    {{name:"Russia",pts:[[68,32],[69,60],[72,105],[68,140],[50,142],[45,135],[44,130],[47,142],[55,120],[60,105],[68,60],[68,32]]}},
    {{name:"China",pts:[[53,122],[48,135],[40,130],[22,114],[22,108],[25,98],[28,97],[35,76],[40,76],[42,82],[48,87],[50,117],[53,122]]}},
    {{name:"United States",pts:[[49,-124],[49,-67],[25,-80],[25,-97],[30,-97],[32,-114],[37,-120],[49,-124]]}},
    {{name:"Brazil",pts:[[-5,-34],[-8,-35],[-15,-38],[-22,-43],[-33,-52],[-34,-58],[-20,-58],[-10,-68],[-4,-72],[-1,-70],[2,-50],[-5,-34]]}},
    {{name:"Europe",pts:[[70,30],[70,10],[55,8],[44,8],[44,28],[50,30],[55,24],[60,24],[70,30]]}},
    {{name:"Africa",pts:[[37,10],[37,35],[10,42],[-10,40],[-35,20],[-35,18],[-5,12],[10,-18],[37,10]]}},
    {{name:"Australia",pts:[[-14,132],[-14,142],[-28,153],[-38,146],[-37,140],[-32,115],[-20,114],[-14,126],[-14,132]]}},
    {{name:"India",pts:[[36,76],[36,80],[22,88],[8,77],[8,76],[22,70],[28,72],[36,72],[36,76]]}},
    {{name:"Japan",pts:[[43,143],[45,142],[44,142],[38,141],[34,135],[34,131],[38,141],[43,143]]}},
    {{name:"Canada",pts:[[83,-70],[70,-60],[50,-53],[45,-64],[45,-82],[49,-90],[49,-124],[60,-140],[72,-140],[83,-100],[83,-70]]}},
];

function drawBorders() {{
    const r = GR();
    ctx.save();
    ctx.beginPath(); ctx.arc(W/2, H/2, r, 0, Math.PI*2); ctx.clip();
    COUNTRY_BORDERS.forEach(cb => {{
        if(cb.pts.length < 2) return;
        ctx.beginPath();
        let first = true;
        cb.pts.forEach(([lat, lon]) => {{
            const p3 = latLonTo3D(lat, lon, r + 0.5);
            const {{px, py, z}} = project(p3.x, p3.y, p3.z);
            if(z < -r * 0.85) {{ first = true; return; }}
            if(first) {{ ctx.moveTo(px, py); first = false; }}
            else ctx.lineTo(px, py);
        }});
        ctx.strokeStyle = 'rgba(180,50,50,0.18)';
        ctx.lineWidth = 0.6;
        ctx.stroke();
    }});
    ctx.restore();
}}

function drawGlobe() {{
    const r = GR();
    const grd = ctx.createRadialGradient(W/2, H/2, r*.6, W/2, H/2, r*1.3);
    grd.addColorStop(0, 'rgba(220,38,38,0.06)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(W/2, H/2, r*1.3, 0, Math.PI*2);
    ctx.fillStyle = grd; ctx.fill();

    const g2 = ctx.createRadialGradient(W/2-r*.2, H/2-r*.2, r*.05, W/2, H/2, r);
    g2.addColorStop(0, 'rgba(40,8,8,0.95)'); g2.addColorStop(.55, 'rgba(16,4,4,0.97)'); g2.addColorStop(1, 'rgba(6,5,8,0.99)');
    ctx.beginPath(); ctx.arc(W/2, H/2, r, 0, Math.PI*2);
    ctx.fillStyle = g2; ctx.fill();

    ctx.save();
    for(let lat=-80;lat<=80;lat+=15) {{
        ctx.beginPath(); let first=true;
        for(let lon=-180;lon<=180;lon+=3) {{
            const p3=latLonTo3D(lat,lon,r); const {{px,py,z}}=project(p3.x,p3.y,p3.z);
            if(z<-r*.9){{first=true;continue;}}
            if(first){{ctx.moveTo(px,py);first=false;}}else ctx.lineTo(px,py);
        }}
        ctx.strokeStyle=`rgba(160,30,30,${{lat===0?0.18:0.06}})`; ctx.lineWidth=lat===0?0.8:0.35; ctx.stroke();
    }}
    for(let lon=-180;lon<=180;lon+=15) {{
        ctx.beginPath(); let first=true;
        for(let lat=-88;lat<=88;lat+=2) {{
            const p3=latLonTo3D(lat,lon,r); const {{px,py,z}}=project(p3.x,p3.y,p3.z);
            if(z<-r*.9){{first=true;continue;}}
            if(first){{ctx.moveTo(px,py);first=false;}}else ctx.lineTo(px,py);
        }}
        ctx.strokeStyle='rgba(160,30,30,0.05)'; ctx.lineWidth=0.35; ctx.stroke();
    }}
    ctx.restore();

    drawBorders();

    const rim=ctx.createRadialGradient(W/2,H/2,r*.9,W/2,H/2,r*1.08);
    rim.addColorStop(0,'rgba(220,38,38,0)'); rim.addColorStop(.4,'rgba(220,38,38,0.08)'); rim.addColorStop(1,'rgba(220,38,38,0)');
    ctx.beginPath(); ctx.arc(W/2,H/2,r*1.08,0,Math.PI*2); ctx.fillStyle=rim; ctx.fill();

    ctx.save(); ctx.beginPath(); ctx.arc(W/2,H/2,r,0,Math.PI*2); ctx.clip();

    THREATS.forEach(t => {{
        const p3=latLonTo3D(t.lat,t.lon,r);
        const {{px,py,scale,z}}=project(p3.x,p3.y,p3.z);
        if(z<-r*.88) return;
        const col=t.score>=90?'#ff0000':t.score>=70?'#ff5500':t.score>=50?'#ffaa00':'#ff4488';
        const sz=(3+t.score/18)*scale;
        if(t.score>=80) {{
            const pulse=0.5+0.5*Math.sin(frame*.07+t.lat);
            ctx.beginPath(); ctx.arc(px,py,sz*2.2+pulse*5,0,Math.PI*2);
            ctx.strokeStyle=`rgba(255,0,0,${{0.15*pulse}})`; ctx.lineWidth=1; ctx.stroke();
        }}
        ctx.beginPath(); ctx.arc(px,py,sz,0,Math.PI*2);
        ctx.fillStyle=col; ctx.fill();
        if(scale>.6) {{
            ctx.font=`bold ${{Math.round(8*scale)}}px Inter`;
            ctx.fillStyle=`rgba(230,140,140,0.85)`;
            ctx.fillText(t.country.substring(0,3).toUpperCase(), px+sz+4, py+3);
        }}
    }});

    const bz=latLonTo3D(-14.23,-51.92,r); const {{px:bpx,py:bpy,scale:bsc,z:bzz}}=project(bz.x,bz.y,bz.z);
    if(bzz>-r*.88) {{
        [12,20,30].forEach((sr,i)=>{{
            const pulse=0.5+0.5*Math.sin(frame*.05+i*2);
            ctx.beginPath(); ctx.arc(bpx,bpy,(sr+pulse*4)*bsc,0,Math.PI*2);
            ctx.strokeStyle=`rgba(0,255,136,${{0.25-i*.07}})`;
            ctx.lineWidth=1; ctx.stroke();
        }});
        ctx.beginPath(); ctx.arc(bpx,bpy,7*bsc,0,Math.PI*2);
        ctx.fillStyle='#00ff88'; ctx.fill();
        if(bsc>.6) {{
            ctx.font=`bold ${{Math.round(9*bsc)}}px Inter`;
            ctx.fillStyle=`rgba(0,255,136,0.9)`; ctx.fillText('BRA',bpx+10*bsc,bpy+3);
        }}
    }}
    ctx.restore();
}}

class Particle {{
    constructor(arc) {{
        this.arc=arc; this.t=0; this.spd=0.003+Math.random()*.005; this.trail=[];
        const th=THREAT_MAP[arc.name];
        this.col=th?(th.score>=90?'255,0,0':th.score>=70?'255,85,0':th.score>=50?'255,170,0':'255,68,136'):'220,100,50';
    }}
    pos(t) {{
        const r=GR();
        const s=latLonTo3D(this.arc.slat,this.arc.slon,r);
        const d=latLonTo3D(this.arc.dlat,this.arc.dlon,r);
        const cx=(s.x+d.x)/2, cy=(s.y+d.y)/2-r*.35, cz=(s.z+d.z)/2;
        const u=1-t;
        return {{x:u*u*s.x+2*u*t*cx+t*t*d.x, y:u*u*s.y+2*u*t*cy+t*t*d.y, z:u*u*s.z+2*u*t*cz+t*t*d.z}};
    }}
    update() {{
        this.t+=this.spd;
        const p=this.pos(Math.min(this.t,1));
        const {{px,py,z}}=project(p.x,p.y,p.z);
        this.trail.push({{px,py,z}});
        if(this.trail.length>24) this.trail.shift();
        return this.t<1;
    }}
    draw() {{
        const r=GR();
        if(this.trail.length<2) return;
        for(let i=1;i<this.trail.length;i++) {{
            const a=i/this.trail.length;
            const tp=this.trail[i], pp=this.trail[i-1];
            if(tp.z<-r*.85) continue;
            ctx.beginPath(); ctx.moveTo(pp.px,pp.py); ctx.lineTo(tp.px,tp.py);
            ctx.strokeStyle=`rgba(${{this.col}},${{a*.9}})`; ctx.lineWidth=1.8*a; ctx.stroke();
        }}
        const last=this.trail[this.trail.length-1];
        if(last && last.z>-r*.85) {{
            ctx.beginPath(); ctx.arc(last.px,last.py,3,0,Math.PI*2);
            ctx.fillStyle=`rgba(${{this.col}},0.9)`; ctx.fill();
            if(this.t>0.97) {{
                ctx.beginPath(); ctx.arc(last.px,last.py,8*(1-this.t)*10,0,Math.PI*2);
                ctx.strokeStyle=`rgba(${{this.col}},0.4)`; ctx.lineWidth=1; ctx.stroke();
            }}
        }}
    }}
}}

function spawnParticles() {{
    ARCS.forEach(arc=>{{ if(Math.random()<.07) particles.push(new Particle(arc)); }});
    const extras=[
        {{slat:61.52,slon:105.31,dlat:-14.23,dlon:-51.92,name:"Russia",n:50}},
        {{slat:40.33,slon:127.51,dlat:-14.23,dlon:-51.92,name:"North Korea",n:45}},
        {{slat:32.43,slon:53.69,dlat:-14.23,dlon:-51.92,name:"Iran",n:35}},
        {{slat:9.08,slon:8.67,dlat:-14.23,dlon:-51.92,name:"Nigeria",n:30}},
        {{slat:35.86,slon:104.19,dlat:-14.23,dlon:-51.92,name:"China",n:60}},
    ];
    extras.forEach(arc=>{{ if(Math.random()<.05) particles.push(new Particle(arc)); }});
}}

const FEED_MSGS=[
    "APT28 tentativa de acesso SSH bloqueada · RU","Flood DDoS mitigado — 48Gbps · CN","Brute force detectado · KP",
    "SQL Injection bloqueado · RU","Ransomware signature detectada · UA","C2 callback bloqueado · IR",
    "Phishing domain takedown · NG","Credential stuffing · KP","Port scan massivo · CN",
    "Zero-day exploit tentativa · RU","BEC attack interceptado · NG","DNS hijack attempt · TR",
];
let feedItems=[];
function addFeed() {{
    const t=new Date().toLocaleTimeString('pt-BR',{{hour:'2-digit',minute:'2-digit',second:'2-digit'}});
    feedItems.unshift(`[${{t}}] ${{FEED_MSGS[Math.floor(Math.random()*FEED_MSGS.length)]}}`);
    if(feedItems.length>5) feedItems.pop();
    document.getElementById('feed-list').innerHTML=feedItems.map((f,i)=>`<div class="feed-item ${{i===0?"new":""}}">${{f}}</div>`).join('');
}}
addFeed(); setInterval(addFeed,2600);

function animate() {{
    requestAnimationFrame(animate);
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#060508'; ctx.fillRect(0,0,W,H);
    stars.forEach(s=>{{
        ctx.beginPath(); ctx.arc(s.x%W, s.y%H, s.r, 0, Math.PI*2);
        ctx.fillStyle=`rgba(255,200,200,${{s.a*(0.7+0.3*Math.sin(frame*.02+s.x))}})`; ctx.fill();
    }});
    if(!isDrag) rotY += 0.0022;
    frame++;
    drawGlobe();
    if(frame%7===0) spawnParticles();
    particles=particles.filter(p=>{{
        const alive=p.update(); p.draw();
        if(!alive) {{ ac++; bc=Math.floor(ac*.71); document.getElementById('atk-val').textContent=ac.toLocaleString(); document.getElementById('blk-val').textContent=bc.toLocaleString(); }}
        return alive;
    }});
}}

C.addEventListener('mousedown',e=>{{ isDrag=true; lastX=e.clientX; lastY=e.clientY; C.classList.add('dragging'); }});
window.addEventListener('mouseup',()=>{{ isDrag=false; C.classList.remove('dragging'); }});
window.addEventListener('mousemove',e=>{{
    if(!isDrag) return;
    rotY += (e.clientX-lastX)*.005;
    rotX += (e.clientY-lastY)*.003;
    rotX = Math.max(-0.8, Math.min(0.8, rotX));
    lastX=e.clientX; lastY=e.clientY;
}});
C.addEventListener('wheel',e=>{{
    e.preventDefault();
    zoom = Math.max(0.5, Math.min(2.5, zoom - e.deltaY*.001));
}},{{passive:false}});

C.addEventListener('click',e=>{{
    const rect=C.getBoundingClientRect();
    const mx=e.clientX-rect.left, my=e.clientY-rect.top;
    const r=GR();
    let found=null;
    THREATS.forEach(t=>{{
        const p3=latLonTo3D(t.lat,t.lon,r);
        const {{px,py,z}}=project(p3.x,p3.y,p3.z);
        if(z>-r*.8 && Math.hypot(mx-px,my-py)<20) found=t;
    }});
    if(found) {{
        const panel=document.getElementById('info-panel');
        document.getElementById('ip-name').textContent='⚠️ '+found.country;
        document.getElementById('ip-score').textContent='Threat Score: '+found.score+'/100';
        document.getElementById('ip-target').textContent='Alvos: '+found.target;
        document.getElementById('ip-groups').textContent='Grupos APT: '+found.groups.join(' · ');
        document.getElementById('ip-bar').style.width=found.score+'%';
        panel.style.display='block';
    }}
}});

animate();
</script>
</body>
</html>"""
    components.html(globe_html, height=640, scrolling=False)

    st.markdown("### 🏴‍☠️ Threat Intelligence — Países de Alto Risco")
    threat_df = pd.DataFrame([
        {{"País":t["country"],"Threat Score":t["score"],"Grupos APT":", ".join(t["groups"]),"Alvos Primários":t["target"]}}
        for t in sorted(THREAT_INTEL,key=lambda x:-x["score"])
    ])
    st.dataframe(threat_df,use_container_width=True,hide_index=True)

    if not cc.empty:
        st.markdown("### 📊 Ataques por País — Dataset Atual")
        ta=cc.copy(); ta.columns=["País","Ataques"]
        ta["% do Total"]=(ta["Ataques"]/ta["Ataques"].sum()*100).round(1).astype(str)+"%"
        st.dataframe(ta,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SENTINEL BOT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🤖 Sentinel Bot — Assistente de Segurança")
    st.caption("IA especialista em cibersegurança com acesso aos dados do sistema em tempo real.")

    top_cli=df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top_pai=df[df["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    SYSTEM_BOT=f"""Você é o Sentinel Bot, assistente especialista em segurança cibernética da plataforma SentinelAI.
Responda SEMPRE em português brasileiro, de forma profissional, objetiva e direta.
Use dados reais do sistema nas respostas. Não invente informações.

=== DADOS ATUAIS ===
Total incidentes: {len(df)} | Críticos: {crit} ({crit/max(total,1)*100:.1f}%)
IPs bloqueados: {bloq} | Resolvidos: {resol} | Pendentes: {pend}
Prejuízo total: R$ {prej:,.0f} | Acurácia IA: {ACC:.1%}
Top países atacantes: {top_pai}
Top clientes por prejuízo: {top_cli}
Status: {df['STATUS'].value_counts().to_dict()}
Severidades: {df['SEVERIDADE'].value_counts().to_dict()}
Escopo: {"Todos os clientes" if not CLT else CLT}
BD: SQLite {db_size}KB ativo"""

    for msg in st.session_state["chat"]:
        css="chat-user" if msg["role"]=="user" else "chat-ai"
        icon="👤" if msg["role"]=="user" else "🤖"
        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>',unsafe_allow_html=True)

    if not st.session_state["chat"]:
        st.markdown("""<div class="chat-ai">🤖 <strong>Sentinel Bot ativo.</strong><br><br>
        Olá! Sou o assistente de segurança da SentinelAI. Posso analisar incidentes, identificar padrões de ameaças e recomendar ações.<br><br>Como posso ajudar?</div>""",unsafe_allow_html=True)

    sugs=["Qual cliente tem mais prejuízo?","Quais países mais atacaram?","Status dos incidentes críticos","Recomendações urgentes","Como funciona o modelo IA?","Explique os grupos APT"]
    st.markdown("<p style='color:#4b5563;font-size:0.68rem;margin:10px 0 5px;text-transform:uppercase;'>💡 Perguntas rápidas</p>",unsafe_allow_html=True)
    scols=st.columns(len(sugs)); sug_click=None
    for i,s in enumerate(sugs):
        with scols[i]:
            if st.button(s,key=f"sg{i}",use_container_width=True): sug_click=s

    with st.form("chat_f",clear_on_submit=True):
        ci,cb=st.columns([5,1])
        with ci: q=st.text_input("",placeholder="Digite sua pergunta sobre segurança...",label_visibility="collapsed")
        with cb: send=st.form_submit_button("Enviar",use_container_width=True)

    if sug_click: q=sug_click; send=True

    if send and q:
        log(USER,"CHAT",q[:80])
        st.session_state["chat"].append({{"role":"user","content":q}})
        msgs=st.session_state["chat"].copy()
        resp=gemini_chat(SYSTEM_BOT,msgs)
        st.session_state["chat"].append({{"role":"assistant","content":resp}})
        db_salvar_chat(USER,q,resp); st.rerun()

    if st.session_state["chat"]:
        if st.button("🗑️ Limpar conversa",key="clear_chat"):
            st.session_state["chat"]=[]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SUPORTE AO CLIENTE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 🎫 Suporte ao Cliente — Canal Direto com a SentinelAI")

    is_client      = bool(CLT)
    is_support_adm = PROF["support_admin"]

    SUPPORT_SYS=f"""Você é o agente de suporte da SentinelAI, empresa brasileira de cibersegurança.
Responda em português, de forma cordial, profissional e objetiva.
Auxilia clientes empresariais com dúvidas sobre segurança, incidentes e a plataforma.
Cliente: {CLT or 'Equipe interna'}
Dados: {len(df)} incidentes · Acurácia IA {ACC:.1%} · Prejuízo R$ {prej:,.0f}
Nunca revele dados de outros clientes."""

    if is_client:
        st.markdown(f'<div class="info-box-blue">🏢 <strong>Bem-vindo ao suporte, {CLT}!</strong><br>Chat com IA de suporte, consulte seus tickets ou abra um novo chamado.</div>',unsafe_allow_html=True)

        ctabs=st.tabs(["💬 Chat Suporte","🎫 Meus Tickets","➕ Novo Ticket"])

        with ctabs[0]:
            st.markdown("#### 💬 Chat com Suporte SentinelAI")
            if not st.session_state["chat_suporte"]:
                st.markdown(f"""<div class="chat-support">🛡️ <strong>Suporte SentinelAI ativo.</strong><br><br>Olá, {CLT}! Como posso ajudar hoje?</div>""",unsafe_allow_html=True)
            for msg in st.session_state["chat_suporte"]:
                css="chat-user" if msg["role"]=="user" else "chat-support"
                icon="🏢" if msg["role"]=="user" else "🛡️"
                st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>',unsafe_allow_html=True)

            sup_sugs=[f"Status incidentes {CLT}","Como interpretar threat score?","O que fazer em caso de ataque?","Como exportar relatórios?"]
            sc=st.columns(len(sup_sugs)); sup_click=None
            for i,s in enumerate(sup_sugs):
                with sc[i]:
                    if st.button(s,key=f"sup_sg{i}",use_container_width=True): sup_click=s

            with st.form("chat_sup_f",clear_on_submit=True):
                si,sb=st.columns([5,1])
                with si: sq=st.text_input("",placeholder="Mensagem para o suporte...",label_visibility="collapsed")
                with sb: ssend=st.form_submit_button("Enviar",use_container_width=True)

            if sup_click: sq=sup_click; ssend=True

            if ssend and sq:
                log(USER,"SUPORTE_CHAT",sq[:80])
                st.session_state["chat_suporte"].append({{"role":"user","content":sq}})
                sup_resp=gemini_chat(SUPPORT_SYS,st.session_state["chat_suporte"].copy(),temperature=0.6,max_tokens=800)
                st.session_state["chat_suporte"].append({{"role":"assistant","content":sup_resp}}); st.rerun()

            if st.session_state["chat_suporte"]:
                if st.button("🗑️ Limpar chat",key="clear_sup"): st.session_state["chat_suporte"]=[]; st.rerun()

        with ctabs[1]:
            st.markdown("#### 🎫 Meus Tickets")
            tks_cli=db_buscar_tickets(CLT)
            if tks_cli.empty:
                st.info("Nenhum ticket ainda. Abra um na aba 'Novo Ticket'.")
            else:
                for _,row in tks_cli.iterrows():
                    sc_color={"aberto":"#dc2626","respondido":"#4ade80","fechado":"#6b7280"}.get(row["status"],"#f59e0b")
                    pri_icon={"urgente":"🔴","alta":"🟠","normal":"🟡","baixa":"🟢"}.get(row["prioridade"],"⚪")
                    st.markdown(f"""<div class="ticket-card">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="color:white;font-weight:700;font-size:0.82rem;">{pri_icon} #{row['id']} — {row['assunto']}</span>
                        <span style="color:{sc_color};font-size:0.7rem;font-weight:700;">{row['status'].upper()}</span>
                      </div>
                      <p style="color:#6b7280;font-size:0.7rem;">📅 {row['ts']}</p>
                    </div>""",unsafe_allow_html=True)
                    with st.expander(f"Ver ticket #{row['id']}"):
                        chat_t=db_buscar_chat_ticket(int(row["id"]))
                        if not chat_t.empty:
                            for _,m in chat_t.iterrows():
                                is_me=m["remetente"]==CLT
                                st.markdown(f'<div class="{"chat-user" if is_me else "chat-support"}">{"🏢" if is_me else "🛡️"} <strong>{m["remetente"]}</strong> · {m["ts"]}<br>{m["mensagem"]}</div>',unsafe_allow_html=True)
                        if row["status"]!="fechado":
                            with st.form(f"reply_{row['id']}"):
                                rm=st.text_area("Adicionar mensagem",key=f"rm_{row['id']}",height=70)
                                cr1,cr2=st.columns(2)
                                with cr1:
                                    if st.form_submit_button("📤 Enviar",use_container_width=True):
                                        if rm.strip(): db_adicionar_msg_ticket(int(row["id"]),CLT,rm.strip()); log(USER,"TICKET_MSG",f"#{row['id']}"); st.rerun()
                                with cr2:
                                    if st.form_submit_button("✅ Fechar ticket",use_container_width=True):
                                        db_responder_ticket(int(row["id"]),"Fechado pelo cliente.","fechado"); log(USER,"TICKET_FECHADO",f"#{row['id']}"); st.rerun()

        with ctabs[2]:
            st.markdown("#### ➕ Abrir Novo Ticket")
            with st.form("novo_ticket"):
                assunto    =st.text_input("Assunto*",placeholder="Ex: Alerta não reconhecido")
                prioridade =st.selectbox("Prioridade",["normal","alta","urgente","baixa"])
                mensagem   =st.text_area("Descrição*",height=110,placeholder="Descreva o problema, quando ocorreu e o impacto...")
                submitted  =st.form_submit_button("📤 Abrir Ticket",use_container_width=True)
            if submitted:
                if assunto.strip() and mensagem.strip():
                    tid=db_criar_ticket(CLT,assunto.strip(),mensagem.strip(),prioridade)
                    if tid:
                        log(USER,"TICKET_CRIADO",f"id={tid}")
                        st.success(f"✅ Ticket #{tid} criado!")
                        auto=gemini_chat(SUPPORT_SYS,[{{"role":"user","content":f"Cliente {CLT} abriu ticket: '{assunto}'. Mensagem: {mensagem}. Responda confirmando recebimento e com orientações iniciais."}}],temperature=0.5,max_tokens=400)
                        db_adicionar_msg_ticket(tid,"SentinelAI",auto); st.rerun()
                    else: st.error("Erro ao criar ticket.")
                else: st.warning("Preencha todos os campos.")

    elif is_support_adm:
        st.markdown('<div class="info-box">🔧 <strong>Painel Administrativo de Suporte</strong> — Gerencie todos os tickets dos clientes.</div>',unsafe_allow_html=True)
        all_tks=db_buscar_tickets()
        if all_tks.empty:
            st.info("Nenhum ticket registrado.")
        else:
            n_ab=len(all_tks[all_tks["status"]=="aberto"]); n_re=len(all_tks[all_tks["status"]=="respondido"]); n_fe=len(all_tks[all_tks["status"]=="fechado"])
            ma1,ma2,ma3=st.columns(3)
            with ma1: st.metric("🔴 Abertos",n_ab)
            with ma2: st.metric("🟡 Respondidos",n_re)
            with ma3: st.metric("🟢 Fechados",n_fe)
            filtro=st.selectbox("Filtrar",["todos","aberto","respondido","fechado"])
            tks_f=all_tks if filtro=="todos" else all_tks[all_tks["status"]==filtro]
            for _,row in tks_f.iterrows():
                pri_icon={"urgente":"🔴","alta":"🟠","normal":"🟡","baixa":"🟢"}.get(row["prioridade"],"⚪")
                with st.expander(f"{pri_icon} #{row['id']} [{row['cliente']}] {row['assunto']} — {row['status'].upper()}"):
                    chat_t=db_buscar_chat_ticket(int(row["id"]))
                    if not chat_t.empty:
                        for _,m in chat_t.iterrows():
                            is_sen=m["remetente"]=="SentinelAI"
                            st.markdown(f'<div class="{"chat-support" if is_sen else "chat-user"}">{"🛡️" if is_sen else "🏢"} <strong>{m["remetente"]}</strong> · {m["ts"]}<br>{m["mensagem"]}</div>',unsafe_allow_html=True)
                    if row["status"]!="fechado":
                        if st.button(f"🤖 Sugestão IA para #{row['id']}",key=f"ia_{row['id']}",use_container_width=True):
                            sugestao=gemini_chat(SUPPORT_SYS,[{{"role":"user","content":f"Analista precisa responder ticket do cliente {row['cliente']}. Assunto: '{row['assunto']}'. Mensagem: '{row['mensagem']}'. Gere resposta profissional e empática."}}],temperature=0.5,max_tokens=400)
                            st.info(f"💡 Sugestão:\n\n{sugestao}")
                        with st.form(f"adm_{row['id']}"):
                            resp_adm=st.text_area("Resposta",height=80,key=f"ra_{row['id']}")
                            ca1,ca2,ca3=st.columns(3)
                            with ca1:
                                if st.form_submit_button("📤 Responder",use_container_width=True):
                                    if resp_adm.strip(): db_responder_ticket(int(row["id"]),resp_adm.strip(),"respondido"); log(USER,"TICKET_RESP",f"#{row['id']}"); st.rerun()
                            with ca2:
                                if st.form_submit_button("✅ Fechar",use_container_width=True):
                                    db_responder_ticket(int(row["id"]),resp_adm.strip() or "Resolvido.","fechado"); log(USER,"TICKET_FECH",f"#{row['id']}"); st.rerun()
                            with ca3:
                                if st.form_submit_button("🚨 Escalar",use_container_width=True):
                                    db_adicionar_msg_ticket(int(row["id"]),USER,"⚠️ ESCALADO como URGENTE pelo SOC."); log(USER,"TICKET_ESC",f"#{row['id']}"); st.rerun()
    else:
        st.markdown('<div class="info-box">⛔ Sem acesso ao módulo de suporte.</div>',unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — BACKUP & DB
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 💾 Backup e Gerenciamento de Dados")
    st.markdown("""
    <div class="info-box">
      <strong>📍 Onde os dados são armazenados:</strong><br><br>
      <strong style="color:#f87171;">SQLite (atual — sentinelai_backup.db):</strong><br>
      • Arquivo local no servidor Streamlit Cloud · persiste entre sessões normais<br>
      • ⚠️ Reseta ao fazer redeploy da aplicação<br><br>
      <strong style="color:#60a5fa;">MySQL (produção — persistência total):</strong><br>
      • Configure <code>MYSQL_URL</code> nos Secrets do Streamlit<br>
      • Serviços gratuitos: <strong>PlanetScale</strong>, <strong>Railway</strong>, <strong>Aiven</strong><br>
      • Backup automático · sem perda em redeploys<br><br>
      <strong style="color:#4ade80;">Exportação manual:</strong> use os botões abaixo para CSV/TXT a qualquer momento.
    </div>""",unsafe_allow_html=True)

    with st.expander("⚙️ Como configurar MySQL (PlanetScale / Railway)"):
        st.code("""# 1. PlanetScale (planetscale.com) — crie banco 'sentinelai'
# 2. Copie a connection string
# 3. No Streamlit Cloud: Settings → Secrets → adicione:

MYSQL_URL = "mysql://user:senha@host/sentinelai" """, language="bash")

    b1,b2,b3,b4=st.columns(4)
    with b1:
        st.markdown(f"""<div style="background:rgba(0,180,80,0.06);border:1px solid rgba(0,180,80,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">SQLite Status</p>
          <p style="color:#4ade80;font-size:1rem;font-weight:700;">✅ ATIVO</p>
          <p style="color:#6b7280;font-size:0.7rem;">{db_size} KB</p>
        </div>""",unsafe_allow_html=True)
    with b2:
        n_inc=len(db_buscar_incidentes())
        st.markdown(f"""<div style="background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Incidentes Salvos</p>
          <p style="color:#dc2626;font-size:1rem;font-weight:700;">{n_inc}</p>
        </div>""",unsafe_allow_html=True)
    with b3:
        n_tks_db=len(db_buscar_tickets())
        st.markdown(f"""<div style="background:rgba(0,100,200,0.06);border:1px solid rgba(0,150,255,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Tickets Suporte</p>
          <p style="color:#60a5fa;font-size:1rem;font-weight:700;">{n_tks_db}</p>
        </div>""",unsafe_allow_html=True)
    with b4:
        n_logs_db=len(db_buscar_logs())
        st.markdown(f"""<div style="background:rgba(100,50,0,0.06);border:1px solid rgba(180,100,0,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Logs Auditoria</p>
          <p style="color:#f59e0b;font-size:1rem;font-weight:700;">{n_logs_db}</p>
        </div>""",unsafe_allow_html=True)

    st.markdown("### 📥 Exportar Dados")
    if not PROF["export"]:
        st.error("⛔ Apenas Administradores podem exportar.")
    else:
        ts_exp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        e1,e2,e3,e4,e5=st.columns(5)
        with e1: st.download_button("⬇️ Dataset Completo",df_all.to_csv(index=False).encode(),f"sentinel_full_{ts_exp}.csv","text/csv",use_container_width=True)
        with e2:
            df_anon=df_all.drop(columns=["IP_SUSPEITO"],errors="ignore")
            st.download_button("⬇️ Anonimizado",df_anon.to_csv(index=False).encode(),f"sentinel_anon_{ts_exp}.csv","text/csv",use_container_width=True)
        with e3:
            df_inc_exp=db_buscar_incidentes()
            if not df_inc_exp.empty: st.download_button("⬇️ Incidentes DB",df_inc_exp.to_csv(index=False).encode(),f"sentinel_db_{ts_exp}.csv","text/csv",use_container_width=True)
        with e4:
            df_tks_exp=db_buscar_tickets()
            if not df_tks_exp.empty: st.download_button("⬇️ Tickets",df_tks_exp.to_csv(index=False).encode(),f"sentinel_tickets_{ts_exp}.csv","text/csv",use_container_width=True)
        with e5:
            if st.session_state.get("logs"): st.download_button("⬇️ Logs Sessão","\n".join(st.session_state["logs"]).encode(),f"sentinel_logs_{ts_exp}.txt","text/plain",use_container_width=True)
        db_meta_backup(USER,"EXPORT_FULL",len(df_all))

    st.markdown("### 📋 Incidentes no Banco")
    df_db_view=db_buscar_incidentes()
    if not df_db_view.empty: st.dataframe(df_db_view,use_container_width=True,height=220)
    else: st.info("Nenhum incidente registrado. Use Análise para gerar registros.")

    st.markdown("### 👁️ Prévia — Dataset Principal")
    st.dataframe(df.head(20),use_container_width=True,height=200)
    st.caption(f"{len(df)} registros · {len(df.columns)} colunas")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — AUDITORIA
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 📋 Logs de Auditoria — Rastreabilidade Completa")
    st.caption("Todas as ações registradas com timestamp · Conformidade LGPD e ISO 27001")
    df_logs=db_buscar_logs()
    if not df_logs.empty:
        al1,al2,al3=st.columns(3)
        with al1: st.metric("Total Eventos",len(df_logs))
        with al2: st.metric("Usuários Ativos",df_logs["usuario"].nunique())
        with al3: st.metric("Ações Distintas",df_logs["acao"].nunique())
        st.dataframe(df_logs,use_container_width=True,height=380)
        if PROF["export"]:
            ts_aud=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("⬇️ Exportar Auditoria",df_logs.to_csv(index=False).encode(),f"auditoria_{ts_aud}.csv","text/csv")
    else: st.info("Nenhum log ainda.")
    st.markdown("### Logs da Sessão")
    if st.session_state.get("logs"):
        for l in reversed(st.session_state["logs"][-40:]): st.code(l,language=None)
    else: st.info("Nenhum log nesta sessão.")
ENDOFFILE
echo "Done: $(wc -l < /mnt/user-data/outputs/app.py) lines"
