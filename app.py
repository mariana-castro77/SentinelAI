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
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ─── BANCO DE DADOS ───────────────────────────────────────────────────────────

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
    except: pass

def salvar_incidente_sqlite(conn, d):
    try:
        conn.cursor().execute(
            "INSERT INTO incidentes_registrados (usuario,tipo_incidente,origem,status,severidade_prevista,cliente) VALUES (?,?,?,?,?,?)",
            (d["usuario"],d["tipo"],d["origem"],d["status"],d["severidade"],d["cliente"]))
        conn.commit()
    except: pass

def salvar_log_sqlite(conn, usuario, acao):
    try:
        conn.cursor().execute("INSERT INTO logs_sistema (usuario,acao) VALUES (?,?)", (usuario, acao))
        conn.commit()
    except: pass

# ─── CONFIG ───────────────────────────────────────────────────────────────────

st.set_page_config(page_title="SentinelAI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;}
.stApp{background:#060b18;}
[data-testid="stHeader"]{background:rgba(0,0,0,0);}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#060b18 0%,#0a1128 100%);border-right:1px solid rgba(0,212,255,0.08);}
.block-container{padding:1.2rem 1.5rem;max-width:100%;}
div[data-testid="metric-container"]{background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(6,11,24,0.9));border:1px solid rgba(0,212,255,0.12);border-radius:14px;padding:1rem 1.2rem;transition:all .25s ease;position:relative;overflow:hidden;}
div[data-testid="metric-container"]::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.4),transparent);}
div[data-testid="metric-container"]:hover{border-color:rgba(0,212,255,0.35);transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,212,255,0.08);}
[data-testid="stMetricLabel"]{color:#5a7a9e!important;font-size:.65rem!important;text-transform:uppercase;letter-spacing:.1em;font-weight:500;}
[data-testid="stMetricValue"]{color:#00d4ff!important;font-size:1.6rem!important;font-weight:700;font-family:'JetBrains Mono',monospace;}
div.stButton>button{background:linear-gradient(135deg,#0077b6,#00b4d8);color:white;border-radius:10px;border:none;padding:.55rem 1rem;font-weight:600;font-size:.82rem;transition:all .2s ease;width:100%;}
div.stButton>button:hover{background:linear-gradient(135deg,#0096c7,#00d4ff);transform:translateY(-1px);box-shadow:0 4px 20px rgba(0,180,216,.3);}
.chat-user{background:linear-gradient(135deg,#0077b6,#00b4d8);border-radius:18px 18px 4px 18px;padding:.75rem 1rem;margin:.5rem 0;margin-left:auto;max-width:82%;width:fit-content;color:white;font-size:.84rem;line-height:1.5;}
.chat-ai{background:rgba(10,17,40,.95);border:1px solid rgba(0,212,255,.18);border-radius:18px 18px 18px 4px;padding:.75rem 1rem;margin:.5rem 0;max-width:82%;width:fit-content;color:#d0dce8;font-size:.84rem;line-height:1.5;}
.sentinel-header{background:linear-gradient(135deg,rgba(0,180,216,.06),rgba(0,50,100,.04));border:1px solid rgba(0,212,255,.12);border-radius:18px;padding:1.4rem 1.8rem;margin-bottom:1.5rem;position:relative;overflow:hidden;}
.sentinel-header::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,.5),transparent);}
.badge-online{display:inline-block;background:rgba(0,255,100,.08);border:1px solid rgba(0,255,100,.25);color:#00ff64;padding:.25rem .75rem;border-radius:20px;font-size:.65rem;font-weight:600;letter-spacing:.08em;font-family:'JetBrains Mono',monospace;}
.badge-db{display:inline-block;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);color:#00d4ff;padding:.25rem .75rem;border-radius:20px;font-size:.65rem;font-weight:600;}
.stTabs [data-baseweb="tab-list"]{background:rgba(10,17,40,.8);border-radius:14px;padding:.3rem;gap:.2rem;border:1px solid rgba(0,212,255,.08);}
.stTabs [data-baseweb="tab"]{border-radius:10px;color:#5a7a9e;font-weight:500;padding:.45rem 1rem;font-size:.8rem;transition:all .2s;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,180,216,.18),rgba(0,119,182,.1));color:#00d4ff!important;border:1px solid rgba(0,212,255,.2);}
input,textarea,select{background:rgba(10,17,40,.9)!important;border:1px solid rgba(0,212,255,.15)!important;border-radius:10px!important;color:white!important;}
hr{border-color:rgba(0,212,255,.07);margin:1rem 0;}
code{background:rgba(0,212,255,.08);color:#00d4ff;border-radius:4px;padding:.1rem .4rem;font-family:'JetBrains Mono',monospace;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-thumb{background:rgba(0,212,255,.2);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ─── UTILS ────────────────────────────────────────────────────────────────────

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
    if ip == "Nenhum" or pd.isna(ip): return "***.***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

# ─── POLÍTICA DE PRIVACIDADE ──────────────────────────────────────────────────

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(0,180,216,.06),rgba(0,50,100,.04));
                    border:1px solid rgba(0,212,255,.15);border-radius:20px;
                    padding:2.5rem 2rem;margin:3rem 0;text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔒</div>
            <h2 style="color:#00d4ff;margin-bottom:.8rem;">Política de Privacidade</h2>
            <p style="color:#8b9dc3;font-size:.88rem;line-height:1.6;">
                Esta plataforma está em conformidade com a <strong style="color:#00d4ff;">LGPD (Lei 13.709/2018)</strong>.<br>
                Seus dados estão protegidos e não são compartilhados com terceiros.
            </p>
        </div>""", unsafe_allow_html=True)
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

# ─── LOGIN / LANDING PAGE ─────────────────────────────────────────────────────

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    # Esconder sidebar e padding no login
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none;}
    .block-container{padding:0!important;max-width:100%!important;}
    header{display:none!important;}
    </style>
    """, unsafe_allow_html=True)

    landing_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*{margin:0;padding:0;box-sizing:border-box;}
:root{
  --cyan:#00d4ff;
  --cyan-dim:rgba(0,212,255,.15);
  --cyan-glow:rgba(0,212,255,.08);
  --bg:#060b18;
  --bg2:#0a1128;
  --text:#e2eaf4;
  --muted:#5a7a9e;
}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;overflow-x:hidden;}

/* ── Canvas particles ── */
#bg-canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;}

/* ── Sections ── */
section{position:relative;z-index:1;}

/* ══ HERO ══════════════════════════════════════════════════════════════════ */
#hero{
  min-height:100vh;
  display:flex;align-items:center;justify-content:center;
  text-align:center;
  padding:2rem 1.5rem;
}
.hero-inner{max-width:780px;width:100%;}

.shield-wrap{
  display:inline-flex;align-items:center;justify-content:center;
  width:96px;height:96px;
  background:radial-gradient(circle,rgba(0,180,216,.18) 0%,rgba(0,50,100,.06) 70%);
  border:1px solid rgba(0,212,255,.25);
  border-radius:50%;
  font-size:2.8rem;
  margin-bottom:1.6rem;
  animation:float 4s ease-in-out infinite;
  box-shadow:0 0 40px rgba(0,212,255,.12);
}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}

.badge-live{
  display:inline-flex;align-items:center;gap:6px;
  background:rgba(0,255,100,.07);
  border:1px solid rgba(0,255,100,.2);
  color:#00ff64;
  padding:.3rem .9rem;border-radius:30px;
  font-size:.7rem;font-weight:600;
  letter-spacing:.1em;font-family:'JetBrains Mono',monospace;
  margin-bottom:1.4rem;
}
.badge-live span{
  width:7px;height:7px;border-radius:50%;background:#00ff64;
  animation:blink 1.4s ease-in-out infinite;
}
@keyframes blink{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(0,255,100,.5);}50%{opacity:.6;box-shadow:0 0 0 5px rgba(0,255,100,0);}}

h1.hero-title{
  font-size:clamp(2.8rem,6vw,5rem);
  font-weight:800;
  line-height:1.1;
  letter-spacing:-.02em;
  margin-bottom:.8rem;
  background:linear-gradient(135deg,#ffffff 30%,#00d4ff 70%,#0077b6 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{
  font-size:clamp(.95rem,2vw,1.15rem);
  color:var(--muted);
  line-height:1.7;
  max-width:540px;
  margin:0 auto 2.2rem;
  font-weight:400;
}

/* stats row */
.stats-row{
  display:flex;justify-content:center;gap:1rem;
  flex-wrap:wrap;margin-bottom:2.5rem;
}
.stat-chip{
  background:rgba(0,212,255,.05);
  border:1px solid rgba(0,212,255,.12);
  border-radius:12px;padding:.7rem 1.2rem;
  text-align:center;min-width:110px;
}
.stat-chip .num{
  color:var(--cyan);
  font-size:1.4rem;font-weight:700;
  font-family:'JetBrains Mono',monospace;
  display:block;
}
.stat-chip .lbl{color:var(--muted);font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;}

.scroll-hint{
  margin-top:1.8rem;
  color:var(--muted);font-size:.75rem;
  display:flex;flex-direction:column;align-items:center;gap:6px;
  animation:fadeInUp 1s ease .8s both;
}
.scroll-arrow{
  width:22px;height:22px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);
  transform:rotate(45deg);
  animation:scrollBounce 1.5s ease-in-out infinite;
}
@keyframes scrollBounce{0%,100%{transform:rotate(45deg) translateY(0);}50%{transform:rotate(45deg) translateY(5px);}}

/* ══ FEATURES ══════════════════════════════════════════════════════════════ */
#features{
  padding:5rem 1.5rem;
  background:linear-gradient(180deg,var(--bg) 0%,var(--bg2) 50%,var(--bg) 100%);
}
.section-label{
  text-align:center;
  color:var(--cyan);font-size:.7rem;
  letter-spacing:.18em;text-transform:uppercase;
  font-family:'JetBrains Mono',monospace;
  margin-bottom:.6rem;
}
.section-title{
  text-align:center;
  font-size:clamp(1.6rem,3.5vw,2.4rem);font-weight:700;
  color:#fff;margin-bottom:.6rem;
}
.section-desc{text-align:center;color:var(--muted);font-size:.9rem;margin-bottom:3rem;max-width:480px;margin-left:auto;margin-right:auto;}

.features-grid{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:1.2rem;max-width:960px;margin:0 auto;
}
.feat-card{
  background:linear-gradient(135deg,rgba(0,212,255,.04),rgba(6,11,24,.9));
  border:1px solid rgba(0,212,255,.1);
  border-radius:16px;padding:1.6rem;
  transition:all .3s ease;
  position:relative;overflow:hidden;
}
.feat-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,212,255,.3),transparent);
}
.feat-card:hover{
  border-color:rgba(0,212,255,.3);
  transform:translateY(-4px);
  box-shadow:0 12px 40px rgba(0,212,255,.07);
}
.feat-icon{font-size:1.8rem;margin-bottom:.9rem;}
.feat-title{color:#fff;font-weight:600;font-size:.95rem;margin-bottom:.4rem;}
.feat-desc{color:var(--muted);font-size:.82rem;line-height:1.6;}

/* ══ CLIENTS ═══════════════════════════════════════════════════════════════ */
#clients{padding:4rem 1.5rem;text-align:center;}
.clients-row{
  display:flex;justify-content:center;align-items:center;
  gap:1.5rem;flex-wrap:wrap;margin-top:2rem;
}
.client-chip{
  background:rgba(0,212,255,.04);
  border:1px solid rgba(0,212,255,.1);
  border-radius:10px;padding:.6rem 1.4rem;
  color:var(--muted);font-size:.82rem;font-weight:500;
  transition:all .25s;
}
.client-chip:hover{color:var(--cyan);border-color:rgba(0,212,255,.3);}

/* ══ LOGIN FORM ═════════════════════════════════════════════════════════════ */
#login-section{
  padding:5rem 1.5rem 6rem;
  display:flex;flex-direction:column;align-items:center;
}
.login-card{
  background:linear-gradient(135deg,rgba(0,212,255,.04) 0%,rgba(10,17,40,.98) 100%);
  border:1px solid rgba(0,212,255,.18);
  border-radius:24px;
  padding:2.5rem 2rem;
  width:100%;max-width:400px;
  position:relative;overflow:hidden;
  box-shadow:0 32px 80px rgba(0,0,0,.5),0 0 60px rgba(0,212,255,.04);
}
.login-card::before{
  content:'';position:absolute;top:0;left:10%;right:10%;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,212,255,.5),transparent);
}
.login-card h2{
  color:#fff;font-size:1.25rem;font-weight:700;
  text-align:center;margin-bottom:.3rem;
}
.login-card p{color:var(--muted);font-size:.8rem;text-align:center;margin-bottom:1.6rem;}

.inp-group{margin-bottom:1rem;}
.inp-group label{display:block;color:var(--muted);font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.4rem;}
.inp-group input{
  width:100%;background:rgba(6,11,24,.9);
  border:1px solid rgba(0,212,255,.15);
  border-radius:10px;padding:.7rem 1rem;
  color:#fff;font-size:.88rem;font-family:'Inter',sans-serif;
  outline:none;transition:border-color .2s,box-shadow .2s;
}
.inp-group input:focus{border-color:var(--cyan);box-shadow:0 0 0 3px rgba(0,212,255,.08);}
.inp-group input::placeholder{color:rgba(90,122,158,.5);}

.btn-login{
  width:100%;padding:.75rem;margin-top:.4rem;
  background:linear-gradient(135deg,#0077b6,#00b4d8);
  color:#fff;font-weight:700;font-size:.9rem;
  border:none;border-radius:12px;cursor:pointer;
  transition:all .2s;letter-spacing:.02em;
  font-family:'Inter',sans-serif;
}
.btn-login:hover{background:linear-gradient(135deg,#0096c7,#00d4ff);transform:translateY(-1px);box-shadow:0 8px 24px rgba(0,180,216,.3);}
.btn-login:active{transform:translateY(0);}

.error-msg{
  background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.25);
  color:#fca5a5;border-radius:8px;padding:.6rem .9rem;
  font-size:.8rem;margin-top:.8rem;text-align:center;display:none;
}

.login-hint{
  margin-top:1.2rem;text-align:center;
  color:var(--muted);font-size:.72rem;
  font-family:'JetBrains Mono',monospace;
}

/* ══ ANIMATIONS ═════════════════════════════════════════════════════════════ */
.reveal{opacity:0;transform:translateY(28px);transition:opacity .7s ease,transform .7s ease;}
.reveal.visible{opacity:1;transform:translateY(0);}

@keyframes fadeInUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
.hero-inner>*{animation:fadeInUp .7s ease both;}
.hero-inner>*:nth-child(1){animation-delay:.1s;}
.hero-inner>*:nth-child(2){animation-delay:.2s;}
.hero-inner>*:nth-child(3){animation-delay:.3s;}
.hero-inner>*:nth-child(4){animation-delay:.4s;}
.hero-inner>*:nth-child(5){animation-delay:.5s;}

/* ── Responsive ── */
@media(max-width:600px){
  .stats-row{gap:.7rem;}
  .stat-chip{min-width:90px;padding:.5rem .8rem;}
  .stat-chip .num{font-size:1.1rem;}
  .login-card{padding:2rem 1.4rem;}
  .features-grid{grid-template-columns:1fr;}
}
</style>
</head>
<body>

<canvas id="bg-canvas"></canvas>

<!-- ══ HERO ══════════════════════════════════════════════════════════════════ -->
<section id="hero">
  <div class="hero-inner">
    <div class="shield-wrap">🛡️</div>
    <div class="badge-live"><span></span>SISTEMA ATIVO — 24/7</div>
    <h1 class="hero-title">SentinelAI</h1>
    <p class="hero-sub">
      Plataforma de Inteligência contra Ameaças Cibernéticas.<br>
      Detecção em tempo real, análise com IA e resposta automatizada.
    </p>
    <div class="stats-row">
      <div class="stat-chip"><span class="num" id="s1">0</span><span class="lbl">Ameaças/dia</span></div>
      <div class="stat-chip"><span class="num" id="s2">0</span><span class="lbl">IPs Bloqueados</span></div>
      <div class="stat-chip"><span class="num" id="s3">0%</span><span class="lbl">Acurácia IA</span></div>
      <div class="stat-chip"><span class="num" id="s4">0</span><span class="lbl">Clientes</span></div>
    </div>
    <div class="scroll-hint">
      <span>Saiba mais</span>
      <div class="scroll-arrow"></div>
    </div>
  </div>
</section>

<!-- ══ FEATURES ══════════════════════════════════════════════════════════════ -->
<section id="features">
  <p class="section-label reveal">Capacidades</p>
  <h2 class="section-title reveal">Proteção Inteligente em Cada Camada</h2>
  <p class="section-desc reveal">Monitoramento contínuo com machine learning para detectar, classificar e responder a ameaças antes que causem dano.</p>
  <div class="features-grid">
    <div class="feat-card reveal">
      <div class="feat-icon">🤖</div>
      <div class="feat-title">IA Preditiva</div>
      <div class="feat-desc">Modelo de classificação treinado para prever a severidade de incidentes com alta acurácia antes mesmo da escalada.</div>
    </div>
    <div class="feat-card reveal">
      <div class="feat-icon">🌍</div>
      <div class="feat-title">Mapa de Ameaças</div>
      <div class="feat-desc">Visualização global em tempo real de ataques cibernéticos com rastreamento de origem e volume por país.</div>
    </div>
    <div class="feat-card reveal">
      <div class="feat-icon">⚡</div>
      <div class="feat-title">Resposta Automática</div>
      <div class="feat-desc">Bloqueio de IPs, atualização de firewall e notificação de equipes em milissegundos após detecção.</div>
    </div>
    <div class="feat-card reveal">
      <div class="feat-icon">🔒</div>
      <div class="feat-title">LGPD Compliance</div>
      <div class="feat-desc">Controle granular de acesso por perfil, mascaramento de dados sensíveis e logs auditáveis.</div>
    </div>
    <div class="feat-card reveal">
      <div class="feat-icon">📊</div>
      <div class="feat-title">Dashboards Executivos</div>
      <div class="feat-desc">Métricas de impacto financeiro, volume de ameaças e desempenho do modelo em painéis interativos.</div>
    </div>
    <div class="feat-card reveal">
      <div class="feat-icon">💬</div>
      <div class="feat-title">Assistente IA</div>
      <div class="feat-desc">SentinelBot responde perguntas sobre incidentes, clientes e tendências usando os dados do sistema em tempo real.</div>
    </div>
  </div>
</section>

<!-- ══ CLIENTS ════════════════════════════════════════════════════════════════ -->
<section id="clients">
  <p class="section-label reveal">Clientes Protegidos</p>
  <h2 class="section-title reveal">Confiado por Líderes do Mercado</h2>
  <div class="clients-row reveal">
    <div class="client-chip">🟣 Nubank</div>
    <div class="client-chip">🟡 Mercado Livre</div>
    <div class="client-chip">🔴 Santander</div>
    <div class="client-chip">🔵 + Outros</div>
  </div>
</section>

<!-- ══ LOGIN ══════════════════════════════════════════════════════════════════ -->
<section id="login-section">
  <p class="section-label reveal" style="margin-bottom:1rem;">Acesso Seguro</p>
  <div class="login-card reveal">
    <h2>Entrar na Plataforma</h2>
    <p>Credenciais corporativas requeridas</p>
    <div class="inp-group">
      <label>Usuário</label>
      <input type="text" id="user-input" placeholder="Digite seu usuário" autocomplete="username">
    </div>
    <div class="inp-group">
      <label>Senha</label>
      <input type="password" id="pass-input" placeholder="••••••••" autocomplete="current-password">
    </div>
    <button class="btn-login" id="login-btn" onclick="doLogin()">🔐 Entrar</button>
    <div class="error-msg" id="err-msg">❌ Usuário ou senha incorretos</div>
    <div class="login-hint">Acesso restrito a usuários autorizados</div>
  </div>
</section>

<script>
/* ── Particles background ── */
var canvas = document.getElementById('bg-canvas');
var ctx    = canvas.getContext('2d');
var W, H, dots = [], lines = [];

function resize(){
  W = canvas.width  = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
resize();
window.addEventListener('resize', resize);

for(var i=0;i<70;i++){
  dots.push({
    x:Math.random()*2, y:Math.random(),
    vx:(Math.random()-.5)*.0003, vy:(Math.random()-.5)*.0002,
    r:Math.random()*.9+.3, a:Math.random()*.4+.1
  });
}

function drawParticles(){
  ctx.clearRect(0,0,W,H);
  for(var i=0;i<dots.length;i++){
    var d=dots[i];
    d.x+=d.vx; d.y+=d.vy;
    if(d.x<0)d.x=2; if(d.x>2)d.x=0;
    if(d.y<0)d.y=1; if(d.y>1)d.y=0;
    var px=d.x%1*W, py=d.y*H;
    ctx.beginPath();
    ctx.arc(px,py,d.r,0,Math.PI*2);
    ctx.fillStyle='rgba(0,180,255,'+d.a+')';
    ctx.fill();
    for(var j=i+1;j<dots.length;j++){
      var d2=dots[j];
      var px2=d2.x%1*W, py2=d2.y*H;
      var dist=Math.hypot(px-px2,py-py2);
      if(dist<130){
        ctx.beginPath();
        ctx.moveTo(px,py); ctx.lineTo(px2,py2);
        ctx.strokeStyle='rgba(0,180,255,'+(0.04*(1-dist/130))+')';
        ctx.lineWidth=.5; ctx.stroke();
      }
    }
  }
  requestAnimationFrame(drawParticles);
}
drawParticles();

/* ── Counter animation ── */
function animCount(id, target, suffix, dur){
  var el=document.getElementById(id), start=0, step=target/60;
  var timer=setInterval(function(){
    start=Math.min(start+step, target);
    el.textContent=Math.floor(start).toLocaleString()+(suffix||'');
    if(start>=target) clearInterval(timer);
  }, dur/60);
}
setTimeout(function(){
  animCount('s1',1284,'',800);
  animCount('s2',3471,'',900);
  animCount('s3',94,'%',600);
  animCount('s4',12,'',500);
},400);

/* ── Scroll reveal ── */
var reveals = document.querySelectorAll('.reveal');
var observer = new IntersectionObserver(function(entries){
  entries.forEach(function(e){
    if(e.isIntersecting){ e.target.classList.add('visible'); }
  });
},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
reveals.forEach(function(r){ observer.observe(r); });

/* ── Parallax ── */
window.addEventListener('scroll', function(){
  var sy = window.scrollY;
  var hero = document.querySelector('.hero-inner');
  if(hero) hero.style.transform='translateY('+sy*.18+'px)';
});

/* ── Login — envia para Streamlit via URL ── */
function doLogin(){
  var u=document.getElementById('user-input').value.trim();
  var p=document.getElementById('pass-input').value;
  if(!u||!p){
    document.getElementById('err-msg').style.display='block';
    return;
  }
  /* Passa credenciais via query string para o Streamlit processar */
  var params=new URLSearchParams(window.location.search);
  params.set('_u', btoa(u));
  params.set('_p', btoa(p));
  window.location.search=params.toString();
}

/* Enter key */
document.addEventListener('keydown',function(e){
  if(e.key==='Enter') doLogin();
});
</script>
</body>
</html>
"""

    # Renderiza o HTML da landing page
    components.html(landing_html, height=3200, scrolling=True)

    # Captura parâmetros de login vindos do HTML
    params = st.query_params
    u_enc  = params.get("_u", "")
    p_enc  = params.get("_p", "")

    if u_enc and p_enc:
        try:
            import base64
            u = base64.b64decode(u_enc).decode()
            p = base64.b64decode(p_enc).decode()
            if autenticar(u, p):
                st.session_state["autenticado"]   = True
                st.session_state["usuario_atual"] = u
                st.query_params.clear()
                adicionar_log(u, "Login realizado")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos")
                st.query_params.clear()
        except Exception:
            st.query_params.clear()

    st.stop()

# ─── SESSÃO ───────────────────────────────────────────────────────────────────

usuario_atual = st.session_state["usuario_atual"]
perfil_atual  = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão iniciada")

if "sqlite_conn" not in st.session_state:
    st.session_state["sqlite_conn"] = conectar_sqlite()
    if st.session_state["sqlite_conn"]:
        inicializar_sqlite(st.session_state["sqlite_conn"])

sqlite_conn  = st.session_state["sqlite_conn"]
sqlite_ativo = sqlite_conn is not None

# ─── DADOS ────────────────────────────────────────────────────────────────────

@st.cache_data
def carregar_dados():
    df = pd.read_csv("dataset_final.csv").dropna(subset=["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS","NIVEL_AMEACA","RISCO_FINANCEIRO"]:
        if col in df.columns: df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo","origem","status","severidade"]}
    df["TIPO_ENC"]       = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"]     = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"]     = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"] = enc["severidade"].fit_transform(df["SEVERIDADE"])
    X = df[["TIPO_ENC","ORIGEM_ENC","TEMPO RESOLUÇÃO","STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.2,random_state=42)
    m = DecisionTreeClassifier(random_state=42); m.fit(Xtr,ytr)
    return df, enc, m, accuracy_score(yte,m.predict(Xte)), Xte, yte

df, encoders, modelo, acuracia, X_test, y_test = carregar_dados()
cliente_vinculado = perfil_atual["cliente_vinculado"]
df_vis = df[df["CLIENTE"]==cliente_vinculado].copy() if cliente_vinculado else df.copy()
salvar_backup_sessao(df_vis, usuario_atual, "Login")

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:1.2rem 0 .5rem;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:52px;height:52px;background:rgba(0,180,216,.1);
                  border:1px solid rgba(0,212,255,.2);border-radius:50%;font-size:1.6rem;">🛡️</div>
      <h3 style="color:#00d4ff;margin:.5rem 0 0;font-size:1.1rem;font-weight:700;">SentinelAI</h3>
      <p style="color:#3a5a7e;font-size:.62rem;letter-spacing:.15em;font-family:'JetBrains Mono',monospace;">CYBER INTELLIGENCE</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,.05);border:1px solid rgba(0,212,255,.1);border-radius:12px;padding:.9rem;margin:.5rem 0;">
      <p style="color:#3a5a7e;font-size:.6rem;letter-spacing:.1em;margin-bottom:.3rem;">PERFIL ATIVO</p>
      <p style="color:white;font-weight:600;font-size:.9rem;margin-bottom:.1rem;">{perfil_atual['perfil']}</p>
      <p style="color:#5a7a9e;font-size:.72rem;font-family:'JetBrains Mono',monospace;">@{usuario_atual}</p>
    </div>""", unsafe_allow_html=True)
    badge_db = ('<span class="badge-db">📁 SQLite Ativo</span>' if sqlite_ativo
                else '<span class="badge-db" style="border-color:rgba(255,68,68,.3);color:#ff4444;">⚠️ Offline</span>')
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='color:#3a5a7e;font-size:.65rem;letter-spacing:.1em;'>PERMISSÕES</p>", unsafe_allow_html=True)
    for nome, ativo in [("📊 Análise",perfil_atual["pode_analisar"]),("📤 Exportar",perfil_atual["pode_exportar"]),("👁️ Ver IPs",perfil_atual["ver_pii"])]:
        c,i = ("#00ff64","✓") if ativo else ("#ff4444","✗")
        st.markdown(f"<p style='color:{c};font-size:.75rem;margin:.2rem 0;'>{i} {nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,.05);border:1px solid rgba(0,212,255,.1);border-radius:12px;padding:.9rem;text-align:center;">
      <p style="color:#3a5a7e;font-size:.62rem;letter-spacing:.1em;">ACURÁCIA DO MODELO</p>
      <p style="color:#00d4ff;font-size:1.6rem;font-weight:700;font-family:'JetBrains Mono',monospace;">{acuracia:.1%}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado":False,"usuario_atual":None})
        st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="sentinel-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.8rem;">
    <div>
      <p style="color:#3a5a7e;font-size:.62rem;letter-spacing:.15em;font-family:'JetBrains Mono',monospace;margin-bottom:.3rem;">BEM-VINDO, {usuario_atual.upper()}</p>
      <h1 style="color:white;margin:0;font-size:1.5rem;font-weight:700;">Painel de Inteligência contra Ameaças</h1>
      <p style="color:#5a7a9e;margin-top:.3rem;font-size:.8rem;">
        {f"Visão do Cliente: <strong style='color:#00d4ff;'>{cliente_vinculado}</strong>" if cliente_vinculado else "Visão Global — Todos os Clientes"}
      </p>
    </div>
    <div style="text-align:right;">
      <span class="badge-online">● SISTEMA PROTEGIDO</span>
      <p style="color:#3a5a7e;font-size:.65rem;margin-top:.5rem;font-family:'JetBrains Mono',monospace;">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ─── MÉTRICAS ─────────────────────────────────────────────────────────────────

total_incidentes      = len(df_vis)
incidentes_criticos   = len(df_vis[df_vis["SEVERIDADE"]=="crítica"])
ips_bloqueados        = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
prejuizo_total        = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"]=="resolvido"])
incidentes_pendentes  = len(df_vis[df_vis["STATUS"]=="pendente"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.metric("Total Incidentes",   f"{total_incidentes:,}")
with c2: st.metric("Críticos",           f"{incidentes_criticos:,}")
with c3: st.metric("IPs Bloqueados",     f"{ips_bloqueados:,}")
with c4: st.metric("Resolvidos",         f"{incidentes_resolvidos:,}")
with c5: st.metric("Pendentes",          f"{incidentes_pendentes:,}")
with c6:
    pf = f"R$ {prejuizo_total:,.0f}".replace(",","X").replace(".",",").replace("X",".")
    st.metric("Prejuízo Estimado", pf)

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["🔍 Análise","📊 Métricas","🌍 Mapa de Ameaças","🤖 Assistente IA","💾 Backup","📋 Logs"])

# ════════════ TAB 1 — ANÁLISE ════════════════════════════════════════════════

with tab1:
    st.markdown("### Análise de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Seu perfil não tem permissão para realizar análises.")
    else:
        ca,cb = st.columns(2)
        with ca:
            tipo_incidente  = st.selectbox("Tipo de Incidente", encoders["tipo"].classes_)
            origem_ataque   = st.selectbox("Origem",            encoders["origem"].classes_)
            cliente_afetado = st.selectbox("Cliente",           sorted(df["CLIENTE"].unique()))
        with cb:
            tempo_resolucao = st.slider("Tempo de Resolução (min)", 1, 120, 30)
            status_atual    = st.selectbox("Status",            encoders["status"].classes_)
        if st.button("🚀 Iniciar Análise", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: {tipo_incidente}")
            with st.spinner("Analisando ameaça..."):
                time.sleep(1)
            entrada = pd.DataFrame({"TIPO_ENC":[encoders["tipo"].transform([tipo_incidente])[0]],
                                    "ORIGEM_ENC":[encoders["origem"].transform([origem_ataque])[0]],
                                    "TEMPO RESOLUÇÃO":[tempo_resolucao],
                                    "STATUS_ENC":[encoders["status"].transform([status_atual])[0]]})
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status_atual=="resolvido": resultado="baixa"
            elif tipo_incidente in ["ataque","falha servidor"]: resultado="crítica"
            elif tipo_incidente in ["lentidão","erro sistema"]: resultado=random.choice(["baixa","média"])
            risco=random.randint(10,99); prej_est=random.uniform(3000,30000)
            risco_fin="ALTO" if prej_est>15000 else ("MÉDIO" if prej_est>7000 else "BAIXO")
            ataques=df[df["TIPO INCIDENTE"]=="ataque"]
            if not ataques.empty:
                l=ataques.sample(1).iloc[0]
                ip_ex=l["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(l["IP_SUSPEITO"])
                pais=l["PAIS_ATAQUE"]
            else: ip_ex,pais="DESCONHECIDO","INTERNO"
            st.markdown("---")
            if resultado=="crítica":   st.error(f"🔴 Severidade: **{resultado.upper()}** — AÇÃO IMEDIATA")
            elif resultado=="média":   st.warning(f"🟡 Severidade: **{resultado.upper()}** — MONITORAR")
            else:                      st.success(f"🟢 Severidade: **{resultado.upper()}** — BAIXO RISCO")
            r1,r2,r3=st.columns(3)
            with r1: st.metric("Pontuação de Ameaça",f"{risco}/100")
            with r2: st.metric("Prejuízo Estimado",f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Risco Financeiro",risco_fin)
            if tipo_incidente=="ataque":
                st.error(f"🌍 Origem: **{pais}** | IP: `{ip_ex}`")
                with st.expander("🛡️ Resposta Automática"):
                    for a in ["✅ IP bloqueado","✅ Firewall atualizado","✅ Equipe notificada","✅ Logs capturados"]: st.write(a)
            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn,{"usuario":usuario_atual,"tipo":tipo_incidente,"origem":origem_ataque,"status":status_atual,"severidade":resultado,"cliente":cliente_afetado})
                st.success("💾 Incidente salvo")
            adicionar_log(usuario_atual,f"Análise concluída: {resultado}")

# ════════════ TAB 2 — MÉTRICAS ═══════════════════════════════════════════════

with tab2:
    st.markdown("### Painel de Métricas")
    L=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#8b9dc3",font_family="Inter")
    g1,g2=st.columns(2)
    with g1:
        fig=px.pie(df_vis,names="SEVERIDADE",title="Distribuição por Severidade",color_discrete_sequence=["#f59e0b","#10b981","#ef4444"])
        fig.update_layout(**L,title_font_color="#00d4ff"); st.plotly_chart(fig,use_container_width=True)
    with g2:
        vc=df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig=px.bar(vc,x="TIPO INCIDENTE",y="count",title="Incidentes por Tipo",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L,title_font_color="#00d4ff"); st.plotly_chart(fig,use_container_width=True)
    df_time=df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig=px.line(df_time,x="DATA",y="Incidentes",title="Volume ao Longo do Tempo",color_discrete_sequence=["#00d4ff"])
    fig.update_layout(**L,title_font_color="#00d4ff"); st.plotly_chart(fig,use_container_width=True)
    g3,g4=st.columns(2)
    with g3:
        fig=px.histogram(df_vis,x="PAIS_ATAQUE",title="Ataques por País",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L,title_font_color="#00d4ff"); st.plotly_chart(fig,use_container_width=True)
    with g4:
        dmg=df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index().sort_values("PREJUIZO_ESTIMADO",ascending=False).head(7)
        fig=px.bar(dmg,x="CLIENTE",y="PREJUIZO_ESTIMADO",title="Impacto Financeiro por Cliente",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L,title_font_color="#00d4ff"); st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Desempenho do Modelo")
    m1,m2,m3=st.columns(3)
    with m1: st.metric("Acurácia",f"{acuracia:.1%}")
    with m2: st.metric("Treino",f"{int(len(df)*.8):,}")
    with m3: st.metric("Teste",f"{int(len(df)*.2):,}")
    cm=confusion_matrix(y_test,modelo.predict(X_test)); labels=encoders["severidade"].classes_
    fig=go.Figure(go.Heatmap(z=cm,x=labels,y=labels,colorscale=[[0,"#060b18"],[1,"#00d4ff"]],text=cm,texttemplate="%{text}",showscale=True))
    fig.update_layout(title="Matriz de Confusão",title_font_color="#00d4ff",xaxis_title="Previsto",yaxis_title="Real",height=320,**L)
    st.plotly_chart(fig,use_container_width=True)

# ════════════ TAB 3 — MAPA ═══════════════════════════════════════════════════

with tab3:
    st.markdown("### 🌍 Mapa Global de Ameaças em Tempo Real")
    COORDS={"China":(35.86,104.19),"Russia":(61.52,105.31),"United States":(37.09,-95.71),
            "North Korea":(40.33,127.51),"Germany":(51.16,10.45),"Brazil":(-14.23,-51.92),
            "Canada":(56.13,-106.34),"India":(20.59,78.96),"France":(46.22,2.21),
            "United Kingdom":(52.13,-1.09),"Iran":(36.20,53.68),"Australia":(-25.27,133.77),
            "Japan":(36.20,138.25),"Netherlands":(52.13,5.29),"Ukraine":(48.38,31.17)}
    TARGET=(-15.78,-47.92)
    attack_df=df_vis[df_vis["TIPO INCIDENTE"]=="ataque"].copy()
    cc=attack_df["PAIS_ATAQUE"].value_counts().reset_index(); cc.columns=["country","total"]
    import json
    arcs=[]
    for _,row in cc.iterrows():
        c=row["country"]
        if c in COORDS:
            s=COORDS[c]
            arcs.append({"src_lat":s[0],"src_lon":s[1],"dst_lat":TARGET[0],"dst_lon":TARGET[1],
                         "name":c,"count":int(row["total"]),
                         "severity":"high" if row["total"]>30 else ("medium" if row["total"]>15 else "low")})
    map_html="""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#060b18;overflow:hidden;font-family:'Segoe UI',sans-serif;}
canvas{display:block;}
.panel{position:absolute;background:rgba(4,8,20,.88);backdrop-filter:blur(14px);border:1px solid rgba(0,212,255,.18);border-radius:14px;z-index:100;pointer-events:none;}
.panel::before{content:'';position:absolute;top:0;left:10%;right:10%;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,.45),transparent);}
#ps{top:16px;right:16px;padding:14px 20px;min-width:155px;text-align:center;}
.sl{color:rgba(90,122,158,.9);font-size:9px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:2px;}
.sv{color:#00d4ff;font-size:26px;font-weight:700;font-family:'Courier New',monospace;line-height:1.1;}
.sd{border:none;border-top:1px solid rgba(0,212,255,.1);margin:10px 0;}
#pl{bottom:16px;left:16px;padding:12px 16px;}
.lt{color:#00d4ff;font-size:11px;font-weight:600;margin-bottom:8px;}
.lr{display:flex;align-items:center;gap:8px;margin:4px 0;}
.ld{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.lx{color:rgba(180,200,220,.8);font-size:10px;}
#pf{top:16px;left:16px;padding:10px 14px;min-width:175px;}
.fl{color:#00d4ff;font-size:11px;font-weight:600;}
.fd{margin-top:8px;max-height:80px;overflow:hidden;}
.fi{color:rgba(160,190,210,.85);font-size:9.5px;padding:2px 0;border-bottom:1px solid rgba(0,212,255,.06);font-family:'Courier New',monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ld2{display:inline-block;width:8px;height:8px;border-radius:50%;background:#00ff64;margin-right:6px;animation:p 1.5s ease-in-out infinite;}
@keyframes p{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(0,255,100,.4);}50%{opacity:.7;box-shadow:0 0 0 5px rgba(0,255,100,0);}}
#tt{position:absolute;display:none;pointer-events:none;z-index:200;background:rgba(4,8,20,.96);border:1px solid rgba(0,212,255,.35);border-radius:10px;padding:10px 14px;font-size:11px;color:#00d4ff;min-width:155px;box-shadow:0 8px 32px rgba(0,0,0,.5);}
</style></head><body>
<canvas id="c"></canvas>
<div class="panel" id="pf"><div><span class="ld2"></span><span class="fl">ATAQUES AO VIVO</span></div><div class="fd" id="fd"></div></div>
<div class="panel" id="ps">
  <div class="sl">Ameaças</div><div class="sv" id="ac">0</div><hr class="sd">
  <div class="sl">IPs Bloqueados</div><div class="sv" id="ic">0</div><hr class="sd">
  <div class="sl">Países</div><div class="sv" id="cc2">0</div>
</div>
<div class="panel" id="pl">
  <div class="lt">🌐 LEGENDA</div>
  <div class="lr"><div class="ld" style="background:#ef4444;box-shadow:0 0 6px #ef4444;"></div><span class="lx">Alto (&gt;30)</span></div>
  <div class="lr"><div class="ld" style="background:#f59e0b;box-shadow:0 0 6px #f59e0b;"></div><span class="lx">Médio (15–30)</span></div>
  <div class="lr"><div class="ld" style="background:#00d4ff;box-shadow:0 0 6px #00d4ff;"></div><span class="lx">Baixo (&lt;15)</span></div>
  <div class="lr" style="margin-top:8px;border-top:1px solid rgba(0,212,255,.1);padding-top:8px;">
    <div class="ld" style="background:#00ff64;box-shadow:0 0 8px #00ff64;width:11px;height:11px;"></div>
    <span class="lx" style="color:#00ff64;font-weight:600;">🎯 ALVO: BRASIL</span>
  </div>
</div>
<div id="tt"><div id="tn" style="font-weight:700;font-size:12px;margin-bottom:4px;"></div><div id="tc" style="color:rgba(180,200,220,.8);"></div><div style="height:3px;background:rgba(0,212,255,.15);border-radius:2px;margin-top:6px;overflow:hidden;"><div id="tf" style="height:100%;background:#00d4ff;border-radius:2px;"></div></div></div>
<script>
var A="""+json.dumps(arcs)+""";
var mx=A.reduce(function(m,a){return Math.max(m,a.count);},1);
document.getElementById('cc2').textContent=A.length;
var cv=document.getElementById('c'),ctx=cv.getContext('2d'),W,H,pts=[],fn=0,at=0,ip=0;
function rsz(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}
rsz();window.addEventListener('resize',rsz);
function ll(lat,lon){return[(lon+180)/360*W,(90-lat)/180*H];}
function col(a){return a.severity==='high'?[239,68,68]:a.severity==='medium'?[245,158,11]:[0,212,255];}
var stars=[];for(var i=0;i<150;i++)stars.push({x:Math.random(),y:Math.random(),r:Math.random()*.9+.2,a:Math.random()*.3+.05});
function dStars(){for(var i=0;i<stars.length;i++){var s=stars[i];ctx.beginPath();ctx.arc(s.x*W,s.y*H,s.r,0,Math.PI*2);ctx.fillStyle='rgba(150,180,220,'+s.a+')';ctx.fill();}}
function dGrid(){ctx.lineWidth=.4;for(var lon=-180;lon<=180;lon+=30){var p=ll(0,lon);ctx.beginPath();ctx.moveTo(p[0],0);ctx.lineTo(p[0],H);ctx.strokeStyle='rgba(0,180,255,.05)';ctx.stroke();}for(var lat=-90;lat<=90;lat+=30){var p=ll(lat,0);ctx.beginPath();ctx.moveTo(0,p[1]);ctx.lineTo(W,p[1]);ctx.strokeStyle='rgba(0,180,255,.05)';ctx.stroke();}}
var N=[[35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],[40.33,127.51,"PRK"],[51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],[56.13,-106.34,"CAN"],[20.59,78.96,"IND"],[46.22,2.21,"FRA"],[52.13,-1.09,"GBR"],[36.20,53.68,"IRN"],[-25.27,133.77,"AUS"],[36.20,138.25,"JPN"],[52.13,5.29,"NLD"],[48.38,31.17,"UKR"]];
function dNodes(t){for(var i=0;i<N.length;i++){var n=N[i],p=ll(n[0],n[1]),br=n[2]==='BRA';if(br){var pls=.5+.5*Math.sin(t*.05);ctx.beginPath();ctx.arc(p[0],p[1],20+pls*10,0,Math.PI*2);ctx.strokeStyle='rgba(0,255,100,'+(0.08+pls*.08)+')';ctx.lineWidth=1;ctx.stroke();ctx.beginPath();ctx.arc(p[0],p[1],12,0,Math.PI*2);ctx.strokeStyle='rgba(0,255,100,.3)';ctx.lineWidth=1.2;ctx.stroke();ctx.beginPath();ctx.arc(p[0],p[1],5,0,Math.PI*2);ctx.fillStyle='#00ff64';ctx.shadowColor='#00ff64';ctx.shadowBlur=14;ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#00ff64';ctx.font='bold 11px Segoe UI';ctx.fillText(n[2],p[0]+10,p[1]+4);}else{ctx.beginPath();ctx.arc(p[0],p[1],3.5,0,Math.PI*2);ctx.fillStyle='rgba(0,180,255,.35)';ctx.shadowColor='rgba(0,180,255,.5)';ctx.shadowBlur=6;ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='rgba(120,170,210,.7)';ctx.font='9px Segoe UI';ctx.fillText(n[2],p[0]+6,p[1]+3);}}}
function dArcGhost(a){var s=ll(a.src_lat,a.src_lon),d=ll(a.dst_lat,a.dst_lon),mx2=(s[0]+d[0])/2,my=Math.min(s[1],d[1])-Math.abs(d[0]-s[0])*.18,c=col(a);ctx.beginPath();ctx.moveTo(s[0],s[1]);ctx.quadraticCurveTo(mx2,my,d[0],d[1]);ctx.strokeStyle='rgba('+c[0]+','+c[1]+','+c[2]+',.06)';ctx.lineWidth=.8;ctx.stroke();}
function Pt(a){this.a=a;this.t=0;this.sp=.0025+Math.random()*.003;this.tr=[];this.tl=22+Math.floor(Math.random()*12);this.w=1.2+Math.random()*1.4;}
Pt.prototype.pos=function(t){var s=ll(this.a.src_lat,this.a.src_lon),d=ll(this.a.dst_lat,this.a.dst_lon),mx2=(s[0]+d[0])/2,my=Math.min(s[1],d[1])-Math.abs(d[0]-s[0])*.18,u=1-t;return[u*u*s[0]+2*u*t*mx2+t*t*d[0],u*u*s[1]+2*u*t*my+t*t*d[1]];};
Pt.prototype.upd=function(){this.t+=this.sp;this.tr.push(this.pos(Math.min(this.t,1)));if(this.tr.length>this.tl)this.tr.shift();return this.t<1;};
Pt.prototype.drw=function(){if(this.tr.length<2)return;var c=col(this.a);for(var i=1;i<this.tr.length;i++){var al=i/this.tr.length;ctx.beginPath();ctx.moveTo(this.tr[i-1][0],this.tr[i-1][1]);ctx.lineTo(this.tr[i][0],this.tr[i][1]);ctx.strokeStyle='rgba('+c[0]+','+c[1]+','+c[2]+','+al+')';ctx.lineWidth=this.w*al;ctx.stroke();}var l=this.tr[this.tr.length-1];ctx.beginPath();ctx.arc(l[0],l[1],2.5,0,Math.PI*2);ctx.fillStyle='rgb('+c[0]+','+c[1]+','+c[2]+')';ctx.shadowColor='rgb('+c[0]+','+c[1]+','+c[2]+')';ctx.shadowBlur=8;ctx.fill();ctx.shadowBlur=0;};
var FN=['Ransomware','DDoS','SQLi','Phishing','Brute Force','Zero-Day','MitM','Malware'];
function addFeed(a){var el=document.getElementById('fd'),d=document.createElement('div');d.className='fi';var n=new Date(),h=String(n.getHours()).padStart(2,'0'),m=String(n.getMinutes()).padStart(2,'0'),s=String(n.getSeconds()).padStart(2,'0');d.textContent=h+':'+m+':'+s+' '+a.name+' → '+FN[Math.floor(Math.random()*FN.length)];el.insertBefore(d,el.firstChild);while(el.children.length>6)el.removeChild(el.lastChild);}
function spawn(){if(!A.length)return;var a=A[Math.floor(Math.random()*A.length)];if(Math.random()<.15+a.count/mx*.25)pts.push(new Pt(a));}
function loop(){requestAnimationFrame(loop);ctx.fillStyle='#060b18';ctx.fillRect(0,0,W,H);dStars();dGrid();A.forEach(dArcGhost);dNodes(fn);if(fn%8===0)spawn();var alive=[];for(var i=0;i<pts.length;i++){if(pts[i].upd()){pts[i].drw();alive.push(pts[i]);}else{at++;ip=Math.floor(at*.72);document.getElementById('ac').textContent=at.toLocaleString();document.getElementById('ic').textContent=ip.toLocaleString();if(at%3===0)addFeed(pts[i].a);}}pts=alive;fn++;}
loop();
cv.addEventListener('mousemove',function(e){var r=cv.getBoundingClientRect(),mx2=(e.clientX-r.left)*(W/r.width),my2=(e.clientY-r.top)*(H/r.height),tip=document.getElementById('tt'),found=false;for(var i=0;i<A.length;i++){var a=A[i],p=ll(a.src_lat,a.src_lon);if(Math.hypot(mx2-p[0],my2-p[1])<22){document.getElementById('tn').textContent=a.name;document.getElementById('tc').textContent=a.count+' ataques detectados';document.getElementById('tf').style.width=(a.count/mx*100)+'%';tip.style.display='block';tip.style.left=(e.clientX+18)+'px';tip.style.top=(e.clientY-55)+'px';found=true;break;}}if(!found)tip.style.display='none';});
cv.addEventListener('mouseleave',function(){document.getElementById('tt').style.display='none';});
</script></body></html>"""
    components.html(map_html, height=580, scrolling=False)
    st.markdown("### Países com Mais Ataques")
    ta=df_vis[df_vis["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns=["País","Ataques"]
    ta["Percentual"]=(ta["Ataques"]/ta["Ataques"].sum()*100).round(1).astype(str)+"%"
    st.dataframe(ta,use_container_width=True,hide_index=True)

# ════════════ TAB 4 — ASSISTENTE IA (GEMINI) ════════════════════════════════

with tab4:
    st.markdown("### 🤖 Assistente de IA — SentinelBot")
    st.caption("Powered by Google Gemini — Pergunte sobre incidentes, clientes, ameaças ou recomendações")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    top5c = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5a = df_vis[df_vis["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()

    system_prompt = f"""Você é o SentinelBot, assistente de segurança cibernética da SentinelAI.
Responda em português do Brasil, de forma profissional e direta.

DADOS DO SISTEMA:
- Total de incidentes: {len(df_vis)}
- Críticos: {len(df_vis[df_vis['SEVERIDADE']=='crítica'])} ({len(df_vis[df_vis['SEVERIDADE']=='crítica'])/len(df_vis)*100:.1f}%)
- IPs bloqueados: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower()=='sim'])}
- Prejuízo total: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- Acurácia do modelo: {acuracia:.1%}
- Tipos: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Clientes: {', '.join(df_vis['CLIENTE'].unique())}
- Top países atacantes: {top5a}
- Top clientes por prejuízo: {top5c}
- Período: {df_vis['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].min()) else 'N/A'} a {df_vis['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].max()) else 'N/A'}
{'- Visão global' if not cliente_vinculado else f'- Filtro: {cliente_vinculado}'}"""

    if not GEMINI_API_KEY:
        st.error("🔴 Assistente offline — Configure GEMINI_API_KEY nos Secrets do Streamlit")
    else:
        st.success("🟢 SentinelBot ativo — Powered by Gemini 1.5 Flash")

    for msg in st.session_state["chat_history"]:
        css = "chat-user" if msg["role"]=="user" else "chat-ai"
        ico = "👤" if msg["role"]=="user" else "🤖"
        st.markdown(f'<div class="{css}">{ico} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        cq,cb = st.columns([5,1])
        with cq:
            pergunta = st.text_input("",placeholder="Ex: Qual cliente teve mais prejuízo?",label_visibility="collapsed",disabled=not GEMINI_API_KEY)
        with cb:
            enviar = st.form_submit_button("Enviar",use_container_width=True,disabled=not GEMINI_API_KEY)

    sugs=["Qual cliente teve mais prejuízo?","Quais países mais atacaram?","Como estão os críticos?","Acurácia do modelo?","Recomendações de segurança"]
    cols_s=st.columns(len(sugs)); sug_esc=None
    for i,s in enumerate(sugs):
        with cols_s[i]:
            if st.button(s[:22]+"…" if len(s)>22 else s,key=f"sg{i}",use_container_width=True,disabled=not GEMINI_API_KEY): sug_esc=s
    if sug_esc: pergunta=sug_esc; enviar=True

    if enviar and pergunta and GEMINI_API_KEY:
        adicionar_log(usuario_atual,f"Chat: {pergunta[:50]}")
        st.session_state["chat_history"].append({"role":"user","content":pergunta})
        with st.spinner("🤔 Analisando..."):
            try:
                # Monta histórico no formato Gemini
                contents = [{"role":"user","parts":[{"text":system_prompt+"\n\nAgora responda a pergunta do usuário."}]},
                             {"role":"model","parts":[{"text":"Entendido. Estou pronto para responder sobre o sistema SentinelAI."}]}]
                for m in st.session_state["chat_history"]:
                    role = "user" if m["role"]=="user" else "model"
                    contents.append({"role":role,"parts":[{"text":m["content"]}]})

                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                payload_g = {"contents": contents,
                             "generationConfig":{"temperature":0.7,"maxOutputTokens":1024}}
                resp_g = requests.post(url,json=payload_g,timeout=30)
                if resp_g.status_code==200:
                    resposta = resp_g.json()["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    err = resp_g.json()
                    resposta = f"⚠️ Erro {resp_g.status_code}: {err.get('error',{}).get('message',resp_g.text[:120])}"
            except Exception as e:
                resposta = f"⚠️ Erro de conexão: {str(e)[:100]}"
        st.session_state["chat_history"].append({"role":"assistant","content":resposta})
        adicionar_log(usuario_atual,"Resposta gerada pelo SentinelBot")
        st.rerun()

    if st.session_state["chat_history"]:
        if st.button("🗑️ Limpar conversa"):
            st.session_state["chat_history"]=[]
            st.rerun()

# ════════════ TAB 5 — BACKUP ══════════════════════════════════════════════════

with tab5:
    st.markdown("### Backup e Exportação")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas administradores podem exportar dados.")
    else:
        ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        b1,b2,b3=st.columns(3)
        with b1: st.download_button("📥 CSV Completo",df.to_csv(index=False).encode("utf-8"),f"sentinel_{ts}.csv","text/csv",use_container_width=True)
        with b2:
            df_a=df.drop(columns=["IP_SUSPEITO"],errors="ignore")
            st.download_button("🔒 Anonimizado",df_a.to_csv(index=False).encode("utf-8"),f"sentinel_anon_{ts}.csv","text/csv",use_container_width=True)
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button("📋 Logs","\n".join(st.session_state["logs_sistema"]).encode("utf-8"),f"sentinel_logs_{ts}.txt","text/plain",use_container_width=True)
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db","rb") as f:
                st.download_button("🗄️ Backup SQLite",f.read(),f"sentinel_db_{ts}.db","application/x-sqlite3",use_container_width=True)
    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### Histórico")
        st.dataframe(pd.DataFrame(st.session_state["backups"]),use_container_width=True)
    st.markdown("### Prévia")
    st.dataframe(df_vis.head(20),use_container_width=True)

# ════════════ TAB 6 — LOGS ════════════════════════════════════════════════════

with tab6:
    st.markdown("### Logs do Sistema")
    tl1,tl2=st.tabs(["📱 Sessão Atual","💾 Histórico do Banco"])
    with tl1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]): st.code(log,language=None)
        else: st.info("Nenhum log na sessão atual.")
    with tl2:
        if sqlite_ativo:
            try:
                ld=pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100",sqlite_conn)
                st.dataframe(ld,use_container_width=True) if not ld.empty else st.info("Nenhum log no banco.")
            except: st.info("Erro ao carregar logs.")
        else: st.warning("Banco offline.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center;padding:1.2rem 0;border-top:1px solid rgba(0,212,255,.07);margin-top:1.5rem;">
  <p style="color:#2a4a6a;font-size:.68rem;font-family:'JetBrains Mono',monospace;">
    SentinelAI © 2025 — Plataforma de Segurança Cibernética | LGPD Compliance | Powered by Gemini
  </p>
</div>""", unsafe_allow_html=True)
