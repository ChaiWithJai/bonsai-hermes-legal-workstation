"""Analyze one captured Hermes session as a workload, with explicit cost assumptions.

This is a planning model. It does not measure power, quality, hosted performance,
or the missing Slack -> Drive -> Sheets transaction.
"""

import argparse
import json
from pathlib import Path


def nonnegative(value):
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("value must be nonnegative")
    return number


def positive(value):
    number = nonnegative(value)
    if number == 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return number


def fraction(value):
    number = positive(value)
    if number > 1:
        raise argparse.ArgumentTypeError("value must be at most 1")
    return number


def analyze(session, args):
    usage = session.get("calls")
    if not isinstance(usage, list) or not usage:
        raise ValueError("Provide per-call usage in calls; session summary totals are not billable request totals")
    for row in usage:
        for field in ("input_tokens", "output_tokens"):
            if type(row.get(field)) is not int or row[field] < 0:
                raise ValueError("Per-call token counts must be nonnegative integers")
    inputs = sum(row["input_tokens"] for row in usage)
    outputs = sum(row["output_tokens"] for row in usage)
    calls = len(usage)
    volume = args.monthly_attempts
    local_fixed = (
        args.machine_price / args.amortization_months
        + args.idle_watts * args.online_hours / 1000 * args.electricity_per_kwh
        + args.local_operations_month
    )
    local_variable = (
        args.incremental_watts * args.end_to_end_seconds / 3_600_000
        * args.electricity_per_kwh
        + args.local_review_per_attempt
    )
    hosted_variable = (
        (inputs * args.hosted_input_per_million
         + outputs * args.hosted_output_per_million) / 1_000_000
        + args.hosted_review_per_attempt
    )
    local_total = local_fixed + volume * local_variable
    hosted_total = args.hosted_operations_month + volume * hosted_variable
    single_slot_capacity = args.online_hours * 3600 / args.end_to_end_seconds
    return {
        "status": "illustrative_planning_model_not_measured_savings",
        "session_id": session.get("session_id"),
        "session_scope": session.get("scope"),
        "observed_from_session": {
            "model_api_calls": calls,
            "input_tokens": inputs,
            "output_tokens": outputs,
        },
        "assumptions": {
            key: value for key, value in vars(args).items() if key != "session"
        },
        "monthly_projection": {
            "local_total": round(local_total, 2),
            "hosted_total": round(hosted_total, 2),
            "local_cost_per_accepted_task": round(
                local_total / (volume * args.local_acceptance_rate), 4
            ),
            "hosted_cost_per_accepted_task": round(
                hosted_total / (volume * args.hosted_acceptance_rate), 4
            ),
            "single_slot_capacity_upper_bound_attempts": int(single_slot_capacity),
            "volume_exceeds_capacity_upper_bound": volume > single_slot_capacity,
        },
        "exclusions": [
            "The captured legal assignment is a direct local Hermes session, not a connected Slack to Drive to Sheets task.",
            "Power, end-to-end duration, acceptance rates, hosted prices, review labor and operations are supplied assumptions.",
            "All input tokens are priced at the supplied input rate; cached-input discounts are not modeled.",
            "Hosted token usage is assumed equal to the local captured session; a hosted comparator must be measured separately.",
            "Capacity is an optimistic one-slot bound and excludes queueing, maintenance and external tool time variation.",
            "Quality and latency have not been matched against a hosted model on the same task.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    for name, typ in [
        ("monthly-attempts", positive),
        ("machine-price", nonnegative),
        ("amortization-months", positive),
        ("idle-watts", nonnegative),
        ("incremental-watts", nonnegative),
        ("online-hours", positive),
        ("end-to-end-seconds", positive),
        ("electricity-per-kwh", nonnegative),
        ("local-operations-month", nonnegative),
        ("hosted-operations-month", nonnegative),
        ("local-review-per-attempt", nonnegative),
        ("hosted-review-per-attempt", nonnegative),
        ("hosted-input-per-million", nonnegative),
        ("hosted-output-per-million", nonnegative),
        ("local-acceptance-rate", fraction),
        ("hosted-acceptance-rate", fraction),
    ]:
        parser.add_argument("--" + name, type=typ, required=True)
    args = parser.parse_args()
    try:
        result = analyze(json.loads(args.session.read_text()), args)
    except (ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
