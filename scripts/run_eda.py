"""Executa a análise exploratória reproduzível e a baseline do projeto."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Permite executar o script diretamente a partir da raiz, sem instalar o
# projeto como pacote Python.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

# O script roda sem interface gráfica e salva as figuras diretamente em PNG.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data_pipeline import (
    TARGET_COLUMN,
    prepare_modeling_data,
    profile_dataset,
    read_raw_data,
    save_json,
    save_modeling_data,
)
from src.modeling import evaluate_baseline

TARGET_ORDER = ["Sem Vítimas", "Com Vítimas Feridas", "Com Vítimas Fatais"]
TARGET_COLORS = {
    "Sem Vítimas": "#5b8ff9",
    "Com Vítimas Feridas": "#f6bd16",
    "Com Vítimas Fatais": "#e8684a",
}
NUMERIC_EDA_COLUMNS = ["hora", "km", "veiculos", "pessoas"]
PHASE_ORDER = ["Amanhecer", "Pleno dia", "Anoitecer", "Plena Noite"]
WEEKDAY_ORDER = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]


def _available_targets(data: pd.DataFrame) -> list[str]:
    """Mantém a mesma ordem das classes em gráficos, tabelas e relatório."""

    present = set(data[TARGET_COLUMN].dropna().unique())
    return [target for target in TARGET_ORDER if target in present]


def _save_figure(figure: plt.Figure, output: Path) -> None:
    figure.tight_layout()
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _save_target_distribution(modeling: pd.DataFrame, figures_dir: Path) -> None:
    labels = _available_targets(modeling)
    counts = modeling[TARGET_COLUMN].value_counts().reindex(labels, fill_value=0)
    figure, axis = plt.subplots(figsize=(9, 5))
    bars = axis.bar(counts.index, counts.values, color=[TARGET_COLORS[label] for label in labels])
    axis.set_title("Distribuição da classificação dos acidentes")
    axis.set_xlabel("Classe de gravidade")
    axis.set_ylabel("Quantidade de acidentes")
    axis.tick_params(axis="x", rotation=15)
    for bar, count in zip(bars, counts.values, strict=True):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            count,
            f"{count:,}".replace(",", "."),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    _save_figure(figure, figures_dir / "distribuicao_classes.png")


def _save_missing_values(raw: pd.DataFrame, figures_dir: Path) -> None:
    missing = raw.isna().sum().loc[lambda values: values.gt(0)].sort_values()
    figure, axis = plt.subplots(figsize=(9, 5))
    if missing.empty:
        axis.text(0.5, 0.5, "Nenhum valor ausente", ha="center", va="center")
        axis.set_axis_off()
    else:
        bars = axis.barh(missing.index, missing.values, color="#d98c3f")
        axis.set_title("Valores ausentes por coluna")
        axis.set_xlabel("Quantidade de registros ausentes")
        axis.set_ylabel("Coluna")
        for bar, count in zip(bars, missing.values, strict=True):
            axis.text(count, bar.get_y() + bar.get_height() / 2, f" {count}", va="center")
    _save_figure(figure, figures_dir / "valores_ausentes.png")


def _save_numeric_histograms(modeling: pd.DataFrame, figures_dir: Path) -> None:
    # Histogramas mostram concentração, assimetria e possíveis valores extremos.
    labels = {
        "hora": "Hora do acidente",
        "km": "Quilômetro da rodovia",
        "veiculos": "Veículos envolvidos",
        "pessoas": "Pessoas envolvidas",
    }
    # veiculos e pessoas concentram mais de 90% dos casos em 1-3 unidades; sem
    # escala logarítmica, a cauda longa desses dois atributos fica invisível.
    log_scale_columns = {"veiculos", "pessoas"}
    figure, axes = plt.subplots(2, 2, figsize=(11, 8))
    for axis, column in zip(axes.flat, NUMERIC_EDA_COLUMNS, strict=True):
        bins = range(1, 21) if column in log_scale_columns else 30
        axis.hist(modeling[column].dropna(), bins=bins, color="#4a8f65", edgecolor="white")
        title = labels[column]
        if column in log_scale_columns:
            axis.set_yscale("log")
            title += " (eixo em escala logarítmica)"
        axis.set_title(title)
        axis.set_xlabel(labels[column])
        axis.set_ylabel("Quantidade de acidentes")
    figure.suptitle("Distribuição das variáveis numéricas", y=1.02)
    _save_figure(figure, figures_dir / "distribuicoes_numericas.png")


def _save_boxplots(modeling: pd.DataFrame, figures_dir: Path) -> None:
    """Compara variáveis numéricas entre as três classes de gravidade."""

    labels = _available_targets(modeling)
    columns = ["km", "veiculos", "pessoas"]
    names = {
        "km": "Quilômetro da rodovia",
        "veiculos": "Veículos envolvidos",
        "pessoas": "Pessoas envolvidas",
    }
    # veiculos e pessoas têm outliers tão extremos que, em escala linear, a
    # caixa e a mediana ficam achatadas perto de zero e viram uma linha única.
    log_scale_columns = {"veiculos", "pessoas"}
    figure, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    for axis, column in zip(axes, columns, strict=True):
        values = [modeling.loc[modeling[TARGET_COLUMN].eq(label), column].dropna() for label in labels]
        box = axis.boxplot(values, tick_labels=labels, patch_artist=True, showfliers=True)
        for patch, label in zip(box["boxes"], labels, strict=True):
            patch.set_facecolor(TARGET_COLORS[label])
            patch.set_alpha(0.7)
        title = names[column]
        if column in log_scale_columns:
            axis.set_yscale("log")
            title += " (eixo em escala logarítmica)"
        axis.set_title(title)
        axis.set_xlabel("Classe de gravidade")
        axis.set_ylabel(names[column])
        axis.tick_params(axis="x", rotation=20)
    figure.suptitle("Boxplots das variáveis numéricas por classificação", y=1.03)
    _save_figure(figure, figures_dir / "boxplots_por_classe.png")


def _save_correlation(modeling: pd.DataFrame, figures_dir: Path) -> pd.DataFrame:
    """Gera a matriz de correlação somente com atributos permitidos no modelo."""

    correlation = modeling[NUMERIC_EDA_COLUMNS].corr()
    labels = ["hora", "km", "veículos", "pessoas"]
    figure, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(correlation, vmin=-1, vmax=1, cmap="YlGnBu")
    axis.set_xticks(range(len(labels)), labels=labels, rotation=25, ha="right")
    axis.set_yticks(range(len(labels)), labels=labels)
    for row in range(len(labels)):
        for column in range(len(labels)):
            axis.text(
                column,
                row,
                f"{correlation.iloc[row, column]:.2f}",
                ha="center",
                va="center",
                color="black",
            )
    colorbar = figure.colorbar(image, ax=axis)
    colorbar.set_label("Correlação de Pearson")
    axis.set_title("Correlação entre atributos numéricos de modelagem")
    _save_figure(figure, figures_dir / "correlacao_numericas.png")
    return correlation


def _save_scatter(modeling: pd.DataFrame, figures_dir: Path) -> None:
    """Compara a densidade de km x pessoas envolvidas entre as classes.

    Um único scatter com as três classes sobrepostas satura visualmente nos
    valores baixos de pessoas, onde a maioria dos acidentes se concentra, e
    não deixa comparar as classes. Pessoas é essencialmente discreta (1 a 10
    cobre 99,4% dos casos), então um histograma 2D com um bin por valor
    inteiro - em vez de um hexbin, cujas células hexagonais não alinham com
    números inteiros - representa a contagem real sem distorção visual.
    """

    labels = _available_targets(modeling)
    y_max = 10
    people_edges = np.arange(0.5, y_max + 1.5, 1.0)
    km_edges = np.linspace(0, modeling["km"].max(), 21)
    # As classes têm tamanhos muito diferentes (de ~2 mil a ~26 mil acidentes),
    # então cada painel traz sua própria barra de cor para comparar a FORMA da
    # distribuição; uma escala absoluta compartilhada apagaria as duas classes
    # minoritárias diante da classe majoritária.
    figure, axes = plt.subplots(1, len(labels), figsize=(5.2 * len(labels), 5))
    axes = [axes] if len(labels) == 1 else list(axes)
    for axis, label in zip(axes, labels, strict=True):
        subset = modeling.loc[modeling[TARGET_COLUMN].eq(label)]
        counts, _, _ = np.histogram2d(subset["km"], subset["pessoas"], bins=(km_edges, people_edges))
        mesh = axis.pcolormesh(km_edges, people_edges, counts.T, cmap="YlGnBu", vmin=0)
        figure.colorbar(mesh, ax=axis, label="Acidentes por célula", shrink=0.85)
        axis.set_title(f"{label} (n={len(subset):,})".replace(",", "."), color=TARGET_COLORS[label], fontweight="bold")
        axis.set_xlabel("Quilômetro da rodovia (km)")
        axis.set_yticks(range(1, y_max + 1))
        axis.set_ylim(0.5, y_max + 0.5)
    axes[0].set_ylabel("Pessoas envolvidas (até 10)")
    figure.suptitle("Densidade de acidentes por quilômetro e pessoas envolvidas, por classe")
    figure.savefig(figures_dir / "dispersao_km_pessoas.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def _save_severity_by_accident_type(modeling: pd.DataFrame, figures_dir: Path, top_n: int = 8) -> pd.DataFrame:
    """Mostra a taxa de gravidade dentro dos tipos de acidente mais frequentes.

    Os atributos numéricos (km, hora, veículos, pessoas) quase não se
    correlacionam com a gravidade (Figura 5); este gráfico testa se um
    atributo categórico - tipo_acidente - carrega mais sinal.
    """

    labels = _available_targets(modeling)
    top_types = modeling["tipo_acidente"].value_counts().head(top_n).index.tolist()
    subset = modeling.loc[modeling["tipo_acidente"].isin(top_types)]
    counts = pd.crosstab(subset["tipo_acidente"], subset[TARGET_COLUMN]).reindex(columns=labels, fill_value=0)
    rate = counts.div(counts.sum(axis=1), axis=0) * 100
    # Ordenar pela taxa de fatais destaca o tipo mais crítico no topo do gráfico.
    rate = rate.sort_values("Com Vítimas Fatais")
    counts = counts.loc[rate.index]

    figure, axis = plt.subplots(figsize=(10, 5.5))
    left = pd.Series(0.0, index=rate.index)
    for label in labels:
        axis.barh(rate.index, rate[label], left=left, color=TARGET_COLORS[label], label=label)
        left = left + rate[label]
    for row, (type_name, fatal_rate) in enumerate(rate["Com Vítimas Fatais"].items()):
        axis.text(100.5, row, f"{fatal_rate:.1f}% fatais", va="center", fontsize=8.5)
    axis.set_xlim(0, 118)
    axis.set_xlabel("Percentual de acidentes (%)")
    axis.set_title(f"Gravidade dentro dos {top_n} tipos de acidente mais frequentes")
    axis.legend(
        title="Classe de gravidade", loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3,
    )
    _save_figure(figure, figures_dir / "gravidade_por_tipo_acidente.png")

    summary = counts.join(rate, lsuffix="_n", rsuffix="_pct")
    return summary


def _save_phase_distribution(modeling: pd.DataFrame, figures_dir: Path) -> pd.DataFrame:
    """Mostra como as classes aparecem nas diferentes fases do dia."""

    labels = _available_targets(modeling)
    phase = pd.crosstab(modeling["fase_dia"], modeling[TARGET_COLUMN])
    phase = phase.reindex(index=PHASE_ORDER, columns=labels, fill_value=0)
    figure, axis = plt.subplots(figsize=(10, 6))
    bottom = pd.Series(0, index=phase.index, dtype="int64")
    for label in labels:
        axis.bar(phase.index, phase[label], bottom=bottom, label=label, color=TARGET_COLORS[label])
        bottom = bottom + phase[label]
    axis.set_title("Classificação dos acidentes por fase do dia")
    axis.set_xlabel("Fase do dia")
    axis.set_ylabel("Quantidade de acidentes")
    axis.legend(title="Classe de gravidade")
    _save_figure(figure, figures_dir / "fase_dia_por_classe.png")
    return phase


def _save_weekday_distribution(modeling: pd.DataFrame, figures_dir: Path) -> pd.Series:
    weekday = modeling["dia_semana"].value_counts().reindex(WEEKDAY_ORDER, fill_value=0)
    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(weekday.index, weekday.values, color="#176b87")
    axis.set_title("Quantidade de acidentes por dia da semana")
    axis.set_xlabel("Dia da semana")
    axis.set_ylabel("Quantidade de acidentes")
    axis.tick_params(axis="x", rotation=20)
    _save_figure(figure, figures_dir / "acidentes_por_dia_semana.png")
    return weekday


def _as_jsonable(frame: pd.DataFrame | pd.Series) -> dict:
    """Converte estruturas pandas em tipos básicos aceitos pelo JSON."""

    return json.loads(frame.to_json(force_ascii=False))


def _save_eda_artifacts(raw: pd.DataFrame, modeling: pd.DataFrame, output_dir: Path) -> None:
    figures_dir = output_dir / "figures"
    metrics_dir = output_dir / "metrics"
    figures_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    _save_target_distribution(modeling, figures_dir)
    _save_missing_values(raw, figures_dir)
    _save_numeric_histograms(modeling, figures_dir)
    _save_boxplots(modeling, figures_dir)
    correlation = _save_correlation(modeling, figures_dir)
    _save_scatter(modeling, figures_dir)
    phase = _save_phase_distribution(modeling, figures_dir)
    weekday = _save_weekday_distribution(modeling, figures_dir)
    severity_by_type = _save_severity_by_accident_type(modeling, figures_dir)

    numeric_description = modeling[NUMERIC_EDA_COLUMNS].describe(
        percentiles=[0.25, 0.5, 0.75]
    ).round(3)
    classes = modeling[TARGET_COLUMN].value_counts().reindex(
        _available_targets(modeling), fill_value=0
    )
    class_summary = pd.DataFrame(
        {
            "quantidade": classes,
            "percentual": (classes / len(modeling) * 100).round(3),
        }
    )

    numeric_description.to_csv(metrics_dir / "estatisticas_numericas.csv", encoding="utf-8")
    correlation.round(4).to_csv(metrics_dir / "correlacao_numericas.csv", encoding="utf-8")
    phase.to_csv(metrics_dir / "fase_dia_por_classe.csv", encoding="utf-8")
    weekday.rename("quantidade").to_csv(metrics_dir / "acidentes_por_dia_semana.csv", encoding="utf-8")
    class_summary.to_csv(metrics_dir / "distribuicao_classes.csv", encoding="utf-8")
    severity_by_type.round(3).to_csv(metrics_dir / "gravidade_por_tipo_acidente.csv", encoding="utf-8")
    save_json(
        {
            "distribuicao_classes": _as_jsonable(class_summary),
            "estatisticas_numericas": _as_jsonable(numeric_description),
            "correlacao_numericas": _as_jsonable(correlation.round(4)),
            "fase_dia_por_classe": _as_jsonable(phase),
            "acidentes_por_dia_semana": _as_jsonable(weekday),
            "gravidade_por_tipo_acidente": _as_jsonable(severity_by_type.round(3)),
        },
        metrics_dir / "eda_summary.json",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "raw" / "datatran2026.csv",
        help="Caminho para o CSV bruto.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results",
        help="Diretório dos resultados gerados.",
    )
    args = parser.parse_args()

    raw = read_raw_data(args.input)
    modeling = prepare_modeling_data(raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_json(profile_dataset(raw), args.output_dir / "metrics" / "data_profile.json")
    save_modeling_data(modeling, ROOT / "data" / "processed" / "modeling_base.csv")
    _save_eda_artifacts(raw, modeling, args.output_dir)

    # A baseline cria uma referência mínima para avaliar se os modelos futuros
    # realmente melhoram o desempenho.
    metrics, matrix = evaluate_baseline(modeling)
    save_json(metrics, args.output_dir / "metrics" / "baseline_metrics.json")
    matrix.to_csv(args.output_dir / "metrics" / "baseline_confusion_matrix.csv", encoding="utf-8")

    print(f"Registros brutos: {len(raw)}")
    print(f"Registros na modelagem: {len(modeling)}")
    print(f"F1 macro da baseline: {metrics['f1_macro']:.4f}")
    print(f"Resultados salvos em: {args.output_dir}")


if __name__ == "__main__":
    main()
