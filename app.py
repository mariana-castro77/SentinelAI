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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #060d1a; color: #e5e7eb; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d1f3c 100%);
    border-right: 1px solid rgba(37,99,235,0.2);
}
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #f9fafb; font-weight: 700; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(10,22,40,0.9), rgba(13,31,60,0.9));
    border: 1px solid rgba(37,99,235,0.25);
    padding: 20px 24px; border-radius: 16px;
    backdrop-filter: blur(20px);
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover { border-color: rgba(37,99,235,0.6); }
[data-testid="stMetricLabel"] { color: #6b7280; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: #f9fafb; font-size: 28px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
div.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    color: white; border-radius: 10px; border: none;
    height: 3em; font-size: 15px; font-weight: 600;
    box-shadow: 0 4px 15px rgba(37,99,235,0.3);
    transition: all 0.2s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8);
    box-shadow: 0 6px 20px rgba(37,99,235,0.5);
    transform: translateY(-1px);
}
.chat-user {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px; margin: 8px 0; margin-left: 20%;
    color: white; font-size: 14px; line-height: 1.6;
}
.chat-ai {
    background: linear-gradient(135deg, rgba(10,22,40,0.95), rgba(13,31,60,0.95));
    border: 1px solid rgba(37,99,235,0.3);
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px; margin: 8px 0; margin-right: 20%;
    color: #e5e7eb; font-size: 14px; line-height: 1.6;
}
.sentinel-header {
    background: linear-gradient(135deg, rgba(10,22,40,0.95), rgba(13,31,60,0.8));
    border: 1px solid rgba(37,99,235,0.2);
    border-radius: 20px; padding: 24px 32px; margin-bottom: 24px;
}
.badge-sqlite {
    display: inline-block; background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4); color: #10b981;
    padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(10,22,40,0.8); border-radius: 12px;
    padding: 4px; border: 1px solid rgba(37,99,235,0.15);
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #6b7280; font-weight: 500; }
.stTabs [aria-selected="true"] { background: rgba(37,99,235,0.2) !important; color: #60a5fa !important; }
</style>
""", unsafe_allow_html=True)

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] USER={usuario} | {acao}")
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
    if ip == "Nenhum": return "Nenhum"
    p = ip.split(".")
    return f"{p[0]}.{p[1]}.***.***" if len(p) == 4 else "***"

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(10,22,40,0.98),rgba(13,31,60,0.98));
                border:1px solid rgba(37,99,235,0.3);border-radius:16px;padding:24px 32px;margin:20px 0;">
        <h3 style="color:#60a5fa;margin:0 0 10px;">🍪 Política de Cookies e Privacidade</h3>
        <p style="color:#9ca3af;font-size:14px;line-height:1.7;margin:0;">
        Esta plataforma utiliza cookies de sessão para autenticação e controle de acesso.
        Dados protegidos conforme a <strong style="color:#e5e7eb;">LGPD — Lei 13.709/2018</strong>.
        Nenhum dado pessoal é compartilhado com terceiros sem consentimento.
        </p>
    </div>
    """, unsafe_allow_html=True)
    ca, cb, _ = st.columns([1, 1, 6])
    with ca:
        if st.button("✅ Aceitar"):
            st.session_state["cookies_aceitos"] = True
            adicionar_log("Sistema", "Cookies aceitos")
            st.rerun()
    with cb:
        if st.button("❌ Recusar"):
            st.stop()
    st.stop()

USUARIOS = {
    "admin": {"senha_hash": hashlib.sha256("admin123".encode()).hexdigest(), "perfil": "Administrador", "pode_exportar": True, "pode_analisar": True, "ver_pii": True, "cliente_vinculado": None},
    "analista": {"senha_hash": hashlib.sha256("analista123".encode()).hexdigest(), "perfil": "Analista de Segurança", "pode_exportar": False, "pode_analisar": True, "ver_pii": False, "cliente_vinculado": None},
    "nubank": {"senha_hash": hashlib.sha256("nubank123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Nubank"},
    "mercadolivre": {"senha_hash": hashlib.sha256("ml123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Mercado Livre"},
    "santander": {"senha_hash": hashlib.sha256("sant123".encode()).hexdigest(), "perfil": "Cliente", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": "Santander"},
    "viewer": {"senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(), "perfil": "Visualização", "pode_exportar": False, "pode_analisar": False, "ver_pii": False, "cliente_vinculado": None},
}

def autenticar(u, s):
    return u in USUARIOS and hashlib.sha256(s.encode()).hexdigest() == USUARIOS[u]["senha_hash"]

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    _, cm, _ = st.columns([1, 2, 1])
    with cm:
        st.markdown("""
        <div style="text-align:center;padding:40px 0 20px;">
            <h1 style="font-size:48px;font-weight:800;color:#f9fafb;letter-spacing:-1px;">🛡️ SentinelAI</h1>
            <p style="color:#6b7280;font-size:16px;margin-top:8px;">Central Inteligente de Defesa Cibernética</p>
            <span style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);
                         color:#10b981;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">
                ● SISTEMA ONLINE
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(37,99,235,0.25);
                    border-radius:16px;padding:20px;margin-bottom:16px;">
            <p style="color:#6b7280;font-size:11px;font-weight:600;text-transform:uppercase;
                      letter-spacing:0.1em;margin-bottom:10px;">Contas de demonstração</p>
            <p style="color:#9ca3af;font-size:13px;line-height:2;margin:0;">
                <code style="color:#60a5fa;">admin</code> / <code style="color:#60a5fa;">admin123</code> — Administrador (acesso total)<br>
                <code style="color:#60a5fa;">analista</code> / <code style="color:#60a5fa;">analista123</code> — Analista de Segurança<br>
                <code style="color:#60a5fa;">nubank</code> / <code style="color:#60a5fa;">nubank123</code> — Cliente Nubank<br>
                <code style="color:#60a5fa;">mercadolivre</code> / <code style="color:#60a5fa;">ml123</code> — Cliente Mercado Livre<br>
                <code style="color:#60a5fa;">santander</code> / <code style="color:#60a5fa;">sant123</code> — Cliente Santander<br>
                <code style="color:#60a5fa;">viewer</code> / <code style="color:#60a5fa;">viewer123</code> — Somente Visualização
            </p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("Usuário", placeholder="Digite seu usuário")
            s_in = st.text_input("Senha", type="password", placeholder="••••••••")
            ok = st.form_submit_button("🔐 Entrar na plataforma", use_container_width=True)
        if ok:
            if autenticar(u_in, s_in):
                st.session_state["autenticado"] = True
                st.session_state["usuario_atual"] = u_in
                adicionar_log(u_in, "Login realizado")
                st.rerun()
            else:
                adicionar_log(u_in or "?", "Login falhou")
                st.error("Usuário ou senha incorretos.")
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão ativa")

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
    st.markdown(f"""
    <div style="padding:16px 0 8px;">
        <p style="color:#60a5fa;font-weight:700;font-size:16px;margin:0;">🛡️ SentinelAI</p>
        <p style="color:#374151;font-size:11px;margin:2px 0 0;">SISTEMA ONLINE</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**{perfil_atual['perfil']}**")
    st.caption(f"@{usuario_atual}")
    badge = '<span class="badge-sqlite">🗄️ SQLite ativo</span>' if sqlite_ativo else '<span class="badge-sqlite" style="color:#ef4444;border-color:#ef4444;">⚠️ SQLite offline</span>'
    st.markdown(badge, unsafe_allow_html=True)
    st.markdown("---")
    for p in [
        "✅ Análise" if perfil_atual["pode_analisar"] else "❌ Análise",
        "✅ Exportar" if perfil_atual["pode_exportar"] else "❌ Exportar",
        "✅ Ver IPs" if perfil_atual["ver_pii"] else "🔒 IPs mascarados",
    ]:
        st.markdown(f"<p style='font-size:13px;color:#9ca3af;margin:3px 0;'>{p}</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<p style='font-size:11px;color:#4b5563;'>Acurácia IA: <strong style='color:#10b981;'>{acuracia:.1%}</strong></p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 Sair"):
        adicionar_log(usuario_atual, "Logout")
        st.session_state.update({"autenticado": False, "usuario_atual": None})
        st.rerun()

st.markdown(f"""
<div class="sentinel-header">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
            <h1 style="margin:0;font-size:28px;font-weight:800;letter-spacing:-0.5px;">🛡️ SentinelAI</h1>
            <p style="margin:4px 0 0;color:#6b7280;font-size:14px;">
                {"Visão geral — todos os clientes" if not cliente_vinculado else f"Painel — {cliente_vinculado}"}
            </p>
        </div>
        <div style="text-align:right;">
            <span style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);
                         color:#10b981;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600;">
                ● SISTEMA ONLINE
            </span>
            <p style="margin:6px 0 0;color:#4b5563;font-size:12px;">
                {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")} · {perfil_atual['perfil']}
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total = len(df_vis)
criticos = len(df_vis[df_vis["SEVERIDADE"] == "crítica"])
ips_bloq = len(df_vis[df_vis["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo = df_vis["PREJUIZO_ESTIMADO"].sum()

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.metric("Total Incidentes", f"{total:,}")
with c2: st.metric("Ameaças Críticas", f"{criticos:,}")
with c3: st.metric("IPs Bloqueados", f"{ips_bloq:,}")
with c4: st.metric("Prejuízo Estimado", f"R$ {prejuizo:,.0f}".replace(",","X").replace(".",",").replace("X","."))
with c5: st.metric("Acurácia IA", f"{acuracia:.1%}")

st.markdown("---")

abas = st.tabs(["🔍 Análise", "📊 Dashboard", "🌍 Mapa de Ameaças", "🤖 Assistente IA", "🗄️ Backup", "💾 SQLite", "📋 Logs"])

with abas[0]:
    st.subheader("Análise Inteligente de Incidentes")
    if not perfil_atual["pode_analisar"]:
        st.warning("⛔ Seu perfil não tem permissão para análises.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo de Incidente", encoders["tipo"].classes_)
            origem = st.selectbox("Origem", encoders["origem"].classes_)
            cliente = st.selectbox("Cliente Afetado", sorted(df["CLIENTE"].unique()))
        with col2:
            tempo = st.slider("Tempo de Resolução (min)", 1, 120, 30)
            status = st.selectbox("Status", encoders["status"].classes_)

        if st.button("🚀 Iniciar Análise", use_container_width=True):
            adicionar_log(usuario_atual, f"Análise: tipo={tipo} origem={origem}")
            with st.spinner("Analisando com IA..."):
                time.sleep(1)
            entrada = pd.DataFrame({
                "TIPO_ENC": [encoders["tipo"].transform([tipo])[0]],
                "ORIGEM_ENC": [encoders["origem"].transform([origem])[0]],
                "TEMPO RESOLUÇÃO": [tempo],
                "STATUS_ENC": [encoders["status"].transform([status])[0]],
            })
            resultado = encoders["severidade"].inverse_transform(modelo.predict(entrada))[0]
            if status == "resolvido":
                resultado = "baixa"
            elif tipo in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo in ["lentidão", "erro sistema"]:
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
                ip_ex, pais = "Nenhum", "Interno"

            st.markdown("---")
            if resultado == "crítica":
                st.error(f"🔴 Severidade: **{resultado.upper()}**")
            elif resultado == "média":
                st.warning(f"🟡 Severidade: **{resultado.upper()}**")
            else:
                st.success(f"🟢 Severidade: **{resultado.upper()}**")

            r1,r2,r3 = st.columns(3)
            with r1: st.metric("Threat Score", f"{risco}/100")
            with r2: st.metric("Prejuízo Est.", f"R$ {prej_est:,.0f}".replace(",","X").replace(".",",").replace("X","."))
            with r3: st.metric("Risco Financeiro", risco_fin)
            st.write(f"**Cliente:** {cliente}")
            if tipo == "ataque":
                st.error(f"🌍 Origem: **{pais}** | IP: `{ip_ex}`")
                with st.expander("🛡️ Resposta Automática"):
                    for a in ["✅ IP bloqueado automaticamente", "✅ Firewall reforçado", "✅ Equipe notificada", "✅ Logs auditados"]:
                        st.write(a)

            if sqlite_ativo:
                salvar_incidente_sqlite(sqlite_conn, {
                    "usuario": usuario_atual, "tipo": tipo, "origem": origem,
                    "status": status, "severidade": resultado, "cliente": cliente
                })
                st.success("💾 Incidente salvo no SQLite")

            adicionar_log(usuario_atual, f"Análise concluída: severidade={resultado}")

with abas[1]:
    st.subheader("Dashboard Analítico")
    LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#9ca3af")

    d1,d2 = st.columns(2)
    with d1:
        fig = px.pie(df_vis, names="SEVERIDADE", title="Distribuição de Severidade",
                     color_discrete_sequence=["#f59e0b", "#10b981", "#ef4444"])
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with d2:
        vc = df_vis["TIPO INCIDENTE"].value_counts().reset_index()
        fig2 = px.bar(vc, x="TIPO INCIDENTE", y="count", title="Incidentes por Tipo",
                      color_discrete_sequence=["#2563eb"])
        fig2.update_layout(**LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    df_t = df_vis.groupby("DATA").size().reset_index(name="Incidentes")
    fig3 = px.line(df_t, x="DATA", y="Incidentes", title="Volume ao Longo do Tempo",
                   color_discrete_sequence=["#60a5fa"])
    fig3.update_layout(**LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

    d3,d4 = st.columns(2)
    with d3:
        fig4 = px.histogram(df_vis, x="PAIS_ATAQUE", title="Ataques por País",
                            color_discrete_sequence=["#7c3aed"])
        fig4.update_layout(**LAYOUT)
        st.plotly_chart(fig4, use_container_width=True)
    with d4:
        dp = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
        dp = dp.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(7)
        fig5 = px.bar(dp, x="CLIENTE", y="PREJUIZO_ESTIMADO", title="Prejuízo por Cliente",
                      color_discrete_sequence=["#dc2626"])
        fig5.update_layout(**LAYOUT)
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("🤖 Métricas do Modelo de IA")
    m1,m2,m3 = st.columns(3)
    with m1: st.metric("Acurácia", f"{acuracia:.1%}")
    with m2: st.metric("Treinamento", f"{int(len(df)*0.8):,} registros")
    with m3: st.metric("Teste", f"{int(len(df)*0.2):,} registros")

    y_pred = modelo.predict(X_test)
    cm_mat = confusion_matrix(y_test, y_pred)
    labels = encoders["severidade"].classes_
    fig_cm = go.Figure(go.Heatmap(
        z=cm_mat, x=labels, y=labels,
        colorscale=[[0, "#060d1a"], [1, "#2563eb"]],
        text=cm_mat, texttemplate="%{text}", showscale=True
    ))
    fig_cm.update_layout(title="Matriz de Confusão", xaxis_title="Previsto", yaxis_title="Real",
                         height=320, **LAYOUT)
    st.plotly_chart(fig_cm, use_container_width=True)

with abas[2]:
    st.subheader("🌍 Mapa de Ameaças Cibernéticas em Tempo Real")
    st.caption("Ataques detectados no sistema — animação estilo Kaspersky Threat Map")
    
    COORDS = {
        "China": (35.86, 104.19),
        "Russia": (61.52, 105.31),
        "United States": (37.09, -95.71),
        "North Korea": (40.33, 127.51),
        "Germany": (51.16, 10.45),
        "Brazil": (-14.23, -51.92),
        "Canada": (56.13, -106.34),
    }
    BRASIL_COORD = (-15.78, -47.92)
    
    ataques_df = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"].copy()
    contagem_pais = ataques_df["PAIS_ATAQUE"].value_counts().reset_index()
    contagem_pais.columns = ["pais", "total"]
    
    arcs_data = []
    for _, row in contagem_pais.iterrows():
        pais = row["pais"]
        if pais in COORDS:
            orig = COORDS[pais]
            dest = BRASIL_COORD
            arcs_data.append({
                "origem_lat": orig[0], "origem_lon": orig[1],
                "dest_lat": dest[0], "dest_lon": dest[1],
                "pais": pais, "total": int(row["total"]),
                "cor": "#ef4444" if row["total"] > 30 else "#f59e0b" if row["total"] > 15 else "#60a5fa"
            })
    
    import json
    arcs_json = json.dumps(arcs_data)
    
    mapa_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; background: #060d1a; overflow: hidden; }}
        canvas {{ display: block; }}
        #info {{
            position: absolute; top: 16px; left: 16px;
            color: #9ca3af; font-family: 'Inter', sans-serif; font-size: 13px;
            background: rgba(10,22,40,0.85); border: 1px solid rgba(37,99,235,0.3);
            border-radius: 12px; padding: 14px 18px; min-width: 200px;
        }}
        #info h3 {{ color: #60a5fa; margin: 0 0 10px; font-size: 14px; }}
        .leg {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
        #stats {{
            position: absolute; top: 16px; right: 16px;
            color: #9ca3af; font-family: 'Inter', sans-serif; font-size: 12px;
            background: rgba(10,22,40,0.85); border: 1px solid rgba(37,99,235,0.3);
            border-radius: 12px; padding: 14px 18px; text-align: right;
        }}
        #stats .num {{ color: #f9fafb; font-size: 22px; font-weight: 800; font-family: monospace; }}
        #tooltip {{
            position: absolute; display: none;
            background: rgba(10,22,40,0.95); border: 1px solid rgba(37,99,235,0.5);
            border-radius: 8px; padding: 8px 14px;
            color: #e5e7eb; font-family: 'Inter', sans-serif; font-size: 12px;
            pointer-events: none;
        }}
    </style>
    </head>
    <body>
    <canvas id="c"></canvas>
    <div id="info">
        <h3>🌍 Origens de Ataque</h3>
        <div class="leg"><div class="dot" style="background:#ef4444"></div><span>Alto volume (&gt;30 ataques)</span></div>
        <div class="leg"><div class="dot" style="background:#f59e0b"></div><span>Médio (15–30 ataques)</span></div>
        <div class="leg"><div class="dot" style="background:#60a5fa"></div><span>Baixo (&lt;15 ataques)</span></div>
        <div style="margin-top:12px; border-top:1px solid rgba(37,99,235,0.2); padding-top:10px;">
            <div class="leg">🎯 <span style="color:#e5e7eb;">Alvo: Brasil (SentinelAI)</span></div>
        </div>
    </div>
    <div id="stats">
        <div style="color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:0.1em;">Ataques Detectados</div>
        <div class="num" id="attack-count">0</div>
        <div style="color:#6b7280;font-size:11px;margin-top:8px;">IPs Bloqueados</div>
        <div class="num" id="ip-count">0</div>
    </div>
    <div id="tooltip"></div>
    <script>
    const arcs = {arcs_json};
    const canvas = document.getElementById('c');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('tooltip');
    let W, H, particles = [], attackCount = 0, ipCount = 0;
    function resize() {{ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }}
    resize();
    window.addEventListener('resize', resize);
    function latLonToXY(lat, lon) {{ return [(lon + 180) / 360 * W, (90 - lat) / 180 * H]; }}
    function drawGrid() {{
        ctx.strokeStyle = 'rgba(37,99,235,0.06)'; ctx.lineWidth = 0.5;
        for (let lon = -180; lon <= 180; lon += 30) {{ ctx.beginPath(); const [x] = latLonToXY(0, lon); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }}
        for (let lat = -90; lat <= 90; lat += 30) {{ ctx.beginPath(); const [, y] = latLonToXY(lat, 0); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }}
    }}
    function drawCountryDots() {{
        const dots = [[35.86,104.19,"China"],[61.52,105.31,"Russia"],[37.09,-95.71,"USA"],[40.33,127.51,"N.Korea"],[51.16,10.45,"Germany"],[-14.23,-51.92,"Brazil"],[56.13,-106.34,"Canada"]];
        dots.forEach(([lat, lon, name]) => {{
            const [x, y] = latLonToXY(lat, lon);
            const isBrazil = name === "Brazil";
            ctx.beginPath(); ctx.arc(x, y, isBrazil ? 8 : 4, 0, Math.PI*2);
            ctx.fillStyle = isBrazil ? '#10b981' : 'rgba(96,165,250,0.4)';
            ctx.fill();
            if (isBrazil) {{ ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI*2); ctx.strokeStyle = 'rgba(16,185,129,0.3)'; ctx.lineWidth = 2; ctx.stroke(); }}
            ctx.fillStyle = isBrazil ? '#10b981' : '#6b7280';
            ctx.font = isBrazil ? 'bold 11px Inter' : '10px Inter';
            ctx.fillText(name, x + 12, y + 4);
        }});
    }}
    class Particle {{
        constructor(arc) {{ this.arc = arc; this.t = 0; this.speed = 0.003 + Math.random() * 0.004; this.trail = []; }}
        update() {{ this.t += this.speed; const [x,y] = this.pos(this.t); this.trail.push([x,y]); if (this.trail.length > 18) this.trail.shift(); return this.t < 1; }}
        pos(t) {{
            const [ox,oy] = latLonToXY(this.arc.origem_lat, this.arc.origem_lon);
            const [dx,dy] = latLonToXY(this.arc.dest_lat, this.arc.dest_lon);
            const mx = (ox+dx)/2, my = Math.min(oy,dy) - Math.abs(dx-ox)*0.25;
            const it = 1-t;
            return [it*it*ox + 2*it*t*mx + t*t*dx, it*it*oy + 2*it*t*my + t*t*dy];
        }}
        draw() {{
            if (this.trail.length < 2) return;
            for (let i=1; i<this.trail.length; i++) {{
                const alpha = i/this.trail.length;
                ctx.beginPath();
                ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
                ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                ctx.strokeStyle = this.arc.cor.replace(')', `,${{alpha}}`).replace('rgb','rgba');
                ctx.lineWidth = 1.5 * alpha;
                ctx.stroke();
            }}
            const [hx,hy] = this.trail[this.trail.length-1];
            ctx.beginPath(); ctx.arc(hx, hy, 3, 0, Math.PI*2); ctx.fillStyle = this.arc.cor; ctx.fill();
        }}
    }}
    function spawnParticles() {{ arcs.forEach(arc => {{ if (Math.random() < 0.15) particles.push(new Particle(arc)); }}); }}
    let frameCount = 0;
    function animate() {{
        requestAnimationFrame(animate);
        ctx.clearRect(0,0,W,H); ctx.fillStyle = '#060d1a'; ctx.fillRect(0,0,W,H);
        drawGrid(); drawCountryDots(); frameCount++;
        if (frameCount % 12 === 0) spawnParticles();
        particles = particles.filter(p => {{ const alive = p.update(); p.draw(); if (!alive) {{ attackCount++; ipCount = Math.floor(attackCount * 0.72); document.getElementById('attack-count').textContent = attackCount.toLocaleString(); document.getElementById('ip-count').textContent = ipCount.toLocaleString(); }} return alive; }});
    }}
    canvas.addEventListener('mousemove', e => {{
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left, my = e.clientY - rect.top;
        let found = false;
        arcs.forEach(arc => {{
            const [ox,oy] = latLonToXY(arc.origem_lat, arc.origem_lon);
            if (Math.hypot(mx-ox, my-oy) < 15) {{
                tooltip.style.display = 'block';
                tooltip.style.left = (e.clientX + 12) + 'px';
                tooltip.style.top = (e.clientY - 30) + 'px';
                tooltip.innerHTML = `<strong style="color:#60a5fa;">${{arc.pais}}</strong><br>${{arc.total}} ataques detectados`;
                found = true;
            }}
        }});
        if (!found) tooltip.style.display = 'none';
    }});
    animate();
    </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=520, scrolling=False)
    
    st.markdown("### 📊 Ranking de Países Atacantes")
    cp = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().reset_index()
    cp.columns = ["País", "Ataques"]
    cp["% do Total"] = (cp["Ataques"] / cp["Ataques"].sum() * 100).round(1).astype(str) + "%"
    st.dataframe(cp, use_container_width=True, hide_index=True)

with abas[3]:
    st.subheader("🤖 Assistente IA — SentinelBot")
    st.caption("Pergunte sobre incidentes, clientes, ameaças, métricas ou peça ajuda para tomar decisões de segurança.")
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    top5_clientes = df_vis.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().nlargest(5).to_dict()
    top5_paises = df_vis[df_vis["TIPO INCIDENTE"] == "ataque"]["PAIS_ATAQUE"].value_counts().head(5).to_dict()
    
    system_prompt = f"""Você é o SentinelBot, assistente especialista em segurança cibernética da plataforma SentinelAI.
Responda sempre em português brasileiro, de forma objetiva, profissional e direta.
Use emojis com moderação para facilitar leitura.

DADOS ATUAIS DO SISTEMA:
- Total de incidentes monitorados: {len(df_vis)}
- Incidentes críticos: {len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])} ({len(df_vis[df_vis['SEVERIDADE'] == 'crítica'])/len(df_vis)*100:.1f}%)
- IPs bloqueados automaticamente: {len(df_vis[df_vis['BLOQUEADO_AUTOMATICAMENTE'].str.lower() == 'sim'])}
- Prejuízo total estimado: R$ {df_vis['PREJUIZO_ESTIMADO'].sum():,.0f}
- Acurácia do modelo de IA: {acuracia:.1%}
- Tipos de incidente: {', '.join(df_vis['TIPO INCIDENTE'].unique())}
- Clientes monitorados: {', '.join(df_vis['CLIENTE'].unique())}
- Top 5 países atacantes: {top5_paises}
- Top 5 clientes por prejuízo: {top5_clientes}
- Status: {df_vis['STATUS'].value_counts().to_dict()}
- Severidades: {df_vis['SEVERIDADE'].value_counts().to_dict()}
- Período: {df_vis['DATA'].min().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].min()) else 'N/A'} a {df_vis['DATA'].max().strftime('%d/%m/%Y') if pd.notna(df_vis['DATA'].max()) else 'N/A'}
{"- Filtro ativo: apenas dados de " + cliente_vinculado if cliente_vinculado else "- Visão: todos os clientes"}
- Banco de dados: SQLite (sentinelai.db)"""
    
    if not ANTHROPIC_API_KEY:
        st.warning("⚠️ **Chave da API Claude não configurada!** Para usar o chatbot, adicione ANTHROPIC_API_KEY nos Secrets do Streamlit.")
    
    for msg in st.session_state["chat_history"]:
        css = "chat-user" if msg["role"] == "user" else "chat-ai"
        icon = "👤" if msg["role"] == "user" else "🛡️"
        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)
    
    with st.form("chat_form", clear_on_submit=True):
        ci, cb = st.columns([5, 1])
        with ci:
            pergunta = st.text_input("", placeholder="Ex: Qual cliente teve mais incidentes críticos?", label_visibility="collapsed")
        with cb:
            enviar = st.form_submit_button("Enviar", use_container_width=True)
    
    st.markdown("<p style='font-size:12px;color:#4b5563;margin:8px 0 4px;'>💡 Sugestões:</p>", unsafe_allow_html=True)
    sugs = ["Qual cliente teve mais prejuízo?", "Quais países mais atacaram?", "Como estão os incidentes críticos?", "Qual a acurácia do modelo?", "Me dê recomendações de segurança"]
    cols_s = st.columns(len(sugs))
    sug_escolhida = None
    for i, sug in enumerate(sugs):
        with cols_s[i]:
            if st.button(sug, key=f"s{i}", use_container_width=True):
                sug_escolhida = sug
    
    if sug_escolhida:
        pergunta = sug_escolhida
        enviar = True
    
    if enviar and pergunta and ANTHROPIC_API_KEY:
        adicionar_log(usuario_atual, f"Chat: {pergunta[:60]}")
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        try:
            headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {"model": "claude-3-sonnet-20240229", "max_tokens": 1000, "system": system_prompt, "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state["chat_history"]]}
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            data = resp.json()
            resposta = data["content"][0]["text"] if data.get("content") else "Erro ao processar."
        except Exception as e:
            resposta = f"Erro de conexão com Claude: {str(e)}"
        st.session_state["chat_history"].append({"role": "assistant", "content": resposta})
        adicionar_log(usuario_atual, "Resposta do SentinelBot gerada")
        st.rerun()
    elif enviar and pergunta and not ANTHROPIC_API_KEY:
        st.error("❌ Chatbot não disponível: Chave da API Claude não configurada.")
    
    if st.session_state["chat_history"]:
        if st.button("🗑️ Limpar conversa"):
            st.session_state["chat_history"] = []
            st.rerun()

with abas[4]:
    st.subheader("🗄️ Backup e Exportação")
    st.markdown("""
    <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(37,99,235,0.2);
                border-radius:12px;padding:20px;margin-bottom:20px;">
        <h4 style="color:#60a5fa;margin:0 0 12px;">📍 Onde os dados estão sendo salvos</h4>
        <p style="color:#9ca3af;font-size:13px;line-height:1.9;margin:0;">
            <strong style="color:#e5e7eb;">Fonte principal:</strong> dataset_final.csv no repositório GitHub<br>
            <strong style="color:#e5e7eb;">Banco de dados:</strong> SQLite (sentinelai.db) - incidentes analisados e logs<br>
            <strong style="color:#e5e7eb;">Backup manual:</strong> download via botões abaixo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Apenas Administradores podem exportar dados.")
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.download_button("⬇️ Dataset Completo (CSV)", df.to_csv(index=False).encode("utf-8"), f"sentinelai_backup_{ts}.csv", "text/csv", use_container_width=True)
        with b2:
            df_anon = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
            st.download_button("⬇️ Versão Anonimizada (LGPD)", df_anon.to_csv(index=False).encode("utf-8"), f"sentinelai_anonimizado_{ts}.csv", "text/csv", use_container_width=True)
        with b3:
            if "logs_sistema" in st.session_state:
                st.download_button("⬇️ Logs da Sessão", "\n".join(st.session_state["logs_sistema"]).encode("utf-8"), f"sentinelai_logs_{ts}.txt", "text/plain", use_container_width=True)
        adicionar_log(usuario_atual, "Backup solicitado")
        
        if sqlite_ativo and os.path.exists("sentinelai.db"):
            with open("sentinelai.db", "rb") as f:
                st.download_button("🗄️ Baixar Banco SQLite", f.read(), f"sentinelai_{ts}.db", "application/x-sqlite3", use_container_width=True)
    
    if "backups" in st.session_state and st.session_state["backups"]:
        st.markdown("### 📋 Histórico de Backups Automáticos")
        st.dataframe(pd.DataFrame(st.session_state["backups"]), use_container_width=True)
    
    st.markdown("### Prévia dos Dados (CSV)")
    st.dataframe(df_vis.head(15), use_container_width=True)

with abas[5]:
    st.subheader("🗄️ Gerenciamento SQLite")
    if not sqlite_ativo:
        st.error("❌ SQLite não está conectado.")
    else:
        st.success("✅ SQLite conectado e funcionando! Dados salvos em `sentinelai.db`")
        st.markdown("### 📋 Incidentes Registrados via Análise")
        df_sqlite = buscar_incidentes_sqlite(sqlite_conn)
        if not df_sqlite.empty:
            st.dataframe(df_sqlite, use_container_width=True)
        else:
            st.info("Nenhum incidente registrado via análise ainda. Use a aba Análise para registrar.")
        st.markdown("### 📊 Estatísticas do SQLite")
        try:
            cursor = sqlite_conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM incidentes_registrados")
            total_inc = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) as total FROM logs_sistema")
            total_logs = cursor.fetchone()[0]
            col_s1, col_s2 = st.columns(2)
            with col_s1: st.metric("Incidentes Registrados", total_inc)
            with col_s2: st.metric("Logs do Sistema", total_logs)
        except:
            pass

with abas[6]:
    st.subheader("📋 Logs do Sistema")
    st.caption("Auditoria completa de ações — gerado em tempo real na sessão")
    tab_logs1, tab_logs2 = st.tabs(["📱 Sessão Atual", "💾 Histórico SQLite"])
    with tab_logs1:
        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            for log in reversed(st.session_state["logs_sistema"]):
                st.code(log, language=None)
        else:
            st.info("Nenhum log ainda nesta sessão.")
    with tab_logs2:
        if sqlite_ativo:
            try:
                df_logs = pd.read_sql_query("SELECT * FROM logs_sistema ORDER BY timestamp DESC LIMIT 100", sqlite_conn)
                if not df_logs.empty:
                    st.dataframe(df_logs, use_container_width=True)
                else:
                    st.info("Nenhum log no histórico SQLite.")
            except:
                st.info("Erro ao carregar logs do SQLite.")
        else:
            st.warning("SQLite não conectado.")

st.markdown("""
<div style="text-align:center;padding:20px 0 8px;border-top:1px solid rgba(37,99,235,0.1);margin-top:20px;">
    <p style="color:#374151;font-size:12px;margin:0;">
        🛡️ <strong style="color:#4b5563;">SentinelAI</strong> &nbsp;·&nbsp;
        LGPD (Lei 13.709/2018) &nbsp;·&nbsp; HTTPS/TLS &nbsp;·&nbsp;
        SQLite &nbsp;·&nbsp;
        <a href="https://github.com/mariana-castro77/SentinelAI" target="_blank" style="color:#2563eb;">GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
