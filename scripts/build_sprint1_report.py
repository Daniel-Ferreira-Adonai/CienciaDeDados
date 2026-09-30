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
    table = Table(data, colWidths=column_widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f4c5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
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
            Paragraph("Relatório técnico - Sprint 1", styles["subtitle"]),
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
            Paragraph("2 Background e Trabalhos Relacionados", styles["heading1"]),
            Paragraph(
                "Seção reservada para as próximas sprints. A revisão da literatura e a fundamentação teórica serão "
                "incluídas antes da entrega final.",
                styles["reserved"],
            ),
            Paragraph("3 Protocolo Experimental", styles["heading1"]),
            Paragraph("3.1 Base de Dados", styles["heading2"]),
            _paragraph(
                "A base utilizada é a DataTran 2026, disponibilizada pela Polícia Rodoviária Federal (PRF) em seu "
                "portal de dados abertos e compartilhada com a equipe por meio de um link do Google Drive. Ela contém "
                "registros de acidentes em rodovias federais e permite estudar características do evento, da via e do "
                "contexto em que o acidente ocorreu.",
                styles,
            ),
            _paragraph(
                "O recorte analisado contém 42.322 instâncias e 30 atributos, referentes ao período de 1º de janeiro "
                "a 31 de julho de 2026. Os atributos incluem identificadores, data e horário, localização, características "
                "da rodovia, condições do acidente, pessoas e veículos envolvidos, além da classificação do acidente.",
                styles,
            ),
        ]
    )

    profile_data = [
        ["Característica", "Descrição"],
        ["Formato", "CSV com separador ponto e vírgula e codificação cp1252"],
        ["Instâncias", "42.322 acidentes"],
        ["Atributos", "30 colunas no arquivo bruto"],
        ["Período", "01/01/2026 a 31/07/2026"],
        ["Tarefa", "Classificação multiclasse"],
        ["Variável-alvo", "classificacao_acidente"],
        ["Classes", "Sem Vítimas; Com Vítimas Feridas; Com Vítimas Fatais"],
    ]
    story.extend(
        [
            _table(profile_data, [4.1 * cm, 12.1 * cm]),
            Spacer(1, 0.25 * cm),
            Paragraph("Tabela 1 - Perfil da base selecionada.", styles["caption"]),
            _paragraph(
                "A base possui atributos categóricos, numéricos e temporais. Entre os atributos categóricos estão "
                "dia da semana, causa e tipo do acidente, fase do dia, condição meteorológica, tipo e traçado da pista "
                "e uso do solo. Os atributos numéricos relevantes incluem quilômetro da rodovia, número de veículos e "
                "número de pessoas envolvidas. Data e horário são atributos temporais; latitude e longitude são geográficos.",
                styles,
            ),
            _paragraph(
                "A análise verificou ausência em quatro colunas: classificacao_acidente (1 registro), regional (1), "
                "delegacia (10) e uop (22). Não foram identificados IDs ou linhas duplicadas. O único rótulo ausente foi "
                "completado apenas para fins de consistência a partir das colunas de desfecho; tais colunas não são usadas "
                "como entrada dos modelos para evitar vazamento de dados.",
                styles,
            ),
            Paragraph("3.2 Pré-processamento", styles["heading2"]),
            Paragraph(
                "Seção reservada para detalhamento completo nas próximas sprints. Nesta etapa, foi registrada a preparação "
                "inicial necessária para a análise exploratória e preservada a separação entre atributos de entrada e variáveis de desfecho.",
                styles["reserved"],
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
                "A classe Com Vítimas Feridas concentra 32.726 registros (77,33%), seguida por Sem Vítimas com 6.584 "
                "registros (15,56%) e Com Vítimas Fatais com 3.012 registros (7,12%). Portanto, o problema é desbalanceado. "
                "Nas próximas etapas, as métricas macro e estratégias apropriadas de balanceamento deverão receber mais "
                "atenção do que a acurácia isolada.",
                styles,
            ),
            _figure(
                "distribuicao_classes.png",
                "Figura 1 - Distribuição da variável-alvo após a validação do rótulo.",
            ),
            _paragraph(
                "As ausências são pontuais e estão concentradas em colunas administrativas que não fazem parte do conjunto "
                "inicial de atributos de modelagem. A ausência da classificação foi tratada e não há falta de valores em km, "
                "veículos ou pessoas após a conversão correta do separador decimal.",
                styles,
            ),
            _figure(
                "valores_ausentes.png",
                "Figura 2 - Quantidade de valores ausentes por atributo no arquivo bruto.",
            ),
            Paragraph("4.1.2 Distribuições e valores discrepantes", styles["heading2"]),
            _paragraph(
                "A mediana do horário é 14h e a distribuição indica maior volume de ocorrências principalmente no início "
                "da manhã e no fim da tarde. O quilômetro apresenta assimetria à direita: a mediana é 190,25 km, enquanto "
                "o valor máximo chega a 1.260 km. Em geral, os acidentes envolvem poucos veículos e pessoas: as medianas "
                "são 2 veículos e 2 pessoas. Os valores muito altos representam acidentes de maior porte e devem ser avaliados "
                "no contexto do domínio antes de qualquer remoção.",
                styles,
            ),
            _figure(
                "distribuicoes_numericas.png",
                "Figura 3 - Histogramas das variáveis numéricas utilizadas na análise exploratória.",
            ),
            _paragraph(
                "Os boxplots reforçam a presença de valores extremos, especialmente em pessoas e veículos envolvidos. A classe "
                "Com Vítimas Fatais apresenta mediana de 3 pessoas, superior às demais classes, que possuem mediana de 2. "
                "Esse padrão não prova causalidade, mas indica uma relação que merece investigação nos modelos posteriores.",
                styles,
            ),
            _figure(
                "boxplots_por_classe.png",
                "Figura 4 - Boxplots de km, veículos e pessoas por classe de gravidade.",
            ),
            PageBreak(),
            Paragraph("4.1.3 Relações entre atributos numéricos", styles["heading2"]),
            _paragraph(
                "A correlação de Pearson mais relevante foi observada entre número de veículos e número de pessoas "
                "envolvidas (r = 0,42), uma associação moderada e esperada. As demais correlações ficaram próximas de zero, "
                "o que sugere pouca relação linear entre horário, quilômetro e essas duas contagens. Isso não elimina a "
                "possibilidade de relações não lineares ou interações com atributos categóricos.",
                styles,
            ),
            _figure(
                "correlacao_numericas.png",
                "Figura 5 - Matriz de correlação de Pearson entre os atributos numéricos de modelagem.",
            ),
            _paragraph(
                "O gráfico de dispersão mostra alta concentração de acidentes com até cinco pessoas envolvidas em diferentes "
                "quilômetros das rodovias. Não há separação visual nítida das classes somente por esses dois atributos, o que "
                "justifica combinar informações de contexto, via e acidente nos futuros classificadores.",
                styles,
            ),
            _figure(
                "dispersao_km_pessoas.png",
                "Figura 6 - Amostra reprodutível de 12.000 acidentes: quilômetro versus pessoas envolvidas.",
            ),
            Paragraph("4.1.4 Padrões temporais", styles["heading2"]),
            _paragraph(
                "A maior parte dos registros ocorreu em pleno dia (23.387; 55,26%), seguida por plena noite "
                "(14.562; 34,41%). Em números absolutos, as ocorrências fatais também se concentram nesses dois períodos. "
                "Como as categorias têm tamanhos diferentes, uma comparação futura deve considerar taxas relativas por fase do dia.",
                styles,
            ),
            _figure(
                "fase_dia_por_classe.png",
                "Figura 7 - Quantidade de acidentes por fase do dia e classe de gravidade.",
            ),
            _paragraph(
                "Sexta-feira apresentou o maior número de acidentes (6.700), seguida por domingo (6.643) e sábado "
                "(6.489). Terça-feira teve a menor contagem (5.320). O padrão sugere maior volume próximo ao fim de semana, "
                "mas essa observação deve ser interpretada junto à exposição ao tráfego, que não está disponível na base.",
                styles,
            ),
            _figure(
                "acidentes_por_dia_semana.png",
                "Figura 8 - Quantidade de acidentes por dia da semana.",
            ),
            Paragraph("4.1.5 Síntese da análise exploratória", styles["heading2"]),
            _paragraph(
                "A base apresenta volume suficiente e variedade de atributos para o problema de classificação proposto. "
                "As principais decisões para a próxima etapa são: preservar o tratamento de leakage, usar métricas adequadas "
                "ao desbalanceamento das classes, manter os valores extremos para avaliação criteriosa e testar modelos capazes "
                "de combinar atributos numéricos, categóricos e temporais.",
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
                "BASE DATATRAN 2026. Arquivo compartilhado com a equipe por meio do Google Drive do projeto. "
                "Recorte utilizado: acidentes registrados de janeiro a julho de 2026.",
                styles,
            ),
        ]
    )

    document.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return OUTPUT


if __name__ == "__main__":
    report = build_report()
    print(f"Relatório gerado em: {report}")
