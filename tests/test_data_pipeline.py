import unittest

import pandas as pd

from src.data_pipeline import OUTCOME_COLUMNS, TARGET_COLUMN, prepare_modeling_data


class DataPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        # Fixture pequena que reproduz os casos importantes da base real:
        # rótulo ausente, decimal com vírgula e variáveis de desfecho.
        self.data = pd.DataFrame(
            {
                "classificacao_acidente": [pd.NA, "Sem Vítimas", "Com Vítimas Feridas"],
                "dia_semana": ["quinta-feira"] * 3,
                "horario": ["04:04:00", "12:30:00", "18:45:00"],
                "causa_acidente": ["Causa A"] * 3,
                "tipo_acidente": ["Tipo A"] * 3,
                "fase_dia": ["Pleno dia"] * 3,
                "condicao_metereologica": ["Céu claro"] * 3,
                "tipo_pista": ["Simples"] * 3,
                "tracado_via": ["Reta"] * 3,
                "uso_solo": ["Rural"] * 3,
                "br": ["101", "101", "222"],
                "km": ["146,1", "20", "393,4"],
                "veiculos": [2, 1, 3],
                "pessoas": [3, 1, 4],
                "mortos": [1, 0, 0],
                "feridos": [0, 0, 2],
                "feridos_leves": [0, 0, 2],
                "feridos_graves": [0, 0, 0],
                "ilesos": [2, 1, 2],
                "ignorados": [0, 0, 0],
            }
        )

    def test_missing_target_is_derived_from_outcomes(self) -> None:
        modeling = prepare_modeling_data(self.data)
        self.assertEqual(modeling[TARGET_COLUMN].tolist()[0], "Com Vítimas Fatais")

    def test_decimal_comma_is_preserved_as_numeric(self) -> None:
        modeling = prepare_modeling_data(self.data)
        self.assertAlmostEqual(modeling["km"].iloc[0], 146.1)
        self.assertEqual(modeling["hora"].tolist(), [4, 12, 18])

    def test_outcome_columns_do_not_enter_modeling_data(self) -> None:
        # Esta proteção evita que o modelo receba informações descobertas
        # somente depois do acidente.
        modeling = prepare_modeling_data(self.data)
        self.assertTrue(set(OUTCOME_COLUMNS).isdisjoint(modeling.columns))
        self.assertEqual(len(modeling), 3)


if __name__ == "__main__":
    unittest.main()
