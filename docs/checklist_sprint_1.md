# Checklist de entrega - Sprint 1

Este arquivo separa o que já está produzido no repositório do que ainda exige uma ação real da equipe.

## Pronto no repositório

- [x] Base DataTran 2026 documentada: origem, formato, período, tamanho, atributos e variável-alvo.
- [x] Código reprodutível da análise exploratória em `scripts/run_eda.py`.
- [x] Gráficos e tabelas sobre classes, ausências, distribuições, valores extremos, correlação, dispersão e padrões temporais.
- [x] Interpretações dos gráficos no relatório.
- [x] Relatório da Sprint 1 em `docs/artigo/relatorio_sprint_1.pdf`, com as seções posteriores explicitamente reservadas.
- [x] Testes básicos do pipeline de dados.

## Ações da equipe antes de enviar

- [ ] Compartilhar o quadro do Trello com `cynthiamaia@unifor.br`.
- [ ] Registrar no Trello o histórico verdadeiro da Sprint 1: responsáveis, datas e movimentação dos cartões. Não inventar datas ou atividades.
- [ ] Confirmar com a professora se a base PRF/DataTran está validada para o tema proposto, caso isso ainda não tenha sido feito.
- [ ] Conferir se os nomes, matrículas e e-mails da equipe no `README.md` estão corretos.
- [ ] Executar os comandos abaixo em uma máquina do grupo e abrir o PDF gerado para uma última conferência.
- [ ] Fazer commit e enviar os arquivos ao GitHub.

## Como reproduzir o material

Na raiz do repositório, com o CSV salvo em `data/raw/datatran2026.csv`:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/run_eda.py
python scripts/build_sprint1_report.py
```

## Sugestão de cartões para o Trello

Cadastre somente os responsáveis e as datas que realmente ocorreram:

- Selecionar e documentar a base DataTran 2026
- Configurar estrutura inicial do repositório
- Implementar leitura e validação do CSV
- Executar análise exploratória e gerar gráficos
- Interpretar resultados da EDA
- Revisar e gerar o relatório da Sprint 1
- Revisar entrega e publicar no GitHub
- Compartilhar o Trello com a professora
