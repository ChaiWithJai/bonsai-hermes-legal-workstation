import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('serve_cost',Path(__file__).resolve().parents[1]/'scripts/serve_cost.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class CostWorksheetTests(unittest.TestCase):
    def values(self):
        values=dict.fromkeys(module.FIELDS,0.0)
        values.update(monthly_attempts=100,machine_price=3600,amortization_months=36,online_hours=100,end_to_end_seconds=60,local_acceptance_rate=.5,hosted_acceptance_rate=1,hosted_input_per_million=1,hosted_output_per_million=2)
        return values
    def test_connected_usage_includes_auxiliary_request(self):
        result=module.calculate(self.values())
        self.assertEqual(result['observed_from_session'],dict(model_api_calls=4,input_tokens=9735,output_tokens=1436))
        self.assertEqual(result['monthly_projection']['local_cost_per_accepted_task'],2)
        self.assertEqual(result['monthly_projection']['hosted_cost_per_accepted_task'],.0126)
        self.assertEqual(result['monthly_projection']['single_slot_capacity_upper_bound_attempts'],6000)
    def test_invalid_assumptions(self):
        for key,value in [('monthly_attempts',0),('machine_price',float('nan')),('local_acceptance_rate',1.1),('idle_watts',True)]:
            with self.subTest(key=key),self.assertRaises(ValueError):module.calculate(self.values()|{key:value})
        with self.assertRaises(ValueError):module.calculate({})
