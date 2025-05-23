# 🛡️ HP – Detecção e Monitoramento de Produtos Falsificados

## 🎯 Objetivo

Transformar os insights obtidos na Sprint 1 em ações tangíveis por meio da:

- Prototipagem de dashboards analíticos.
- Construção de modelo preditivo para detecção de produtos falsificados.
- Aplicação de práticas de Governança de IA.
- Desenvolvimento de plano de educação e engajamento do cliente.
- Estimativa do impacto de medidas preventivas.

## 📦 Destaques dos Insights

- 🧾 **Chamados por Região:** Nordeste possui até **3x mais chamados** por cartuchos falsificados do que o Sul.
- 📉 **NPS Médio:** Originais ~72 | Genéricos ~41.
- ♻️ **Taxa de Devolução:** Genéricos apresentam até **4x mais devoluções**.

## 🚀 Funcionalidades Entregues

### 1. 📊 Dashboard Interativo

Protótipo funcional desenvolvido em **Python + Streamlit**, com recursos como:

- Filtros por **região e período**.
- Visualização de **chamados, devoluções e NPS** por tipo e região.
- Exportação em **PDF** com gráficos e estatísticas.
- Integração com banco de dados local **SQLite**.

### 2. 🔍 Modelo de Detecção de Falsificação

Modelo preditivo com base em regras simuladas e aprendizado de máquina:

- **Algoritmo:** Random Forest.
- **Variáveis:** Número de chamados, taxa de devolução, NPS.
- **Critério Simulado:** Genérico com >200 chamados e >15% de devoluções → "Alta chance de falsificação".
- Métricas exibidas: precisão, recall e f1-score.
- **Explicabilidade com SHAP** para transparência nas decisões.

### 3. 🧠 Governança de IA

Princípios aplicados ao modelo:

- **Transparência:** Gráficos SHAP para justificar decisões.
- **Responsabilidade:** Estrutura para supervisão contínua dos modelos.
- **Privacidade:** Proteção de dados dos clientes e uso anonimizado.
- **Mitigação de Vieses:** Prevenção de penalizações injustas por região ou renda.

### 4. 📚 Educação ao Cliente

Módulo informativo integrado à aplicação com:

- Dicas práticas para **identificar falsificações**.
- **Vídeos oficiais da HP** sobre riscos e identificação de cartuchos falsos.
- Incentivo ao uso de **aplicativos oficiais e QR Code de verificação**.
- Sugestão de campanhas digitais e programa de fidelidade.

### 5. 📈 Simulação de Impacto

Cenários projetados com dados sintéticos:

- **Sem ação:** +20% em devoluções em 1 ano.
- **Com IA e prevenção:** -35% em suporte técnico.
- Visualização comparativa clara entre os dois cenários.

## 🛠️ Tecnologias Utilizadas

| Categoria            | Ferramentas Utilizadas                                 |
|----------------------|--------------------------------------------------------|
| Linguagem            | Python 3.10+                                           |
| Web App              | Streamlit                                              |
| Machine Learning     | scikit-learn                                           |
| Explicabilidade      | SHAP                                                   |
| Visualizações        | Matplotlib, Seaborn                                    |
| Banco de Dados       | SQLite                                                 |
| Manipulação de Dados | Pandas, NumPy                                          |
| Outros               | OpenPyXL (upload de Excel), PDF Export (matplotlib)    |

## 🧪 Como Executar Localmente

1. **Clone o repositório:**

```bash
git clone <url-do-repo>
cd hp-falsificados
````

2. **Crie e ative um ambiente virtual:**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Execute a aplicação:**

```bash
streamlit run app.py
```

## 👥 Equipe

* **André Rovai** – RM555848
* **Thiago Almança** – RM558108
* **Alan de Souza** – RM557088
* **Leonardo Zago** – RM558691
* **Renan de França** – RM558413
* **Antonio Vinicius** – RM558014

## 📌 Observações Finais

Este projeto é um **estudo simulado com fins acadêmicos e educativos**, sem objetivo comercial. Os dados utilizados são **sintéticos** e têm como propósito exemplificar o uso de:

* Técnicas de Business Analytics.
* Modelagem preditiva.
* Aplicação prática de Governança de IA.
* Estratégias de engajamento com o consumidor.

## 📄 Licença

Distribuído sob a Licença MIT.
Consulte o arquivo `LICENSE` para mais detalhes.

```
