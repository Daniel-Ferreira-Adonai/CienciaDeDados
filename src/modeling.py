"""Modelos iniciais e metricas para estabelecer uma linha de base"""

from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data_pipeline import (
    CATEGORICAL_COLUMNS, MODEL_FEATURE_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN,
)


def _one_hot_encoder() -> OneHotEncoder:
    """Mantém compatibilidade entre versões recentes e anteriores do sklearn."""

    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=True)


def build_baseline_pipeline() -> Pipeline:
    # O pré-processamento fica dentro do Pipeline para ser ajustado apenas no
    # conjunto de treino, evitando vazamento de informação para o teste.
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", _one_hot_encoder()),
        ]
    )
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[
            ("categorical", categorical, CATEGORICAL_COLUMNS),
            ("numeric", numeric, NUMERIC_COLUMNS),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            (
                "classifier",
                # O balanceamento dá mais peso às classes minoritárias e torna
                # o F1 macro uma referência mais informativa que a acurácia.
                LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            ),
        ]
    )


def evaluate_baseline(
    data: pd.DataFrame, random_state: int = 42
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Treina uma regressão logística e retorna métricas e matriz de confusão."""

    features, target = data[MODEL_FEATURE_COLUMNS], data[TARGET_COLUMN]
    # A estratificação mantém aproximadamente a mesma proporção de classes em
    # treino e teste, essencial para comparar modelos de forma justa.
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=random_state, stratify=target,
    )
    model = build_baseline_pipeline()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    labels = sorted(target.dropna().unique().tolist())
    # Fixar a ordem dos rótulos torna a matriz de confusão comparável entre
    # execuções e entre os futuros modelos da equipe.
    matrix = pd.DataFrame(
        confusion_matrix(y_test, predictions, labels=labels), index=labels, columns=labels
    )
    report = classification_report(
        y_test, predictions, labels=labels, output_dict=True, zero_division=0
    )
    metrics = {
        "model": "LogisticRegression + OneHotEncoder",
        "random_state": random_state, "test_size": 0.2,
        "n_train": int(len(x_train)), "n_test": int(len(x_test)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, predictions)),
        "precision_macro": float(precision_score(y_test, predictions, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, predictions, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
        "classification_report": report,
    }
    return metrics, matrix
