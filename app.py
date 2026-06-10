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
from groq import Groq

groq_client = Groq(api_key="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")

st.set_page_config(
    page_title="SentinelAI — SOC Platform",
    page_icon="robo.png" if os.path.exists("robo.png") else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

input, textarea, [data-baseweb="input"] input {
    background: rgba(10,5,7,0.9) !important;
    border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-baseweb="select"] > div {
    background: rgba(10,5,7,0.9) !important;
    border: 1px solid rgba(180,0,0,0.25) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}

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
.chat-support {
    background: linear-gradient(135deg, rgba(0,100,200,0.15), rgba(0,50,120,0.2));
    border: 1px solid rgba(0,150,255,0.25);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    margin: 0.6rem 0;
    max-width: 75%;
    width: fit-content;
    color: #bae6fd;
    font-size: 0.82rem;
    line-height: 1.6;
}

.typing-indicator {
    background: rgba(10,5,7,0.95);
    border: 1px solid rgba(180,0,0,0.2);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem;
    margin: 0.6rem 0;
    width: fit-content;
    display: flex;
    align-items: center;
    gap: 5px;
}
.typing-dot {
    width: 7px; height: 7px;
    background: #dc2626;
    border-radius: 50%;
    animation: typing-bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-6px); opacity: 1; }
}

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

.badge-online {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,255,100,0.06); border: 1px solid rgba(0,255,100,0.22);
    color: #4ade80; padding: 4px 14px; border-radius: 20px;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
}
.badge-critical {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(220,38,38,0.1); border: 1px solid rgba(220,38,38,0.35);
    color: #f87171; padding: 4px 14px; border-radius: 20px;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em;
}

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
.robot-float-img {
    width: 72px; height: 72px; object-fit: contain;
    animation: float-robot 4s ease-in-out infinite, glow-pulse 2.5s ease-in-out infinite;
    display: block; margin: 0 auto;
}

@keyframes scan {
    0%   { transform: translateY(-100%); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
}
.scan-line {
    position: fixed; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(220,38,38,0.4), transparent);
    animation: scan 6s linear infinite;
    pointer-events: none; z-index: 0;
}

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
    conn.commit()
    conn.close()

init_db()

def db_log(usuario, acao, detalhe=""):
    try:
        conn = get_db()
        conn.execute("INSERT INTO logs_auditoria (usuario,acao,detalhe) VALUES (?,?,?)", (usuario, acao, detalhe[:500]))
        conn.commit()
        conn.close()
    except: pass

def db_salvar_incidente(d):
    try:
        conn = get_db()
        conn.execute("""INSERT INTO incidentes_analisados (usuario,tipo,origem,status,severidade,cliente,risco,prejuizo)
            VALUES (?,?,?,?,?,?,?,?)""", (d["usuario"],d["tipo"],d["origem"],d["status"],d["severidade"],d["cliente"],d["risco"],d["prejuizo"]))
        conn.commit(); conn.close(); return True
    except: return False

def db_salvar_chat(usuario, pergunta, resposta):
    try:
        conn = get_db()
        conn.execute("INSERT INTO chat_historico (usuario,pergunta,resposta) VALUES (?,?,?)", (usuario, pergunta[:1000], resposta[:2000]))
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
        conn.execute("INSERT INTO backups_meta (usuario,tipo,registros) VALUES (?,?,?)", (usuario, tipo, registros))
        conn.commit(); conn.close()
    except: pass

def db_criar_ticket(cliente, assunto, mensagem, prioridade="normal"):
    try:
        conn = get_db()
        cur = conn.execute("INSERT INTO tickets_suporte (cliente,assunto,mensagem,prioridade) VALUES (?,?,?,?)", (cliente,assunto,mensagem,prioridade))
        tid = cur.lastrowid
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)", (tid, cliente, mensagem))
        conn.commit(); conn.close(); return tid
    except: return None

def db_buscar_tickets(cliente=None):
    try:
        conn = get_db()
        if cliente:
            df = pd.read_sql("SELECT * FROM tickets_suporte WHERE cliente=? ORDER BY ts DESC", conn, params=(cliente,))
        else:
            df = pd.read_sql("SELECT * FROM tickets_suporte ORDER BY ts DESC", conn)
        conn.close(); return df
    except: return pd.DataFrame()

def db_responder_ticket(ticket_id, resposta, status="respondido"):
    try:
        conn = get_db()
        conn.execute("UPDATE tickets_suporte SET resposta=?,status=?,ts_resposta=CURRENT_TIMESTAMP WHERE id=?", (resposta,status,ticket_id))
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)", (ticket_id,"SentinelAI",resposta))
        conn.commit(); conn.close(); return True
    except: return False

def db_buscar_chat_ticket(ticket_id):
    try:
        conn = get_db()
        df = pd.read_sql("SELECT * FROM chat_suporte WHERE ticket_id=? ORDER BY ts ASC", conn, params=(ticket_id,))
        conn.close(); return df
    except: return pd.DataFrame()

def db_adicionar_msg_ticket(ticket_id, remetente, mensagem):
    try:
        conn = get_db()
        conn.execute("INSERT INTO chat_suporte (ticket_id,remetente,mensagem) VALUES (?,?,?)", (ticket_id,remetente,mensagem))
        conn.commit(); conn.close(); return True
    except: return False

def log(usuario, acao, detalhe=""):
    if "logs" not in st.session_state:
        st.session_state["logs"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs"].append(f"[{ts}] {usuario} → {acao} {detalhe}")
    db_log(usuario, acao, detalhe)

USERS = {
    "admin":        {"pw":"admin123",    "role":"Administrador",  "export":True,  "analyze":True,  "pii":True,  "client":None,           "support_admin":True},
    "analista":     {"pw":"analista123", "role":"Analista SOC",   "export":False, "analyze":True,  "pii":False, "client":None,           "support_admin":True},
    "nubank":       {"pw":"nubank123",   "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Nubank",       "support_admin":False},
    "mercadolivre": {"pw":"ml123",       "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Mercado Livre","support_admin":False},
    "santander":    {"pw":"sant123",     "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"Santander",    "support_admin":False},
    "ifood":        {"pw":"ifood123",    "role":"Cliente",        "export":False, "analyze":False, "pii":False, "client":"iFood",        "support_admin":False},
    "viewer":       {"pw":"viewer123",   "role":"Visualizador",   "export":False, "analyze":False, "pii":False, "client":None,           "support_admin":False},
}
_H = {u: hashlib.sha256(v["pw"].encode()).hexdigest() for u, v in USERS.items()}

def auth(u, p):
    return u in _H and hashlib.sha256(p.encode()).hexdigest() == _H[u]

def mask_ip(ip):
    if not ip or str(ip) == "Nenhum" or pd.isna(ip): return "***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

for k, v in {"authed":False,"user":None,"lgpd":False,"chat":[],"chat_suporte":[],"logs":[],"ticket_ativo":None,"show_prospect":False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def gemini_chat(system_prompt, messages, temperature=0.7, max_tokens=1000):
    try:
        openai_messages = [{"role":"system","content":system_prompt}]
        for m in messages:
            openai_messages.append({"role":m["role"],"content":m["content"]})
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na API: {str(e)}"

# ─── LGPD ────────────────────────────────────────────────────────────────────
if not st.session_state["lgpd"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)

    lgpd_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
body{
    background:radial-gradient(ellipse at 20% 50%,rgba(139,0,0,0.2) 0%,transparent 60%),
               radial-gradient(ellipse at 80% 20%,rgba(180,0,0,0.15) 0%,transparent 55%),#060508;
    min-height:100vh; display:flex; align-items:center; justify-content:center;
    font-family:'Inter',sans-serif; overflow-y:auto; position:relative; padding:20px;
}
.grid-bg{
    position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;
    background-image:linear-gradient(rgba(180,0,0,0.04) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(180,0,0,0.04) 1px,transparent 1px);
    background-size:50px 50px; animation:grid-move 20s linear infinite;
}
@keyframes grid-move{0%{background-position:0 0;}100%{background-position:50px 50px;}}
.scan-line{
    position:fixed;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,transparent,rgba(220,38,38,0.5),transparent);
    animation:scan 5s linear infinite;z-index:1;
}
@keyframes scan{0%{top:-2px;}100%{top:100vh;}}
.particles{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;}
.particle{
    position:absolute;border-radius:50%;
    animation:float-particle linear infinite;
}
@keyframes float-particle{
    0%{transform:translateY(100vh) rotate(0deg);opacity:0;}
    10%{opacity:1;}90%{opacity:1;}
    100%{transform:translateY(-100px) rotate(720deg);opacity:0;}
}
.card{
    background:linear-gradient(135deg,rgba(15,5,8,0.98),rgba(10,5,7,0.99));
    border:1px solid rgba(180,0,0,0.25);border-radius:24px;
    padding:2rem 2rem;
    max-width:700px;
    width:90%;
    position:relative;z-index:10;
    box-shadow:0 40px 120px rgba(139,0,0,0.3),0 0 60px rgba(0,0,0,0.8);
}
.card::before{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;border-radius:24px 24px 0 0;
    background:linear-gradient(90deg,transparent,rgba(220,38,38,0.7),transparent);
}
.robot-wrap{display:flex;justify-content:center;margin-bottom:1rem;}
.robot-img{
    width:90px;height:90px;object-fit:contain;
    animation:robot-float 3s ease-in-out infinite;
    filter:drop-shadow(0 0 20px rgba(220,38,38,0.7)) drop-shadow(0 0 40px rgba(139,0,0,0.5));
}
@keyframes robot-float{
    0%,100%{transform:translateY(0px) rotate(-3deg);}
    25%{transform:translateY(-12px) rotate(2deg);}
    50%{transform:translateY(-6px) rotate(-1deg);}
    75%{transform:translateY(-16px) rotate(3deg);}
}
.title{text-align:center;margin-bottom:1rem;}
.title h1{color:white;font-size:1.8rem;font-weight:900;letter-spacing:-0.5px;}
.title h1 span{color:#dc2626;}
.title p{color:#6b7280;font-size:0.7rem;margin-top:4px;font-family:'JetBrains Mono',monospace;}
.badges{display:flex;gap:8px;justify-content:center;margin-bottom:1rem;flex-wrap:wrap;}
.badge-green{
    background:rgba(0,255,100,0.06);border:1px solid rgba(0,255,100,0.22);color:#4ade80;
    padding:4px 12px;border-radius:20px;font-size:0.55rem;font-weight:700;
    display:inline-flex;align-items:center;gap:5px;
}
.badge-red{
    background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.35);color:#f87171;
    padding:4px 12px;border-radius:20px;font-size:0.55rem;font-weight:700;
}
.pulse-dot{
    display:inline-block;width:5px;height:5px;background:#4ade80;border-radius:50%;
    animation:pulse-anim 1.5s infinite;
}
@keyframes pulse-anim{
    0%,100%{box-shadow:0 0 0 0 rgba(74,222,128,0.5);}
    50%{box-shadow:0 0 0 4px rgba(74,222,128,0);}
}
.lgpd-text{
    background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.15);border-left:3px solid #dc2626;
    border-radius:10px;padding:0.8rem 1rem;margin-bottom:1rem;color:#94a3b8;
    font-size:0.72rem;line-height:1.6;
}
.lgpd-text strong{color:#fca5a5;}
.privacy-grid{display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:1rem;}
.privacy-item{
    background:rgba(10,5,7,0.8);border:1px solid rgba(180,0,0,0.12);border-radius:8px;
    padding:0.5rem 0.7rem;display:flex;align-items:center;gap:8px;
    font-size:0.68rem;color:#9ca3af;
}
.priv-icon{
    width:14px;height:14px;flex-shrink:0;
    display:inline-block;background:rgba(220,38,38,0.2);
    border-radius:3px;font-size:9px;line-height:14px;text-align:center;color:#f87171;
}
.counter{text-align:center;margin-top:0.8rem;color:#374151;font-size:0.55rem;font-family:'JetBrains Mono',monospace;}
@media (max-width: 600px){
    .card{padding:1.2rem;}
    .privacy-grid{grid-template-columns:1fr;}
    .robot-img{width:60px;height:60px;}
    .title h1{font-size:1.4rem;}
}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="scan-line"></div>
<div class="particles" id="particles"></div>
<div class="card">
    <div class="robot-wrap">
        <img class="robot-img" src="https://raw.githubusercontent.com/mariana-castro77/SentinelAI/main/robo.png" alt="Sentinel AI"
             onerror="this.outerHTML='<div style=font-size:60px;text-align:center;filter:drop-shadow(0 0 20px rgba(220,38,38,0.7))>&#129302;</div>'">
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
        <div class="privacy-item"><span class="priv-icon">🔐</span>Dados criptografados em trânsito</div>
        <div class="privacy-item"><span class="priv-icon">🎭</span>IPs mascarados por perfil</div>
        <div class="privacy-item"><span class="priv-icon">📋</span>Auditoria completa de ações</div>
        <div class="privacy-item"><span class="priv-icon">🚫</span>Zero compartilhamento externo</div>
        <div class="privacy-item"><span class="priv-icon">💾</span>Backup automático SQLite</div>
        <div class="privacy-item"><span class="priv-icon">⏱️</span>Sessões com timeout automático</div>
    </div>
    <div class="counter">
        <span class="pulse-dot"></span>MONITORAMENTO ATIVO · <span id="ctime"></span>
    </div>
</div>
<script>
const pc = document.getElementById('particles');
for(let i=0;i<20;i++){
    const p=document.createElement('div'); p.className='particle';
    p.style.left=Math.random()*100+'%';
    p.style.animationDuration=(8+Math.random()*12)+'s';
    p.style.animationDelay=(-Math.random()*20)+'s';
    const sz=1+Math.random()*2;
    p.style.width=p.style.height=sz+'px';
    p.style.background=`rgba(${Math.random()>.5?'220,38,38':'139,0,0'},${0.2+Math.random()*0.4})`;
    pc.appendChild(p);
}
function tick(){ document.getElementById('ctime').textContent=new Date().toLocaleTimeString('pt-BR'); }
tick(); setInterval(tick,1000);
</script>
</body>
</html>"""

    components.html(lgpd_html, height=600, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ ACEITAR E CONTINUAR", use_container_width=True, key="lgpd_accept"):
            st.session_state["lgpd"] = True
            log("sistema", "LGPD_ACEITO")
            st.rerun()
    with col2:
        if st.button("❌ RECUSAR (BLOQUEIA ACESSO)", use_container_width=True, key="lgpd_reject"):
            st.error("Você recusou os termos. Acesso bloqueado.")
            st.stop()
    st.stop()

# ─── LOGIN ────────────────────────────────────────────────────────────────────
if not st.session_state["authed"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none!important;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 2rem;">
        <h1 style="font-size:2.8rem;font-weight:900;color:white;letter-spacing:-1px;margin:0;">
            Sentinel<span style="color:#dc2626;">AI</span>
        </h1>
        <p style="color:#6b7280;font-size:0.9rem;margin:8px 0 0;">Security Operations Center — Plataforma de Inteligência Cibernética</p>
        <div style="display:flex;gap:10px;justify-content:center;margin-top:14px;flex-wrap:wrap;">
          <span class="badge-online">&#9679; SISTEMA OPERACIONAL</span>
          <span class="badge-critical">ACESSO RESTRITO</span>
        </div>
    </div>""", unsafe_allow_html=True)

    _, col_login, _ = st.columns([1, 1.4, 1])
    with col_login:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(139,0,0,0.07),rgba(10,5,7,0.98));
                    border:1px solid rgba(180,0,0,0.2);border-radius:20px;padding:2rem;margin-bottom:1.2rem;
                    box-shadow:0 24px 80px rgba(139,0,0,0.2);">
          <p style="color:#6b7280;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:1rem;">
            Credenciais de Acesso
          </p>""", unsafe_allow_html=True)
        creds = [
            ("admin","admin123","Administrador"),("analista","analista123","Analista SOC"),
            ("nubank","nubank123","Nubank"),("mercadolivre","ml123","Mercado Livre"),
            ("santander","sant123","Santander"),("ifood","ifood123","iFood"),("viewer","viewer123","Visualizador")
        ]
        for u, p, label in creds:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;
                        border-radius:8px;margin:3px 0;background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.1);">
              <span style="color:#e2e8f0;font-size:0.72rem;font-weight:500;">{label}</span>
              <code style="color:#f87171;font-size:0.65rem;background:rgba(220,38,38,0.08);padding:2px 8px;border-radius:4px;">{u} / {p}</code>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            u_in = st.text_input("", placeholder="Usuario", label_visibility="collapsed")
            p_in = st.text_input("", placeholder="Senha", type="password", label_visibility="collapsed")
            ok = st.form_submit_button("ACESSAR O SISTEMA", use_container_width=True)
        if ok:
            if auth(u_in.strip(), p_in):
                st.session_state.update({"authed":True,"user":u_in.strip(),"show_prospect":False})
                log(u_in.strip(),"LOGIN","Acesso concedido")
                st.rerun()
            else:
                log(u_in.strip() or "?","LOGIN_FAIL","Credenciais inválidas")
                st.error("Usuário ou senha incorretos.")

        # ── Divisor prospect ──────────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin:1.2rem 0 0.8rem;">
          <div style="flex:1;height:1px;background:rgba(180,0,0,0.15);"></div>
          <span style="color:#374151;font-size:0.62rem;font-weight:600;letter-spacing:0.08em;white-space:nowrap;">
            AINDA NÃO É CLIENTE?
          </span>
          <div style="flex:1;height:1px;background:rgba(180,0,0,0.15);"></div>
        </div>""", unsafe_allow_html=True)

        if st.button(
            "Conheça os planos SentinelAI",
            use_container_width=True,
            key="btn_prospect"
        ):
            st.session_state["show_prospect"] = not st.session_state["show_prospect"]
            st.rerun()

    # ── Landing page de prospecção ─────────────────────────────────────────────
    if st.session_state["show_prospect"]:
        prospect_html = _PROSPECT_HTML  # definido abaixo
        components.html(prospect_html, height=5400, scrolling=True)

    st.stop()

# ─── HTML DA LANDING PAGE (definido como constante para não poluir o fluxo) ──
_PROSPECT_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{
  --r9:#7f1d1d;--r8:#991b1b;--r7:#b91c1c;--r6:#dc2626;--r4:#f87171;--r3:#fca5a5;
  --bg:#060508;--card:rgba(10,5,7,0.95);--brd:rgba(180,0,0,0.2);--brdh:rgba(220,38,38,0.45);
  --tm:#6b7280;--td:#94a3b8;--tb:#cbd5e1;--tw:#f1f5f9;
}
html{scroll-behavior:smooth;}
body{font-family:'Inter',system-ui,sans-serif;
  background:radial-gradient(ellipse at 20% 50%,rgba(139,0,0,0.18) 0%,transparent 60%),
             radial-gradient(ellipse at 80% 20%,rgba(180,0,0,0.12) 0%,transparent 55%),
             radial-gradient(ellipse at 50% 80%,rgba(100,0,0,0.10) 0%,transparent 50%),#060508;
  color:var(--tb);min-height:100vh;}
.grid-bg{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(180,0,0,0.035) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(180,0,0,0.035) 1px,transparent 1px);
  background-size:60px 60px;}
.scan{position:fixed;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(220,38,38,0.4),transparent);
  animation:sc 7s linear infinite;pointer-events:none;z-index:1;}
@keyframes sc{0%{top:-1px;}100%{top:100vh;}}
.wrap{max-width:1060px;margin:0 auto;padding:0 22px;position:relative;z-index:2;}

/* NAV */
nav{position:sticky;top:0;z-index:100;background:rgba(6,5,8,0.93);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--brd);padding:13px 0;}
.nav-in{max-width:1060px;margin:0 auto;padding:0 22px;display:flex;justify-content:space-between;align-items:center;}
.logo{font-size:1.35rem;font-weight:900;letter-spacing:-0.5px;color:var(--tw);text-decoration:none;}
.logo s{color:var(--r6);font-style:normal;text-decoration:none;}
.logo sub{font-size:0.44rem;color:var(--tm);font-weight:500;letter-spacing:0.12em;text-transform:uppercase;
  margin-left:6px;vertical-align:0.2em;font-family:'JetBrains Mono',monospace;}
.bon{display:inline-flex;align-items:center;gap:5px;
  background:rgba(0,255,100,0.05);border:1px solid rgba(0,255,100,0.2);color:#4ade80;
  padding:4px 12px;border-radius:20px;font-size:0.57rem;font-weight:700;letter-spacing:0.1em;}
.dot{display:inline-block;width:5px;height:5px;background:#4ade80;border-radius:50%;animation:pa 1.6s infinite;}
@keyframes pa{0%,100%{box-shadow:0 0 0 0 rgba(74,222,128,0.4);}50%{box-shadow:0 0 0 5px rgba(74,222,128,0);}}

/* HERO */
.hero{padding:88px 0 68px;text-align:center;}
.eye{display:inline-block;margin-bottom:20px;
  background:rgba(139,0,0,0.1);border:1px solid rgba(220,38,38,0.25);color:var(--r4);
  padding:5px 18px;border-radius:20px;font-size:0.61rem;font-weight:700;letter-spacing:0.14em;
  text-transform:uppercase;font-family:'JetBrains Mono',monospace;}
.hero h1{font-size:clamp(2.3rem,6vw,4rem);font-weight:900;color:var(--tw);
  letter-spacing:-1.5px;line-height:1.06;margin-bottom:20px;}
.hero h1 em{color:var(--r6);font-style:normal;}
.hero p{font-size:clamp(0.88rem,2vw,1.02rem);color:var(--td);max-width:600px;
  margin:0 auto 34px;line-height:1.75;font-weight:400;}
.cta{display:inline-flex;gap:12px;flex-wrap:wrap;justify-content:center;}
.btn-p{background:linear-gradient(135deg,var(--r9),var(--r8),var(--r7));color:white;
  border:1px solid rgba(220,38,38,0.4);border-radius:11px;padding:13px 28px;
  font-weight:700;font-size:0.79rem;letter-spacing:0.06em;text-transform:uppercase;
  cursor:pointer;transition:all .22s;text-decoration:none;box-shadow:0 6px 20px rgba(139,0,0,0.35);}
.btn-p:hover{background:linear-gradient(135deg,var(--r8),var(--r7),var(--r6));
  transform:translateY(-2px);box-shadow:0 10px 30px rgba(220,38,38,0.4);}
.btn-g{background:transparent;color:var(--td);border:1px solid var(--brd);border-radius:11px;
  padding:13px 28px;font-weight:600;font-size:0.79rem;cursor:pointer;transition:all .22s;text-decoration:none;}
.btn-g:hover{border-color:var(--brdh);color:var(--r4);}

/* STATS */
.stats{border-top:1px solid var(--brd);border-bottom:1px solid var(--brd);padding:26px 0;margin-bottom:76px;}
.stats-in{max-width:1060px;margin:0 auto;padding:0 22px;
  display:flex;justify-content:space-around;flex-wrap:wrap;gap:22px;}
.sv{font-size:1.65rem;font-weight:900;color:var(--r4);font-family:'JetBrains Mono',monospace;line-height:1;text-align:center;}
.sl{color:var(--tm);font-size:0.61rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;text-align:center;}

/* SECTION */
.sec{padding:68px 0;}
.slbl{color:var(--r4);font-size:0.59rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;
  font-family:'JetBrains Mono',monospace;margin-bottom:11px;}
.stit{font-size:clamp(1.45rem,3.5vw,2.1rem);font-weight:800;color:var(--tw);letter-spacing:-0.5px;margin-bottom:13px;}
.ssub{color:var(--td);font-size:0.9rem;line-height:1.72;max-width:540px;}

/* SERVICES */
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:15px;margin-top:40px;}
.sc{background:var(--card);border:1px solid var(--brd);border-radius:16px;padding:24px 26px;
  position:relative;overflow:hidden;transition:all .28s cubic-bezier(0.4,0,.2,1);}
.sc::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(220,38,38,0.5),transparent);opacity:0;transition:opacity .28s;}
.sc:hover{border-color:var(--brdh);transform:translateY(-3px);box-shadow:0 12px 40px rgba(139,0,0,0.2);}
.sc:hover::before{opacity:1;}
.si{width:36px;height:36px;background:rgba(139,0,0,0.12);border:1px solid rgba(220,38,38,0.2);
  border-radius:9px;display:flex;align-items:center;justify-content:center;margin-bottom:14px;font-size:0.95rem;}
.sn{color:var(--tw);font-size:0.9rem;font-weight:700;margin-bottom:7px;}
.sd{color:var(--td);font-size:0.77rem;line-height:1.65;}
.stag{display:inline-block;margin-top:13px;background:rgba(139,0,0,0.1);border:1px solid rgba(220,38,38,0.18);
  color:var(--r4);padding:3px 10px;border-radius:20px;font-size:0.57rem;font-weight:700;
  letter-spacing:0.08em;font-family:'JetBrains Mono',monospace;}

/* PRICING */
.pg{display:grid;grid-template-columns:repeat(auto-fit,minmax(295px,1fr));gap:17px;margin-top:40px;}
.pc{background:var(--card);border:1px solid var(--brd);border-radius:18px;padding:28px 26px;
  position:relative;overflow:hidden;transition:all .28s cubic-bezier(0.4,0,.2,1);cursor:pointer;}
.pc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(220,38,38,0.4),transparent);}
.pc.featured{border-color:rgba(220,38,38,0.5);
  background:linear-gradient(145deg,rgba(139,0,0,0.1),rgba(10,5,7,0.98));
  box-shadow:0 0 0 1px rgba(220,38,38,0.12),0 16px 50px rgba(139,0,0,0.22);}
.pc.featured::before{background:linear-gradient(90deg,transparent,rgba(220,38,38,0.8),transparent);opacity:1;}
.pc.selected{border-color:rgba(220,38,38,0.7)!important;
  box-shadow:0 0 0 2px rgba(220,38,38,0.25),0 16px 50px rgba(139,0,0,0.3)!important;
  transform:translateY(-4px);}
.pc:hover:not(.selected){border-color:rgba(220,38,38,0.35);transform:translateY(-2px);}
.pb{display:inline-block;margin-bottom:13px;background:rgba(220,38,38,0.15);
  border:1px solid rgba(220,38,38,0.3);color:var(--r4);padding:3px 12px;border-radius:20px;
  font-size:0.57rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
  font-family:'JetBrains Mono',monospace;}
.pb.pop{background:rgba(220,38,38,0.2);border-color:rgba(220,38,38,0.5);color:var(--r3);}
.pn{color:var(--tw);font-size:1.08rem;font-weight:800;margin-bottom:3px;}
.pt{color:var(--tm);font-size:0.71rem;margin-bottom:18px;}
.pm{color:var(--tw);font-size:1.95rem;font-weight:900;font-family:'JetBrains Mono',monospace;letter-spacing:-1px;}
.pm span{color:var(--r4);font-size:0.98rem;font-weight:600;vertical-align:top;margin-top:5px;display:inline-block;}
.pp{color:var(--tm);font-size:0.69rem;margin:4px 0 2px;}
.pa{color:#4ade80;font-size:0.67rem;font-weight:600;margin-bottom:18px;}
.pdiv{border:none;border-top:1px solid rgba(180,0,0,0.12);margin:16px 0;}
.pf{list-style:none;padding:0;margin-bottom:22px;}
.pf li{display:flex;align-items:flex-start;gap:7px;color:var(--td);font-size:0.75rem;line-height:1.55;margin-bottom:8px;}
.pf li .ck{color:var(--r4);font-size:0.69rem;flex-shrink:0;margin-top:2px;}
.pf li .xk{color:#374151;font-size:0.69rem;flex-shrink:0;margin-top:2px;}
.pf li.dis{color:#374151;}
.bpl{width:100%;padding:11px;border-radius:10px;font-weight:700;font-size:0.74rem;
  letter-spacing:0.06em;text-transform:uppercase;cursor:pointer;transition:all .22s;
  border:1px solid rgba(220,38,38,0.3);background:rgba(139,0,0,0.12);color:var(--r4);}
.bpl:hover,.bpl.active{background:linear-gradient(135deg,var(--r9),var(--r8));
  color:white;border-color:rgba(220,38,38,0.5);box-shadow:0 4px 16px rgba(139,0,0,0.3);}
.bpl.active{background:linear-gradient(135deg,var(--r7),var(--r6));}

/* BILLING TABS */
.tabs{display:flex;gap:4px;background:rgba(10,5,7,0.85);border:1px solid rgba(180,0,0,0.1);
  border-radius:12px;padding:4px;margin-top:40px;width:fit-content;}
.tb{padding:9px 20px;border-radius:8px;font-size:0.71rem;font-weight:700;
  letter-spacing:0.06em;text-transform:uppercase;cursor:pointer;
  color:var(--tm);background:transparent;border:none;transition:all .2s;}
.tb.active{background:linear-gradient(135deg,rgba(139,0,0,0.4),rgba(180,0,0,0.25));
  color:var(--r4);box-shadow:0 0 12px rgba(180,0,0,0.18);}

/* FORM */
.fsec{background:var(--card);border:1px solid var(--brd);border-radius:20px;
  padding:38px 42px;margin-top:18px;position:relative;overflow:hidden;}
.fsec::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(220,38,38,0.6),transparent);}
.fg{display:grid;grid-template-columns:1fr 1fr;gap:15px;}
.fgrp{display:flex;flex-direction:column;gap:6px;}
.fgrp.full{grid-column:1/-1;}
.flbl{color:var(--tm);font-size:0.64rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;}
.flbl .req{color:var(--r4);margin-left:2px;}
.fi,.fsel,.fta{background:rgba(15,7,9,0.8);border:1px solid rgba(180,0,0,0.2);
  border-radius:10px;color:var(--tw);font-family:'Inter',sans-serif;font-size:0.81rem;
  padding:11px 13px;outline:none;transition:border-color .2s,box-shadow .2s;-webkit-appearance:none;}
.fi::placeholder,.fta::placeholder{color:var(--tm);}
.fi:focus,.fsel:focus,.fta:focus{border-color:rgba(220,38,38,0.5);box-shadow:0 0 0 3px rgba(220,38,38,0.08);}
.fsel{cursor:pointer;}
.fsel option{background:#0f0507;color:var(--tw);}
.fta{resize:vertical;min-height:98px;line-height:1.6;}
.spd{background:rgba(139,0,0,0.1);border:1px solid rgba(220,38,38,0.25);
  border-radius:10px;padding:11px 13px;color:var(--r3);font-size:0.81rem;font-weight:600;
  min-height:43px;display:flex;align-items:center;gap:7px;}
.spd.empty{color:var(--tm);font-weight:400;}
.bsub{width:100%;padding:14px;border-radius:12px;font-weight:800;font-size:0.84rem;
  letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;transition:all .25s;
  background:linear-gradient(135deg,var(--r9),var(--r8),var(--r7));color:white;
  border:1px solid rgba(220,38,38,0.4);box-shadow:0 6px 24px rgba(139,0,0,0.35);margin-top:22px;}
.bsub:hover{background:linear-gradient(135deg,var(--r8),var(--r7),var(--r6));
  transform:translateY(-2px);box-shadow:0 12px 36px rgba(220,38,38,0.4);}
.bsub:active{transform:translateY(0);}
.fnote{color:var(--tm);font-size:0.64rem;text-align:center;margin-top:13px;line-height:1.6;}

/* SUCCESS */
.succ{display:none;text-align:center;padding:48px 20px;}
.succ.show{display:block;}
.succ-icon{width:68px;height:68px;background:rgba(0,200,80,0.08);
  border:2px solid rgba(0,200,80,0.25);border-radius:50%;display:flex;align-items:center;
  justify-content:center;margin:0 auto 22px;font-size:1.75rem;}
.succ-title{color:var(--tw);font-size:1.35rem;font-weight:800;margin-bottom:9px;}
.succ-co{color:var(--r4);}
.succ-body{color:var(--td);font-size:0.84rem;line-height:1.75;max-width:450px;margin:0 auto 26px;}

/* FAQ */
.faq{margin-top:18px;}
.fi-wrap{background:var(--card);border:1px solid var(--brd);border-radius:12px;margin-bottom:7px;overflow:hidden;}
.fq{width:100%;padding:15px 19px;text-align:left;background:none;border:none;
  color:var(--tw);font-size:0.81rem;font-weight:600;cursor:pointer;
  display:flex;justify-content:space-between;align-items:center;gap:11px;transition:color .2s;}
.fq:hover{color:var(--r4);}
.fq .arr{color:var(--tm);font-size:0.69rem;transition:transform .22s;flex-shrink:0;}
.fq.open .arr{transform:rotate(180deg);color:var(--r4);}
.fa{max-height:0;overflow:hidden;transition:max-height .3s ease,padding .3s ease;
  color:var(--td);font-size:0.79rem;line-height:1.7;padding:0 19px;}
.fa.open{max-height:200px;padding:0 19px 15px;}

/* FOOTER */
footer{border-top:1px solid var(--brd);padding:30px 0;margin-top:76px;
  text-align:center;color:var(--tm);font-size:0.67rem;}

@media(max-width:660px){
  .fg{grid-template-columns:1fr;}
  .fsec{padding:26px 18px;}
  .pg{grid-template-columns:1fr;}
  .stats-in{gap:26px;}
  .hero{padding:56px 0 46px;}
  .sec{padding:46px 0;}
}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="scan"></div>

<nav>
  <div class="nav-in">
    <a href="#" class="logo">Sentinel<s>AI</s><sub>SOC PLATFORM</sub></a>
    <span class="bon"><span class="dot"></span>SISTEMA OPERACIONAL</span>
  </div>
</nav>

<section class="hero">
  <div class="wrap">
    <div class="eye">Seguranca Cibernetica Gerenciada &middot; SOC 24/7</div>
    <h1>Protecao de nivel corporativo<br>para a <em>sua empresa</em></h1>
    <p>A SentinelAI opera um Centro de Operacoes de Seguranca com monitoramento continuo, inteligencia artificial e resposta a incidentes em tempo real — para que voce cuide do negocio enquanto nos cuidamos das ameacas.</p>
    <div class="cta">
      <a href="#planos" class="btn-p">Ver planos e precos</a>
      <a href="#contato" class="btn-g">Falar com um especialista</a>
    </div>
  </div>
</section>

<div class="stats">
  <div class="stats-in">
    <div><div class="sv">99,97%</div><div class="sl">Disponibilidade do SOC</div></div>
    <div><div class="sv">&lt; 4 min</div><div class="sl">Tempo medio de deteccao</div></div>
    <div><div class="sv">23 Bi+</div><div class="sl">Ameacas bloqueadas/ano BR</div></div>
    <div><div class="sv">LGPD</div><div class="sl">Conformidade certificada</div></div>
  </div>
</div>

<section class="sec" id="servicos">
  <div class="wrap">
    <div class="slbl">O que entregamos</div>
    <div class="stit">Solucoes de seguranca end-to-end</div>
    <p class="ssub">Do monitoramento continuo a resposta forense, a SentinelAI cobre todo o ciclo de vida da ameaca com tecnologia propria e analistas especializados.</p>
    <div class="sg">
      <div class="sc"><div class="si">&#128737;</div><div class="sn">SOC como Servico</div><div class="sd">Centro de Operacoes de Seguranca dedicado com analistas 24h/7d monitorando sua infraestrutura, correlacionando eventos e emitindo alertas priorizados por severidade.</div><span class="stag">24 x 7 x 365</span></div>
      <div class="sc"><div class="si">&#128269;</div><div class="sn">Deteccao e Resposta (MDR)</div><div class="sd">Identificacao proativa de ameacas avancadas com EDR/XDR, threat hunting manual e contencao automatizada de incidentes em minutos, nao em dias.</div><span class="stag">MDR / XDR</span></div>
      <div class="sc"><div class="si">&#129302;</div><div class="sn">Inteligencia Artificial</div><div class="sd">Motor de IA treinado em dados de ameacas globais classifica incidentes, prediz severidade e reduz falsos positivos em ate 87% — permitindo que seus times foquem no que importa.</div><span class="stag">Machine Learning</span></div>
      <div class="sc"><div class="si">&#128200;</div><div class="sn">Gestao de Vulnerabilidades</div><div class="sd">Escaneamento continuo, priorizacao por risco real de negocio e plano de remediacao com SLA definido por criticidade de ativo.</div><span class="stag">CTEM / RBVM</span></div>
      <div class="sc"><div class="si">&#128196;</div><div class="sn">Conformidade e LGPD</div><div class="sd">Dashboards de conformidade, relatorios de auditoria e evidencias para atender LGPD, ISO 27001 e PCI-DSS. Historico completo de acoes e eventos para a ANPD.</div><span class="stag">GRC / ISO 27001</span></div>
      <div class="sc"><div class="si">&#127758;</div><div class="sn">Threat Intelligence Global</div><div class="sd">Feeds de inteligencia de ameacas de mais de 190 paises com correlacao de APTs, grupos criminosos e campanhas ativas para antecipar ataques antes que ocorram.</div><span class="stag">Threat Intel</span></div>
    </div>
  </div>
</section>

<section class="sec" id="planos">
  <div class="wrap">
    <div class="slbl">Planos e investimento</div>
    <div class="stit">Escolha a cobertura ideal</div>
    <p class="ssub">Contratos anuais com SLA garantido. Todos os planos incluem onboarding dedicado, relatorios mensais e acesso a plataforma SentinelAI.</p>

    <div class="tabs">
      <button class="tb active" onclick="swBill('monthly',this)">Mensal</button>
      <button class="tb" onclick="swBill('annual',this)">Anual &mdash; 2 meses gratis</button>
    </div>

    <div class="pg" id="pgrid">
      <!-- ESSENCIAL -->
      <div class="pc" id="pc-e" onclick="selPlan('Essencial — Monitoramento 24/7',this)">
        <span class="pb">Essencial</span>
        <div class="pn">Essencial</div>
        <div class="pt">Para empresas que dao os primeiros passos em seguranca gerenciada</div>
        <div class="pm" data-m="8.900" data-a="7.417"><span>R$</span><span id="pv-e">8.900</span></div>
        <div class="pp">/mes &middot; ate 150 ativos monitorados</div>
        <div class="pa" id="pa-e" style="visibility:hidden">R$ 89.004/ano &mdash; economia de R$ 17.796</div>
        <hr class="pdiv">
        <ul class="pf">
          <li><span class="ck">+</span>SOC monitoramento 8h/dia (horario comercial)</li>
          <li><span class="ck">+</span>SIEM basico com retencao de 30 dias</li>
          <li><span class="ck">+</span>Gestao de vulnerabilidades mensal</li>
          <li><span class="ck">+</span>Relatorio executivo mensal</li>
          <li><span class="ck">+</span>Suporte por e-mail (SLA 8h)</li>
          <li class="dis"><span class="xk">-</span>Threat hunting proativo</li>
          <li class="dis"><span class="xk">-</span>Resposta a incidentes inclusa</li>
          <li class="dis"><span class="xk">-</span>CISO virtual dedicado</li>
        </ul>
        <button class="bpl" id="bb-e">Selecionar plano</button>
      </div>

      <!-- PROFESSIONAL -->
      <div class="pc featured" id="pc-p" onclick="selPlan('Professional — SOC 24/7 + MDR',this)">
        <span class="pb pop">Mais contratado</span>
        <div class="pn">Professional</div>
        <div class="pt">SOC 24/7 completo com deteccao e resposta a incidentes</div>
        <div class="pm" data-m="19.900" data-a="16.583"><span>R$</span><span id="pv-p">19.900</span></div>
        <div class="pp">/mes &middot; ate 500 ativos monitorados</div>
        <div class="pa" id="pa-p" style="visibility:hidden">R$ 198.996/ano &mdash; economia de R$ 39.804</div>
        <hr class="pdiv">
        <ul class="pf">
          <li><span class="ck">+</span>SOC monitoramento 24h/7d/365</li>
          <li><span class="ck">+</span>SIEM avancado com retencao de 90 dias</li>
          <li><span class="ck">+</span>MDR &mdash; deteccao e resposta gerenciada</li>
          <li><span class="ck">+</span>Gestao de vulnerabilidades continua</li>
          <li><span class="ck">+</span>Threat hunting mensal</li>
          <li><span class="ck">+</span>Relatorios semanais e dashboard ao vivo</li>
          <li><span class="ck">+</span>Suporte prioritario 24/7 (SLA 2h)</li>
          <li class="dis"><span class="xk">-</span>CISO virtual dedicado</li>
        </ul>
        <button class="bpl" id="bb-p">Selecionar plano</button>
      </div>

      <!-- ENTERPRISE -->
      <div class="pc" id="pc-n" onclick="selPlan('Enterprise — Cobertura Total + CISO Virtual',this)">
        <span class="pb">Enterprise</span>
        <div class="pn">Enterprise</div>
        <div class="pt">Cobertura total para grandes organizacoes e infraestruturas criticas</div>
        <div class="pm" data-m="49.900" data-a="41.583"><span>R$</span><span id="pv-n">49.900</span></div>
        <div class="pp">/mes &middot; ativos ilimitados</div>
        <div class="pa" id="pa-n" style="visibility:hidden">R$ 498.996/ano &mdash; economia de R$ 99.804</div>
        <hr class="pdiv">
        <ul class="pf">
          <li><span class="ck">+</span>Tudo do plano Professional</li>
          <li><span class="ck">+</span>CISO virtual dedicado (reunioes semanais)</li>
          <li><span class="ck">+</span>Red team e pentest trimestral incluso</li>
          <li><span class="ck">+</span>SIEM ilimitado com retencao de 12 meses</li>
          <li><span class="ck">+</span>Threat hunting continuo e dedicado</li>
          <li><span class="ck">+</span>Resposta a incidentes on-site inclusa</li>
          <li><span class="ck">+</span>Relatorio de conformidade ISO/LGPD</li>
          <li><span class="ck">+</span>SLA de resposta garantido em 30 minutos</li>
        </ul>
        <button class="bpl" id="bb-n">Selecionar plano</button>
      </div>
    </div>

    <p style="color:var(--tm);font-size:0.67rem;margin-top:16px;text-align:center;">
      Todos os valores em BRL. Contratos com fidelidade minima de 12 meses. Precos sujeitos a ajuste conforme escopo tecnico apos avaliacao inicial sem custo.
    </p>
  </div>
</section>

<section class="sec" id="contato">
  <div class="wrap">
    <div class="slbl">Solicitar proposta</div>
    <div class="stit">Fale com nossa equipe comercial</div>
    <p class="ssub">Preencha o formulario abaixo. Um especialista SentinelAI entrara em contato em ate 1 dia util com uma proposta personalizada para o seu ambiente.</p>

    <div class="fsec" id="fwrap">
      <div id="cform">
        <div class="fg">
          <div class="fgrp">
            <label class="flbl">Nome da Empresa <span class="req">*</span></label>
            <input type="text" class="fi" id="fe" placeholder="Ex.: Acme Solucoes Ltda." required>
          </div>
          <div class="fgrp">
            <label class="flbl">Seu Nome <span class="req">*</span></label>
            <input type="text" class="fi" id="fn" placeholder="Nome completo" required>
          </div>
          <div class="fgrp">
            <label class="flbl">E-mail Corporativo <span class="req">*</span></label>
            <input type="email" class="fi" id="fem" placeholder="voce@empresa.com.br" required>
          </div>
          <div class="fgrp">
            <label class="flbl">Telefone / WhatsApp</label>
            <input type="tel" class="fi" id="ft" placeholder="(11) 9 0000-0000">
          </div>
          <div class="fgrp">
            <label class="flbl">Numero de colaboradores <span class="req">*</span></label>
            <select class="fsel" id="fp">
              <option value="">Selecione</option>
              <option>1 a 50</option>
              <option>51 a 200</option>
              <option>201 a 1.000</option>
              <option>1.001 a 5.000</option>
              <option>Acima de 5.000</option>
            </select>
          </div>
          <div class="fgrp">
            <label class="flbl">Setor de atuacao <span class="req">*</span></label>
            <select class="fsel" id="fse">
              <option value="">Selecione</option>
              <option>Financeiro / Fintechs</option>
              <option>Varejo / E-commerce</option>
              <option>Saude</option>
              <option>Industria / Manufatura</option>
              <option>Tecnologia / SaaS</option>
              <option>Telecomunicacoes</option>
              <option>Educacao</option>
              <option>Governo / Setor Publico</option>
              <option>Logistica / Transporte</option>
              <option>Outro</option>
            </select>
          </div>
          <div class="fgrp full">
            <label class="flbl">Servico de interesse</label>
            <div class="spd empty" id="spd">Nenhum plano selecionado &mdash; escolha acima ou selecione abaixo</div>
            <select class="fsel" id="fpl" style="margin-top:7px;">
              <option value="">Selecione um servico</option>
              <option>Essencial — Monitoramento 24/7</option>
              <option>Professional — SOC 24/7 + MDR</option>
              <option>Enterprise — Cobertura Total + CISO Virtual</option>
              <option>Consultoria pontual / Pentest</option>
              <option>Resposta a Incidente urgente</option>
              <option>Ainda nao sei — quero orientacao</option>
            </select>
          </div>
          <div class="fgrp full">
            <label class="flbl">Contexto e principais preocupacoes</label>
            <textarea class="fta" id="fmsg" placeholder="Descreva brevemente o cenario atual: sofreu incidentes recentes, tem exigencias regulatorias, quer substituir uma solucao existente, etc. Quanto mais detalhes, mais assertiva sera nossa proposta."></textarea>
          </div>
        </div>
        <button class="bsub" onclick="subForm()">Solicitar proposta comercial</button>
        <p class="fnote">
          Ao enviar, voce concorda com nossa Politica de Privacidade (LGPD). Seus dados serao usados exclusivamente para retorno comercial.<br>
          Contato direto: <strong style="color:var(--r4);">sentinelai.contato@gmail.com</strong>
        </p>
      </div>

      <div class="succ" id="succ">
        <div class="succ-icon">&#10003;</div>
        <div class="succ-title">Solicitacao recebida, <span class="succ-co" id="sco"></span>!</div>
        <p class="succ-body">
          Obrigado pela confianca na SentinelAI. Nossa equipe comercial ja recebeu sua solicitacao e entrara em contato pelo e-mail informado em breve — fique atento a sua caixa de entrada, incluindo a pasta de spam.<br><br>
          Caso precise de atendimento imediato, escreva para <strong style="color:var(--r4);">sentinelai.contato@gmail.com</strong>.
        </p>
        <a href="#planos" class="btn-g" style="display:inline-block;">Ver novamente os planos</a>
      </div>
    </div>

    <div style="margin-top:54px;">
      <div class="slbl" style="margin-bottom:18px;">Duvidas frequentes</div>
      <div class="faq">
        <div class="fi-wrap"><button class="fq" onclick="tog(this)">Qual o prazo minimo de contrato? <span class="arr">&#9660;</span></button><div class="fa">Os contratos tem fidelidade minima de 12 meses, com renovacao automatica anual. Esse periodo e necessario porque os primeiros 60 a 90 dias sao dedicados ao onboarding, integracao com seu ambiente e calibracao das regras de deteccao.</div></div>
        <div class="fi-wrap"><button class="fq" onclick="tog(this)">Consigo comecar com o plano Essencial e migrar depois? <span class="arr">&#9660;</span></button><div class="fa">Sim. A migracao entre planos e feita com aviso previo de 30 dias. O onboarding inicial ja e projetado para facilitar a expansao futura, sem necessidade de reimplementar integracoes.</div></div>
        <div class="fi-wrap"><button class="fq" onclick="tog(this)">Os dados da minha empresa ficam na SentinelAI? <span class="arr">&#9660;</span></button><div class="fa">Eventos de seguranca ficam armazenados em ambiente isolado por cliente, com criptografia em repouso e em transito. Nenhum dado e compartilhado entre clientes. O contrato define claramente propriedade, retencao e descarte conforme a LGPD.</div></div>
        <div class="fi-wrap"><button class="fq" onclick="tog(this)">Ja temos uma equipe de TI interna. Como a SentinelAI complementa? <span class="arr">&#9660;</span></button><div class="fa">A SentinelAI opera no modelo co-gerenciado: sua equipe mantem o controle do ambiente enquanto nosso SOC provem visibilidade, alertas e resposta para os eventos que exigem expertise especializada em seguranca, reduzindo a sobrecarga sem remover autonomia.</div></div>
        <div class="fi-wrap"><button class="fq" onclick="tog(this)">O que acontece em caso de incidente real durante o contrato? <span class="arr">&#9660;</span></button><div class="fa">Nos planos Professional e Enterprise, a resposta a incidentes esta inclusa. Nossa equipe aciona o playbook correspondente, contem a ameaca, preserva evidencias e emite relatorio forense. No plano Essencial, o suporte a incidentes e cobrado por hora com prioridade garantida.</div></div>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div style="margin-bottom:9px;">
      <span style="color:var(--tw);font-weight:800;font-size:0.88rem;">Sentinel<span style="color:var(--r6);">AI</span></span>
      <span style="margin:0 9px;color:var(--brd);">|</span>Security Operations Center
    </div>
    <p>sentinelai.contato@gmail.com &nbsp;&middot;&nbsp; LGPD Lei 13.709/2018 &nbsp;&middot;&nbsp; ISO 27001</p>
    <p style="margin-top:5px;">&copy; 2025 SentinelAI. Todos os direitos reservados.</p>
  </div>
</footer>

<script>
let billMode='monthly', selName='';

function swBill(m,btn){
  billMode=m;
  document.querySelectorAll('.tb').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  [['e','8.900','7.417','89.004','17.796'],
   ['p','19.900','16.583','198.996','39.804'],
   ['n','49.900','41.583','498.996','99.804']].forEach(([id,mo,an,ytot,ysave])=>{
    document.getElementById('pv-'+id).textContent = m==='monthly' ? mo : an;
    document.getElementById('pa-'+id).style.visibility = m==='annual' ? 'visible' : 'hidden';
  });
}

function selPlan(name, card){
  selName=name;
  document.querySelectorAll('.pc').forEach(c=>c.classList.remove('selected'));
  document.querySelectorAll('.bpl').forEach(b=>{b.classList.remove('active');b.textContent='Selecionar plano';});
  card.classList.add('selected');
  const btn=card.querySelector('.bpl');
  btn.classList.add('active'); btn.textContent='Plano selecionado';
  const spd=document.getElementById('spd');
  spd.textContent=name; spd.classList.remove('empty');
  const sel=document.getElementById('fpl');
  for(let i=0;i<sel.options.length;i++){
    if(sel.options[i].text===name){sel.selectedIndex=i;break;}
  }
  setTimeout(()=>document.getElementById('contato').scrollIntoView({behavior:'smooth',block:'start'}),200);
}

document.getElementById('fpl').addEventListener('change',function(){
  if(this.value){
    const spd=document.getElementById('spd');
    spd.textContent=this.value; spd.classList.remove('empty');
  }
});

function subForm(){
  const e=document.getElementById('fe').value.trim();
  const n=document.getElementById('fn').value.trim();
  const em=document.getElementById('fem').value.trim();
  const p=document.getElementById('fp').value;
  const se=document.getElementById('fse').value;
  const t=document.getElementById('ft').value.trim();
  const pl=document.getElementById('fpl').value || selName || 'Nao informado';
  const msg=document.getElementById('fmsg').value.trim();
  if(!e||!n||!em||!p||!se){alert('Preencha todos os campos obrigatorios (*).'); return;}
  if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em)){alert('Informe um e-mail valido.'); return;}
  const sub=encodeURIComponent('Solicitacao de proposta — '+e);
  const body=encodeURIComponent(
    'Nova solicitacao de proposta recebida pela pagina SentinelAI.\\n\\n'+
    '--- DADOS DO PROSPECT ---\\n'+
    'Empresa: '+e+'\\nResponsavel: '+n+'\\nE-mail: '+em+
    '\\nTelefone: '+(t||'Nao informado')+'\\nPorte: '+p+
    '\\nSetor: '+se+'\\nServico de interesse: '+pl+
    '\\n\\n--- MENSAGEM ---\\n'+(msg||'Nao preenchida.')+
    '\\n\\n---\\nEnviado via pagina de prospectos SentinelAI'
  );
  window.location.href='mailto:sentinelai.contato@gmail.com?subject='+sub+'&body='+body;
  document.getElementById('cform').style.display='none';
  const s=document.getElementById('succ');
  s.classList.add('show');
  document.getElementById('sco').textContent=e;
  s.scrollIntoView({behavior:'smooth',block:'center'});
}

function tog(btn){
  const a=btn.nextElementSibling;
  const open=a.classList.contains('open');
  document.querySelectorAll('.fa').forEach(x=>x.classList.remove('open'));
  document.querySelectorAll('.fq').forEach(x=>x.classList.remove('open'));
  if(!open){a.classList.add('open');btn.classList.add('open');}
}
</script>
</body>
</html>"""

# ─── APP PRINCIPAL ─────────────────────────────────────────────────────────────
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
    Xt, Xv, yt, yv = train_test_split(X, y, test_size=0.2, random_state=42)
    m = DecisionTreeClassifier(random_state=42)
    m.fit(Xt, yt)
    acc = accuracy_score(yv, m.predict(Xv))
    return df, enc, m, acc, Xv, yv

df_all, ENC, MODEL, ACC, Xv, yv = load_data()
CLT = PROF["client"]
df = df_all[df_all["CLIENTE"] == CLT].copy() if CLT else df_all.copy()
prej = df["PREJUIZO_ESTIMADO"].sum()
total = len(df)
crit = len(df[df["SEVERIDADE"] == "crítica"])
bloq = len(df[df["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
resol = len(df[df["STATUS"] == "resolvido"])
pend = len(df[df["STATUS"] == "pendente"])

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    db_ok = os.path.exists(DB_PATH)
    db_size = round(os.path.getsize(DB_PATH)/1024, 1) if db_ok else 0

    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem 0 0.8rem;">
    <img src="https://raw.githubusercontent.com/mariana-castro77/SentinelAI/main/robo.png" class="robot-float-img" alt="Sentinel"
     onerror="this.outerHTML='<div style=font-size:52px;text-align:center;filter:drop-shadow(0 0 12px rgba(220,38,38,0.7))>&#129302;</div>'">
    <hr>
    <div style="background:rgba(139,0,0,0.07);border:1px solid rgba(180,0,0,0.15);border-radius:12px;padding:0.9rem 1rem;margin-bottom:0.8rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">OPERADOR</p>
      <p style="color:white;font-weight:700;font-size:0.9rem;margin:0;">@{USER}</p>
      <p style="color:#9ca3af;font-size:0.7rem;margin:3px 0 8px;">{PROF['role']}</p>
      <span class="badge-online">&#9679; ONLINE</span>
    </div>
    <div style="background:rgba(0,200,100,0.04);border:1px solid rgba(0,200,100,0.15);border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.5rem;">
      <p style="color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;margin-bottom:4px;">ARMAZENAMENTO</p>
      <p style="color:#4ade80;font-size:0.72rem;font-weight:600;">SQLite &middot; {db_size} KB</p>
      <p style="color:#6b7280;font-size:0.6rem;">{DB_PATH} &middot; Streamlit Cloud</p>
      <p style="color:#f59e0b;font-size:0.6rem;margin-top:3px;">Configure MYSQL_URL para persistência total</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<p style='color:#4b5563;font-size:0.55rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;'>PERMISSÕES</p>", unsafe_allow_html=True)
    for label, flag in [("Análise ML",PROF["analyze"]),("Exportar dados",PROF["export"]),("Ver IPs / PII",PROF["pii"]),("Suporte Admin",PROF["support_admin"])]:
        c_col, icon = ("#4ade80","✓") if flag else ("#ef4444","✗")
        st.markdown(f"<p style='color:{c_col};font-size:0.72rem;margin:3px 0;'><b>{icon}</b> {label}</p>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(139,0,0,0.08);border-radius:10px;padding:0.7rem 1rem;margin:0.8rem 0;text-align:center;">
      <p style="color:#4b5563;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;">Acurácia IA</p>
      <p style="color:#dc2626;font-size:1.4rem;font-weight:800;font-family:'JetBrains Mono',monospace;">{ACC:.1%}</p>
    </div>""", unsafe_allow_html=True)

    tks_side = db_buscar_tickets(CLT if CLT else None)
    n_abertos_side = len(tks_side[tks_side["status"] == "aberto"]) if not tks_side.empty else 0
    if n_abertos_side > 0:
        st.markdown(f"""<div style="background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.3);border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.8rem;text-align:center;">
          <p style="color:#f87171;font-size:0.72rem;font-weight:700;">{n_abertos_side} ticket(s) aberto(s)</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Encerrar Sessão", use_container_width=True):
        log(USER,"LOGOUT")
        st.session_state.update({"authed":False,"user":None,"chat":[],"chat_suporte":[]})
        st.rerun()

# ─── HEADER ──────────────────────────────────────────────────────────────────
now = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
scope = f"Cliente: {CLT}" if CLT else "Visão Global — Todos os Clientes"
st.markdown(f"""
<div class="soc-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
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
        <span class="badge-online">&#9679; SISTEMA ONLINE</span>
        <span class="badge-critical">LGPD COMPLIANT</span>
      </div>
      <p style="color:#374151;font-size:0.62rem;font-family:'JetBrains Mono',monospace;">{now}</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.metric("INCIDENTES", f"{total:,}")
with c2: st.metric("CRÍTICOS", f"{crit:,}")
with c3: st.metric("IPs BLOQUEADOS", f"{bloq:,}")
with c4: st.metric("RESOLVIDOS", f"{resol:,}")
with c5: st.metric("PENDENTES", f"{pend:,}")
with c6: st.metric("PREJUÍZO", f"R$ {prej/1e6:.2f}Mi")
st.markdown("<hr>", unsafe_allow_html=True)

tabs = st.tabs(["Análise","Dashboard","Mapa de Ameaças","Sentinel Bot","Suporte","Backup & DB","Auditoria"])

# ─── TAB 0: ANÁLISE ───────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("### Análise Inteligente de Incidentes")
    if not PROF["analyze"]:
        st.markdown('<div class="info-box">Perfil sem permissão para análise. Contate o Administrador.</div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de Incidente", ENC["tipo"].classes_)
            orig = st.selectbox("Origem", ENC["orig"].classes_)
            cli_af = st.selectbox("Cliente Afetado", sorted(df_all["CLIENTE"].unique()))
        with c2:
            tempo = st.slider("Tempo de Resolução (min)", 1, 120, 30)
            stat = st.selectbox("Status", ENC["stat"].classes_)
        if st.button("INICIAR ANÁLISE FORENSE", use_container_width=True):
            log(USER,"ANALISE",f"tipo={tipo}")
            with st.spinner("Processando com IA..."):
                time.sleep(1)
            entrada = pd.DataFrame({"TE":[ENC["tipo"].transform([tipo])[0]],"OE":[ENC["orig"].transform([orig])[0]],"TEMPO RESOLUÇÃO":[tempo],"SE":[ENC["stat"].transform([stat])[0]]})
            sev = ENC["sev"].inverse_transform(MODEL.predict(entrada))[0]
            if stat == "resolvido": sev = "baixa"
            elif tipo in ["ataque","falha servidor"]: sev = "crítica"
            elif tipo in ["lentidão","erro sistema"]: sev = random.choice(["baixa","média"])
            risco = random.randint(10,99)
            prej_val = random.uniform(3000,30000)
            risco_fin = "ALTO" if prej_val>15000 else ("MÉDIO" if prej_val>7000 else "BAIXO")
            atks = df_all[df_all["TIPO INCIDENTE"] == "ataque"]
            if not atks.empty:
                row = atks.sample(1).iloc[0]
                ip = str(row["IP_SUSPEITO"]) if PROF["pii"] else mask_ip(row["IP_SUSPEITO"])
                pais = row["PAIS_ATAQUE"]
            else: ip, pais = "N/A","Interno"
            st.markdown("<hr>", unsafe_allow_html=True)
            if sev == "crítica": st.error("SEVERIDADE PREVISTA: CRÍTICA")
            elif sev == "média": st.warning("SEVERIDADE PREVISTA: MÉDIA")
            else: st.success("SEVERIDADE PREVISTA: BAIXA")
            r1,r2,r3,r4 = st.columns(4)
            with r1: st.metric("THREAT SCORE", f"{risco}/100")
            with r2: st.metric("PREJUÍZO EST.", f"R$ {prej_val:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("RISCO FIN.", risco_fin)
            with r4: st.metric("CLIENTE", cli_af)
            if tipo == "ataque":
                st.error(f"Origem: {pais}  |  IP: {ip}")
                with st.expander("Resposta Automática Acionada"):
                    for a in ["IP bloqueado no firewall","Regras de firewall atualizadas","Equipe SOC notificada","Logs enviados para auditoria"]:
                        st.write(f"✓ {a}")
            saved = db_salvar_incidente({"usuario":USER,"tipo":tipo,"origem":orig,"status":stat,"severidade":sev,"cliente":cli_af,"risco":risco,"prejuizo":prej_val})
            if saved: st.success("Incidente salvo no banco de dados SQLite")
        st.markdown("### Registros do Dataset")
        cols_show = ["DATA","TIPO INCIDENTE","SEVERIDADE","STATUS","CLIENTE","PAIS_ATAQUE","PREJUIZO_ESTIMADO"]
        if PROF["pii"]: cols_show.append("IP_SUSPEITO")
        df_show = df[cols_show].copy()
        if not PROF["pii"] and "IP_SUSPEITO" in df_show.columns:
            df_show["IP_SUSPEITO"] = df_show["IP_SUSPEITO"].apply(mask_ip)
        st.dataframe(df_show, use_container_width=True, height=300)

# ─── TAB 1: DASHBOARD ─────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### Telemetria & Métricas")
    L = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8", font_family="Inter")

    g1, g2 = st.columns(2)
    with g1:
        ordem_cores = {"crítica": "#dc2626", "média": "#f59e0b", "baixa": "#22c55e"}
        fig = px.pie(df, names="SEVERIDADE", title="Distribuição de Severidade",
                     color="SEVERIDADE", color_discrete_map=ordem_cores)
        fig.update_layout(**L, title_font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        vc = df["TIPO INCIDENTE"].value_counts().reset_index()
        fig = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Incidentes por Tipo", color_discrete_sequence=["#dc2626"])
        fig.update_layout(**L, title_font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    dt = df.groupby("DATA").size().reset_index(name="n")
    fig = px.area(dt, x="DATA", y="n", title="Volume ao Longo do Tempo", color_discrete_sequence=["#dc2626"])
    fig.update_traces(fill="tozeroy", fillcolor="rgba(220,38,38,0.1)")
    fig.update_layout(**L, title_font_color="white")
    st.plotly_chart(fig, use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        fig = px.histogram(df, x="PAIS_ATAQUE", title="Ataques por País", color_discrete_sequence=["#b91c1c"])
        fig.update_layout(**L, title_font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    with g4:
        dp = df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index().sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig = px.bar(dp, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="Prejuízo por Cliente", color_discrete_sequence=["#991b1b"])
        fig.update_layout(**L, title_font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Performance do Modelo de IA")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("ACURÁCIA", f"{ACC:.1%}")
    with m2: st.metric("TREINO", f"{int(len(df_all)*0.8):,}")
    with m3: st.metric("TESTE", f"{int(len(df_all)*0.2):,}")

    ypred = MODEL.predict(Xv)
    cm = confusion_matrix(yv, ypred)
    lbs = ENC["sev"].classes_
    fig = go.Figure(go.Heatmap(z=cm, x=lbs, y=lbs, colorscale=[[0, "#0a0507"], [0.5, "#7f1d1d"], [1, "#dc2626"]], text=cm, texttemplate="%{text}", showscale=True))
    fig.update_layout(title="Matriz de Confusão", xaxis_title="Previsto", yaxis_title="Real", height=320, **L, title_font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ─── TAB 2: MAPA ─────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### Mapa Global de Ameaças Cibernéticas")
    st.caption("Globo 3D interativo · Arraste para girar · Scroll para zoom · Clique nos países para threat intel")

    atk_df = df[df["TIPO INCIDENTE"] == "ataque"]
    cc = atk_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country","total"]

    THREAT_INTEL = [
        {"country":"China","lat":35.86,"lon":104.19,"score":98,"groups":["APT41","APT10","Volt Typhoon"],"target":"Espionagem industrial · infraestrutura crítica"},
        {"country":"Russia","lat":61.52,"lon":105.31,"score":97,"groups":["APT28","APT29","Sandworm"],"target":"Governos · energia · eleições"},
        {"country":"North Korea","lat":40.33,"lon":127.51,"score":91,"groups":["Lazarus Group","Kimsuky","APT38"],"target":"Bancos · exchanges · defesa"},
        {"country":"Iran","lat":32.43,"lon":53.69,"score":85,"groups":["APT33","APT35","MuddyWater"],"target":"Energia · governo · telecom"},
        {"country":"Vietnam","lat":14.05,"lon":108.27,"score":72,"groups":["APT32"],"target":"Manufatura · governos ASEAN"},
        {"country":"Romania","lat":45.94,"lon":24.96,"score":68,"groups":["SilverTerrier"],"target":"Fraude financeira · ATM"},
        {"country":"Nigeria","lat":9.08,"lon":8.67,"score":65,"groups":["BEC groups","SilverTerrier"],"target":"Fraude BEC · phishing"},
        {"country":"Pakistan","lat":30.37,"lon":69.34,"score":62,"groups":["Transparent Tribe","APT36"],"target":"Sul-asiáticos · governo"},
        {"country":"Ukraine","lat":48.38,"lon":31.17,"score":70,"groups":["TA473"],"target":"Infraestrutura crítica"},
        {"country":"United States","lat":37.09,"lon":-95.71,"score":60,"groups":["NSA","FBI Cyber"],"target":"Principal alvo de APTs globais"},
        {"country":"Netherlands","lat":52.13,"lon":5.29,"score":55,"groups":["Bulletproof hosters"],"target":"Hospedagem maliciosa · C2"},
        {"country":"Turkey","lat":38.96,"lon":35.24,"score":58,"groups":["Sea Turtle","StrongPity"],"target":"DNS hijacking · oposição política"},
    ]

    COORDS = {
        "China":(35.86,104.19),"Russia":(61.52,105.31),"United States":(37.09,-95.71),
        "Germany":(51.16,10.45),"North Korea":(40.33,127.51),"Canada":(56.13,-106.34),
        "India":(20.59,78.96),"France":(46.23,2.21),"United Kingdom":(55.37,-3.43),
        "Iran":(32.43,53.69),"Japan":(36.20,138.25),"Australia":(-25.27,133.77),
        "South Korea":(35.90,127.76),"Ukraine":(48.38,31.17),"Romania":(45.94,24.96),
        "Nigeria":(9.08,8.67),"Pakistan":(30.37,69.34),"Vietnam":(14.05,108.27),
        "Indonesia":(-0.78,113.92),"Netherlands":(52.13,5.29),"Turkey":(38.96,35.24),
        "Argentina":(-38.41,-63.61),"Mexico":(23.63,-102.55),"Colombia":(4.57,-74.29),
    }

    arcs = []
    for _, row in cc.iterrows():
        c = row["country"]
        if c in COORDS and c != "Brazil":
            s = COORDS[c]
            arcs.append({"slat":s[0],"slon":s[1],"dlat":-14.23,"dlon":-51.92,"name":c,"n":int(row["total"])})

    extra_arcs = [
        {"slat":61.52,"slon":105.31,"dlat":-14.23,"dlon":-51.92,"name":"Russia","n":50},
        {"slat":40.33,"slon":127.51,"dlat":-14.23,"dlon":-51.92,"name":"North Korea","n":45},
        {"slat":32.43,"slon":53.69,"dlat":-14.23,"dlon":-51.92,"name":"Iran","n":35},
        {"slat":9.08,"slon":8.67,"dlat":-14.23,"dlon":-51.92,"name":"Nigeria","n":30},
        {"slat":35.86,"slon":104.19,"dlat":-14.23,"dlon":-51.92,"name":"China","n":60},
        {"slat":38.96,"slon":35.24,"dlat":-14.23,"dlon":-51.92,"name":"Turkey","n":25},
        {"slat":14.05,"slon":108.27,"dlat":-14.23,"dlon":-51.92,"name":"Vietnam","n":20},
    ]
    all_arcs = arcs + [a for a in extra_arcs if not any(x["name"]==a["name"] for x in arcs)]

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
.panel{{
    position:absolute;background:rgba(4,2,6,0.88);
    border:1px solid rgba(180,30,30,0.28);border-radius:10px;
    padding:10px 14px;backdrop-filter:blur(16px);
}}
#legend{{top:12px;left:12px;min-width:180px;}}
#legend h4{{color:#dc2626;font-size:9.5px;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;font-weight:700;}}
.leg-item{{display:flex;align-items:center;gap:7px;margin:3px 0;font-size:9px;color:#9ca3af;}}
.leg-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;}}
#counters{{top:12px;right:12px;text-align:right;min-width:130px;}}
#counters .lbl{{color:#4b5563;font-size:8px;text-transform:uppercase;letter-spacing:0.1em;}}
#counters .val{{color:#dc2626;font-size:1.25rem;font-weight:800;line-height:1.2;font-family:monospace;}}
#feed{{bottom:12px;left:12px;max-width:270px;}}
#feed h4{{color:#dc2626;font-size:8.5px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px;font-weight:700;}}
.feed-item{{color:#4b5563;font-size:8px;line-height:1.6;margin:2px 0;padding-left:6px;border-left:2px solid rgba(180,30,30,0.2);}}
.feed-item.new{{color:#f87171;border-color:#dc2626;}}
#status-bar{{bottom:12px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:7px;white-space:nowrap;}}
.pulse-dot{{width:6px;height:6px;border-radius:50%;background:#4ade80;animation:pulse 1.5s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(74,222,128,0.5);}}50%{{box-shadow:0 0 0 4px transparent;}}}}
#status-bar span{{color:#4ade80;font-size:8.5px;letter-spacing:0.06em;}}
#info-panel{{top:12px;left:50%;transform:translateX(-50%);min-width:260px;max-width:320px;display:none;z-index:20;}}
#info-panel h4{{color:#f87171;font-size:10.5px;margin-bottom:5px;font-weight:700;}}
#info-panel .sbar{{background:rgba(220,38,38,0.12);border-radius:3px;height:4px;margin:5px 0;overflow:hidden;}}
#info-panel .sfill{{height:100%;background:linear-gradient(90deg,#7f1d1d,#dc2626);border-radius:3px;transition:width .4s;}}
#info-panel p{{color:#9ca3af;font-size:8.5px;line-height:1.6;margin:2px 0;}}
#info-panel .grp{{color:#fca5a5;font-size:8.5px;}}
#close-info{{position:absolute;top:7px;right:9px;color:#6b7280;cursor:pointer;font-size:13px;background:none;border:none;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="overlay" style="position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;">
  <div class="panel" id="legend">
    <h4>Threat Intelligence</h4>
    <div class="leg-item"><div class="leg-dot" style="background:#ff1a1a"></div>Score 90-100 — APT Nação</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ff6600"></div>Score 70-89 — Alto risco</div>
    <div class="leg-item"><div class="leg-dot" style="background:#ffaa00"></div>Score 50-69 — Moderado</div>
    <div class="leg-item"><div class="leg-dot" style="background:#00ff88"></div>Brasil — Alvo protegido</div>
    <div class="leg-item" style="margin-top:5px;color:#374151;font-size:8px;">Arraste · Scroll = Zoom · Clique = Info</div>
  </div>
  <div class="panel" id="counters">
    <div class="lbl">Ataques detectados</div>
    <div class="val" id="atk-val">0</div>
    <div class="lbl" style="margin-top:5px;">IPs bloqueados</div>
    <div class="val" id="blk-val">0</div>
    <div class="lbl" style="margin-top:5px;">Países em alerta</div>
    <div class="val" id="ctr-val">0</div>
  </div>
  <div class="panel" id="feed">
    <h4>Feed ao vivo</h4>
    <div id="feed-list"></div>
  </div>
  <div class="panel" id="status-bar">
    <div class="pulse-dot"></div>
    <span>THREAT MONITORING — TEMPO REAL</span>
  </div>
  <div class="panel" id="info-panel" style="pointer-events:all;">
    <button id="close-info" onclick="document.getElementById('info-panel').style.display='none'">&#10005;</button>
    <h4 id="ip-name"></h4>
    <div class="sbar"><div class="sfill" id="ip-bar"></div></div>
    <p id="ip-score"></p>
    <p id="ip-target"></p>
    <div class="grp" id="ip-groups"></div>
  </div>
</div>
<script>
const ARCS={json.dumps(all_arcs)};
const THREATS={json.dumps(THREAT_INTEL)};
const TMAP={{}};
THREATS.forEach(t=>TMAP[t.country]=t);
document.getElementById('ctr-val').textContent=THREATS.length;

const C=document.getElementById('c');
const ctx=C.getContext('2d');
let W,H;
function resize(){{W=C.width=window.innerWidth;H=C.height=window.innerHeight;}}
resize(); window.addEventListener('resize',resize);

let rotY=0.5,rotX=0.12,zoom=1.0,isDrag=false,lastX=0,lastY=0,frame=0,totalAtk=0,totalBlk=0;
const stars=[];
for(let i=0;i<300;i++) stars.push({{x:Math.random()*2200,y:Math.random()*1400,r:Math.random()*.9+.15,a:Math.random()*.4+.1}});

const GR=()=>Math.min(W,H)*0.36*zoom;

function ll3d(lat,lon,r){{
    const phi=(90-lat)*Math.PI/180, tht=(lon+180)*Math.PI/180;
    return {{x:r*Math.sin(phi)*Math.cos(tht), y:-r*Math.cos(phi), z:r*Math.sin(phi)*Math.sin(tht)}};
}}
function proj(x,y,z){{
    let rx=x*Math.cos(rotY)+z*Math.sin(rotY);
    let rz=-x*Math.sin(rotY)+z*Math.cos(rotY);
    let ry2=y*Math.cos(rotX)-rz*Math.sin(rotX);
    let rz2=y*Math.sin(rotX)+rz*Math.cos(rotX);
    const fov=1400, sc=fov/(fov-rz2);
    return {{px:W/2+rx*sc, py:H/2+ry2*sc, scale:sc, z:rz2}};
}}

const BORDERS=[
  {{n:"Russia",pts:[[68,32],[69,60],[72,105],[68,140],[50,142],[45,135],[44,130],[47,142],[55,120],[60,105],[68,60],[68,32]]}},
  {{n:"China",pts:[[53,122],[48,135],[40,130],[22,114],[22,108],[25,98],[28,97],[35,76],[40,76],[42,82],[48,87],[50,117],[53,122]]}},
  {{n:"USA",pts:[[49,-124],[49,-67],[25,-80],[25,-97],[30,-97],[32,-114],[37,-120],[49,-124]]}},
  {{n:"Brazil",pts:[[-5,-34],[-8,-35],[-15,-38],[-22,-43],[-33,-52],[-34,-58],[-20,-58],[-10,-68],[-4,-72],[-1,-70],[2,-50],[-5,-34]]}},
  {{n:"Europe",pts:[[70,30],[70,10],[55,8],[44,8],[44,28],[50,30],[55,24],[60,24],[70,30]]}},
  {{n:"Africa",pts:[[37,10],[37,35],[10,42],[-10,40],[-35,20],[-35,18],[-5,12],[10,-18],[37,10]]}},
  {{n:"Australia",pts:[[-14,132],[-14,142],[-28,153],[-38,146],[-37,140],[-32,115],[-20,114],[-14,126],[-14,132]]}},
  {{n:"India",pts:[[36,76],[36,80],[22,88],[8,77],[8,76],[22,70],[28,72],[36,72],[36,76]]}},
  {{n:"Canada",pts:[[83,-70],[70,-60],[50,-53],[45,-64],[45,-82],[49,-90],[49,-124],[60,-140],[72,-140],[83,-100],[83,-70]]}},
  {{n:"Mexico",pts:[[32,-117],[30,-105],[24,-98],[16,-92],[18,-88],[22,-88],[30,-110],[32,-117]]}},
  {{n:"Argentina",pts:[[-22,-63],[-22,-53],[-40,-62],[-55,-68],[-55,-66],[-40,-70],[-35,-72],[-22,-68],[-22,-63]]}},
  {{n:"Iran",pts:[[38,44],[38,62],[26,60],[26,56],[30,48],[38,44]]}},
  {{n:"Ukraine",pts:[[51,24],[52,38],[47,38],[45,34],[44,34],[46,30],[46,24],[51,24]]}},
  {{n:"SouthKorea",pts:[[38,126],[38,130],[35,130],[34,126],[38,126]]}},
  {{n:"NorthKorea",pts:[[42,124],[42,130],[40,130],[38,128],[38,124],[42,124]]}},
  {{n:"Vietnam",pts:[[22,104],[22,107],[16,108],[10,104],[10,103],[16,105],[22,103],[22,104]]}},
  {{n:"Turkey",pts:[[42,28],[42,44],[36,44],[36,35],[38,28],[42,28]]}},
  {{n:"Nigeria",pts:[[14,3],[14,15],[6,15],[4,7],[6,3],[14,3]]}},
  {{n:"Japan",pts:[[43,143],[45,142],[44,142],[38,141],[34,135],[34,131],[38,141],[43,143]]}},
];

function drawGlobe(){{
    const r=GR();
    const atm=ctx.createRadialGradient(W/2,H/2,r*.85,W/2,H/2,r*1.18);
    atm.addColorStop(0,'rgba(0,0,0,0)');
    atm.addColorStop(.5,'rgba(180,20,20,0.05)');
    atm.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(W/2,H/2,r*1.18,0,Math.PI*2);
    ctx.fillStyle=atm; ctx.fill();

    const g=ctx.createRadialGradient(W/2-r*.22,H/2-r*.22,r*.04,W/2,H/2,r);
    g.addColorStop(0,'rgba(30,6,6,0.96)');
    g.addColorStop(.55,'rgba(14,3,4,0.98)');
    g.addColorStop(1,'rgba(6,5,8,0.99)');
    ctx.beginPath(); ctx.arc(W/2,H/2,r,0,Math.PI*2);
    ctx.fillStyle=g; ctx.fill();

    ctx.save();
    for(let lat=-80;lat<=80;lat+=15){{
        ctx.beginPath(); let f=true;
        for(let lon=-180;lon<=180;lon+=3){{
            const p=ll3d(lat,lon,r),q=proj(p.x,p.y,p.z);
            if(q.z<-r*.88){{f=true;continue;}}
            f?ctx.moveTo(q.px,q.py):ctx.lineTo(q.px,q.py); f=false;
        }}
        ctx.strokeStyle=`rgba(140,20,20,${{lat===0?.16:.05}})`;
        ctx.lineWidth=lat===0?.7:.3; ctx.stroke();
    }}
    for(let lon=-180;lon<=180;lon+=15){{
        ctx.beginPath(); let f=true;
        for(let lat=-88;lat<=88;lat+=2){{
            const p=ll3d(lat,lon,r),q=proj(p.x,p.y,p.z);
            if(q.z<-r*.88){{f=true;continue;}}
            f?ctx.moveTo(q.px,q.py):ctx.lineTo(q.px,q.py); f=false;
        }}
        ctx.strokeStyle='rgba(140,20,20,0.04)'; ctx.lineWidth=.3; ctx.stroke();
    }}

    BORDERS.forEach(b=>{{
        if(b.pts.length<2) return;
        ctx.beginPath(); let f=true;
        b.pts.forEach(([lat,lon])=>{{
            const p=ll3d(lat,lon,r+.5),q=proj(p.x,p.y,p.z);
            if(q.z<-r*.85){{f=true;return;}}
            f?ctx.moveTo(q.px,q.py):ctx.lineTo(q.px,q.py); f=false;
        }});
        ctx.strokeStyle='rgba(200,60,60,0.22)'; ctx.lineWidth=.7; ctx.stroke();
    }});
    ctx.restore();

    ctx.save(); ctx.beginPath(); ctx.arc(W/2,H/2,r,0,Math.PI*2); ctx.clip();
    THREATS.forEach(t=>{{
        const p=ll3d(t.lat,t.lon,r),q=proj(p.x,p.y,p.z);
        if(q.z<-r*.86) return;
        const vis=Math.max(0,(q.z+r)/(2*r));
        const col=t.score>=90?'255,26,26':t.score>=70?'255,102,0':t.score>=50?'255,170,0':'255,68,136';
        const sz=(3+t.score/20)*q.scale;

        if(t.score>=75){{
            const pulse=.5+.5*Math.sin(frame*.065+t.lat*.3);
            ctx.beginPath(); ctx.arc(q.px,q.py,sz*2.5+pulse*6,0,Math.PI*2);
            ctx.strokeStyle=`rgba(${{col}},${{vis*.12*pulse}})`; ctx.lineWidth=1.2; ctx.stroke();
            ctx.beginPath(); ctx.arc(q.px,q.py,sz*4+pulse*10,0,Math.PI*2);
            ctx.strokeStyle=`rgba(${{col}},${{vis*.05*pulse}})`; ctx.lineWidth=.6; ctx.stroke();
        }}

        const gw=ctx.createRadialGradient(q.px,q.py,0,q.px,q.py,sz*4);
        gw.addColorStop(0,`rgba(${{col}},${{vis*.4}})`);
        gw.addColorStop(1,'rgba(0,0,0,0)');
        ctx.beginPath(); ctx.arc(q.px,q.py,sz*4,0,Math.PI*2);
        ctx.globalAlpha=1; ctx.fillStyle=gw; ctx.fill();

        ctx.beginPath(); ctx.arc(q.px,q.py,sz,0,Math.PI*2);
        ctx.fillStyle=`rgba(${{col}},${{vis}})`; ctx.fill();

        if(q.scale>.55){{
            ctx.font=`700 ${{Math.round(7.5*q.scale)}}px Inter`;
            ctx.fillStyle=`rgba(230,150,150,${{vis*.8}})`;
            ctx.fillText(t.country.substring(0,3).toUpperCase(),q.px+sz+4,q.py+3);
        }}
    }});

    const bz=ll3d(-14.23,-51.92,r),bq=proj(bz.x,bz.y,bz.z);
    if(bq.z>-r*.86){{
        const vis=Math.max(0,(bq.z+r)/(2*r));
        [10,18,28].forEach((sr,i)=>{{
            const pulse=.5+.5*Math.sin(frame*.05+i*2.1);
            ctx.beginPath(); ctx.arc(bq.px,bq.py,(sr+pulse*4)*bq.scale,0,Math.PI*2);
            ctx.strokeStyle=`rgba(0,255,136,${{vis*(.22-i*.06)}})`;
            ctx.lineWidth=1.2; ctx.stroke();
        }});
        ctx.beginPath(); ctx.arc(bq.px,bq.py,6.5*bq.scale,0,Math.PI*2);
        ctx.fillStyle=`rgba(0,255,136,${{vis}})`; ctx.fill();
        if(bq.scale>.55){{
            ctx.font=`700 ${{Math.round(8.5*bq.scale)}}px Inter`;
            ctx.fillStyle=`rgba(0,255,136,${{vis*.9}})`; ctx.fillText('BRA',bq.px+9*bq.scale,bq.py+3);
        }}
    }}
    ctx.restore();

    const rim=ctx.createRadialGradient(W/2,H/2,r*.92,W/2,H/2,r*1.06);
    rim.addColorStop(0,'rgba(180,30,30,0)');
    rim.addColorStop(.5,'rgba(180,30,30,0.07)');
    rim.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath(); ctx.arc(W/2,H/2,r*1.06,0,Math.PI*2);
    ctx.fillStyle=rim; ctx.fill();
}}

class Missile{{
    constructor(arc){{
        this.arc=arc; this.t=0; this.spd=0.0025+Math.random()*.004;
        this.trail=[]; this.maxTrail=32; this.dead=false; this.impactFrame=0;
        const th=TMAP[arc.name];
        if(th){{this.col=th.score>=90?[255,26,26]:th.score>=70?[255,102,0]:th.score>=50?[255,170,0]:[255,68,136];}}
        else{{this.col=[220,100,50];}}
        const r=GR();
        const s=ll3d(arc.slat,arc.slon,r);
        const d=ll3d(arc.dlat,arc.dlon,r);
        const dist=Math.hypot(s.x-d.x,s.y-d.y,s.z-d.z);
        this.arcH=dist*.38;
    }}
    bezier(t){{
        const r=GR();
        const s=ll3d(this.arc.slat,this.arc.slon,r);
        const d=ll3d(this.arc.dlat,this.arc.dlon,r);
        const mx=(s.x+d.x)/2, my=(s.y+d.y)/2, mz=(s.z+d.z)/2;
        const len=Math.sqrt(mx*mx+my*my+mz*mz)||1;
        const cx=mx+mx/len*this.arcH, cy=my+my/len*this.arcH, cz=mz+mz/len*this.arcH;
        const u=1-t;
        return {{x:u*u*s.x+2*u*t*cx+t*t*d.x, y:u*u*s.y+2*u*t*cy+t*t*d.y, z:u*u*s.z+2*u*t*cz+t*t*d.z}};
    }}
    update(){{
        if(this.dead) return false;
        this.t=Math.min(this.t+this.spd,1);
        const p=this.bezier(this.t), q=proj(p.x,p.y,p.z);
        this.trail.push({{px:q.px,py:q.py,z:q.z,scale:q.scale}});
        if(this.trail.length>this.maxTrail) this.trail.shift();
        if(this.t>=1){{this.impactFrame++; if(this.impactFrame>18) this.dead=true;}}
        return true;
    }}
    draw(){{
        const r=GR();
        if(this.trail.length<2) return;
        const [cr,cg,cb]=this.col;
        for(let i=1;i<this.trail.length;i++){{
            const a=i/this.trail.length, tp=this.trail[i], pp=this.trail[i-1];
            if(tp.z<-r*.88) continue;
            const vis=Math.max(0,(tp.z+r)/(2*r));
            ctx.beginPath(); ctx.moveTo(pp.px,pp.py); ctx.lineTo(tp.px,tp.py);
            ctx.strokeStyle=`rgba(${{cr}},${{cg}},${{cb}},${{a*vis*.95}})`; ctx.lineWidth=a*2.2; ctx.stroke();
        }}
        const last=this.trail[this.trail.length-1];
        if(last && last.z>-r*.88){{
            const vis=Math.max(0,(last.z+r)/(2*r));
            const gw=ctx.createRadialGradient(last.px,last.py,0,last.px,last.py,8*last.scale);
            gw.addColorStop(0,`rgba(${{cr}},${{cg}},${{cb}},${{vis*.9}})`);
            gw.addColorStop(1,'rgba(0,0,0,0)');
            ctx.beginPath(); ctx.arc(last.px,last.py,8*last.scale,0,Math.PI*2); ctx.fillStyle=gw; ctx.fill();
            ctx.beginPath(); ctx.arc(last.px,last.py,2.5*last.scale,0,Math.PI*2);
            ctx.fillStyle=`rgba(255,255,255,${{vis}})`; ctx.fill();
            if(this.t>=1){{
                const prog=this.impactFrame/18, rad=(12+prog*30)*last.scale;
                ctx.beginPath(); ctx.arc(last.px,last.py,rad,0,Math.PI*2);
                ctx.strokeStyle=`rgba(${{cr}},${{cg}},${{cb}},${{(1-prog)*.6}})`; ctx.lineWidth=2; ctx.stroke();
                ctx.beginPath(); ctx.arc(last.px,last.py,rad*.5,0,Math.PI*2);
                ctx.strokeStyle=`rgba(${{cr}},${{cg}},${{cb}},${{(1-prog)*.35}})`; ctx.lineWidth=1; ctx.stroke();
            }}
        }}
    }}
}}

let missiles=[];
function spawnMissiles(){{
    ARCS.forEach(arc=>{{ if(Math.random()<.055) missiles.push(new Missile(arc)); }});
}}

const FEED_MSGS=[
    "APT28 tentativa SSH bloqueada · RU","Flood DDoS mitigado 48Gbps · CN",
    "Brute force detectado · KP","SQL Injection bloqueado · RU",
    "Ransomware signature detectada · UA","C2 callback bloqueado · IR",
    "Phishing domain takedown · NG","Credential stuffing · KP",
    "Port scan massivo · CN","Zero-day exploit bloqueado · RU",
    "BEC attack interceptado · NG","DNS hijack attempt · TR",
    "Mimikatz detectado em memória · RU","Cobalt Strike beacon · CN",
    "Lazarus waterhole attack · KP","MuddyWater backdoor · IR",
];
let feedItems=[];
function addFeed(){{
    const t=new Date().toLocaleTimeString('pt-BR',{{hour:'2-digit',minute:'2-digit',second:'2-digit'}});
    feedItems.unshift('['+t+'] '+FEED_MSGS[Math.floor(Math.random()*FEED_MSGS.length)]);
    if(feedItems.length>6) feedItems.pop();
    document.getElementById('feed-list').innerHTML=
        feedItems.map((f,i)=>'<div class="feed-item '+(i===0?'new':'')+'" >'+f+'</div>').join('');
}}
addFeed(); setInterval(addFeed,2800);

function animate(){{
    requestAnimationFrame(animate);
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#060508'; ctx.fillRect(0,0,W,H);
    stars.forEach(s=>{{
        ctx.beginPath(); ctx.arc(s.x%W,s.y%H,s.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(255,200,200,${{s.a*(.6+.4*Math.sin(frame*.018+s.x))}})`; ctx.fill();
    }});
    if(!isDrag) rotY+=.0018;
    frame++;
    drawGlobe();
    if(frame%9===0) spawnMissiles();
    missiles=missiles.filter(m=>{{
        const alive=m.update(); m.draw();
        if(m.dead){{
            totalAtk++; totalBlk=Math.floor(totalAtk*.73);
            document.getElementById('atk-val').textContent=totalAtk.toLocaleString();
            document.getElementById('blk-val').textContent=totalBlk.toLocaleString();
        }}
        return !m.dead;
    }});
}}

C.addEventListener('mousedown',e=>{{isDrag=true;lastX=e.clientX;lastY=e.clientY;C.classList.add('dragging');}});
window.addEventListener('mouseup',()=>{{isDrag=false;C.classList.remove('dragging');}});
window.addEventListener('mousemove',e=>{{
    if(!isDrag) return;
    rotY+=(e.clientX-lastX)*.005; rotX+=(e.clientY-lastY)*.003;
    rotX=Math.max(-.8,Math.min(.8,rotX)); lastX=e.clientX; lastY=e.clientY;
}});
C.addEventListener('wheel',e=>{{
    e.preventDefault();
    zoom=Math.max(.5,Math.min(2.5,zoom-e.deltaY*.001));
}},{{passive:false}});

let ltx=0,lty=0,ldist=0;
C.addEventListener('touchstart',e=>{{e.preventDefault();ltx=e.touches[0].clientX;lty=e.touches[0].clientY;if(e.touches.length===2)ldist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);}},{{passive:false}});
C.addEventListener('touchmove',e=>{{
    e.preventDefault();
    if(e.touches.length===1){{rotY+=(e.touches[0].clientX-ltx)*.005;rotX+=(e.touches[0].clientY-lty)*.003;rotX=Math.max(-.8,Math.min(.8,rotX));ltx=e.touches[0].clientX;lty=e.touches[0].clientY;}}
    else if(e.touches.length===2){{const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);zoom=Math.max(.5,Math.min(2.5,zoom*(d/ldist)));ldist=d;}}
}},{{passive:false}});

C.addEventListener('click',e=>{{
    const rect=C.getBoundingClientRect();
    const mx=e.clientX-rect.left, my=e.clientY-rect.top;
    const r=GR(); let found=null;
    THREATS.forEach(t=>{{
        const p=ll3d(t.lat,t.lon,r),q=proj(p.x,p.y,p.z);
        if(q.z>-r*.8 && Math.hypot(mx-q.px,my-q.py)<22) found=t;
    }});
    if(found){{
        document.getElementById('ip-name').textContent=found.country;
        document.getElementById('ip-score').textContent='Threat Score: '+found.score+'/100';
        document.getElementById('ip-target').textContent='Alvos: '+found.target;
        document.getElementById('ip-groups').textContent='Grupos APT: '+found.groups.join(' · ');
        document.getElementById('ip-bar').style.width=found.score+'%';
        document.getElementById('info-panel').style.display='block';
    }}
}});

animate();
</script>
</body>
</html>"""

    components.html(globe_html, height=640, scrolling=False)

    st.markdown("### Threat Intelligence — Países de Alto Risco")
    threat_df = pd.DataFrame([{
        "País":t["country"],"Threat Score":t["score"],
        "Grupos APT":", ".join(t["groups"]),"Alvos Primários":t["target"]
    } for t in sorted(THREAT_INTEL, key=lambda x: -x["score"])])
    st.dataframe(threat_df, use_container_width=True, hide_index=True)

    if not cc.empty:
        st.markdown("### Ataques por País — Dataset Atual")
        ta = cc.copy(); ta.columns = ["País","Ataques"]
        ta["% do Total"] = (ta["Ataques"]/ta["Ataques"].sum()*100).round(1).astype(str)+"%"
        st.dataframe(ta, use_container_width=True, hide_index=True)

# ─── TAB 3: SENTINEL BOT ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### Sentinel Bot — Assistente de Segurança")
    st.caption("IA especialista em cibersegurança com acesso aos dados do sistema em tempo real.")

    top_cli = df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top_pai = df[df["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    SYSTEM_BOT = f"""Você é o Sentinel Bot, assistente especialista em segurança cibernética da plataforma SentinelAI.
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
Escopo: {"Todos os clientes" if not CLT else CLT}"""

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat"]:
            css = "chat-user" if msg["role"]=="user" else "chat-ai"
            label = "Você" if msg["role"]=="user" else "Sentinel Bot"
            st.markdown(f'<div class="{css}"><strong style="font-size:0.68rem;opacity:0.6;">{label}</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)
        if not st.session_state["chat"]:
            st.markdown("""<div class="chat-ai">
            <strong style="font-size:0.68rem;opacity:0.6;">Sentinel Bot</strong><br>
            Olá! Sou o assistente de segurança da SentinelAI. Analiso incidentes, identifico padrões de ameaças e recomendo ações de mitigação.<br><br>Como posso ajudar?
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#4b5563;font-size:0.7rem;margin-bottom:0.8rem;font-weight:600;'>PERGUNTAS RÁPIDAS</p>", unsafe_allow_html=True)

    sugs = [
        "Qual cliente tem mais prejuízo?",
        "Quais países mais atacaram?",
        "Status dos incidentes críticos",
        "Recomendações urgentes",
        "Como funciona o modelo IA?",
        "Explique os grupos APT"
    ]

    col1, col2 = st.columns(2)
    with col1:
        if st.button(sugs[0], key="sg0", use_container_width=True): sug_click = sugs[0]
    with col2:
        if st.button(sugs[1], key="sg1", use_container_width=True): sug_click = sugs[1]
    col3, col4 = st.columns(2)
    with col3:
        if st.button(sugs[2], key="sg2", use_container_width=True): sug_click = sugs[2]
    with col4:
        if st.button(sugs[3], key="sg3", use_container_width=True): sug_click = sugs[3]
    col5, col6 = st.columns(2)
    with col5:
        if st.button(sugs[4], key="sg4", use_container_width=True): sug_click = sugs[4]
    with col6:
        if st.button(sugs[5], key="sg5", use_container_width=True): sug_click = sugs[5]

    st.markdown("---")
    with st.form("chat_f", clear_on_submit=True):
        col_input, col_button = st.columns([5,1])
        with col_input:
            q = st.text_input("", placeholder="Digite sua pergunta sobre segurança...", label_visibility="collapsed")
        with col_button:
            send = st.form_submit_button("Enviar", use_container_width=True)

    sug_click = None
    for i in range(6):
        if f"sg{i}" in st.session_state and st.session_state[f"sg{i}"]:
            sug_click = sugs[i]

    if sug_click:
        q = sug_click
        send = True

    if send and q:
        log(USER,"CHAT",q[:80])
        st.session_state["chat"].append({"role":"user","content":q})
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="color:#6b7280;font-size:0.7rem;margin-left:8px;">Sentinel Bot está digitando...</span>
        </div>""", unsafe_allow_html=True)
        msgs = st.session_state["chat"].copy()
        resp = gemini_chat(SYSTEM_BOT, msgs)
        typing_placeholder.empty()
        st.session_state["chat"].append({"role":"assistant","content":resp})
        db_salvar_chat(USER,q,resp)
        st.rerun()

    if st.session_state["chat"]:
        col_clear, _ = st.columns([1,5])
        with col_clear:
            if st.button("Limpar conversa", key="clear_chat", use_container_width=True):
                st.session_state["chat"] = []
                st.rerun()

# ─── TAB 4: SUPORTE ───────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("### Suporte ao Cliente — Canal Direto com a SentinelAI")

    is_client = bool(CLT)
    is_support_adm = PROF["support_admin"]

    SUPPORT_SYS = f"""Você é o agente de suporte da SentinelAI, empresa brasileira de cibersegurança.
Responda em português, de forma cordial, profissional e objetiva.
Cliente: {CLT or 'Equipe interna'}
Dados: {len(df)} incidentes · Acurácia IA {ACC:.1%} · Prejuízo R$ {prej:,.0f}
Nunca revele dados de outros clientes."""

    if is_client:
        st.markdown(f'<div class="info-box-blue">Bem-vindo ao suporte, <strong>{CLT}</strong>. Use o chat para dúvidas rápidas ou abra um ticket formal.</div>', unsafe_allow_html=True)

        ctabs = st.tabs(["Chat Suporte","Meus Tickets","Novo Ticket"])

        with ctabs[0]:
            st.markdown("#### Chat com Suporte SentinelAI")
            if not st.session_state["chat_suporte"]:
                st.markdown(f"""<div class="chat-support">
                <strong style="font-size:0.68rem;opacity:0.7;">Suporte SentinelAI</strong><br>
                Olá, {CLT}! Como posso ajudar hoje?</div>""", unsafe_allow_html=True)
            for msg in st.session_state["chat_suporte"]:
                css = "chat-user" if msg["role"]=="user" else "chat-support"
                label = CLT if msg["role"]=="user" else "Suporte SentinelAI"
                st.markdown(f'<div class="{css}"><strong style="font-size:0.68rem;opacity:0.6;">{label}</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

            sup_sugs = [f"Status incidentes {CLT}","Como interpretar threat score?","O que fazer em caso de ataque?","Como exportar relatórios?"]
            sc = st.columns(len(sup_sugs))
            sup_click = None
            for i, s in enumerate(sup_sugs):
                with sc[i]:
                    if st.button(s, key=f"sup_sg{i}", use_container_width=True):
                        sup_click = s

            with st.form("chat_sup_f", clear_on_submit=True):
                si, sb = st.columns([5,1])
                with si:
                    sq = st.text_input("", placeholder="Mensagem para o suporte...", label_visibility="collapsed")
                with sb:
                    ssend = st.form_submit_button("Enviar", use_container_width=True)

            if sup_click: sq = sup_click; ssend = True

            if ssend and sq:
                log(USER,"SUPORTE_CHAT",sq[:80])
                st.session_state["chat_suporte"].append({"role":"user","content":sq})
                typing_ph = st.empty()
                typing_ph.markdown("""<div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>""", unsafe_allow_html=True)
                sup_resp = gemini_chat(SUPPORT_SYS, st.session_state["chat_suporte"].copy(), temperature=0.6, max_tokens=800)
                typing_ph.empty()
                st.session_state["chat_suporte"].append({"role":"assistant","content":sup_resp})
                st.rerun()

            if st.session_state["chat_suporte"]:
                if st.button("Limpar chat", key="clear_sup"):
                    st.session_state["chat_suporte"] = []
                    st.rerun()

        with ctabs[1]:
            st.markdown("#### Meus Tickets")
            tks_cli = db_buscar_tickets(CLT)
            if tks_cli.empty:
                st.info("Nenhum ticket ainda. Abra um na aba 'Novo Ticket'.")
            else:
                for _, row in tks_cli.iterrows():
                    sc_color = {"aberto":"#dc2626","respondido":"#4ade80","fechado":"#6b7280"}.get(row["status"],"#f59e0b")
                    pri_label = {"urgente":"URGENTE","alta":"ALTA","normal":"NORMAL","baixa":"BAIXA"}.get(row["prioridade"],"NORMAL")
                    st.markdown(f"""<div class="ticket-card">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <span style="color:white;font-weight:700;font-size:0.82rem;">#{row['id']} — {row['assunto']}</span>
                        <div>
                          <span style="color:#6b7280;font-size:0.65rem;margin-right:8px;">{pri_label}</span>
                          <span style="color:{sc_color};font-size:0.7rem;font-weight:700;">{row['status'].upper()}</span>
                        </div>
                      </div>
                      <p style="color:#6b7280;font-size:0.7rem;">{row['ts']}</p>
                    </div>""", unsafe_allow_html=True)
                    with st.expander(f"Ver ticket #{row['id']}"):
                        chat_t = db_buscar_chat_ticket(int(row["id"]))
                        if not chat_t.empty:
                            for _, m in chat_t.iterrows():
                                is_me = m["remetente"] == CLT
                                st.markdown(f'<div class="{"chat-user" if is_me else "chat-support"}"><strong style="font-size:0.68rem;opacity:0.6;">{m["remetente"]}</strong> · {m["ts"]}<br>{m["mensagem"]}</div>', unsafe_allow_html=True)
                        if row["status"] != "fechado":
                            with st.form(f"reply_{row['id']}"):
                                rm = st.text_area("Adicionar mensagem", key=f"rm_{row['id']}", height=70)
                                cr1, cr2 = st.columns(2)
                                with cr1:
                                    if st.form_submit_button("Enviar mensagem", use_container_width=True):
                                        if rm.strip():
                                            db_adicionar_msg_ticket(int(row["id"]),CLT,rm.strip())
                                            log(USER,"TICKET_MSG",f"#{row['id']}"); st.rerun()
                                with cr2:
                                    if st.form_submit_button("Fechar ticket", use_container_width=True):
                                        db_responder_ticket(int(row["id"]),"Fechado pelo cliente.","fechado")
                                        log(USER,"TICKET_FECHADO",f"#{row['id']}"); st.rerun()

        with ctabs[2]:
            st.markdown("#### Abrir Novo Ticket")
            with st.form("novo_ticket"):
                assunto = st.text_input("Assunto*", placeholder="Ex: Alerta não reconhecido")
                prioridade = st.selectbox("Prioridade", ["normal","alta","urgente","baixa"])
                mensagem = st.text_area("Descrição*", height=110, placeholder="Descreva o problema, quando ocorreu e o impacto...")
                submitted = st.form_submit_button("Abrir Ticket", use_container_width=True)
            if submitted:
                if assunto.strip() and mensagem.strip():
                    tid = db_criar_ticket(CLT,assunto.strip(),mensagem.strip(),prioridade)
                    if tid:
                        log(USER,"TICKET_CRIADO",f"id={tid}")
                        st.success(f"Ticket #{tid} criado com sucesso.")
                        auto = gemini_chat(SUPPORT_SYS,[{"role":"user","content":f"Cliente {CLT} abriu ticket: '{assunto}'. Mensagem: {mensagem}. Responda confirmando recebimento e com orientações iniciais."}],temperature=0.5,max_tokens=400)
                        db_adicionar_msg_ticket(tid,"SentinelAI",auto)
                        st.rerun()
                    else: st.error("Erro ao criar ticket.")
                else: st.warning("Preencha todos os campos.")

    elif is_support_adm:
        st.markdown('<div class="info-box">Painel Administrativo de Suporte — Gerencie todos os tickets dos clientes.</div>', unsafe_allow_html=True)
        all_tks = db_buscar_tickets()
        if all_tks.empty:
            st.info("Nenhum ticket registrado.")
        else:
            n_ab=len(all_tks[all_tks["status"]=="aberto"])
            n_re=len(all_tks[all_tks["status"]=="respondido"])
            n_fe=len(all_tks[all_tks["status"]=="fechado"])
            ma1,ma2,ma3 = st.columns(3)
            with ma1: st.metric("Abertos",n_ab)
            with ma2: st.metric("Respondidos",n_re)
            with ma3: st.metric("Fechados",n_fe)
            filtro = st.selectbox("Filtrar",["todos","aberto","respondido","fechado"])
            tks_f = all_tks if filtro=="todos" else all_tks[all_tks["status"]==filtro]
            for _,row in tks_f.iterrows():
                pri_label = {"urgente":"[URGENTE]","alta":"[ALTA]","normal":"[NORMAL]","baixa":"[BAIXA]"}.get(row["prioridade"],"")
                with st.expander(f"{pri_label} #{row['id']} [{row['cliente']}] {row['assunto']} — {row['status'].upper()}"):
                    chat_t = db_buscar_chat_ticket(int(row["id"]))
                    if not chat_t.empty:
                        for _,m in chat_t.iterrows():
                            is_sen = m["remetente"]=="SentinelAI"
                            st.markdown(f'<div class="{"chat-support" if is_sen else "chat-user"}"><strong style="font-size:0.68rem;opacity:0.6;">{m["remetente"]}</strong> · {m["ts"]}<br>{m["mensagem"]}</div>', unsafe_allow_html=True)
                    if row["status"]!="fechado":
                        if st.button(f"Gerar sugestão IA — #{row['id']}",key=f"ia_{row['id']}",use_container_width=True):
                            sugestao = gemini_chat(SUPPORT_SYS,[{"role":"user","content":f"Analista responde ticket do cliente {row['cliente']}. Assunto: '{row['assunto']}'. Mensagem: '{row['mensagem']}'. Gere resposta profissional."}],temperature=0.5,max_tokens=400)
                            st.info(f"Sugestão gerada:\n\n{sugestao}")
                        with st.form(f"adm_{row['id']}"):
                            resp_adm = st.text_area("Resposta",height=80,key=f"ra_{row['id']}")
                            ca1,ca2,ca3 = st.columns(3)
                            with ca1:
                                if st.form_submit_button("Responder",use_container_width=True):
                                    if resp_adm.strip():
                                        db_responder_ticket(int(row["id"]),resp_adm.strip(),"respondido")
                                        log(USER,"TICKET_RESP",f"#{row['id']}"); st.rerun()
                            with ca2:
                                if st.form_submit_button("Fechar",use_container_width=True):
                                    db_responder_ticket(int(row["id"]),resp_adm.strip() or "Resolvido.","fechado")
                                    log(USER,"TICKET_FECH",f"#{row['id']}"); st.rerun()
                            with ca3:
                                if st.form_submit_button("Escalar urgente",use_container_width=True):
                                    db_adicionar_msg_ticket(int(row["id"]),USER,"ESCALADO como URGENTE pelo SOC.")
                                    log(USER,"TICKET_ESC",f"#{row['id']}"); st.rerun()
    else:
        st.markdown('<div class="info-box">Sem acesso ao módulo de suporte.</div>', unsafe_allow_html=True)

# ─── TAB 5: BACKUP ───────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown("### Backup e Gerenciamento de Dados")
    st.markdown("""
    <div class="info-box">
      <strong>Onde os dados são armazenados:</strong><br><br>
      <strong style="color:#f87171;">SQLite (atual — sentinelai_backup.db):</strong><br>
      Arquivo local no servidor Streamlit Cloud. Persiste entre sessões normais,
      mas reseta ao fazer redeploy.<br><br>
      <strong style="color:#60a5fa;">MySQL (produção — persistência total):</strong><br>
      Configure <code>MYSQL_URL</code> nos Secrets do Streamlit.
      Serviços gratuitos: PlanetScale, Railway, Aiven.<br><br>
      <strong style="color:#4ade80;">Exportação manual:</strong> use os botões abaixo a qualquer momento.
    </div>""", unsafe_allow_html=True)

    with st.expander("Como configurar MySQL (PlanetScale / Railway)"):
        st.code("""# 1. PlanetScale (planetscale.com) — crie banco 'sentinelai'
# 2. Copie a connection string
# 3. Streamlit Cloud > Settings > Secrets:
MYSQL_URL = "mysql://user:senha@host/sentinelai" """, language="bash")

    db_ok = os.path.exists(DB_PATH)
    db_size = round(os.path.getsize(DB_PATH)/1024,1) if db_ok else 0
    b1,b2,b3,b4 = st.columns(4)
    with b1:
        st.markdown(f"""<div style="background:rgba(0,180,80,0.06);border:1px solid rgba(0,180,80,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">SQLite Status</p>
          <p style="color:#4ade80;font-size:1rem;font-weight:700;">ATIVO</p>
          <p style="color:#6b7280;font-size:0.7rem;">{db_size} KB</p>
        </div>""", unsafe_allow_html=True)
    with b2:
        n_inc = len(db_buscar_incidentes())
        st.markdown(f"""<div style="background:rgba(139,0,0,0.06);border:1px solid rgba(180,0,0,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Incidentes Salvos</p>
          <p style="color:#dc2626;font-size:1rem;font-weight:700;">{n_inc}</p>
        </div>""", unsafe_allow_html=True)
    with b3:
        n_tks_db = len(db_buscar_tickets())
        st.markdown(f"""<div style="background:rgba(0,100,200,0.06);border:1px solid rgba(0,150,255,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Tickets Suporte</p>
          <p style="color:#60a5fa;font-size:1rem;font-weight:700;">{n_tks_db}</p>
        </div>""", unsafe_allow_html=True)
    with b4:
        n_logs_db = len(db_buscar_logs())
        st.markdown(f"""<div style="background:rgba(100,50,0,0.06);border:1px solid rgba(180,100,0,0.2);border-radius:12px;padding:1rem;text-align:center;">
          <p style="color:#4b5563;font-size:0.6rem;text-transform:uppercase;">Logs Auditoria</p>
          <p style="color:#f59e0b;font-size:1rem;font-weight:700;">{n_logs_db}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Exportar Dados")
    if not PROF["export"]:
        st.error("Apenas Administradores podem exportar dados.")
    else:
        ts_exp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        e1,e2,e3,e4,e5 = st.columns(5)
        with e1:
            st.download_button("Dataset Completo", df_all.to_csv(index=False).encode(), f"sentinel_full_{ts_exp}.csv","text/csv",use_container_width=True)
        with e2:
            df_anon = df_all.drop(columns=["IP_SUSPEITO"],errors="ignore")
            st.download_button("Anonimizado", df_anon.to_csv(index=False).encode(), f"sentinel_anon_{ts_exp}.csv","text/csv",use_container_width=True)
        with e3:
            df_inc_exp = db_buscar_incidentes()
            if not df_inc_exp.empty:
                st.download_button("Incidentes DB", df_inc_exp.to_csv(index=False).encode(), f"sentinel_db_{ts_exp}.csv","text/csv",use_container_width=True)
        with e4:
            df_tks_exp = db_buscar_tickets()
            if not df_tks_exp.empty:
                st.download_button("Tickets", df_tks_exp.to_csv(index=False).encode(), f"sentinel_tickets_{ts_exp}.csv","text/csv",use_container_width=True)
        with e5:
            if st.session_state.get("logs"):
                st.download_button("Logs Sessão", "\n".join(st.session_state["logs"]).encode(), f"sentinel_logs_{ts_exp}.txt","text/plain",use_container_width=True)
        db_meta_backup(USER,"EXPORT_FULL",len(df_all))

    st.markdown("### Incidentes no Banco")
    df_db_view = db_buscar_incidentes()
    if not df_db_view.empty:
        st.dataframe(df_db_view,use_container_width=True,height=220)
    else:
        st.info("Nenhum incidente registrado. Use a aba Análise para gerar registros.")

    st.markdown("### Prévia — Dataset Principal")
    st.dataframe(df.head(20),use_container_width=True,height=200)
    st.caption(f"{len(df)} registros · {len(df.columns)} colunas")

# ─── TAB 6: AUDITORIA ────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("### Logs de Auditoria — Rastreabilidade Completa")
    st.caption("Todas as ações registradas com timestamp · Conformidade LGPD e ISO 27001")
    df_logs = db_buscar_logs()
    if not df_logs.empty:
        al1,al2,al3 = st.columns(3)
        with al1: st.metric("Total Eventos",len(df_logs))
        with al2: st.metric("Usuários Ativos",df_logs["usuario"].nunique())
        with al3: st.metric("Ações Distintas",df_logs["acao"].nunique())
        st.dataframe(df_logs,use_container_width=True,height=380)
        if PROF["export"]:
            ts_aud = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("Exportar Auditoria",df_logs.to_csv(index=False).encode(),f"auditoria_{ts_aud}.csv","text/csv")
    else:
        st.info("Nenhum log ainda.")
    st.markdown("### Logs da Sessão Atual")
    if st.session_state.get("logs"):
        for l in reversed(st.session_state["logs"][-40:]):
            st.code(l, language=None)
    else:
        st.info("Nenhum log nesta sessão.")
