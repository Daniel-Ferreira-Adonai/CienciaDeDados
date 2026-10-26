"""Gera o relatório em PDF da Sprint 1 a partir dos resultados reproduzíveis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = ROOT / "docs" / "artigo" / "relatorio_sprint_1.pdf"
FIGURES = ROOT / "results" / "figures"


def _styles() -> dict[str, ParagraphStyle]:
    """Define um conjunto enxuto de estilos para manter o relatório uniforme."""

    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=23,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#3f4a54"),
            spaceAfter=8,
        ),
        "heading1": ParagraphStyle(
            "Heading1Custom",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0f4c5c"),
            spaceBefore=12,
            spaceAfter=8,
        ),
        "heading2": ParagraphStyle(
            "Heading2Custom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#1d5f73"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.3,
            leading=14.5,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4d5963"),
            spaceAfter=10,
        ),
        "reserved": ParagraphStyle(
            "Reserved",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#616e7c"),
            spaceAfter=7,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.6,
            leading=10.5,
            textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=10.8,
            alignment=TA_CENTER,
        ),
        "table_cell_left": ParagraphStyle(
            "TableCellLeft",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=10.8,
            alignment=0,
        ),
    }


def _paragraph(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, styles["body"])


def _figure(filename: str, caption: str, width: float = 16.3 * cm) -> KeepTogether:
    """Adiciona uma figura já gerada pelo pipeline, preservando a proporção."""

    path = FIGURES / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Figura não encontrada: {path}. Execute 'python scripts/run_eda.py'."
        )
    image = Image(str(path))
    ratio = image.imageHeight / image.imageWidth
    image.drawWidth = width
    image.drawHeight = width * ratio
    styles = _styles()
    return KeepTogether([image, Spacer(1, 0.15 * cm), Paragraph(caption, styles["caption"])])


def _table(data: list[list[str]], column_widths: list[float]) -> Table:
    # Células com texto puro não quebram linha no reportlab e podem vazar para
    # fora da coluna (ou da página) quando o conteúdo é longo; envolver cada
    # célula em um Paragraph garante a quebra automática dentro da largura
    # definida para a coluna.
    styles = _styles()
    wrapped = [[Paragraph(str(cell), styles["table_header"]) for cell in data[0]]]
    for row in data[1:]:
        wrapped.append(
            [
                Paragraph(str(cell), styles["table_cell_left"] if column == 0 else styles["table_cell"])
                for column, cell in enumerate(row)
            ]
        )
    table = Table(wrapped, colWidths=column_widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b7c4ce")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f7f8")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _header_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#b7c4ce"))
    canvas.line(document.leftMargin, A4[1] - 1.35 * cm, A4[0] - document.rightMargin, A4[1] - 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#52616b"))
    canvas.drawString(document.leftMargin, A4[1] - 1.05 * cm, "Ciência de Dados - UNIFOR | Sprint 1")
    canvas.drawRightString(A4[0] - document.rightMargin, 0.95 * cm, f"Página {document.page}")
    canvas.restoreState()


def build_report() -> Path:
    """Compõe apenas os conteúdos previstos para a Sprint 1 do projeto."""

    styles = _styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2.0 * cm,
        leftMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=1.7 * cm,
        title="Relatório - Sprint 1 - Ciência de Dados",
        author="Daniel Felix; Davi Klein; Josué Castro; Maximus Ulisses Magalhães",
    )
    story = []

    story.extend(
        [
            Spacer(1, 3.0 * cm),
            Paragraph("UNIVERSIDADE DE FORTALEZA - UNIFOR", styles["subtitle"]),
            Paragraph("Disciplina: Ciência de Dados", styles["subtitle"]),
            Spacer(1, 1.8 * cm),
            Paragraph(
                "Predição da gravidade de acidentes em rodovias federais com aprendizado de máquina",
                styles["title"],
            ),
            Paragraph("Relatório técnico - Sprint 1 (revisado para a Sprint 2)", styles["subtitle"]),
            Spacer(1, 1.2 * cm),
            Paragraph("Daniel Felix", styles["subtitle"]),
            Paragraph("Davi Klein", styles["subtitle"]),
            Paragraph("Josué Castro", styles["subtitle"]),
            Paragraph("Maximus Ulisses Magalhães", styles["subtitle"]),
            Spacer(1, 2.2 * cm),
            Paragraph("Fortaleza - CE", styles["subtitle"]),
            Paragraph("30 de setembro de 2026", styles["subtitle"]),
            PageBreak(),
            Paragraph("Resumo", styles["heading1"]),
            _paragraph(
                "Esta primeira versão do relatório apresenta a seleção e a análise exploratória da base "
                "DataTran 2026, composta por registros de acidentes em rodovias federais brasileiras. "
                "O objetivo do projeto é classificar a gravidade dos acidentes em três categorias: sem vítimas, "
                "com vítimas feridas e com vítimas fatais, utilizando somente informações disponíveis no momento "
                "da ocorrência. Foram avaliadas a qualidade dos dados, a distribuição das classes, as variáveis "
                "numéricas, a correlação entre atributos e padrões temporais. Esta etapa estabelece a base para "
                "os experimentos com algoritmos individuais e comitês nas sprints seguintes.",
                styles,
            ),
            _paragraph(
                "Palavras-chave: ciência de dados; acidentes rodoviários; classificação; análise exploratória; PRF.",
                styles,
            ),
            Paragraph("1 Introdução", styles["heading1"]),
            Paragraph(
                "Seção reservada para desenvolvimento nas etapas posteriores, conforme o planejamento do projeto.",
                styles["reserved"],
            ),
            Paragraph("2 Trabalhos Relacionados", styles["heading1"]),
            _paragraph(
                "Scholz e Pinheiro (2023) investigaram a influência de atributos do ambiente e do veículo na "
                "gravidade de acidentes em rodovias federais brasileiras, com dados da PRF de 2017 a 2022 "
                "(862.465 registros após limpeza). O trabalho busca prever se um acidente é grave ou leve, a "
                "partir do estado físico da vítima; a unidade de análise é a pessoa envolvida, não o acidente, e "
                "o alvo é binário, diferente das três classes originais deste projeto. As variáveis foram "
                "testadas em três cenários incrementais: atributos gerais (dia da semana, horário, idade, sexo), "
                "de ambiente (condição meteorológica, tipo de pista, região) e de veículo (tipo, marca, ano de "
                "fabricação, preço obtido via tabela FIPE). Cinco algoritmos foram comparados (Árvore de Decisão, "
                "Random Forest, Naive Bayes, MLP e kNN); o cenário com atributos de veículo teve o melhor "
                "desempenho, com o Naive Bayes alcançando o maior F1-score (61%), superando o Random Forest mesmo "
                "este tendo acurácia nominal maior (86%) - os autores alertam que a acurácia isolada engana dado "
                "o desbalanceamento das classes (85,68% leve, 14,31% grave), ressalva também adotada neste "
                "relatório (Seção 4.1.1). A semelhança com este projeto está na fonte dos dados (PRF); a "
                "diferença, além da unidade de análise (pessoa, não acidente) e da granularidade binária do "
                "alvo, também aparece no tratamento de causa_acidente: Scholz e Pinheiro a excluem por "
                "vazamento, enquanto aqui ela entra como atributo via TargetEncoder (Seção 3.2) - um ponto que "
                "merece revisão, já que a causa também só é apurada pela PRF depois do acidente.",
                styles,
            ),
            _paragraph(
                "Mafort e Kappel (2025) publicaram recentemente um modelo de gravidade de acidentes nas "
                "rodovias federais do Rio de Janeiro, usando dados da PRF de 2020 a 2023. Depois de filtrar só "
                "o estado e remover registros incompletos, a base deles ficou com 18.104 linhas. O alvo também "
                "vem das colunas de desfecho (ilesos, feridos_leves, feridos_graves, mortos), como aqui (Seção "
                "3.1), mas colapsado em duas categorias - grave ou não-grave - em vez das três adotadas neste "
                "projeto. Entre as variáveis usadas estão tipo de acidente, fase do dia, clima, localização "
                "(latitude e longitude resumidas por PCA) e uma taxa de acidentes por quilômetro de rodovia, "
                "criada pelos próprios autores para capturar trechos mais perigosos. Testaram sete algoritmos "
                "(Regressão Logística, Naive Bayes, kNN, Árvore de Decisão, Random Forest, SVM e MLP) com busca "
                "bayesiana de hiperparâmetros; a Regressão Logística venceu, com 73,85% de acurácia e AUC-ROC de "
                "69,77%. Rodaram ainda o LIME para explicar as previsões e chegaram a uma conclusão parecida "
                "com a da Seção 4.1.5: tipo de acidente, fase do dia e clima pesam mais do que as variáveis "
                "numéricas isoladas. As principais diferenças em relação ao que fizemos aqui são o alvo binário, "
                "o recorte estadual e o período mais curto (2020-2023, contra o nacional de 2026 deste projeto), "
                "além do balanceamento por subamostragem, em vez do peso por classe testado na baseline (Seção "
                "3.2).",
                styles,
            ),
            Paragraph("3 Protocolo Experimental", styles["heading1"]),
            Paragraph("3.1 Base de Dados", styles["heading2"]),
            _paragraph(
                "A base utilizada é a DataTran 2026, disponibilizada pela Polícia Rodoviária Federal (PRF) em seu "
                "portal de dados abertos. Ela contém registros de acidentes em rodovias federais e permite "
                "estudar características do evento, da via e do contexto em que o acidente ocorreu.",
                styles,
            ),
            _paragraph(
                "O recorte analisado contém 33.694 instâncias e 30 atributos, referentes ao período de 1º de "
                "janeiro a 31 de julho de 2026. Os atributos incluem identificadores, data e horário, localização, "
                "características da rodovia, condições do acidente, pessoas e veículos envolvidos, além da "
                "classificação do acidente.",
                styles,
            ),
        ]
    )

    profile_data = [
        ["Característica", "Descrição"],
        ["Formato", "CSV com separador ponto e vírgula e codificação cp1252"],
        ["Instâncias", "33.694 acidentes"],
        ["Atributos", "30 colunas no arquivo bruto"],
        ["Período", "01/01/2026 a 31/07/2026"],
        ["Tarefa", "Classificação multiclasse"],
        ["Variável-alvo", "classificacao_acidente"],
        ["Classes", "Sem Vítimas; Com Vítimas Feridas; Com Vítimas Fatais"],
    ]
    attribute_types_data = [
        ["Tipo de atributo", "Qtd.", "Exemplos"],
        ["Categóricos (entrada do modelo)", "9", "dia_semana, causa_acidente, tipo_acidente, fase_dia, "
         "condicao_metereologica, tipo_pista, tracado_via, uso_solo, br"],
        ["Numéricos (entrada do modelo)", "3", "km, veiculos, pessoas (mais a hora, derivada do horario)"],
        ["Temporais", "2", "data_inversa, horario"],
        ["Geográficos", "4", "uf, municipio, latitude, longitude"],
        ["Identificador", "1", "id"],
        ["Variável-alvo", "1", "classificacao_acidente"],
        ["Desfecho (excluídos da modelagem)", "6", "mortos, feridos, feridos_leves, feridos_graves, ilesos, ignorados"],
        ["Administrativos (não utilizados)", "4", "sentido_via, regional, delegacia, uop"],
    ]
    story.extend(
        [
            KeepTogether(
                [
                    _table(profile_data, [4.1 * cm, 12.1 * cm]),
                    Spacer(1, 0.25 * cm),
                    Paragraph("Tabela 1 - Perfil da base selecionada.", styles["caption"]),
                ]
            ),
            _paragraph(
                "A base possui atributos categóricos, numéricos, temporais e geográficos, além de um "
                "identificador, da variável-alvo, de colunas de desfecho e de colunas administrativas que não "
                "entram na modelagem. A Tabela 2 quantifica essa divisão para as 30 colunas do arquivo bruto.",
                styles,
            ),
            KeepTogether(
                [
                    _table(attribute_types_data, [4.6 * cm, 1.4 * cm, 10.2 * cm]),
                    Spacer(1, 0.25 * cm),
                    Paragraph("Tabela 2 - Tipos de atributos da base bruta (30 colunas no total).", styles["caption"]),
                ]
            ),
            _paragraph(
                "A análise verificou ausência em quatro colunas, sobre um total de 33.694 registros: "
                "classificacao_acidente (1 registro), regional (3.105), delegacia (3.111) e uop (3.119). Não "
                "foram identificados IDs ou linhas duplicadas. O único rótulo ausente foi completado apenas para "
                "fins de consistência a partir das colunas de desfecho, de um total de 33.694 registros; tais "
                "colunas não são usadas como entrada dos modelos, para evitar vazamento de dados.",
                styles,
            ),
            Paragraph("3.2 Pré-processamento", styles["heading2"]),
            _paragraph(
                "O pré-processamento ocorre em duas etapas. A primeira, fora do pipeline de aprendizado, normaliza "
                "o arquivo bruto antes de qualquer ajuste de modelo: horario é convertido em hora inteira (0 a "
                "23), km/veiculos/pessoas têm a vírgula decimal convertida para ponto, e tracado_via é decomposta "
                "em colunas binárias (detalhado adiante). A segunda etapa roda dentro de um Pipeline do "
                "scikit-learn, treinado apenas sobre a partição de treino, para que nenhuma estatística do teste "
                "(moda, mediana, categorias ou médias do alvo) influencie o ajuste.",
                styles,
            ),
            KeepTogether(
                [
                    _table(
                        [
                            ["Grupo de atributos", "Etapas de pré-processamento"],
                            ["Categóricos de baixa cardinalidade (6 colunas)", "Imputação pela moda seguida de "
                             "codificação one-hot; categorias não vistas no treino são ignoradas no teste."],
                            ["Categóricos de alta cardinalidade (causa_acidente: 69 categorias; br: 110 "
                             "categorias)", "Imputação pela moda seguida de codificação pela média do alvo "
                             "(TargetEncoder, ajustada só no treino)."],
                            ["tracado_via (1 coluna bruta, 432 combinações distintas)", "Decomposta em 12 colunas "
                             "binárias, uma por característica física da via (reta, curva, aclive, interseção "
                             "etc.)."],
                            ["Numéricos (hora, km, veículos, pessoas + as 12 colunas de tracado_via)", "Imputação "
                             "pela mediana seguida de padronização (z-score: média 0 e desvio padrão 1)."],
                            ["Demais colunas (id, datas, desfecho, administrativas, geográficas)", "Descartadas "
                             "pelo ColumnTransformer (remainder=\"drop\"); nunca chegam ao classificador."],
                        ],
                        [4.4 * cm, 11.9 * cm],
                    ),
                    Spacer(1, 0.25 * cm),
                    Paragraph(
                        "Tabela 3 - Pré-processamento aplicado por grupo de atributos, dentro do Pipeline do scikit-learn.",
                        styles["caption"],
                    ),
                ]
            ),
            _paragraph(
                "A coluna tracado_via chega como combinações livres separadas por ponto e vírgula (por exemplo, "
                "\"Aclive;Reta\"), com 432 valores distintos nas 33.694 linhas e 200 deles aparecendo uma única "
                "vez; além de gerar centenas de colunas esparsas em one-hot, \"Aclive;Reta\" e \"Reta;Aclive\" "
                "seriam tratadas como categorias diferentes apesar de descreverem o mesmo trecho. Por isso, cada "
                "uma das 12 características identificadas (reta, curva, aclive, declive, interseção de vias, "
                "retorno regulamentado, rotatória, obras, viaduto, ponte, desvio temporário, túnel) vira uma "
                "coluna binária própria. causa_acidente (69 categorias) e br (110 categorias) têm o mesmo "
                "problema de cardinalidade; em vez de one-hot, cada categoria é substituída pela taxa média do "
                "alvo dentro dela (TargetEncoder, de Micci-Barreca, 2001), calculada apenas no treino - a mesma "
                "técnica usada por Scholz e Pinheiro (2023) para marca, tipo de veículo e região (Seção 2).",
                styles,
            ),
            _paragraph(
                "Manter causa_acidente como atributo é uma escolha que precisa ser revisitada: tanto Scholz e "
                "Pinheiro (2023) quanto Mafort e Kappel (2025) a excluem, já que a causa só é apurada pela PRF "
                "depois da ocorrência, o que a aproxima das colunas de desfecho em termos de disponibilidade "
                "temporal (Seção 2). Por ora optamos por mantê-la, dado o ganho de sinal observado na EDA "
                "(Seção 4.1.5), mas um teste comparativo com e sem essa coluna deve entrar nas próximas sprints.",
                styles,
            ),
            _paragraph(
                "Para o desbalanceamento das classes (Figura 1), testamos três estratégias na mesma regressão "
                "logística: peso balanceado por classe (class_weight=\"balanced\"), sobreamostragem sintética da "
                "classe minoritária (SMOTE) e SMOTE combinado à limpeza de vizinhos ambíguos (SMOTEENN). Os "
                "resultados não favoreceram a reamostragem nesta baseline linear: class_weight obteve F1 macro de "
                "0,480, SMOTE ficou praticamente empatado (0,480), e SMOTEENN piorou bastante (0,374), pois a "
                "limpeza de vizinhos removeu exemplos das classes majoritárias e derrubou a precisão geral. Por "
                "isso, a baseline atual mantém class_weight=\"balanced\"; a comparação deve ser refeita quando "
                "algoritmos de árvore entrarem na Seção 3.4.",
                styles,
            ),
            _paragraph(
                "Essa estrutura (ColumnTransformer com um sub-pipeline por grupo de atributo, dentro de um "
                "Pipeline maior com o classificador) deve se manter nas próximas sprints: o passo \"resample\" já "
                "está pronto para receber SMOTE ou SMOTEENN (de imblearn), e a etapa \"classifier\" pode ser "
                "trocada por outros algoritmos individuais e comitês, sem reescrever a imputação ou a "
                "codificação. O código está em src/modeling.py (build_baseline_pipeline) e src/data_pipeline.py "
                "(prepare_modeling_data), executado por scripts/run_eda.py.",
                styles,
            ),
            Paragraph("3.3 a 3.8 Demais componentes do protocolo", styles["heading2"]),
            Paragraph(
                "As definições de divisão de dados, algoritmos individuais, comitês, métricas e configuração experimental "
                "permanecem reservadas para as sprints posteriores.",
                styles["reserved"],
            ),
            Paragraph("4 Resultados", styles["heading1"]),
            Paragraph("4.1 Parte 1 - Análise Exploratória dos Dados", styles["heading2"]),
            Paragraph("4.1.1 Qualidade dos dados e distribuição das classes", styles["heading2"]),
            _paragraph(
                "Na Figura 1, a classe Com Vítimas Feridas concentra 26.032 registros (77,26%), seguida por Sem "
                "Vítimas com 5.195 registros (15,42%) e Com Vítimas Fatais com 2.467 registros (7,32%). Portanto, "
                "o problema é desbalanceado, com a classe de maior interesse prático - acidentes fatais - sendo "
                "também a mais rara. Nas próximas etapas, as métricas macro e estratégias apropriadas de "
                "balanceamento deverão receber mais atenção do que a acurácia isolada.",
                styles,
            ),
            _figure(
                "distribuicao_classes.png",
                "Figura 1 - Distribuição da variável-alvo após a validação do rótulo.",
            ),
            _paragraph(
                "Na Figura 2, as ausências aparecem concentradas em três colunas administrativas - regional, "
                "delegacia e uop -, cada uma com cerca de 9% de registros em branco (entre 3.105 e 3.119 "
                "ausências); nenhuma dessas colunas integra o conjunto de atributos de modelagem, então essas "
                "ausências não afetam os experimentos. A quarta coluna com ausência é a própria "
                "classificacao_acidente, com um único registro, já recuperado a partir das colunas de desfecho "
                "(Seção 3.1). Nenhum dos atributos numéricos de modelagem - km, veículos e pessoas - tem valores "
                "ausentes, pois a vírgula decimal do arquivo original foi convertida corretamente para ponto "
                "antes da conversão para número.",
                styles,
            ),
            _figure(
                "valores_ausentes.png",
                "Figura 2 - Quantidade de valores ausentes por atributo no arquivo bruto.",
            ),
            Paragraph("4.1.2 Distribuições e valores discrepantes", styles["heading2"]),
            _paragraph(
                "Na Figura 3, hora e quilômetro estão em escala linear, enquanto veículos e pessoas foram "
                "colocados em escala logarítmica no eixo vertical: em escala linear, mais de 90% dos acidentes "
                "concentrados em 1 a 3 veículos ou pessoas escondiam por completo a cauda longa desses dois "
                "atributos. A mediana do horário é 13h, com maior concentração de acidentes no início da manhã e "
                "no fim da tarde. O quilômetro é assimétrico à direita, com mediana de 193 km e máximo de "
                "1.260 km. Em veículos e pessoas, as medianas são 2 e 2, respectivamente, mas a escala "
                "logarítmica revela acidentes raros com até 18 veículos e 88 pessoas envolvidas, que devem ser "
                "avaliados no contexto do domínio antes de qualquer remoção.",
                styles,
            ),
            _figure(
                "distribuicoes_numericas.png",
                "Figura 3 - Histogramas das variáveis numéricas utilizadas na análise exploratória "
                "(veículos e pessoas em escala logarítmica).",
            ),
            _paragraph(
                "Na Figura 4, veículos e pessoas também estão em escala logarítmica para que a caixa e a mediana "
                "de cada classe permaneçam visíveis apesar dos valores extremos. A classe Com Vítimas Fatais "
                "apresenta mediana de 3 pessoas envolvidas, acima da mediana de 2 das demais classes; a mediana "
                "de veículos é 2 nas três classes. Esse padrão não prova causalidade, mas indica uma relação que "
                "merece investigação nos modelos posteriores.",
                styles,
            ),
            _figure(
                "boxplots_por_classe.png",
                "Figura 4 - Boxplots de km, veículos e pessoas por classe de gravidade "
                "(veículos e pessoas em escala logarítmica).",
            ),
            PageBreak(),
            Paragraph("4.1.3 Relações entre atributos numéricos", styles["heading2"]),
            _paragraph(
                "Na Figura 5, a correlação de Pearson mais relevante aparece entre número de veículos e número de "
                "pessoas envolvidas (r = 0,42), uma associação moderada e esperada - acidentes com mais veículos "
                "tendem a envolver mais pessoas. As demais correlações ficam próximas de zero, o que sugere pouca "
                "relação linear entre hora, quilômetro e essas duas contagens. Isso não elimina a possibilidade de "
                "relações não lineares ou interações com atributos categóricos.",
                styles,
            ),
            _figure(
                "correlacao_numericas.png",
                "Figura 5 - Matriz de correlação de Pearson entre os atributos numéricos de modelagem.",
            ),
            _paragraph(
                "A Figura 6 substitui o gráfico de dispersão único por um histograma 2D de densidade por classe, "
                "com uma célula por valor inteiro de pessoas, pois a sobreposição de mais de 33 mil pontos "
                "coloridos escondia qualquer padrão. Cada painel usa sua própria escala de cor, já que as classes "
                "têm tamanhos muito diferentes (de 2.467 a 26.032 acidentes); o eixo de pessoas foi limitado a "
                "10, faixa que cobre 99,4% dos registros. Na Figura "
                "6, a classe Sem Vítimas concentra-se fortemente em acidentes com apenas 1 pessoa envolvida, "
                "enquanto Com Vítimas Feridas e, principalmente, Com Vítimas Fatais têm peso relativo maior em 2 "
                "e 3 pessoas - compatível com a mediana de 3 pessoas da classe fatal observada na Figura 4. Em "
                "nenhuma das três classes há concentração específica por trecho de rodovia (eixo horizontal), o "
                "que sugere que o quilômetro isolado não separa bem as classes e reforça a necessidade de "
                "combinar atributos de contexto, via e acidente nos futuros classificadores.",
                styles,
            ),
            _figure(
                "dispersao_km_pessoas.png",
                "Figura 6 - Densidade de acidentes por quilômetro e pessoas envolvidas, por classe "
                "(escala de cor própria de cada painel; eixo de pessoas limitado a 10).",
            ),
            Paragraph("4.1.4 Padrões temporais", styles["heading2"]),
            _paragraph(
                "Na Figura 7, a maior parte dos registros ocorreu em pleno dia (18.793; 55,78%), seguida por "
                "plena noite (11.436; 33,94%); amanhecer e anoitecer somam juntos pouco mais de 10% dos casos. "
                "Em números absolutos, as ocorrências fatais também se concentram nesses dois períodos maiores, "
                "mas, em taxa relativa dentro de cada fase, os acidentes fatais são proporcionalmente mais "
                "comuns no amanhecer (11,86% dos casos daquele período) e na plena noite (10,47%) do que no "
                "pleno dia (5,04%) ou no anoitecer (6,95%) - ou seja, embora menos frequentes, os acidentes de "
                "madrugada e à noite têm maior chance relativa de serem fatais.",
                styles,
            ),
            _figure(
                "fase_dia_por_classe.png",
                "Figura 7 - Quantidade de acidentes por fase do dia e classe de gravidade.",
            ),
            _paragraph(
                "Na Figura 8, domingo apresentou o maior número de acidentes (5.326), seguido de perto por "
                "sábado (5.237) e sexta-feira (5.231); terça-feira teve a menor contagem (4.227). O padrão "
                "sugere maior volume de acidentes do meio para o fim de semana, mas essa observação deve ser "
                "interpretada junto à exposição ao tráfego, que não está disponível na base.",
                styles,
            ),
            _figure(
                "acidentes_por_dia_semana.png",
                "Figura 8 - Quantidade de acidentes por dia da semana.",
            ),
            Paragraph("4.1.5 Gravidade por tipo de acidente", styles["heading2"]),
            _paragraph(
                "Os atributos numéricos de modelagem quase não se correlacionam com a gravidade (Figura 5), o que "
                "levanta a pergunta se um atributo categórico carrega mais sinal. Na Figura 9, os oito tipos de "
                "acidente mais frequentes - que juntos cobrem a maior parte da base - são ordenados pela taxa de "
                "acidentes fatais. A colisão frontal se destaca isoladamente: 30,6% dos seus casos são fatais, "
                "contra apenas 3,0% a 5,7% nos demais sete tipos. Esse salto é muito maior do que qualquer relação "
                "encontrada entre as variáveis numéricas, e reforça a conclusão da Seção 4.1.3 de que combinar "
                "atributos categóricos de contexto do acidente deve ser prioridade nos próximos modelos.",
                styles,
            ),
            _figure(
                "gravidade_por_tipo_acidente.png",
                "Figura 9 - Taxa de gravidade dentro dos oito tipos de acidente mais frequentes, "
                "ordenados pela taxa de acidentes fatais.",
            ),
            Paragraph("4.1.6 Síntese da análise exploratória", styles["heading2"]),
            _paragraph(
                "A base apresenta volume suficiente e variedade de atributos para o problema de classificação "
                "proposto. O principal achado desta etapa é que atributos categóricos de contexto - como o tipo "
                "do acidente - carregam muito mais sinal sobre a gravidade do que os atributos numéricos "
                "isolados. As principais decisões para a próxima etapa são: preservar o tratamento de leakage, "
                "usar métricas adequadas ao desbalanceamento das classes, manter os valores extremos para "
                "avaliação criteriosa e testar modelos capazes de combinar atributos numéricos, categóricos e "
                "temporais.",
                styles,
            ),
            Paragraph("4.2 a 4.5 Resultados dos modelos e comitês", styles["heading2"]),
            Paragraph(
                "Seções reservadas para as sprints de experimentação com algoritmos individuais, comitês homogêneos e heterogêneos.",
                styles["reserved"],
            ),
            Paragraph("5 Conclusão", styles["heading1"]),
            Paragraph(
                "Seção reservada para a versão final do projeto.",
                styles["reserved"],
            ),
            Paragraph("Referências", styles["heading1"]),
            _paragraph(
                "POLÍCIA RODOVIÁRIA FEDERAL. Dados abertos da PRF. Disponível em: "
                "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf. "
                "Acesso em: 30 set. 2026.",
                styles,
            ),
            _paragraph(
                "BASE DATATRAN 2026. Arquivo disponibilizado pela Polícia Rodoviária Federal. "
                "Recorte utilizado: acidentes registrados de janeiro a julho de 2026.",
                styles,
            ),
            _paragraph(
                "SCHOLZ, J. C. W.; PINHEIRO, Y. P. Prevendo a gravidade de acidentes rodoviários no Brasil: a "
                "influência do ambiente e características do veículo. 2023. Trabalho de Conclusão de Curso "
                "(Graduação em Engenharia de Computação) - Universidade Tecnológica Federal do Paraná. "
                "Orientador: Thiago Henrique da Silva.",
                styles,
            ),
            _paragraph(
                "MAFORT, E. V.; KAPPEL, M. A. A. Técnicas de Aprendizado de Máquina para Predição de Gravidade "
                "de Acidentes em Rodovias do Estado do Rio de Janeiro. Revista Eletrônica de Iniciação "
                "Científica em Computação, v. 23, n. 1, 2025. DOI: 10.5753/reic.2025.6274.",
                styles,
            ),
            _paragraph(
                "MICCI-BARRECA, D. A preprocessing scheme for high-cardinality categorical attributes in "
                "classification and prediction problems. SIGKDD Explorations Newsletter, v. 3, n. 1, p. 27-32, "
                "2001. DOI: 10.1145/507533.507538.",
                styles,
            ),
        ]
    )

    document.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return OUTPUT


if __name__ == "__main__":
    report = build_report()
    print(f"Relatório gerado em: {report}")
