# Painel Executivo do Piloto — Governança & Analytics

[![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)](https://painel-executivo-piloto.streamlit.app/)

Dashboard interativo para monitoramento e governança de um piloto de Inteligência Artificial, focado em análise de performance, fairness e impacto de negócio (ROI). Este projeto representa o entregável da **Sprint 3**.

### 🔗 **[Acesse o Painel Interativo](https://painel-executivo-piloto.streamlit.app/)**

---

## 🎯 Sobre o Projeto

O objetivo deste painel é fornecer uma visão 360º dos resultados do piloto para uma audiência executiva, permitindo a tomada de decisão informada sobre a continuidade do modelo (Go/No-Go). Ele integra dados de detecção, operação, fairness e negócio em uma única interface, com filtros dinâmicos e capacidade de exportação de dados.

## ✨ Funcionalidades Principais

O painel é dividido em seções de fácil navegação:

*   **📊 Visão Geral**: KPIs centrais do modelo (Precisão, Recall, FPR, FNR), comparação de metas vs. realizado e tendência temporal de tickets e devoluções.
*   **⚙️ Detecção & Operação**: Matriz de confusão, tempo médio de detecção, fila de revisão humana (*human-in-the-loop*) e taxa de override.
*   **⚖️ Fairness & Governança**: Análise de equidade do modelo por diferentes segmentos (região, canal), além de um "Model Card" e resumo "LGPD mini" para transparência.
*   **📈 Negócio & ROI**: Comparativo de resultados ("Com Ação" vs. "Sem Ação") com estimativa de ROI e payback para avaliar o impacto financeiro.
*   **🗺️ Mapa Regional**: Mapa de calor interativo exibindo a incidência de suspeitas por região para identificar hotspots de falsificação.
*   **📥 Downloads & Evidências**: Ferramentas para exportar dados filtrados (CSV), gerar resumos executivos e registrar insights.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem**: Python 3.10+
*   **Framework**: Streamlit
*   **Bibliotecas**: Pandas, NumPy, Plotly, Scikit-learn

---

## 🚀 Como Executar Localmente

Siga os passos abaixo para executar o dashboard em sua máquina.

### Pré-requisitos

*   [Python 3.8+](https://www.python.org/downloads/)
*   `pip` (gerenciador de pacotes do Python)

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/painel-executivo-piloto-ia.git
    cd painel-executivo-piloto-ia
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências a partir do `requirements.txt`:**
    *Primeiro, certifique-se de que o arquivo `requirements.txt` existe com o seguinte conteúdo:*
    ```txt
    streamlit
    pandas
    numpy
    plotly
    scikit-learn
    ```
    *Depois, execute o comando de instalação:*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    *Substitua `app.py` pelo nome do seu arquivo principal (ex: `painel-executivo-piloto.py`).*
    ```bash
    streamlit run app.py
    ```

Após executar o comando, o dashboard será aberto automaticamente no seu navegador padrão.

---

## 👥 Equipe do Projeto

| Nome             | RM       |
| ---------------- | -------- |
| André Rovai      | RM555848 |
| Thiago Almança   | RM558108 |
| Alan de Souza    | RM557088 |
| Leonardo Zago    | RM558691 |
| Renan de França  | RM558413 |
| Antonio Vinicius | RM558014 |
