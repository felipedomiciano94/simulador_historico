
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from unidecode import unidecode
import io

st.set_page_config(page_title="Simulador Histórico - DataLake", layout="wide")
st.image("logo.png", width=150)
st.title("📊 Análise Histórica de Demandas - DataLake")

# Upload da base histórica original
arquivo = st.file_uploader("📂 Faça o upload da base simulador_datalake.xlsx", type="xlsx")
if not arquivo:
    st.warning("⚠️ Aguarde o upload do arquivo para continuar.")
    st.stop()

# Leitura da base com colunas originais
df_raw = pd.read_excel(arquivo)
df_raw.columns = df_raw.columns.str.upper().str.strip()

# Mapeamento interno para nomes padrão
df_demandas = pd.DataFrame()
df_demandas["DEMANDA KMM"] = df_raw["SOLICITACAO_CARGA_ID"]
df_demandas["DATA"] = pd.to_datetime(df_raw["DATA_CARGA"])
df_demandas["MODALIDADE_REALIZADA"] = df_raw["MODALIDADE"]
df_demandas["ORIGEM"] = df_raw["ORIGEM E UF"]
df_demandas["DESTINO"] = df_raw["DESTINO E UF"]
df_demandas["CLIENTE"] = ""

# Leitura da base de custos
try:
    df_custos = pd.read_csv("custos_consolidados.csv", sep=",")
    df_custos.columns = df_custos.columns.str.upper().str.strip()
except FileNotFoundError:
    st.error("❌ Arquivo 'custos_consolidados.csv' não encontrado.")
    st.stop()

required = {"ORIGEM", "DESTINO", "CUSTO_FROTA", "CUSTO_AGREGADO"}
if not required.issubset(df_custos.columns):
    st.error(f"❌ Colunas faltando em custos_consolidados.csv: {required - set(df_custos.columns)}")
    st.stop()

# Normalização
df_custos["ORIGEM_NORM"] = df_custos["ORIGEM"].apply(lambda x: unidecode(str(x).upper().strip()))
df_custos["DESTINO_NORM"] = df_custos["DESTINO"].apply(lambda x: unidecode(str(x).upper().strip()))
df_demandas["ORIGEM_NORM"] = df_demandas["ORIGEM"].apply(lambda x: unidecode(str(x).upper().strip()))
df_demandas["DESTINO_NORM"] = df_demandas["DESTINO"].apply(lambda x: unidecode(str(x).upper().strip()))

# Filtro por data
datas_disponiveis = df_demandas["DATA"].dropna()
data_inicial, data_final = st.date_input(
    "🗓️ Período para análise",
    [datas_disponiveis.min(), datas_disponiveis.max()]
)

df_demandas = df_demandas[
    (df_demandas["DATA"] >= pd.to_datetime(data_inicial)) &
    (df_demandas["DATA"] <= pd.to_datetime(data_final))
]

# Merge com custos
df_merge = pd.merge(df_demandas, df_custos, on=["ORIGEM_NORM", "DESTINO_NORM"], how="left")

# Garantir que ORIGEM e DESTINO existam
if "ORIGEM" not in df_merge.columns and "ORIGEM_x" in df_merge.columns:
    df_merge["ORIGEM"] = df_merge["ORIGEM_x"]
if "DESTINO" not in df_merge.columns and "DESTINO_x" in df_merge.columns:
    df_merge["DESTINO"] = df_merge["DESTINO_x"]

# Melhor custo
df_merge["MELHOR CUSTO"] = df_merge.apply(
    lambda r: "Frota Própria" if r["CUSTO_FROTA"] < r["CUSTO_AGREGADO"] else "Agregado", axis=1
)

# Comparação com modalidade realizada
df_merge["ERRO DE ALOCAÇÃO"] = df_merge.apply(
    lambda r: r["MODALIDADE_REALIZADA"].strip().upper() != r["MELHOR CUSTO"].strip().upper(), axis=1
)

df_merge["SAVING POTENCIAL"] = df_merge.apply(
    lambda r: r["CUSTO_AGREGADO"] - r["CUSTO_FROTA"] if r["ERRO DE ALOCAÇÃO"] and r["MELHOR CUSTO"] == "Frota Própria"
    else (r["CUSTO_FROTA"] - r["CUSTO_AGREGADO"] if r["MELHOR CUSTO"] == "Agregado" and r["ERRO DE ALOCAÇÃO"]
    else 0),
    axis=1
)

# Abas
aba = st.sidebar.radio("Escolha a aba:", ["📋 Resultados Detalhados", "📈 Resumo Analítico"])

if aba == "📋 Resultados Detalhados":
    mostrar = [
        "DEMANDA KMM", "DATA", "CLIENTE", "ORIGEM", "DESTINO",
        "CUSTO_FROTA", "CUSTO_AGREGADO", "MODALIDADE_REALIZADA", "MELHOR CUSTO",
        "ERRO DE ALOCAÇÃO", "SAVING POTENCIAL"
    ]
    colunas_existentes = [col for col in mostrar if col in df_merge.columns]
    st.dataframe(df_merge[colunas_existentes], use_container_width=True)

    # Exportar resultado
    buffer = io.BytesIO()
    df_merge[colunas_existentes].to_excel(buffer, index=False)
    st.download_button("⬇️ Baixar análise histórica", data=buffer.getvalue(), file_name="resultado_datalake.xlsx")

elif aba == "📈 Resumo Analítico":
    st.subheader("🔢 Indicadores Gerais")

    total_viagens = len(df_merge)
    total_agregado = (df_merge["MODALIDADE_REALIZADA"].str.upper() == "AGREGADO").sum()
    total_frota = (df_merge["MODALIDADE_REALIZADA"].str.upper() == "FROTA").sum()
    total_terceiro = (df_merge["MODALIDADE_REALIZADA"].str.upper() == "TERCEIRO").sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🚚 Total de Viagens", f"{total_viagens}")
    col2.metric("🛻 Agregados", f"{total_agregado}")
    col3.metric("🏭 Frota Própria", f"{total_frota}")
    col4.metric("🔗 Terceiros", f"{total_terceiro}")

    st.subheader("💰 Custos Totais")
    custo_realizado = df_merge[["MODALIDADE_REALIZADA", "CUSTO_AGREGADO", "CUSTO_FROTA"]].copy()
    custo_realizado["CUSTO_REALIZADO"] = custo_realizado.apply(
        lambda r: r["CUSTO_AGREGADO"] if r["MODALIDADE_REALIZADA"].strip().upper() == "AGREGADO"
        else r["CUSTO_FROTA"] if r["MODALIDADE_REALIZADA"].strip().upper() == "FROTA"
        else 0,
        axis=1
    )

    st.metric("💳 Custo Total Realizado", f"R$ {custo_realizado['CUSTO_REALIZADO'].sum():,.2f}")
    st.metric("📈 Custo Total Otimizado", f"R$ {df_merge[['CUSTO_FROTA', 'CUSTO_AGREGADO']].apply(lambda r: min(r), axis=1).sum():,.2f}")

    st.subheader("📆 Análise por Mês/Ano e Modalidade")
    df_merge["ANO"] = df_merge["DATA"].dt.year
    df_merge["MES"] = df_merge["DATA"].dt.month
    resumo = df_merge.groupby(["ANO", "MES", "MODALIDADE_REALIZADA"]).agg({
        "DEMANDA KMM": "count",
        "CUSTO_FROTA": "sum",
        "CUSTO_AGREGADO": "sum",
        "SAVING POTENCIAL": "sum"
    }).rename(columns={"DEMANDA KMM": "QTD_VIAGENS"}).reset_index()

    st.dataframe(resumo, use_container_width=True)


    st.subheader("📉 Gráfico de Saving Potencial por Modalidade")

    # Agrupamento por mês/ano e modalidade
    df_merge["ANO_MES"] = df_merge["DATA"].dt.to_period("M").astype(str)
    saving_mensal = df_merge.groupby(["ANO_MES", "MODALIDADE_REALIZADA"])["SAVING POTENCIAL"].sum().reset_index()

    # Pivotar para formato gráfico
    pivot = saving_mensal.pivot(index="ANO_MES", columns="MODALIDADE_REALIZADA", values="SAVING POTENCIAL").fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker='o', label=col)
        for i, val in enumerate(pivot[col]):
            ax.text(i, val, f"R$ {val:,.0f}", ha='center', va='bottom', fontsize=8)

    ax.set_title("Saving Potencial por Modalidade ao Longo do Tempo")
    ax.set_xlabel("Mês/Ano")
    ax.set_ylabel("Saving Potencial (R$)")
    ax.legend(title="Modalidade")
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
