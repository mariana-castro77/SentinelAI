import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import requests
import time
import os
import random

# ==============================================================================
# 1. CONFIGURAÇÃO AVANÇADA DA PLATAFORMA DE SEGURANÇA
# ==============================================================================
st.set_page_config(
    page_title="SentinelAI // Cyber Security Enterprise Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chave de contingência para o modelo de IA
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# ==============================================================================
# 2. CARREGAMENTO E TRATAMENTO DO DATASET REAL (CSV)
# ==============================================================================
@st.cache_data
def carregar_dados_sistema():
    caminho_arquivo = "dataset_final.csv" if os.path.exists("dataset_final.csv") else "dataset_mysql.csv"
    
    if os.path.exists(caminho_arquivo):
        df = pd.read_csv(caminho_arquivo)
    else:
        # Fallback estruturado idêntico ao layout do seu CSV original caso o arquivo suma
        dados_reserva = {
            "ID": range(1, 6),
            "DATA": ["2026-03-11", "2026-03-27", "2026-04-05", "2026-04-03", "2026-03-07"],
            "TIPO INCIDENTE": ["ataque", "lentidão", "ataque", "lentidão", "lentidão"],
            "SEVERIDADE": ["crítica", "crítica", "crítica", "média", "baixa"],
            "TEMPO RESOLUÇÃO": [24, 24, 78, 58, 49],
            "ORIGEM": ["aplicação", "rede", "servidor", "banco de dados", "aplicação"],
            "STATUS": ["pendente", "pendente", "resolvido", "pendente", "resolvido"],
            "PAIS_ATAQUE": ["China", "Interno", "Alemanha", "Rússia", "Estados Unidos"],
            "PREJUIZO_ESTIMADO": [13016, 18187, 15719, 4486, 1173],
            "CLIENTE": ["Nubank", "Santander", "Mercado Livre", "XP Investimentos", "iFood"],
            "IP_SUSPEITO": ["129.211.51.50", "Nenhum", "202.202.156.53", "185.220.101.5", "Nenhum"],
            "BLOQUEADO_AUTOMATICAMENTE": ["Sim", "Não", "Sim", "Não", "Não"],
            "RISCO_FINANCEIRO": ["médio", "alto", "alto", "médio", "baixo"]
        }
        df = pd.DataFrame(dados_reserva)
        
    # Padronização e limpeza estrita para garantir filtros precisos
    df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str).str.lower()
    df["ORIGEM"] = df["ORIGEM"].astype(str).str.lower()
    df["STATUS"] = df["STATUS"].astype(str).str.lower()
    df["CLIENTE"] = df["CLIENTE"].astype(str)
    return df

df_soc = carregar_dados_sistema()

# ==============================================================================
# 3. ESTILIZAÇÃO VISUAL CORPORATIVA (CSS CUSTOMIZADO)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* Fundo com efeito Parallax escuro */
.stApp {
    background-image: linear-gradient(180deg, rgba(15, 3, 3, 0.9) 0%, rgba(2, 4, 8, 0.97) 100%), 
                      url('https://images.unsplash.com/photo-1614064641938-3bbee52942c7?q=80&w=1920');
    background-attachment: fixed;
    background-size: cover;
    background-position: center;
}

/* Containers estilo HUD/Cards Militares */
.hud-container-soc {
    background: rgba(5, 9, 16, 0.95);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.9), inset 0 0 30px rgba(239, 68, 68, 0.05);
}

.titulo-holografico {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}
</style>
""", unsafe_allow_html=True)

# Inicialização dos estados de controle da sessão
if "termo_aceito" not in st.session_state:
    st.session_state["termo_aceito"] = False
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["perfil_usuario"] = None
    st.session_state["cliente_usuario"] = None

# ==============================================================================
# PÁGINA 1: TERMO DE COOKIES / LGPD (CONFORME O SEU DESENHO)
# ==============================================================================
if not st.session_state["termo_aceito"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_c1, c_center, c_c2 = st.columns([1, 1.8, 1])
    with c_center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Estrutura do Card baseado na sua imagem
        st.markdown("""
        <div class="hud-container-soc" style="border: 2px solid #ff3333; padding: 2.5rem; background: rgba(5, 9, 16, 0.98);">
            <div style="font-size: 3.5rem; margin-bottom: 1rem; text-align: center;">🛡️</div>
            <h2 class="titulo-holografico" style="font-size: 1.6rem; text-align: center; margin-bottom: 1.5rem;">
                TERMO DE CONFORMIDADE E PRIVACIDADE DE DADOS
            </h2>
            <p style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6; text-align: justify; margin-bottom: 2.5rem;">
                Em conformidade estrita com a <b>Lei Geral de Proteção de Dados (LGPD) - Lei nº 13.709/2018</b>, informamos que este ecossistema corporativo armazena cookies temporários e processa telemetrias perimetrais críticas em tempo real para garantir a estabilidade das aplicações. Ao avançar, você autoriza explicitamente a coleta de logs de auditoria e assume a responsabilidade de manter o sigilo absoluto sobre quaisquer dados e faturamentos de clientes exibidos neste centro de comando.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botões alinhados LADO A LADO: Aceitar antes, Recusar depois
        col_btn_aceitar, col_btn_recusar = st.columns(2)
        
        with col_btn_aceitar:
            if st.button("✓ ACEITAR E PROSSEGUIR", use_container_width=True, type="primary"):
                st.session_state["termo_aceito"] = True
                st.toast("Termo aceito com sucesso!", icon="🔓")
                time.sleep(0.4)
                st.rerun()
                
        with col_btn_recusar:
            if st.button("✕ RECUSAR ACESSO", use_container_width=True):
                st.error("Terminal bloqueado de forma preventiva.")
                st.stop()
                
    st.stop()

# ==============================================================================
# PÁGINA 2: SISTEMA DE LOGIN DE ALTO NÍVEL COM USUÁRIOS E PERFIS
# ==============================================================================
if not st.session_state["autenticado"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c_l1, c_login, c_l2 = st.columns([1, 1.6, 1])
    with c_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="hud-container-soc" style="text-align: center; margin-bottom: 1.5rem; padding: 1.5rem;">
            <span style="color: #ff3333; font-weight:700; font-size:0.75rem; letter-spacing:3px;">SENTINELAI SECURITY ENTERPRISE</span>
            <h2 class="titulo-holografico" style="margin-top:5px; font-size:1.8rem;">Autenticação de Perfil</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabela demonstrativa de usuários visível para a banca
        st.markdown("""
        <table style="width:100%; font-size:11px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.07); color:#8a99ad; margin-bottom:15px; border-collapse:collapse; text-align:left;">
            <thead>
                <tr style="border-bottom:1px solid rgba(255,255,255,0.1); color:#fff; background: rgba(239,68,68,0.1);">
                    <th style="padding:6px;">Usuário (User)</th>
                    <th style="padding:6px;">Senha (Password)</th>
                    <th style="padding:6px;">Nível/Perfil</th>
                    <th style="padding:6px;">Escopo de Dados</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">admin</td><td style="padding:5px;">root99</td><td style="padding:5px;">Administrador</td><td style="padding:5px;">Global Completo</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">analista</td><td style="padding:5px;">soc123</td><td style="padding:5px;">Analista SOC</td><td style="padding:5px;">Global Completo</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">nubank_view</td><td style="padding:5px;">nu2026</td><td style="padding:5px;">Viewer Cliente</td><td style="padding:5px; color:#ff7733;">Nubank</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">ifood_view</td><td style="padding:5px;">ifood77</td><td style="padding:5px;">Viewer Cliente</td><td style="padding:5px; color:#ff7733;">iFood</td></tr>
                <tr><td style="padding:5px; font-weight:bold; color:#fff;">mercado_view</td><td style="padding:5px;">ml2026</td><td style="padding:5px;">Viewer Cliente</td><td style="padding:5px; color:#ff7733;">Mercado Livre</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        with st.form("form_login_sistema"):
            usuario = st.text_input("Credencial do Usuário", placeholder="Ex: admin")
            senha = st.text_input("Assinatura Criptográfica", type="password", placeholder="••••••••")
            botao_entrar = st.form_submit_button("AUTENTICAR NO INFRAESTRUTURA")
            
            if botao_entrar:
                if usuario == "admin" and senha == "root99":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Administrador"
                    st.rerun()
                elif usuario == "analista" and senha == "soc123":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Analista"
                    st.rerun()
                elif usuario == "nubank_view" and senha == "nu2026":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Viewer"
                    st.session_state["cliente_usuario"] = "Nubank"
                    st.rerun()
                elif usuario == "ifood_view" and senha == "ifood77":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Viewer"
                    st.session_state["cliente_usuario"] = "iFood"
                    st.rerun()
                elif usuario == "mercado_view" and senha == "ml2026":
                    st.session_state["autenticado"] = True
                    st.session_state["perfil_usuario"] = "Viewer"
                    st.session_state["cliente_usuario"] = "Mercado Livre"
                    st.rerun()
                else:
                    st.error("Falha na validação das chaves de acesso.")
    st.stop()

# ==============================================================================
# PÁGINA 3: DASHBOARD PRINCIPAL - CONTROLE DE ESCOPO DO OPERADOR
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0;">
        <h2 class="titulo-holografico" style="font-size:1.8rem; margin:0;">Sentinel<span style="color:#ff3333;">AI</span></h2>
        <small style="color:#ff3333; font-weight:700; letter-spacing:1px;">{st.session_state['perfil_usuario'].upper()} MODE</small>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Restrição física de dados baseada no login do cliente
    if st.session_state["perfil_usuario"] == "Viewer":
        st.warning(f"Escopo limitado: {st.session_state['cliente_usuario']}")
        df_soc = df_soc[df_soc["CLIENTE"].str.lower() == st.session_state["cliente_usuario"].lower()]
        
    if st.button("🚪 ENCERRAR SESSÃO", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["perfil_usuario"] = None
        st.session_state["cliente_usuario"] = None
        st.rerun()

# Cabeçalho unificado do Command Center
st.markdown("""
<div class="hud-container-soc" style="padding: 1.2rem; margin-bottom: 1.5rem; background: linear-gradient(90deg, rgba(239,68,68,0.1) 0%, rgba(0,0,0,0) 100%); border-radius:8px;">
    <h1 class="titulo-holografico" style="margin: 0; font-size: 2rem;">Cyber Command Center Live Dashboard</h1>
</div>
""", unsafe_allow_html=True)

tab_analise, tab_mapa, tab_bi, tab_ia = st.tabs([
    "🔍 TRIAGEM FORENSE DE INCIDENTES", 
    "🌍 GLOBO LIVE KASPERSKY INTERATIVO", 
    "📊 TELEMETRIA CORPORATIVA", 
    "🤖 ASSISTENTE COGNITIVO SEGURADO"
])

# ==============================================================================
# ABA 1: TRIAGEM FORENSE CORRIGIDA COM OS FILTROS REAIS DO CSV
# ==============================================================================
with tab_analise:
    st.markdown("### Motores de Triagem Avançada")
    
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        tipo_sel = st.selectbox("Tipo de Incidente (Vetor)", sorted(df_soc["TIPO INCIDENTE"].unique()))
    with c_f2:
        # Filtro de Origem dinâmica puxando direto do seu arquivo CSV (banco de dados, rede, etc.)
        origem_sel = st.selectbox("Origem do Incidente (Asset)", sorted(df_soc["ORIGEM"].unique()))
    with c_f3:
        if st.session_state["perfil_usuario"] == "Viewer":
            lista_clientes = [st.session_state["cliente_usuario"]]
        else:
            lista_clientes = sorted(df_soc["CLIENTE"].unique())
        cliente_sel = st.selectbox("Cliente Corporativo Afetado", lista_clientes)

    c_f4, c_f5 = st.columns(2)
    with c_f4:
        status_sel = st.selectbox("Status Operacional Atual", sorted(df_soc["STATUS"].unique()))
    with c_f5:
        # Filtro real de tempo mapeado perfeitamente em minutos com base no seu dataset
        min_minutos = int(df_soc["TEMPO RESOLUÇÃO"].min())
        max_minutos = int(df_soc["TEMPO RESOLUÇÃO"].max())
        tempo_sel = st.slider("Tempo Limite de Resolução (Em Minutos)", min_minutos, max_minutos, max_minutos)

    st.markdown("<br>", unsafe_allow_html=True)
    
    key_execucao = f"analise_{tipo_sel}_{origem_sel}_{cliente_sel}"
    if key_execucao not in st.session_state:
        st.session_state[key_execucao] = False

    if st.button("🚀 DISPARAR INVESTIGAÇÃO PERIMETRAL", use_container_width=True):
        st.session_state[key_execucao] = True

    if st.session_state[key_execucao]:
        # Filtragem precisa baseada na sua seleção real
        res = df_soc[
            (df_soc["TIPO INCIDENTE"] == tipo_sel) & 
            (df_soc["ORIGEM"] == origem_sel) & 
            (df_soc["CLIENTE"] == cliente_sel) & 
            (df_soc["STATUS"] == status_sel) & 
            (df_soc["TEMPO RESOLUÇÃO"] <= tempo_sel)
        ]
        
        if res.empty:
            res = df_soc[(df_soc["TIPO INCIDENTE"] == tipo_sel) | (df_soc["CLIENTE"] == cliente_sel)]
            
        match = res.iloc[0] if not res.empty else df_soc.iloc[0]

        st.markdown("---")
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ff3333; padding: 12px; border-radius: 6px; margin-bottom: 1.5rem;">
            <span style="color: #ff3333; font-weight: bold;">🔴 Alerta Forense: Severidade Registrada como {match['SEVERIDADE'].upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        k_col1, k_col2, k_col3 = st.columns(3)
        with k_col1:
            st.metric("Risco Financeiro Atribuído", str(match['RISCO_FINANCEIRO']).upper())
        with k_col2:
            st.metric("Prejuízo Alocado", f"R$ {match['PREJUIZO_ESTIMADO']:,.2f}")
        with k_col3:
            st.metric("Tempo de Resolução", f"{match['TEMPO RESOLUÇÃO']} Minutos")

        st.markdown(f"""
        <div class="hud-container-soc" style="border-left: 4px solid #ff3333; margin-top:1rem; padding:1.2rem;">
            <p style="margin:0 0 6px 0;">🌐 <b>Endereço IP Rastreado:</b> <span style="color:#ff3333; font-family:monospace;">{match['IP_SUSPEITO']}</span></p>
            <p style="margin:0 0 6px 0;">🌍 <b>País de Origem do Ataque:</b> {match['PAIS_ATAQUE']}</p>
            <p style="margin:0;">⚙️ <b>Bloqueado de Forma Automática pelo Firewall:</b> {match['BLOQUEADO_AUTOMATICAMENTE']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>#### 🛠️ Plano Preventivo e Ações Corretivas SOC Engine", unsafe_allow_html=True)
        st.write("**O que foi feito ou será feito para mitigar este incidente:**")
        st.info("Varredura estrutural de privilégios completada, isolamento lógico do asset comprometido e rotatividade forçada das credenciais perimetrais.")
        
        st.write("**Solução de Engenharia de Longo Prazo:**")
        st.success("Refatoração das políticas de proteção de borda, implementação de barreira de mitigação de requisições por IP e auditoria continuada via Framework NIST.")
    else:
        st.markdown("<p style='color:#4f5e71; text-align:center; padding:3rem;'>Dispare o motor de triagem acima para processar as assinaturas operacionais do dataset.</p>", unsafe_allow_html=True)

# ==============================================================================
# ABA 2: GLOBO 3D INTERATIVO KASPERSKY COM CONTROLE LIVRE VIA MOUSE
# ==============================================================================
with tab_mapa:
    st.markdown("### Monitor Global de Ameaças (Kaspersky Threat Map)")
    st.caption("Interação Total: Clique e arraste com o mouse para girar o globo. Use o scroll para dar Zoom.")

    # Mapeando os ataques do arquivo real para alimentar o script JS do Globo 3D
    ataques_reais_js = []
    for _, row in df_soc.iterrows():
        if str(row["PAIS_ATAQUE"]) != "Interno":
            ataques_reais_js.append(f"{{origem: '{row['PAIS_ATAQUE']}', ip: '{row['IP_SUSPEITO']}', tipo: '{row['TIPO INCIDENTE']}', cliente: '{row['CLIENTE']}'}}")
    string_array_ataques = ", ".join(ataques_reais_js[:12])

    # Código HTML com Three.js e OrbitControls integrado para movimentação 100% interativa com o mouse
    kaspersky_globe_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <style>
            body { margin: 0; background: #03060d; overflow: hidden; font-family: 'Courier New', monospace; }
            #canvas-holder { width: 100%; height: 550px; position: relative; cursor: grab; }
            #canvas-holder:active { cursor: grabbing; }
            .kaspersky-hud { 
                position: absolute; top: 15px; left: 15px; 
                background: rgba(4,10,22,0.95); width: 330px;
                padding: 15px; border: 1px solid #ff3333; 
                font-size: 11px; color: #fff; border-radius: 6px;
                box-shadow: 0 0 25px rgba(255,51,51,0.2);
                pointer-events: none;
            }
            .hud-header { color: #ff3333; font-weight: bold; border-bottom: 1px solid rgba(255,51,51,0.3); padding-bottom: 5px; margin-bottom: 8px; letter-spacing:1px;}
            .feed-row { margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 4px; }
            .badge-neon { background: #ff3333; color: white; padding: 1px 4px; border-radius: 3px; font-size: 9px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div id="canvas-holder">
            <div class="kaspersky-hud">
                <div class="hud-header">📡 LIVE ATTACK MONITOR (KASPERSKY SIM)</div>
                <div id="live-feed-box"></div>
            </div>
        </div>
        <script>
            const dbAtaques = [__DATA_STREAM_ATAQUES__];
            const feedContainer = document.getElementById('live-feed-box');

            function streamingInterface() {
                feedContainer.innerHTML = "";
                for(let i=0; i<3; i++) {
                    let item = dbAtaques[Math.floor(Math.random() * dbAtaques.length)];
                    feedContainer.innerHTML += `
                        <div class="feed-row">
                            <span class="badge-neon">PACOTE MALICIOSO MITIGADO</span><br>
                            ⚔️ <b>PAÍS ATACANTE:</b> ${item.origem.toUpperCase()}<br>
                            🎯 <b>PAÍS ALVO:</b> Brasil (Infraestrutura ${item.cliente})<br>
                            🌐 <b>IP ORIGEM:</b> ${item.ip}
                        </div>
                    `;
                }
            }
            streamingInterface();
            setInterval(streamingInterface, 2500);

            // Inicialização da Scene 3D
            const container = document.getElementById('canvas-holder');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(60, container.clientWidth / 550, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(container.clientWidth, 550);
            container.appendChild(renderer.domElement);

            // ATIVAÇÃO COMPLETA DOS CONTROLES DO MOUSE
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.rotateSpeed = 0.7;

            // Esfera Sólida Base
            const geoPlaneta = new THREE.SphereGeometry(2.2, 45, 45);
            const matPlaneta = new THREE.MeshBasicMaterial({ color: 0x050a12 });
            const meshPlaneta = new THREE.Mesh(geoPlaneta, matPlaneta);
            scene.add(meshPlaneta);

            // Grid Metálico Iluminado Estilo Cyber Threat Map
            const matWireframe = new THREE.MeshBasicMaterial({ color: 0xff3333, wireframe: true, transparent: true, opacity: 0.14 });
            const meshWireframe = new THREE.Mesh(geoPlaneta, matWireframe);
            scene.add(meshWireframe);

            const arcGroup = new THREE.Group();
            scene.add(arcGroup);

            function drawAttackArc() {
                if(arcGroup.children.length > 15) arcGroup.remove(arcGroup.children[0]);
                
                const points = [];
                const startX = (Math.random() - 0.5) * 3.6;
                const startY = (Math.random() * 1.8) + 0.5;
                const startZ = Math.sqrt(Math.abs(4.84 - startX*startX - startY*startY));

                const endX = 0; const endY = -1.5; const startTargetZ = 1.6;

                for (let i = 0; i <= 40; i++) {
                    let t = i / 40;
                    let p = new THREE.Vector3().lerpVectors(new THREE.Vector3(startX, startY, startZ), new THREE.Vector3(endX, endY, startTargetZ), t);
                    p.normalize().multiplyScalar(2.2 + Math.sin(t * Math.PI) * 0.5); // Elevação da curva balística
                    points.push(p);
                }
                
                const curve = new THREE.CatmullRomCurve3(points);
                const geoLine = new THREE.BufferGeometry().setFromPoints(curve.getPoints(50));
                const matLine = new THREE.LineBasicMaterial({ color: 0xff3333, transparent: true, opacity: 0.85 });
                const line = new THREE.Line(geoLine, matLine);
                arcGroup.add(line);
            }
            setInterval(drawAttackArc, 600);

            camera.position.z = 4.6;

            function animationLoop() {
                requestAnimationFrame(animationLoop);
                meshPlaneta.rotation.y += 0.0012;
                meshWireframe.rotation.y += 0.0012;
                arcGroup.rotation.y += 0.0012;
                
                controls.update(); // Permite que o mouse controle a órbita livremente
                renderer.render(scene, camera);
            }
            window.addEventListener('resize', () => {
                camera.aspect = container.clientWidth / 550; camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, 550);
            });
            animationLoop();
        </script>
    </body>
    </html>
    """.replace("__DATA_STREAM_ATAQUES__", string_array_ataques)
    
    components.html(kaspersky_globe_html, height=560, scrolling=False)

# ==============================================================================
# ABA 3: TELEMETRIA CORPORATIVA (GRÁFICOS GERENCIAIS VIVOS)
# ==============================================================================
with tab_bi:
    st.markdown("### Telemetria e Consolidação Gerencial")
    
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        fig_pie = px.pie(df_soc, names="RISCO_FINANCEIRO", title="Distribuição Percentual de Risco Financeiro", color_discrete_sequence=["#ff3333", "#ff7733", "#22aa66"])
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c_g2:
        fig_bar = px.bar(df_soc, x="CLIENTE", y="PREJUIZO_ESTIMADO", color="TIPO INCIDENTE", title="Impacto Financeiro Mitigado por Carteira (R$)", color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# ABA 4: CHATBOT DE SEGURANÇA ISOLADO CONTRA CRASHES DE TELA
# ==============================================================================
with tab_ia:
    st.markdown("### Assistente Cognitivo SentinelCore")
    st.caption("Engine isolada para playbooks de remediação estruturados.")

    if "cyber_chat_v3" not in st.session_state:
        st.session_state["cyber_chat_v3"] = [
            {"role": "model", "content": "Sistema cognitivo ativado. Aguardando vetor ou comando técnico de varredura."}
        ]

    # Exibição do histórico de mensagens
    for msg in st.session_state["cyber_chat_v3"]:
        if msg["role"] == "user":
            st.markdown(f"""<div style='background:rgba(255,119,51,0.05); border-left:3px solid #ff7733; padding:10px; margin-bottom:8px; border-radius:4px;'><b>👤 Operador Técnico:</b><br>{msg['content']}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style='background:rgba(239,68,68,0.03); border-left:3px solid #ff3333; padding:10px; margin-bottom:8px; border-radius:4px;'><b>🤖 SentinelCore:</b><br>{msg['content']}</div>""", unsafe_allow_html=True)

    # Macros avançadas prontas para uso em apresentação
    st.markdown("<p style='color:#ff3333; font-size:0.75rem; font-weight:700; margin-top:1rem;'>DISPARAR SELEÇÃO DE MACROS SOC:</p>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    prompt_macro_acionado = ""
    with b1:
        if st.button("🔴 Auditoria Técnica: Bloqueio Geográfico de IPs Suspeitos", use_container_width=True):
            prompt_macro_acionado = "Explique estruturadamente como configurar firewalls de borda para realizar drop imediato de ataques volumétricos simulando logs da Kaspersky."
    with b2:
        if st.button("🔒 Isolar Infraestrutura: Vazamento em Banco de Dados", use_container_width=True):
            prompt_macro_acionado = "Quais as ações imediatas sob o framework NIST para mitigar o comprometimento de credenciais em APIs críticas corporativas?"

    # Entrada de texto com proteção completa de fluxo
    with st.form("chat_secure_v3", clear_on_submit=True):
        input_usuario = st.text_input("Inserir prompt de auditoria perimetral:", placeholder="Ex: Como proteger microsserviços do OWASP Top 10?")
        botao_disparo_chat = st.form_submit_button("DISPARAR PROMPT COGNITIVO")

    prompt_final_chat = input_usuario if botao_disparo_chat else prompt_macro_acionado

    if prompt_final_chat.strip():
        st.session_state["cyber_chat_v3"].append({"role": "user", "content": prompt_final_chat})
        
        # Estrutura de contingência para evitar quebras de tela caso a API falhe ou a chave suma
        if not GEMINI_API_KEY:
            resposta_segura = "⚠️ **Modo de Contingência Ativo:** Chave `GEMINI_API_KEY` ausente nos Secrets do Streamlit. Sistema operando em modo offline de resposta tática local."
        else:
            url_api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {"contents": [{"parts": [{"text": f"Você é uma IA de SOC de cibersegurança avançada corporativa. Responda tecnicamente em tópicos limpos:\n{prompt_final_chat}"}]}]}
            try:
                r_post = requests.post(url_api, json=payload, timeout=10)
                if r_post.status_code == 200:
                    resposta_segura = r_post.json()["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    resposta_segura = f"⚠️ **Alerta de Gateway:** O servidor retornou status HTTP {r_post.status_code}. Executando isolamento de pacotes preventivo."
            except Exception as e:
                resposta_segura = f"⚠️ **Timeout de Resposta:** Conexão interrompida com o gateway cognitivo externo. Código técnico: {str(e)}"
        
        st.session_state["cyber_chat_v3"].append({"role": "model", "content": resposta_segura})
        st.rerun()

# Streaming contínuo de pacotes de rodapé
st.markdown("---")
st.markdown("#### 📡 Inspeção Profunda de Pacotes em Tempo Real (Live Stream)")
momento_atual = datetime.datetime.now()
timestamps = [(momento_atual - datetime.timedelta(seconds=idx * 5)).strftime("%H:%M:%S") for idx in range(12)]
timestamps.reverse()
fluxo_requisicoes = [random.randint(1500, 4200) for _ in range(12)]

fig_stream = go.Figure()
fig_stream.add_trace(go.Scatter(x=timestamps, y=fluxo_requisicoes, mode='lines+markers', line=dict(color='#ff3333', width=3), fill='tozeroy', fillcolor='rgba(239,68,68,0.04)'))
fig_stream.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(4,8,16,0.6)", font_color="#8a99ad", margin=dict(l=30, r=30, t=30, b=30), height=180)
st.plotly_chart(fig_stream, use_container_width=True)
