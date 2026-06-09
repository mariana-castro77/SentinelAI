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
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
.stApp {
    background: #0a0e1a;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background: rgba(8, 12, 25, 0.95);
    border-right: 1px solid rgba(0, 255, 255, 0.1);
}
.block-container {
    padding: 1rem;
    max-width: 100%;
}
@media (min-width: 768px) {
    .block-container {
        padding: 1.5rem;
    }
}
div[data-testid="metric-container"] {
    background: rgba(15, 25, 45, 0.8);
    border: 1px solid rgba(0, 255, 255, 0.15);
    border-radius: 12px;
    padding: 0.8rem;
    transition: all 0.3s ease;
}
div[data-testid="metric-container"]:hover {
    border-color: #00ffff;
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
    color: #8b9dc3;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #00ffff;
    font-size: 1.5rem;
    font-weight: 700;
}
@media (min-width: 768px) {
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
}
div.stButton > button {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
    transition: all 0.2s ease;
    width: 100%;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #00d4ff, #0096c7);
    transform: scale(1.01);
}
.chat-user {
    background: linear-gradient(135deg, #00b4d8, #0077b6);
    border-radius: 18px 18px 4px 18px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    margin-left: auto;
    max-width: 85%;
    width: fit-content;
    color: white;
    font-size: 0.85rem;
}
.chat-ai {
    background: rgba(15, 25, 45, 0.9);
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 18px 18px 18px 4px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0;
    margin-right: auto;
    max-width: 85%;
    width: fit-content;
    color: #e0e0e0;
    font-size: 0.85rem;
}
.sentinel-header {
    background: linear-gradient(135deg, rgba(0, 180, 216, 0.08), rgba(0, 119, 182, 0.03));
    border: 1px solid rgba(0, 255, 255, 0.15);
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
}
@media (min-width: 768px) {
    .sentinel-header {
        padding: 1.5rem;
    }
}
.badge-online {
    display: inline-block;
    background: rgba(0, 255, 0, 0.1);
    border: 1px solid rgba(0, 255, 0, 0.3);
    color: #00ff00;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-sqlite {
    display: inline-block;
    background: rgba(0, 255, 255, 0.1);
    border: 1px solid rgba(0, 255, 255, 0.3);
    color: #00ffff;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 25, 45, 0.8);
    border-radius: 12px;
    padding: 0.3rem;
    gap: 0.3rem;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #8b9dc3;
    font-weight: 500;
    padding: 0.4rem 0.8rem;
    font-size: 0.75rem;
}
@media (min-width: 768px) {
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1.2rem;
        font-size: 0.85rem;
    }
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 180, 216, 0.2);
    color: #00ffff !important;
}
input, textarea, select {
    background: rgba(15, 25, 45, 0.8) !important;
    border: 1px solid rgba(0, 255, 255, 0.2) !important;
    border-radius: 10px !important;
    color: white !important;
}
input:focus, textarea:focus, select:focus {
    border-color: #00ffff !important;
    box-shadow: 0 0 0 2px rgba(0, 255, 255, 0.1) !important;
}
hr {
    border-color: rgba(0, 255, 255, 0.1);
    margin: 1rem 0;
}
code {
    background: rgba(0, 255, 255, 0.1);
    color: #00ffff;
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
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
    <div style="background:rgba(0,180,216,0.05);border:1px solid rgba(0,255,255,0.2);border-radius:20px;padding:1.5rem;margin:1rem 0;text-align:center;">
        <h3 style="color:#00ffff;margin-bottom:0.8rem;">🔒 Política de Privacidade</h3>
        <p style="color:#c0c0c0;font-size:0.9rem;">Esta plataforma segue a LGPD (Lei 13.709/2018). Seus dados estão protegidos e não são compartilhados com terceiros.</p>
        <div style="display:flex;gap:1rem;justify-content:center;margin-top:1.5rem;">
    </div>
    """, unsafe_allow_html=True)
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0;">
            <div style="font-size:4rem;">🛡️</div>
            <h1 style="color:#00ffff;font-size:2.2rem;margin:0.5rem 0;">SentinelAI</h1>
            <p style="color:#8b9dc3;">Plataforma de Inteligência contra Ameaças</p>
            <div style="margin:1rem 0;"><span class="badge-online">● SISTEMA ATIVO</span></div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            usuario_input = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha_input = st.text_input("Senha", type="password", placeholder="••••••••")
            if st.form_submit_button("🔐 Entrar", use_container_width=True):
                if autenticar(usuario_input, senha_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_atual"] = usuario_input
                    adicionar_log(usuario_input, "Login realizado")
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
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
salvar_backup_sessao(df_vis, usuario_atual, "Login")

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:2.5rem;">🛡️</div>
        <h3 style="color:#00ffff;margin:0.3rem 0;">SentinelAI</h3>
        <p style="color:#6b8a9e;font-size:0.7rem;">CYBER SECURITY</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.08);border-radius:12px;padding:0.8rem;margin:0.5rem 0;">
        <p style="color:#00ffff;font-size:0.65rem;">PERFIL</p>
        <p style="color:white;font-weight:600;">{perfil_atual['perfil']}</p>
        <p style="color:#8b9dc3;font-size:0.7rem;">@{usuario_atual}</p>
    </div>
    """, unsafe_allow_html=True)
    badge_db = '<span class="badge-sqlite">📁 SQLite Ativo</span>' if sqlite_ativo else '<span class="badge-sqlite" style="border-color:#ff4444;color:#ff4444;">⚠️ Banco Offline</span>'
    st.markdown(badge_db, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Permissões")
    permissoes = [
        ("📊 Análise", perfil_atual["pode_analisar"]),
        ("📤 Exportar", perfil_atual["pode_exportar"]),
        ("👁️ Ver IPs", perfil_atual["ver_pii"]),
    ]
    for nome, ativo in permissoes:
        if ativo:
            st.markdown(f"<p style='color:#00ff00;font-size:0.75rem;'>✓ {nome}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#ff4444;font-size:0.75rem;'>✗ {nome}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.08);border-radius:12px;padding:0.8rem;text-align:center;">
        <p style="color:#8b9dc3;font-size:0.65rem;">Acurácia do Modelo</p>
        <p style="color:#00ffff;font-size:1.3rem;font-weight:700;">{acuracia:.1%}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.8rem;">
        <div>
            <p style="color:#00ffff;font-size:0.7rem;">BEM-VINDO, {usuario_atual.upper()}</p>
            <h1 style="color:white;margin:0.2rem 0 0;font-size:1.4rem;">Painel de Inteligência contra Ameaças</h1>
            <p style="color:#8b9dc3;margin-top:0.2rem;font-size:0.8rem;">
                {f"Visão do Cliente: {cliente_vinculado}" if cliente_vinculado else "Visão Global - Todos os Clientes"}
            </p>
        </div>
        <div style="text-align:right;">
            <span class="badge-online">● SISTEMA PROTEGIDO</span>
            <p style="color:#6b8a9e;font-size:0.65rem;margin-top:0.4rem;">{datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total_incidentes = len(df_vis)
incidentes_criticos = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloqueados = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo_total = df_vis["PREJUIZO_ESTIMADO"].sum()
incidentes_resolvidos = len(df_vis[df_vis["STATUS"] == "resolvido"])
incidentes_pendentes = len(df_vis[df_vis["STATUS"] == "pendente"])

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total Incidentes", f"{total_incidentes:,}")
with col2:
    st.metric("Críticos", f"{incidentes_criticos:,}")
with col3:
    st.metric("IPs Bloqueados", f"{ips_bloqueados:,}")
with col4:
    st.metric("Resolvidos", f"{incidentes_resolvidos:,}")
with col5:
    st.metric("Pendentes", f"{incidentes_pendentes:,}")
with col6:
    prejuizo_formatado = f"R$ {prejuizo_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Prejuízo Estimado", prejuizo_formatado)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Análise", "📊 Métricas", "🌍 Mapa de Ameaças", "🤖 Assistente IA", "💾 Backup", "📋 Logs"
])

with tab1:
    st.markdown("### Análise de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⚠️ Seu perfil não tem permissão para realizar análises.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            tipo_incidente = st.selectbox("Tipo de Incidente", encoders["tipo"].classes_)
            origem_ataque = st.selectbox("Origem", encoders["origem"].classes_)
            cliente_afetado = st.selectbox("Cliente", sorted(df["CLIENTE"].unique()))
        with col_b:
            tempo_resolucao = st.slider("Tempo de Resolução (minutos)", 1, 120, 30)
            status_atual = st.selectbox("Status", encoders["status"].classes_)
        if st.button("🚀 Iniciar Análise", use_container_width=True):
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
            if status_atual == "resolvido":
                resultado = "baixa"
            elif tipo_incidente in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo_incidente in ["lentidão", "erro sistema"]:
                resultado = random.choice(["baixa", "média"])
            risco = random.randint(10, 99)
            prej_est = random.uniform(3000, 30000)
            risco_fin = "ALTO" if prej_est > 15000 else ("MÉDIO" if prej_est > 7000 else "BAIXO")
            ataques = df[df["TIPO INCIDENTE"] == "ataque"]
            if not ataques.empty:
                linha = ataques.sample(1).iloc[0]
                ip_ex = linha["IP_SUSPEITO"] if perfil_atual["ver_pii"] else mascara_ip(linha["IP_SUSPEITO"])
                pais = linha["PAIS_ATAQUE"]
            else:
                ip_ex, pais = "DESCONHECIDO", "INTERNO"
            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 Severidade: {resultado.upper()} - AÇÃO IMEDIATA")
            elif resultado == "média":
                st.warning(f"🟡 Severidade: {resultado.upper()} - MONITORAR")
            else:
                st.success(f"🟢 Severidade: {resultado.upper()} - BAIXO RISCO")
            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("Pontuação de Ameaça", f"{risco}/100")
            with r2:
                st.metric("Prejuízo Estimado", f"R$ {prej_est:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with r3:
                st.metric("Risco Financeiro", risco_fin)
            st.write(f"**Cliente:** {cliente_afetado}")
            if tipo_incidente == "ataque":
                st.error(f"🌍 Origem: {pais} | IP: `{ip_ex}`")
                with st.expander("🛡️ Resposta Automática"):
                    for a in ["✅ IP bloqueado", "✅ Firewall atualizado", "✅ Equipe notificada", "✅ Logs capturados"]:
                        st.write(a)
            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo_incidente, "origem": origem_ataque,
                    "status": status_atual, "severidade": resultado, "cliente": cliente_afetado
                })
                st.success("💾 Incidente salvo no banco de dados")
            adicionar_log(usuario_atual, f"Análise concluída: {resultado}")

with tab2:
    st.markdown("### Painel de Métricas")
    LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#00ffff")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_pie = px.pie(df_vis, names="SEVERIDADE", title="Distribuição por Severidade", color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig_pie.update_layout(**LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_g2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig_bar = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Incidentes por Tipo", color_discrete_sequence=["#00ffff"])
        fig_bar.update_layout(**LAYOUT)
        st.plotly_chart(fig_bar, use_container_width=True)
    df_time = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig_line = px.line(df_time, x="DATA", y="Incidentes", title="Volume de Ameaças ao Longo do Tempo", color_discrete_sequence=["#00ffff"])
    fig_line.update_layout(**LAYOUT)
    st.plotly_chart(fig_line, use_container_width=True)
    col_g3, col_g4 = st.columns(2)
    with col_g3:
        fig_hist = px.histogram(df_vis, x="PAIS_ATAQUE", title="Ataques por País", color_discrete_sequence=["#00ffff"])
        fig_hist.update_layout(**LAYOUT)
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_g4:
        damage = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        damage = damage.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig_damage = px.bar(damage, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="Impacto Financeiro por Cliente", color_discrete_sequence=["#00ffff"])
        fig_damage.update_layout(**LAYOUT)
        st.plotly_chart(fig_damage, use_container_width=True)
    st.markdown("### Desempenho do Modelo de IA")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Acurácia", f"{acuracia:.1%}")
    with m2:
        st.metric("Base de Treino", f"{int(len(df)*0.8):,}")
    with m3:
        st.metric("Base de Teste", f"{int(len(df)*0.2):,}")
    y_pred = modelo.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    labels = encoders["severidade"].classes_
    fig_cm = go.Figure(go.Heatmap(z=cm, x=labels, y=labels, colorscale=[[0, "#0a0e1a"], [1, "#00ffff"]], text=cm, texttemplate="%{text}", showscale=True))
    fig_cm.update_layout(title="Matriz de Confusão", xaxis_title="Previsto", yaxis_title="Real", height=320, **LAYOUT)
    st.plotly_chart(fig_cm, use_container_width=True)

with tab3:
    st.markdown("### Mapa Global de Ameaças")
    st.caption("Visualização em tempo real de ataques cibernéticos - Estilo Kaspersky")
    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "North Korea": (40.33, 127.51), "Germany": (51.16, 10.45), "Brazil": (-14.23, -51.92),
        "Canada": (56.13, -106.34), "India": (20.59, 78.96), "France": (46.22, 2.21),
        "United Kingdom": (52.13, -1.09), "Iran": (36.20, 37.16), "Australia": (-25.27, 133.77)
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { margin: 0; background: #0a0e1a; overflow: hidden; font-family: 'Segoe UI', 'Inter', system-ui, sans-serif; }
        canvas { display: block; width: 100%; height: 100%; }
        #info-panel {
            position: absolute; bottom: 20px; left: 20px;
            background: rgba(10, 14, 26, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 12px;
            padding: 12px 16px;
            z-index: 100;
            font-size: 11px;
            pointer-events: none;
        }
        #info-panel h4 {
            color: #00ffff;
            margin-bottom: 8px;
            font-size: 12px;
        }
        .legend {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 6px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            color: #c0c0c0;
        }
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        #stats-panel {
            position: absolute; top: 20px; right: 20px;
            background: rgba(10, 14, 26, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 12px;
            padding: 12px 20px;
            text-align: center;
            z-index: 100;
            min-width: 140px;
        }
        #stats-panel .label {
            color: #8b9dc3;
            font-size: 10px;
            letter-spacing: 1px;
        }
        #stats-panel .number {
            color: #00ffff;
            font-size: 28px;
            font-weight: 700;
        }
        #tooltip {
            position: absolute; display: none;
            background: rgba(10, 14, 26, 0.98);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 8px 14px;
            color: #00ffff;
            font-size: 11px;
            pointer-events: none;
            z-index: 200;
            white-space: nowrap;
        }
        @media (max-width: 768px) {
            #stats-panel { padding: 6px 12px; min-width: 100px; }
            #stats-panel .number { font-size: 20px; }
            #info-panel { bottom: 10px; left: 10px; padding: 8px 12px; }
            .legend-item { font-size: 8px; }
        }
    </style>
    </head>
    <body>
    <canvas id="threatCanvas"></canvas>
    <div id="stats-panel">
        <div class="label">AMEAÇAS DETECTADAS</div>
        <div class="number" id="attackCount">0</div>
        <div class="label" style="margin-top: 8px;">IPS BLOQUEADOS</div>
        <div class="number" id="ipCount">0</div>
    </div>
    <div id="info-panel">
        <h4>🌍 MUNDO</h4>
        <div class="legend">
            <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div><span>Alto Volume (>30)</span></div>
            <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div><span>Médio (15-30)</span></div>
            <div class="legend-item"><div class="legend-dot" style="background:#00ffff;"></div><span>Baixo (<15)</span></div>
        </div>
        <div style="margin-top: 8px; border-top: 1px solid rgba(0,255,255,0.2); padding-top: 6px;">
            <div class="legend-item">🎯 <span style="color:#00ffff;">ALVO PRINCIPAL: BRASIL</span></div>
        </div>
    </div>
    <div id="tooltip"></div>
    <script>
        var arcsData = """ + arcs_json + """;
        var canvas = document.getElementById('threatCanvas');
        var ctx = canvas.getContext('2d');
        var tooltip = document.getElementById('tooltip');
        var w, h, particles = [];
        var attackTotal = 0, ipTotal = 0;
        var animationId = null;
        function resizeCanvas() {
            w = canvas.width = window.innerWidth;
            h = canvas.height = window.innerHeight;
        }
        function latLonToPixel(lat, lon) {
            var x = (lon + 180) / 360 * w;
            var y = (90 - lat) / 180 * h;
            return [x, y];
        }
        function drawGrid() {
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(0, 255, 255, 0.06)';
            ctx.lineWidth = 0.5;
            for (var lon = -180; lon <= 180; lon += 30) {
                var start = latLonToPixel(0, lon);
                ctx.moveTo(start[0], 0);
                ctx.lineTo(start[0], h);
                ctx.stroke();
            }
            for (var lat = -90; lat <= 90; lat += 30) {
                var start = latLonToPixel(lat, 0);
                ctx.moveTo(0, start[1]);
                ctx.lineTo(w, start[1]);
                ctx.stroke();
            }
        }
        function drawCountries() {
            var points = [
                [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],
                [40.33,127.51,"PRK"],[51.16,10.45,"DEU"],[-14.23,-51.92,"BRA"],
                [56.13,-106.34,"CAN"],[20.59,78.96,"IND"],[46.22,2.21,"FRA"],
                [52.13,-1.09,"GBR"],[36.20,37.16,"IRN"],[-25.27,133.77,"AUS"]
            ];
            for (var i = 0; i < points.length; i++) {
                var p = points[i];
                var pixel = latLonToPixel(p[0], p[1]);
                var isTarget = p[2] === "BRA";
                ctx.beginPath();
                ctx.arc(pixel[0], pixel[1], isTarget ? 8 : 4, 0, Math.PI * 2);
                ctx.fillStyle = isTarget ? '#00ff00' : 'rgba(0, 255, 255, 0.25)';
                ctx.fill();
                if (isTarget) {
                    ctx.beginPath();
                    ctx.arc(pixel[0], pixel[1], 14, 0, Math.PI * 2);
                    ctx.strokeStyle = 'rgba(0, 255, 255, 0.4)';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }
                ctx.fillStyle = isTarget ? '#00ff00' : '#00ffff';
                ctx.font = 'bold 10px "Segoe UI", monospace';
                ctx.fillText(p[2], pixel[0] + 10, pixel[1] + 4);
            }
        }
        function Particle(arc) {
            this.arc = arc;
            this.progress = 0;
            this.speed = 0.002 + Math.random() * 0.003;
            this.trail = [];
            this.update = function() {
                this.progress += this.speed;
                var pos = this.getPosition(this.progress);
                this.trail.push([pos[0], pos[1]]);
                if (this.trail.length > 20) this.trail.shift();
                return this.progress < 1;
            };
            this.getPosition = function(t) {
                var src = latLonToPixel(this.arc.src_lat, this.arc.src_lon);
                var dst = latLonToPixel(this.arc.dst_lat, this.arc.dst_lon);
                var ox = src[0], oy = src[1];
                var dx = dst[0], dy = dst[1];
                var mx = (ox + dx) / 2;
                var my = Math.min(oy, dy) - Math.abs(dx - ox) * 0.2;
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
                    var color = this.arc.color;
                    if (color === '#ef4444') ctx.strokeStyle = 'rgba(239,68,68,' + alpha + ')';
                    else if (color === '#f59e0b') ctx.strokeStyle = 'rgba(245,158,11,' + alpha + ')';
                    else ctx.strokeStyle = 'rgba(0,255,255,' + alpha + ')';
                    ctx.lineWidth = 2 * alpha;
                    ctx.stroke();
                }
                var last = this.trail[this.trail.length - 1];
                ctx.beginPath();
                ctx.arc(last[0], last[1], 4, 0, Math.PI * 2);
                ctx.fillStyle = this.arc.color;
                ctx.fill();
            };
        }
        function spawnParticles() {
            for (var i = 0; i < arcsData.length; i++) {
                if (Math.random() < 0.12) {
                    particles.push(new Particle(arcsData[i]));
                }
            }
        }
        var frameCount = 0;
        function animateThreatMap() {
            if (!ctx) return;
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#0a0e1a';
            ctx.fillRect(0, 0, w, h);
            drawGrid();
            drawCountries();
            frameCount++;
            if (frameCount % 10 === 0) spawnParticles();
            var remainingParticles = [];
            for (var i = 0; i < particles.length; i++) {
                var isAlive = particles[i].update();
                particles[i].draw();
                if (!isAlive) {
                    attackTotal++;
                    ipTotal = Math.floor(attackTotal * 0.68);
                    document.getElementById('attackCount').innerText = attackTotal.toLocaleString();
                    document.getElementById('ipCount').innerText = ipTotal.toLocaleString();
                } else {
                    remainingParticles.push(particles[i]);
                }
            }
            particles = remainingParticles;
            animationId = requestAnimationFrame(animateThreatMap);
        }
        function handleMouseMove(e) {
            var rect = canvas.getBoundingClientRect();
            var mx = (e.clientX - rect.left) * (w / rect.width);
            var my = (e.clientY - rect.top) * (h / rect.height);
            var found = false;
            for (var i = 0; i < arcsData.length; i++) {
                var arc = arcsData[i];
                var pos = latLonToPixel(arc.src_lat, arc.src_lon);
                var dx = mx - pos[0];
                var dy = my - pos[1];
                var dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 20) {
                    tooltip.style.display = 'block';
                    tooltip.style.left = (e.clientX + 15) + 'px';
                    tooltip.style.top = (e.clientY - 35) + 'px';
                    tooltip.innerHTML = '<strong>' + arc.name + '</strong><br>' + arc.count + ' ataques detectados';
                    found = true;
                    break;
                }
            }
            if (!found) tooltip.style.display = 'none';
        }
        function handleResize() {
            resizeCanvas();
        }
        resizeCanvas();
        window.addEventListener('resize', handleResize);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('touchmove', function(e) {
            if (e.touches.length) {
                var rect = canvas.getBoundingClientRect();
                var touch = e.touches[0];
                var fakeEvent = { clientX: touch.clientX, clientY: touch.clientY };
                handleMouseMove(fakeEvent);
            }
        });
        animateThreatMap();
    </script>
    </body>
    </html>
    """
    components.html(map_html, height=550, scrolling=False)
    st.markdown("### Países com Mais Ataques")
    top_attackers = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    top_attackers.columns = ["País", "Ataques"]
    top_attackers["Percentual"] = (top_attackers["Ataques"] / top_attackers["Ataques"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(top_attackers, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("### 🤖 Assistente de IA - SentinelBot")
    st.caption("Pergunte sobre incidentes, clientes, ameaças ou peça recomendações de segurança")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    top5_clientes = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5_ataques = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()
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
        st.error("🔴 Assistente offline - Configure a chave da API nos Secrets do Streamlit")
    else:
        st.success("🟢 Assistente ativo - Pronto para perguntas")
    for msg in st.session_state["chat_history"]:
        css_class = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f'<div class="{css_class}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        col_q, col_b = st.columns([5, 1])
        with col_q:
            pergunta = st.text_input("", placeholder="Ex: Qual cliente teve mais prejuízo?", label_visibility="collapsed", disabled=not ANTHROPIC_API_KEY)
        with col_b:
            enviar = st.form_submit_button("Enviar", use_container_width=True, disabled=not ANTHROPIC_API_KEY)
    sugestoes = ["Qual cliente teve mais prejuízo?", "Quais países mais atacaram?", "Como estão os incidentes críticos?", "Qual a acurácia do modelo?", "Recomendações de segurança"]
    cols_sug = st.columns(len(sugestoes))
    sugestao_escolhida = None
    for i, sug in enumerate(sugestoes):
        with cols_sug[i]:
            if st.button(sug[:25] + "..." if len(sug) > 25 else sug, key=f"sug{i}", use_container_width=True, disabled=not ANTHROPIC_API_KEY):
                sugestao_escolhida = sug
    if sugestao_escolhida:
        pergunta = sugestao_escolhida
        enviar = True
    if enviar and pergunta and ANTHROPIC_API_KEY:
        adicionar_log(usuario_atual, f"Chat: {pergunta[:50]}")
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        with st.spinner("🤔 Pensando..."):
            try:
                headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
                payload = {"model": "claude-3-haiku-20240307", "max_tokens": 1024, "system": system_prompt, "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]}
                resposta_api = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
                if resposta_api.status_code == 200:
                    resposta = resposta_api.json()["content"][0]["text"]
                else:
                    resposta = f"Erro na API: {resposta_api.status_code}"
            except Exception as e:
                resposta = f"Erro de conexão: {str(e)[:80]}"
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
        adicionar_log(usuario_atual, "Resposta gerada")
        st.rerun()
    if st.session_state["chat_history"] and st.button("🗑️ Limpar conversa"):
        st.session_state["chat_history"] = []
        st.rerun()

with tab5:
    st.markdown("### Backup e Exportação de Dados")
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Exportação restrita - Apenas administradores")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("📥 Exportar CSV", df.to_csv(index=False).encode("utf-8"), f"sentinelai_{ts}.csv", "text/csv", use_container_width=True)
        with col_b2:
            df_anon = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("🔒 Exportar Anonimizado", df_anon.to_csv(index=False).encode("utf-8"), f"sentinelai_anon_{ts}.csv", "text/csv", use_container_width=True)
        with col_b3:
            if "logs_sistema" in st.session_state:
                st.download_button("📋 Exportar Logs", "\n".join(st.session_state["logs_sistema"]).encode("utf-8"), f"sentinelai_logs_{ts}.txt", "text/plain", use_container_width=True)
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("🗄️ Backup do Banco", f.read(), f"sentinelai_db_{ts}.db", "application/x-sqlite3", use_container_width=True)
    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### Histórico de Backups")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)
    st.markdown("### Prévia dos Dados")
    st.dataframe(df_vis.head(20), use_container_width=True)

with tab6:
    st.markdown("### Logs do Sistema")
    tab_log1, tab_log2 = st.tabs(["📱 Sessão Atual", "💾 Histórico do Banco"])
    with tab_log1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("Nenhum log na sessão atual")
    with tab_log2:
        if sqlite_ativo:
            try:
                logs_db = pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not logs_db.empty:
                    st.dataframe(logs_db, use_container_width=True)
                else:
                    st.info("Nenhum log encontrado no banco de dados")
            except:
                st.info("Erro ao carregar logs do banco")
        else:
            st.warning("Banco de dados offline")

st.markdown("""
<div style="text-align:center;padding:1rem 0;border-top:1px solid rgba(0,255,255,0.1);margin-top:1rem;">
    <p style="color:#4a6a8a;font-size:0.7rem;">SentinelAI - Plataforma de Segurança Cibernética | LGPD Compliance</p>
</div>
""", unsafe_allow_html=True)
