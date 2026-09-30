"""Gera uma cópia do relatório da Sprint 1 no formato do modelo da disciplina."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    }


def p(text: str, s: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, s["body"])


def bullet(text: str, s: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"• {text}", s["bullet"])


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
        ("2.7", "Trabalhos Relacionados"),
    ]:
        story.extend(
            [
                Paragraph(f"{number} &nbsp;&nbsp; {heading}", s["h2"]),
                Paragraph("Conteúdo reservado para desenvolvimento nas próximas sprints.", s["reserved"]),
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
                "de dados abertos e compartilhada com a equipe por meio de um link do Google Drive. Ela registra acidentes "
                "ocorridos em rodovias federais brasileiras.",
                s,
            ),
            p(
                "O recorte contém 42.322 instâncias e 30 atributos, referentes ao período de 1º de janeiro a 31 de julho "
                "de 2026. A tarefa é de classificação multiclasse, cuja variável-alvo é classificacao_acidente.",
                s,
            ),
            bullet("Formato: CSV com separador ponto e vírgula e codificação cp1252.", s),
            bullet("Classes: Sem Vítimas; Com Vítimas Feridas; Com Vítimas Fatais.", s),
            bullet("Atributos categóricos, numéricos, temporais e geográficos.", s),
            bullet("Atributos numéricos relevantes: quilômetro, número de veículos e número de pessoas.", s),
            bullet("Um rótulo ausente, preenchido somente para consistência a partir de colunas de desfecho.", s),
            bullet("Ausências adicionais: regional (1), delegacia (10) e uop (22); não foram encontradas linhas duplicadas.", s),
            p(
                "As colunas de desfecho mortos, feridos, feridos_leves, feridos_graves, ilesos e ignorados não são usadas "
                "como entrada dos modelos. Essa decisão evita vazamento de dados, pois essas informações só se tornam "
                "conhecidas após a ocorrência.",
                s,
            ),
        ]
    )
    for number, heading, description in [
        ("3.2", "Pré-processamento", "Seção reservada para detalhar transformações, imputação e codificação aplicadas antes do treinamento."),
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
                "A classe Com Vítimas Feridas concentra 32.726 registros (77,33%), seguida por Sem Vítimas com 6.584 "
                "(15,56%) e Com Vítimas Fatais com 3.012 (7,12%). O problema é desbalanceado; por isso, as próximas etapas "
                "devem avaliar métricas macro além da acurácia isolada.",
                s,
            ),
            figure("distribuicao_classes.png", "Figura 1: Distribuição da variável-alvo após a validação do rótulo."),
            p(
                "As ausências são pontuais e se concentram em colunas administrativas. Não há valores ausentes em km, "
                "veículos ou pessoas após a conversão correta dos campos numéricos.",
                s,
            ),
            figure("valores_ausentes.png", "Figura 2: Quantidade de valores ausentes por atributo no arquivo bruto."),
            Paragraph("4.1.2 &nbsp;&nbsp; Distribuições e valores discrepantes", s["h2"]),
            p(
                "A mediana do horário é 14h. O quilômetro é assimétrico à direita: mediana de 190,25 km e máximo de 1.260 km. "
                "As medianas de veículos e pessoas são 2, enquanto valores muito altos representam ocorrências de maior porte "
                "e devem ser avaliados no contexto do domínio antes de qualquer remoção.",
                s,
            ),
            figure("distribuicoes_numericas.png", "Figura 3: Histogramas das variáveis numéricas utilizadas na análise exploratória."),
            p(
                "Os boxplots reforçam a existência de valores extremos, especialmente em pessoas e veículos. A classe Com "
                "Vítimas Fatais apresenta mediana de 3 pessoas, enquanto as demais têm mediana de 2; é um indício a ser "
                "investigado posteriormente, não uma relação causal.",
                s,
            ),
            figure("boxplots_por_classe.png", "Figura 4: Boxplots de km, veículos e pessoas por classe de gravidade."),
            Paragraph("4.1.3 &nbsp;&nbsp; Relações entre atributos numéricos", s["h2"]),
            p(
                "A correlação de Pearson mais relevante ocorre entre número de veículos e número de pessoas envolvidas "
                "(r = 0,42), associação moderada e esperada. As demais correlações ficam próximas de zero, sugerindo pouca "
                "relação linear entre horário, quilômetro e as contagens.",
                s,
            ),
            figure("correlacao_numericas.png", "Figura 5: Matriz de correlação de Pearson dos atributos numéricos."),
            p(
                "No gráfico de dispersão, acidentes com até cinco pessoas predominam em diferentes quilômetros das rodovias. "
                "Não há separação visual nítida das classes apenas por esses dois atributos, justificando a combinação de "
                "informações de contexto, via e acidente nos classificadores futuros.",
                s,
            ),
            figure("dispersao_km_pessoas.png", "Figura 6: Amostra de 12.000 acidentes: quilômetro versus pessoas envolvidas."),
            Paragraph("4.1.4 &nbsp;&nbsp; Padrões temporais", s["h2"]),
            p(
                "A maior parte dos registros ocorreu em pleno dia (23.387; 55,26%), seguida por plena noite (14.562; 34,41%). "
                "As ocorrências fatais também se concentram nesses dois períodos em valores absolutos; comparações futuras "
                "devem considerar taxas relativas por fase do dia.",
                s,
            ),
            figure("fase_dia_por_classe.png", "Figura 7: Quantidade de acidentes por fase do dia e classe de gravidade."),
            p(
                "Sexta-feira apresenta o maior número de acidentes (6.700), seguida por domingo (6.643) e sábado (6.489). "
                "Terça-feira possui a menor contagem (5.320). O padrão sugere maior volume próximo ao fim de semana, mas "
                "a base não contém a exposição ao tráfego necessária para conclusões causais.",
                s,
            ),
            figure("acidentes_por_dia_semana.png", "Figura 8: Quantidade de acidentes por dia da semana."),
            Paragraph("4.1.5 &nbsp;&nbsp; Síntese da análise exploratória", s["h2"]),
            p(
                "A base apresenta volume e variedade de atributos adequados ao problema. Para as próximas etapas, devem ser "
                "preservados o controle de vazamento de dados, o uso de métricas adequadas ao desbalanceamento e a avaliação "
                "criteriosa de valores extremos.",
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
                "BASE DATATRAN 2026. Arquivo compartilhado com a equipe por meio do Google Drive do projeto. "
                "Recorte utilizado: acidentes registrados de janeiro a julho de 2026.",
                s,
            ),
        ]
    )
    document.build(story, onFirstPage=page_number, onLaterPages=page_number)
    return OUTPUT


if __name__ == "__main__":
    report = build_report()
    print(f"Relatório gerado em: {report}")
