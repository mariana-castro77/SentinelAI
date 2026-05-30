# 🛡️ SentinelAI — Documentação Técnica

Central Inteligente de Monitoramento de Segurança Cibernética

---

## 1. Problema de Negócio e Arquitetura

O SentinelAI resolve o problema de **falta de visibilidade e resposta lenta a incidentes de segurança cibernética** em ambientes corporativos.

### Decisão de Arquitetura: OLTP × OLAP

| Camada | Função | Tecnologia | Justificativa |
|---|---|---|---|
| **OLTP** | Registro de incidentes em tempo de execução | MySQL (ACID) | Exige integridade referencial e consistência forte nas escritas |
| **OLAP** | Análise histórica e dashboards | Power BI + Streamlit | Consultas analíticas agregadas, não afetam a camada transacional |
| **Data Lake** | Armazenamento bruto do CSV | Arquivo CSV versionado | Dados não estruturados / semiestruturados antes do carregamento |

**Por que MySQL (relacional/SQL) e não NoSQL?**
- Os dados de incidentes têm **schema fixo e bem definido** (ID, data, tipo, severidade etc.).
- Exige **integridade referencial** entre incidentes e clientes.
- O Teorema CAP: optamos por **CP (Consistência + Tolerância a Partição)** — preferimos dados corretos a dados sempre disponíveis.
- Trade-off assumido: menor flexibilidade de schema em troca de garantias ACID.

---

## 2. Pipeline ETL — Ponta a Ponta

Arquitetura de camadas (simplificada do modelo Medallion):

```
[FONTE]           [STAGING]          [PROCESSAMENTO]        [CONSUMO]
CSV bruto    →   Leitura Pandas   →  Limpeza + Encoding  →  ML + Dashboard
dataset_final.csv   (bruto)         pandas / sklearn       Streamlit / Power BI
```

### Detalhamento das Camadas

**Staging (Bronze):**
- Leitura do CSV com `pandas.read_csv()`
- Dado bruto preservado para rastreabilidade

**Processamento (Prata):**
- Remoção de nulos nas colunas obrigatórias (`TIPO INCIDENTE`, `SEVERIDADE`, `ORIGEM`, `STATUS`)
- Padronização de datas para `datetime`
- Normalização de texto (strip + lowercase) para consistência
- Label Encoding das colunas categóricas para o modelo ML

**Consumo (Ouro):**
- Treinamento do modelo `DecisionTreeClassifier` (scikit-learn)
- DataFrame pronto para visualizações no Streamlit e Power BI

**Tipo de processamento:** **Batch** — os dados são carregados e transformados de uma vez, cacheados via `@st.cache_data`. Não há necessidade de streaming contínuo dado o volume (600 registros) e o contexto analítico.

**Reprodutibilidade:** Todo o código de pipeline está versionado no GitHub. O `random_state=42` no modelo garante reprodutibilidade dos resultados.

---

## 3. Processamento e Tecnologias

| Etapa | Ferramenta | Justificativa |
|---|---|---|
| Ingestão | Python + Pandas | Leve, suficiente para o volume atual (600 registros) |
| Transformação | Pandas | Operações vetorizadas eficientes para dataset pequeno/médio |
| ML | Scikit-learn (DecisionTree) | Simples, interpretável, sem necessidade de Spark neste volume |
| Visualização | Plotly + Streamlit | Dashboards interativos sem backend separado |
| BI Analítico | Power BI | Camada analítica separada da transacional |

**Por que não Spark?**
Com 600 registros, Spark seria overengineering. A escolha de Pandas é justificada pelo volume — Spark se justifica a partir de dezenas de milhões de linhas ou processamento distribuído.

---

## 4. Infraestrutura e Cloud

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Hospedagem do app | Streamlit Community Cloud | Gratuito, CI/CD integrado ao GitHub, HTTPS automático |
| Banco de dados | MySQL (local / cloud) | Relacional, ACID, suporte amplo |
| Versionamento | GitHub | Controle de versão, histórico de mudanças, colaboração |

**Escalabilidade:** Para crescimento de volume, a arquitetura suporta migração para:
- MySQL → Cloud SQL (GCP) ou RDS (AWS) para escalabilidade vertical
- Pandas → Spark/Databricks para processamento distribuído
- Streamlit Cloud → Kubernetes (GKE/EKS) para alta disponibilidade

**Trade-off assumido:** Streamlit Community Cloud não garante SLA de disponibilidade — aceito para fins acadêmicos e MVP.

---

## 5. Governança, Segurança e DataOps

### Controle de Acesso (RBAC)

| Perfil | Análise | Exportação | Ver IPs (PII) |
|---|---|---|---|
| Administrador | ✅ | ✅ | ✅ |
| Analista | ✅ | ❌ | ❌ (mascarado) |
| Viewer | ❌ | ❌ | ❌ |

### Proteção de Dados (LGPD)
- **IPs suspeitos** são dados pessoais identificáveis (PII) — mascarados para perfis sem permissão
- Exportação separada de versão **anonimizada** (sem coluna `IP_SUSPEITO`)
- Aviso de cookies exibido no primeiro acesso com opção de recusa
- Senhas armazenadas como **hash SHA-256** (em produção: bcrypt + salt)
- Comunicação via **HTTPS/TLS** (garantido pelo Streamlit Cloud)

### DataOps
- **Versionamento:** GitHub (histórico completo de commits)
- **CI/CD:** Deploy automático no Streamlit Cloud a cada push na branch `main`
- **Logs:** Cada ação do usuário registrada com timestamp e ID (visível na aba "Logs do Sistema")
- **Cache:** `@st.cache_data` garante que o pipeline ETL não reexecute desnecessariamente

### Qualidade de Dados
- Validação de nulos nas colunas obrigatórias (registros inválidos são descartados no staging)
- Padronização de encoding UTF-8
- Padronização de formato de datas

---

## 6. Como Executar Localmente

```bash
# Clonar o repositório
git clone https://github.com/mariana-castro77/SentinelAI.git
cd SentinelAI

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py
```

**Contas de acesso (demonstração):**
| Usuário | Senha | Perfil |
|---|---|---|
| admin | admin123 | Administrador |
| analista | analista123 | Analista de Segurança |
| viewer | viewer123 | Somente Visualização |

---

## 7. Estrutura do Repositório

```
SentinelAI/
├── app.py                  # Aplicação principal (Streamlit)
├── dataset_final.csv       # Dataset de incidentes (fonte de dados)
├── requirements.txt        # Dependências Python
└── README.md               # Documentação técnica
```

---

## 8. Referências

- Python Software Foundation — https://docs.python.org
- Streamlit Documentation — https://docs.streamlit.io
- Scikit-Learn Documentation — https://scikit-learn.org
- Pandas Documentation — https://pandas.pydata.org
- LGPD — Lei 13.709/2018 — https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- MySQL Documentation — https://dev.mysql.com/doc
- Power BI Documentation — https://learn.microsoft.com/pt-br/power-bi
