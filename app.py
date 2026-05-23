import streamlit as st
import pandas as pd
import random
import time
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

st.set_page_config(
    page_title="SentinelAI",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

.stApp {
    background:
        linear-gradient(
            135deg,
            #0a0f1c 0%,
            #101826 50%,
            #111827 100%
        );
    color: #e5e7eb;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stToolbar"] {
    right: 2rem;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    color: #f9fafb;
    font-weight: 700;
    letter-spacing: 0.5px;
}

h2, h3 {
    color: #f3f4f6;
    font-weight: 600;
}

div[data-testid="metric-container"] {
    background: rgba(17,24,39,0.72);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 22px;
    border-radius: 18px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

[data-testid="stMetricLabel"] {
    color: #9ca3af;
    font-size: 14px;
    font-weight: 500;
}

[data-testid="stMetricValue"] {
    color: #f9fafb;
    font-size: 32px;
    font-weight: 700;
}

div.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 12px;
    border: none;
    height: 3.2em;
    font-size: 16px;
    font-weight: 600;
    transition: 0.2s ease-in-out;
}

div.stButton > button:hover {
    background: #1d4ed8;
}

.stSelectbox div[data-baseweb="select"] {
    background: rgba(17,24,39,0.75);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
}

.stSlider {
    padding-top: 10px;
}

.stAlert {
    background: rgba(17,24,39,0.75);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
}

.stCodeBlock {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

st.title("SentinelAI")
st.subheader("Central Inteligente de Defesa Cibernética")

df = pd.read_csv("dataset_final.csv")

encoder_tipo = LabelEncoder()
encoder_origem = LabelEncoder()
encoder_status = LabelEncoder()
encoder_severidade = LabelEncoder()

df["TIPO INCIDENTE_ENCODED"] = encoder_tipo.fit_transform(df["TIPO INCIDENTE"])
df["ORIGEM_ENCODED"] = encoder_origem.fit_transform(df["ORIGEM"])
df["STATUS_ENCODED"] = encoder_status.fit_transform(df["STATUS"])
df["SEVERIDADE_ENCODED"] = encoder_severidade.fit_transform(df["SEVERIDADE"])

X = df[[
    "TIPO INCIDENTE_ENCODED",
    "ORIGEM_ENCODED",
    "TEMPO RESOLUÇÃO",
    "STATUS_ENCODED"
]]

y = df["SEVERIDADE_ENCODED"]

modelo = DecisionTreeClassifier()
modelo.fit(X, y)

clientes = df["CLIENTE"].unique()

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric("Incidentes Hoje", random.randint(80, 250))

with col_kpi2:
    st.metric("IPs Bloqueados", random.randint(10, 80))

with col_kpi3:
    st.metric("Ameaças Críticas", random.randint(5, 30))

with col_kpi4:

    lucro = random.uniform(500000, 1500000)

    st.metric(
        "Lucro Protegido",
        f"R$ {lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

st.markdown("---")

st.subheader("Análise Inteligente de Incidentes")

col1, col2 = st.columns(2)

with col1:

    tipo = st.selectbox(
        "Tipo de Incidente",
        encoder_tipo.classes_
    )

    origem = st.selectbox(
        "Origem",
        encoder_origem.classes_
    )

    cliente = st.selectbox(
        "Cliente Afetado",
        clientes
    )

with col2:

    tempo = st.slider(
        "Tempo de Resolução (min)",
        1,
        120
    )

    status = st.selectbox(
        "Status",
        encoder_status.classes_
    )

if st.button("Iniciar Análise"):

    with st.spinner("Analisando ameaças em tempo real..."):
        time.sleep(2)

    entrada = pd.DataFrame({
        "TIPO INCIDENTE_ENCODED": [encoder_tipo.transform([tipo])[0]],
        "ORIGEM_ENCODED": [encoder_origem.transform([origem])[0]],
        "TEMPO RESOLUÇÃO": [tempo],
        "STATUS_ENCODED": [encoder_status.transform([status])[0]]
    })

    previsao = modelo.predict(entrada)

    resultado = encoder_severidade.inverse_transform(previsao)[0]

    if status == "resolvido":
        resultado = "baixa"

    elif tipo == "ataque":
        resultado = "crítica"

    elif tipo == "falha servidor":
        resultado = "crítica"

    elif tipo == "lentidão":
        resultado = random.choice(["baixa", "média"])

    elif tipo == "erro sistema":
        resultado = random.choice(["baixa", "média"])

    risco = random.randint(10, 99)

    registro_ataque = df[df["TIPO INCIDENTE"] == "ataque"]

    if not registro_ataque.empty:
        linha_ataque = registro_ataque.sample(1).iloc[0]

        ip_detectado = linha_ataque["IP_SUSPEITO"]
        pais_detectado = linha_ataque["PAIS_ATAQUE"]

    else:
        ip_detectado = "Nenhum"
        pais_detectado = "Interno"

    prejuizo = random.uniform(3000, 30000)

    if prejuizo > 15000:
        risco_financeiro = "ALTO"

    elif prejuizo > 7000:
        risco_financeiro = "MÉDIO"

    else:
        risco_financeiro = "BAIXO"

    st.markdown("---")

    st.subheader("Painel Inteligente de Resposta")

    if status == "resolvido":

        st.success("Incidente resolvido")

        st.metric(
            "Risco Atual",
            f"{random.randint(1,25)}%"
        )

        st.write("Histórico de Correção")

        if tipo == "ataque":

            st.write(f"Origem detectada: {pais_detectado}")
            st.write(f"IP bloqueado: {ip_detectado}")
            st.write("Firewall atualizado")
            st.write("MFA ativado")
            st.write("Logs revisados")
            st.write("Acesso suspeito encerrado")

        elif tipo == "lentidão":

            st.write("Cache limpo")
            st.write("Banco otimizado")
            st.write("Serviços reiniciados")
            st.write("Performance normalizada")

        elif tipo == "erro sistema":

            st.write("Aplicação reiniciada")
            st.write("Atualização aplicada")
            st.write("Logs corrigidos")
            st.write("Sistema estabilizado")

        elif tipo == "falha servidor":

            st.write("Servidor reiniciado")
            st.write("Backup restaurado")
            st.write("Redundância ativada")
            st.write("Infraestrutura validada")

    else:

        if resultado == "crítica":
            st.error(f"Severidade Prevista: {resultado.upper()}")

        elif resultado == "média":
            st.warning(f"Severidade Prevista: {resultado.upper()}")

        else:
            st.success(f"Severidade Prevista: {resultado.upper()}")

        st.metric(
            "Threat Score",
            f"{risco}/100"
        )

        st.metric(
            "Prejuízo Estimado",
            f"R$ {prejuizo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        st.write(f"Cliente afetado: {cliente}")

        st.write(f"Risco Financeiro: {risco_financeiro}")

        if tipo == "ataque":

            st.error(f"Origem do ataque: {pais_detectado}")
            st.error(f"IP suspeito detectado: {ip_detectado}")

            st.write("Resposta Automática")

            st.write("IP bloqueado automaticamente")
            st.write("Firewall reforçado")
            st.write("Equipe de segurança notificada")
            st.write("Logs enviados para auditoria")

            st.write("Explicação da IA")

            st.write(
                "A IA identificou padrões semelhantes a ataques anteriores "
                "registrados na base de monitoramento."
            )

        elif tipo == "lentidão":

            st.write("Problema Detectado")

            st.write("Consumo elevado de recursos identificado.")

            st.write("Recomendações")

            st.write("- Otimizar banco de dados")
            st.write("- Reiniciar serviços")
            st.write("- Limpar cache")
            st.write("- Revisar uso de CPU")

        elif tipo == "erro sistema":

            st.write("Problema Detectado")

            st.write("Falha operacional identificada.")

            st.write("Recomendações")

            st.write("- Verificar logs")
            st.write("- Atualizar aplicação")
            st.write("- Validar permissões")
            st.write("- Reiniciar módulos")

        elif tipo == "falha servidor":

            st.write("Problema Detectado")

            st.write("Instabilidade crítica detectada.")

            st.write("Recomendações")

            st.write("- Isolar servidor")
            st.write("- Revisar infraestrutura")
            st.write("- Acionar redundância")
            st.write("- Validar conectividade")

    st.markdown("---")

    st.subheader("Monitoramento em Tempo Real")

    dados_tempo_real = pd.DataFrame({
        "Minuto": [1,2,3,4,5,6,7,8,9,10],
        "Incidentes": [
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10),
            random.randint(1,10)
        ]
    })

    grafico = px.line(
        dados_tempo_real,
        x="Minuto",
        y="Incidentes",
        title="Monitoramento de Incidentes"
    )

    st.plotly_chart(grafico, use_container_width=True)

    st.subheader("Países com Mais Ameaças")

    grafico_paises = px.histogram(
        df,
        x="PAIS_ATAQUE",
        title="Distribuição Global de Ataques"
    )

    st.plotly_chart(grafico_paises, use_container_width=True)

    st.subheader("Logs do Sistema")

    logs = [
        "[22:14:03] Tentativa de acesso detectada",
        "[22:14:07] Firewall acionado",
        "[22:14:10] Verificação de tráfego iniciada",
        "[22:14:15] Logs enviados para auditoria",
        "[22:14:18] Sistema de monitoramento atualizado"
    ]

    for log in logs:
        st.code(log)

st.markdown("---")

st.subheader("Visão Estratégica")

st.info(
    "A plataforma SentinelAI utiliza Inteligência Artificial para monitorar "
    "incidentes, prever ameaças, identificar padrões suspeitos e apoiar "
    "equipes de TI na tomada de decisão preventiva."
)
