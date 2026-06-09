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
div[data-testid="metric-container"]{background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(6,11,24,0.9));border:1px solid rgba(0,212,255,0.12);border-radius:14px;padding:1rem 1.2rem;transition:all .25s ease;}
div[data-testid="metric-container"]:hover{border-color:rgba(0,212,255,0.35);transform:translateY(-2px);}
[data-testid="stMetricLabel"]{color:#5a7a9e!important;font-size:.65rem!important;text-transform:uppercase;letter-spacing:.1em;}
[data-testid="stMetricValue"]{color:#00d4ff!important;font-size:1.6rem!important;font-weight:700;font-family:'JetBrains Mono',monospace;}
div.stButton>button{background:linear-gradient(135deg,#0077b6,#00b4d8);color:white;border-radius:10px;border:none;padding:.55rem 1rem;font-weight:600;transition:all .2s ease;width:100%;}
div.stButton>button:hover{background:linear-gradient(135deg,#0096c7,#00d4ff);transform:translateY(-1px);}
.chat-user{background:linear-gradient(135deg,#0077b6,#00b4d8);border-radius:18px 18px 4px 18px;padding:.75rem 1rem;margin:.5rem 0;margin-left:auto;max-width:82%;width:fit-content;color:white;font-size:.84rem;}
.chat-ai{background:rgba(10,17,40,.95);border:1px solid rgba(0,212,255,.18);border-radius:18px 18px 18px 4px;padding:.75rem 1rem;margin:.5rem 0;max-width:82%;width:fit-content;color:#d0dce8;font-size:.84rem;}
.sentinel-header{background:linear-gradient(135deg,rgba(0,180,216,.06),rgba(0,50,100,.04));border:1px solid rgba(0,212,255,.12);border-radius:18px;padding:1.4rem 1.8rem;margin-bottom:1.5rem;}
.badge-online{display:inline-block;background:rgba(0,255,100,.08);border:1px solid rgba(0,255,100,.25);color:#00ff64;padding:.25rem .75rem;border-radius:20px;font-size:.65rem;font-weight:600;}
.badge-db{display:inline-block;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);color:#00d4ff;padding:.25rem .75rem;border-radius:20px;font-size:.65rem;font-weight:600;}
.stTabs [data-baseweb="tab-list"]{background:rgba(10,17,40,.8);border-radius:14px;padding:.3rem;gap:.2rem;border:1px solid rgba(0,212,255,.08);}
.stTabs [data-baseweb="tab"]{border-radius:10px;color:#5a7a9e;font-weight:500;padding:.45rem 1rem;font-size:.8rem;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,180,216,.18),rgba(0,119,182,.1));color:#00d4ff!important;}
input,textarea,select{background:rgba(10,17,40,.9)!important;border:1px solid rgba(0,212,255,.15)!important;border-radius:10px!important;color:white!important;}
hr{border-color:rgba(0,212,255,.07);margin:1rem 0;}
code{background:rgba(0,212,255,.08);color:#00d4ff;border-radius:4px;padding:.1rem .4rem;}
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
    st.session_state["backups"].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "usuario": usuario, "motivo": motivo, "registros": len(df)
    })

def mascara_ip(ip):
    if ip == "Nenhum" or pd.isna(ip): return "***.***.***.***"
    p = str(ip).split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(0,180,216,.06),rgba(0,50,100,.04));
                    border:1px solid rgba(0,212,255,.15);border-radius:20px;
                    padding:2rem;margin:2rem 0;text-align:center;">
            <div style="font-size:3rem;">🔒</div>
            <h2 style="color:#00d4ff;">Política de Privacidade</h2>
            <p style="color:#8b9dc3;">Esta plataforma está em conformidade com a LGPD (Lei 13.709/2018).<br>Seus dados estão protegidos.</p>
            <div style="margin-top:1.5rem;"></div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Aceitar", use_container_width=True):
                st.session_state["cookies_aceitos"] = True
                adicionar_log("Sistema", "Termos aceitos")
                st.rerun()
        with c2:
            if st.button("❌ Recusar", use_container_width=True):
                st.stop()
    st.stop()

USUARIOS = {
    "admin": {"senha_hash": hashlib.sha256("admin123".encode()).hexdigest(), "perfil": "Administrador", "pode_exportar": True, "pode_analisar": True, "ver_pii": True, "cliente_vinculado": None},
    "analista": {"senha_hash": hashlib.sha256("analista123".encode()).hexdigest(), "perfil": "Analista", "pode_exportar": False, "pode_analisar": True, "ver_pii": False, "cliente_vinculado": None},
    "nubank": {"senha_hash": hashlib.sha256("nubank123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha_hash": hashlib.sha256("ml123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander": {"senha_hash": hashlib.sha256("sant123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer": {"senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(), "perfil": "Visualizador", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
}

def autenticar(u, s):
    return u in USUARIOS and hashlib.sha256(s.encode()).hexdigest() == USUARIOS[u]["senha_hash"]

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none;}
    header{display:none!important;}
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1rem 0;">
            <div style="font-size:4rem;">🛡️</div>
            <h1 style="color:#00d4ff;font-size:2.5rem;margin:0.5rem 0;">SentinelAI</h1>
            <p style="color:#8b9dc3;margin-bottom:1.5rem;">Plataforma de Inteligência contra Ameaças Cibernéticas</p>
            <div style="margin-bottom:1.5rem;"><span class="badge-online">● SISTEMA ATIVO</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            usuario_input = st.text_input("Usuário", placeholder="Digite seu usuário", key="login_user")
            senha_input = st.text_input("Senha", type="password", placeholder="••••••••", key="login_pass")
            submit = st.form_submit_button("🔐 Entrar", use_container_width=True)
            
            if submit:
                if autenticar(usuario_input, senha_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = usuario_input
                    adicionar_log(usuario_input, "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
        
        st.markdown("""
        <div style="background:rgba(0,180,216,.05);border-radius:12px;padding:0.8rem;margin-top:1rem;text-align:center;">
            <p style="color:#5a7a9e;font-size:0.7rem;">Acessos de demonstração: admin/admin123 | analista/analista123</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão iniciada")

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
    for col in ["TIPO INCIDENTE","SEVERIDADE","ORIGEM","STATUS","NIVEL_AMEACA","RISCO_FINANCEIRO"]:
        if col in df.columns: df[col] = df[col].str.strip().str.lower()
    enc = {k: LabelEncoder() for k in ["tipo","origem","status","severidade"]}
    df["TIPO_ENC"] = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"] = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"] = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"] = enc["severidade"].fit_transform(df["SEVERIDADE"])
    X = df[["TIPO_ENC","ORIGEM_ENC","TEMPO RESOLUÇÃO","STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    m = DecisionTreeClassifier(random_state=42)
    m.fit(Xtr, ytr)
    return df, enc, m, accuracy_score(yte, m.predict(Xte)), Xte, yte

df, encoders, modelo, acuracia, X_test, y_test = carregar_dados()
cliente_vinculado = perfil_atual["cliente_vinculado"]
df_vis = df[df["CLIENTE"]==cliente_vinculado].copy() if cliente_vinculado else df.copy()
salvar_backup_sessao(df_vis, usuario_atual, "Login")

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:2.5rem;">🛡️</div>
        <h3 style="color:#00d4ff;">SentinelAI</h3>
        <p style="color:#3a5a7e;font-size:.6rem;">CYBER INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,.05);border-radius:12px;padding:.8rem;margin:.5rem 0;">
        <p style="color:#3a5a7e;font-size:.6rem;">PERFIL</p>
        <p style="color:white;font-weight:600;">{perfil_atual['perfil']}</p>
        <p style="color:#5a7a9e;font-size:.7rem;">@{usuario_atual}</p>
    </div>""", unsafe_allow_html=True)
    badge_db = '<span class="badge-db">📁 SQLite Ativo</span>' if sqlite_ativo else '<span class="badge-db" style="border-color:#ff4444;color:#ff4444;">⚠️ Offline</span>'
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Permissões")
    for nome, ativo in [("📊 Análise",perfil_atual["pode_analisar"]),("📤 Exportar",perfil_atual["pode_exportar"]),("👁️ Ver IPs",perfil_atual["ver_pii"])]:
        c,i = ("#00ff64","✓") if ativo else ("#ff4444","✗")
        st.markdown(f"<p style='color:{c};font-size:.75rem;margin:.2rem 0;'>{i} {nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,.05);border-radius:12px;padding:.8rem;text-align:center;">
        <p style="color:#3a5a7e;font-size:.6rem;">ACURÁCIA</p>
        <p style="color:#00d4ff;font-size:1.5rem;font-weight:700;">{acuracia:.1%}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado":False,"usuario_atual":None})
        st.rerun()

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
        <div>
            <p style="color:#3a5a7e;font-size:.6rem;">BEM-VINDO, {usuario_atual.upper()}</p>
            <h1 style="color:white;margin:0;font-size:1.5rem;">Painel de Inteligência contra Ameaças</h1>
            <p style="color:#5a7a9e;margin-top:.3rem;">
                {f"Cliente: {cliente_vinculado}" if cliente_vinculado else "Visão Global"}
            </p>
        </div>
        <div style="text-align:right;">
            <span class="badge-online">● SISTEMA PROTEGIDO</span>
            <p style="color:#3a5a7e;font-size:.6rem;margin-top:.5rem;">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

total_incidentes = len(df_vis)
incidentes_criticos = len(df_vis[df_vis["SEVERIDADE"]=="crítica"])
ips_bloqueados = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower()=="sim"])
prejuizo_total = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"]=="resolvido"])
incidentes_pendentes = len(df_vis[df_vis["STATUS"]=="pendente"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.metric("Total Incidentes", f"{total_incidentes:,}")
with c2: st.metric("Críticos", f"{incidentes_criticos:,}")
with c3: st.metric("IPs Bloqueados", f"{ips_bloqueados:,}")
with c4: st.metric("Resolvidos", f"{incidentes_resolvidos:,}")
with c5: st.metric("Pendentes", f"{incidentes_pendentes:,}")
with c6:
    pf = f"R$ {prejuizo_total:,.0f}".replace(",","X").replace(".",",").replace("X",".")
    st.metric("Prejuízo", pf)

st.markdown("---")

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["🔍 Análise","📊 Métricas","🌍 Mapa","🤖 Assistente IA","💾 Backup","📋 Logs"])

with tab1:
    st.markdown("### Análise de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Sem permissão")
    else:
        ca,cb = st.columns(2)
        with ca:
            tipo_incidente = st.selectbox("Tipo", encoders["tipo"].classes_)
            origem_ataque = st.selectbox("Origem", encoders["origem"].classes_)
            cliente_afetado = st.selectbox("Cliente", sorted(df["CLIENTE"].unique()))
        with cb:
            tempo_resolucao = st.slider("Tempo (min)", 1, 120, 30)
            status_atual = st.selectbox("Status", encoders["status"].classes_)
        if st.button("🚀 Analisar", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: {tipo_incidente}")
            with st.spinner("Analisando..."):
                time.sleep(1)
            entrada = pd.DataFrame({
                "TIPO_ENC": [encoders["tipo"].transform([tipo_incidente])[0]],
                "ORIGEM_ENC": [encoders["origem"].transform([origem_ataque])[0]],
                "TEMPO RESOLUÇÃO": [tempo_resolucao],
                "STATUS_ENC": [encoders["status"].transform([status_atual])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status_atual=="resolvido": resultado="baixa"
            elif tipo_incidente in ["ataque","falha servidor"]: resultado="crítica"
            elif tipo_incidente in ["lentidão","erro sistema"]: resultado=random.choice(["baixa","média"])
            risco=random.randint(10,99)
            prej_est=random.uniform(3000,30000)
            risco_fin="ALTO" if prej_est>15000 else ("MÉDIO" if prej_est>7000 else "BAIXO")
            ataques=df[df["TIPO INCIDENTE"]=="ataque"]
            if not ataques.empty:
                l=ataques.sample(1).iloc[0]
                ip_ex=l["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(l["IP_SUSPEITO"])
                pais=l["PAIS_ATAQUE"]
            else:
                ip_ex,pais="DESCONHECIDO","INTERNO"
            st.markdown("---")
            if resultado=="crítica":
                st.error(f"🔴 Severidade: {resultado.upper()} — AÇÃO IMEDIATA")
            elif resultado=="média":
                st.warning(f"🟡 Severidade: {resultado.upper()} — MONITORAR")
            else:
                st.success(f"🟢 Severidade: {resultado.upper()} — BAIXO RISCO")
            r1,r2,r3=st.columns(3)
            with r1: st.metric("Pontuação", f"{risco}/100")
            with r2: st.metric("Prejuízo", f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Risco", risco_fin)
            if tipo_incidente=="ataque":
                st.error(f"🌍 Origem: {pais} | IP: {ip_ex}")
            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn,{"usuario":usuario_atual,"tipo":tipo_incidente,"origem":origem_ataque,"status":status_atual,"severidade":resultado,"cliente":cliente_afetado})
                st.success("💾 Salvo")

with tab2:
    st.markdown("### Métricas")
    L=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#8b9dc3")
    g1,g2=st.columns(2)
    with g1:
        fig=px.pie(df_vis,names="SEVERIDADE",title="Severidade",color_discrete_sequence=["#f59e0b","#10b981","#ef4444"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    with g2:
        vc=df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig=px.bar(vc,x="TIPO INCIDENTE",y="count",title="Por Tipo",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    df_time=df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig=px.line(df_time,x="DATA",y="Incidentes",title="Volume ao Longo do Tempo",color_discrete_sequence=["#00d4ff"])
    fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    g3,g4=st.columns(2)
    with g3:
        fig=px.histogram(df_vis,x="PAIS_ATAQUE",title="Ataques por País",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    with g4:
        dmg=df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index().sort_values("PREJUIZO_ESTIMADO",ascending=False).head(7)
        fig=px.bar(dmg,x="CLIENTE",y="PREJUIZO_ESTIMADO",title="Impacto Financeiro",color_discrete_sequence=["#00d4ff"])
        fig.update_layout(**L); st.plotly_chart(fig,use_container_width=True)
    st.markdown("### Modelo")
    m1,m2,m3=st.columns(3)
    with m1: st.metric("Acurácia",f"{acuracia:.1%}")
    with m2: st.metric("Treino",f"{int(len(df)*.8):,}")
    with m3: st.metric("Teste",f"{int(len(df)*.2):,}")
    cm=confusion_matrix(y_test,modelo.predict(X_test))
    labels=encoders["severidade"].classes_
    fig=go.Figure(go.Heatmap(z=cm,x=labels,y=labels,colorscale=[[0,"#060b18"],[1,"#00d4ff"]],text=cm,texttemplate="%{text}",showscale=True))
    fig.update_layout(title="Matriz de Confusão",height=320,**L)
    st.plotly_chart(fig,use_container_width=True)

with tab3:
    st.markdown("### Mapa Global de Ameaças")
    
    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "North Korea": (40.33, 127.51), "Germany": (51.16, 10.45), "Brazil": (-14.23, -51.92),
        "Canada": (56.13, -106.34), "India": (20.59, 78.96), "France": (46.22, 2.21),
        "United Kingdom": (52.13, -1.09), "Iran": (36.20, 53.68), "Australia": (-25.27, 133.77),
        "Japan": (36.20, 138.25), "Netherlands": (52.13, 5.29), "Ukraine": (48.38, 31.17)
    }
    TARGET = (-15.78, -47.92)
    
    attack_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    cc = attack_df["PAIS_ATAQUE"].value_counts().reset_index()
    cc.columns = ["country", "total"]
    
    import json
    arcs = []
    for _, row in cc.iterrows():
        c = row["country"]
        if c in COORDS:
            s = COORDS[c]
            severity = "high" if row["total"] > 30 else ("medium" if row["total"] > 15 else "low")
            arcs.append({
                "src_lat": s[0], "src_lon": s[1],
                "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                "name": c, "count": int(row["total"]),
                "severity": severity
            })
    
    map_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{background:#060b18;overflow:hidden;font-family:'Segoe UI',sans-serif;}}
        canvas{{display:block;}}
        .panel{{position:absolute;background:rgba(4,8,20,.9);backdrop-filter:blur(10px);border:1px solid rgba(0,212,255,.2);border-radius:12px;z-index:100;pointer-events:none;}}
        #ps{{top:16px;right:16px;padding:10px 16px;min-width:120px;text-align:center;}}
        .sl{{color:#5a7a9e;font-size:8px;letter-spacing:.1em;}}
        .sv{{color:#00d4ff;font-size:20px;font-weight:700;font-family:monospace;}}
        #pl{{bottom:16px;left:16px;padding:8px 12px;}}
        .lt{{color:#00d4ff;font-size:9px;font-weight:600;margin-bottom:4px;}}
        .lr{{display:flex;align-items:center;gap:6px;margin:2px 0;}}
        .ld{{width:7px;height:7px;border-radius:50%;}}
        .lx{{color:#8b9dc3;font-size:8px;}}
        #tt{{position:absolute;display:none;background:rgba(4,8,20,.96);border:1px solid #00d4ff;border-radius:8px;padding:6px 10px;font-size:9px;color:#00d4ff;z-index:200;}}
        hr{{margin:4px 0;border-color:rgba(0,212,255,.1);}}
    </style>
    </head>
    <body>
    <canvas id="c"></canvas>
    <div class="panel" id="ps">
        <div class="sl">Ameaças</div>
        <div class="sv" id="ac">0</div>
        <hr>
        <div class="sl">IPs</div>
        <div class="sv" id="ic">0</div>
    </div>
    <div class="panel" id="pl">
        <div class="lt">🌐 LEGENDA</div>
        <div class="lr"><div class="ld" style="background:#ef4444;"></div><span class="lx">Alto</span></div>
        <div class="lr"><div class="ld" style="background:#f59e0b;"></div><span class="lx">Médio</span></div>
        <div class="lr"><div class="ld" style="background:#00d4ff;"></div><span class="lx">Baixo</span></div>
    </div>
    <div id="tt"><div id="tn" style="font-weight:700;"></div><div id="tc"></div></div>
    <script>
        var A = {json.dumps(arcs)};
        var maxCount = Math.max(...A.map(a=>a.count),1);
        var cv = document.getElementById('c'), ctx = cv.getContext('2d');
        var W, H, particles = [], frame = 0, attackTotal = 0, ipTotal = 0;
        
        function resize() {{ W = cv.width = window.innerWidth; H = cv.height = window.innerHeight; }}
        resize();
        window.addEventListener('resize', resize);
        
        function ll(lat, lon) {{ return [(lon+180)/360*W, (90-lat)/180*H]; }}
        
        function getColor(sev) {{
            if(sev === 'high') return [239,68,68];
            if(sev === 'medium') return [245,158,11];
            return [0,212,255];
        }}
        
        var countries = [
            [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],[40.33,127.51,"PRK"],
            [51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],[56.13,-106.34,"CAN"],[20.59,78.96,"IND"]
        ];
        
        function drawCountries() {{
            for(var c of countries) {{
                var p = ll(c[0], c[1]);
                var isTarget = c[2] === 'BRA';
                if(isTarget) {{
                    ctx.beginPath();
                    ctx.arc(p[0], p[1], 8, 0, Math.PI*2);
                    ctx.fillStyle = '#00ff64';
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(p[0], p[1], 14, 0, Math.PI*2);
                    ctx.strokeStyle = 'rgba(0,255,100,0.3)';
                    ctx.stroke();
                }} else {{
                    ctx.beginPath();
                    ctx.arc(p[0], p[1], 3, 0, Math.PI*2);
                    ctx.fillStyle = 'rgba(0,180,255,0.4)';
                    ctx.fill();
                }}
                ctx.fillStyle = isTarget ? '#00ff64' : 'rgba(120,170,210,0.8)';
                ctx.font = 'bold 8px monospace';
                ctx.fillText(c[2], p[0]+6, p[1]+3);
            }}
        }}
        
        function Particle(a) {{
            this.a = a;
            this.t = 0;
            this.speed = 0.003 + Math.random() * 0.003;
            this.trail = [];
            this.color = getColor(a.severity);
            this.pos = function(t) {{
                var s = ll(this.a.src_lat, this.a.src_lon);
                var d = ll(this.a.dst_lat, this.a.dst_lon);
                var mx = (s[0]+d[0])/2;
                var my = Math.min(s[1],d[1]) - Math.abs(d[0]-s[0])*0.2;
                var u = 1-t;
                return [u*u*s[0] + 2*u*t*mx + t*t*d[0], u*u*s[1] + 2*u*t*my + t*t*d[1]];
            }};
            this.update = function() {{
                this.t += this.speed;
                this.trail.push(this.pos(Math.min(this.t,1)));
                if(this.trail.length > 20) this.trail.shift();
                return this.t < 1;
            }};
            this.draw = function() {{
                if(this.trail.length < 2) return;
                for(var i=1; i<this.trail.length; i++) {{
                    var alpha = i/this.trail.length;
                    ctx.beginPath();
                    ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
                    ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                    ctx.strokeStyle = 'rgba('+this.color[0]+','+this.color[1]+','+this.color[2]+','+alpha+')';
                    ctx.lineWidth = 1.5 * alpha;
                    ctx.stroke();
                }}
                var last = this.trail[this.trail.length-1];
                ctx.beginPath();
                ctx.arc(last[0], last[1], 2.5, 0, Math.PI*2);
                ctx.fillStyle = 'rgb('+this.color[0]+','+this.color[1]+','+this.color[2]+')';
                ctx.fill();
            }};
        }}
        
        function spawn() {{
            if(!A.length) return;
            var idx = Math.floor(Math.random() * A.length);
            var a = A[idx];
            if(Math.random() < 0.1 + a.count/maxCount * 0.15) {{
                particles.push(new Particle(a));
            }}
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            ctx.fillStyle = '#060b18';
            ctx.fillRect(0, 0, W, H);
            ctx.lineWidth = 0.5;
            for(var lon=-180; lon<=180; lon+=30) {{
                var p = ll(0, lon);
                ctx.beginPath();
                ctx.moveTo(p[0], 0);
                ctx.lineTo(p[0], H);
                ctx.strokeStyle = 'rgba(0,180,255,0.05)';
                ctx.stroke();
            }}
            drawCountries();
            frame++;
            if(frame % 10 === 0) spawn();
            var alive = [];
            for(var p of particles) {{
                if(p.update()) {{
                    p.draw();
                    alive.push(p);
                }} else {{
                    attackTotal++;
                    ipTotal = Math.floor(attackTotal * 0.7);
                    document.getElementById('ac').innerText = attackTotal.toLocaleString();
                    document.getElementById('ic').innerText = ipTotal.toLocaleString();
                }}
            }}
            particles = alive;
        }}
        
        cv.addEventListener('mousemove', function(e) {{
            var rect = cv.getBoundingClientRect();
            var mx = (e.clientX - rect.left) * (W/rect.width);
            var my = (e.clientY - rect.top) * (H/rect.height);
            var tip = document.getElementById('tt');
            var found = false;
            for(var a of A) {{
                var p = ll(a.src_lat, a.src_lon);
                var dx = mx - p[0], dy = my - p[1];
                if(Math.hypot(dx, dy) < 18) {{
                    tip.style.display = 'block';
                    tip.style.left = (e.clientX + 12) + 'px';
                    tip.style.top = (e.clientY - 35) + 'px';
                    document.getElementById('tn').innerHTML = '<strong>' + a.name + '</strong>';
                    document.getElementById('tc').innerHTML = a.count + ' ataques';
                    found = true;
                    break;
                }}
            }}
            if(!found) tip.style.display = 'none';
        }});
        
        animate();
    </script>
    </body>
    </html>
    """
    components.html(map_html, height=520, scrolling=False)
    
    st.markdown("### Países com Mais Ataques")
    ta = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    ta.columns = ["País", "Ataques"]
    ta["Percentual"] = (ta["Ataques"] / ta["Ataques"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(ta, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### 🤖 Assistente IA - SentinelBot")
    st.caption("Powered by Google Gemini - Pergunte sobre incidentes, clientes, ameaças")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    top5c = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5a = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()
    
    prompt_base = f"""Você é o SentinelBot, assistente de segurança cibernética.
Responda em português do Brasil, de forma profissional.

DADOS DO SISTEMA:
- Total: {len(df_vis)} incidentes
- Críticos: {len(df_vis[df_vis['SEVERIDADE']=='crítica'])} ({len(df_vis[df_vis['SEVERIDADE']=='crítica'])/len(df_vis)*100:.1f}%)
- IPs bloqueados: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower()=='sim'])}
- Prejuízo: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- Acurácia IA: {acuracia:.1%}
- Tipos: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Clientes: {', '.join(df_vis['CLIENTE'].unique())}
- Top países atacantes: {top5a}
- Top clientes prejuízo: {top5c}"""
    
    if not GEMINI_API_KEY:
        st.error("🔴 Assistente offline - Configure GEMINI_API_KEY nos Secrets")
    else:
        st.success("🟢 SentinelBot ativo")
    
    for msg in st.session_state["chat_history"]:
        css = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        cq, cb = st.columns([5, 1])
        with cq:
            pergunta = st.text_input("", placeholder="Ex: Qual cliente teve mais prejuízo?", label_visibility="collapsed", disabled=not GEMINI_API_KEY)
        with cb:
            enviar = st.form_submit_button("Enviar", use_container_width=True, disabled=not GEMINI_API_KEY)
    
    sugs = ["Qual cliente teve mais prejuízo?", "Quais países mais atacaram?", "Como estão os críticos?", "Acurácia do modelo?", "Recomendações"]
    cols_s = st.columns(len(sugs))
    sug_esc = None
    for i, s in enumerate(sugs):
        with cols_s[i]:
            if st.button(s[:20] + "..." if len(s) > 20 else s, key=f"sg{i}", use_container_width=True, disabled=not GEMINI_API_KEY):
                sug_esc = s
    
    if sug_esc:
        pergunta = sug_esc
        enviar = True
    
    if enviar and pergunta and GEMINI_API_KEY:
        adicionar_log(usuario_atual, f"Chat: {pergunta[:50]}")
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        
        with st.spinner("🤔 Processando..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                
                payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": prompt_base + "\n\nPergunta: " + pergunta}]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1024
                    }
                }
                
                resp = requests.post(url, json=payload, timeout=30)
                
                if resp.status_code == 200:
                    data = resp.json()
                    resposta = data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    resposta = f"Erro {resp.status_code}"
                    
            except Exception as e:
                resposta = f"Erro: {str(e)[:80]}"
        
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
        adicionar_log(usuario_atual, "Resposta gerada")
        st.rerun()
    
    if st.session_state["chat_history"] and st.button("🗑️ Limpar conversa"):
        st.session_state["chat_history"] = []
        st.rerun()

with tab5:
    st.markdown("### Backup e Exportação")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas administradores")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.download_button("📥 CSV", df.to_csv(index=False).encode("utf-8"), f"sentinel_{ts}.csv", "text/csv", use_container_width=True)
        with b2:
            df_a = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("🔒 Anonimizado", df_a.to_csv(index=False).encode("utf-8"), f"sentinel_anon_{ts}.csv", "text/csv", use_container_width=True)
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button("📋 Logs", "\n".join(st.session_state["logs_sistema"]).encode("utf-8"), f"sentinel_logs_{ts}.txt", "text/plain", use_container_width=True)
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("🗄️ Banco", f.read(), f"sentinel_db_{ts}.db", "application/x-sqlite3", use_container_width=True)
    
    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### Histórico")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)
    
    st.markdown("### Prévia dos Dados")
    st.dataframe(df_vis.head(20), use_container_width=True)

with tab6:
    st.markdown("### Logs do Sistema")
    tl1, tl2 = st.tabs(["📱 Sessão Atual", "💾 Histórico"])
    with tl1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("Nenhum log na sessão")
    with tl2:
        if sqlite_ativo:
            try:
                logs_db = pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not logs_db.empty:
                    st.dataframe(logs_db, use_container_width=True)
                else:
                    st.info("Nenhum log no banco")
            except:
                st.info("Erro ao carregar")
        else:
            st.warning("Banco offline")

st.markdown("""
<div style="text-align:center;padding:1rem 0;border-top:1px solid rgba(0,212,255,.07);margin-top:1rem;">
    <p style="color:#2a4a6a;font-size:.65rem;">SentinelAI © 2025 — Segurança Cibernética | LGPD</p>
</div>
""", unsafe_allow_html=True)
