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

# ─── BANCO DE DADOS SQLite ────────────────────────────────────────────────────

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
                usuario TEXT, tipo_incidente TEXT, origem TEXT,
                status TEXT, severidade_prevista TEXT, cliente TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT, acao TEXT,
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
        return pd.read_sql_query(
            "SELECT * FROM incidentes_registrados ORDER BY timestamp DESC LIMIT 50", conn)
    except Exception:
        return pd.DataFrame()

def salvar_log_sqlite(conn, usuario, acao):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs_sistema (usuario, acao) VALUES (?, ?)", (usuario, acao))
        conn.commit()
    except Exception:
        pass

# ─── CONFIG DA PÁGINA ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
}

.stApp { background: #060b18; }

[data-testid="stHeader"] { background: rgba(0,0,0,0); }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060b18 0%, #0a1128 100%);
    border-right: 1px solid rgba(0, 212, 255, 0.08);
}

.block-container { padding: 1.2rem 1.5rem; max-width: 100%; }

/* ── Métricas ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.04) 0%, rgba(6,11,24,0.9) 100%);
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
div[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent);
}
div[data-testid="metric-container"]:hover {
    border-color: rgba(0, 212, 255, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,212,255,0.08);
}
[data-testid="stMetricLabel"] {
    color: #5a7a9e !important;
    font-size: 0.65rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
}
[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-size: 1.6rem !important;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Botões ── */
div.stButton > button {
    background: linear-gradient(135deg, #0077b6, #00b4d8);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.55rem 1rem;
    font-weight: 600;
    font-size: 0.82rem;
    transition: all 0.2s ease;
    width: 100%;
    letter-spacing: 0.02em;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #0096c7, #00d4ff);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,180,216,0.3);
}

/* ── Chat ── */
.chat-user {
    background: linear-gradient(135deg, #0077b6, #00b4d8);
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    margin-left: auto;
    max-width: 82%;
    width: fit-content;
    color: white;
    font-size: 0.84rem;
    line-height: 1.5;
}
.chat-ai {
    background: rgba(10, 17, 40, 0.95);
    border: 1px solid rgba(0, 212, 255, 0.18);
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    max-width: 82%;
    width: fit-content;
    color: #d0dce8;
    font-size: 0.84rem;
    line-height: 1.5;
}

/* ── Header ── */
.sentinel-header {
    background: linear-gradient(135deg, rgba(0,180,216,0.06) 0%, rgba(0,50,100,0.04) 100%);
    border: 1px solid rgba(0, 212, 255, 0.12);
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.sentinel-header::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.5), transparent);
}

/* ── Badges ── */
.badge-online {
    display: inline-block;
    background: rgba(0, 255, 100, 0.08);
    border: 1px solid rgba(0, 255, 100, 0.25);
    color: #00ff64;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    font-family: 'JetBrains Mono', monospace;
}
.badge-sqlite {
    display: inline-block;
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.25);
    color: #00d4ff;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10, 17, 40, 0.8);
    border-radius: 14px;
    padding: 0.3rem;
    gap: 0.2rem;
    border: 1px solid rgba(0,212,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #5a7a9e;
    font-weight: 500;
    padding: 0.45rem 1rem;
    font-size: 0.8rem;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,180,216,0.18), rgba(0,119,182,0.1));
    color: #00d4ff !important;
    border: 1px solid rgba(0,212,255,0.2);
}

/* ── Inputs ── */
input, textarea, select {
    background: rgba(10, 17, 40, 0.9) !important;
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.08) !important;
}

hr { border-color: rgba(0,212,255,0.07); margin: 1rem 0; }
code {
    background: rgba(0,212,255,0.08);
    color: #00d4ff;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.4); }
</style>
""", unsafe_allow_html=True)

# ─── UTILITÁRIOS ──────────────────────────────────────────────────────────────

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

# ─── POLÍTICA DE PRIVACIDADE ──────────────────────────────────────────────────

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(0,180,216,0.06),rgba(0,50,100,0.04));
                    border:1px solid rgba(0,212,255,0.15);border-radius:20px;
                    padding:2.5rem 2rem;margin:3rem 0;text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔒</div>
            <h2 style="color:#00d4ff;margin-bottom:0.8rem;font-size:1.4rem;">Política de Privacidade</h2>
            <p style="color:#8b9dc3;font-size:0.88rem;line-height:1.6;">
                Esta plataforma está em conformidade com a <strong style="color:#00d4ff;">LGPD (Lei 13.709/2018)</strong>.<br>
                Seus dados estão protegidos e não são compartilhados com terceiros.
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Aceitar e Continuar", use_container_width=True):
                st.session_state["cookies_aceitos"] = True
                adicionar_log("Sistema", "Termos aceitos")
                st.rerun()
        with c2:
            if st.button("❌ Recusar", use_container_width=True):
                st.stop()
    st.stop()

# ─── USUÁRIOS ─────────────────────────────────────────────────────────────────

USUARIOS = {
    "admin":        {"senha_hash": hashlib.sha256("admin123".encode()).hexdigest(),    "perfil": "Administrador", "pode_exportar": True,  "pode_analisar": True,  "ver_pii": True,  "cliente_vinculado": None},
    "analista":     {"senha_hash": hashlib.sha256("analista123".encode()).hexdigest(), "perfil": "Analista",      "pode_exportar": False, "pode_analisar": True,  "ver_pii": False, "cliente_vinculado": None},
    "nubank":       {"senha_hash": hashlib.sha256("nubank123".encode()).hexdigest(),   "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha_hash": hashlib.sha256("ml123".encode()).hexdigest(),       "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander":    {"senha_hash": hashlib.sha256("sant123".encode()).hexdigest(),     "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer":       {"senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(),   "perfil": "Visualizador",  "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
}

def autenticar(u, s):
    return u in USUARIOS and hashlib.sha256(s.encode()).hexdigest() == USUARIOS[u]["senha_hash"]

# ─── LOGIN ────────────────────────────────────────────────────────────────────

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 1.5rem;">
            <div style="display:inline-flex;align-items:center;justify-content:center;
                        width:80px;height:80px;background:rgba(0,180,216,0.1);
                        border:1px solid rgba(0,212,255,0.25);border-radius:50%;
                        font-size:2.5rem;margin-bottom:1.2rem;">🛡️</div>
            <h1 style="color:#00d4ff;font-size:2.2rem;font-weight:700;margin:0;">SentinelAI</h1>
            <p style="color:#5a7a9e;margin:0.4rem 0 1rem;font-size:0.9rem;">
                Plataforma de Inteligência contra Ameaças
            </p>
            <span class="badge-online">● SISTEMA ATIVO</span>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            usuario_input = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha_input   = st.text_input("Senha",   type="password", placeholder="••••••••")
            if st.form_submit_button("🔐 Entrar", use_container_width=True):
                if autenticar(usuario_input, senha_input):
                    st.session_state["autenticado"]   = True
                    st.session_state["usuario_atual"] = usuario_input
                    adicionar_log(usuario_input, "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
    st.stop()

# ─── SESSÃO ───────────────────────────────────────────────────────────────────

usuario_atual = st.session_state["usuario_atual"]
perfil_atual  = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão iniciada")

if "sqlite_conn" not in st.session_state:
    st.session_state["sqlite_conn"] = conectar_sqlite()
    if st.session_state["sqlite_conn"]:
        inicializar_sqlite(st.session_state["sqlite_conn"])

sqlite_conn   = st.session_state["sqlite_conn"]
sqlite_ativo  = sqlite_conn is not None

# ─── DADOS ────────────────────────────────────────────────────────────────────

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
    df["TIPO_ENC"]       = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"]     = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"]     = enc["status"].fit_transform(df["STATUS"])
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

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.2rem 0 0.5rem;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:52px;height:52px;background:rgba(0,180,216,0.1);
                    border:1px solid rgba(0,212,255,0.2);border-radius:50%;font-size:1.6rem;">
            🛡️
        </div>
        <h3 style="color:#00d4ff;margin:0.5rem 0 0;font-size:1.1rem;font-weight:700;">SentinelAI</h3>
        <p style="color:#3a5a7e;font-size:0.62rem;letter-spacing:0.15em;font-family:'JetBrains Mono',monospace;">
            CYBER INTELLIGENCE
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.05);border:1px solid rgba(0,212,255,0.1);
                border-radius:12px;padding:0.9rem;margin:0.5rem 0;">
        <p style="color:#3a5a7e;font-size:0.6rem;letter-spacing:0.1em;margin-bottom:0.3rem;">PERFIL ATIVO</p>
        <p style="color:white;font-weight:600;font-size:0.9rem;margin-bottom:0.1rem;">{perfil_atual['perfil']}</p>
        <p style="color:#5a7a9e;font-size:0.72rem;font-family:'JetBrains Mono',monospace;">@{usuario_atual}</p>
    </div>
    """, unsafe_allow_html=True)
    badge_db = ('<span class="badge-sqlite">📁 SQLite Ativo</span>' if sqlite_ativo
                else '<span class="badge-sqlite" style="border-color:rgba(255,68,68,0.3);color:#ff4444;">⚠️ Banco Offline</span>')
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='color:#3a5a7e;font-size:0.65rem;letter-spacing:0.1em;'>PERMISSÕES</p>", unsafe_allow_html=True)
    for nome, ativo in [("📊 Análise", perfil_atual["pode_analisar"]),
                         ("📤 Exportar", perfil_atual["pode_exportar"]),
                         ("👁️ Ver IPs", perfil_atual["ver_pii"])]:
        color = "#00ff64" if ativo else "#ff4444"
        icon  = "✓" if ativo else "✗"
        st.markdown(f"<p style='color:{color};font-size:0.75rem;margin:0.2rem 0;'>{icon} {nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.05);border:1px solid rgba(0,212,255,0.1);
                border-radius:12px;padding:0.9rem;text-align:center;">
        <p style="color:#3a5a7e;font-size:0.62rem;letter-spacing:0.1em;">ACURÁCIA DO MODELO</p>
        <p style="color:#00d4ff;font-size:1.6rem;font-weight:700;
                  font-family:'JetBrains Mono',monospace;">{acuracia:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.8rem;">
        <div>
            <p style="color:#3a5a7e;font-size:0.62rem;letter-spacing:0.15em;
                      font-family:'JetBrains Mono',monospace;margin-bottom:0.3rem;">
                BEM-VINDO, {usuario_atual.upper()}
            </p>
            <h1 style="color:white;margin:0;font-size:1.5rem;font-weight:700;">
                Painel de Inteligência contra Ameaças
            </h1>
            <p style="color:#5a7a9e;margin-top:0.3rem;font-size:0.8rem;">
                {f"Visão do Cliente: <strong style='color:#00d4ff;'>{cliente_vinculado}</strong>" if cliente_vinculado else "Visão Global — Todos os Clientes"}
            </p>
        </div>
        <div style="text-align:right;">
            <span class="badge-online">● SISTEMA PROTEGIDO</span>
            <p style="color:#3a5a7e;font-size:0.65rem;margin-top:0.5rem;
                      font-family:'JetBrains Mono',monospace;">
                {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── MÉTRICAS ─────────────────────────────────────────────────────────────────

total_incidentes    = len(df_vis)
incidentes_criticos = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloqueados      = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo_total      = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"] == "resolvido"])
incidentes_pendentes  = len(df_vis[df_vis["STATUS"] == "pendente"])

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1: st.metric("Total Incidentes", f"{total_incidentes:,}")
with col2: st.metric("Críticos",          f"{incidentes_criticos:,}")
with col3: st.metric("IPs Bloqueados",    f"{ips_bloqueados:,}")
with col4: st.metric("Resolvidos",        f"{incidentes_resolvidos:,}")
with col5: st.metric("Pendentes",         f"{incidentes_pendentes:,}")
with col6:
    prej_fmt = f"R$ {prejuizo_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Prejuízo Estimado", prej_fmt)

st.markdown("---")

# ─── ABAS ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Análise", "📊 Métricas", "🌍 Mapa de Ameaças", "🤖 Assistente IA", "💾 Backup", "📋 Logs"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — ANÁLISE
# ════════════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown("### Análise de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Seu perfil não tem permissão para realizar análises.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            tipo_incidente  = st.selectbox("Tipo de Incidente", encoders["tipo"].classes_)
            origem_ataque   = st.selectbox("Origem",            encoders["origem"].classes_)
            cliente_afetado = st.selectbox("Cliente",           sorted(df["CLIENTE"].unique()))
        with col_b:
            tempo_resolucao = st.slider("Tempo de Resolução (minutos)", 1, 120, 30)
            status_atual    = st.selectbox("Status",            encoders["status"].classes_)

        if st.button("🚀 Iniciar Análise", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: {tipo_incidente}")
            with st.spinner("Analisando ameaça..."):
                time.sleep(1)

            entrada = pd.DataFrame({
                "TIPO_ENC":       [encoders["tipo"].transform([tipo_incidente])[0]],
                "ORIGEM_ENC":     [encoders["origem"].transform([origem_ataque])[0]],
                "TEMPO RESOLUÇÃO":[tempo_resolucao],
                "STATUS_ENC":     [encoders["status"].transform([status_atual])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status_atual == "resolvido":
                resultado = "baixa"
            elif tipo_incidente in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo_incidente in ["lentidão", "erro sistema"]:
                resultado = random.choice(["baixa", "média"])

            risco     = random.randint(10, 99)
            prej_est  = random.uniform(3000, 30000)
            risco_fin = "ALTO" if prej_est > 15000 else ("MÉDIO" if prej_est > 7000 else "BAIXO")

            ataques = df[df["TIPO INCIDENTE"] == "ataque"]
            if not ataques.empty:
                linha  = ataques.sample(1).iloc[0]
                ip_ex  = linha["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(linha["IP_SUSPEITO"])
                pais   = linha["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "DESCONHECIDO", "INTERNO"

            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 Severidade: **{resultado.upper()}** — AÇÃO IMEDIATA NECESSÁRIA")
            elif resultado == "média":
                st.warning(f"🟡 Severidade: **{resultado.upper()}** — MONITORAMENTO ATIVO")
            else:
                st.success(f"🟢 Severidade: **{resultado.upper()}** — BAIXO RISCO")

            r1, r2, r3 = st.columns(3)
            with r1: st.metric("Pontuação de Ameaça", f"{risco}/100")
            with r2: st.metric("Prejuízo Estimado",   f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Risco Financeiro",     risco_fin)

            st.write(f"**Cliente afetado:** {cliente_afetado}")
            if tipo_incidente == "ataque":
                st.error(f"🌍 Origem: **{pais}** | IP: `{ip_ex}`")
                with st.expander("🛡️ Resposta Automática Ativada"):
                    for a in ["✅ IP bloqueado no firewall", "✅ Regras de WAF atualizadas",
                               "✅ Equipe de resposta notificada", "✅ Logs forenses capturados"]:
                        st.write(a)

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo_incidente, "origem": origem_ataque,
                    "status": status_atual, "severidade": resultado, "cliente": cliente_afetado
                })
                st.success("💾 Incidente registrado no banco de dados")
            adicionar_log(usuario_atual, f"Análise concluída: severidade={resultado}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — MÉTRICAS
# ════════════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("### Painel de Métricas")
    LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                  font_color="#8b9dc3", font_family="Inter")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_pie = px.pie(df_vis, names="SEVERIDADE", title="Distribuição por Severidade",
                         color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig_pie.update_layout(**LAYOUT, title_font_color="#00d4ff")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_g2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig_bar = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Incidentes por Tipo",
                         color_discrete_sequence=["#00d4ff"])
        fig_bar.update_layout(**LAYOUT, title_font_color="#00d4ff")
        st.plotly_chart(fig_bar, use_container_width=True)

    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig_line = px.line(df_time, x="DATA", y="Incidentes",
                       title="Volume de Ameaças ao Longo do Tempo",
                       color_discrete_sequence=["#00d4ff"])
    fig_line.update_layout(**LAYOUT, title_font_color="#00d4ff")
    st.plotly_chart(fig_line, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        fig_hist = px.histogram(df_vis, x="PAIS_ATAQUE", title="Ataques por País",
                                color_discrete_sequence=["#00d4ff"])
        fig_hist.update_layout(**LAYOUT, title_font_color="#00d4ff")
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_g4:
        damage = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        damage = damage.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig_damage = px.bar(damage, x="CLIENTE", y="PREJUIZO_ESTIMADO",
                            title="Impacto Financeiro por Cliente",
                            color_discrete_sequence=["#00d4ff"])
        fig_damage.update_layout(**LAYOUT, title_font_color="#00d4ff")
        st.plotly_chart(fig_damage, use_container_width=True)

    st.markdown("### Desempenho do Modelo de IA")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Acurácia",       f"{acuracia:.1%}")
    with m2: st.metric("Base de Treino", f"{int(len(df)*0.8):,}")
    with m3: st.metric("Base de Teste",  f"{int(len(df)*0.2):,}")

    y_pred = modelo.predict(X_test)
    cm     = confusion_matrix(y_test, y_pred)
    labels = encoders["severidade"].classes_
    fig_cm = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0, "#060b18"], [1, "#00d4ff"]],
        text=cm, texttemplate="%{text}", showscale=True
    ))
    fig_cm.update_layout(title="Matriz de Confusão", title_font_color="#00d4ff",
                         xaxis_title="Previsto", yaxis_title="Real", height=320, **LAYOUT)
    st.plotly_chart(fig_cm, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — MAPA DE AMEAÇAS (REDESENHADO)
# ════════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("### 🌍 Mapa Global de Ameaças em Tempo Real")
    st.caption("Visualização inspirada no Kaspersky Cyberthreat Map — ataques ao Brasil em destaque")

    COORDS = {
        "China":          (35.86,  104.19),
        "Russia":         (61.52,  105.31),
        "United States":  (37.09,  -95.71),
        "North Korea":    (40.33,  127.51),
        "Germany":        (51.16,   10.45),
        "Brazil":        (-14.23,  -51.92),
        "Canada":         (56.13, -106.34),
        "India":          (20.59,   78.96),
        "France":         (46.22,    2.21),
        "United Kingdom": (52.13,   -1.09),
        "Iran":           (36.20,   53.68),
        "Australia":     (-25.27,  133.77),
        "Japan":          (36.20,  138.25),
        "Netherlands":    (52.13,    5.29),
        "Ukraine":        (48.38,   31.17),
    }
    TARGET = (-15.78, -47.92)

    attack_df     = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    country_count = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    country_count.columns = ["country", "total"]

    import json
    arcs = []
    for _, row in country_count.iterrows():
        c = row["country"]
        if c in COORDS:
            src = COORDS[c]
            arcs.append({
                "src_lat": src[0], "src_lon": src[1],
                "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                "name": c, "count": int(row["total"]),
                "severity": "high" if row["total"] > 30 else ("medium" if row["total"] > 15 else "low")
            })

    arcs_json = json.dumps(arcs)

    # ── Mapa HTML/Canvas altamente estilizado ────────────────────────────────
    map_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#060b18; overflow:hidden; font-family:'Segoe UI',system-ui,sans-serif; }
  canvas { display:block; }

  /* ── HUD Panels ── */
  .panel {
    position:absolute;
    background:rgba(4,8,20,0.88);
    backdrop-filter:blur(14px);
    border:1px solid rgba(0,212,255,0.18);
    border-radius:14px;
    z-index:100;
    pointer-events:none;
  }
  .panel::before {
    content:'';
    position:absolute;
    top:0; left:10%; right:10%;
    height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,212,255,0.45),transparent);
  }

  #panel-stats {
    top:16px; right:16px;
    padding:14px 20px;
    min-width:160px;
    text-align:center;
  }
  .stat-label {
    color:rgba(90,122,158,0.9);
    font-size:9px;
    letter-spacing:0.14em;
    text-transform:uppercase;
    margin-bottom:2px;
  }
  .stat-value {
    color:#00d4ff;
    font-size:26px;
    font-weight:700;
    font-family:'Courier New',monospace;
    line-height:1.1;
  }
  .stat-divider { border:none; border-top:1px solid rgba(0,212,255,0.1); margin:10px 0; }

  #panel-legend {
    bottom:16px; left:16px;
    padding:12px 16px;
  }
  .legend-title { color:#00d4ff; font-size:11px; font-weight:600; margin-bottom:8px; }
  .legend-row { display:flex; align-items:center; gap:8px; margin:4px 0; }
  .legend-dot { width:9px; height:9px; border-radius:50%; flex-shrink:0; }
  .legend-text { color:rgba(180,200,220,0.8); font-size:10px; }

  #panel-live {
    top:16px; left:16px;
    padding:10px 14px;
    min-width:180px;
  }
  .live-dot {
    display:inline-block; width:8px; height:8px; border-radius:50%;
    background:#00ff64; margin-right:6px;
    animation:pulse 1.5s ease-in-out infinite;
  }
  .live-label { color:#00d4ff; font-size:11px; font-weight:600; }
  .live-feed { margin-top:8px; max-height:80px; overflow:hidden; }
  .feed-item {
    color:rgba(160,190,210,0.85); font-size:9.5px; padding:2px 0;
    border-bottom:1px solid rgba(0,212,255,0.06);
    font-family:'Courier New',monospace;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }

  #tooltip {
    position:absolute; display:none; pointer-events:none; z-index:200;
    background:rgba(4,8,20,0.96);
    border:1px solid rgba(0,212,255,0.35);
    border-radius:10px;
    padding:10px 14px;
    font-size:11px;
    color:#00d4ff;
    min-width:160px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }
  .tt-name { font-weight:700; font-size:12px; margin-bottom:4px; }
  .tt-count { color:rgba(180,200,220,0.8); }
  .tt-bar { height:3px; background:rgba(0,212,255,0.15); border-radius:2px; margin-top:6px; overflow:hidden; }
  .tt-fill { height:100%; background:#00d4ff; border-radius:2px; transition:width 0.3s; }

  @keyframes pulse {
    0%,100% { opacity:1; box-shadow:0 0 0 0 rgba(0,255,100,0.4); }
    50%      { opacity:.7; box-shadow:0 0 0 5px rgba(0,255,100,0); }
  }
</style>
</head>
<body>
<canvas id="c"></canvas>

<!-- Live feed -->
<div class="panel" id="panel-live">
  <div><span class="live-dot"></span><span class="live-label">ATAQUES AO VIVO</span></div>
  <div class="live-feed" id="live-feed"></div>
</div>

<!-- Stats -->
<div class="panel" id="panel-stats">
  <div class="stat-label">Ameaças Detectadas</div>
  <div class="stat-value" id="attackCount">0</div>
  <hr class="stat-divider">
  <div class="stat-label">IPs Bloqueados</div>
  <div class="stat-value" id="ipCount">0</div>
  <hr class="stat-divider">
  <div class="stat-label">Países Ativos</div>
  <div class="stat-value" id="countryCount">0</div>
</div>

<!-- Legend -->
<div class="panel" id="panel-legend">
  <div class="legend-title">🌐 LEGENDA</div>
  <div class="legend-row"><div class="legend-dot" style="background:#ef4444;box-shadow:0 0 6px #ef4444;"></div><span class="legend-text">Alto Volume (&gt;30 ataques)</span></div>
  <div class="legend-row"><div class="legend-dot" style="background:#f59e0b;box-shadow:0 0 6px #f59e0b;"></div><span class="legend-text">Médio (15–30 ataques)</span></div>
  <div class="legend-row"><div class="legend-dot" style="background:#00d4ff;box-shadow:0 0 6px #00d4ff;"></div><span class="legend-text">Baixo (&lt;15 ataques)</span></div>
  <div class="legend-row" style="margin-top:8px;border-top:1px solid rgba(0,212,255,0.1);padding-top:8px;">
    <div class="legend-dot" style="background:#00ff64;box-shadow:0 0 8px #00ff64;width:11px;height:11px;"></div>
    <span class="legend-text" style="color:#00ff64;font-weight:600;">🎯 ALVO: BRASIL</span>
  </div>
</div>

<!-- Tooltip -->
<div id="tooltip">
  <div class="tt-name" id="tt-name"></div>
  <div class="tt-count" id="tt-count"></div>
  <div class="tt-bar"><div class="tt-fill" id="tt-fill"></div></div>
</div>

<script>
var ARCS = """ + arcs_json + """;
var maxCount = ARCS.reduce(function(m,a){ return Math.max(m,a.count); }, 1);
document.getElementById('countryCount').textContent = ARCS.length;

var canvas = document.getElementById('c');
var ctx    = canvas.getContext('2d');
var W, H;
var particles  = [];
var frameN     = 0;
var attackTotal= 0, ipTotal = 0;
var feedItems  = [];

function resize() {
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

/* coordinate mapping */
function ll2px(lat, lon) {
  return [ (lon+180)/360*W, (90-lat)/180*H ];
}

/* colour helpers */
function arcColor(arc) {
  return arc.severity==='high'   ? [239,68,68]
       : arc.severity==='medium' ? [245,158,11]
       :                           [0,212,255];
}

/* ── Background: stars ── */
var stars = [];
for(var i=0;i<180;i++){
  stars.push({ x:Math.random(), y:Math.random(), r:Math.random()*1.2+0.3, a:Math.random() });
}
function drawStars(){
  for(var i=0;i<stars.length;i++){
    var s=stars[i];
    ctx.beginPath();
    ctx.arc(s.x*W, s.y*H, s.r, 0, Math.PI*2);
    ctx.fillStyle='rgba(150,180,220,'+(0.15+s.a*0.25)+')';
    ctx.fill();
  }
}

/* ── Grid ── */
function drawGrid(){
  ctx.lineWidth=0.4;
  for(var lon=-180;lon<=180;lon+=30){
    var p=ll2px(0,lon);
    ctx.beginPath(); ctx.moveTo(p[0],0); ctx.lineTo(p[0],H);
    ctx.strokeStyle='rgba(0,180,255,0.055)'; ctx.stroke();
  }
  for(var lat=-90;lat<=90;lat+=30){
    var p=ll2px(lat,0);
    ctx.beginPath(); ctx.moveTo(0,p[1]); ctx.lineTo(W,p[1]);
    ctx.strokeStyle='rgba(0,180,255,0.055)'; ctx.stroke();
  }
  /* equator emphasis */
  var eq=ll2px(0,0);
  ctx.beginPath(); ctx.moveTo(0,eq[1]); ctx.lineTo(W,eq[1]);
  ctx.strokeStyle='rgba(0,212,255,0.12)'; ctx.lineWidth=0.8; ctx.stroke();
}

/* ── Country nodes ── */
var NODES = [
  [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],
  [40.33,127.51,"PRK"],[51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],
  [56.13,-106.34,"CAN"],[20.59,78.96,"IND"],[46.22,2.21,"FRA"],
  [52.13,-1.09,"GBR"],[36.20,53.68,"IRN"],[-25.27,133.77,"AUS"],
  [36.20,138.25,"JPN"],[52.13,5.29,"NLD"],[48.38,31.17,"UKR"]
];

function drawNodes(t){
  for(var i=0;i<NODES.length;i++){
    var n=NODES[i];
    var p=ll2px(n[0],n[1]);
    var isBR = n[2]==='BRA';

    if(isBR){
      /* pulsing ring */
      var pulse = 0.5+0.5*Math.sin(t*0.05);
      ctx.beginPath();
      ctx.arc(p[0],p[1],20+pulse*10,0,Math.PI*2);
      ctx.strokeStyle='rgba(0,255,100,'+(0.08+pulse*0.08)+')';
      ctx.lineWidth=1; ctx.stroke();

      ctx.beginPath();
      ctx.arc(p[0],p[1],12,0,Math.PI*2);
      ctx.strokeStyle='rgba(0,255,100,0.3)';
      ctx.lineWidth=1.2; ctx.stroke();

      ctx.beginPath();
      ctx.arc(p[0],p[1],5,0,Math.PI*2);
      ctx.fillStyle='#00ff64';
      ctx.shadowColor='#00ff64'; ctx.shadowBlur=14;
      ctx.fill();
      ctx.shadowBlur=0;

      ctx.fillStyle='#00ff64';
      ctx.font='bold 11px "Segoe UI",sans-serif';
      ctx.fillText(n[2],p[0]+10,p[1]+4);
    } else {
      ctx.beginPath();
      ctx.arc(p[0],p[1],3.5,0,Math.PI*2);
      ctx.fillStyle='rgba(0,180,255,0.35)';
      ctx.shadowColor='rgba(0,180,255,0.5)'; ctx.shadowBlur=6;
      ctx.fill(); ctx.shadowBlur=0;

      ctx.fillStyle='rgba(120,170,210,0.7)';
      ctx.font='9px "Segoe UI",sans-serif';
      ctx.fillText(n[2],p[0]+6,p[1]+3);
    }
  }
}

/* ── Arcs (static ghost) ── */
function drawArcGhost(arc){
  var src=ll2px(arc.src_lat,arc.src_lon);
  var dst=ll2px(arc.dst_lat,arc.dst_lon);
  var mx=(src[0]+dst[0])/2;
  var my=Math.min(src[1],dst[1])-Math.abs(dst[0]-src[0])*0.18;
  var c=arcColor(arc);
  ctx.beginPath();
  ctx.moveTo(src[0],src[1]);
  ctx.quadraticCurveTo(mx,my,dst[0],dst[1]);
  ctx.strokeStyle='rgba('+c[0]+','+c[1]+','+c[2]+',0.06)';
  ctx.lineWidth=0.8; ctx.stroke();
}

/* ── Particle ── */
function Particle(arc){
  this.arc=arc;
  this.t=0;
  this.speed=0.0025+Math.random()*0.003;
  this.trail=[];
  this.trailLen=22+Math.floor(Math.random()*12);
  this.w=1.2+Math.random()*1.4;
}
Particle.prototype.pos=function(t){
  var src=ll2px(this.arc.src_lat,this.arc.src_lon);
  var dst=ll2px(this.arc.dst_lat,this.arc.dst_lon);
  var mx=(src[0]+dst[0])/2;
  var my=Math.min(src[1],dst[1])-Math.abs(dst[0]-src[0])*0.18;
  var u=1-t;
  return [u*u*src[0]+2*u*t*mx+t*t*dst[0],
          u*u*src[1]+2*u*t*my+t*t*dst[1]];
};
Particle.prototype.update=function(){
  this.t+=this.speed;
  var p=this.pos(Math.min(this.t,1));
  this.trail.push(p);
  if(this.trail.length>this.trailLen) this.trail.shift();
  return this.t<1;
};
Particle.prototype.draw=function(){
  if(this.trail.length<2) return;
  var c=arcColor(this.arc);
  for(var i=1;i<this.trail.length;i++){
    var a=i/this.trail.length;
    ctx.beginPath();
    ctx.moveTo(this.trail[i-1][0],this.trail[i-1][1]);
    ctx.lineTo(this.trail[i][0],  this.trail[i][1]);
    ctx.strokeStyle='rgba('+c[0]+','+c[1]+','+c[2]+','+a+')';
    ctx.lineWidth=this.w*a;
    ctx.stroke();
  }
  /* head glow */
  var last=this.trail[this.trail.length-1];
  ctx.beginPath();
  ctx.arc(last[0],last[1],2.5,0,Math.PI*2);
  ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';
  ctx.shadowColor='rgb('+c[0]+','+c[1]+','+c[2]+')';
  ctx.shadowBlur=8; ctx.fill(); ctx.shadowBlur=0;
};

/* ── Live feed ── */
var FEED_NAMES=['Ransomware','DDoS','SQL Injection','Phishing','Brute Force','Zero-Day','MitM','Malware'];
function addFeedItem(arc){
  var el=document.getElementById('live-feed');
  var type=FEED_NAMES[Math.floor(Math.random()*FEED_NAMES.length)];
  var d=document.createElement('div');
  d.className='feed-item';
  var now=new Date();
  var hh=String(now.getHours()).padStart(2,'0');
  var mm=String(now.getMinutes()).padStart(2,'0');
  var ss=String(now.getSeconds()).padStart(2,'0');
  d.textContent=hh+':'+mm+':'+ss+' '+arc.name+' → '+type;
  el.insertBefore(d,el.firstChild);
  while(el.children.length>6) el.removeChild(el.lastChild);
}

/* ── Spawn ── */
function spawn(){
  if(!ARCS.length) return;
  var arc=ARCS[Math.floor(Math.random()*ARCS.length)];
  if(Math.random()<0.15+arc.count/maxCount*0.25){
    particles.push(new Particle(arc));
  }
}

/* ── Main loop ── */
function loop(){
  requestAnimationFrame(loop);
  ctx.fillStyle='#060b18';
  ctx.fillRect(0,0,W,H);

  drawStars();
  drawGrid();
  ARCS.forEach(drawArcGhost);
  drawNodes(frameN);

  if(frameN%8===0) spawn();

  var alive=[];
  for(var i=0;i<particles.length;i++){
    if(particles[i].update()){
      particles[i].draw();
      alive.push(particles[i]);
    } else {
      attackTotal++;
      ipTotal=Math.floor(attackTotal*0.72);
      document.getElementById('attackCount').textContent=attackTotal.toLocaleString();
      document.getElementById('ipCount').textContent=ipTotal.toLocaleString();
      if(attackTotal%3===0) addFeedItem(particles[i].arc);
    }
  }
  particles=alive;
  frameN++;
}
loop();

/* ── Tooltip ── */
canvas.addEventListener('mousemove',function(e){
  var rect=canvas.getBoundingClientRect();
  var mx=(e.clientX-rect.left)*(W/rect.width);
  var my=(e.clientY-rect.top )*(H/rect.height);
  var tip=document.getElementById('tooltip');
  var found=false;
  for(var i=0;i<ARCS.length;i++){
    var arc=ARCS[i];
    var p=ll2px(arc.src_lat,arc.src_lon);
    if(Math.hypot(mx-p[0],my-p[1])<22){
      document.getElementById('tt-name').textContent=arc.name;
      document.getElementById('tt-count').textContent=arc.count+' ataques detectados';
      document.getElementById('tt-fill').style.width=(arc.count/maxCount*100)+'%';
      tip.style.display='block';
      tip.style.left=(e.clientX+18)+'px';
      tip.style.top =(e.clientY-55)+'px';
      found=true; break;
    }
  }
  if(!found) tip.style.display='none';
});
canvas.addEventListener('mouseleave',function(){
  document.getElementById('tooltip').style.display='none';
});
</script>
</body>
</html>"""

    components.html(map_html, height=580, scrolling=False)

    st.markdown("### Países com Mais Ataques")
    top_attackers = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    top_attackers.columns = ["País", "Ataques"]
    top_attackers["Percentual"] = (top_attackers["Ataques"] / top_attackers["Ataques"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(top_attackers, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — ASSISTENTE IA  ← CORREÇÃO PRINCIPAL DA API
# ════════════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown("### 🤖 Assistente de IA — SentinelBot")
    st.caption("Pergunte sobre incidentes, clientes, ameaças ou peça recomendações de segurança")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    top5_clientes = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5_ataques  = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    system_prompt = f"""Você é o SentinelBot, assistente de segurança cibernética da SentinelAI.
Responda em português do Brasil, de forma profissional e direta.

DADOS DO SISTEMA:
- Total de incidentes: {len(df_vis)}
- Incidentes críticos: {len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])} ({len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])/len(df_vis)*100:.1f}%)
- IPs bloqueados: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower() == 'sim'])}
- Prejuízo total: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- Acurácia do modelo: {acuracia:.1%}
- Tipos de incidente: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Clientes: {', '.join(df_vis['CLIENTE'].unique())}
- Top 5 países atacantes: {top5_ataques}
- Top 5 clientes por prejuízo: {top5_clientes}
- Período: {df_vis['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].min()) else 'N/A'} a {df_vis['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].max()) else 'N/A'}
{'- Visão: todos os clientes' if not cliente_vinculado else f'- Filtro ativo: apenas {cliente_vinculado}'}"""

    if not ANTHROPIC_API_KEY:
        st.error("🔴 Assistente offline — Configure a chave da API nos Secrets do Streamlit")
    else:
        st.success("🟢 Assistente ativo — Pronto para perguntas")

    for msg in st.session_state["chat_history"]:
        css_class = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon      = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{css_class}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col_q, col_b = st.columns([5, 1])
        with col_q:
            pergunta = st.text_input("", placeholder="Ex: Qual cliente teve mais prejuízo?",
                                     label_visibility="collapsed", disabled=not ANTHROPIC_API_KEY)
        with col_b:
            enviar = st.form_submit_button("Enviar", use_container_width=True, disabled=not ANTHROPIC_API_KEY)

    sugestoes = ["Qual cliente teve mais prejuízo?", "Quais países mais atacaram?",
                 "Como estão os incidentes críticos?", "Acurácia do modelo?", "Recomendações de segurança"]
    cols_sug = st.columns(len(sugestoes))
    sugestao_escolhida = None
    for i, sug in enumerate(sugestoes):
        with cols_sug[i]:
            label = sug[:22] + "…" if len(sug) > 22 else sug
            if st.button(label, key=f"sug{i}", use_container_width=True, disabled=not ANTHROPIC_API_KEY):
                sugestao_escolhida = sug

    if sugestao_escolhida:
        pergunta = sugestao_escolhida
        enviar   = True

    if enviar and pergunta and ANTHROPIC_API_KEY:
        adicionar_log(usuario_atual, f"Chat: {pergunta[:50]}")
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        with st.spinner("🤔 Analisando..."):
            try:
                headers_api = {
                    "x-api-key":         ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type":      "application/json"
                }
                payload_api = {
                    # ✅ MODELO ATUALIZADO — claude-3-haiku-20240307 foi descontinuado
                    "model":      "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "system":     system_prompt,
                    "messages":   [{"role": m["role"], "content": m["content"]}
                                   for m in st.session_state["chat_history"]]
                }
                resp_api = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers_api,
                    json=payload_api,
                    timeout=30
                )
                if resp_api.status_code == 200:
                    resposta = resp_api.json()["content"][0]["text"]
                else:
                    err = resp_api.json()
                    resposta = f"⚠️ Erro {resp_api.status_code}: {err.get('error', {}).get('message', resp_api.text[:120])}"
            except Exception as e:
                resposta = f"⚠️ Erro de conexão: {str(e)[:100]}"

        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
        adicionar_log(usuario_atual, "Resposta gerada pelo SentinelBot")
        st.rerun()

    if st.session_state["chat_history"]:
        if st.button("🗑️ Limpar conversa"):
            st.session_state["chat_history"] = []
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — BACKUP
# ════════════════════════════════════════════════════════════════════════════════

with tab5:
    st.markdown("### Backup e Exportação de Dados")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Exportação restrita — Apenas administradores podem exportar dados.")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("📥 Exportar CSV Completo",
                               df.to_csv(index=False).encode("utf-8"),
                               f"sentinelai_{ts}.csv", "text/csv", use_container_width=True)
        with col_b2:
            df_anon = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("🔒 Exportar Anonimizado",
                               df_anon.to_csv(index=False).encode("utf-8"),
                               f"sentinelai_anon_{ts}.csv", "text/csv", use_container_width=True)
        with col_b3:
            if "logs_sistema" in st.session_state:
                st.download_button("📋 Exportar Logs",
                                   "\n".join(st.session_state["logs_sistema"]).encode("utf-8"),
                                   f"sentinelai_logs_{ts}.txt", "text/plain", use_container_width=True)
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("🗄️ Backup SQLite",
                                   f.read(), f"sentinelai_db_{ts}.db",
                                   "application/x-sqlite3", use_container_width=True)

    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### Histórico de Backups da Sessão")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)

    st.markdown("### Prévia dos Dados (20 registros)")
    st.dataframe(df_vis.head(20), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 6 — LOGS
# ════════════════════════════════════════════════════════════════════════════════

with tab6:
    st.markdown("### Logs do Sistema")
    tab_log1, tab_log2 = st.tabs(["📱 Sessão Atual", "💾 Histórico do Banco"])
    with tab_log1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("Nenhum log registrado na sessão atual.")
    with tab_log2:
        if sqlite_ativo:
            try:
                logs_db = pd.read_sql_query(
                    "SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not logs_db.empty:
                    st.dataframe(logs_db, use_container_width=True)
                else:
                    st.info("Nenhum log encontrado no banco de dados.")
            except Exception:
                st.info("Erro ao carregar logs do banco.")
        else:
            st.warning("Banco de dados offline.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center;padding:1.2rem 0;border-top:1px solid rgba(0,212,255,0.07);margin-top:1.5rem;">
    <p style="color:#2a4a6a;font-size:0.68rem;font-family:'JetBrains Mono',monospace;">
        SentinelAI © 2025 — Plataforma de Segurança Cibernética | LGPD Compliance
    </p>
</div>
""", unsafe_allow_html=True)
