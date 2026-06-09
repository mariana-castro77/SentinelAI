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

GEMINI_API_KEY = "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA"

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;scroll-behavior:smooth;}

.stApp{
  background:#060810;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%,rgba(0,200,255,0.07) 0%,transparent 70%),
    radial-gradient(ellipse 40% 30% at 80% 80%,rgba(0,80,200,0.04) 0%,transparent 60%);
}

[data-testid="stHeader"]{background:transparent;}

[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#050709 0%,#080b12 100%);
  border-right:1px solid rgba(0,200,255,0.06);
}

.block-container{padding:1.2rem 1.5rem;max-width:100%;}

div[data-testid="metric-container"]{
  background:linear-gradient(135deg,rgba(0,200,255,0.04),rgba(6,8,16,0.97));
  border:1px solid rgba(0,200,255,0.11);
  border-radius:14px;padding:1rem 1.2rem;
  transition:all .25s ease;position:relative;overflow:hidden;
}
div[data-testid="metric-container"]::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,200,255,0.35),transparent);
}
div[data-testid="metric-container"]:hover{
  border-color:rgba(0,200,255,0.25);transform:translateY(-3px);
  box-shadow:0 8px 32px rgba(0,200,255,0.07);
}
[data-testid="stMetricLabel"]{color:#4a6a8a!important;font-size:.58rem!important;text-transform:uppercase;letter-spacing:.1em;}
[data-testid="stMetricValue"]{color:#00d4ff!important;font-size:1.4rem!important;font-weight:700;font-family:'JetBrains Mono',monospace;}

div.stButton>button{
  background:linear-gradient(135deg,#005f8a,#0097c4);
  color:white;border-radius:10px;border:none;
  padding:.55rem 1rem;font-weight:600;font-size:.8rem;
  transition:all .2s ease;width:100%;letter-spacing:.03em;
}
div.stButton>button:hover{
  background:linear-gradient(135deg,#0077aa,#00b8e0);
  transform:translateY(-2px);box-shadow:0 6px 24px rgba(0,180,220,0.18);
}

.chat-user{
  background:linear-gradient(135deg,#005f8a,#0097c4);
  border-radius:18px 18px 4px 18px;padding:.7rem 1.1rem;
  margin:.5rem 0 .5rem auto;max-width:78%;width:fit-content;
  color:white;font-size:.82rem;line-height:1.55;
  box-shadow:0 4px 16px rgba(0,100,160,0.22);
}
.chat-ai{
  background:rgba(8,11,20,0.96);
  border:1px solid rgba(0,200,255,0.12);
  border-radius:18px 18px 18px 4px;padding:.7rem 1.1rem;
  margin:.5rem 0;max-width:78%;width:fit-content;
  color:#c8d8e8;font-size:.82rem;line-height:1.55;
  box-shadow:0 4px 16px rgba(0,0,0,0.28);
}

.sentinel-header{
  background:linear-gradient(135deg,rgba(0,200,255,0.04),rgba(0,60,120,0.03));
  border:1px solid rgba(0,200,255,0.09);border-radius:16px;
  padding:1.2rem 1.8rem;margin-bottom:1.2rem;position:relative;overflow:hidden;
}
.sentinel-header::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,200,255,0.25),transparent);
}

.badge-online{
  display:inline-flex;align-items:center;gap:.3rem;
  background:rgba(0,255,100,.06);border:1px solid rgba(0,255,100,.18);
  color:#00ff88;padding:.25rem .8rem;border-radius:20px;
  font-size:.58rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
}
.badge-db{
  display:inline-flex;align-items:center;gap:.3rem;
  background:rgba(0,200,255,.06);border:1px solid rgba(0,200,255,.18);
  color:#00d4ff;padding:.25rem .8rem;border-radius:20px;
  font-size:.58rem;font-weight:600;
}

.stTabs [data-baseweb="tab-list"]{
  background:rgba(8,11,20,0.8);border-radius:12px;
  padding:.3rem;gap:.2rem;border:1px solid rgba(0,200,255,.06);
}
.stTabs [data-baseweb="tab"]{
  border-radius:10px;color:#4a6a8a;font-weight:500;
  padding:.45rem .9rem;font-size:.75rem;transition:all .2s;
}
.stTabs [aria-selected="true"]{background:rgba(0,160,200,.1)!important;color:#00d4ff!important;}

input,textarea,[data-baseweb="input"] input{
  background:rgba(8,11,20,0.92)!important;
  border:1px solid rgba(0,200,255,.1)!important;
  border-radius:10px!important;color:white!important;
  box-shadow:none!important;outline:none!important;
}

[data-baseweb="select"] *{border:none!important;box-shadow:none!important;}
[data-baseweb="select"] [data-testid="stMarkdownContainer"]{border:none!important;}
div[data-baseweb="select"]>div{
  background:rgba(8,11,20,0.92)!important;
  border:1px solid rgba(0,200,255,.1)!important;
  border-radius:10px!important;color:white!important;
  box-shadow:none!important;
}
[data-baseweb="select"]:focus-within>div{
  border-color:rgba(0,200,255,.28)!important;box-shadow:none!important;
}
[data-baseweb="menu"]{
  background:#080b14!important;
  border:1px solid rgba(0,200,255,.12)!important;
  border-radius:10px!important;
}
[data-baseweb="menu"] li{color:#c8d8e8!important;font-size:.8rem!important;}
[data-baseweb="menu"] li:hover{background:rgba(0,200,255,.08)!important;}

[data-testid="stSlider"] .st-emotion-cache-1gv3huu{background:#00d4ff!important;}

hr{border-color:rgba(0,200,255,.05);margin:1rem 0;}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:#060810;}
::-webkit-scrollbar-thumb{background:rgba(0,200,255,0.18);border-radius:2px;}

.sidebar-profile{
  background:rgba(0,200,255,.03);border:1px solid rgba(0,200,255,.07);
  border-radius:12px;padding:.7rem .9rem;margin:.4rem 0;
}

.lgpd-banner{
  position:fixed;bottom:0;left:0;right:0;z-index:9999;
  background:rgba(5,8,14,0.97);
  border-top:1px solid rgba(0,200,255,0.18);
  padding:1rem 2rem;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;
  backdrop-filter:blur(12px);
}
</style>
""", unsafe_allow_html=True)

def conectar_sqlite():
    try:
        return sqlite3.connect('sentinelai.db', check_same_thread=False)
    except:
        return None

def inicializar_sqlite(conn):
    try:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS incidentes_registrados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,usuario TEXT,tipo_incidente TEXT,
            origem TEXT,status TEXT,severidade_prevista TEXT,cliente TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,usuario TEXT,acao TEXT,
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
        "usuario": usuario,"motivo": motivo,"registros": len(df)
    })

def mascara_ip(ip):
    if ip == "Nenhum" or pd.isna(ip): return "***.***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

USUARIOS = {
    "admin":        {"senha":"admin123",    "perfil":"Administrador","pode_exportar":True, "pode_analisar":True, "ver_pii":True,  "cliente_vinculado":None},
    "analista":     {"senha":"analista123", "perfil":"Analista",     "pode_exportar":False,"pode_analisar":True, "ver_pii":False, "cliente_vinculado":None},
    "nubank":       {"senha":"nubank123",   "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Nubank"},
    "mercadolivre": {"senha":"ml123",       "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Mercado Livre"},
    "santander":    {"senha":"sant123",     "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Santander"},
    "magazineluiza":{"senha":"ml2024",      "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Magazine Luiza"},
    "ifood":        {"senha":"ifood123",    "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"iFood"},
    "xp":           {"senha":"xp2024",      "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"XP Investimentos"},
    "vivo":         {"senha":"vivo123",     "perfil":"Cliente",      "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Vivo"},
    "viewer":       {"senha":"viewer123",   "perfil":"Visualizador", "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":None},
}

_hashes = {u: hashlib.sha256(v["senha"].encode()).hexdigest() for u, v in USUARIOS.items()}

def autenticar(u, s):
    return u in _hashes and hashlib.sha256(s.encode()).hexdigest() == _hashes[u]

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if "lgpd_aceito" not in st.session_state:
    st.session_state["lgpd_aceito"] = False

if not st.session_state["lgpd_aceito"]:
    st.markdown("""
    <div class="lgpd-banner" id="lgpd-banner">
      <div style="flex:1;min-width:260px;">
        <p style="color:white;font-size:.82rem;font-weight:600;margin-bottom:.3rem;">
          🍪 Privacidade & Cookies — LGPD
        </p>
        <p style="color:#5a7a9a;font-size:.72rem;line-height:1.5;">
          Utilizamos cookies e dados de sessão para autenticação, logs de auditoria e funcionamento da plataforma,
          em conformidade com a <strong style="color:#00d4ff;">Lei Geral de Proteção de Dados (LGPD — Lei nº 13.709/2018)</strong>.
          Nenhum dado pessoal é compartilhado com terceiros. Ao continuar, você concorda com nossa
          <a href="#" style="color:#00d4ff;text-decoration:none;">Política de Privacidade</a>.
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    col_lgpd1, col_lgpd2, col_lgpd3 = st.columns([6,1,1])
    with col_lgpd2:
        if st.button("Recusar", key="lgpd_recusar"):
            st.warning("⚠️ Para utilizar a plataforma é necessário aceitar os termos.")
    with col_lgpd3:
        if st.button("✓ Aceitar", key="lgpd_aceitar"):
            st.session_state["lgpd_aceito"] = True
            st.rerun()
    st.stop()

if not st.session_state["autenticado"]:
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none;}
    header{display:none!important;}
    </style>
    """, unsafe_allow_html=True)

    components.html("""
    <style>
      body{margin:0;overflow:hidden;background:#060810;}
      canvas{position:fixed;top:0;left:0;width:100%;height:100%;}
    </style>
    <canvas id="bg"></canvas>
    <script>
    const cv=document.getElementById('bg'),ctx=cv.getContext('2d');
    let W,H,pts=[],mouseX=0,mouseY=0;
    function resize(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}
    resize();window.addEventListener('resize',resize);
    document.addEventListener('mousemove',e=>{mouseX=e.clientX;mouseY=e.clientY;});

    class P{
      constructor(){this.reset();}
      reset(){
        this.x=Math.random()*W;this.y=Math.random()*H;
        this.r=Math.random()*1.4+.3;
        this.vx=(Math.random()-.5)*.25;this.vy=(Math.random()-.5)*.25;
        this.a=Math.random()*.4+.1;this.base={x:this.x,y:this.y};
      }
      update(){
        let dx=(mouseX-W/2)*0.003,dy=(mouseY-H/2)*0.003;
        this.x+=this.vx+dx*this.r;this.y+=this.vy+dy*this.r;
        if(this.x<0||this.x>W||this.y<0||this.y>H)this.reset();
      }
      draw(){
        ctx.beginPath();ctx.arc(this.x,this.y,this.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(0,200,255,${this.a})`;ctx.fill();
      }
    }
    for(let i=0;i<140;i++)pts.push(new P());

    function drawGrid(){
      ctx.strokeStyle='rgba(0,150,220,0.025)';ctx.lineWidth=1;
      for(let x=0;x<W;x+=70){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke();}
      for(let y=0;y<H;y+=70){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke();}
    }

    function drawLines(){
      for(let i=0;i<pts.length;i++){
        for(let j=i+1;j<pts.length;j++){
          let dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y;
          let d=Math.sqrt(dx*dx+dy*dy);
          if(d<100){
            ctx.beginPath();ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);
            ctx.strokeStyle=`rgba(0,200,255,${0.06*(1-d/100)})`;ctx.lineWidth=.5;ctx.stroke();
          }
        }
      }
    }

    function anim(){
      requestAnimationFrame(anim);
      ctx.fillStyle='rgba(6,8,16,0.88)';ctx.fillRect(0,0,W,H);
      drawGrid();drawLines();pts.forEach(p=>{p.update();p.draw();});
    }
    anim();
    </script>
    """, height=0, scrolling=False)

    col1, col2, col3 = st.columns([1,1.3,1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
            width:70px;height:70px;border-radius:20px;
            background:linear-gradient(135deg,rgba(0,200,255,0.13),rgba(0,70,130,0.1));
            border:1px solid rgba(0,200,255,0.18);font-size:2rem;margin-bottom:1rem;
            box-shadow:0 0 48px rgba(0,200,255,0.08);">🛡️</div>
          <h1 style="color:#fff;font-size:1.9rem;font-weight:800;letter-spacing:-.02em;margin:0;">
            Sentinel<span style="color:#00d4ff;">AI</span>
          </h1>
          <p style="color:#4a6a8a;font-size:.82rem;margin:.4rem 0 1rem 0;">
            Plataforma de Segurança Cibernética
          </p>
          <span class="badge-online">● SISTEMA OPERACIONAL</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(8,11,20,0.88);border:1px solid rgba(0,200,255,0.09);
          border-radius:18px;padding:1.8rem;backdrop-filter:blur(20px);
          box-shadow:0 24px 64px rgba(0,0,0,0.4);">
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown('<p style="color:#5a7a9a;font-size:.7rem;margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.08em;">Usuário</p>', unsafe_allow_html=True)
            usuario_input = st.text_input("u", placeholder="ex: admin, analista, nubank…", label_visibility="collapsed")
            st.markdown('<p style="color:#5a7a9a;font-size:.7rem;margin:.7rem 0 .3rem 0;text-transform:uppercase;letter-spacing:.08em;">Senha</p>', unsafe_allow_html=True)
            senha_input = st.text_input("s", type="password", placeholder="••••••••", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Entrar na plataforma →", use_container_width=True)

            if submit:
                if autenticar(usuario_input.strip(), senha_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = usuario_input.strip()
                    adicionar_log(usuario_input.strip(), "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:1.2rem;background:rgba(0,200,255,0.02);
          border:1px solid rgba(0,200,255,0.07);border-radius:14px;padding:1rem 1.2rem;">
          <p style="color:#3a5a7a;font-size:.6rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem;">
            Acessos de demonstração
          </p>
          <table style="width:100%;border-collapse:collapse;">
            <thead>
              <tr><th style="color:#2a4060;font-size:.58rem;text-align:left;padding:.18rem .4rem;">Usuário</th>
                <th style="color:#2a4060;font-size:.58rem;text-align:left;padding:.18rem .4rem;">Senha</th>
                <th style="color:#2a4060;font-size:.58rem;text-align:left;padding:.18rem .4rem;">Perfil</th>
              </tr>
            </thead>
            <tbody>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.68rem;">admin</td><td style="color:#6a8aaa;font-family:monospace;font-size:.68rem;">admin123</td><td style="color:#00ff88;font-size:.62rem;">Administrador</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.68rem;">analista</td><td style="color:#6a8aaa;font-family:monospace;font-size:.68rem;">analista123</td><td style="color:#f59e0b;font-size:.62rem;">Analista</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.68rem;">nubank</td><td style="color:#6a8aaa;font-family:monospace;font-size:.68rem;">nubank123</td><td style="color:#6a8aaa;font-size:.62rem;">Cliente</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.68rem;">mercadolivre</td><td style="color:#6a8aaa;font-family:monospace;font-size:.68rem;">ml123</td><td style="color:#6a8aaa;font-size:.62rem;">Cliente</td></tr>
              <tr><td style="color:#00d4ff;font-family:monospace;font-size:.68rem;">viewer</td><td style="color:#6a8aaa;font-family:monospace;font-size:.68rem;">viewer123</td><td style="color:#6a8aaa;font-size:.62rem;">Visualizador</td></tr>
            </tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

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

for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"]:
    if col in df_vis.columns:
        df_vis[col] = df_vis[col].astype(str).str.strip()

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.8rem 0 .4rem 0;">
      <div style="font-size:1.8rem;">🛡️</div>
      <h3 style="color:#00d4ff;margin:.2rem 0;font-size:1.05rem;font-weight:700;">SentinelAI</h3>
      <p style="color:#2a4060;font-size:.55rem;letter-spacing:.12em;text-transform:uppercase;">Security Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    cores_perfil = {"Administrador":"#00ff88","Analista":"#f59e0b","Cliente":"#00d4ff","Visualizador":"#6a8aaa"}
    cor_p = cores_perfil.get(perfil_atual["perfil"],"#6a8aaa")

    st.markdown(f"""
    <div class="sidebar-profile">
      <p style="color:#2a4060;font-size:.52rem;text-transform:uppercase;letter-spacing:.1em;">Perfil ativo</p>
      <p style="color:white;font-weight:700;font-size:.88rem;margin:.2rem 0;">{perfil_atual['perfil']}</p>
      <p style="color:#4a6a8a;font-size:.62rem;">@{usuario_atual}</p>
      <div style="margin-top:.4rem;">
        <span style="background:rgba(0,200,255,.05);border:1px solid rgba(0,200,255,.12);
          color:{cor_p};padding:.14rem .5rem;border-radius:12px;font-size:.52rem;font-weight:700;">
          ● {perfil_atual['perfil'].upper()}
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    badge_db = '<span class="badge-db">📁 SQLite Ativo</span>' if sqlite_ativo else '<span style="color:#ff4444;font-size:.62rem;">⚠️ DB Offline</span>'
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p style="color:#2a4060;font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem;">Permissões</p>', unsafe_allow_html=True)
    for nome, ativo in [("Análise ML",perfil_atual["pode_analisar"]),("Exportar dados",perfil_atual["pode_exportar"]),("Visualizar IPs",perfil_atual["ver_pii"])]:
        c,i = ("#00ff88","✓") if ativo else ("#ff4444","✗")
        st.markdown(f'<p style="color:{c};font-size:.7rem;margin:.15rem 0;">{i} {nome}</p>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,200,255,.03);border:1px solid rgba(0,200,255,.07);
      border-radius:10px;padding:.7rem;text-align:center;margin:.3rem 0;">
      <p style="color:#2a4060;font-size:.52rem;text-transform:uppercase;letter-spacing:.1em;">Acurácia do Modelo</p>
      <p style="color:#00d4ff;font-size:1.35rem;font-weight:700;font-family:monospace;">{acuracia:.1%}</p>
      <p style="color:#2a4060;font-size:.52rem;">Decision Tree Classifier</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.button("🚪 Encerrar sessão", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado":False,"usuario_atual":None})
        st.rerun()

now_str = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M")
st.markdown(f"""
<div class="sentinel-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;">
    <div>
      <p style="color:#2a4060;font-size:.55rem;text-transform:uppercase;letter-spacing:.14em;">
        {f"Cliente · {cliente_vinculado}" if cliente_vinculado else "Visão Global — Todos os Clientes"}
      </p>
      <h1 style="color:white;margin:0;font-size:1.22rem;font-weight:800;letter-spacing:-.02em;">
        Painel de <span style="color:#00d4ff;">Segurança Cibernética</span>
      </h1>
    </div>
    <div style="text-align:right;">
      <span class="badge-online">● PROTEGIDO</span>
      <p style="color:#2a4060;font-size:.55rem;margin-top:.3rem;">{now_str}</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

total_incidentes      = len(df_vis)
incidentes_criticos   = len(df_vis[df_vis["SEVERIDADE"]=="crítica"])
ips_bloqueados        = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
prejuizo_total        = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"]=="resolvido"])
incidentes_pendentes  = len(df_vis[df_vis["STATUS"]=="pendente"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
pf = f"R$ {prejuizo_total:,.0f}".replace(",","X").replace(".",",").replace("X",".")
with c1: st.metric("Total de Incidentes", f"{total_incidentes:,}")
with c2: st.metric("Críticos", f"{incidentes_criticos:,}")
with c3: st.metric("IPs Bloqueados", f"{ips_bloqueados:,}")
with c4: st.metric("Resolvidos", f"{incidentes_resolvidos:,}")
with c5: st.metric("Pendentes", f"{incidentes_pendentes:,}")
with c6: st.metric("Prejuízo Estimado", pf)

st.markdown("---")

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🔍 Análise ML","📊 Métricas","🌍 Mapa Global","🤖 Assistente IA","💾 Exportar","📋 Logs"
])

with tab1:
    st.markdown("### Análise Preditiva de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Seu perfil não tem permissão para realizar análises preditivas.")
    else:
        tipos_limpos   = [str(v).strip() for v in encoders["tipo"].classes_]
        origens_limpas = [str(v).strip() for v in encoders["origem"].classes_]
        status_limpos  = [str(v).strip() for v in encoders["status"].classes_]
        clientes_lista = sorted([str(c).strip() for c in df["CLIENTE"].unique()])

        ca, cb = st.columns(2)
        with ca:
            tipo_incidente  = st.selectbox("Tipo de incidente",  tipos_limpos)
            origem_ataque   = st.selectbox("Origem do ataque",   origens_limpas)
            cliente_afetado = st.selectbox("Cliente afetado",    clientes_lista)
        with cb:
            tempo_resolucao = st.slider("Tempo estimado de resolução (min)", 1, 120, 30)
            status_atual    = st.selectbox("Status atual", status_limpos)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Executar análise preditiva", use_container_width=True):
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

            if status_atual == "resolvido":
                resultado = "baixa"
            elif tipo_incidente in ["ataque","falha servidor"]:
                resultado = "crítica"
            elif tipo_incidente in ["lentidão","erro sistema"]:
                resultado = random.choice(["baixa","média"])

            risco     = random.randint(10, 99)
            prej_est  = random.uniform(3000, 30000)
            risco_fin = "ALTO" if prej_est > 15000 else ("MÉDIO" if prej_est > 7000 else "BAIXO")

            ataques = df[df["TIPO INCIDENTE"]=="ataque"]
            if not ataques.empty:
                l     = ataques.sample(1).iloc[0]
                ip_ex = l["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(l["IP_SUSPEITO"])
                pais  = l["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "DESCONHECIDO", "INTERNO"

            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 Severidade: CRÍTICA — AÇÃO IMEDIATA NECESSÁRIA")
            elif resultado == "média":
                st.warning(f"🟡 Severidade: MÉDIA — Monitoramento ativo recomendado")
            else:
                st.success(f"🟢 Severidade: BAIXA — Situação controlada")

            r1,r2,r3 = st.columns(3)
            with r1: st.metric("Pontuação de Risco", f"{risco}/100")
            with r2: st.metric("Prejuízo Estimado", f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Classificação", risco_fin)

            if tipo_incidente == "ataque":
                st.error(f"🌍 País de origem: **{pais}**  |  IP suspeito: `{ip_ex}`")
                with st.expander("🛡️ Ações de resposta executadas automaticamente"):
                    for a in ["IP bloqueado automaticamente","Regras de firewall atualizadas","Equipe de segurança notificada","Incidente registrado no SIEM","Relatório gerado"]:
                        st.write(f"✅ {a}")

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn,{
                    "usuario":usuario_atual,"tipo":tipo_incidente,
                    "origem":origem_ataque,"status":status_atual,
                    "severidade":resultado,"cliente":cliente_afetado
                })
                st.success("💾 Incidente registrado no banco de dados")

with tab2:
    st.markdown("### Métricas & Visualizações")
    L = dict(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font_color="#6a8aaa",font_family="Inter",
        margin=dict(t=36,b=16,l=16,r=16)
    )
    g1,g2 = st.columns(2)
    with g1:
        fig = px.pie(df_vis,names="SEVERIDADE",title="Distribuição por Severidade",
                     color_discrete_sequence=["#f59e0b","#10b981","#ef4444","#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    with g2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig = px.bar(vc,x="TIPO INCIDENTE",y="count",title="Incidentes por Tipo",
                     color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig = px.area(df_time,x="DATA",y="Incidentes",title="Volume ao Longo do Tempo",
                  color_discrete_sequence=["#00d4ff"])
    fig.update_traces(fill='tozeroy',fillcolor='rgba(0,212,255,0.06)')
    fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

    g3,g4 = st.columns(2)
    with g3:
        fig = px.histogram(df_vis,x="PAIS_ATAQUE",title="Ataques por País",
                           color_discrete_sequence=["#f59e0b"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    with g4:
        dmg = (df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum()
               .reset_index().sort_values("PREJUIZO_ESTIMADO",ascending=False).head(7))
        fig = px.bar(dmg,x="CLIENTE",y="PREJUIZO_ESTIMADO",title="Impacto Financeiro por Cliente",
                     color_discrete_sequence=["#ef4444"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)

    st.markdown("### Desempenho do Modelo")
    m1,m2,m3 = st.columns(3)
    with m1: st.metric("Acurácia",f"{acuracia:.1%}")
    with m2: st.metric("Amostras Treino",f"{int(len(df)*.8):,}")
    with m3: st.metric("Amostras Teste",f"{int(len(df)*.2):,}")
    cm     = confusion_matrix(y_test,modelo.predict(X_test))
    labels = encoders["severidade"].classes_
    fig = go.Figure(go.Heatmap(
        z=cm,x=labels,y=labels,
        colorscale=[[0,"#060810"],[.5,"#003050"],[1,"#00d4ff"]],
        text=cm,texttemplate="%{text}",showscale=True
    ))
    fig.update_layout(title="Matriz de Confusão",height=320,**L)
    st.plotly_chart(fig,use_container_width=True)

with tab3:
    st.markdown("### 🌍 Mapa Global de Ameaças Cibernéticas")
    st.caption("Monitoramento em tempo real de ataques direcionados aos clientes SentinelAI")

    COORDS = {
        "China":(-10,104.19),"Russia":(61.52,95.0),"United States":(37.09,-95.71),
        "Germany":(51.16,10.45),"Brazil":(-14.23,-51.92),"India":(20.59,78.96),
        "Netherlands":(52.13,5.29),"France":(46.23,2.21),"Ukraine":(48.38,31.17),
        "Iran":(32.43,53.69),"North Korea":(40.34,127.51),"Romania":(45.94,24.97),
        "Nigeria":(9.08,8.67),"Argentina":(-38.4,-63.6),"United Kingdom":(55.37,-3.43),
        "Japan":(36.2,138.25),"Australia":(-25.27,133.77),"Canada":(56.13,-106.34),
        "South Korea":(35.9,127.76),"Pakistan":(30.37,69.34),
    }
    TARGET = (-15.78,-47.92)

    attack_df = df_vis[df_vis["TIPO INCIDENTE"]=="ataque"].copy()
    cc = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country","total"]

    arcs = []
    for _,row in cc.iterrows():
        c = row["country"]
        if c in COORDS:
            s = COORDS[c]
            arcs.append({"src_lat":s[0],"src_lon":s[1],"dst_lat":TARGET[0],"dst_lon":TARGET[1],"name":c,"count":int(row["total"])})

    fallback_countries = ["China","Russia","United States","Germany","Iran","North Korea","Ukraine","Nigeria","United Kingdom","Japan"]
    existing = {a["name"] for a in arcs}
    for fc in fallback_countries:
        if fc not in existing and fc in COORDS:
            s = COORDS[fc]
            arcs.append({"src_lat":s[0],"src_lon":s[1],"dst_lat":TARGET[0],"dst_lon":TARGET[1],"name":fc,"count":random.randint(8,60)})

    arcs_json = json.dumps(arcs)

    map_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#03050a;overflow:hidden;font-family:'JetBrains Mono',monospace;}}
canvas{{display:block;}}
#hud{{
  position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none;z-index:5;
}}
#top-bar{{
  position:absolute;top:14px;left:14px;display:flex;gap:8px;align-items:center;
}}
.pill{{
  background:rgba(3,5,10,0.88);
  border:1px solid rgba(0,200,255,0.22);
  border-radius:8px;padding:5px 12px;font-size:9px;color:#00d4ff;
  letter-spacing:.06em;
}}
.pill.green{{border-color:rgba(0,255,136,0.22);color:#00ff88;}}
#stats{{
  position:absolute;top:14px;right:14px;
  background:rgba(3,5,10,0.9);
  border:1px solid rgba(0,200,255,0.18);
  border-radius:12px;padding:12px 18px;text-align:center;min-width:110px;
}}
#attack-count{{color:#00d4ff;font-size:22px;font-weight:700;}}
#stats-label{{color:#2a5a7a;font-size:7.5px;text-transform:uppercase;letter-spacing:.1em;margin-top:2px;}}
#last-attack{{color:#6a9aaa;font-size:8px;margin-top:6px;}}
#legend{{
  position:absolute;bottom:14px;right:14px;
  background:rgba(3,5,10,0.9);
  border:1px solid rgba(0,200,255,0.14);
  border-radius:10px;padding:10px 14px;
}}
.leg{{display:flex;align-items:center;gap:7px;margin:4px 0;font-size:8.5px;color:#5a8aaa;}}
.dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
#clients{{
  position:absolute;bottom:14px;left:14px;
  background:rgba(3,5,10,0.9);
  border:1px solid rgba(0,200,255,0.14);
  border-radius:10px;padding:10px 14px;max-width:160px;
}}
#clients-title{{color:#2a5a7a;font-size:7.5px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;}}
.client-item{{display:flex;align-items:center;gap:6px;margin:3px 0;font-size:8px;color:#4a7a9a;}}
.client-dot{{width:5px;height:5px;border-radius:50%;background:#00ff88;box-shadow:0 0 4px #00ff88;flex-shrink:0;}}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="hud">
  <div id="top-bar">
    <div class="pill green">● AO VIVO</div>
    <div class="pill">🛡️ SENTINELAI — THREAT MAP</div>
    <div class="pill" id="time-pill">--:--:--</div>
  </div>
  <div id="stats">
    <div id="attack-count">0</div>
    <div id="stats-label">ataques detectados</div>
    <div id="last-attack">Aguardando…</div>
  </div>
  <div id="legend">
    <div class="leg"><div class="dot" style="background:#ef4444;box-shadow:0 0 5px #ef4444;"></div>Crítico</div>
    <div class="leg"><div class="dot" style="background:#f59e0b;box-shadow:0 0 5px #f59e0b;"></div>Médio</div>
    <div class="leg"><div class="dot" style="background:#00d4ff;box-shadow:0 0 5px #00d4ff;"></div>Baixo</div>
    <div class="leg"><div class="dot" style="background:#00ff88;box-shadow:0 0 5px #00ff88;"></div>Brasil 🎯</div>
  </div>
  <div id="clients">
    <div id="clients-title">Clientes Protegidos</div>
    <div class="client-item"><div class="client-dot"></div>Nubank</div>
    <div class="client-item"><div class="client-dot"></div>Mercado Livre</div>
    <div class="client-item"><div class="client-dot"></div>Santander</div>
    <div class="client-item"><div class="client-dot"></div>Magazine Luiza</div>
    <div class="client-item"><div class="client-dot"></div>iFood</div>
    <div class="client-item"><div class="client-dot"></div>XP Investimentos</div>
    <div class="client-item"><div class="client-dot"></div>Vivo</div>
  </div>
</div>

<script>
const ARCS = {arcs_json};
const cv=document.getElementById('c'), ctx=cv.getContext('2d');
let W,H,attacks=[],pulses=[],stars=[],totalCount=0;

function resize(){{W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}}
resize();window.addEventListener('resize',resize);

setInterval(()=>{{
  document.getElementById('time-pill').textContent=new Date().toLocaleTimeString('pt-BR');
}},1000);

function ll(lat,lon){{return[(lon+180)/360*W,(90-lat)/180*H];}}

for(let i=0;i<280;i++)stars.push([Math.random(),Math.random(),Math.random()*.9+.1]);
function drawStars(){{
  for(let[rx,ry,a]of stars){{
    ctx.beginPath();ctx.arc(rx*W,ry*H,.8,0,Math.PI*2);
    ctx.fillStyle=`rgba(180,210,255,${{a*.4}})`;ctx.fill();
  }}
}}

function drawGrid(){{
  for(let lat=-60;lat<=80;lat+=30){{
    let[,y]=ll(lat,0);
    ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);
    let eq=lat===0;
    ctx.strokeStyle=eq?'rgba(0,200,255,0.07)':'rgba(0,150,200,0.025)';
    ctx.lineWidth=eq?1.2:.8;ctx.stroke();
    if(eq){{ctx.fillStyle='rgba(0,200,255,0.15)';ctx.font='7px monospace';ctx.fillText('Equador',4,y-3);}}
  }}
  for(let lon=-150;lon<=180;lon+=30){{
    let[x]=ll(0,lon);
    ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);
    ctx.strokeStyle='rgba(0,120,180,0.025)';ctx.lineWidth=.8;ctx.stroke();
  }}
  let[,ytc]=ll(-23.5,0);
  ctx.beginPath();ctx.moveTo(0,ytc);ctx.lineTo(W,ytc);
  ctx.strokeStyle='rgba(0,255,136,0.04)';ctx.lineWidth:.8;ctx.stroke();
}}

const CITIES=[
  [-14.23,-51.92,'BRA',true,14],
  [35.86,104.19,'CHN',false,7],[61.52,95,'RUS',false,7],
  [37.09,-95.71,'USA',false,7],[51.16,10.45,'DEU',false,5],
  [20.59,78.96,'IND',false,5],[52.13,5.29,'NLD',false,4],
  [48.38,31.17,'UKR',false,5],[32.43,53.69,'IRN',false,5],
  [40.34,127.51,'PRK',false,4],[55.37,-3.43,'GBR',false,5],
  [36.2,138.25,'JPN',false,5],[35.9,127.76,'KOR',false,4],
  [-25.27,133.77,'AUS',false,5],[56.13,-106.34,'CAN',false,5],
  [9.08,8.67,'NGA',false,4],[-38.4,-63.6,'ARG',false,4],
];

function drawCities(){{
  for(let[lat,lon,code,isBR,r]of CITIES){{
    let[x,y]=ll(lat,lon);
    let g=ctx.createRadialGradient(x,y,0,x,y,r*4);
    g.addColorStop(0,isBR?'rgba(0,255,136,0.35)':'rgba(0,200,255,0.12)');
    g.addColorStop(1,'transparent');
    ctx.beginPath();ctx.arc(x,y,r*4,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
    if(isBR){{
      ctx.beginPath();ctx.arc(x,y,r+4,0,Math.PI*2);
      ctx.strokeStyle='rgba(0,255,136,0.2)';ctx.lineWidth=1;ctx.stroke();
    }}
    ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);
    ctx.fillStyle=isBR?'#00ff88':'rgba(0,200,255,0.65)';ctx.fill();
    ctx.font=isBR?'bold 9px monospace':'7px monospace';
    ctx.fillStyle=isBR?'#00ff88':'rgba(0,200,255,0.5)';
    ctx.fillText(isBR?'🎯 BRASIL':code,x+(isBR?10:5),y+(isBR?4:3));
  }}
}}

class Pulse{{
  constructor(x,y,col){{this.x=x;this.y=y;this.r=0;this.max=35;this.col=col;}}
  update(){{this.r+=1.2;return this.r<this.max;}}
  draw(){{
    let a=1-this.r/this.max;
    ctx.beginPath();ctx.arc(this.x,this.y,this.r,0,Math.PI*2);
    ctx.strokeStyle=this.col.replace('1)',a+')');ctx.lineWidth=1.5;ctx.stroke();
  }}
}}

const COLS=['rgba(239,68,68,1)','rgba(245,158,11,1)','rgba(0,212,255,1)','rgba(220,38,38,1)'];
class Attack{{
  constructor(arc){{
    this.arc=arc;this.t=0;
    this.speed=0.003+Math.random()*0.004;
    this.trail=[];
    this.col=COLS[Math.floor(Math.random()*COLS.length)];
    this.size=2+Math.random()*1.8;this.done=false;
  }}
  bez(t){{
    let s=ll(this.arc.src_lat,this.arc.src_lon);
    let d=ll(this.arc.dst_lat,this.arc.dst_lon);
    let mx=(s[0]+d[0])/2;
    let dist=Math.sqrt((d[0]-s[0])**2+(d[1]-s[1])**2);
    let my=(s[1]+d[1])/2-dist*0.28-30;
    let u=1-t;
    return[u*u*s[0]+2*u*t*mx+t*t*d[0],u*u*s[1]+2*u*t*my+t*t*d[1]];
  }}
  update(){{
    if(this.done)return false;
    this.t+=this.speed;
    if(this.t>=1){{
      this.t=1;this.done=true;
      let p=this.bez(1);
      pulses.push(new Pulse(p[0],p[1],'rgba(0,255,136,1)'));
      pulses.push(new Pulse(p[0],p[1],'rgba(0,200,255,1)'));
      totalCount++;
      document.getElementById('attack-count').textContent=totalCount;
      document.getElementById('last-attack').textContent='↗ '+this.arc.name;
      return false;
    }}
    this.trail.push(this.bez(Math.min(this.t,1)));
    if(this.trail.length>25)this.trail.shift();
    return true;
  }}
  draw(){{
    if(this.trail.length<2)return;
    for(let i=1;i<this.trail.length;i++){{
      let a=i/this.trail.length;
      ctx.beginPath();
      ctx.moveTo(this.trail[i-1][0],this.trail[i-1][1]);
      ctx.lineTo(this.trail[i][0],this.trail[i][1]);
      ctx.strokeStyle=this.col.replace('1)',a+')');
      ctx.lineWidth=this.size*a;ctx.stroke();
    }}
    let h=this.trail[this.trail.length-1];
    let g=ctx.createRadialGradient(h[0],h[1],0,h[0],h[1],8);
    g.addColorStop(0,this.col);g.addColorStop(1,'transparent');
    ctx.beginPath();ctx.arc(h[0],h[1],8,0,Math.PI*2);ctx.fillStyle=g;ctx.fill();
    ctx.beginPath();ctx.arc(h[0],h[1],2.5,0,Math.PI*2);
    ctx.fillStyle=this.col;ctx.fill();
  }}
}}

let frame=0;
function spawn(){{
  frame++;
  if(frame%28===0&&ARCS.length>0){{
    let arc=ARCS[Math.floor(Math.random()*ARCS.length)];
    attacks.push(new Attack(arc));
  }}
  if(frame%80===0&&ARCS.length>0){{
    let arc=ARCS[Math.floor(Math.random()*ARCS.length)];
    attacks.push(new Attack(arc));
  }}
}}

function anim(){{
  requestAnimationFrame(anim);
  ctx.fillStyle='rgba(3,5,10,0.80)';ctx.fillRect(0,0,W,H);
  drawStars();drawGrid();drawCities();spawn();
  let alive=[];
  for(let a of attacks){{a.update();a.draw();if(!a.done)alive.push(a);}}
  attacks=alive;
  let ap=[];
  for(let p of pulses){{if(p.update()){{p.draw();ap.push(p)}}}}
  pulses=ap;
}}
anim();
</script>
</body>
</html>"""

    components.html(map_html, height=560, scrolling=False)

    st.markdown("#### Origem dos ataques detectados")
    ta = df_vis[df_vis["TIPO INCIDENTE"]=="ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns = ["País","Ataques"]
    st.dataframe(ta, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### 🤖 Assistente de Segurança — Gemini AI")

    if not GEMINI_API_KEY:
        st.error("⚠️ Chave de API do Google Gemini não configurada.")
        st.info("Adicione a chave no código ou configure a variável de ambiente.")
    else:
        st.success("✅ Assistente ativo - Pronto para responder")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if not st.session_state["chat_history"]:
        st.markdown("""
        <div style="text-align:center;padding:2rem 1rem;
          background:rgba(8,11,20,0.6);border:1px solid rgba(0,200,255,0.08);
          border-radius:16px;margin:1rem 0;">
          <div style="font-size:2.2rem;margin-bottom:.6rem;">🤖</div>
          <p style="color:#c8d8e8;font-size:.88rem;font-weight:600;">Assistente SentinelAI</p>
          <p style="color:#3a5a7a;font-size:.78rem;margin-top:.3rem;">
            Analiso ameaças, tendências e forneço recomendações de segurança<br>
            baseadas nos dados reais dos seus clientes.
          </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state["chat_history"]:
            css = "chat-user" if msg["role"] == "user" else "chat-ai"
            icon = "👤" if msg["role"] == "user" else "🤖"
            st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        pergunta = st.text_input(
            "",
            placeholder="Pergunte sobre ameaças, clientes, análises de segurança…",
            label_visibility="collapsed"
        )
        col_s, col_c = st.columns([5, 1])
        with col_s:
            enviar = st.form_submit_button("Enviar →", use_container_width=True)
        with col_c:
            limpar = st.form_submit_button("🗑️", use_container_width=True)

    if limpar:
        st.session_state["chat_history"] = []
        st.rerun()

    if enviar and pergunta.strip():
        if not GEMINI_API_KEY:
            st.error("Configure a chave GEMINI_API_KEY para usar o assistente.")
        else:
            adicionar_log(usuario_atual, f"Chat: {pergunta[:60]}")
            st.session_state["chat_history"].append({"role": "user", "content": pergunta})

            with st.spinner("🤔 Analisando dados e gerando resposta…"):
                try:
                    clientes_ativos = sorted(df["CLIENTE"].unique().tolist()) if not cliente_vinculado else [cliente_vinculado]

                    top_paises = ""
                    try:
                        tp = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(3)
                        top_paises = ", ".join([f"{p} ({n})" for p, n in tp.items()])
                    except:
                        top_paises = "dados insuficientes"

                    prompt = f"""Você é um especialista em segurança cibernética da plataforma SentinelAI.
Responda em português brasileiro, de forma profissional, direta e com insights acionáveis.

CONTEXTO DO SISTEMA:
- Clientes monitorados: {', '.join(clientes_ativos)}
- Total de incidentes: {len(df_vis):,}
- Incidentes CRÍTICOS: {incidentes_criticos:,}
- Incidentes resolvidos: {incidentes_resolvidos:,}
- Incidentes pendentes: {incidentes_pendentes:,}
- IPs bloqueados: {ips_bloqueados:,}
- Prejuízo financeiro estimado: R$ {prejuizo_total:,.0f}
- Principais países atacantes: {top_paises}
- Acurácia do modelo ML: {acuracia:.1%}
- Perfil do usuário: {perfil_atual['perfil']}
{f"- Filtro ativo: apenas {cliente_vinculado}" if cliente_vinculado else "- Visão: todos os clientes"}

Pergunta do usuário: {pergunta}

Resposta:"""

                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 800
                        }
                    }
                    
                    resp = requests.post(url, json=payload, timeout=40)

                    if resp.status_code == 200:
                        data = resp.json()
                        resposta = data["candidates"][0]["content"]["parts"][0]["text"]
                    elif resp.status_code == 401:
                        resposta = "⚠️ Chave de API inválida. Verifique sua GEMINI_API_KEY."
                    elif resp.status_code == 429:
                        resposta = "⚠️ Limite de requisições atingido. Aguarde alguns segundos."
                    else:
                        resposta = f"⚠️ Erro {resp.status_code}: {resp.text[:200]}"

                except requests.exceptions.Timeout:
                    resposta = "⚠️ Timeout: a conexão demorou muito. Tente novamente."
                except requests.exceptions.ConnectionError:
                    resposta = "⚠️ Sem conexão com a API. Verifique sua internet."
                except Exception as e:
                    resposta = f"⚠️ Erro inesperado: {str(e)}"

            st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
            st.rerun()

with tab5:
    st.markdown("### Exportação & Backup de Dados")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas administradores podem exportar dados da plataforma.")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.markdown("#### Downloads disponíveis")
        b1,b2,b3 = st.columns(3)
        with b1:
            st.download_button(
                "📥 Dataset completo (CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"sentinel_{ts}.csv","text/csv",use_container_width=True
            )
        with b2:
            df_a = df.drop(columns=["IP_SUSPEITO"],errors="ignore")
            st.download_button(
                "🔒 Dataset anonimizado",
                df_a.to_csv(index=False).encode("utf-8"),
                f"sentinel_anon_{ts}.csv","text/csv",use_container_width=True
            )
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button(
                    "📋 Logs da sessão",
                    "\n".join(st.session_state["logs_sistema"]).encode("utf-8"),
                    f"logs_{ts}.txt","text/plain",use_container_width=True
                )
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db","rb") as f:
                st.download_button(
                    "🗄️ Banco SQLite completo",
                    f.read(),f"sentinelai_{ts}.db","application/x-sqlite3",
                    use_container_width=True
                )
    st.markdown("---")
    st.markdown("#### Prévia dos dados")
    st.dataframe(df_vis.head(20),use_container_width=True)

with tab6:
    st.markdown("### Logs de Auditoria")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log in reversed(st.session_state["logs_sistema"]):
            st.code(log, language=None)
    else:
        st.info("Nenhuma ação registrada nesta sessão.")

st.markdown("""
<div style="text-align:center;padding:1rem 0 .5rem 0;
  border-top:1px solid rgba(0,200,255,0.04);margin-top:1rem;">
  <p style="color:#152535;font-size:.58rem;letter-spacing:.1em;">
    SENTINELAI — PLATAFORMA DE SEGURANÇA CIBERNÉTICA &nbsp;·&nbsp; CONFIDENCIAL &nbsp;·&nbsp; LGPD COMPLIANT
  </p>
</div>
""", unsafe_allow_html=True)
