"""Gera uma cópia do relatório da Sprint 1 no formato do modelo da disciplina."""

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
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = ROOT / "docs" / "artigo" / "relatorio_sprint_1_formato_modelo.pdf"
FIGURES = ROOT / "results" / "figures"


def styles() -> dict[str, ParagraphStyle]:
    """Reproduz a tipografia, margens e hierarquia visual do modelo acadêmico."""

    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ModelTitle",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=16,
            leading=19,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "authors": ParagraphStyle(
            "ModelAuthors",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=13,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "abstract_title": ParagraphStyle(
            "AbstractTitle",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
            spaceBefore=13,
            spaceAfter=4,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=11.5,
            alignment=TA_JUSTIFY,
            leftIndent=0.75 * cm,
            rightIndent=0.75 * cm,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=13.2,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "h1": ParagraphStyle(
            "HeadingOne",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=15,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "HeadingTwo",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=12.5,
            leading=15,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            spaceBefore=2,
            spaceAfter=9,
        ),
        "reserved": ParagraphStyle(
            "Reserved",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=10.5,
            leading=13.2,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=13.2,
            leftIndent=0.7 * cm,
            firstLineIndent=-0.45 * cm,
            spaceAfter=2,
        ),
        "table_header": ParagraphStyle(
            "ModelTableHeader",
            parent=base["BodyText"],
            fontName="Times-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "ModelTableCell",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=9,
            leading=11.2,
            alignment=TA_CENTER,
        ),
        "table_cell_left": ParagraphStyle(
            "ModelTableCellLeft",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=9,
            leading=11.2,
        ),
    }


def p(text: str, s: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, s["body"])


def bullet(text: str, s: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"• {text}", s["bullet"])


def model_table(data: list[list[str]], column_widths: list[float]) -> Table:
    """Tabela no mesmo espírito tipográfico do modelo (Times, cabeçalho escuro).

    Células de texto puro não quebram linha no reportlab e podem vazar para
    fora da coluna quando o conteúdo é longo, então cada célula vira um
    Paragraph para garantir a quebra automática dentro da largura da coluna.
    """

    s = styles()
    wrapped = [[Paragraph(str(cell), s["table_header"]) for cell in data[0]]]
    for row in data[1:]:
        wrapped.append(
            [
                Paragraph(str(cell), s["table_cell_left"] if column == 0 else s["table_cell"])
                for column, cell in enumerate(row)
            ]
        )
    table = Table(wrapped, colWidths=column_widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2b2b")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def figure(filename: str, caption: str) -> KeepTogether:
    """Insere figura da EDA com legenda no padrão simples do modelo."""

    image_path = FIGURES / filename
    if not image_path.exists():
        raise FileNotFoundError(
            f"Figura não encontrada: {image_path}. Execute 'python scripts/run_eda.py'."
        )
    # A segunda instância recebe as dimensões no construtor: assim a largura
    # nativa do PNG não substitui a largura definida para a coluna do artigo.
    source_image = Image(str(image_path))
    width = 14.3 * cm
    ratio = source_image.imageHeight / source_image.imageWidth
    image = Image(str(image_path), width=width, height=width * ratio)
    s = styles()
    return KeepTogether([image, Paragraph(caption, s["caption"])])


def page_number(canvas, document) -> None:
    """Coloca apenas a numeração central inferior, como no PDF modelo."""

    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, str(document.page))
    canvas.restoreState()


def build_report() -> Path:
    s = styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.65 * cm,
        rightMargin=2.65 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.65 * cm,
        title="Predição da gravidade de acidentes em rodovias federais",
        author="Daniel Felix; Davi Klein; Josué Castro; Maximus Ulisses Magalhães",
    )
    story = []

    # Topo da primeira página no mesmo estilo: título, subtítulo e autores sem capa.
    story.extend(
        [
            Paragraph(
                "Predição da gravidade de acidentes em rodovias federais<br/>"
                "<font name='Times-Roman' size='11'>Sprint 1 - Análise Exploratória dos Dados</font>",
                s["title"],
            ),
            Paragraph("Daniel Felix &nbsp;&nbsp;&nbsp; Davi Klein", s["authors"]),
            Paragraph("Josué Castro &nbsp;&nbsp;&nbsp; Maximus Ulisses Magalhães", s["authors"]),
            Paragraph("Abstract", s["abstract_title"]),
            Paragraph(
                "Este trabalho apresenta a análise inicial da base DataTran 2026, composta por registros de acidentes "
                "em rodovias federais brasileiras. O objetivo do projeto é classificar a gravidade da ocorrência em três "
                "categorias: sem vítimas, com vítimas feridas e com vítimas fatais, utilizando somente informações "
                "disponíveis no momento do acidente. Nesta Sprint 1, foram descritas a origem, a estrutura e a qualidade "
                "da base, além de uma análise exploratória com distribuições, valores ausentes, gráficos numéricos, "
                "boxplots, correlação e padrões temporais. Os achados estabelecem a base para os experimentos com "
                "algoritmos individuais e comitês nas sprints seguintes.",
                s["abstract"],
            ),
            Paragraph(
                "<b>Palavras-chave:</b> aprendizado de máquina; análise de dados; classificação; acidentes rodoviários; PRF.",
                s["abstract"],
            ),
            Paragraph("1 &nbsp;&nbsp; Introdução", s["h1"]),
            Paragraph(
                "Esta seção será desenvolvida nas próximas sprints. O estudo investiga a predição da gravidade de acidentes "
                "em rodovias federais brasileiras a partir de informações conhecidas no momento da ocorrência.",
                s["reserved"],
            ),
            Paragraph("2 &nbsp;&nbsp; Background e Trabalhos Relacionados", s["h1"]),
            Paragraph(
                "As subseções a seguir ficam reservadas para a fundamentação teórica e a revisão de literatura da versão final.",
                s["reserved"],
            ),
        ]
    )
    for number, heading in [
        ("2.1", "Aprendizado de Máquina"),
        ("2.2", "Classificação"),
        ("2.3", "Algoritmos de Aprendizado de Máquina"),
        ("2.4", "Aprendizado por Comitês"),
        ("2.5", "Comitês Homogêneos"),
        ("2.6", "Comitês Heterogêneos"),
    ]:
        story.extend(
            [
                Paragraph(f"{number} &nbsp;&nbsp; {heading}", s["h2"]),
                Paragraph("Conteúdo reservado para desenvolvimento nas próximas sprints.", s["reserved"]),
            ]
        )

    story.extend(
        [
            Paragraph("2.7 &nbsp;&nbsp; Trabalhos Relacionados", s["h2"]),
            p(
                "<b>Scholz e Pinheiro (2023)</b> investigaram a influência de atributos do ambiente e do veículo "
                "na gravidade de acidentes em rodovias federais brasileiras, com dados da PRF de 2017 a 2022 "
                "(862.465 registros após limpeza). O trabalho busca prever se um acidente é grave ou leve, a "
                "partir do estado físico da vítima; a unidade de análise é a pessoa envolvida, não o acidente, e "
                "o alvo é binário, diferente das três classes originais deste projeto. As variáveis foram "
                "testadas em três cenários incrementais: atributos gerais (dia da semana, horário, idade, sexo), "
                "de ambiente (condição meteorológica, tipo de pista, região) e de veículo (tipo, marca, ano de "
                "fabricação, preço obtido via tabela FIPE). Cinco algoritmos foram comparados (Árvore de Decisão, "
                "Random Forest, Naive Bayes, MLP e kNN); o cenário com atributos de veículo teve o melhor "
                "desempenho, com o Naive Bayes alcançando o maior F1-score (61%), superando o Random Forest "
                "mesmo este tendo acurácia nominal maior (86%) - os autores alertam que a acurácia isolada "
                "engana dado o desbalanceamento das classes (85,68% leve, 14,31% grave), ressalva também "
                "adotada neste relatório (Seção 4.1.1). A semelhança com este projeto está na fonte dos dados "
                "(PRF); a diferença, além da unidade de análise (pessoa, não acidente) e da granularidade "
                "binária do alvo, também aparece no tratamento de causa_acidente: Scholz e Pinheiro a excluem "
                "por vazamento, enquanto aqui ela entra como atributo via TargetEncoder (Seção 3.2) - um ponto "
                "que merece revisão, já que a causa também só é apurada pela PRF depois do acidente.",
                s,
            ),
            p(
                "<b>Mafort e Kappel (2025)</b> publicaram recentemente um modelo de gravidade de acidentes nas "
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
                s,
            ),
        ]
    )

    story.extend(
        [
            Paragraph("3 &nbsp;&nbsp; Protocolo Experimental", s["h1"]),
            p(
                "Esta seção descreve os procedimentos adotados nesta primeira etapa, permitindo que a análise exploratória "
                "seja reproduzida pela equipe.",
                s,
            ),
            Paragraph("3.1 &nbsp;&nbsp; Base de Dados", s["h2"]),
            p(
                "A base utilizada é a DataTran 2026, disponibilizada pela Polícia Rodoviária Federal (PRF) em seu portal "
                "de dados abertos. Ela registra acidentes ocorridos em rodovias federais brasileiras.",
                s,
            ),
            p(
                "O recorte contém 33.694 instâncias e 30 atributos, referentes ao período de 1º de janeiro a 31 de julho "
                "de 2026. A tarefa é de classificação multiclasse, cuja variável-alvo é classificacao_acidente.",
                s,
            ),
            bullet("Formato: CSV com separador ponto e vírgula e codificação cp1252.", s),
            bullet("Classes: Sem Vítimas; Com Vítimas Feridas; Com Vítimas Fatais.", s),
            bullet(
                "Atributos categóricos, numéricos, temporais e geográficos, além de identificador, variável-alvo, "
                "colunas de desfecho e colunas administrativas não usadas na modelagem (Tabela 1).",
                s,
            ),
            bullet(
                "Atributos numéricos relevantes: quilômetro, número de veículos e número de pessoas (3 atributos, "
                "além da hora derivada do horário).",
                s,
            ),
            bullet(
                "Um rótulo ausente, de um total de 33.694 registros, preenchido somente para consistência a partir "
                "de colunas de desfecho.",
                s,
            ),
            bullet(
                "Ausências adicionais, em colunas administrativas não usadas na modelagem: regional (3.105), "
                "delegacia (3.111) e uop (3.119); não foram encontradas linhas duplicadas.",
                s,
            ),
            p(
                "As colunas de desfecho mortos, feridos, feridos_leves, feridos_graves, ilesos e ignorados não são usadas "
                "como entrada dos modelos. Essa decisão evita vazamento de dados, pois essas informações só se tornam "
                "conhecidas após a ocorrência.",
                s,
            ),
            Spacer(1, 0.2 * cm),
            KeepTogether(
                [
                    model_table(
                        [
                            ["Tipo de atributo", "Qtd.", "Exemplos"],
                            ["Categóricos (entrada do modelo)", "9", "dia_semana, causa_acidente, tipo_acidente, "
                             "fase_dia, condicao_metereologica, tipo_pista, tracado_via, uso_solo, br"],
                            ["Numéricos (entrada do modelo)", "3", "km, veiculos, pessoas (mais a hora, derivada do horario)"],
                            ["Temporais", "2", "data_inversa, horario"],
                            ["Geográficos", "4", "uf, municipio, latitude, longitude"],
                            ["Identificador", "1", "id"],
                            ["Variável-alvo", "1", "classificacao_acidente"],
                            ["Desfecho (excluídos da modelagem)", "6", "mortos, feridos, feridos_leves, feridos_graves, ilesos, ignorados"],
                            ["Administrativos (não utilizados)", "4", "sentido_via, regional, delegacia, uop"],
                        ],
                        [4.2 * cm, 1.2 * cm, 8.9 * cm],
                    ),
                    Paragraph("Tabela 1. Tipos de atributos da base bruta (30 colunas no total).", s["caption"]),
                ]
            ),
        ]
    )
    story.extend(
        [
            Paragraph("3.2 &nbsp;&nbsp; Pré-processamento", s["h2"]),
            p(
                "O pré-processamento ocorre em duas etapas. A primeira, fora do pipeline de aprendizado, normaliza "
                "o arquivo bruto antes de qualquer ajuste de modelo: horario é convertido em hora inteira (0 a "
                "23), km/veiculos/pessoas têm a vírgula decimal convertida para ponto, e tracado_via é "
                "decomposta em colunas binárias (detalhado adiante). A segunda etapa roda dentro de um Pipeline "
                "do scikit-learn, treinado apenas sobre a partição de treino, para que nenhuma estatística do "
                "teste (moda, mediana, categorias ou médias do alvo) influencie o ajuste.",
                s,
            ),
            Spacer(1, 0.2 * cm),
            KeepTogether(
                [
                    model_table(
                        [
                            ["Grupo de atributos", "Etapas de pré-processamento"],
                            ["Categóricos de baixa cardinalidade (6 colunas)", "Imputação pela moda seguida de "
                             "codificação one-hot; categorias não vistas no treino são ignoradas no teste."],
                            ["Categóricos de alta cardinalidade (causa_acidente: 69 cat.; br: 110 cat.)",
                             "Imputação pela moda seguida de codificação pela média do alvo (TargetEncoder, "
                             "ajustada só no treino)."],
                            ["tracado_via (1 coluna bruta, 432 combinações distintas)", "Decomposta em 12 colunas "
                             "binárias, uma por característica física da via."],
                            ["Numéricos (hora, km, veículos, pessoas + 12 colunas de tracado_via)", "Imputação "
                             "pela mediana seguida de padronização (z-score: média 0 e desvio padrão 1)."],
                            ["Demais colunas (id, datas, desfecho, administrativas, geográficas)", "Descartadas "
                             "pelo ColumnTransformer (remainder=\"drop\"); nunca chegam ao classificador."],
                        ],
                        [4.0 * cm, 10.3 * cm],
                    ),
                    Paragraph(
                        "Tabela 2. Pré-processamento aplicado por grupo de atributos, dentro do Pipeline do scikit-learn.",
                        s["caption"],
                    ),
                ]
            ),
            p(
                "A coluna tracado_via chega como combinações livres separadas por ponto e vírgula (por exemplo, "
                "\"Aclive;Reta\"), com 432 valores distintos nas 33.694 linhas e 200 deles aparecendo uma única "
                "vez; \"Aclive;Reta\" e \"Reta;Aclive\" seriam tratadas como categorias diferentes em one-hot "
                "apesar de descreverem o mesmo trecho. Por isso, cada uma das 12 características identificadas "
                "(reta, curva, aclive, declive, interseção de vias, retorno regulamentado, rotatória, obras, "
                "viaduto, ponte, desvio temporário, túnel) vira uma coluna binária própria. causa_acidente (69 "
                "categorias) e br (110 categorias) têm o mesmo problema de cardinalidade; em vez de one-hot, "
                "cada categoria é substituída pela taxa média do alvo dentro dela (TargetEncoder, de "
                "Micci-Barreca, 2001), calculada apenas no treino - a mesma técnica usada por Scholz e Pinheiro "
                "(2023) para marca, tipo de veículo e região (Seção 2.7).",
                s,
            ),
            p(
                "Manter causa_acidente como atributo é uma escolha que precisa ser revisitada: tanto Scholz e "
                "Pinheiro (2023) quanto Mafort e Kappel (2025) a excluem, já que a causa só é apurada pela PRF "
                "depois da ocorrência, o que a aproxima das colunas de desfecho em termos de disponibilidade "
                "temporal (Seção 2.7). Por ora optamos por mantê-la, dado o ganho de sinal observado na EDA "
                "(Seção 4.1.5), mas um teste comparativo com e sem essa coluna deve entrar nas próximas sprints.",
                s,
            ),
            p(
                "Para o desbalanceamento das classes (Figura 1), testamos três estratégias na mesma regressão "
                "logística: peso balanceado por classe (class_weight=\"balanced\"), sobreamostragem sintética da "
                "classe minoritária (SMOTE) e SMOTE combinado à limpeza de vizinhos ambíguos (SMOTEENN). Os "
                "resultados não favoreceram a reamostragem nesta baseline linear: class_weight obteve F1 macro de "
                "0,480, SMOTE ficou praticamente empatado (0,480), e SMOTEENN piorou bastante (0,374), pois a "
                "limpeza de vizinhos removeu exemplos das classes majoritárias e derrubou a precisão geral. Por "
                "isso, a baseline atual mantém class_weight=\"balanced\"; a comparação deve ser refeita quando "
                "algoritmos de árvore entrarem na Seção 3.4.",
                s,
            ),
            p(
                "Essa estrutura (ColumnTransformer com um sub-pipeline por grupo de atributo, dentro de um "
                "Pipeline maior com o classificador) deve se manter nas próximas sprints: o passo \"resample\" "
                "já está pronto para receber SMOTE ou SMOTEENN (de imblearn), e a etapa \"classifier\" pode ser "
                "trocada por outros algoritmos individuais e comitês, sem reescrever a imputação ou a "
                "codificação. O código está em src/modeling.py (build_baseline_pipeline) e "
                "src/data_pipeline.py (prepare_modeling_data), executado por scripts/run_eda.py.",
                s,
            ),
        ]
    )
    for number, heading, description in [
        ("3.3", "Divisão dos Dados", "Seção reservada para a definição de treinamento, validação, teste e validação cruzada."),
        ("3.4", "Algoritmos Individuais", "Seção reservada para os algoritmos e hiperparâmetros avaliados."),
        ("3.5", "Comitês Homogêneos", "Seção reservada para métodos compostos por modelos de uma mesma família."),
        ("3.6", "Comitês Heterogêneos", "Seção reservada para a combinação de algoritmos diferentes."),
        ("3.7", "Métricas de Avaliação", "Seção reservada para as métricas e a justificativa de sua adequação ao problema."),
        ("3.8", "Configuração Experimental", "Seção reservada para ambiente, bibliotecas, sementes e demais condições dos experimentos."),
    ]:
        story.extend([Paragraph(f"{number} &nbsp;&nbsp; {heading}", s["h2"]), Paragraph(description, s["reserved"])])

    story.extend(
        [
            Paragraph("4 &nbsp;&nbsp; Resultados", s["h1"]),
            p("Esta seção apresenta os resultados da análise exploratória e suas interpretações.", s),
            Paragraph("4.1 &nbsp;&nbsp; Parte 1 - Análise Exploratória dos Dados", s["h2"]),
            Paragraph("4.1.1 &nbsp;&nbsp; Qualidade dos dados e distribuição das classes", s["h2"]),
            p(
                "Na Figura 1, a classe Com Vítimas Feridas concentra 26.032 registros (77,26%), seguida por Sem "
                "Vítimas com 5.195 (15,42%) e Com Vítimas Fatais com 2.467 (7,32%). O problema é desbalanceado, "
                "com a classe de maior interesse prático sendo também a mais rara; por isso, as próximas etapas "
                "devem avaliar métricas macro além da acurácia isolada.",
                s,
            ),
            figure("distribuicao_classes.png", "Figura 1: Distribuição da variável-alvo após a validação do rótulo."),
            p(
                "Na Figura 2, as ausências aparecem concentradas em três colunas administrativas - regional, "
                "delegacia e uop -, cada uma com cerca de 9% de registros em branco; nenhuma delas integra o "
                "conjunto de atributos de modelagem. A quarta coluna com ausência é a própria "
                "classificacao_acidente (1 registro), já recuperada a partir das colunas de desfecho. Não há "
                "valores ausentes em km, veículos ou pessoas após a conversão correta dos campos numéricos.",
                s,
            ),
            figure("valores_ausentes.png", "Figura 2: Quantidade de valores ausentes por atributo no arquivo bruto."),
            Paragraph("4.1.2 &nbsp;&nbsp; Distribuições e valores discrepantes", s["h2"]),
            p(
                "Na Figura 3, veículos e pessoas estão em escala logarítmica no eixo vertical, pois mais de 90% dos "
                "acidentes concentrados em 1 a 3 unidades escondiam a cauda longa desses atributos em escala "
                "linear. A mediana do horário é 13h. O quilômetro é assimétrico à direita: mediana de 193 km e "
                "máximo de 1.260 km. As medianas de veículos e pessoas são 2, enquanto a escala logarítmica revela "
                "ocorrências raras com até 18 veículos e 88 pessoas, que devem ser avaliadas no contexto do "
                "domínio antes de qualquer remoção.",
                s,
            ),
            figure(
                "distribuicoes_numericas.png",
                "Figura 3: Histogramas das variáveis numéricas (veículos e pessoas em escala logarítmica).",
            ),
            p(
                "Na Figura 4, veículos e pessoas também estão em escala logarítmica para manter caixa e mediana "
                "visíveis apesar dos valores extremos. A classe Com Vítimas Fatais apresenta mediana de 3 pessoas, "
                "enquanto as demais têm mediana de 2; é um indício a ser investigado posteriormente, não uma "
                "relação causal.",
                s,
            ),
            figure(
                "boxplots_por_classe.png",
                "Figura 4: Boxplots de km, veículos e pessoas por classe de gravidade (veículos e pessoas em escala logarítmica).",
            ),
            Paragraph("4.1.3 &nbsp;&nbsp; Relações entre atributos numéricos", s["h2"]),
            p(
                "Na Figura 5, a correlação de Pearson mais relevante ocorre entre número de veículos e número de "
                "pessoas envolvidas (r = 0,42), associação moderada e esperada. As demais correlações ficam "
                "próximas de zero, sugerindo pouca relação linear entre horário, quilômetro e as contagens.",
                s,
            ),
            figure("correlacao_numericas.png", "Figura 5: Matriz de correlação de Pearson dos atributos numéricos."),
            p(
                "A Figura 6 substitui o antigo gráfico de dispersão único por um histograma 2D de densidade por "
                "classe, com uma célula por valor inteiro de pessoas, pois a sobreposição de mais de 33 mil "
                "pontos coloridos escondia qualquer padrão; cada painel usa sua própria escala de cor, já que as "
                "classes têm tamanhos muito diferentes. Na Figura 6, a classe "
                "Sem Vítimas concentra-se fortemente em acidentes com 1 pessoa envolvida, enquanto Com Vítimas "
                "Feridas e, principalmente, Com Vítimas Fatais têm peso relativo maior em 2 e 3 pessoas. Em "
                "nenhuma das três classes há concentração específica por trecho de rodovia, o que sugere que o "
                "quilômetro isolado não separa bem as classes, justificando a combinação de informações de "
                "contexto, via e acidente nos classificadores futuros.",
                s,
            ),
            figure(
                "dispersao_km_pessoas.png",
                "Figura 6: Densidade de acidentes por quilômetro e pessoas envolvidas, por classe "
                "(escala de cor própria de cada painel; eixo de pessoas limitado a 10).",
            ),
            Paragraph("4.1.4 &nbsp;&nbsp; Padrões temporais", s["h2"]),
            p(
                "Na Figura 7, a maior parte dos registros ocorreu em pleno dia (18.793; 55,78%), seguida por "
                "plena noite (11.436; 33,94%). Em valores absolutos as ocorrências fatais também se concentram "
                "nesses dois períodos, mas, em taxa relativa dentro de cada fase, elas são proporcionalmente mais "
                "comuns no amanhecer (11,86%) e na plena noite (10,47%) do que no pleno dia (5,04%) ou no "
                "anoitecer (6,95%).",
                s,
            ),
            figure("fase_dia_por_classe.png", "Figura 7: Quantidade de acidentes por fase do dia e classe de gravidade."),
            p(
                "Na Figura 8, domingo apresenta o maior número de acidentes (5.326), seguido de perto por sábado "
                "(5.237) e sexta-feira (5.231). Terça-feira possui a menor contagem (4.227). O padrão sugere maior "
                "volume próximo ao fim de semana, mas a base não contém a exposição ao tráfego necessária para "
                "conclusões causais.",
                s,
            ),
            figure("acidentes_por_dia_semana.png", "Figura 8: Quantidade de acidentes por dia da semana."),
            Paragraph("4.1.5 &nbsp;&nbsp; Gravidade por tipo de acidente", s["h2"]),
            p(
                "Os atributos numéricos de modelagem quase não se correlacionam com a gravidade (Figura 5), o "
                "que levanta a pergunta se um atributo categórico carrega mais sinal. Na Figura 9, os oito tipos "
                "de acidente mais frequentes são ordenados pela taxa de acidentes fatais. A colisão frontal se "
                "destaca isoladamente: 30,6% dos seus casos são fatais, contra apenas 3,0% a 5,7% nos demais "
                "sete tipos. Esse salto é muito maior do que qualquer relação encontrada entre as variáveis "
                "numéricas, reforçando que combinar atributos categóricos de contexto do acidente deve ser "
                "prioridade nos próximos modelos.",
                s,
            ),
            figure(
                "gravidade_por_tipo_acidente.png",
                "Figura 9: Taxa de gravidade dentro dos oito tipos de acidente mais frequentes, "
                "ordenados pela taxa de acidentes fatais.",
            ),
            Paragraph("4.1.6 &nbsp;&nbsp; Síntese da análise exploratória", s["h2"]),
            p(
                "A base apresenta volume e variedade de atributos adequados ao problema. O principal achado desta "
                "etapa é que atributos categóricos de contexto - como o tipo do acidente - carregam muito mais "
                "sinal sobre a gravidade do que os atributos numéricos isolados. Para as próximas etapas, devem "
                "ser preservados o controle de vazamento de dados, o uso de métricas adequadas ao "
                "desbalanceamento e a avaliação criteriosa de valores extremos.",
                s,
            ),
        ]
    )
    for number, heading in [
        ("4.2", "Parte 2 - Algoritmos Individuais"),
        ("4.3", "Parte 3 - Comitês Homogêneos"),
        ("4.4", "Parte 4 - Comitês Heterogêneos"),
        ("4.5", "Comparação Geral dos Resultados"),
    ]:
        story.extend(
            [
                Paragraph(f"{number} &nbsp;&nbsp; {heading}", s["h2"]),
                Paragraph("Seção reservada para desenvolvimento nas próximas sprints.", s["reserved"]),
            ]
        )
    story.extend(
        [
            Paragraph("5 &nbsp;&nbsp; Conclusão", s["h1"]),
            Paragraph("Seção reservada para a versão final do projeto.", s["reserved"]),
            Paragraph("References", s["h1"]),
            p(
                "POLÍCIA RODOVIÁRIA FEDERAL. Dados abertos da PRF. Disponível em: "
                "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf. Acesso em: 30 set. 2026.",
                s,
            ),
            p(
                "BASE DATATRAN 2026. Arquivo disponibilizado pela Polícia Rodoviária Federal. "
                "Recorte utilizado: acidentes registrados de janeiro a julho de 2026.",
                s,
            ),
            p(
                "SCHOLZ, J. C. W.; PINHEIRO, Y. P. Prevendo a gravidade de acidentes rodoviários no Brasil: a "
                "influência do ambiente e características do veículo. 2023. Trabalho de Conclusão de Curso "
                "(Graduação em Engenharia de Computação) - Universidade Tecnológica Federal do Paraná. "
                "Orientador: Thiago Henrique da Silva.",
                s,
            ),
            p(
                "MAFORT, E. V.; KAPPEL, M. A. A. Técnicas de Aprendizado de Máquina para Predição de Gravidade "
                "de Acidentes em Rodovias do Estado do Rio de Janeiro. Revista Eletrônica de Iniciação "
                "Científica em Computação, v. 23, n. 1, 2025. DOI: 10.5753/reic.2025.6274.",
                s,
            ),
            p(
                "MICCI-BARRECA, D. A preprocessing scheme for high-cardinality categorical attributes in "
                "classification and prediction problems. SIGKDD Explorations Newsletter, v. 3, n. 1, p. 27-32, "
                "2001. DOI: 10.1145/507533.507538.",
                s,
            ),
        ]
    )
    document.build(story, onFirstPage=page_number, onLaterPages=page_number)
    return OUTPUT


if __name__ == "__main__":
    report = build_report()
    print(f"Relatório gerado em: {report}")
