"""
Measure what one FitFindr run actually costs (unit 5).

    python measure_cost.py            # 10 runs
    python measure_cost.py --runs 20

Runs the full agent N times with the response cache OFF, so every model call
is a real request, then averages the records those runs wrote to
logs/runs.jsonl. Nothing is estimated: model calls, token counts and seconds
all come from the run log, and the token counts come from the service's own
usage_metadata on each response (see generate.token_counts).

The queries rotate through five that all match, with the example wardrobe, so
every run goes the full path (search → pick → outfit → fit card). An empty
search costs 0 model calls and would drag the average down.
"""

import argparse
import os
import statistics

os.environ["AI201_CACHE"] = "0"  # before config is imported: real calls only

import config  # noqa: E402,F401
import generate  # noqa: E402
import runlog  # noqa: E402
from agent import run_agent  # noqa: E402
from utils.data_loader import get_example_wardrobe  # noqa: E402

QUERIES = [
    "vintage graphic tee under $30",
    "denim jacket under $60",
    "cargo pants under $40",
    "sneakers under $80",
    "y2k top under $25",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--runs", type=int, default=10)
    args = parser.parse_args()

    assert not config.CACHE_ENABLED, "cache must be off for a cost measurement"
    runlog.set_source("measure")

    run_ids = []
    for i in range(args.runs):
        query = QUERIES[i % len(QUERIES)]
        print(f"run {i + 1}/{args.runs}: {query}", flush=True)
        run_agent(query, get_example_wardrobe())
        run_ids.append(runlog.read(1)[0]["run_id"])

    rows = [r for r in runlog.read() if r["run_id"] in set(run_ids)]

    def col(name):
        return [r[name] for r in rows]

    def line(label, values, fmt="{:.1f}"):
        print(f"  {label:<16} mean {fmt.format(statistics.mean(values))}"
              f"   median {fmt.format(statistics.median(values))}"
              f"   min {fmt.format(min(values))}   max {fmt.format(max(values))}")

    total = [r["prompt_tokens"] + r["output_tokens"] for r in rows]
    print(f"\n{len(rows)} runs, cache off, model {config.MODEL}")
    print(f"  statuses         {', '.join(sorted(set(col('status'))))}")
    line("model calls", col("model_calls"))
    line("prompt tokens", col("prompt_tokens"), "{:.0f}")
    line("output tokens", col("output_tokens"), "{:.0f}")
    line("total tokens", total, "{:.0f}")
    line("seconds", col("duration_s"))
    print(f"\n  session total: {generate.usage()}")


if __name__ == "__main__":
    main()
