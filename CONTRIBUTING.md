# Como contribuir

## Fluxo recomendado

1. Atualize sua branch a partir de `main`.
2. Crie uma branch curta, por exemplo `feat/modelos-individuais`, `fix/preprocessamento` ou `docs/artigo`.
3. Não adicione CSVs, modelos serializados ou outros artefatos grandes ao Git.
4. Rode o pipeline e as verificações locais antes de abrir o pull request:

   ```bash
   python -m py_compile src/data_pipeline.py src/modeling.py scripts/run_eda.py
   python -m unittest discover -s tests
   python scripts/run_eda.py
   ```

5. Descreva no pull request a motivação, os arquivos alterados, as métricas e qualquer decisão sobre dados ou leakage.

## Regras de experimento

- Mantenha o pré-processamento dentro de `src/`, para que notebooks e scripts reutilizem a mesma lógica.
- Registre semente aleatória, divisão dos dados, hiperparâmetros e métricas.
- Nunca use colunas de desfecho como atributos de entrada.
- Prefira `results/metrics/` e `results/figures/` para artefatos pequenos e revisáveis; bases e modelos continuam locais.
- Antes de trocar a fonte ou o período dos dados, atualize `data/raw/README.md` e `docs/primeira_entrega.md`.
