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

*{margin:0;padding:0;box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;}
.stApp{background:#060810;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#050709 0%,#080b12 100%);border-right:1px solid rgba(0,200,255,0.06);}
.block-container{padding:1.2rem 1.5rem;max-width:100%;}

div[data-testid="metric-container"]{
  background:linear-gradient(135deg,rgba(0,200,255,0.04),rgba(6,8,16,0.97));
  border:1px solid rgba(0,200,255,0.11);
  border-radius:14px;padding:1rem 1.2rem;
  transition:all .25s ease;
}
div[data-testid="metric-container"]:hover{
  border-color:rgba(0,200,255,0.25);transform:translateY(-3px);
}
[data-testid="stMetricLabel"]{color:#4a6a8a!important;font-size:.58rem!important;text-transform:uppercase;}
[data-testid="stMetricValue"]{color:#00d4ff!important;font-size:1.4rem!important;font-weight:700;}

div.stButton>button{
  background:linear-gradient(135deg,#005f8a,#0097c4);
  color:white;border-radius:10px;border:none;
  padding:.55rem 1rem;font-weight:600;font-size:.8rem;
  transition:all .2s ease;width:100%;
}
div.stButton>button:hover{
  background:linear-gradient(135deg,#0077aa,#00b8e0);
  transform:translateY(-2px);
}

.chat-user{
  background:linear-gradient(135deg,#005f8a,#0097c4);
  border-radius:18px 18px 4px 18px;padding:.7rem 1.1rem;
  margin:.5rem 0 .5rem auto;max-width:78%;width:fit-content;
  color:white;font-size:.82rem;
}
.chat-ai{
  background:rgba(8,11,20,0.96);
  border:1px solid rgba(0,200,255,0.12);
  border-radius:18px 18px 18px 4px;padding:.7rem 1.1rem;
  margin:.5rem 0;max-width:78%;width:fit-content;
  color:#c8d8e8;font-size:.82rem;
}

.sentinel-header{
  background:linear-gradient(135deg,rgba(0,200,255,0.04),rgba(0,60,120,0.03));
  border:1px solid rgba(0,200,255,0.09);border-radius:16px;
  padding:1.2rem 1.8rem;margin-bottom:1.2rem;
}

.badge-online{
  display:inline-flex;align-items:center;gap:.3rem;
  background:rgba(0,255,100,.06);border:1px solid rgba(0,255,100,.18);
  color:#00ff88;padding:.25rem .8rem;border-radius:20px;
  font-size:.58rem;font-weight:700;
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
  padding:.45rem .9rem;font-size:.75rem;
}
.stTabs [aria-selected="true"]{background:rgba(0,160,200,.1)!important;color:#00d4ff!important;}

input,textarea,select{background:rgba(8,11,20,0.92)!important;border:1px solid rgba(0,200,255,.1)!important;border-radius:10px!important;color:white!important;}
hr{border-color:rgba(0,200,255,.05);margin:1rem 0;}
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
    "admin": {"senha":"admin123", "perfil":"Administrador","pode_exportar":True, "pode_analisar":True, "ver_pii":True, "cliente_vinculado":None},
    "analista": {"senha":"analista123", "perfil":"Analista", "pode_exportar":False,"pode_analisar":True, "ver_pii":False, "cliente_vinculado":None},
    "nubank": {"senha":"nubank123", "perfil":"Cliente", "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Nubank"},
    "mercadolivre": {"senha":"ml123", "perfil":"Cliente", "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Mercado Livre"},
    "santander": {"senha":"sant123", "perfil":"Cliente", "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":"Santander"},
    "viewer": {"senha":"viewer123", "perfil":"Visualizador", "pode_exportar":False,"pode_analisar":False,"ver_pii":False, "cliente_vinculado":None},
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
    <div style="position:fixed;bottom:0;left:0;right:0;z-index:9999;background:rgba(5,8,14,0.97);border-top:1px solid rgba(0,200,255,0.18);padding:1rem 2rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
      <div><p style="color:white;font-size:.82rem;">🍪 Privacidade & Cookies — LGPD (Lei 13.709/2018)</p></div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([6,1,1])
    with col2:
        if st.button("Recusar"):
            st.warning("Aceite para continuar.")
    with col3:
        if st.button("✓ Aceitar"):
            st.session_state["lgpd_aceito"] = True
            st.rerun()
    st.stop()

if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;}header{display:none!important;}</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.3,1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;">
          <div style="font-size:3rem;">🛡️</div>
          <h1 style="color:#fff;font-size:2rem;">Sentinel<span style="color:#00d4ff;">AI</span></h1>
          <p style="color:#4a6a8a;">Plataforma de Segurança Cibernética</p>
          <span class="badge-online">● SISTEMA OPERACIONAL</span>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            usuario_input = st.text_input("Usuário", placeholder="admin, analista, nubank...", label_visibility="collapsed")
            senha_input = st.text_input("Senha", type="password", placeholder="••••••••", label_visibility="collapsed")
            if st.form_submit_button("Entrar", use_container_width=True):
                if autenticar(usuario_input.strip(), senha_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = usuario_input.strip()
                    adicionar_log(usuario_input.strip(), "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
        st.markdown("""
        <div style="margin-top:1rem;background:rgba(0,200,255,0.02);border-radius:14px;padding:1rem;text-align:center;">
          <p style="color:#6a8aaa;font-size:.7rem;">admin/admin123 | analista/analista123 | nubank/nubank123</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual = USUARIOS[usuario_atual]

if "sqlite_conn" not in st.session_state:
    st.session_state["sqlite_conn"] = conectar_sqlite()
    if st.session_state["sqlite_conn"]:
        inicializar_sqlite(st.session_state["sqlite_conn"])

sqlite_conn = st.session_state["sqlite_conn"]
sqlite_ativo = sqlite_conn is not None

@st.cache_data
def carregar_dados():
    df = pd.read_csv("dataset_final.csv").dropna(subset=["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"])
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo","origem","status","severidade"]}
    df["TIPO_ENC"] = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"] = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"] = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"] = enc["severidade"].fit_transform(df["SEVERIDADE"])
    X = df[["TIPO_ENC","ORIGEM_ENC","TEMPO RESOLUÇÃO","STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.2,random_state=42)
    m = DecisionTreeClassifier(random_state=42)
    m.fit(Xtr,ytr)
    return df, enc, m, accuracy_score(yte,m.predict(Xte)), Xte, yte

df, encoders, modelo, acuracia, X_test, y_test = carregar_dados()

cliente_vinculado = perfil_atual["cliente_vinculado"]
df_vis = df[df["CLIENTE"]==cliente_vinculado].copy() if cliente_vinculado else df.copy()
salvar_backup_sessao(df_vis, usuario_atual, "Login")

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:.8rem 0;'><div style='font-size:2rem;'>🛡️</div><h3 style='color:#00d4ff;'>SentinelAI</h3></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='background:rgba(0,200,255,.03);border-radius:12px;padding:.7rem;'><p style='color:#2a4060;font-size:.52rem;'>PERFIL</p><p style='color:white;font-weight:700;'>{perfil_atual['perfil']}</p><p style='color:#4a6a8a;font-size:.62rem;'>@{usuario_atual}</p></div>", unsafe_allow_html=True)
    st.markdown('<span class="badge-db">📁 SQLite Ativo</span>' if sqlite_ativo else '<span style="color:#ff4444;">⚠️ Offline</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Permissões")
    for nome, ativo in [("Análise ML",perfil_atual["pode_analisar"]),("Exportar",perfil_atual["pode_exportar"]),("Ver IPs",perfil_atual["ver_pii"])]:
        c,i = ("#00ff88","✓") if ativo else ("#ff4444","✗")
        st.markdown(f"<p style='color:{c};font-size:.7rem;'>{i} {nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='background:rgba(0,200,255,.03);border-radius:10px;padding:.7rem;text-align:center;'><p style='color:#2a4060;font-size:.52rem;'>Acurácia</p><p style='color:#00d4ff;font-size:1.35rem;font-weight:700;'>{acuracia:.1%}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado":False,"usuario_atual":None})
        st.rerun()

now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"""
<div class="sentinel-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
    <div><p style="color:#2a4060;font-size:.55rem;">{f"Cliente: {cliente_vinculado}" if cliente_vinculado else "Visão Global"}</p><h1 style="color:white;margin:0;font-size:1.2rem;">Painel de Segurança Cibernética</h1></div>
    <div style="text-align:right;"><span class="badge-online">● PROTEGIDO</span><p style="color:#2a4060;font-size:.55rem;">{now_str}</p></div>
  </div>
</div>
""", unsafe_allow_html=True)

total_incidentes = len(df_vis)
incidentes_criticos = len(df_vis[df_vis["SEVERIDADE"]=="crítica"])
ips_bloqueados = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
prejuizo_total = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"]=="resolvido"])
incidentes_pendentes = len(df_vis[df_vis["STATUS"]=="pendente"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
pf = f"R$ {prejuizo_total:,.0f}".replace(",","X").replace(".",",").replace("X",".")
with c1: st.metric("Total", f"{total_incidentes:,}")
with c2: st.metric("Críticos", f"{incidentes_criticos:,}")
with c3: st.metric("IPs Bloqueados", f"{ips_bloqueados:,}")
with c4: st.metric("Resolvidos", f"{incidentes_resolvidos:,}")
with c5: st.metric("Pendentes", f"{incidentes_pendentes:,}")
with c6: st.metric("Prejuízo", pf)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔍 Análise", "📊 Métricas", "🌍 Mapa", "🤖 Chat", "💾 Backup", "📋 Logs"])

with tab1:
    st.markdown("### Análise de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Sem permissão")
    else:
        tipos = [str(v).strip() for v in encoders["tipo"].classes_]
        origens = [str(v).strip() for v in encoders["origem"].classes_]
        status_opts = [str(v).strip() for v in encoders["status"].classes_]
        clientes = sorted([str(c).strip() for c in df["CLIENTE"].unique()])

        ca, cb = st.columns(2)
        with ca:
            tipo_incidente = st.selectbox("Tipo", tipos)
            origem_ataque = st.selectbox("Origem", origens)
            cliente_afetado = st.selectbox("Cliente", clientes)
        with cb:
            tempo_resolucao = st.slider("Tempo (min)", 1, 120, 30)
            status_atual = st.selectbox("Status", status_opts)

        if st.button("🚀 Analisar", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: {tipo_incidente}")
            with st.spinner("Processando..."):
                time.sleep(1)
            entrada = pd.DataFrame({
                "TIPO_ENC": [encoders["tipo"].transform([tipo_incidente])[0]],
                "ORIGEM_ENC": [encoders["origem"].transform([origem_ataque])[0]],
                "TEMPO RESOLUÇÃO": [tempo_resolucao],
                "STATUS_ENC": [encoders["status"].transform([status_atual])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status_atual == "resolvido":
                resultado = "baixa"
            elif tipo_incidente in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo_incidente in ["lentidão", "erro sistema"]:
                resultado = random.choice(["baixa", "média"])
            risco = random.randint(10, 99)
            prej_est = random.uniform(3000, 30000)
            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 Severidade: CRÍTICA")
            elif resultado == "média":
                st.warning(f"🟡 Severidade: MÉDIA")
            else:
                st.success(f"🟢 Severidade: BAIXA")
            r1, r2, r3 = st.columns(3)
            with r1: st.metric("Risco", f"{risco}/100")
            with r2: st.metric("Prejuízo", f"R$ {prej_est:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with r3: st.metric("Cliente", cliente_afetado)
            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {"usuario": usuario_atual, "tipo": tipo_incidente, "origem": origem_ataque, "status": status_atual, "severidade": resultado, "cliente": cliente_afetado})
                st.success("💾 Registrado")

with tab2:
    st.markdown("### Métricas")
    L = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#6a8aaa")
    g1, g2 = st.columns(2)
    with g1:
        fig = px.pie(df_vis, names="SEVERIDADE", title="Severidade", color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig.update_layout(**L); st.plotly_chart(fig, use_container_width=True)
    with g2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Por Tipo", color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig, use_container_width=True)
    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig = px.area(df_time, x="DATA", y="Incidentes", title="Volume", color_discrete_sequence=["#00d4ff"])
    fig.update_layout(**L); st.plotly_chart(fig, use_container_width=True)
    cm = confusion_matrix(y_test, modelo.predict(X_test))
    labels = encoders["severidade"].classes_
    fig = go.Figure(go.Heatmap(z=cm, x=labels, y=labels, colorscale=[[0, "#060810"], [1, "#00d4ff"]], text=cm, texttemplate="%{text}", showscale=True))
    fig.update_layout(title="Matriz de Confusão", height=320, **L)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### 🌍 Mapa Global de Ameaças")
    st.caption("Visualização de ataques em tempo real com contornos dos continentes")
    
    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "Germany": (51.16, 10.45), "India": (20.59, 78.96), "France": (46.23, 2.21),
        "Ukraine": (48.38, 31.17), "Iran": (32.43, 53.69), "North Korea": (40.34, 127.51),
        "United Kingdom": (55.37, -3.43), "Japan": (36.2, 138.25), "Australia": (-25.27, 133.77),
        "Canada": (56.13, -106.34), "South Korea": (35.9, 127.76), "Brazil": (-14.23, -51.92)
    }
    TARGET = (-15.78, -47.92)
    
    attack_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    cc = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country", "total"]
    
    arcs = []
    for _, row in cc.iterrows():
        c = row["country"]
        if c in COORDS:
            s = COORDS[c]
            arcs.append({"src_lat": s[0], "src_lon": s[1], "dst_lat": TARGET[0], "dst_lon": TARGET[1], "name": c, "count": int(row["total"])})
    
    arcs_json = json.dumps(arcs)
    
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><style>
        body{{margin:0;background:#060810;overflow:hidden;}}
        canvas{{display:block;}}
        .info{{position:absolute;bottom:15px;left:15px;background:rgba(0,0,0,0.7);border:1px solid #00d4ff;border-radius:8px;padding:8px 15px;color:#00d4ff;font-size:12px;z-index:100;font-family:monospace;}}
        .stats{{position:absolute;top:15px;right:15px;background:rgba(0,0,0,0.7);border:1px solid #00d4ff;border-radius:8px;padding:8px 15px;color:#00d4ff;font-size:12px;z-index:100;text-align:center;}}
    </style></head>
    <body>
    <canvas id="c"></canvas>
    <div class="info">🌍 ATAQUES DIRECIONADOS AO BRASIL</div>
    <div class="stats" id="attackStats">ATAQUES: 0</div>
    <script>
        var arcs = {arcs_json};
        var canvas = document.getElementById('c');
        var ctx = canvas.getContext('2d');
        var w, h, particles = [];
        var attackCount = 0;
        
        function resize() {{ w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }}
        resize();
        window.addEventListener('resize', resize);
        
        function latLonToXY(lat, lon) {{ return [(lon + 180) / 360 * w, (90 - lat) / 180 * h]; }}
        
        var countryPoints = [
            [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],[51.16,10.45,"DEU"],
            [-14.23,-51.92,"BRA"],[20.59,78.96,"IND"],[46.23,2.21,"FRA"],[48.38,31.17,"UKR"],
            [32.43,53.69,"IRN"],[40.34,127.51,"PRK"],[55.37,-3.43,"GBR"],[36.2,138.25,"JPN"],
            [-25.27,133.77,"AUS"],[56.13,-106.34,"CAN"],[35.9,127.76,"KOR"]
        ];
        
        function drawWorldMap() {{
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(0,200,255,0.15)';
            ctx.lineWidth = 0.5;
            for (var lon = -180; lon <= 180; lon += 30) {{
                var p1 = latLonToXY(0, lon);
                ctx.beginPath();
                ctx.moveTo(p1[0], 0);
                ctx.lineTo(p1[0], h);
                ctx.stroke();
            }}
            for (var lat = -90; lat <= 90; lat += 30) {{
                var p1 = latLonToXY(lat, 0);
                ctx.beginPath();
                ctx.moveTo(0, p1[1]);
                ctx.lineTo(w, p1[1]);
                ctx.stroke();
            }}
            for (var c of countryPoints) {{
                var p = latLonToXY(c[0], c[1]);
                var isTarget = c[2] === "BRA";
                ctx.beginPath();
                ctx.arc(p[0], p[1], isTarget ? 10 : 4, 0, Math.PI * 2);
                ctx.fillStyle = isTarget ? '#00ff00' : 'rgba(0,200,255,0.3)';
                ctx.fill();
                ctx.beginPath();
                ctx.arc(p[0], p[1], isTarget ? 14 : 6, 0, Math.PI * 2);
                ctx.strokeStyle = isTarget ? 'rgba(0,255,0,0.4)' : 'rgba(0,200,255,0.2)';
                ctx.stroke();
                ctx.fillStyle = isTarget ? '#00ff00' : 'rgba(0,200,255,0.8)';
                ctx.font = isTarget ? 'bold 12px monospace' : '10px monospace';
                ctx.fillText(c[2], p[0] + 8, p[1] + 4);
            }}
        }}
        
        function Particle(arc) {{
            this.arc = arc;
            this.t = 0;
            this.speed = 0.003 + Math.random() * 0.004;
            this.trail = [];
            this.pos = function(t) {{
                var s = latLonToXY(this.arc.src_lat, this.arc.src_lon);
                var d = latLonToXY(this.arc.dst_lat, this.arc.dst_lon);
                var mx = (s[0] + d[0]) / 2;
                var my = Math.min(s[1], d[1]) - Math.abs(d[0] - s[0]) * 0.25;
                var u = 1 - t;
                return [u*u*s[0] + 2*u*t*mx + t*t*d[0], u*u*s[1] + 2*u*t*my + t*t*d[1]];
            }};
            this.update = function() {{
                this.t += this.speed;
                this.trail.push(this.pos(Math.min(this.t, 1)));
                if (this.trail.length > 25) this.trail.shift();
                return this.t < 1;
            }};
            this.draw = function() {{
                if (this.trail.length < 2) return;
                for (var i = 1; i < this.trail.length; i++) {{
                    var alpha = i / this.trail.length;
                    ctx.beginPath();
                    ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
                    ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                    ctx.strokeStyle = 'rgba(0,200,255,' + alpha + ')';
                    ctx.lineWidth = 2.5 * alpha;
                    ctx.stroke();
                }}
                var last = this.trail[this.trail.length - 1];
                ctx.beginPath();
                ctx.arc(last[0], last[1], 4, 0, Math.PI * 2);
                ctx.fillStyle = '#00d4ff';
                ctx.fill();
            }};
        }}
        
        function spawn() {{
            if (arcs.length && Math.random() < 0.12) {{
                var idx = Math.floor(Math.random() * arcs.length);
                particles.push(new Particle(arcs[idx]));
            }}
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            ctx.fillStyle = '#060810';
            ctx.fillRect(0, 0, w, h);
            drawWorldMap();
            spawn();
            var alive = [];
            for (var p of particles) {{
                if (p.update()) {{
                    p.draw();
                    alive.push(p);
                }} else {{
                    attackCount++;
                    document.getElementById('attackStats').innerHTML = 'ATAQUES: ' + attackCount;
                }}
            }}
            particles = alive;
        }}
        
        animate();
    </script>
    </body>
    </html>
    """
    components.html(map_html, height=550, scrolling=False)
    
    st.markdown("#### Países com mais ataques")
    ta = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns = ["País", "Ataques"]
    st.dataframe(ta, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### 🤖 Assistente de Segurança")
    
    if not GEMINI_API_KEY:
        st.error("⚠️ Chave de API não configurada.")
    else:
        st.success("✅ Assistente ativo")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # Exibir histórico de mensagens
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    
    # Formulário para nova pergunta
    with st.form("chat_form", clear_on_submit=True):
        pergunta = st.text_input("", placeholder="Digite sua pergunta sobre segurança...", label_visibility="collapsed")
        col1, col2 = st.columns([5, 1])
        with col1:
            enviar = st.form_submit_button("📤 Enviar", use_container_width=True)
        with col2:
            limpar = st.form_submit_button("🗑️ Limpar", use_container_width=True)
    
    if limpar:
        st.session_state["chat_history"] = []
        st.rerun()
    
    if enviar and pergunta.strip():
        if GEMINI_API_KEY:
            st.session_state["chat_history"].append({"role": "user", "content": pergunta})
            with st.spinner("🤔 Processando..."):
                try:
                    prompt = f"""Você é um especialista em segurança cibernética da SentinelAI. Responda em português de forma profissional e direta.

DADOS DO SISTEMA:
- Total de incidentes: {len(df_vis)}
- Incidentes críticos: {incidentes_criticos}
- IPs bloqueados: {ips_bloqueados}
- Prejuízo total estimado: R$ {prejuizo_total:,.0f}
- Acurácia do modelo de IA: {acuracia:.1%}
- Clientes monitorados: {', '.join(df_vis['CLIENTE'].unique()[:5])}

Pergunta: {pergunta}

Resposta:"""
                    
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    resp = requests.post(url, json=payload, timeout=30)
                    
                    if resp.status_code == 200:
                        resposta = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        resposta = f"Erro {resp.status_code}: Tente novamente."
                except Exception as e:
                    resposta = f"Erro de conexão: {str(e)[:100]}"
            
            st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
            st.rerun()

with tab5:
    st.markdown("### Backup")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas administradores")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button("📥 Exportar CSV", df.to_csv(index=False).encode("utf-8"), f"sentinel_{ts}.csv", "text/csv", use_container_width=True)

with tab6:
    st.markdown("### Logs")
    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log in reversed(st.session_state["logs_sistema"][-30:]):
            st.code(log, language=None)
    else:
        st.info("Nenhum log registrado")

st.markdown("""
<div style="text-align:center;padding:1rem 0;border-top:1px solid rgba(0,200,255,0.05);margin-top:1rem;">
  <p style="color:#152535;font-size:.6rem;">SENTINELAI — SEGURANÇA CIBERNÉTICA | LGPD</p>
</div>
""", unsafe_allow_html=True)
