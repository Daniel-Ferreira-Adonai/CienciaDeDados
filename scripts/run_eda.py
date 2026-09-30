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
    figure, axes = plt.subplots(2, 2, figsize=(11, 8))
    for axis, column in zip(axes.flat, NUMERIC_EDA_COLUMNS, strict=True):
        axis.hist(modeling[column].dropna(), bins=30, color="#4a8f65", edgecolor="white")
        axis.set_title(labels[column])
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
    figure, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    for axis, column in zip(axes, columns, strict=True):
        values = [modeling.loc[modeling[TARGET_COLUMN].eq(label), column].dropna() for label in labels]
        box = axis.boxplot(values, tick_labels=labels, patch_artist=True, showfliers=True)
        for patch, label in zip(box["boxes"], labels, strict=True):
            patch.set_facecolor(TARGET_COLORS[label])
            patch.set_alpha(0.7)
        axis.set_title(names[column])
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
    """Exibe a relação entre localização do acidente e pessoas envolvidas."""

    labels = _available_targets(modeling)
    # A amostra fixa reduz sobreposição visual e mantém a figura reproduzível.
    sample = modeling.sample(n=min(12_000, len(modeling)), random_state=42)
    figure, axis = plt.subplots(figsize=(9, 6))
    for label in labels:
        subset = sample.loc[sample[TARGET_COLUMN].eq(label)]
        axis.scatter(
            subset["km"],
            subset["pessoas"],
            s=10,
            alpha=0.25,
            color=TARGET_COLORS[label],
            label=label,
            edgecolors="none",
        )
    axis.set_title("Relação entre quilômetro da rodovia e pessoas envolvidas")
    axis.set_xlabel("Quilômetro da rodovia (km)")
    axis.set_ylabel("Pessoas envolvidas")
    axis.legend(title="Classe de gravidade")
    _save_figure(figure, figures_dir / "dispersao_km_pessoas.png")


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
    save_json(
        {
            "distribuicao_classes": _as_jsonable(class_summary),
            "estatisticas_numericas": _as_jsonable(numeric_description),
            "correlacao_numericas": _as_jsonable(correlation.round(4)),
            "fase_dia_por_classe": _as_jsonable(phase),
            "acidentes_por_dia_semana": _as_jsonable(weekday),
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
