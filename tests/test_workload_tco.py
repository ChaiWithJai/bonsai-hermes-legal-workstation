import argparse
import unittest
import json
from pathlib import Path

from workload_tco import analyze


class WorkloadTcoTest(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace(
            session="fixture.json",
            monthly_attempts=10,
            machine_price=1200,
            amortization_months=12,
            idle_watts=100,
            incremental_watts=100,
            online_hours=100,
            end_to_end_seconds=3600,
            electricity_per_kwh=1,
            local_operations_month=10,
            hosted_operations_month=20,
            local_review_per_attempt=2,
            hosted_review_per_attempt=3,
            hosted_input_per_million=1000,
            hosted_output_per_million=2000,
            local_acceptance_rate=0.5,
            hosted_acceptance_rate=1,
        )

    def test_costs_use_captured_tokens_and_acceptance(self):
        session = {
            "session_id": "test-session",
            "calls": [
                {"input_tokens": 500, "output_tokens": 50},
                {"input_tokens": 500, "output_tokens": 50},
                {"api_call_count": 1, "input_tokens": 500, "output_tokens": 200},
            ],
        }
        result = analyze(session, self.args)
        self.assertEqual(result["observed_from_session"], {
            "model_api_calls": 3, "input_tokens": 1500, "output_tokens": 300
        })
        self.assertEqual(result["monthly_projection"]["local_total"], 141)
        self.assertEqual(result["monthly_projection"]["local_cost_per_accepted_task"], 28.2)
        self.assertEqual(result["monthly_projection"]["hosted_total"], 71)
        self.assertEqual(result["monthly_projection"]["hosted_cost_per_accepted_task"], 7.1)

    def test_capacity_flag_identifies_infeasible_volume(self):
        self.args.monthly_attempts = 101
        session = {"calls": [{"api_call_count": 1, "input_tokens": 1, "output_tokens": 1}]}
        result = analyze(session, self.args)
        self.assertTrue(result["monthly_projection"]["volume_exceeds_capacity_upper_bound"])

    def test_connected_assignment_includes_auxiliary_request(self):
        source = Path(__file__).resolve().parents[1] / "evidence/slack-anthony-request-usage.json"
        session = json.loads(source.read_text())
        result = analyze(session, self.args)
        self.assertEqual(result["observed_from_session"], {
            "model_api_calls": 4, "input_tokens": 9735, "output_tokens": 1436})
        self.assertAlmostEqual(result["monthly_projection"]["hosted_total"], 176.07)
        session["session_title_requests"] = session["main_requests"][:1]
        with self.assertRaisesRegex(ValueError, "Duplicate exchange"):
            analyze(session, self.args)

    def test_auxiliary_usage_cannot_be_silently_omitted(self):
        with self.assertRaisesRegex(ValueError, "explicitly include"):
            analyze({"main_requests": [{}]}, self.args)

    def test_summary_usage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "per-call"):
            analyze({"usage": [{"input_tokens": 7307, "output_tokens": 4287}]}, self.args)

    def test_repeated_context_is_counted_on_each_call(self):
        result = analyze({"calls": [{"input_tokens": 1000, "output_tokens": 10},
                                     {"input_tokens": 1100, "output_tokens": 20}]}, self.args)
        self.assertEqual(result["observed_from_session"]["input_tokens"], 2100)


if __name__ == "__main__":
    unittest.main()
