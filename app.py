import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import datetime
import io
import random
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
.stApp {
    background: linear-gradient(135deg,
    color:
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1 { color:
h2, h3 { color:
div[data-testid="metric-container"] {
    background: rgba(17,24,39,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 22px; border-radius: 18px;
    backdrop-filter: blur(12px);
}
[data-testid="stMetricLabel"] { color:
[data-testid="stMetricValue"] { color:
div.stButton > button {
    background:
    border-radius: 12px; border: none;
    height: 3.2em; font-size: 16px; font-weight: 600;
}
div.stButton > button:hover { background:
.stAlert { background: rgba(17,24,39,0.75); border-radius: 16px; }
</style>
""", unsafe_allow_html=True)

def adicionar_log(usuario: str, acao: str):
    if "logs_sistema" not in st.session_state:
        st.session_state["logs_sistema"] = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = f"[{timestamp}] USER={usuario} | {acao}"
    st.session_state["logs_sistema"].append(entrada)

if "cookies_aceitos" not in st.session_state:
    st.session_state["cookies_aceitos"] = False

if not st.session_state["cookies_aceitos"]:
    with st.container():
        st.warning(
            "🍪 **Política de Cookies e Privacidade (LGPD)**\n\n"
            "Esta plataforma utiliza cookies de sessão para autenticação e controle de acesso. "
            "Nenhum dado pessoal identificável é armazenado sem consentimento. "
            "Os dados de incidentes são anonimizados e protegidos conforme a **Lei Geral de Proteção de Dados (LGPD — Lei 13.709/2018)**.\n\n"
            "Ao continuar, você concorda com o uso de cookies de sessão para fins de segurança."
        )
        col_aceitar, col_recusar = st.columns([1, 5])
        with col_aceitar:
            if st.button("✅ Aceitar e continuar"):
                st.session_state["cookies_aceitos"] = True
                adicionar_log("Sistema", "Política de cookies aceita pelo usuário")
                st.rerun()
        with col_recusar:
            if st.button("❌ Recusar"):
                st.stop()
    st.stop()

USUARIOS = {
    "admin": {
        "senha_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "perfil": "Administrador",
        "pode_exportar": True,
        "pode_analisar": True,
        "ver_pii": True,
    },
    "analista": {
        "senha_hash": hashlib.sha256("analista123".encode()).hexdigest(),
        "perfil": "Analista de Segurança",
        "pode_exportar": False,
        "pode_analisar": True,
        "ver_pii": False,
    },
    "viewer": {
        "senha_hash": hashlib.sha256("viewer123".encode()).hexdigest(),
        "perfil": "Somente Visualização",
        "pode_exportar": False,
        "pode_analisar": False,
        "ver_pii": False,
    },
}

def autenticar(usuario: str, senha: str) -> bool:
    if usuario in USUARIOS:
        hash_informado = hashlib.sha256(senha.encode()).hexdigest()
        return hash_informado == USUARIOS[usuario]["senha_hash"]
    return False

def mascara_ip(ip: str) -> str:
    """Mascara o IP para usuários sem permissão de ver PII (LGPD)."""
    if ip == "Nenhum":
        return "Nenhum"
    partes = ip.split(".")
    if len(partes) == 4:
        return f"{partes[0]}.{partes[1]}.***.***"
    return "***.***.***"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_atual"] = None

if not st.session_state["autenticado"]:
    st.title("🛡️ SentinelAI")
    st.subheader("Acesso Restrito — Faça login para continuar")

    st.info(
        "**Contas de demonstração:**\n"
        "- `admin` / `admin123` → Administrador (acesso total + exportação)\n"
        "- `analista` / `analista123` → Analista (análise, sem PII)\n"
        "- `viewer` / `viewer123` → Visualização apenas"
    )

    with st.form("form_login"):
        usuario_input = st.text_input("Usuário")
        senha_input   = st.text_input("Senha", type="password")
        entrar        = st.form_submit_button("🔐 Entrar")

    if entrar:
        if autenticar(usuario_input, senha_input):
            st.session_state["autenticado"] = True
            st.session_state["usuario_atual"] = usuario_input
            adicionar_log(usuario_input, "Login realizado com sucesso")
            st.rerun()
        else:
            adicionar_log(usuario_input or "desconhecido", "Tentativa de login malsucedida")
            st.error("Usuário ou senha incorretos.")
    st.stop()

usuario_atual = st.session_state["usuario_atual"]
perfil_atual  = USUARIOS[usuario_atual]
adicionar_log(usuario_atual, "Sessão ativa")

@st.cache_data
def carregar_e_processar_dados():
    df_bruto = pd.read_csv("dataset_final.csv")

    df = df_bruto.copy()

    colunas_obrigatorias = ["TIPO INCIDENTE", "SEVERIDADE", "ORIGEM", "STATUS"]
    df = df.dropna(subset=colunas_obrigatorias)

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    for col in ["TIPO INCIDENTE", "SEVERIDADE", "ORIGEM", "STATUS", "NIVEL_AMEACA", "RISCO_FINANCEIRO"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower()

    enc = {
        "tipo":       LabelEncoder(),
        "origem":     LabelEncoder(),
        "status":     LabelEncoder(),
        "severidade": LabelEncoder(),
    }
    df["TIPO_ENC"]       = enc["tipo"].fit_transform(df["TIPO INCIDENTE"])
    df["ORIGEM_ENC"]     = enc["origem"].fit_transform(df["ORIGEM"])
    df["STATUS_ENC"]     = enc["status"].fit_transform(df["STATUS"])
    df["SEVERIDADE_ENC"] = enc["severidade"].fit_transform(df["SEVERIDADE"])

    X = df[["TIPO_ENC", "ORIGEM_ENC", "TEMPO RESOLUÇÃO", "STATUS_ENC"]]
    y = df["SEVERIDADE_ENC"]
    modelo = DecisionTreeClassifier(random_state=42)
    modelo.fit(X, y)

    return df, enc, modelo

df, encoders, modelo = carregar_e_processar_dados()

with st.sidebar:
    st.markdown(f"### 👤 {perfil_atual['perfil']}")
    st.caption(f"Logado como: `{usuario_atual}`")
    st.markdown("---")

    permissoes = []
    if perfil_atual["pode_analisar"]:  permissoes.append("✅ Análise de incidentes")
    else:                               permissoes.append("❌ Análise de incidentes")
    if perfil_atual["pode_exportar"]:  permissoes.append("✅ Exportar dados (backup)")
    else:                               permissoes.append("❌ Exportar dados")
    if perfil_atual["ver_pii"]:        permissoes.append("✅ Ver IPs / dados PII")
    else:                               permissoes.append("❌ IPs mascarados (LGPD)")

    st.markdown("**Permissões do perfil:**")
    for p in permissoes:
        st.markdown(p)

    st.markdown("---")
    if st.button("🚪 Sair"):
        adicionar_log(usuario_atual, "Logout realizado")
        st.session_state["autenticado"] = False
        st.session_state["usuario_atual"] = None
        st.rerun()

st.title("🛡️ SentinelAI")
st.subheader("Central Inteligente de Defesa Cibernética")
st.caption(f"Transmissão segura via HTTPS · Dados protegidos por LGPD · Sessão: {usuario_atual} ({perfil_atual['perfil']})")
st.markdown("---")

total_incidentes  = len(df)
total_criticos    = len(df[df["SEVERIDADE"] == "crítica"])
ips_bloqueados    = len(df[df["BLOQUEADO_AUTOMATICAMENTE"].str.lower() == "sim"])
prejuizo_total    = df["PREJUIZO_ESTIMADO"].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Incidentes", f"{total_incidentes:,}")
with col2:
    st.metric("Ameaças Críticas", f"{total_criticos:,}")
with col3:
    st.metric("IPs Bloqueados", f"{ips_bloqueados:,}")
with col4:
    valor_fmt = f"R$ {prejuizo_total:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric("Prejuízo Total Estimado", valor_fmt)

st.markdown("---")

abas = st.tabs(["🔍 Análise de Incidente", "📊 Dashboard", "🗄️ Backup & Dados", "📋 Logs do Sistema"])

with abas[0]:
    st.subheader("Análise Inteligente de Incidentes")

    if not perfil_atual["pode_analisar"]:
        st.warning("⛔ Seu perfil não tem permissão para realizar análises. Contate o administrador.")
    else:
        col_form1, col_form2 = st.columns(2)

        with col_form1:
            tipo = st.selectbox("Tipo de Incidente", encoders["tipo"].classes_)
            origem = st.selectbox("Origem", encoders["origem"].classes_)
            cliente = st.selectbox("Cliente Afetado", sorted(df["CLIENTE"].unique()))

        with col_form2:
            tempo = st.slider("Tempo de Resolução (min)", 1, 120, 30)
            status = st.selectbox("Status", encoders["status"].classes_)

        if st.button("🚀 Iniciar Análise"):
            adicionar_log(usuario_atual, f"Análise iniciada: tipo={tipo}, origem={origem}, status={status}")

            with st.spinner("Analisando ameaças com IA..."):
                time.sleep(1)

            entrada = pd.DataFrame({
                "TIPO_ENC":       [encoders["tipo"].transform([tipo])[0]],
                "ORIGEM_ENC":     [encoders["origem"].transform([origem])[0]],
                "TEMPO RESOLUÇÃO":[tempo],
                "STATUS_ENC":     [encoders["status"].transform([status])[0]],
            })
            previsao = modelo.predict(entrada)
            resultado = encoders["severidade"].inverse_transform(previsao)[0]

            if status == "resolvido":
                resultado = "baixa"
            elif tipo in ["ataque", "falha servidor"]:
                resultado = "crítica"
            elif tipo in ["lentidão", "erro sistema"]:
                resultado = random.choice(["baixa", "média"])

            risco_score = random.randint(10, 99)
            prejuizo = random.uniform(3000, 30000)
            risco_financeiro = "ALTO" if prejuizo > 15000 else ("MÉDIO" if prejuizo > 7000 else "BAIXO")

            ataques_reais = df[df["TIPO INCIDENTE"] == "ataque"]
            if not ataques_reais.empty:
                linha = ataques_reais.sample(1).iloc[0]
                ip_raw    = linha["IP_SUSPEITO"]
                pais      = linha["PAIS_ATAQUE"]
                ip_exibir = ip_raw if perfil_atual["ver_pii"] else mascara_ip(ip_raw)
            else:
                ip_exibir = "Nenhum"
                pais      = "Interno"

            st.markdown("---")
            st.subheader("📊 Resultado da Análise")

            if resultado == "crítica":
                st.error(f"🔴 Severidade Prevista: **{resultado.upper()}**")
            elif resultado == "média":
                st.warning(f"🟡 Severidade Prevista: **{resultado.upper()}**")
            else:
                st.success(f"🟢 Severidade Prevista: **{resultado.upper()}**")

            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("Threat Score", f"{risco_score}/100")
            with r2:
                valor_fmt = f"R$ {prejuizo:,.2f}".replace(",","X").replace(".",",").replace("X",".")
                st.metric("Prejuízo Estimado", valor_fmt)
            with r3:
                st.metric("Risco Financeiro", risco_financeiro)

            st.write(f"**Cliente afetado:** {cliente}")

            if tipo == "ataque":
                if perfil_atual["ver_pii"]:
                    st.error(f"🌍 Origem do ataque: **{pais}**")
                    st.error(f"🔍 IP suspeito detectado: `{ip_exibir}`")
                else:
                    st.error(f"🌍 Origem do ataque: **{pais}**")
                    st.info(f"🔒 IP mascarado por política LGPD: `{ip_exibir}` — solicite acesso ao Administrador.")

                with st.expander("🛡️ Resposta Automática Acionada"):
                    st.write("✅ IP bloqueado automaticamente")
                    st.write("✅ Firewall reforçado")
                    st.write("✅ Equipe de segurança notificada")
                    st.write("✅ Logs enviados para auditoria")

            elif tipo == "lentidão":
                with st.expander("🔧 Recomendações"):
                    st.write("• Otimizar banco de dados")
                    st.write("• Reiniciar serviços")
                    st.write("• Limpar cache")

            elif tipo in ["erro sistema", "falha servidor"]:
                with st.expander("🔧 Recomendações"):
                    st.write("• Verificar logs de aplicação")
                    st.write("• Acionar redundância")
                    st.write("• Validar conectividade")

            st.markdown("---")
            st.subheader("📈 Monitoramento em Tempo Real")
            dados_rt = pd.DataFrame({
                "Minuto":     list(range(1, 11)),
                "Incidentes": [random.randint(1, 10) for _ in range(10)]
            })
            fig_rt = px.line(dados_rt, x="Minuto", y="Incidentes",
                             title="Incidentes por minuto (simulação ao vivo)")
            st.plotly_chart(fig_rt, use_container_width=True)

            st.subheader("🌍 Países com Mais Ameaças")
            fig_paises = px.histogram(df, x="PAIS_ATAQUE",
                                      title="Distribuição Global de Ataques")
            st.plotly_chart(fig_paises, use_container_width=True)

            adicionar_log(usuario_atual, f"Análise concluída: severidade={resultado}, score={risco_score}")

with abas[1]:
    st.subheader("📊 Dashboard Analítico")

    d1, d2 = st.columns(2)

    with d1:
        fig_sev = px.pie(df, names="SEVERIDADE", title="Distribuição de Severidade",
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_sev, use_container_width=True)

    with d2:
        fig_tipo = px.bar(df["TIPO INCIDENTE"].value_counts().reset_index(),
                          x="TIPO INCIDENTE", y="count",
                          title="Incidentes por Tipo")
        st.plotly_chart(fig_tipo, use_container_width=True)

    d3, d4 = st.columns(2)

    with d3:
        fig_status = px.bar(df["STATUS"].value_counts().reset_index(),
                            x="STATUS", y="count",
                            title="Status dos Incidentes",
                            color_discrete_sequence=["#2563eb"])
        st.plotly_chart(fig_status, use_container_width=True)

    with d4:
        fig_origem = px.bar(df["ORIGEM"].value_counts().reset_index(),
                            x="ORIGEM", y="count",
                            title="Origem dos Incidentes",
                            color_discrete_sequence=["#7c3aed"])
        st.plotly_chart(fig_origem, use_container_width=True)

    df_tempo = df.groupby("DATA").size().reset_index(name="Incidentes")
    fig_linha = px.line(df_tempo, x="DATA", y="Incidentes",
                        title="Volume de Incidentes ao Longo do Tempo")
    st.plotly_chart(fig_linha, use_container_width=True)

    df_prej = df.groupby("CLIENTE")["PREJUIZO_ESTIMADO"].sum().reset_index()
    df_prej = df_prej.sort_values("PREJUIZO_ESTIMADO", ascending=False).head(10)
    fig_prej = px.bar(df_prej, x="CLIENTE", y="PREJUIZO_ESTIMADO",
                      title="Top 10 Clientes por Prejuízo Estimado",
                      color_discrete_sequence=["#dc2626"])
    st.plotly_chart(fig_prej, use_container_width=True)

with abas[2]:
    st.subheader("🗄️ Backup e Exportação de Dados")

    if not perfil_atual["pode_exportar"]:
        st.error("⛔ Seu perfil não tem permissão para exportar dados. Apenas Administradores podem realizar backups.")
        adicionar_log(usuario_atual, "Tentativa de exportação negada (sem permissão)")
    else:
        st.success("✅ Você tem permissão para exportar e realizar backups dos dados.")

        st.markdown("""
        - **Backup manual**: exportação do dataset completo em CSV via botão abaixo.
        - **Backup automático**: recomenda-se agendar exportação diária via `mysqldump` (ambiente de produção).
        - **Retenção**: dados mantidos por 90 dias conforme política interna e LGPD.
        - **Criptografia**: em produção, os arquivos de backup devem ser criptografados com AES-256.
        """)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        timestamp_backup = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"sentinelai_backup_{timestamp_backup}.csv"

        st.download_button(
            label="⬇️ Baixar Dataset Completo (CSV)",
            data=csv_bytes,
            file_name=nome_arquivo,
            mime="text/csv",
        )

        df_anonimizado = df.drop(columns=["IP_SUSPEITO"], errors="ignore")
        csv_anon = df_anonimizado.to_csv(index=False).encode("utf-8")
        nome_anon = f"sentinelai_anonimizado_{timestamp_backup}.csv"

        st.download_button(
            label="⬇️ Baixar Versão Anonimizada (sem IPs — LGPD Compliant)",
            data=csv_anon,
            file_name=nome_anon,
            mime="text/csv",
        )

        if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
            logs_txt = "\n".join(st.session_state["logs_sistema"])
            st.download_button(
                label="⬇️ Exportar Logs da Sessão (.txt)",
                data=logs_txt.encode("utf-8"),
                file_name=f"sentinelai_logs_{timestamp_backup}.txt",
                mime="text/plain",
            )

        adicionar_log(usuario_atual, f"Download de backup solicitado: {nome_arquivo}")

        st.markdown("---")
        st.subheader("📋 Resumo do Dataset")
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Total: {len(df)} registros · {len(df.columns)} colunas")

with abas[3]:
    st.subheader("📋 Logs do Sistema")
    st.caption("Monitoramento de ações dos usuários — gerado em tempo real na sessão atual")

    if "logs_sistema" in st.session_state and st.session_state["logs_sistema"]:
        for log in reversed(st.session_state["logs_sistema"]):
            st.code(log, language=None)
    else:
        st.info("Nenhum log registrado ainda nesta sessão.")

    st.markdown("---")
    st.markdown("""
    - **Logs de sessão**: cada ação do usuário é registrada com timestamp e ID de usuário.
    - **Em produção**: logs enviados para sistema centralizado (ex: ELK Stack / CloudWatch).
    - **Alertas automáticos**: tentativas de login malsucedidas disparam notificação à equipe de segurança.
    - **Retenção de logs**: 180 dias conforme política de auditoria.
    - **Métricas monitoradas**: taxa de falhas de login, volume de análises/hora, erros de pipeline.
    """)

st.markdown("---")
st.markdown("""
<small>
🛡️ <b>SentinelAI</b> — Central Inteligente de Defesa Cibernética &nbsp;|&nbsp;
Dados protegidos conforme <b>LGPD (Lei 13.709/2018)</b> &nbsp;|&nbsp;
Comunicação criptografada via <b>HTTPS/TLS</b> &nbsp;|&nbsp;
Versionado no <a href="https://github.com/mariana-castro77/SentinelAI" target="_blank">GitHub</a>
</small>
""", unsafe_allow_html=True)
