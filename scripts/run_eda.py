"""Executa o primeiro pipeline reproduzível de EDA e baseline."""

from __future__ import annotations

import argparse
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
    TARGET_COLUMN, prepare_modeling_data, profile_dataset, read_raw_data,
    save_json, save_modeling_data,
)
from src.modeling import evaluate_baseline


def _save_plots(raw: pd.DataFrame, modeling: pd.DataFrame, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)

    # A distribuição do alvo é a primeira verificação da desproporção entre
    # classes e orienta a escolha de métricas e técnicas de balanceamento.
    target = modeling[TARGET_COLUMN].value_counts().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    target.plot.bar(ax=ax, color="#176b87")
    ax.set_title("Distribuição da classificação dos acidentes")
    ax.set_xlabel("Classe"); ax.set_ylabel("Quantidade"); ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(); fig.savefig(figures_dir / "distribuicao_classes.png", dpi=160); plt.close(fig)

    # Só exibimos colunas com ausência para manter o gráfico legível.
    missing = raw.isna().sum().loc[lambda values: values.gt(0)].sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    if missing.empty:
        ax.text(0.5, 0.5, "Nenhum valor ausente", ha="center", va="center"); ax.set_axis_off()
    else:
        missing.plot.barh(ax=ax, color="#d98c3f")
        ax.set_title("Valores ausentes por coluna"); ax.set_xlabel("Quantidade"); ax.set_ylabel("Coluna")
    fig.tight_layout(); fig.savefig(figures_dir / "valores_ausentes.png", dpi=160); plt.close(fig)

    # Histogramas ajudam a identificar assimetria, concentrações e possíveis
    # valores extremos antes da etapa de modelagem.
    axes = modeling[["km", "veiculos", "pessoas"]].hist(
        figsize=(10, 7), bins=30, color="#4a8f65", edgecolor="white"
    )
    figure = axes[0][0].get_figure(); figure.suptitle("Distribuição das variáveis numéricas", y=1.02)
    figure.tight_layout(); figure.savefig(figures_dir / "distribuicoes_numericas.png", dpi=160, bbox_inches="tight"); plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "raw" / "datatran2026.csv", help="Caminho para o CSV bruto.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results", help="Diretório dos resultados gerados.")
    args = parser.parse_args()

    raw = read_raw_data(args.input)
    modeling = prepare_modeling_data(raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_json(profile_dataset(raw), args.output_dir / "metrics" / "data_profile.json")
    save_modeling_data(modeling, ROOT / "data" / "processed" / "modeling_base.csv")
    _save_plots(raw, modeling, args.output_dir / "figures")

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
