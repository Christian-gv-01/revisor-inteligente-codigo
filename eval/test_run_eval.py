"""Pruebas del cálculo y contrato, independientes de ChromaDB y Gemini."""
import copy
import unittest
from run_eval import DEFAULT_DATA, load_cases, retrieval_metrics, analysis_metrics, summarize, validate_response


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.case = load_cases(DEFAULT_DATA)[0]
        self.finding = dict(linea=2, categoria="Inyección SQL", titulo="SQL concatenado",
                            severidad="alta", explicacion="Entrada no confiable", correccion_sugerida="Parametrizar",
                            referencias=["seguridad_python-002"])
        self.response = dict(archivo=self.case["archivo"], estado="analizado", hallazgos=[self.finding],
                             fuentes=[dict(id="seguridad_python-002", documento="seguridad_python.md", seccion="Regla 2", fuente="OWASP", url="https://owasp.org")])

    def test_dataset_balance(self):
        cases = load_cases(DEFAULT_DATA)
        self.assertEqual(len(cases), 20)
        self.assertEqual(sum(bool(c["hallazgos_esperados"]) for c in cases), 12)
        self.assertEqual(sum(c["estado_esperado"] == "abstenido" for c in cases), 2)

    def test_ranking_and_duplicates(self):
        result = retrieval_metrics(["x", "a", "a", "b"], ["a", "b"], 3)
        self.assertAlmostEqual(result["precision_at_k"], 2/3)
        self.assertEqual(result["recall_at_k"], 1)
        self.assertEqual(result["mrr_at_k"], .5)

    def test_empty_expected_is_not_perfect_recall(self):
        result = retrieval_metrics([], [], 3)
        self.assertIsNone(result["recall_at_k"])
        self.assertEqual(result["sin_fuentes_fuera_cobertura"], 1)

    def test_fewer_than_k_uses_fixed_denominator(self):
        self.assertEqual(retrieval_metrics(["a"], ["a"], 3)["precision_at_k"], 1/3)

    def test_duplicate_finding_counts_as_false_positive(self):
        self.response["hallazgos"].append(copy.deepcopy(self.finding))
        result = analysis_metrics(self.case, self.response)
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (1, 1, 0))
        self.assertFalse(result["acierto_caso"])

    def test_wrong_line_does_not_match(self):
        self.finding["linea"] = 1
        result = analysis_metrics(self.case, self.response)
        self.assertEqual((result["tp"], result["fp"], result["fn"]), (0, 1, 1))

    def test_unresolved_citation_is_not_grounding(self):
        self.finding["referencias"] = ["inventada"]
        result = analysis_metrics(self.case, self.response)
        self.assertEqual(result["referencias_resueltas"], 0)
        self.assertEqual(result["hallazgos_con_citas_resueltas"], 0)

    def test_abstention_is_not_safe_true_negative(self):
        case = load_cases(DEFAULT_DATA)[4]
        self.response.update(archivo=case["archivo"], estado="abstenido", hallazgos=[])
        self.assertFalse(analysis_metrics(case, self.response)["acierto_caso"])

    def test_error_only_run_has_no_quality_score(self):
        rows = [dict(estado_ejecucion="error", duracion_ms=1)]
        summary = summarize(rows, "api")
        self.assertEqual(summary["errores"], 1)
        self.assertIsNone(summary["f1"])
        self.assertIsNone(summary["recall_at_k"])
        self.assertEqual(summary["tasa_completitud"], 0)

    def test_contract_rejects_inconsistent_abstention_and_boolean_line(self):
        validate_response(self.response, self.case)
        self.response["estado"] = "abstenido"
        with self.assertRaises(ValueError):
            validate_response(self.response, self.case)
        self.response["estado"] = "analizado"
        self.finding["linea"] = True
        with self.assertRaises(ValueError):
            validate_response(self.response, self.case)


if __name__ == "__main__":
    unittest.main()
