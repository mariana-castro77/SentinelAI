import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import datetime
import requests
import time
import os

# Configuração da Chave da API do Gemini via Secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AQ.Ab8RN6JQCK4sNXAmcF1MuR_xMH6TiyijiYKMTlYeEQrG4gLwqA")

# 1. Configuração da Página Cyber SOC
st.set_page_config(
    page_title="SentinelAI // SOC Enterprise",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Carregamento do Dataset Oficial (CSV) com Fallback Seguro
@st.cache_data
def carregar_dataset_oficial():
    if os.path.exists("dataset_final.csv"):
        df = pd.read_csv("dataset_final.csv")
    elif os.path.exists("dataset_mysql.csv"):
        df = pd.read_csv("dataset_mysql.csv")
    else:
        dados_mock = {
            "ID": range(1, 6),
            "DATA": ["2026-03-11", "2026-03-27", "2026-04-05", "2026-04-03", "2026-03-07"],
            "TIPO INCIDENTE": ["Ataque", "Lentidão", "Ataque", "Lentidão", "Lentidão"],
            "SEVERIDADE": ["Crítica", "Crítica", "Crítica", "Média", "Baixa"],
            "TEMPO RESOLUÇÃO": [24, 24, 78, 58, 49],
            "ORIGEM": ["aplicação", "aplicação", "servidor", "banco de dados", "aplicação"],
            "STATUS": ["Pendente", "Pendente", "Resolvido", "Pendente", "Resolvido"],
            "PAIS_ATAQUE": ["China", "Interno", "Alemanha", "Interno", "Interno"],
            "PREJUIZO_ESTIMADO": [13016, 18187, 15719, 4486, 1173],
            "RECEITA_CLIENTE": [88516, 55707, 78030, 92356, 66453],
            "CLIENTE": ["Nubank", "Santander", "Mercado Livre", "XP Investimentos", "iFood"],
            "NIVEL_AMEACA": ["crítico", "crítico", "crítico", "médio", "baixo"],
            "IP_SUSPEITO": ["129.211.51.50", "Nenhum", "202.202.156.53", "Nenhum", "Nenhum"],
            "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Não", "Não"]
        }
        df = pd.DataFrame(dados_mock)
    
    df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str).str.title()
    df["SEVERIDADE"] = df["SEVERIDADE"].astype(str).str.title()
    df["STATUS"] = df["STATUS"].astype(str).str.title()
    df["CLIENTE"] = df["CLIENTE"].astype(str)
    return df

df_soc = carregar_dataset_oficial()

def adicionar_log(usuario, acao):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["logs_sistema"].append(f"[{ts}] {usuario} | {acao}")

# 3. Estilização Avançada Baseada no Kaspersky e Red Neon Aesthetics
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #e2e8f0;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #150505 0%, #05070a 70%, #010203 100%);
}

[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }

/* Sidebars e Painéis */
[data-testid="stSidebar"] {
    background: #040608 !important;
    border-right: 1px solid rgba(239, 68, 68, 0.2) !important;
}

div[data-testid="metric-container"] {
    background: rgba(11, 15, 23, 0.8);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
}
[data-testid="stMetricLabel"] { color: #8a99ad !important; font-size: 0.75rem !important; font-weight: 600; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #ff3333 !important; font-size: 1.8rem !important; font-family: 'Space Grotesk', sans-serif; }

/* Design das Abas */
.stTabs [data-baseweb="tab-list"] {
    background: #090d14 !important;
    border-radius: 8px !important;
    padding: 0.25rem !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(239, 68, 68, 0.15) !important;
    color: #ff3333 !important;
    border-radius: 6px !important;
}

/* Modais de Consentimento Centralizados */
.cookie-blur-bg {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(3, 4, 7, 0.9); backdrop-filter: blur(10px);
    z-index: 99998; display: flex; align-items: center; justify-content: center;
}
.cookie-modal-center {
    background: #080c12; border: 2px solid #ff3333; border-radius: 16px;
    padding: 2.5rem; max-width: 500px; width: 90%; text-align: center;
    box-shadow: 0 0 40px rgba(239, 68, 68, 0.25); z-index: 99999;
}

/* Cartões Técnicos de Análise */
.analise-card {
    background: #090d16;
    border-left: 4px solid #ff3333;
    padding: 1.2rem;
    border-radius: 4px 12px 12px 4px;
    margin-bottom: 1rem;
    border-top: 1px solid rgba(255,255,255,0.02);
    border-right: 1px solid rgba(255,255,255,0.02);
    border-bottom: 1px solid rgba(255,255,255,0.02);
}
</style>
""", unsafe_allow_html=True)

# 4. Estados Globais de Sessão
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
if "lgpd_consent" not in st.session_state:
    st.session_state["lgpd_consent"] = False

# --- CONTROLE LGPD CENTRALIZADO ---
if not st.session_state["lgpd_consent"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    st.markdown("""
    <div class="cookie-blur-bg">
        <div class="cookie-modal-center">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
            <h3 style="color: #fff; font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; margin-bottom: 1rem; font-weight:700;">CONTRATO DE CONFORMIDADE DE DADOS</h3>
            <p style="color: #8a99ad; font-size: 0.85rem; line-height: 1.6; margin-bottom: 2rem;">
                Este terminal processa dados de inteligência contra ameaças e mapeamento de tráfego corporativo. Ao prosseguir, você autoriza a indexação temporária dos datasets operacionais em conformidade com as diretrizes da LGPD.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c_sp, c_b1, c_b2, c_sp2 = st.columns([1, 1.5, 1.5, 1])
    with c_b1:
        if st.button("RECUSAR TERMO", use_container_width=True):
            st.error("Acesso negado.")
    with c_b2:
        if st.button("CONCORDAR E ENTRAR", use_container_width=True):
            st.session_state["lgpd_consent"] = True
            st.rerun()
    st.stop()

# --- INSTÂNCIA DE AUTENTICAÇÃO ---
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    c_l, c_mid, c_r = st.columns([1, 1.2, 1])
    with c_mid:
        st.markdown("""
        <div style="text-align: center; margin-top: 5rem; margin-bottom: 1.5rem;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; color: #fff; font-size: 2.2rem; margin: 0;">Sentinel<span style="color:#ff3333;">AI</span></h1>
            <p style="color: #4f5e71; font-size: 0.85rem;">Terminal de Monitoramento de Infraestrutura</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div style='background: #080c14; padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.03);'>", unsafe_allow_html=True)
            OPERADORES = {"admin": "admin123", "analista": "analista123", "supervisor": "superSOC99", "professor": "ecomove2026"}
            
            user_in = st.text_input("Operador (User)", placeholder="Ex: analista")
            pass_in = st.text_input("Token de Acesso", type="password", placeholder="••••••••")
            
            if st.button("CONECTAR AO CLUSTER", use_container_width=True):
                if user_in in OPERADORES and OPERADORES[user_in] == pass_in:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = user_in
                    adicionar_log(user_in, "Acessou a console principal do SOC")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

user_atual = st.session_state["usuario"]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='text-align:center; padding:1rem 0;'><h2 style='font-family:\"Space Grotesk\"; color:#fff; margin:0;'>Sentinel<span style='color:#ff3333;'>AI</span></h2></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); border-radius: 8px; padding: 0.8rem;'>
        <p style='color: #4f5e71; font-size: 0.65rem; margin:0; font-weight:700;'>OPERADOR LOGADO</p>
        <p style='color: #ffffff; font-weight: 700; margin: 0 0 0.3rem 0; font-size: 0.9rem;'>@{user_atual.upper()}</p>
        <span style="color:#10b981; font-size:0.7rem; font-weight:600;">● TELEMETRIA ATIVA (CSV)</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 DESCONECTAR TERMINAL", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

# --- CABEÇALHO ---
st.markdown("""
<div style="background: linear-gradient(90deg, rgba(239,68,68,0.05) 0%, rgba(0,0,0,0) 100%); border: 1px solid rgba(239,68,68,0.15); border-radius: 12px; padding: 1.2rem; margin-bottom: 1.5rem;">
    <p style="color: #ff3333; font-size: 0.7rem; font-weight: 700; letter-spacing: 2px; margin:0;">NÚCLEO DE RESPOSTA CRÍTICA</p>
    <h2 style="color: #fff; font-family: 'Space Grotesk', sans-serif; margin: 0; font-weight: 700;">Painel Integrado Contra Incidentes Virtuais</h2>
</div>
""", unsafe_allow_html=True)

# Métricas Principais
t_ocorr = len(df_soc)
t_crit = len(df_soc[df_soc["SEVERIDADE"].str.upper() == "CRÍTICA"])
t_prej = df_soc["PREJUIZO_ESTIMADO"].sum()

m1, m2, m3 = st.columns(3)
with m1: st.metric("Eventos Totais Mapeados", f"{t_ocorr:,}")
with m2: st.metric("Ameaças de Alta Severidade", f"{t_crit:,}")
with m3: st.metric("Prejuízo Histórico Mitigado", f"R$ {t_prej:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

tab_analise, tab_globe, tab_bi, tab_ai = st.tabs([
    "🔍 ANÁLISE COMPLETA", "🌍 GLOBO DE AMEAÇAS KASPERSKY", "📊 PERFORMANCE DASHBOARD", "🤖 ASSISTENTE COGNITIVO"
])

# --- ABA 1: ANÁLISE CONDICIONAL (SÓ EXIBE APÓS DISPARO) ---
with tab_analise:
    st.markdown("### Motores de Varredura Forense e Triagem")
    st.caption("Escolha os filtros corporativos baseados na base de dados para iniciar o mapeamento dinâmico.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tipo_sel = st.selectbox("Tipo de Vetor Identificado:", sorted(df_soc["TIPO INCIDENTE"].unique()))
    with col_f2:
        clientes_disp = sorted(df_soc[df_soc["TIPO INCIDENTE"] == tipo_sel]["CLIENTE"].unique())
        cliente_sel = st.selectbox("Organização/Cliente Afetado:", clientes_disp)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Controle de acionamento por Session State para não sumir ao interagir
    if f"scan_{tipo_sel}_{cliente_sel}" not in st.session_state:
        st.session_state[f"scan_{tipo_sel}_{cliente_sel}"] = False
        
    if st.button("⚡ INICIAR ANÁLISE FORENSE", use_container_width=True):
        prog_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            prog_bar.progress(i + 1)
        st.session_state[f"scan_{tipo_sel}_{cliente_sel}"] = True
        st.toast("Varredura estrutural concluída!", icon="🛡️")

    # Exibição condicional estrita solicitada pelo usuário
    if st.session_state[f"scan_{tipo_sel}_{cliente_sel}"]:
        dados_res = df_soc[(df_soc["TIPO INCIDENTE"] == tipo_sel) & (df_soc["CLIENTE"] == cliente_sel)]
        
        if not dados_res.empty:
            match = dados_res.iloc[0]
            st.markdown("---")
            st.markdown("#### 📋 Resultados Detalhados da Varredura")
            
            c_res1, c_res2, c_res3, c_res4 = st.columns(4)
            with c_res1:
                st.markdown(f"""<div class='analise-card'>
                    <p style='color:#8a99ad; font-size:0.7rem; margin:0;'>STATUS OPERACIONAL</p>
                    <b style='color:#ff3333; font-size:1.1rem;'>{match.get('STATUS', 'Pendente')}</b>
                </div>""", unsafe_allow_html=True)
            with c_res2:
                st.markdown(f"""<div class='analise-card'>
                    <p style='color:#8a99ad; font-size:0.7rem; margin:0;'>VETOR DE ORIGEM</p>
                    <b style='color:#fff; font-size:1.1rem;'>{match.get('PAIS_ATAQUE', 'Desconhecido')}</b>
                </div>""", unsafe_allow_html=True)
            with c_res3:
                st.markdown(f"""<div class='analise-card'>
                    <p style='color:#8a99ad; font-size:0.7rem; margin:0;'>IP SUSPEITO RASTREADO</p>
                    <b style='color:#ff3333; font-family:monospace; font-size:1.1rem;'>{match.get('IP_SUSPEITO', 'Nenhum')}</b>
                </div>""", unsafe_allow_html=True)
            with c_res4:
                st.markdown(f"""<div class='analise-card'>
                    <p style='color:#8a99ad; font-size:0.7rem; margin:0;'>DANO PATRIMONIAL</p>
                    <b style='color:#fff; font-size:1.1rem;'>R$ {match.get('PREJUIZO_ESTIMADO', 0):,.2f}</b>
                </div>""", unsafe_allow_html=True)
                
            # Playbook Automático de Resposta Integrado
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### ⚡ Resposta Automática Vinculada (Playbook SOC)")
            if "ataque" in tipo_sel.lower():
                msg_playbook = f"Regra perimetral disparada com sucesso. O IP corporativo {match.get('IP_SUSPEITO')} foi mitigado nas camadas de roteamento de borda do cliente {cliente_sel}."
            else:
                msg_playbook = f"A lentidão sistêmica foi contida através do rebalanceamento dinâmico dos clusters operacionais de processamento de dados do cliente {cliente_sel}."
                
            st.info(msg_playbook)
        else:
            st.warning("Nenhum registro correspondente foi localizado no arquivo CSV.")
    else:
        st.markdown("<p style='color:#4f5e71; text-align:center; padding:2rem;'>Aguardando comando de disparo do analista para expor os dados estruturais.</p>", unsafe_allow_html=True)

# --- ABA 2: GLOBO DE AMEAÇAS ESTILO KASPERSKY MAP COM ARCOS ---
with tab_globe:
    st.markdown("### Mapa de Ataques em Tempo Real (Kaspersky Inspired Style)")
    st.caption("Visualização tridimensional com projeção contínua de arcos balísticos neon conectando vetores globais.")
    
    lista_paises = [p for p in df_soc["PAIS_ATAQUE"].unique() if p != "Interno"]
    string_js_paises = ", ".join([f"'{p}'" for p in lista_paises])
    
    kaspersky_globe_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; background: #030508; overflow: hidden; font-family: 'Courier New', monospace; color: #ff3333; }
            #canvas-soc { width: 100%; height: 500px; position: relative; }
            .kaspersky-hud { position: absolute; bottom: 20px; left: 20px; background: rgba(5,8,14,0.95); padding: 15px; border-left: 3px solid #ff3333; font-size: 11px; color: #a2b4c7; border-radius: 0 8px 8px 0; }
            .country-tag { color: #fff; font-weight: bold; }
        </style>
    </head>
    <body>
        <div id="canvas-soc">
            <div class="kaspersky-hud">
                <span style="color:#ff3333; font-weight:bold;">[LIVE STREAMING CORE]</span><br>
                > MONITORANDO PAÍSES ALVO: <br>
                <span class="country-tag">[__PAISES__]</span>
            </div>
        </div>
        <script>
            const container = document.getElementById('canvas-soc');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(55, container.clientWidth / 500, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, 500);
            container.appendChild(renderer.domElement);

            // Esfera Principal do Planeta Escuro
            const globeGeo = new THREE.SphereGeometry(2, 40, 40);
            const globeMat = new THREE.MeshBasicMaterial({ color: 0x09101a, wireframe: false });
            const planet = new THREE.Mesh(globeGeo, globeMat);
            scene.add(planet);

            // Grid Neon da Malha Geopolítica
            const gridMat = new THREE.MeshBasicMaterial({ color: #ff3333, wireframe: true, transparent: true, opacity: 0.08 });
            const gridMesh = new THREE.Mesh(globeGeo, gridMat);
            scene.add(gridMesh);

            // Linhas de Ataque Balísticas Estilo Kaspersky
            const lineGroup = new THREE.Group();
            scene.add(lineGroup);

            function generateAttackArc() {
                if(lineGroup.children.length > 8) {
                    lineGroup.remove(lineGroup.children[0]);
                }
                const points = [];
                const startX = (Math.random() - 0.5) * 3;
                const startY = (Math.random() - 0.5) * 3;
                const startZ = Math.sqrt(4 - startX*startX - startY*startY) * (Math.random() > 0.5 ? 1 : -1);

                const endX = (Math.random() - 0.5) * 3;
                const endY = (Math.random() - 0.5) * 3;
                const endZ = Math.sqrt(4 - endX*endX - endY*endY) * (Math.random() > 0.5 ? 1 : -1);

                // Criar curva em arco entre os pontos
                for (let i = 0; i <= 20; i++) {
                    let t = i / 20;
                    let p = new THREE.Vector3().lerpVectors(new THREE.Vector3(startX, startY, startZ), new THREE.Vector3(endX, endY, endZ), t);
                    p.normalize().multiplyScalar(2 + Math.sin(t * Math.PI) * 0.4); // Altura do arco
                    points.push(p);
                }

                const curveQuad = new THREE.CatmullRomCurve3(points);
                const geoLine = new THREE.BufferGeometry().setFromPoints(curveQuad.getPoints(50));
                const matLine = new THREE.LineBasicMaterial({ color: Math.random() > 0.4 ? 0xff3333 : 0xffaa00, transparent: true, opacity: 0.8 });
                const line = new THREE.Line(geoLine, matLine);
                lineGroup.add(line);
            }

            setInterval(generateAttackArc, 1200);

            camera.position.z = 4.2;
            function animate() {
                requestAnimationFrame(animate);
                planet.rotation.y += 0.0015;
                gridMesh.rotation.y += 0.0015;
                lineGroup.rotation.y += 0.0015;
                renderer.render(scene, camera);
            }
            window.addEventListener('resize', () => {
                camera.aspect = container.clientWidth / 500; camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, 500);
            });
            animate();
        </script>
    </body>
    </html>
    """.replace("__PAISES__", string_js_paises).replace("#ff3333", "0xff3333")
    
    components.html(kaspersky_globe_html, height=520, scrolling=False)

# --- ABA 3: PERFORMANCE GRAPHICS ---
with tab_bi:
    st.markdown("### Monitoramento Estatístico de Riscos de Negócio")
    custom_layout = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#8a99ad")
    
    g1, g2 = st.columns(2)
    with g1:
        f_p = px.pie(df_soc, names="TIPO INCIDENTE", title="Incidências Relativas por Categoria", color_discrete_sequence=["#ff3333", "#ff7733", "#2266ff"])
        f_p.update_layout(**custom_layout)
        st.plotly_chart(f_p, use_container_width=True)
    with g2:
        f_b = px.bar(df_soc, x="CLIENTE", y="RECEITA_CLIENTE", color="NIVEL_AMEACA", title="Volume de Receita Protegida por Contrato", color_discrete_map={"crítico": "#ff3333", "médio": "#ff7733", "baixo": "#2266ff"})
        f_b.update_layout(**custom_layout)
        st.plotly_chart(f_b, use_container_width=True)

# --- ABA 4: CHATBOT COM COMANDOS RÁPIDOS ---
with tab_ai:
    st.markdown("### Assistente de Mitigação Cognitiva Core")
    
    if "chat_history_soc" not in st.session_state:
        st.session_state["chat_history_soc"] = []
        
    for m in st.session_state["chat_history_soc"]:
        cls = "chat-user" if m["role"] == "user" else "chat-ai"
        lbl = "👤 Operador" if m["role"] == "user" else "🤖 SentinelCore"
        st.markdown(f'<div class="{cls}"><b>{lbl}:</b> {m["content"]}</div>', unsafe_allow_html=True)
        
    st.markdown("<p style='color:#4f5e71; font-size:0.75rem; font-weight:700; margin-bottom:0.4rem;'>RODAR CONSULTAS PRÉ-MOLDADAS:</p>", unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    cmd_fast = ""
    with bc1:
        if st.button("📋 Executar Diagnóstico de Vulnerabilidades no Dataset", use_container_width=True):
            cmd_fast = "Gere um resumo técnico destacando quais são os principais países atacantes mapeados no nosso arquivo final e o prejuízo total causado por eles."
    with bc2:
        if st.button("🛡️ Executar Auditoria de Infraestrutura e Respostas", use_container_width=True):
            cmd_fast = "Forneça recomendações de isolamento de rede imediatas para conter anomalias classificadas com severidade crítica no SOC."
            
    with st.form("form_ai", clear_on_submit=True):
        pergunta = st.text_input("Comando customizado:", placeholder="Insira o prompt aqui...")
        enviado = st.form_submit_button("DISPARAR PROMPT")
        
    prompt_alvo = pergunta if enviado else cmd_fast
    
    if prompt_alvo.strip():
        st.session_state["chat_history_soc"].append({"role": "user", "content": prompt_alvo})
        
        ctx = f"Você é o núcleo de IA do SOC SentinelAI. Responda diretamente ao analista {user_atual} em português de forma concisa e estritamente profissional. Volume de dados ativos: {t_ocorr} logs."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": f"{ctx}\n\nComando: {prompt_alvo}"}]}]}, timeout=12)
            out = res.json()["candidates"][0]["content"]["parts"][0]["text"] if res.status_code == 200 else "Erro de comunicação corporativa."
        except:
            out = "Falha de comunicação de rede externa com o LLM."
            
        st.session_state["chat_history_soc"].append({"role": "model", "content": out})
        st.rerun()

# --- STREAMING DE MONITORAMENTO EM TEMPO REAL NO RODAPÉ ---
st.markdown("---")
st.markdown("#### 📡 Monitoramento de Fluxo em Tempo Real")
real_time_stream = f"""
<div style="background:#04070a; border: 1px solid rgba(255,255,255,0.05); padding: 0.8rem; border-radius: 8px; font-family:monospace; font-size: 0.75rem; color:#10b981;">
    <span style="color:#ff3333; font-weight:bold;">[LIVE STREAM]</span> Sincronizado com a sessão ativa de @{user_atual.upper()} | Última varredura realizada no lote de {t_ocorr} incidentes corporativos.
</div>
"""
st.markdown(real_time_stream, unsafe_allow_html=True)
