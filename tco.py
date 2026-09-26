"""Illustrative monthly local versus external inference cost calculation."""
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--machine-price", type=float, required=True)
parser.add_argument("--amortization-months", type=float, required=True)
parser.add_argument("--active-watts", type=float, required=True)
parser.add_argument("--active-hours-month", type=float, required=True)
parser.add_argument("--power-price-kwh", type=float, required=True)
parser.add_argument("--operations-month", type=float, required=True)
parser.add_argument("--requests-month", type=float, required=True)
parser.add_argument("--input-tokens-request", type=float, required=True)
parser.add_argument("--output-tokens-request", type=float, required=True)
parser.add_argument("--external-input-per-million", type=float, required=True)
parser.add_argument("--external-output-per-million", type=float, required=True)
args = parser.parse_args()
if any(value < 0 for value in vars(args).values()) or args.amortization_months <= 0:
    parser.error("Costs and workload must be nonnegative; amortization months must be positive")
local = (args.machine_price / args.amortization_months
         + args.active_watts / 1000 * args.active_hours_month * args.power_price_kwh
         + args.operations_month)
external_per_request = (args.input_tokens_request * args.external_input_per_million
                        + args.output_tokens_request * args.external_output_per_million) / 1_000_000
external = args.requests_month * external_per_request
break_even = local / external_per_request if external_per_request else float("inf")
print("Illustrative assumptions only. This does not measure model throughput or quality.")
print(f"Local monthly cost: ${local:,.2f}")
print(f"External monthly cost: ${external:,.2f}")
print(f"Requests per month at cost parity: {break_even:,.0f}" if break_even != float("inf") else
      "Cost parity cannot be calculated with a zero external request price.")
