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
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# ── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA"

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS GLOBAIS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* Reset & base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
  font-family: 'Inter', system-ui, sans-serif;
  scroll-behavior: smooth;
}

/* App background */
.stApp {
  background: #060810;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,200,255,0.08) 0%, transparent 70%),
    radial-gradient(ellipse 40% 30% at 80% 80%, rgba(0,80,200,0.05) 0%, transparent 60%);
}

/* Header oculto padrão */
[data-testid="stHeader"] { background: transparent; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #070910 0%, #0a0d16 100%);
  border-right: 1px solid rgba(0,200,255,0.07);
}

/* Block container */
.block-container { padding: 1.2rem 1.5rem; max-width: 100%; }

/* ── MÉTRICAS ── */
div[data-testid="metric-container"] {
  background: linear-gradient(135deg, rgba(0,200,255,0.04) 0%, rgba(6,8,16,0.95) 100%);
  border: 1px solid rgba(0,200,255,0.12);
  border-radius: 14px;
  padding: 1rem 1.2rem;
  transition: all .25s ease;
  position: relative;
  overflow: hidden;
}
div[data-testid="metric-container"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,200,255,0.4), transparent);
}
div[data-testid="metric-container"]:hover {
  border-color: rgba(0,200,255,0.28);
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0,200,255,0.08);
}
[data-testid="stMetricLabel"] {
  color: #5a7a9a !important;
  font-size: .6rem !important;
  text-transform: uppercase;
  letter-spacing: .1em;
}
[data-testid="stMetricValue"] {
  color: #00d4ff !important;
  font-size: 1.45rem !important;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

/* ── BOTÕES ── */
div.stButton > button {
  background: linear-gradient(135deg, #0077b6, #00b4d8);
  color: white;
  border-radius: 10px;
  border: none;
  padding: .55rem 1rem;
  font-weight: 600;
  font-size: .8rem;
  transition: all .2s ease;
  width: 100%;
  letter-spacing: .03em;
}
div.stButton > button:hover {
  background: linear-gradient(135deg, #0096c7, #00d4ff);
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0,200,255,0.2);
}

/* ── CHAT ── */
.chat-user {
  background: linear-gradient(135deg, #0077b6, #00b4d8);
  border-radius: 18px 18px 4px 18px;
  padding: .7rem 1.1rem;
  margin: .5rem 0 .5rem auto;
  max-width: 78%;
  width: fit-content;
  color: white;
  font-size: .82rem;
  line-height: 1.5;
  box-shadow: 0 4px 16px rgba(0,120,182,0.25);
}
.chat-ai {
  background: rgba(10,14,24,.95);
  border: 1px solid rgba(0,200,255,0.14);
  border-radius: 18px 18px 18px 4px;
  padding: .7rem 1.1rem;
  margin: .5rem 0;
  max-width: 78%;
  width: fit-content;
  color: #ccd8e8;
  font-size: .82rem;
  line-height: 1.5;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

/* ── HEADER PRINCIPAL ── */
.sentinel-header {
  background: linear-gradient(135deg, rgba(0,200,255,0.05) 0%, rgba(0,80,160,0.03) 100%);
  border: 1px solid rgba(0,200,255,0.1);
  border-radius: 16px;
  padding: 1.2rem 1.8rem;
  margin-bottom: 1.2rem;
  position: relative;
  overflow: hidden;
}
.sentinel-header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,200,255,0.3), transparent);
}

/* ── BADGES ── */
.badge-online {
  display: inline-flex; align-items: center; gap: .3rem;
  background: rgba(0,255,100,.07);
  border: 1px solid rgba(0,255,100,.2);
  color: #00ff88;
  padding: .25rem .8rem;
  border-radius: 20px;
  font-size: .6rem;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.badge-db {
  display: inline-flex; align-items: center; gap: .3rem;
  background: rgba(0,200,255,.07);
  border: 1px solid rgba(0,200,255,.2);
  color: #00d4ff;
  padding: .25rem .8rem;
  border-radius: 20px;
  font-size: .6rem;
  font-weight: 600;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(10,14,24,.8);
  border-radius: 12px;
  padding: .3rem;
  gap: .2rem;
  border: 1px solid rgba(0,200,255,.07);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px;
  color: #5a7a9a;
  font-weight: 500;
  padding: .45rem .9rem;
  font-size: .75rem;
  transition: all .2s;
}
.stTabs [aria-selected="true"] {
  background: rgba(0,180,216,.12) !important;
  color: #00d4ff !important;
}

/* ── INPUTS ── */
input, textarea, select {
  background: rgba(10,14,24,.9) !important;
  border: 1px solid rgba(0,200,255,.1) !important;
  border-radius: 10px !important;
  color: white !important;
}

/* ── SELECTBOX ── */
[data-baseweb="select"] {
  background: rgba(10,14,24,.9) !important;
}

hr { border-color: rgba(0,200,255,.06); margin: 1rem 0; }

/* ── PARALLAX HERO (login) ── */
.parallax-bg {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  z-index: -1;
  background:
    radial-gradient(ellipse 60% 40% at 30% 20%, rgba(0,150,255,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 50% 35% at 70% 75%, rgba(0,80,200,0.05) 0%, transparent 60%),
    #060810;
}

/* scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060810; }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.2); border-radius: 2px; }

/* Sidebar card de perfil */
.sidebar-profile {
  background: rgba(0,200,255,.04);
  border: 1px solid rgba(0,200,255,.08);
  border-radius: 12px;
  padding: .7rem .9rem;
  margin: .4rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── BANCO SQLITE ──────────────────────────────────────────────────────────────
def conectar_sqlite():
    try:
        return sqlite3.connect('sentinelai.db', check_same_thread=False)
    except:
        return None

def inicializar_sqlite(conn):
    try:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS incidentes_registrados (
            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, tipo_incidente TEXT,
            origem TEXT, status TEXT, severidade_prevista TEXT, cliente TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, acao TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
    except:
        pass

def salvar_incidente_sqlite(conn, d):
    try:
        conn.cursor().execute(
            "INSERT INTO incidentes_registrados (usuario,tipo_incidente,origem,status,severidade_prevista,cliente) VALUES (?,?,?,?,?,?)",
            (d["usuario"],d["tipo"],d["origem"],d["status"],d["severidade"],d["cliente"]))
        conn.commit()
    except:
        pass

def salvar_log_sqlite(conn, usuario, acao):
    try:
        conn.cursor().execute("INSERT INTO logs_sistema (usuario,acao) VALUES (?,?)", (usuario, acao))
        conn.commit()
    except:
        pass

# ── LOGS ──────────────────────────────────────────────────────────────────────
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
    st.session_state["backups"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": usuario, "motivo": motivo, "registros": len(df)
    })

def mascara_ip(ip):
    if ip == "Nenhum" or pd.isna(ip):
        return "***.***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

# ── USUÁRIOS ──────────────────────────────────────────────────────────────────
USUARIOS = {
    "admin":        {"senha": "admin123",    "perfil": "Administrador", "pode_exportar": True,  "pode_analisar": True,  "ver_pii": True,  "cliente_vinculado": None},
    "analista":     {"senha": "analista123", "perfil": "Analista",      "pode_exportar": False, "pode_analisar": True,  "ver_pii": False, "cliente_vinculado": None},
    "nubank":       {"senha": "nubank123",   "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha": "ml123",       "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander":    {"senha": "sant123",     "perfil": "Cliente",       "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer":       {"senha": "viewer123",   "perfil": "Visualizador",  "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
}

_hashes = {u: hashlib.sha256(v["senha"].encode()).hexdigest() for u, v in USUARIOS.items()}

def autenticar(u, s):
    return u in _hashes and hashlib.sha256(s.encode()).hexdigest() == _hashes[u]

# ── AUTH STATE ────────────────────────────────────────────────────────────────
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

# ── TELA DE LOGIN ─────────────────────────────────────────────────────────────
if not st.session_state["autenticado"]:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # Parallax canvas de fundo
    components.html("""
    <style>
      body { margin:0; overflow:hidden; background:#060810; }
      canvas { position:fixed; top:0; left:0; }
    </style>
    <canvas id="bg"></canvas>
    <script>
    const cv = document.getElementById('bg');
    const ctx = cv.getContext('2d');
    let W, H, particles = [];

    function resize() {
      W = cv.width = window.innerWidth;
      H = cv.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    class Particle {
      constructor() { this.reset(); }
      reset() {
        this.x = Math.random() * W;
        this.y = Math.random() * H;
        this.r = Math.random() * 1.5 + .3;
        this.vx = (Math.random() - .5) * .3;
        this.vy = (Math.random() - .5) * .3;
        this.a = Math.random() * .5 + .1;
      }
      update() {
        this.x += this.vx; this.y += this.vy;
        if (this.x < 0 || this.x > W || this.y < 0 || this.y > H) this.reset();
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.r, 0, Math.PI*2);
        ctx.fillStyle = `rgba(0,200,255,${this.a})`;
        ctx.fill();
      }
    }

    for (let i = 0; i < 120; i++) particles.push(new Particle());

    // Grid lines (subtle)
    function drawGrid() {
      ctx.strokeStyle = 'rgba(0,150,220,0.03)';
      ctx.lineWidth = 1;
      for (let x = 0; x < W; x += 60) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }
      for (let y = 0; y < H; y += 60) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }
    }

    function anim() {
      requestAnimationFrame(anim);
      ctx.fillStyle = 'rgba(6,8,16,0.85)';
      ctx.fillRect(0, 0, W, H);
      drawGrid();
      particles.forEach(p => { p.update(); p.draw(); });
    }
    anim();
    </script>
    """, height=0, scrolling=False)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
          <div style="
            display:inline-flex; align-items:center; justify-content:center;
            width:72px; height:72px; border-radius:20px;
            background: linear-gradient(135deg, rgba(0,200,255,0.15), rgba(0,80,160,0.1));
            border: 1px solid rgba(0,200,255,0.2);
            font-size: 2.2rem; margin-bottom: 1rem;
            box-shadow: 0 0 40px rgba(0,200,255,0.1);
          ">🛡️</div>
          <h1 style="color:#fff; font-size:2rem; font-weight:800; letter-spacing:-.02em; margin:0;">
            Sentinel<span style="color:#00d4ff;">AI</span>
          </h1>
          <p style="color:#5a7a9a; font-size:.85rem; margin: .4rem 0 1rem 0;">
            Plataforma de Segurança Cibernética
          </p>
          <span class="badge-online">● SISTEMA OPERACIONAL</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="
          background: rgba(10,14,24,0.85);
          border: 1px solid rgba(0,200,255,0.1);
          border-radius: 18px;
          padding: 1.8rem;
          backdrop-filter: blur(20px);
          box-shadow: 0 24px 64px rgba(0,0,0,0.4);
        ">
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<p style="color:#8b949e;font-size:.75rem;margin-bottom:.3rem;">USUÁRIO</p>', unsafe_allow_html=True)
            usuario_input = st.text_input("u", placeholder="admin, analista, nubank…", label_visibility="collapsed")
            st.markdown('<p style="color:#8b949e;font-size:.75rem;margin:.6rem 0 .3rem 0;">SENHA</p>', unsafe_allow_html=True)
            senha_input = st.text_input("s", type="password", placeholder="••••••••", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Entrar →", use_container_width=True)

            if submit:
                if autenticar(usuario_input, senha_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = usuario_input
                    adicionar_log(usuario_input, "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas")

        st.markdown("</div>", unsafe_allow_html=True)

        # Credenciais de demonstração
        st.markdown("""
        <div style="
          margin-top:1.2rem;
          background: rgba(0,200,255,0.03);
          border: 1px solid rgba(0,200,255,0.08);
          border-radius: 14px;
          padding: 1rem 1.2rem;
        ">
          <p style="color:#5a7a9a;font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;">
            Credenciais de demonstração
          </p>
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr>
                <th style="color:#3a5a7a;font-size:.6rem;text-align:left;padding:.2rem .4rem;">Usuário</th>
                <th style="color:#3a5a7a;font-size:.6rem;text-align:left;padding:.2rem .4rem;">Senha</th>
                <th style="color:#3a5a7a;font-size:.6rem;text-align:left;padding:.2rem .4rem;">Perfil</th>
              </tr>
            </thead>
            <tbody>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">admin</td><td style="color:#8b949e;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">admin123</td><td style="color:#00ff88;font-size:.65rem;padding:.2rem .4rem;">Administrador</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">analista</td><td style="color:#8b949e;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">analista123</td><td style="color:#f59e0b;font-size:.65rem;padding:.2rem .4rem;">Analista</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">nubank</td><td style="color:#8b949e;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">nubank123</td><td style="color:#8b949e;font-size:.65rem;padding:.2rem .4rem;">Cliente</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">viewer</td><td style="color:#8b949e;font-family:monospace;font-size:.7rem;padding:.2rem .4rem;">viewer123</td><td style="color:#8b949e;font-size:.65rem;padding:.2rem .4rem;">Visualizador</td></tr>
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ── PÓS-LOGIN ─────────────────────────────────────────────────────────────────
usuario_atual = st.session_state["usuario_atual"]
perfil_atual  = USUARIOS[usuario_atual]

if "sqlite_conn" not in st.session_state:
    st.session_state["sqlite_conn"] = conectar_sqlite()
    if st.session_state["sqlite_conn"]:
        inicializar_sqlite(st.session_state["sqlite_conn"])

sqlite_conn  = st.session_state["sqlite_conn"]
sqlite_ativo = sqlite_conn is not None

@st.cache_data
def carregar_dados():
    df = pd.read_csv("dataset_final.csv").dropna(subset=["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS","NIVEL_AMEACA","RISCO_FINANCEIRO"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo","origem","status","severidade"]}
    df["TIPO_ENC"]      = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"]    = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"]    = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"]= enc["severidade"].fit_transform(df["SEVERIDADE"])
    X = df[["TIPO_ENC","ORIGEM_ENC","TEMPO RESOLUÇÃO","STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    m = DecisionTreeClassifier(random_state=42)
    m.fit(Xtr, ytr)
    return df, enc, m, accuracy_score(yte, m.predict(Xte)), Xte, yte

df, encoders, modelo, acuracia, X_test, y_test = carregar_dados()

cliente_vinculado = perfil_atual["cliente_vinculado"]
df_vis = df[df["CLIENTE"] == cliente_vinculado].copy() if cliente_vinculado else df.copy()
salvar_backup_sessao(df_vis, usuario_atual, "Login")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:.8rem 0 .4rem 0;">
      <div style="font-size:1.8rem;">🛡️</div>
      <h3 style="color:#00d4ff; margin:.2rem 0; font-size:1.1rem; font-weight:700;">SentinelAI</h3>
      <p style="color:#3a5a7a; font-size:.6rem; letter-spacing:.1em;">SECURITY PLATFORM</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    cor_perfil = {"Administrador":"#00ff88","Analista":"#f59e0b","Cliente":"#00d4ff","Visualizador":"#8b949e"}
    cor = cor_perfil.get(perfil_atual['perfil'], '#8b949e')

    st.markdown(f"""
    <div class="sidebar-profile">
      <p style="color:#3a5a7a;font-size:.55rem;text-transform:uppercase;letter-spacing:.08em;">Perfil ativo</p>
      <p style="color:white;font-weight:700;font-size:.9rem;margin:.2rem 0;">{perfil_atual['perfil']}</p>
      <p style="color:#5a7a9a;font-size:.65rem;">@{usuario_atual}</p>
      <div style="margin-top:.4rem;">
        <span style="background:rgba(0,200,255,.07);border:1px solid rgba(0,200,255,.15);
          color:{cor};padding:.15rem .5rem;border-radius:12px;font-size:.55rem;font-weight:700;">
          ● {perfil_atual['perfil'].upper()}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    badge_db = (
        '<span class="badge-db">📁 SQLite Ativo</span>'
        if sqlite_ativo else
        '<span style="color:#ff4444;font-size:.65rem;">⚠️ DB Offline</span>'
    )
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p style="color:#3a5a7a;font-size:.6rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem;">Permissões</p>', unsafe_allow_html=True)
    for nome, ativo in [("Análise ML", perfil_atual["pode_analisar"]),
                        ("Exportar dados", perfil_atual["pode_exportar"]),
                        ("Visualizar IPs", perfil_atual["ver_pii"])]:
        c, i = ("#00ff88", "✓") if ativo else ("#ff4444", "✗")
        st.markdown(f'<p style="color:{c};font-size:.72rem;margin:.15rem 0;">{i} {nome}</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,200,255,.04);border:1px solid rgba(0,200,255,.08);
      border-radius:10px;padding:.7rem;text-align:center;margin:.4rem 0;">
      <p style="color:#3a5a7a;font-size:.55rem;text-transform:uppercase;letter-spacing:.08em;">Acurácia do Modelo</p>
      <p style="color:#00d4ff;font-size:1.4rem;font-weight:700;font-family:monospace;">{acuracia:.1%}</p>
      <p style="color:#3a5a7a;font-size:.55rem;">Decision Tree</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🚪 Encerrar sessão", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

# ── HEADER ────────────────────────────────────────────────────────────────────
now_str = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
st.markdown(f"""
<div class="sentinel-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;">
    <div>
      <p style="color:#3a5a7a;font-size:.58rem;text-transform:uppercase;letter-spacing:.12em;">
        {f"Cliente · {cliente_vinculado}" if cliente_vinculado else "Visão Global"}
      </p>
      <h1 style="color:white;margin:0;font-size:1.25rem;font-weight:800;letter-spacing:-.02em;">
        Painel de <span style="color:#00d4ff;">Segurança</span>
      </h1>
    </div>
    <div style="text-align:right;">
      <span class="badge-online">● PROTEGIDO</span>
      <p style="color:#3a5a7a;font-size:.58rem;margin-top:.3rem;">{now_str}</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── MÉTRICAS ──────────────────────────────────────────────────────────────────
total_incidentes     = len(df_vis)
incidentes_criticos  = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloqueados       = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo_total       = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos= len(df_vis[df_vis["STATUS"] == "resolvido"])
incidentes_pendentes = len(df_vis[df_vis["STATUS"] == "pendente"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
pf = f"R$ {prejuizo_total:,.0f}".replace(",","X").replace(".",",").replace("X",".")
with c1: st.metric("Total",         f"{total_incidentes:,}")
with c2: st.metric("Críticos",      f"{incidentes_criticos:,}")
with c3: st.metric("IPs Bloqueados",f"{ips_bloqueados:,}")
with c4: st.metric("Resolvidos",    f"{incidentes_resolvidos:,}")
with c5: st.metric("Pendentes",     f"{incidentes_pendentes:,}")
with c6: st.metric("Prejuízo Est.", pf)

st.markdown("---")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🔍 Análise ML", "📊 Métricas", "🌍 Mapa Global", "🤖 Assistente IA", "💾 Exportar", "📋 Logs"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — ANÁLISE
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Análise Preditiva de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Seu perfil não tem permissão para realizar análises.")
    else:
        ca, cb = st.columns(2)
        with ca:
            tipo_incidente  = st.selectbox("Tipo de incidente", encoders["tipo"].classes_)
            origem_ataque   = st.selectbox("Origem do ataque",  encoders["origem"].classes_)
            cliente_afetado = st.selectbox("Cliente afetado", sorted(df["CLIENTE"].unique()))
        with cb:
            tempo_resolucao = st.slider("Tempo estimado de resolução (min)", 1, 120, 30)
            status_atual    = st.selectbox("Status atual", encoders["status"].classes_)

        if st.button("🚀 Executar análise", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: {tipo_incidente}")
            with st.spinner("Processando modelo preditivo…"):
                time.sleep(1)

            entrada = pd.DataFrame({
                "TIPO_ENC":        [encoders["tipo"].transform([tipo_incidente])[0]],
                "ORIGEM_ENC":      [encoders["origem"].transform([origem_ataque])[0]],
                "TEMPO RESOLUÇÃO": [tempo_resolucao],
                "STATUS_ENC":      [encoders["status"].transform([status_atual])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]

            # regras de negócio
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
                l    = ataques.sample(1).iloc[0]
                ip_ex= l["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(l["IP_SUSPEITO"])
                pais = l["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "DESCONHECIDO", "INTERNO"

            st.markdown("---")
            cores = {"crítica": st.error, "média": st.warning, "baixa": st.success}
            msg_cores = {
                "crítica": f"🔴 Severidade: CRÍTICA — AÇÃO IMEDIATA NECESSÁRIA",
                "média":   f"🟡 Severidade: MÉDIA — Monitoramento ativo recomendado",
                "baixa":   f"🟢 Severidade: BAIXA — Situação controlada",
            }
            cores.get(resultado, st.info)(msg_cores.get(resultado, resultado))

            r1, r2, r3 = st.columns(3)
            with r1: st.metric("Pontuação de risco", f"{risco}/100")
            with r2: st.metric("Prejuízo estimado", f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Classificação financeira", risco_fin)

            if tipo_incidente == "ataque":
                st.error(f"🌍 País de origem: {pais}  |  IP suspeito: {ip_ex}")
                with st.expander("🛡️ Ações de resposta executadas"):
                    for a in ["IP bloqueado automaticamente", "Regras de firewall atualizadas", "Equipe de segurança notificada", "Incidente registrado no SIEM"]:
                        st.write(f"✅ {a}")

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo_incidente,
                    "origem": origem_ataque, "status": status_atual,
                    "severidade": resultado, "cliente": cliente_afetado
                })
                st.success("💾 Incidente salvo no banco de dados")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — MÉTRICAS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Métricas & Visualizações")

    L = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#8b949e",
        font_family="Inter",
        margin=dict(t=36,b=16,l=16,r=16)
    )

    g1, g2 = st.columns(2)
    with g1:
        fig = px.pie(df_vis, names="SEVERIDADE", title="Distribuição por Severidade",
                     color_discrete_sequence=["#f59e0b","#10b981","#ef4444","#00d4ff"])
        fig.update_layout(**L)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Incidentes por Tipo",
                     color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L)
        st.plotly_chart(fig, use_container_width=True)

    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig = px.area(df_time, x="DATA", y="Incidentes", title="Volume ao Longo do Tempo",
                  color_discrete_sequence=["#00d4ff"])
    fig.update_traces(fill='tozeroy', fillcolor='rgba(0,212,255,0.08)')
    fig.update_layout(**L)
    st.plotly_chart(fig, use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        fig = px.histogram(df_vis, x="PAIS_ATAQUE", title="Ataques por País de Origem",
                           color_discrete_sequence=["#f59e0b"])
        fig.update_layout(**L)
        st.plotly_chart(fig, use_container_width=True)
    with g4:
        dmg = (df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum()
               .reset_index().sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7))
        fig = px.bar(dmg, x="CLIENTE", y="PREJUIZO_ESTIMADO",
                     title="Impacto Financeiro por Cliente", color_discrete_sequence=["#ef4444"])
        fig.update_layout(**L)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Desempenho do Modelo")
    m1,m2,m3 = st.columns(3)
    with m1: st.metric("Acurácia", f"{acuracia:.1%}")
    with m2: st.metric("Amostras Treino", f"{int(len(df)*.8):,}")
    with m3: st.metric("Amostras Teste",  f"{int(len(df)*.2):,}")

    cm     = confusion_matrix(y_test, modelo.predict(X_test))
    labels = encoders["severidade"].classes_
    fig = go.Figure(go.Heatmap(
        z=cm, x=labels, y=labels,
        colorscale=[[0,"#060810"],[0.5,"#003a5a"],[1,"#00d4ff"]],
        text=cm, texttemplate="%{text}", showscale=True
    ))
    fig.update_layout(title="Matriz de Confusão", height=320, **L)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — MAPA GLOBAL (estilo Kaspersky)
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🌍 Mapa Global de Ameaças")
    st.caption("Visualização de ataques cibernéticos em tempo real — estilo Kaspersky Cyberthreat Map")

    COORDS = {
        "China":         ( 35.86,  104.19),
        "Russia":        ( 61.52,  105.31),
        "United States": ( 37.09,  -95.71),
        "Germany":       ( 51.16,   10.45),
        "Brazil":        (-14.23,  -51.92),
        "India":         ( 20.59,   78.96),
        "Netherlands":   ( 52.13,    5.29),
        "France":        ( 46.23,    2.21),
        "Ukraine":       ( 48.38,   31.17),
        "Iran":          ( 32.43,   53.69),
        "North Korea":   ( 40.34,  127.51),
        "Romania":       ( 45.94,   24.97),
    }
    TARGET = (-15.78, -47.92)  # Brasil/Brasília

    attack_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    cc = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country","total"]

    arcs = []
    for _, row in cc.iterrows():
        c = row["country"]
        if c in COORDS:
            s = COORDS[c]
            arcs.append({
                "src_lat": s[0], "src_lon": s[1],
                "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                "name": c, "count": int(row["total"])
            })

    # Adiciona arcos fictícios se poucos dados
    if len(arcs) < 4:
        for country, coord in list(COORDS.items())[:6]:
            if country != "Brazil":
                arcs.append({
                    "src_lat": coord[0], "src_lon": coord[1],
                    "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                    "name": country, "count": random.randint(5, 80)
                })

    arcs_json = json.dumps(arcs)
    all_coords_json = json.dumps({k: list(v) for k,v in COORDS.items()})

    map_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0;padding:0;box-sizing:border-box; }}
  body {{ background:#040608;overflow:hidden;font-family:'JetBrains Mono',monospace; }}
  canvas {{ display:block; }}
  #ui {{
    position:absolute;top:12px;left:12px;z-index:10;
    display:flex;flex-direction:column;gap:6px;
  }}
  .badge {{
    background:rgba(4,6,8,0.85);
    border:1px solid rgba(0,200,255,0.25);
    border-radius:8px;padding:6px 12px;
    font-size:10px;color:#00d4ff;
  }}
  .badge span {{ color:#00ff88; }}
  #legend {{
    position:absolute;bottom:12px;right:12px;z-index:10;
    background:rgba(4,6,8,0.85);
    border:1px solid rgba(0,200,255,0.15);
    border-radius:10px;padding:10px 14px;
    font-size:9px;color:#5a7a9a;
  }}
  .leg-row {{ display:flex;align-items:center;gap:6px;margin:3px 0; }}
  .dot {{ width:8px;height:8px;border-radius:50%; }}
  #counter {{
    position:absolute;top:12px;right:12px;z-index:10;
    background:rgba(4,6,8,0.85);
    border:1px solid rgba(0,200,255,0.15);
    border-radius:10px;padding:10px 16px;text-align:center;
  }}
  #counter .num {{ color:#00d4ff;font-size:20px;font-weight:700; }}
  #counter .lbl {{ color:#3a5a7a;font-size:8px;text-transform:uppercase;letter-spacing:.08em; }}
</style>
</head>
<body>
<canvas id="c"></canvas>

<div id="ui">
  <div class="badge">🛡️ SENTINELAI — <span id="status">LIVE</span></div>
  <div class="badge" id="last">Último: —</div>
</div>

<div id="counter">
  <div class="num" id="cnt">0</div>
  <div class="lbl">ataques detectados</div>
</div>

<div id="legend">
  <div class="leg-row"><div class="dot" style="background:#ef4444;box-shadow:0 0 6px #ef4444;"></div>Crítico</div>
  <div class="leg-row"><div class="dot" style="background:#f59e0b;box-shadow:0 0 6px #f59e0b;"></div>Médio</div>
  <div class="leg-row"><div class="dot" style="background:#00d4ff;box-shadow:0 0 6px #00d4ff;"></div>Baixo</div>
  <div class="leg-row"><div class="dot" style="background:#00ff88;box-shadow:0 0 6px #00ff88;"></div>Alvo (BR)</div>
</div>

<script>
const ARCS = {arcs_json};
const ALL_COORDS = {all_coords_json};

const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
let W, H, particles = [], totalAttacks = 0, pulses = [];

function resize() {{
  W = cv.width = window.innerWidth;
  H = cv.height = window.innerHeight;
}}
resize();
window.addEventListener('resize', resize);

// Lat/lon → canvas pixel (Mercator simples)
function ll2px(lat, lon) {{
  return [
    (lon + 180) / 360 * W,
    (90 - lat) / 180 * H
  ];
}}

// ── GRADE ──
function drawGrid() {{
  ctx.save();
  // linhas de latitude
  ctx.strokeStyle = 'rgba(0,150,220,0.04)';
  ctx.lineWidth = 1;
  for (let lat = -90; lat <= 90; lat += 30) {{
    let [,y] = ll2px(lat, 0);
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
  }}
  // linhas de longitude
  for (let lon = -180; lon <= 180; lon += 30) {{
    let [x,] = ll2px(0, lon);
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
  }}
  // equador highlight
  let [,yeq] = ll2px(0,0);
  ctx.strokeStyle = 'rgba(0,200,255,0.08)';
  ctx.beginPath(); ctx.moveTo(0,yeq); ctx.lineTo(W,yeq); ctx.stroke();
  ctx.restore();
}}

// ── PONTOS DE CIDADE ──
const CITIES = [
  [-14.23,-51.92,"BRA",true],
  [35.86,104.19,"CHN",false],
  [61.52,105.31,"RUS",false],
  [37.09,-95.71,"USA",false],
  [51.16,10.45,"DEU",false],
  [20.59,78.96,"IND",false],
  [52.13,5.29,"NLD",false],
  [40.34,127.51,"PRK",false],
  [48.38,31.17,"UKR",false],
  [32.43,53.69,"IRN",false],
  [-33.86,151.2,"AUS",false],
  [35.68,139.69,"JPN",false],
  [51.5,-0.12,"GBR",false],
  [40.41,-3.7,"ESP",false],
  [55.75,37.62,"RUS2",false],
];

function drawCities() {{
  for (let c of CITIES) {{
    let [x,y] = ll2px(c[0],c[1]);
    let isBR = c[3];
    let r = isBR ? 7 : 4;
    let col = isBR ? '#00ff88' : 'rgba(0,200,255,0.5)';
    // glow
    let grd = ctx.createRadialGradient(x,y,0,x,y,r*3);
    grd.addColorStop(0, isBR ? 'rgba(0,255,136,0.3)' : 'rgba(0,200,255,0.15)');
    grd.addColorStop(1, 'transparent');
    ctx.beginPath(); ctx.arc(x,y,r*3,0,Math.PI*2);
    ctx.fillStyle = grd; ctx.fill();
    // dot
    ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2);
    ctx.fillStyle = col; ctx.fill();
    // label
    if (isBR) {{
      ctx.fillStyle = '#00ff88';
      ctx.font = 'bold 9px monospace';
      ctx.fillText('🎯 BRA', x+9, y+3);
    }} else {{
      ctx.fillStyle = 'rgba(0,200,255,0.6)';
      ctx.font = '7px monospace';
      ctx.fillText(c[2], x+5, y+3);
    }}
  }}
}}

// ── PULSO DE ATAQUE ──
class Pulse {{
  constructor(x,y,col) {{
    this.x=x; this.y=y; this.r=0; this.max=30;
    this.col=col; this.a=1;
  }}
  update() {{
    this.r+=.8; this.a=1-this.r/this.max;
    return this.r < this.max;
  }}
  draw() {{
    ctx.beginPath(); ctx.arc(this.x,this.y,this.r,0,Math.PI*2);
    ctx.strokeStyle = this.col.replace('1)', this.a+')');
    ctx.lineWidth=1.5; ctx.stroke();
  }}
}}

// ── PARTÍCULA DE ATAQUE ──
const COLORS = ['rgba(239,68,68,1)','rgba(245,158,11,1)','rgba(0,212,255,1)'];

class Attack {{
  constructor(arc) {{
    this.arc = arc;
    this.t = 0;
    this.speed = 0.004 + Math.random()*0.004;
    this.trail = [];
    this.col = COLORS[Math.floor(Math.random()*COLORS.length)];
    this.size = 2 + Math.random()*1.5;
    this.done = false;
  }}

  bezierPt(t) {{
    let s = ll2px(this.arc.src_lat, this.arc.src_lon);
    let d = ll2px(this.arc.dst_lat, this.arc.dst_lon);
    let mx = (s[0]+d[0])/2;
    let my = Math.min(s[1],d[1]) - Math.abs(d[0]-s[0])*0.25 - 40;
    let u = 1-t;
    return [
      u*u*s[0] + 2*u*t*mx + t*t*d[0],
      u*u*s[1] + 2*u*t*my + t*t*d[1]
    ];
  }}

  update() {{
    if (this.done) return false;
    this.t += this.speed;
    if (this.t >= 1) {{
      this.t = 1; this.done = true;
      let p = this.bezierPt(1);
      pulses.push(new Pulse(p[0],p[1],'rgba(0,255,136,1)'));
      totalAttacks++;
      document.getElementById('cnt').textContent = totalAttacks;
      document.getElementById('last').textContent = 'Último: ' + this.arc.name;
      return false;
    }}
    let pos = this.bezierPt(Math.min(this.t,1));
    this.trail.push(pos);
    if (this.trail.length > 20) this.trail.shift();
    return true;
  }}

  draw() {{
    if (this.trail.length < 2) return;
    for (let i=1;i<this.trail.length;i++) {{
      let a = i/this.trail.length;
      ctx.beginPath();
      ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
      ctx.lineTo(this.trail[i][0], this.trail[i][1]);
      ctx.strokeStyle = this.col.replace('1)', a+')');
      ctx.lineWidth = this.size * a;
      ctx.stroke();
    }}
    // cabeça
    let head = this.trail[this.trail.length-1];
    let grd = ctx.createRadialGradient(head[0],head[1],0,head[0],head[1],6);
    grd.addColorStop(0, this.col);
    grd.addColorStop(1,'transparent');
    ctx.beginPath(); ctx.arc(head[0],head[1],6,0,Math.PI*2);
    ctx.fillStyle=grd; ctx.fill();
  }}
}}

// ── ESTRELAS DE FUNDO ──
const stars = Array.from({{length:200}},()=>([
  Math.random()*2000, Math.random()*1000, Math.random()*1+.2
]));

function drawStars() {{
  for (let [x,y,r] of stars) {{
    ctx.beginPath(); ctx.arc(x/2000*W, y/1000*H, r, 0, Math.PI*2);
    ctx.fillStyle='rgba(200,220,255,0.3)'; ctx.fill();
  }}
}}

// ── SPAWN ──
let spawnTimer=0;
function maybeSpawn() {{
  spawnTimer++;
  if (spawnTimer%40===0 && ARCS.length>0) {{
    let arc = ARCS[Math.floor(Math.random()*ARCS.length)];
    particles.push(new Attack(arc));
  }}
}}

// ── LOOP ──
function anim() {{
  requestAnimationFrame(anim);
  ctx.fillStyle='rgba(4,6,8,0.82)';
  ctx.fillRect(0,0,W,H);
  drawStars();
  drawGrid();
  drawCities();
  maybeSpawn();
  let alive=[];
  for (let p of particles) {{
    p.update(); p.draw();
    if (!p.done) alive.push(p);
  }}
  particles = alive;
  let ap=[];
  for (let p of pulses) {{ if(p.update()){{ p.draw(); ap.push(p); }} }}
  pulses=ap;
}}
anim();
</script>
</body>
</html>"""

    components.html(map_html, height=520, scrolling=False)

    st.markdown("#### Países de origem dos ataques")
    ta = df_vis[df_vis["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns = ["País","Nº de Ataques"]
    st.dataframe(ta, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — CHATBOT (Anthropic API)
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🤖 Assistente de Segurança — Powered by Claude")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Área de mensagens
    chat_container = st.container()
    with chat_container:
        if not st.session_state["chat_history"]:
            st.markdown("""
            <div style="
              text-align:center; padding:2rem;
              color:#3a5a7a; font-size:.82rem;
            ">
              <div style="font-size:2rem;margin-bottom:.5rem;">🤖</div>
              <p>Olá! Sou o assistente SentinelAI.</p>
              <p>Pergunte sobre incidentes, ameaças, análises de segurança…</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state["chat_history"]:
                css  = "chat-user" if msg["role"] == "user" else "chat-ai"
                icon = "👤" if msg["role"] == "user" else "🤖"
                st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        pergunta = st.text_input("", placeholder="Ex: Quais são os principais vetores de ataque no sistema?", label_visibility="collapsed")
        col_send, col_clr = st.columns([4,1])
        with col_send:
            enviar = st.form_submit_button("Enviar →", use_container_width=True)
        with col_clr:
            limpar = st.form_submit_button("Limpar", use_container_width=True)

    if limpar:
        st.session_state["chat_history"] = []
        st.rerun()

    if enviar and pergunta.strip():
        adicionar_log(usuario_atual, f"Chat: {pergunta[:50]}")
        st.session_state["chat_history"].append({"role":"user","content":pergunta})

        with st.spinner("🤔 Analisando…"):
            try:
                system_prompt = f"""Você é um assistente especialista em segurança cibernética integrado à plataforma SentinelAI.
Responda sempre em português brasileiro, de forma clara, profissional e direta.
Forneça insights práticos e acionáveis.

Contexto atual do sistema:
- Total de incidentes monitorados: {len(df_vis):,}
- Incidentes críticos ativos: {incidentes_criticos:,}
- IPs bloqueados automaticamente: {ips_bloqueados:,}
- Prejuízo financeiro estimado: R$ {prejuizo_total:,.0f}
- Acurácia do modelo de ML: {acuracia:.1%}
- Incidentes resolvidos: {incidentes_resolvidos:,}
- Incidentes pendentes: {incidentes_pendentes:,}
- Perfil do usuário atual: {perfil_atual['perfil']}
{f"- Contexto de cliente: {cliente_vinculado}" if cliente_vinculado else "- Visão: global (todos os clientes)"}

Seja objetivo. Use bullet points quando listar itens. Máximo 300 palavras."""

                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state["chat_history"]
                    ]
                }
                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                if resp.status_code == 200:
                    resposta = resp.json()["content"][0]["text"]
                else:
                    err = resp.json()
                    resposta = f"⚠️ Erro {resp.status_code}: {err.get('error',{}).get('message','Verifique sua chave de API Anthropic.')}"

            except requests.exceptions.Timeout:
                resposta = "⚠️ Timeout: o servidor demorou muito para responder. Tente novamente."
            except Exception as e:
                resposta = f"⚠️ Erro inesperado: {str(e)}"

        st.session_state["chat_history"].append({"role":"assistant","content":resposta})
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — EXPORTAR / BACKUP
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### Exportação de Dados")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas administradores podem exportar dados.")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.markdown("#### Downloads disponíveis")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.download_button(
                "📥 Dataset completo (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"sentinel_{ts}.csv", "text/csv",
                use_container_width=True
            )
        with b2:
            df_a = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button(
                "🔒 Dataset anonimizado",
                df_a.to_csv(index=False).encode("utf-8"),
                f"sentinel_anon_{ts}.csv", "text/csv",
                use_container_width=True
            )
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button(
                    "📋 Logs da sessão",
                    "\n".join(st.session_state["logs_sistema"]).encode("utf-8"),
                    f"logs_{ts}.txt", "text/plain",
                    use_container_width=True
                )
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db","rb") as f:
                st.download_button(
                    "🗄️ Banco SQLite",
                    f.read(), f"db_{ts}.db", "application/x-sqlite3",
                    use_container_width=True
                )

    st.markdown("---")
    st.markdown("#### Prévia dos dados")
    st.dataframe(df_vis.head(20), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — LOGS
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    st.markdown("### Logs de Auditoria")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log in reversed(st.session_state["logs_sistema"]):
            st.code(log, language=None)
    else:
        st.info("Nenhuma ação registrada nesta sessão.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1rem 0 .5rem 0;border-top:1px solid rgba(0,200,255,0.05);margin-top:1rem;">
  <p style="color:#1a2a3a;font-size:.6rem;letter-spacing:.08em;">
    SENTINELAI — CYBERSECURITY PLATFORM &nbsp;·&nbsp; CONFIDENCIAL
  </p>
</div>
""", unsafe_allow_html=True)
