# HP – Detecção de Produtos Falsificados | Streamlit App

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import streamlit as st
# import joblib # Not used
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from io import BytesIO
# import traceback # For detailed traceback if needed

# --- CONFIGURAÇÕES INICIAIS ---
sns.set(style="whitegrid")
np.random.seed(42)
st.set_page_config(page_title="HP Produtos Falsificados", layout="wide", initial_sidebar_state="expanded")

# --- FUNÇÕES AUXILIARES ---
@st.cache_data
def gerar_dados():
    regioes = ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste', 'Norte']
    tipos = ['Original', 'Genérico']
    datas = pd.date_range(end=datetime.today(), periods=180, normalize=True).tolist()
    dados = []
    for data_val in datas:
        for regiao in regioes:
            for tipo in tipos:
                chamados = np.random.randint(50, 200) if tipo == 'Original' else np.random.randint(150, 300)
                devolucao = np.random.uniform(0.02, 0.05) if tipo == 'Original' else np.random.uniform(0.1, 0.25)
                nps = np.random.randint(50, 70) if tipo == 'Original' else np.random.randint(-20, 10)
                dados.append({
                    'Data': data_val, 'Região': regiao, 'Tipo': tipo,
                    'Chamados': chamados, 'Taxa_Devolucao': devolucao, 'NPS': nps
                })
    return pd.DataFrame(dados)

def connect_db(db_name="hp_falsificados.db"):
    return sqlite3.connect(db_name)

# --- CARREGAR DADOS E FILTROS NA SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/HP_logo_2012.svg/1200px-HP_logo_2012.svg.png", width=100) # Example HP Logo
st.sidebar.title("⚙️ Controles e Filtros")

# Carregar dados
df_inicial = gerar_dados() # Start with synthetic data
uploaded_file = st.sidebar.file_uploader("📤 Envie um arquivo Excel", type=[".xlsx"])
if uploaded_file:
    try:
        df_uploaded = pd.read_excel(uploaded_file)
        required_cols = ['Data', 'Região', 'Tipo', 'Chamados', 'Taxa_Devolucao', 'NPS']
        if all(col in df_uploaded.columns for col in required_cols):
            df_inicial = df_uploaded
            st.sidebar.success("Arquivo Excel carregado!")
        else:
            st.sidebar.error(f"Arquivo Excel deve conter: {', '.join(required_cols)}. Usando dados sintéticos.")
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar Excel: {e}. Usando dados sintéticos.")

df = df_inicial.copy() # Work with a copy

# Ensure 'Data' column is in datetime format
df_filtrado = pd.DataFrame() # Initialize to empty
if 'Data' in df.columns:
    try:
        df['Data'] = pd.to_datetime(df['Data'])
    except Exception as e:
        st.sidebar.error(f"Erro ao converter coluna 'Data': {e}. Verifique formato.")
        # df remains as is, subsequent ops might fail if 'Data' is not datetime
else:
    st.sidebar.error("Coluna 'Data' não encontrada. Verifique seus dados.")

# Filtros para o Dashboard (aplicados a 'df')
if not df.empty and 'Data' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Data']):
    default_regioes_dash = list(df['Região'].unique()) if 'Região' in df.columns else []
    regiao_sel_dash = st.sidebar.multiselect(
        "Região (Dashboard)",
        options=df['Região'].unique() if 'Região' in df.columns else [],
        default=default_regioes_dash
    )

    min_data_val_dash = df['Data'].min()
    max_data_val_dash = df['Data'].max()
    start_date_default_dash = min_data_val_dash.date() if pd.notna(min_data_val_dash) else datetime.today().date() - pd.Timedelta(days=30)
    end_date_default_dash = max_data_val_dash.date() if pd.notna(max_data_val_dash) else datetime.today().date()

    periodo_dates_dash = st.sidebar.date_input(
        "Período (Dashboard)",
        value=[start_date_default_dash, end_date_default_dash],
        min_value=start_date_default_dash if pd.notna(start_date_default_dash) else None,
        max_value=end_date_default_dash if pd.notna(end_date_default_dash) else None
    )

    if len(periodo_dates_dash) == 2:
        start_date_obj_dash, end_date_obj_dash = periodo_dates_dash
        start_timestamp_dash = pd.Timestamp(start_date_obj_dash)
        end_timestamp_dash = pd.Timestamp(end_date_obj_dash) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)

        conditions_dash = []
        if 'Região' in df.columns and regiao_sel_dash:
            conditions_dash.append(df['Região'].isin(regiao_sel_dash))
        if start_timestamp_dash and end_timestamp_dash:
            conditions_dash.append(df['Data'].between(start_timestamp_dash, end_timestamp_dash))

        if conditions_dash:
            final_condition_dash = conditions_dash[0]
            for cond in conditions_dash[1:]:
                final_condition_dash &= cond
            df_filtrado = df[final_condition_dash]
        else:
            df_filtrado = df.copy()
    else:
        st.sidebar.warning("Período (Dashboard) inválido.")
        df_filtrado = df.copy()
else:
    st.sidebar.warning("Dados não disponíveis ou coluna 'Data' inválida para filtros do dashboard.")


# --- LAYOUT PRINCIPAL ---
st.title("🛡️ HP – Detecção e Monitoramento de Produtos Falsificados")
st.markdown("---")

clf = None
X_train, X_test, y_train, y_test = None, None, None, None # Initialize for broader scope

if not df_filtrado.empty:
    st.header("📊 Painel de Monitoramento")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("📦 Total de Chamados", int(df_filtrado['Chamados'].sum()))
    with col2: st.metric("📈 Taxa Média de Devolução", f"{df_filtrado['Taxa_Devolucao'].mean()*100:.2f}%")
    with col3: st.metric("📣 NPS Médio", int(df_filtrado['NPS'].mean()))
    st.markdown("---")

    st.subheader("Comparativos por Região e Tipo")
    fig_list_for_pdf = [] # Use a different name to avoid confusion with any fig objects
    try:
        plot_cols = ['Região', 'Chamados', 'Taxa_Devolucao', 'NPS', 'Tipo']
        if all(col in df_filtrado.columns for col in plot_cols):
            # Create figure, plot, display, then append a *copy* or re-generate for PDF
            # For simplicity, we'll just append the objects and hope they are not altered before PDF gen
            # A safer way is to have functions that generate figures on demand.

            fig1_dash = plt.figure(figsize=(10, 4)); sns.barplot(data=df_filtrado, x='Região', y='Chamados', hue='Tipo', ci=None); plt.title("Chamados por Região e Tipo"); st.pyplot(fig1_dash); fig_list_for_pdf.append(fig1_dash); plt.close(fig1_dash)
            fig2_dash = plt.figure(figsize=(10, 4)); sns.barplot(data=df_filtrado, x='Região', y='Taxa_Devolucao', hue='Tipo', ci=None); plt.title("Taxa de Devolução"); st.pyplot(fig2_dash); fig_list_for_pdf.append(fig2_dash); plt.close(fig2_dash)
            fig3_dash = plt.figure(figsize=(10, 4)); sns.barplot(data=df_filtrado, x='Região', y='NPS', hue='Tipo', ci=None); plt.title("NPS por Região e Tipo"); st.pyplot(fig3_dash); fig_list_for_pdf.append(fig3_dash); plt.close(fig3_dash)
        else:
            st.warning(f"Colunas necessárias para gráficos ({', '.join(plot_cols)}) não encontradas.")
    except Exception as e_plot: st.error(f"Erro ao gerar gráficos: {e_plot}")
    st.markdown("---")

    if st.button("📄 Exportar Relatório em PDF"):
        if fig_list_for_pdf:
            buffer = BytesIO()
            with PdfPages(buffer) as pdf:
                # Regenerate figures for PDF to ensure they are not closed or altered
                # This requires abstracting figure generation into functions or carefully managing figure objects.
                # For now, assuming fig_list_for_pdf contains valid, non-closed figures (which is tricky with plt.close)
                # A simple fix is to re-create them if this export logic is complex.
                # For simplicity, let's assume the figures in fig_list_for_pdf can be saved.
                # However, since we used plt.close(), the fig_list_for_pdf figures are closed.
                # So we should ideally re-generate or remove plt.close() from above and close after PDF.
                # Let's remove plt.close() for now from the dashboard display and close after PDF export
                # (This is not ideal for Streamlit's memory if PDF is not exported, but simpler for this example)
                
                # To make PDF export work without re-generating, we'd have to NOT close figs above.
                # For robust PDF export if figures were closed:
                st.info("Recriando gráficos para o PDF...")
                temp_figs_for_pdf = []
                if all(col in df_filtrado.columns for col in plot_cols):
                    f1 = plt.figure(figsize=(10,4)); sns.barplot(data=df_filtrado, x='Região', y='Chamados', hue='Tipo', ci=None); plt.title("Chamados por Região e Tipo"); temp_figs_for_pdf.append(f1)
                    f2 = plt.figure(figsize=(10,4)); sns.barplot(data=df_filtrado, x='Região', y='Taxa_Devolucao', hue='Tipo', ci=None); plt.title("Taxa de Devolução"); temp_figs_for_pdf.append(f2)
                    f3 = plt.figure(figsize=(10,4)); sns.barplot(data=df_filtrado, x='Região', y='NPS', hue='Tipo', ci=None); plt.title("NPS por Região e Tipo"); temp_figs_for_pdf.append(f3)

                for fig_to_save in temp_figs_for_pdf:
                    pdf.savefig(fig_to_save)
                    plt.close(fig_to_save) # Close after saving to PDF

                if not df_filtrado.empty:
                    dfn = df_filtrado.describe().T.reset_index().round(2)
                    fig_table_pdf, ax_table_pdf = plt.subplots(figsize=(10, max(2, len(dfn)*0.5)))
                    ax_table_pdf.axis('tight'); ax_table_pdf.axis('off')
                    table_pdf = ax_table_pdf.table(cellText=dfn.values, colLabels=dfn.columns, loc='center', cellLoc='center')
                    table_pdf.auto_set_font_size(False); table_pdf.set_fontsize(8); table_pdf.scale(1, 1.2)
                    pdf.savefig(fig_table_pdf); plt.close(fig_table_pdf)
            buffer.seek(0)
            st.download_button("📥 Baixar PDF", buffer, "relatorio_HP.pdf", "application/pdf")
        else: st.warning("Nenhum gráfico gerado para exportar.")
    st.markdown("---")

    st.header("🔍 Modelo Preditivo de Detecção de Falsificação")
    df_modelo = df_filtrado.copy()
    min_samples_model = 20
    if not df_modelo.empty and len(df_modelo) >= min_samples_model:
        df_modelo['Falsificado'] = np.where(
            (df_modelo['Tipo'] == 'Genérico') & (df_modelo['Chamados'] > 200) & (df_modelo['Taxa_Devolucao'] > 0.15), 1, 0)

        if df_modelo['Falsificado'].nunique() > 1:
            X_features = ['Chamados', 'Taxa_Devolucao', 'NPS']
            if all(col in df_modelo.columns for col in X_features):
                X = df_modelo[X_features]
                y = df_modelo['Falsificado']
                min_class_count = y.value_counts(dropna=False).min()

                if len(X) >= min_samples_model and min_class_count * (1 - 0.3) >= 2 and not y.isnull().any():
                    try:
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42) # Variables now have broader scope
                        if not X_test.empty and not X_train.empty:
                            clf = RandomForestClassifier(random_state=42) # clf now has broader scope
                            clf.fit(X_train, y_train)
                            pred = clf.predict(X_test)
                            st.markdown("#### Relatório de Classificação:")
                            try:
                                report_dict = classification_report(y_test, pred, zero_division=0, output_dict=True, target_names=['Original (0)', 'Falsificado (1)'])
                                report_df = pd.DataFrame(report_dict).transpose()
                                metrics_cols = ['precision', 'recall', 'f1-score']
                                for col_name in metrics_cols:
                                    if col_name in report_df.columns: report_df[col_name] = pd.to_numeric(report_df[col_name], errors='coerce')
                                st.dataframe(report_df.style.format("{:.2f}", subset=metrics_cols, na_rep="-"))
                            except Exception as e_report:
                                st.error(f"Erro relatório: {e_report}")
                                st.text(classification_report(y_test, pred, zero_division=0))
                    except ValueError as e_split: st.warning(f"Divisão de dados falhou: {e_split}.")
                    except Exception as e_model: st.error(f"Erro no treinamento do modelo: {e_model}")
                else: st.warning("Dados insuficientes por classe ou NaNs na variável alvo para treinar.")
            else: st.warning(f"Colunas para modelo ({', '.join(X_features)}) não encontradas.")
        else: st.warning("Coluna alvo 'Falsificado' não possui variedade suficiente.")
    else: st.warning(f"Dados filtrados insuficientes para modelo ({min_samples_model} linhas mínimas).")
    st.markdown("---")

    # --- GOVERNANÇA DE IA (SHAP) --- Updated Section ---
    st.header("🧠 Painel de Governança de IA")
    if clf and X_train is not None and X_test is not None and not X_test.empty:
        if isinstance(X_train, pd.DataFrame) and isinstance(X_test, pd.DataFrame) and not X_train.columns.empty:
            num_samples_for_shap = min(20, len(X_test))
            if num_samples_for_shap > 0:
                X_test_shap = X_test.head(num_samples_for_shap)
                st.write(f"Gerando explicações SHAP para {len(X_test_shap)} amostras.")
                st.caption(f"Features do modelo (X_train.columns): {list(X_train.columns)}")
                try:
                    explainer = shap.Explainer(clf, X_train)
                    shap_values_obj = explainer(X_test_shap)

                    # --- DETAILED SHAP OBJECT DEBUGGING ---
                    with st.expander("Informações de Debug do Objeto SHAP (Clique para expandir)"):
                        st.write(f"- `type(shap_values_obj)`: `{type(shap_values_obj)}`")
                        if hasattr(shap_values_obj, 'values'):
                            st.write(f"- `shap_values_obj.values.shape`: `{shap_values_obj.values.shape}`")
                        else: st.write("- `shap_values_obj` não possui o atributo 'values'.")
                        if hasattr(shap_values_obj, 'base_values'):
                            base_values_info = shap_values_obj.base_values.shape if hasattr(shap_values_obj.base_values, 'shape') else type(shap_values_obj.base_values)
                            st.write(f"- `shap_values_obj.base_values` (shape or type): `{base_values_info}`")
                        else: st.write("- `shap_values_obj` não possui o atributo 'base_values'.")
                        st.write(f"- `shap_values_obj.feature_names`: `{shap_values_obj.feature_names}`")
                        if hasattr(shap_values_obj, 'data'):
                            data_info = shap_values_obj.data.shape if hasattr(shap_values_obj.data, 'shape') else type(shap_values_obj.data)
                            st.write(f"- `shap_values_obj.data` (shape or type): `{data_info}`")
                        else: st.write("- `shap_values_obj` não possui o atributo 'data'.")
                    # --- END DETAILED DEBUGGING ---

                    if shap_values_obj.feature_names is None and hasattr(X_test_shap, 'columns'):
                        st.caption("SHAP: Tentando atribuir nomes de features ao objeto SHAP (fallback).")
                        shap_values_obj.feature_names = list(X_test_shap.columns)

                    if hasattr(shap_values_obj, 'feature_names') and shap_values_obj.feature_names and hasattr(shap_values_obj, 'values'):
                        st.write("Importância média global das features (SHAP):")
                        plot_values_for_bar = shap_values_obj
                        
                        if len(shap_values_obj.values.shape) == 3 and shap_values_obj.values.shape[-1] == 2: # Binary classification case
                            st.caption("SHAP: Detectado formato para classificação binária. Usando SHAP values para a classe 1 (Falsificado).")
                            plot_values_for_bar = shap_values_obj[:, :, 1] # Explanation object for class 1
                        elif len(shap_values_obj.values.shape) != 2 : # If not (samples, features)
                             st.warning(f"SHAP: Formato inesperado para `shap_values_obj.values` (shape: {shap_values_obj.values.shape}). Gráfico pode não funcionar.")
                        
                        fig_shap_bar, ax_shap_bar = plt.subplots()
                        num_features_to_display = min(len(plot_values_for_bar.feature_names) if plot_values_for_bar.feature_names else X_test_shap.shape[1], 10)
                        
                        shap.plots.bar(plot_values_for_bar, show=False, max_display=num_features_to_display)
                        st.pyplot(fig_shap_bar)
                        plt.close(fig_shap_bar)
                    else:
                        st.error("SHAP: Nomes das features ou valores SHAP não encontrados/inválidos. Não é possível gerar o gráfico.")

                except IndexError as e_shap_idx:
                    st.error(f"SHAP Erro: IndexError - {e_shap_idx}")
                    st.caption("Verifique consistência dos nomes das features ou estrutura do objeto SHAP. Informações de debug acima podem ajudar.")
                except Exception as e_shap:
                    st.error(f"SHAP Erro Inesperado: {type(e_shap).__name__} - {e_shap}")
            else: st.warning("SHAP: Amostras insuficientes em X_test.")
        else: st.warning("SHAP: X_train/X_test não são DataFrames válidos.")
    else: st.info("SHAP: Modelo não treinado ou dados de teste/treino indisponíveis.")
    st.markdown("---")
    # --- End of Updated SHAP Section ---

    st.header("🔌 Interação com Banco de Dados (SQLite)")
    db_conn = None
    try:
        db_conn = connect_db()
        if not df_filtrado.empty:
            df_filtrado.to_sql("relatorio", db_conn, if_exists="replace", index=False)
            st.success("Dados do painel atualizados no banco local ('relatorio').")
        else:
            st.info("Nenhum dado do painel para salvar no banco.")

        st.subheader("Visualizar e Filtrar Dados do Banco")
        cursor = db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='relatorio';")
        table_exists = cursor.fetchone()

        if table_exists:
            db_regioes_disponiveis = pd.read_sql_query("SELECT DISTINCT Região FROM relatorio", db_conn)['Região'].tolist()
            db_tipos_disponiveis = pd.read_sql_query("SELECT DISTINCT Tipo FROM relatorio", db_conn)['Tipo'].tolist()

            db_filter_regiao = st.multiselect("Filtrar Região (DB)", db_regioes_disponiveis, default=db_regioes_disponiveis[:min(3, len(db_regioes_disponiveis))])
            db_filter_tipo = st.multiselect("Filtrar Tipo (DB)", db_tipos_disponiveis, default=db_tipos_disponiveis)
            limit_rows = st.slider("Número de linhas para exibir (DB)", 5, 50, 10)

            if st.button("Aplicar Filtros e Ver Dados do BD"):
                query_db = "SELECT * FROM relatorio"
                filters_sql_db, params_sql_db = [], []
                if db_filter_regiao:
                    filters_sql_db.append(f"Região IN ({','.join(['?']*len(db_filter_regiao))})")
                    params_sql_db.extend(db_filter_regiao)
                if db_filter_tipo:
                    filters_sql_db.append(f"Tipo IN ({','.join(['?']*len(db_filter_tipo))})")
                    params_sql_db.extend(db_filter_tipo)
                if filters_sql_db: query_db += " WHERE " + " AND ".join(filters_sql_db)
                query_db += f" ORDER BY Data DESC LIMIT ?"
                params_sql_db.append(limit_rows)
                try:
                    df_from_db = pd.read_sql_query(query_db, db_conn, params=params_sql_db)
                    if not df_from_db.empty:
                        st.dataframe(df_from_db)
                        total_in_db = pd.read_sql_query("SELECT COUNT(*) FROM relatorio", db_conn).iloc[0,0]
                        st.caption(f"Exibindo {len(df_from_db)} de {total_in_db} linhas (filtros aplicados).")
                    else: st.info("Nenhum dado no banco com os filtros aplicados.")
                except Exception as e_db_read: st.error(f"Erro ao ler dados do banco: {e_db_read}")
        else:
            st.info("Tabela 'relatorio' ainda não existe no banco. Salve dados primeiro.")
    except Exception as e_sql: st.error(f"Erro no SQLite: {e_sql}")
    finally:
        if db_conn: db_conn.close()
    st.markdown("---")
else:
    st.info("Nenhum dado carregado ou que corresponda aos filtros do dashboard.")

st.header("📚 Educação ao Cliente: Proteja-se Contra Falsificações HP")
st.info("""
Produtos HP falsificados não apenas prejudicam seu investimento com baixa qualidade e durabilidade,
mas também podem danificar seus valiosos equipamentos HP e comprometer sua segurança de dados e operacional.
Aprender a identificar produtos falsificados é o primeiro passo para uma experiência HP genuína e segura.
""")
col_edu1, col_edu2 = st.columns(2)
with col_edu1:
    st.subheader("🚨 Como Identificar Cartuchos e Suprimentos HP Falsos?")
    st.markdown("""
    - **🔍 Verifique a Embalagem:** Selos de Segurança HP, Qualidade da Impressão, Danos e Reembalagem.
    - **💰 Preço Suspeito:** Se uma oferta parece boa demais para ser verdade, geralmente é.
    - **📉 Qualidade de Impressão Inferior:** Manchas, cores desbotadas, falhas, menor durabilidade.
    - **📱 Autenticação Móvel HP:** Use o QR Code no selo de segurança com o app HP SureSupply.
    - **🛒 Compre de Fontes Confiáveis:** HP diretamente ou revendedores autorizados.
    """)
    st.video("https://www.youtube.com/watch?v=o_SUz4xSW3Y") # Example: HP Anti-Counterfeit program
    st.caption("Vídeo Oficial HP: Identificando Suprimentos HP Genuínos (Exemplo).")
with col_edu2:
    st.subheader("💥 Perigos e Prejuízos dos Produtos Falsificados")
    st.markdown("""
    - **🛠️ Danos ao Equipamento HP:** Entupimentos, vazamentos, danos permanentes.
    - **🔒 Riscos à Segurança:** Falhas elétricas, superaquecimento por componentes "chipados".
    - **🌎 Impacto Ambiental Negativo:** Sem práticas sustentáveis ou reciclagem.
    - **💸 Perda Financeira Real:** Menor rendimento, substituições frequentes, reparos.
    - **❌ Sem Garantia ou Suporte HP:** Garantia invalidada, sem suporte técnico.
    """)
    st.video("https://www.youtube.com/watch?v=H0rKz_gH7tA") # Example: Why buy original HP ink
    st.caption("Vídeo Oficial HP: A Importância dos Suprimentos Originais (Exemplo).")
st.markdown("""
**Sua Ação é Importante!** Se suspeitar de um produto HP falsificado, denuncie.
Visite o [**Site Oficial HP Anti-Falsificação**](https://www.hp.com/us-en/cartridge/anti-counterfeit.html).
""")
st.markdown("---")

st.header("⏱️ Gestão do Modelo Preditivo")
if not df.empty:
    if st.button("Treinar novamente o modelo com TODOS os dados carregados"):
        df_retrain = df.copy()
        min_samples_retrain = 20
        if not df_retrain.empty and len(df_retrain) >= min_samples_retrain:
            df_retrain['Falsificado'] = np.where(
                (df_retrain['Tipo'] == 'Genérico') & (df_retrain['Chamados'] > 200) & (df_retrain['Taxa_Devolucao'] > 0.15), 1, 0)
            if df_retrain['Falsificado'].nunique() > 1:
                X_features_retrain = ['Chamados', 'Taxa_Devolucao', 'NPS']
                if all(col in df_retrain.columns for col in X_features_retrain):
                    X_full_retrain = df_retrain[X_features_retrain]
                    y_full_retrain = df_retrain['Falsificado']
                    if len(X_full_retrain) >= min_samples_retrain and not y_full_retrain.isnull().any() and y_full_retrain.value_counts().min() * (1-0.3) >=2 :
                        try:
                            clf_retrained_model = RandomForestClassifier(random_state=42)
                            clf_retrained_model.fit(X_full_retrain, y_full_retrain)
                            st.success("Modelo treinado com sucesso com todos os dados carregados!")
                        except Exception as e_retrain_fit: st.error(f"Erro ao treinar: {e_retrain_fit}")
                    else: st.error("Retreino falhou: dados insuficientes por classe ou NaNs na var. alvo.")
                else: st.error(f"Retreino falhou: Colunas ({', '.join(X_features_retrain)}) não encontradas.")
            else: st.error("Retreino falhou: sem variedade na variável alvo 'Falsificado'.")
        else: st.error(f"Retreino falhou: mínimo de {min_samples_retrain} linhas necessárias.")
elif df.empty:
    st.warning("Não há dados carregados para treinar o modelo.")
else:
    st.info("Modelo inicial não treinado (aguardando dados válidos no dashboard).")