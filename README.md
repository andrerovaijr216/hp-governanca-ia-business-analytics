# Painel Executivo do Piloto — Governança & Analytics

Este projeto é o entregável da **Sprint 3**, consistindo em um dashboard interativo desenvolvido com Streamlit para monitorar os resultados de um piloto de Inteligência Artificial. O painel consolida métricas de performance do modelo, governança, ética (Fairness e LGPD) e impacto de negócio (ROI).

---

## 👥 Integrantes

| Nome                | RM       |
| ------------------- | -------- |
| André Rovai         | RM555848 |
| Thiago Almança      | RM558108 |
| Alan de Souza       | RM557088 |
| Leonardo Zago       | RM558691 |
| Renan de França     | RM558413 |
| Antonio Vinicius    | RM558014 |

---

## 🚀 Sobre o Projeto

O objetivo deste painel é fornecer uma visão 360º dos resultados do piloto para uma audiência executiva, permitindo a tomada de decisão informada sobre a continuidade do modelo (Go/No-Go). Ele integra dados de detecção, operação, fairness e negócio em uma única interface, com filtros dinâmicos e capacidade de exportação de dados.

### ✨ Funcionalidades

O painel é dividido nas seguintes seções:

1.  **Visão Geral**: Apresenta os principais KPIs do modelo (Precisão, Recall, FPR, FNR), comparação de metas vs. realizado e a tendência temporal de tickets e devoluções.
2.  **Detecção & Operação**: Mostra a matriz de confusão, o tempo médio para detecção de anomalias, a fila de revisão humana (human-in-the-loop) e a taxa de override.
3.  **Fairness & Governança**: Analisa o desempenho do modelo por diferentes segmentos (região, canal) para garantir a equidade. Inclui um "Model Card" e um resumo "LGPD mini" para transparência.
4.  **Negócio & ROI**: Compara os resultados das iniciativas "Com Ação" vs. "Sem Ação" e calcula uma estimativa de ROI e payback para avaliar o impacto financeiro.
5.  **Mapa Regional**: Exibe um mapa de calor com a incidência de suspeitas por região, identificando hotspots de falsificação.
6.  **Downloads & Evidências**: Permite exportar os dados filtrados em formato CSV e gera um resumo executivo automático, além de um campo para anotações e insights.

---

## 🛠️ Como Executar o Projeto

Siga os passos abaixo para executar o dashboard localmente.

### Pré-requisitos

-   [Python 3.8+](https://www.python.org/downloads/)
-   `pip` (gerenciador de pacotes do Python)

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

3.  **Instale as dependências:**
    Crie um arquivo chamado `requirements.txt` na raiz do projeto com o seguinte conteúdo:
    ```
    streamlit
    pandas
    numpy
    plotly
    scikit-learn
    ```
    Em seguida, instale as bibliotecas com o comando:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```

Após executar o comando, o dashboard será aberto automaticamente no seu navegador padrão.

---
