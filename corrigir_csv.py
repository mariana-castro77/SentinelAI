import pandas as pd

try:
    df = pd.read_csv("dataset_final.csv", encoding="latin1")
except:
    df = pd.read_csv("dataset_final.csv", encoding="utf-8", engine="python")

def corrigir_texto(texto):
    try:
        return texto.encode("latin1").decode("utf-8")
    except:
        return texto

df.columns = [corrigir_texto(col) for col in df.columns]

for coluna in df.select_dtypes(include="object").columns:
    df[coluna] = df[coluna].astype(str).apply(corrigir_texto)

df.to_csv(
    "dataset_mysql.csv",
    index=False,
    encoding="utf-8-sig"
)

print("CSV corrigido com sucesso!")