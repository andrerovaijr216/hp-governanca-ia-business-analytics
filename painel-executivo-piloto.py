import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# --- Mock Data Generation (replace with real data in production) ---
np.random.seed(42)
dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
regions = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
ufs = ["SP", "RJ", "MG", "BA", "RS", "PE", "PR", "SC", "GO", "DF"]
prod_lines = ["Cartucho", "Toner"]
channels = ["E-commerce", "Loja", "Suporte"]
orig_gen = ["Original", "Genérico"]
severities = ["Baixa", "Média", "Alta", "Crítica"]

n = 2000
df = pd.DataFrame({
    "Data": np.random.choice(dates, n),
    "Região": np.random.choice(regions, n),
    "UF": np.random.choice(ufs, n),
    "Linha de Produto": np.random.choice(prod_lines, n),
    "Canal": np.random.choice(channels, n),
    "Tipo": np.random.choice(orig_gen, n),
    "Severidade": np.random.choice(severities, n),
    "Precisão": np.random.uniform(0.7, 0.99, n),
    "Recall": np.random.uniform(0.6, 0.98, n),
    "FPR": np.random.uniform(0.01, 0.2, n),
    "FNR": np.random.uniform(0.01, 0.2, n),
    "Tickets": np.random.randint(1, 10, n),
    "Devoluções": np.random.randint(0, 5, n),
    "Override": np.random.choice([0, 1], n, p=[0.85, 0.15]),
    "Tempo Detecção (min)": np.random.uniform(1, 60, n),
    "Com Ação": np.random.choice([True, False], n, p=[0.6, 0.4]),
    "NPS": np.random.randint(0, 100, n),
    "Custo Suporte": np.random.uniform(10, 100, n),
    "Suspeita": np.random.choice([0, 1], n, p=[0.8, 0.2]),
})

# --- Sidebar Filters ---
st.sidebar.header("Filtros")
periodo = st.sidebar.date_input("Período", [df["Data"].min(), df["Data"].max()])
regiao = st.sidebar.multiselect("Região/UF", sorted(df["Região"].unique()), default=sorted(df["Região"].unique()))
uf = st.sidebar.multiselect("UF", sorted(df["UF"].unique()), default=sorted(df["UF"].unique()))
linha_produto = st.sidebar.multiselect("Linha de Produto", prod_lines, default=prod_lines)
canal = st.sidebar.multiselect("Canal", channels, default=channels)
tipo = st.sidebar.multiselect("Original x Genérico", orig_gen, default=orig_gen)
severidade = st.sidebar.multiselect("Severidade do Chamado", severities, default=severities)

# --- Filter Data ---
df_filt = df[
    (df["Data"] >= pd.to_datetime(periodo[0])) &
    (df["Data"] <= pd.to_datetime(periodo[1])) &
    (df["Região"].isin(regiao)) &
    (df["UF"].isin(uf)) &
    (df["Linha de Produto"].isin(linha_produto)) &
    (df["Canal"].isin(canal)) &
    (df["Tipo"].isin(tipo)) &
    (df["Severidade"].isin(severidade))
]

# --- Page Navigation ---
st.title("Painel Executivo do Piloto — Governança & Analytics")
page = st.sidebar.radio(
    "Navegação",
    [
        "Visão Geral",
        "Detecção & Operação",
        "Fairness & Governança",
        "Negócio & ROI",
        "Mapa Regional",
        "Downloads & Evidências"
    ]
)

# --- Helper Functions ---
def kpi_card(label, value, delta=None, help_text=None):
    col = st.columns(1)[0]
    col.metric(label, value, delta=delta, help=help_text)

def download_button(df, filetype):
    if filetype == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar CSV", csv, "dados.csv", "text/csv")
    elif filetype == "PNG":
        st.info("Clique com o botão direito nos gráficos para salvar como PNG.")
    elif filetype == "PDF":
        st.info("Use a opção de imprimir do navegador para exportar como PDF.")

def resumo_executivo(df):
    total_tickets = df["Tickets"].sum()
    total_devol = df["Devoluções"].sum()
    nps_medio = df["NPS"].mean()
    regioes_top = df["Região"].value_counts().idxmax()
    return (
        f"Resumo Executivo:\n"
        f"- Total de tickets: {total_tickets}\n"
        f"- Total de devoluções: {total_devol}\n"
        f"- NPS médio: {nps_medio:.1f}\n"
        f"- Região com mais ocorrências: {regioes_top}\n"
    )

# --- Visão Geral ---
if page == "Visão Geral":
    st.header("KPIs do Piloto")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Precisão", f"{df_filt['Precisão'].mean():.2%}")
    with col2:
        st.metric("Recall", f"{df_filt['Recall'].mean():.2%}")
    with col3:
        st.metric("FPR", f"{df_filt['FPR'].mean():.2%}")
    with col4:
        st.metric("FNR", f"{df_filt['FNR'].mean():.2%}")
    with col5:
        st.metric("Tickets", int(df_filt["Tickets"].sum()))
    with col6:
        st.metric("Devoluções", int(df_filt["Devoluções"].sum()))

    st.subheader("Metas vs. Realizado")
    metas = {"Precisão": 0.90, "Recall": 0.85, "FPR": 0.05, "FNR": 0.05}
    kpi_real = {
        "Precisão": df_filt["Precisão"].mean(),
        "Recall": df_filt["Recall"].mean(),
        "FPR": df_filt["FPR"].mean(),
        "FNR": df_filt["FNR"].mean(),
    }
    meta_df = pd.DataFrame({
        "KPI": list(metas.keys()),
        "Meta": list(metas.values()),
        "Realizado": [kpi_real[k] for k in metas]
    })
    st.bar_chart(meta_df.set_index("KPI"))

    st.subheader("Tendência Temporal")
    df_time = df_filt.groupby(df_filt["Data"].dt.to_period("M")).agg({
        "Tickets": "sum",
        "Devoluções": "sum",
        "Precisão": "mean",
        "Recall": "mean"
    }).reset_index()
    df_time["Data"] = df_time["Data"].astype(str)
    fig = px.line(df_time, x="Data", y=["Tickets", "Devoluções"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Detecção & Operação ---
elif page == "Detecção & Operação":
    st.header("Matriz de Confusão")
    # Simulação de matriz de confusão
    from sklearn.metrics import confusion_matrix
    y_true = df_filt["Com Ação"]
    y_pred = df_filt["Suspeita"] > 0
    cm = confusion_matrix(y_true, y_pred)
    cm_df = pd.DataFrame(cm, index=["Sem Ação", "Com Ação"], columns=["Pred: Sem", "Pred: Com"])
    st.dataframe(cm_df)

    st.subheader("Tempo Médio de Detecção")
    st.metric("Tempo Médio (min)", f"{df_filt['Tempo Detecção (min)'].mean():.1f}")

    st.subheader("Fila de Revisão Humana")
    fila = df_filt[df_filt["Override"] == 1]
    st.write(f"Chamados em revisão: {len(fila)}")
    st.dataframe(fila[["Data", "Região", "UF", "Linha de Produto", "Canal", "Severidade"]].head(10))

    st.subheader("Taxa de Override")
    taxa_override = fila.shape[0] / max(1, df_filt.shape[0])
    st.metric("Taxa de Override", f"{taxa_override:.2%}")

# --- Fairness & Governança ---
elif page == "Fairness & Governança":
    st.header("Desempenho por Corte")
    corte = st.selectbox("Corte", ["Região", "Canal"])
    corte_df = df_filt.groupby(corte).agg({
        "Precisão": "mean",
        "Recall": "mean",
        "FPR": "mean",
        "FNR": "mean"
    }).reset_index()
    st.dataframe(corte_df)

    st.subheader("Diferenças de Taxas")
    st.bar_chart(corte_df.set_index(corte)[["FPR", "FNR"]])

    st.subheader("Sinal de Deriva")
    # Simulação: diferença de precisão entre períodos
    df_filt["Mês"] = df_filt["Data"].dt.to_period("M")
    drift = df_filt.groupby("Mês")["Precisão"].mean().diff().fillna(0)
    st.line_chart(drift)

    st.markdown("### Model Card")
    st.info(
        "**Objetivo:** Detectar e mitigar falsificações em suprimentos.\n"
        "**Dados usados:** Chamados, devoluções, NPS, logs de suporte.\n"
        "**Limites de uso:** Não substitui revisão humana em casos críticos."
    )

    st.markdown("### LGPD mini")
    st.info(
        "**Base legal:** Execução de contrato e legítimo interesse.\n"
        "**Minimização:** Apenas dados essenciais coletados.\n"
        "**Retenção:** Dados mantidos por 12 meses após o fim do piloto."
    )

# --- Negócio & ROI ---
elif page == "Negócio & ROI":
    st.header("Comparativo Com Ação vs. Sem Ação")
    comp = df_filt.groupby("Com Ação").agg({
        "Tickets": "sum",
        "Devoluções": "sum",
        "NPS": "mean",
        "Custo Suporte": "sum"
    }).rename(index={True: "Com Ação", False: "Sem Ação"})
    st.dataframe(comp)

    st.subheader("Estimativa de ROI/Payback")
    custo_acao = comp.loc["Com Ação", "Custo Suporte"]
    custo_sem = comp.loc["Sem Ação", "Custo Suporte"]
    devol_acao = comp.loc["Com Ação", "Devoluções"]
    devol_sem = comp.loc["Sem Ação", "Devoluções"]
    economia = (devol_sem - devol_acao) * 50  # suposição: R$50 por devolução evitada
    roi = (economia - (custo_acao - custo_sem)) / max(1, (custo_acao - custo_sem))
    st.metric("ROI Estimado", f"{roi:.1%}")
    st.metric("Payback (meses)", f"{np.random.uniform(2, 6):.1f}")

    st.subheader("Recomendação Go/No-Go")
    if roi > 0.1:
        st.success("Recomendação: Go (seguir com o modelo)")
    else:
        st.warning("Recomendação: No-Go (rever estratégia)")

# --- Mapa Regional ---
elif page == "Mapa Regional":
    st.header("Incidência Regional de Suspeitas")
    mapa_df = df_filt.groupby(["UF", "Região"]).agg({"Suspeita": "sum"}).reset_index()
    fig = px.density_mapbox(
        mapa_df, lat=[-23.5 + np.random.uniform(-5, 5) for _ in mapa_df["UF"]],
        lon=[-46.6 + np.random.uniform(-5, 5) for _ in mapa_df["UF"]],
        z="Suspeita", hover_name="UF", hover_data=["Região"],
        radius=20, center=dict(lat=-15, lon=-47), zoom=3,
        mapbox_style="carto-positron"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Hotspots de Falsificação")
    st.dataframe(mapa_df.sort_values("Suspeita", ascending=False).head(10))

# --- Downloads & Evidências ---
elif page == "Downloads & Evidências":
    st.header("Exportar Dados e Gráficos")
    download_button(df_filt, "CSV")
    download_button(df_filt, "PNG")
    download_button(df_filt, "PDF")

    st.subheader("Resumo Executivo")
    st.text(resumo_executivo(df_filt))

    st.subheader("Anotações/Insights")
    insight = st.text_area(
        "Destaque achados (ex: 'Nordeste 3× mais ocorrências que Sul')",
        value="Nordeste apresenta 3× mais ocorrências que Sul."
    )
    st.write("Insight salvo:", insight)
