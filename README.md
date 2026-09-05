# Classificação da gravidade de acidentes em rodovias federais

Projeto acadêmico da disciplina de Ciência de Dados (UNIFOR), desenvolvido pela equipe para analisar acidentes registrados pela Polícia Rodoviária Federal (PRF). O problema foi definido como uma classificação multiclasse da gravidade do acidente:

- `Sem Vítimas`
- `Com Vítimas Feridas`
- `Com Vítimas Fatais`

## Escopo desta primeira entrega

Esta versão estabelece a base reproduzível do projeto:

- leitura do CSV bruto com validação do esquema;
- perfil da base e gráficos exploratórios iniciais;
- tratamento do registro sem classificação publicada, usando `mortos` e `feridos` apenas para completar/validar o alvo;
- preparação de uma base de modelagem com imputação, codificação categórica e transformação do horário;
- baseline de regressão logística para criar uma referência quantitativa;
- documentação para que todos os integrantes executem o mesmo fluxo.

O roteiro completo da disciplina ainda prevê algoritmos individuais, comitês homogêneos e heterogêneos, meta-modelo, avaliação estatística, análise de erros, robustez, artigo e slides. Esses itens devem ser adicionados em etapas posteriores.

## Dados e controle de vazamento

O recorte atual é `datatran2026.csv`, com acidentes de 01/01/2026 a 31/07/2026. O arquivo original tem 30 colunas e não é versionado por ser um artefato bruto grande. Cada integrante deve baixá-lo do [Drive da equipe](https://drive.google.com/file/d/1A3IirNm0AzRaSosA1IS94DOVmvKsn0Ol/view) e salvá-lo como `data/raw/datatran2026.csv`. As instruções estão em [`data/raw/README.md`](data/raw/README.md).

**Atenção:** o PDF do trabalho menciona SSPDS-CE/IBGE como fonte, enquanto esta implementação usa o recorte PRF já escolhido pela equipe. Confirmem essa compatibilidade com a professora antes da entrega final.

As colunas de desfecho (`mortos`, `feridos`, `feridos_leves`, `feridos_graves`, `ilesos` e `ignorados`) não entram como atributos dos modelos. Elas só podem apoiar a derivação ou a validação do rótulo, pois usá-las como entrada seria vazamento de dados.

## Instalação

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## Execução reproduzível

Na raiz do repositório, com o CSV em `data/raw/`:

```bash
python scripts/run_eda.py
```

O comando gera:

- `results/metrics/data_profile.json`: perfil e auditoria da base;
- `results/metrics/baseline_metrics.json`: métricas da baseline;
- `results/metrics/baseline_confusion_matrix.csv`: matriz de confusão;
- `results/figures/`: distribuição das classes, ausências e variáveis numéricas;
- `data/processed/modeling_base.csv`: base derivada local, também ignorada pelo Git.

Para usar outro arquivo:

```bash
python scripts/run_eda.py --input caminho/para/base.csv
```

## Estrutura

```text
data/raw/          CSV bruto local e instruções de obtenção
data/processed/   bases derivadas, não versionadas
notebooks/         análises exploratórias e experimentos interativos
src/               pipeline de dados e modelos reutilizáveis
scripts/           pontos de entrada executáveis
models/            modelos treinados (não versionados)
results/           métricas e figuras produzidas
docs/              documentação técnica e do artigo
```

## Equipe

| Nome | Matrícula | E-mail |
|---|---:|---|
| Daniel Felix | 2320432 | d.calpi100@gmail.com |
| Maximus Ulisses | 2320436 | Ulissesmagalhaes308@gmail.com |
| Josue Castro | 2320426 | josubeba115@gmail.com |
| Davi Klein | 2327146 | davimonteklein1711@gmail.com |

Disciplina: Ciência de Dados — Universidade de Fortaleza (UNIFOR).
