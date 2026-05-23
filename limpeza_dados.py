import pandas as pd
import random

df = pd.read_csv("dataset_incidentes_ti.csv")

df = pd.concat([df] * 4, ignore_index=True)

df = df.sample(frac=1).reset_index(drop=True)

df.columns = df.columns.str.strip()

print(df.head())

print(df.isnull().sum())

df = df.dropna()

df["DATA"] = pd.to_datetime(df["DATA"], dayfirst=True)

df["TIPO INCIDENTE"] = df["TIPO INCIDENTE"].astype(str)
df["SEVERIDADE"] = df["SEVERIDADE"].astype(str)
df["ORIGEM"] = df["ORIGEM"].astype(str)
df["STATUS"] = df["STATUS"].astype(str)

print(df.dtypes)

paises = [
    "Brasil",
    "Rússia",
    "China",
    "Estados Unidos",
    "Alemanha",
    "Coreia do Norte",
    "Canadá"
]

clientes = [
    "Nubank",
    "Mercado Livre",
    "Magazine Luiza",
    "Vivo",
    "Santander",
    "iFood",
    "XP Investimentos"
]

df["PAIS_ATAQUE"] = [
    random.choice(paises)
    if tipo == "ataque"
    else "Interno"
    for tipo in df["TIPO INCIDENTE"]
]

df["PREJUIZO_ESTIMADO"] = [
    random.randint(500, 2000)
    if sev == "baixa"
    else random.randint(3000, 7000)
    if sev == "média"
    else random.randint(10000, 30000)
    for sev in df["SEVERIDADE"]
]

df["RECEITA_CLIENTE"] = [
    random.randint(20000, 100000)
    for _ in range(len(df))
]

df["CLIENTE"] = [
    random.choice(clientes)
    for _ in range(len(df))
]

df["NIVEL_AMEACA"] = [
    "baixo"
    if sev == "baixa"
    else "médio"
    if sev == "média"
    else "crítico"
    for sev in df["SEVERIDADE"]
]

df["LUCRO_EMPRESA"] = (
    df["RECEITA_CLIENTE"] - df["PREJUIZO_ESTIMADO"]
)

df["CRESCIMENTO_EMPRESA"] = [
    random.randint(5, 35)
    for _ in range(len(df))
]

df["RISCO_FINANCEIRO"] = [
    "alto"
    if prejuizo > 15000
    else "médio"
    if prejuizo > 5000
    else "baixo"
    for prejuizo in df["PREJUIZO_ESTIMADO"]
]

df["IP_SUSPEITO"] = [
    f"{random.randint(10,255)}.{random.randint(10,255)}.{random.randint(10,255)}.{random.randint(10,255)}"
    if tipo == "ataque"
    else "Nenhum"
    for tipo in df["TIPO INCIDENTE"]
]

df["BLOQUEADO_AUTOMATICAMENTE"] = [
    "Sim"
    if tipo == "ataque"
    else "Não"
    for tipo in df["TIPO INCIDENTE"]
]

df["TEMPO_INATIVIDADE"] = [
    random.randint(1, 10)
    if sev == "baixa"
    else random.randint(10, 40)
    if sev == "média"
    else random.randint(40, 120)
    for sev in df["SEVERIDADE"]
]

df["SATISFACAO_CLIENTE"] = [
    random.randint(70, 100)
    if status == "resolvido"
    else random.randint(20, 60)
    for status in df["STATUS"]
]

df["CUSTO_OPERACIONAL"] = [
    random.randint(1000, 5000)
    for _ in range(len(df))
]

df["ATAQUE_REAL"] = [
    "Sim"
    if tipo == "ataque"
    else "Não"
    for tipo in df["TIPO INCIDENTE"]
]

df["ID"] = range(1, len(df) + 1)

df.to_csv("dataset_final.csv", index=False)

print("\nDataset final criado com sucesso.")
print(df.head())