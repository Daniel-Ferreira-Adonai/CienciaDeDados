# Primeira entrega técnica

## Objetivo

Preparar uma base sólida para classificar a gravidade de acidentes rodoviários da PRF a partir de circunstâncias conhecidas no momento da ocorrência.

## O que foi implementado

1. **Aquisição reproduzível:** o CSV é mantido localmente em `data/raw/` e o repositório registra apenas a fonte e o nome esperado do arquivo.
2. **Validação:** o pipeline verifica as colunas mínimas, padroniza textos e registra duplicidades, ausências, período e distribuição do alvo.
3. **Controle de leakage:** as colunas de desfecho são usadas somente para completar a classificação ausente; a tabela de modelagem não as contém.
4. **Pré-processamento:** `horario` vira `hora`; `tracado_via` é decomposta em 12 colunas binárias (uma por característica da via), pois chegava com 432 combinações distintas e sensíveis à ordem dos termos. Categóricas de baixa cardinalidade recebem imputação pela moda e one-hot; `causa_acidente` (69 categorias) e `br` (110 categorias) recebem imputação pela moda e codificação pela média do alvo (TargetEncoder). Numéricas recebem imputação pela mediana e padronização.
5. **EDA inicial:** são produzidos gráficos de classes, valores ausentes e distribuições numéricas.
6. **Referência experimental:** uma regressão logística balanceada cria a primeira baseline, usando divisão estratificada de treino e teste.

## Diagnóstico observado na base atual

- 33.694 acidentes e 30 colunas.
- Período de 01/01/2026 a 31/07/2026.
- Classes publicadas: 5.195 sem vítimas, 26.032 com vítimas feridas e 2.467 com vítimas fatais; um registro não tinha classificação e foi completado a partir dos desfechos.
- Não foram encontrados IDs duplicados.
- Ausências principais: `uop` (3.119), `delegacia` (3.111), `regional` (3.105) e o rótulo publicado (1).

Os números acima são reproduzidos automaticamente em `results/metrics/data_profile.json`; não devem ser tratados como resultados definitivos antes das validações posteriores e dos experimentos exigidos pela disciplina.

## Ponto de validação do escopo acadêmico

O roteiro anexado ao trabalho menciona a utilização de dados da SSPDS-CE/IBGE. A base escolhida pela equipe e o README original do repositório apontam para dados abertos da PRF. Essa diferença precisa ser confirmada com a professora antes da versão final do artigo; tecnicamente, o pipeline já está desacoplado da fonte e pode receber uma base compatível mediante atualização do esquema e da documentação.

## Baseline atual

Na divisão estratificada 80/20, a regressão logística obteve acurácia de aproximadamente 0,5792, balanced accuracy de 0,6017 e F1 macro de 0,4802, com `class_weight="balanced"` para lidar com o desbalanceamento. Testamos também reamostragem (SMOTE e SMOTEENN, da biblioteca imblearn) no lugar do peso por classe: SMOTE ficou no mesmo patamar (F1 macro 0,480), e SMOTEENN piorou bastante (F1 macro 0,374), então mantivemos `class_weight="balanced"` por ora. A literatura associa reamostragem a ganhos maiores quando combinada a modelos de árvore, então a comparação deve ser refeita quando esses algoritmos entrarem em cena. Esses números são apenas referência inicial, não uma conclusão sobre o melhor modelo.

## Decisões e limites

- O recorte disponível atualmente é de 2026, até julho. Se a equipe incorporar outros anos, o período e a distribuição precisam ser regenerados.
- O alvo publicado é preservado quando válido. A derivação por `mortos`/`feridos` é um mecanismo de recuperação para rótulos ausentes, não uma justificativa para usar esses campos no modelo.
- A baseline não representa a solução final. Ela serve para comparar, nas próximas etapas, algoritmos individuais e comitês sob a mesma divisão e as mesmas métricas.

## Próximas etapas sugeridas

1. Revisar os gráficos e escolher hipóteses para o artigo.
2. Adicionar validação cruzada estratificada e um conjunto fixo de métricas macro e ponderadas.
3. Implementar algoritmos individuais e registrar hiperparâmetros.
4. Implementar os comitês homogêneos e heterogêneos previstos no roteiro.
5. Adicionar análise de erros, robustez, testes estatísticos, referências e material de apresentação.
