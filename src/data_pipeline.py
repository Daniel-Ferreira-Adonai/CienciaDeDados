"""Leitura, validação e preparação da base de acidentes da PRF.

As funções deste módulo mantêm a separação entre dados brutos, usados para
auditoria e derivação do alvo, e dados de modelagem, que não carregam colunas
de desfecho e, portanto, evitam vazamento de dados.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

# Colunas usadas em etapas diferentes do projeto. A distinção entre as
# features brutas e as features de modelagem ajuda a evitar leakage acidental.
TARGET_COLUMN = "classificacao_acidente"
RAW_FEATURE_COLUMNS = [
    "dia_semana", "horario", "causa_acidente", "tipo_acidente", "fase_dia",
    "condicao_metereologica", "tipo_pista", "tracado_via", "uso_solo", "br",
    "km", "veiculos", "pessoas",
]
MODEL_FEATURE_COLUMNS = [
    "dia_semana", "hora", "causa_acidente", "tipo_acidente", "fase_dia",
    "condicao_metereologica", "tipo_pista", "tracado_via", "uso_solo", "br",
    "km", "veiculos", "pessoas",
]
OUTCOME_COLUMNS = [
    "mortos", "feridos", "feridos_leves", "feridos_graves", "ilesos", "ignorados",
]
# Estas colunas são obrigatórias para garantir que a base recebida tem o
# mesmo esquema usado pela equipe nos experimentos.
REQUIRED_COLUMNS = ["id", TARGET_COLUMN, *RAW_FEATURE_COLUMNS, *OUTCOME_COLUMNS]
CATEGORICAL_COLUMNS = [
    "dia_semana", "causa_acidente", "tipo_acidente", "fase_dia",
    "condicao_metereologica", "tipo_pista", "tracado_via", "uso_solo", "br",
]
NUMERIC_COLUMNS = ["hora", "km", "veiculos", "pessoas"]


def _normalise_label(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().casefold()
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


LABELS = {
    "sem vitimas": "Sem Vítimas",
    "com vitimas feridas": "Com Vítimas Feridas",
    "com vitimas fatais": "Com Vítimas Fatais",
}


def read_raw_data(path: str | Path) -> pd.DataFrame:
    """Lê a base PRF e confirma a presença do esquema mínimo esperado."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Base não encontrada em {path}. Consulte data/raw/README.md."
        )

    last_error: Exception | None = None
    # O arquivo disponibilizado pela PRF usa cp1252 e separador ';'. As outras
    # codificações deixam o leitor preparado para uma futura versão da fonte.
    for encoding in ("cp1252", "latin1", "utf-8-sig"):
        try:
            data = pd.read_csv(
                path, sep=";", encoding=encoding,
                na_values=["NA", "N/A", "NULL", ""], keep_default_na=True,
            )
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise ValueError(f"Não foi possível decodificar {path}: {last_error}")

    # Falhar cedo é melhor do que produzir métricas com colunas trocadas ou
    # ausentes sem que a equipe perceba.
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].astype("string").str.strip()
    return data


def _numeric(data: pd.DataFrame, column: str) -> pd.Series:
    # A coluna km possui valores como "146,1". A troca da vírgula preserva o
    # valor decimal antes da conversão para número.
    values = data[column].astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(values, errors="coerce")


def _derive_target(data: pd.DataFrame) -> pd.Series:
    """Deriva o alvo apenas para registros sem classificação publicada."""

    deaths = _numeric(data, "mortos")
    injured = _numeric(data, "feridos")
    derived = pd.Series(pd.NA, index=data.index, dtype="string")
    # Em caso de conflito, fatalidade tem precedência sobre ferimento; depois
    # vêm acidentes com feridos e, por fim, acidentes sem vítimas.
    derived.loc[deaths.gt(0)] = "Com Vítimas Fatais"
    derived.loc[deaths.fillna(0).eq(0) & injured.gt(0)] = "Com Vítimas Feridas"
    derived.loc[deaths.fillna(0).eq(0) & injured.fillna(0).eq(0)] = "Sem Vítimas"
    return derived


def prepare_modeling_data(data: pd.DataFrame) -> pd.DataFrame:
    """Cria a tabela de modelagem sem variáveis de desfecho.

    O horário é convertido em hora inteira para não transformar cada minuto em
    uma categoria independente. `br` permanece categórica, pois representa o
    código da rodovia, não uma grandeza contínua.
    """

    prepared = data.copy()
    # A classificação publicada é a fonte principal. Só usamos os desfechos
    # para preencher um rótulo ausente, nunca como entrada do modelo.
    published = prepared[TARGET_COLUMN].map(_normalise_label).map(LABELS)
    prepared[TARGET_COLUMN] = published.fillna(_derive_target(prepared)).astype("string")
    prepared["hora"] = pd.to_datetime(
        prepared["horario"], format="%H:%M:%S", errors="coerce"
    ).dt.hour
    # Conversões explícitas evitam que números sejam tratados como texto pelo
    # estimador e permitem que o pipeline faça a imputação corretamente.
    for column in ("km", "veiculos", "pessoas"):
        prepared[column] = _numeric(prepared, column)
    prepared["br"] = prepared["br"].astype("string")

    # A seleção explícita é a principal barreira contra o vazamento das
    # colunas de desfecho (mortos, feridos, ilesos etc.).
    modeling = prepared[[*MODEL_FEATURE_COLUMNS, TARGET_COLUMN]].copy()
    return modeling.dropna(subset=[TARGET_COLUMN])


def profile_dataset(data: pd.DataFrame) -> dict[str, Any]:
    """Produz um perfil serializável para documentação e auditoria."""

    dates = pd.to_datetime(data["data_inversa"], errors="coerce")
    numeric = data.assign(
        km=_numeric(data, "km"), veiculos=_numeric(data, "veiculos"),
        pessoas=_numeric(data, "pessoas"),
    )
    numeric_summary: dict[str, dict[str, float | int | None]] = {}
    for column in ("km", "veiculos", "pessoas"):
        series = numeric[column].dropna()
        numeric_summary[column] = {
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "mean": float(series.mean()) if not series.empty else None,
            "missing": int(numeric[column].isna().sum()),
        }

    # O perfil usa o mesmo tratamento do treinamento para que as contagens do
    # relatório representem exatamente a base que chegará ao modelo.
    target = prepare_modeling_data(data)[TARGET_COLUMN]
    return {
        "rows": int(len(data)), "columns": int(len(data.columns)),
        "column_names": list(data.columns),
        "date_min": dates.min().date().isoformat() if dates.notna().any() else None,
        "date_max": dates.max().date().isoformat() if dates.notna().any() else None,
        "duplicate_rows": int(data.duplicated().sum()),
        "duplicate_ids": int(data["id"].duplicated().sum()),
        "missing_values": {
            column: int(value) for column, value in data.isna().sum().items() if value
        },
        "target_distribution": {
            str(label): int(value) for label, value in target.value_counts().items()
        },
        "numeric_summary": numeric_summary,
        "model_features": MODEL_FEATURE_COLUMNS,
        "excluded_outcome_columns": OUTCOME_COLUMNS,
    }


def save_json(payload: dict[str, Any], path: str | Path) -> None:
    """Salva JSON com UTF-8 e formatação adequada para revisão no Git."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def save_modeling_data(data: pd.DataFrame, path: str | Path) -> None:
    """Salva a base derivada; o .gitignore impede versionar CSVs gerados."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output, index=False, encoding="utf-8")
