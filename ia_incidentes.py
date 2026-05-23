import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

df = pd.read_csv("dataset_final.csv")

encoder = LabelEncoder()

df["TIPO INCIDENTE"] = encoder.fit_transform(df["TIPO INCIDENTE"])
df["ORIGEM"] = encoder.fit_transform(df["ORIGEM"])
df["STATUS"] = encoder.fit_transform(df["STATUS"])
df["SEVERIDADE"] = encoder.fit_transform(df["SEVERIDADE"])

X = df[["TIPO INCIDENTE", "ORIGEM", "TEMPO RESOLUÇÃO", "STATUS"]]

y = df["SEVERIDADE"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

modelo = DecisionTreeClassifier()

modelo.fit(X_train, y_train)

previsoes = modelo.predict(X_test)

acuracia = accuracy_score(y_test, previsoes)

print(f"Acurácia do modelo: {acuracia:.2f}")