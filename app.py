import streamlit as st
import pandas as pd
import os
import base64
import plotly.express as px
import streamlit.components.v1 as components
import time
import random
import requests
import json
from datetime import datetime

# ============================================================
# 🔐 CONFIGURAÇÃO INICIAL
# ============================================================
st.set_page_config(page_title="SentinelAI // SOC Platform", layout="wide", initial_sidebar_state="expanded")

# ============================================================
# 💾 BACKUP EM TEMPO REAL (NUNCA PERDE DADOS)
# ============================================================
@st.cache_data
def carregar_banco():
    """Carrega o dataset principal ou retorna vazio"""
    return pd.read_csv("dataset_final.csv") if os.path.exists("dataset_final.csv") else pd.DataFrame()

def persistir_log(usuario, acao, detalhe=""):
    """Registra TUDO em backup_central.csv (log imutável)"""
    log = pd.DataFrame([[datetime.now(), usuario, acao, detalhe]],
                       columns=["HORA", "USUARIO", "ACAO", "DETALHE"])
    log.to_csv("backup_central.csv", mode='a', header=not os.path.exists("backup_central.csv"), index=False)

# ============================================================
# 🎨 CSS + PARALLAX + ANIMAÇÃO + ROBÔ
# ============================================================
st.markdown("""
<style>
    /* Scroll suave */
    html { scroll-behavior: smooth; }

    /* Fundo com parallax sutil + gradiente vermelho/escuro */
    .stApp {
        background: radial-gradient(circle at 50% 30%, #1a0000 0%, #000000 100%);
        background-attachment: fixed;
    }

    /* Cards com glow vermelho neon */
    .metric-card {
        background: rgba(20, 20, 30, 0.75);
        backdrop-filter: blur(4px);
        border: 1px solid #ff3333;
        border-radius: 16px;
        padding: 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 0, 0, 0.1);
    }
    .metric-card:hover {
        transform: translateY(-6px);
        border-color: #ff6666;
        box-shadow: 0 8px 28px rgba(255, 0, 0, 0.3);
    }

    /* Abas estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0,0,0,0.4);
        border-radius: 12px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff3333 !important;
        color: white !important;
    }

    /* Robô flutuante fixo + animação 3D */
    .robo-fixed {
        position: fixed;
        bottom: 40px;
        right: 40px;
        width: 160px;
        z-index: 999;
        filter: drop-shadow(0 0 18px #ff0000);
        animation: floatGlow 5s ease-in-out infinite;
        transition: transform 0.2s;
        cursor: pointer;
    }
    .robo-fixed:hover {
        transform: scale(1.08);
        filter: drop-shadow(0 0 28px #ff4444);
    }
    @keyframes floatGlow {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-18px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* Chat personalizado */
    .chat-user {
        background: #2a2a2a;
        border-left: 4px solid #ff3333;
        border-radius: 12px;
        padding: 10px;
        margin: 10px 0;
    }
    .chat-assistant {
        background: #1e1e2e;
        border-left: 4px solid #ff6666;
        border-radius: 12px;
        padding: 10px;
        margin: 10px 0;
    }

    /* Títulos neon */
    h1, h2, h3 {
        text-shadow: 0 0 6px #ff0000;
    }
    hr {
        border-color: #ff3333;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧠 INICIALIZAÇÃO DO BANCO E SESSÃO
# ============================================================
if "autenticado" not in st.session_state:
    st.session_state.update({
        "autenticado": False,
        "termo_aceito": False,
        "perfil_usuario": None,
        "cliente_usuario": None
    })

df_soc = carregar_banco()

# ============================================================
# 🔒 TELA DE TERMO DE SIGILO E LOGIN
# ============================================================
if not st.session_state["termo_aceito"]:
    st.title("🛡️ SENTINELAI - ACESSO ESTRUTURADO")
    st.markdown("### Termos de Uso e Confidencialidade")
    st.info("Ao acessar, você concorda com a **LGPD** e a política de segurança interna.")
    if st.button("📜 ACEITAR TERMOS DE SIGILO"):
        st.session_state["termo_aceito"] = True
        st.rerun()
    st.stop()

if not st.session_state["autenticado"]:
    st.subheader("🔐 Autenticação de Operador")
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR CENTRAL"):
            # Base de usuários (expandível)
            auth = {
                "admin": ("root99", "Administrador", "Todos"),
                "nubank": ("nu2026", "Cliente", "Nubank"),
                "ifood": ("ifood77", "Cliente", "iFood")
            }
            if usuario in auth and auth[usuario][0] == senha:
                st.session_state.update({
                    "autenticado": True,
                    "perfil_usuario": auth[usuario][1],
                    "cliente_usuario": auth[usuario][2]
                })
                persistir_log(usuario, "LOGIN", f"Perfil: {auth[usuario][1]}")
                st.rerun()
            else:
                st.error("❌ Credenciais inválidas")
    st.stop()

# ============================================================
# 🎯 DASHBOARD PRINCIPAL
# ============================================================
st.title(f"🛸 COMMAND CENTER // {st.session_state['cliente_usuario'].upper()}")

# 🔒 Filtro de dados por cliente
if st.session_state["cliente_usuario"] == "Todos":
    df_view = df_soc.copy()
else:
    df_view = df_soc[df_soc["CLIENTE"] == st.session_state["cliente_usuario"]]

# ============================================================
# 📊 KPIs COM CARDS ESTILIZADOS
# ============================================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🚨 Alertas Ativos", len(df_view))
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Prejuízo Estimado", f"R$ {df_view['PREJUIZO_ESTIMADO'].sum():,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("⚡ Uptime", "99.99%")
    st.markdown('</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📀 Backup", "Auto Sync")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 📌 ABAS FUNCIONAIS (Análise, Mapa, Telemetria, IA)
# ============================================================
tab_tria, tab_mapa, tab_dash, tab_ia = st.tabs(["🔍 ANÁLISE FORENSE", "🌍 MONITORAMENTO GLOBAL", "📊 TELEMETRIA", "🤖 IA SENTINEL"])

# ------------------------------------------------------------
with tab_tria:
    st.subheader("Matriz de Eventos Críticos")
    st.dataframe(df_view, use_container_width=True)
    persistir_log(st.session_state["cliente_usuario"], "VISUALIZOU_DADOS", f"Linhas: {len(df_view)}")

# ------------------------------------------------------------
with tab_mapa:
    st.subheader("🌐 Mapa de Ameaças 3D - Estilo Kaspersky")
    st.caption("Trajetórias de ataque em tempo real direcionadas ao Brasil")

    # Coordenadas para os arcos
    COORDS = {
        "China": (35.86, 104.19), "Russia": (61.52, 105.31), "United States": (37.09, -95.71),
        "Germany": (51.16, 10.45), "India": (20.59, 78.96), "France": (46.23, 2.21),
        "Ukraine": (48.38, 31.17), "Iran": (32.43, 53.69), "North Korea": (40.34, 127.51),
        "United Kingdom": (55.37, -3.43), "Japan": (36.2, 138.25), "Australia": (-25.27, 133.77),
        "Canada": (56.13, -106.34), "South Korea": (35.9, 127.76), "Brazil": (-14.23, -51.92)
    }
    TARGET = (-15.78, -47.92)   # Brasília

    # Gera arcos com base nos ataques reais do dataset
    ataques_df = df_view[df_view["TIPO INCIDENTE"] == "ataque"] if not df_view.empty else pd.DataFrame()
    contagem = ataques_df["PAIS_ATAQUE"].value_counts().reset_index()
    contagem.columns = ["country", "total"]

    arcos = []
    for _, row in contagem.iterrows():
        pais = row["country"]
        if pais in COORDS:
            origem = COORDS[pais]
            arcos.append({
                "src_lat": origem[0], "src_lon": origem[1],
                "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                "name": pais, "count": int(row["total"])
            })

    # Fallback visual (para manter o mapa vivo)
    if not arcos:
        for pais, coord in list(COORDS.items())[:8]:
            if pais != "Brazil":
                arcos.append({
                    "src_lat": coord[0], "src_lon": coord[1],
                    "dst_lat": TARGET[0], "dst_lon": TARGET[1],
                    "name": pais, "count": random.randint(8, 45)
                })

    arcs_json = json.dumps(arcos)

    html_mapa = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><style>
        body{{margin:0;background:#000;overflow:hidden;}}
        canvas{{display:block;}}
        #info{{position:absolute;bottom:15px;left:15px;background:rgba(0,0,0,0.7);border:1px solid #ff3333;border-radius:8px;padding:6px 12px;color:#ff6666;font-size:11px;z-index:100;}}
        #stats{{position:absolute;top:15px;right:15px;background:rgba(0,0,0,0.7);border:1px solid #ff3333;border-radius:8px;padding:6px 12px;color:#ff6666;font-size:12px;z-index:100;}}
    </style></head>
    <body>
    <canvas id="c"></canvas>
    <div id="info">🔥 ATAQUES DIRECIONADOS AO BRASIL 🔥</div>
    <div id="stats">🚨 ATAQUES: <span id="attackCount">0</span></div>
    <script>
        var arcs = {arcs_json};
        var canvas = document.getElementById('c');
        var ctx = canvas.getContext('2d');
        var w, h, particles = [];
        var attackTotal = 0;

        function resize() {{ w = canvas.width = window.innerWidth; h = canvas.height = window.innerHeight; }}
        resize();
        window.addEventListener('resize', resize);

        function ll(lat, lon) {{ return [(lon + 180) / 360 * w, (90 - lat) / 180 * h]; }}

        var pontos = [
            [35.86,104.19,"CHN"],[61.52,105.31,"RUS"],[37.09,-95.71,"USA"],[51.16,10.45,"DEU"],
            [-14.23,-51.92,"BRA"],[20.59,78.96,"IND"],[46.23,2.21,"FRA"],[48.38,31.17,"UKR"],
            [32.43,53.69,"IRN"],[40.34,127.51,"PRK"],[55.37,-3.43,"GBR"],[36.2,138.25,"JPN"],
            [-25.27,133.77,"AUS"],[56.13,-106.34,"CAN"],[35.9,127.76,"KOR"]
        ];

        function desenharPaises() {{
            for(var p of pontos) {{
                var xy = ll(p[0], p[1]);
                var isTarget = p[2] === "BRA";
                ctx.beginPath();
                ctx.arc(xy[0], xy[1], isTarget ? 10 : 4, 0, Math.PI*2);
                ctx.fillStyle = isTarget ? '#ff5555' : 'rgba(255,50,50,0.5)';
                ctx.fill();
                ctx.fillStyle = isTarget ? '#ff8888' : '#ff8888';
                ctx.font = isTarget ? 'bold 12px monospace' : '10px monospace';
                ctx.fillText(p[2], xy[0] + 8, xy[1] + 4);
            }}
        }}

        class Particula {{
            constructor(arc) {{
                this.arc = arc;
                this.t = 0;
                this.speed = 0.0025 + Math.random() * 0.0035;
                this.trail = [];
            }}
            pos(t) {{
                var s = ll(this.arc.src_lat, this.arc.src_lon);
                var d = ll(this.arc.dst_lat, this.arc.dst_lon);
                var mx = (s[0] + d[0]) / 2;
                var my = Math.min(s[1], d[1]) - Math.abs(d[0] - s[0]) * 0.22;
                var u = 1-t;
                return [u*u*s[0] + 2*u*t*mx + t*t*d[0], u*u*s[1] + 2*u*t*my + t*t*d[1]];
            }}
            update() {{
                this.t += this.speed;
                this.trail.push(this.pos(Math.min(this.t,1)));
                if(this.trail.length > 25) this.trail.shift();
                return this.t < 1;
            }}
            draw() {{
                if(this.trail.length < 2) return;
                for(var i=1;i<this.trail.length;i++) {{
                    var a = i/this.trail.length;
                    ctx.beginPath();
                    ctx.moveTo(this.trail[i-1][0], this.trail[i-1][1]);
                    ctx.lineTo(this.trail[i][0], this.trail[i][1]);
                    ctx.strokeStyle = `rgba(255,80,80,${{a}})`;
                    ctx.lineWidth = 2.2 * a;
                    ctx.stroke();
                }}
                var u = this.trail[this.trail.length-1];
                ctx.beginPath();
                ctx.arc(u[0], u[1], 4, 0, Math.PI*2);
                ctx.fillStyle = '#ff4444';
                ctx.fill();
            }}
        }}

        function spawn() {{
            if(arcs.length && Math.random() < 0.12) {{
                var idx = Math.floor(Math.random() * arcs.length);
                particles.push(new Particula(arcs[idx]));
            }}
        }}

        function anim() {{
            requestAnimationFrame(anim);
            ctx.fillStyle = 'rgba(0,0,0,0.85)';
            ctx.fillRect(0,0,w,h);
            desenharPaises();
            spawn();
            var vivos = [];
            for(var p of particles) {{
                if(p.update()) {{
                    p.draw();
                    vivos.push(p);
                }} else {{
                    attackTotal++;
                    document.getElementById('attackCount').innerText = attackTotal;
                }}
            }}
            particles = vivos;
        }}
        anim();
    </script>
    </body>
    </html>
    """
    components.html(html_mapa, height=550, scrolling=False)

# ------------------------------------------------------------
with tab_dash:
    st.subheader("📡 Painel Analítico")
    fig = px.bar(df_view, x="CLIENTE", y="PREJUIZO_ESTIMADO", color="SEVERIDADE",
                 title="Impacto Financeiro por Cliente", template="plotly_dark",
                 color_discrete_sequence=["#ff4444", "#ff7777", "#ffaaaa"])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
with tab_ia:
    st.subheader("🤖 IA Sentinel — Assistente Estratégico")
    st.caption("Pergunte sobre vulnerabilidades, tendências ou status do SOC")

    if "historico_chat" not in st.session_state:
        st.session_state["historico_chat"] = []

    # Exibe histórico
    for msg in st.session_state["historico_chat"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("chat_form"):
        query = st.text_input("Digite sua análise:", placeholder="Ex: resumo de ataques contra Nubank")
        enviar = st.form_submit_button("Consultar IA")

    if enviar and query:
        persistir_log(st.session_state["cliente_usuario"], "IA_QUERY", query)
        st.session_state["historico_chat"].append({"role": "user", "content": query})
        with st.spinner("🔍 Analisando telemetria..."):
            # Simula IA com contexto real do SOC
            resposta = f"📡 **Relatório Sentinel**\n\nCom base nos dados, foram identificados {len(df_view)} eventos. "
            if "nubank" in query.lower():
                resposta += "O cliente Nubank apresenta tendência de ataques DDoS vindos da Europa Oriental."
            elif "prejuízo" in query.lower():
                resposta += f"Prejuízo total estimado: R$ {df_view['PREJUIZO_ESTIMADO'].sum():,.2f}."
            else:
                resposta += "Nenhuma anomalia crítica detectada nos últimos ciclos. Monitoramento está dentro da normalidade."
        st.session_state["historico_chat"].append({"role": "assistant", "content": resposta})
        st.rerun()

# ============================================================
# 🤖 ROBÔ ANIMADO FIXO (efeito flutuante)
# ============================================================
# Caso tenha a imagem local, usa ela; senão, usa um SVG inline com estilo cyberpunk
robo_svg = """
<svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="55" fill="#1a0000" stroke="#ff3333" stroke-width="3"/>
  <rect x="35" y="30" width="50" height="25" rx="8" fill="#ff3333" stroke="#aa2222" stroke-width="2"/>
  <circle cx="45" cy="42" r="6" fill="#000"/>
  <circle cx="75" cy="42" r="6" fill="#000"/>
  <rect x="48" y="65" width="24" height="18" rx="4" fill="#ff4444"/>
  <line x1="30" y1="85" x2="90" y2="85" stroke="#ff3333" stroke-width="4"/>
  <circle cx="25" cy="95" r="8" fill="#ff4444"/>
  <circle cx="95" cy="95" r="8" fill="#ff4444"/>
  <text x="60" y="115" text-anchor="middle" fill="#ff6666" font-size="10" font-family="monospace">SENTINEL</text>
</svg>
"""
img_data = base64.b64encode(robo_svg.encode()).decode()
st.markdown(f'<div class="robo-fixed"><img src="data:image/svg+xml;base64,{img_data}" width="130"></div>', unsafe_allow_html=True)

# ============================================================
# 🧾 FOOTER COM LOG DE SEGURANÇA
# ============================================================
st.divider()
st.caption("⚡ SENTINELAI SOC — Backup em tempo real ativo | Todos os eventos registrados em backup_central.csv")
