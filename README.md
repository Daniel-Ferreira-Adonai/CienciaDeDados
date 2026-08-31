# Classificação da Gravidade de Acidentes em Rodovias Federais

Projeto da disciplina de Ciência de Dados (UNIFOR).

## Objetivo

Construir e avaliar modelos de aprendizado de máquina para classificar a **gravidade de um acidente de trânsito** em rodovias federais no momento da sua ocorrência, a partir de circunstâncias conhecidas previamente (sem informações sobre o desfecho).

O problema é de **classificação multiclasse**, com a variável-alvo `classificacao_acidente` assumindo um dos seguintes valores:

- `sem vítimas`
- `com vítimas feridas`
- `com vítimas fatais`

### Features utilizadas

Apenas circunstâncias conhecidas **no momento da ocorrência** do acidente:

- dia da semana
- horário
- causa do acidente
- tipo de acidente
- fase do dia
- condição meteorológica
- tipo de pista
- traçado da via
- uso do solo
- BR (rodovia)
- km
- número de veículos envolvidos
- número de pessoas envolvidas

### Vazamento de dados (data leakage)

As colunas de **desfecho** do acidente — `mortos`, `feridos`, `feridos_leves`, `feridos_graves`, `ilesos`, `ignorados` — **não devem ser usadas como features**, pois são resultado direto do acidente e determinam trivialmente o rótulo, o que causaria vazamento de dados (data leakage) e invalidaria a avaliação do modelo. Essas colunas só podem ser usadas para **derivar/validar** a variável-alvo, nunca como entrada do modelo.

## Fonte dos dados

Dados abertos de acidentes registrados pela **Polícia Rodoviária Federal (PRF)**, referentes ao período de **2020 a 2026**.

- Portal de dados abertos da PRF: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf

## Estrutura de pastas

```
.
├── data/
│   ├── raw/            # Dados brutos, exatamente como baixados da fonte (não versionar CSVs grandes)
│   └── processed/       # Dados limpos/transformados, prontos para modelagem
├── notebooks/            # Notebooks de análise exploratória (EDA) e experimentos
├── src/                  # Código-fonte reutilizável (pré-processamento, features, treino, avaliação)
├── models/               # Modelos treinados serializados (.pkl, .joblib)
├── results/
│   ├── figures/          # Gráficos e visualizações geradas
│   └── metrics/          # Métricas de avaliação dos modelos (relatórios, tabelas)
├── docs/
│   ├── artigo/           # Artigo científico do projeto
│   └── slides/           # Slides de apresentação
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalação

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd TrabalhoCynthia
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Reprodução dos experimentos

1. Coloque a base de dados bruta da PRF em `data/raw/`.
2. Execute os notebooks/scripts de pré-processamento para gerar os dados limpos em `data/processed/`.
3. Execute os notebooks de análise exploratória em `notebooks/`.
4. Execute o treinamento dos modelos (os artefatos treinados serão salvos em `models/`).
5. Execute a avaliação dos modelos; figuras e métricas serão salvas em `results/figures/` e `results/metrics/`, respectivamente.

> Observação: a estrutura de código de pré-processamento, features, treino e avaliação ainda será adicionada em `src/`.

## Equipe

| Nome | Matrícula | E-mail |
|------|-----------|--------|
| [Nome do integrante 1] | [Matrícula] | [e-mail] |
| [Nome do integrante 2] | [Matrícula] | [e-mail] |
| [Nome do integrante 3] | [Matrícula] | [e-mail] |
| [Nome do integrante 4] | [Matrícula] | [e-mail] |

Disciplina: Ciência de Dados — Universidade de Fortaleza (UNIFOR)

## Licença

Este projeto tem finalidade exclusivamente **acadêmica**, desenvolvido no âmbito da disciplina de Ciência de Dados da UNIFOR. Os dados utilizados são públicos e disponibilizados pela Polícia Rodoviária Federal (PRF). O conteúdo deste repositório não deve ser utilizado para fins comerciais.
# CienciaDeDados
