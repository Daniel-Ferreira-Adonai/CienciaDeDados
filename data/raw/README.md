# Dados brutos

O arquivo bruto não é versionado no GitHub. Para reproduzir a análise:

1. Baixe `datatran2026.csv` pelo [Google Drive da equipe](https://drive.google.com/file/d/1A3IirNm0AzRaSosA1IS94DOVmvKsn0Ol/view).
2. Salve-o exatamente neste diretório com o nome `datatran2026.csv`.
3. Execute, na raiz do repositório:

   ```bash
   python scripts/run_eda.py
   ```

O pipeline aceita a codificação original `cp1252` e o separador `;`. O arquivo deve permanecer local e ignorado pelo Git; não faça `git add -f` desse CSV.

Fonte temática: [dados abertos da Polícia Rodoviária Federal (PRF)](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf). O recorte atualmente utilizado cobre janeiro a julho de 2026.
