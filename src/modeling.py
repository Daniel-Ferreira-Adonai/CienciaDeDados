"""Modelos iniciais e metricas para estabelecer uma linha de base"""

from __future__ import annotations

from typing import Any

import pandas as pd
from category_encoders import TargetEncoder
from imblearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .data_pipeline import (
    CATEGORICAL_HIGH_CARDINALITY_COLUMNS, CATEGORICAL_LOW_CARDINALITY_COLUMNS,
    MODEL_FEATURE_COLUMNS, NUMERIC_COLUMNS, TARGET_COLUMN, TRACADO_FLAG_COLUMNS,
)

NUMERIC_AND_FLAG_COLUMNS = [*NUMERIC_COLUMNS, *TRACADO_FLAG_COLUMNS]


def _one_hot_encoder() -> OneHotEncoder:
    """Mantém compatibilidade entre versões recentes e anteriores do sklearn."""

    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def build_baseline_pipeline() -> Pipeline:
    # O pré-processamento fica dentro do Pipeline para ser ajustado apenas no
    # conjunto de treino, evitando vazamento de informação para o teste.
    categorical_low_card = SklearnPipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", _one_hot_encoder()),
        ]
    )
    # causa_acidente (69 categorias) e br (110 categorias) são codificadas pela
    # média do alvo em vez de one-hot: one-hot nessas duas colunas geraria ~180
    # colunas majoritariamente esparsas e categorias nunca vistas no treino
    # apareceriam no teste. TargetEncoder resume cada categoria em um único
    # número (a taxa média do alvo naquela categoria) e, como o sklearn ajusta
    # o ColumnTransformer apenas no treino, não há vazamento do teste.
    categorical_high_card = SklearnPipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("target_encode", TargetEncoder()),
        ]
    )
    numeric = SklearnPipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[
            ("categorical_low_card", categorical_low_card, CATEGORICAL_LOW_CARDINALITY_COLUMNS),
            ("categorical_high_card", categorical_high_card, CATEGORICAL_HIGH_CARDINALITY_COLUMNS),
            ("numeric", numeric, NUMERIC_AND_FLAG_COLUMNS),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            # A literatura consultada (Seção 2) recomenda reamostragem (SMOTE,
            # SMOTEENN) em vez de só ponderar a função de perda para melhorar a
            # detecção da classe minoritária (Com Vítimas Fatais). Testamos as
            # duas opções nesta mesma regressão logística: SMOTE sozinho (F1
            # macro 0,480) ficou próximo do class_weight="balanced" (0,480), e
            # SMOTEENN piorou bastante (F1 macro 0,374), pois a limpeza de
            # vizinhos (ENN) derrubou a precisão nas classes majoritárias. Como
            # nenhuma reamostragem superou o class_weight para esta baseline
            # linear, o passo fica como "passthrough" por padrão; a literatura
            # trata resampling como mais eficaz combinado a modelos de árvore,
            # então a comparação deve ser refeita quando esses algoritmos
            # entrarem em 3.4 (basta chamar model.set_params(resample=SMOTE())
            # ou resample=SMOTEENN(), ambos de imblearn, sem reescrever o resto
            # do pipeline).
            ("resample", "passthrough"),
            (
                "classifier",
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
        "model": "LogisticRegression + OneHotEncoder (baixa cardinalidade) + TargetEncoder (alta cardinalidade)",
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
