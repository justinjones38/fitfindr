"""
Structured run logging for FitFindr (unit 5).

Every call to agent.run_agent() appends ONE JSON object, on one line, to
logs/runs.jsonl — successful runs, runs that stopped on an empty search, runs
that ended on a model/MCP error, and runs that crashed outright. A failure
leaves a record instead of an absence.

Read it back with:

    python runlog.py            # the last 10 records, one per line
    python runlog.py -n 25      # the last 25

Fields in each record:

    ts               ISO-8601 UTC time the run started
    run_id           short random id, unique per run
    source           who ran it: "cli", "eval", "serve", "measure", ...
    query            what the user typed
    wardrobe_items   how many wardrobe pieces the run had
    parsed           {description, size, max_price} from parse_query
    status           "ok" | "no_results" | "error" | "crash"
    error            the session error message, or the exception for a crash
    n_results        how many listings search_listings returned
    candidates       the listing ids pick_best_match chose between
    selected         {id, title, price, platform} of selected_item
    pick_fallback    None if the model made the pick, otherwise why not
    pick_reason      pick_best_match's one-sentence reason
    fit_card         the caption (the run's final output)
    duration_s       wall-clock seconds for the whole run (includes rate-limit waits)
    model_calls      model requests this run actually sent (cache hits excluded)
    cache_hits       answers served from the local cache this run
    prompt_tokens    input tokens the service reported for this run
    output_tokens    output tokens the service reported for this run
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone

import config
import generate

LOG_DIR = config.ROOT / "logs"
LOG_FILE = LOG_DIR / "runs.jsonl"

# Who is running the agent. app.py / run_eval.py / serve.py / measure_cost.py
# set this so the log says where a record came from.
SOURCE = os.getenv("FITFINDR_SOURCE", "python")


def set_source(name: str) -> None:
    global SOURCE
    SOURCE = name


def _snapshot() -> dict:
    tokens = generate.token_counts()
    return {
        "calls": generate.call_count(),
        "cache_hits": generate._cache_hits,
        "prompt": tokens["prompt"],
        "output": tokens["output"],
    }


def start() -> dict:
    """Call at the top of a run. Returns the context finish() needs."""
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_id": uuid.uuid4().hex[:8],
        "t0": time.perf_counter(),
        "before": _snapshot(),
    }


def finish(ctx: dict, query: str, wardrobe: dict, session: dict | None,
           crash: BaseException | None = None) -> dict:
    """
    Write one record for the run and return it. Never raises: a logging
    problem must not turn a working run into a failed one.
    """
    try:
        after = _snapshot()
        before = ctx["before"]
        session = session or {}
        item = session.get("selected_item") or {}
        pick = session.get("pick") or {}

        if crash is not None:
            status = "crash"
            error = f"{type(crash).__name__}: {crash}"
        elif session.get("error"):
            status = "no_results" if session.get("error_kind") == "no_results" else "error"
            error = session["error"]
        else:
            status = "ok"
            error = None

        record = {
            "ts": ctx["ts"],
            "run_id": ctx["run_id"],
            "source": SOURCE,
            "query": query,
            "wardrobe_items": len((wardrobe or {}).get("items") or []),
            "parsed": session.get("parsed") or None,
            "status": status,
            "error": error,
            "n_results": len(session.get("search_results") or []),
            "candidates": pick.get("candidates"),
            "selected": ({k: item.get(k) for k in ("id", "title", "price", "platform")}
                         if item else None),
            "pick_fallback": pick.get("fallback"),
            "pick_reason": pick.get("reason"),
            "fit_card": session.get("fit_card"),
            "duration_s": round(time.perf_counter() - ctx["t0"], 2),
            "model_calls": after["calls"] - before["calls"],
            "cache_hits": after["cache_hits"] - before["cache_hits"],
            "prompt_tokens": after["prompt"] - before["prompt"],
            "output_tokens": after["output"] - before["output"],
        }

        LOG_DIR.mkdir(exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record
    except Exception as exc:  # noqa: BLE001
        print(f"  [runlog] couldn't write the run log: {exc}", flush=True)
        return {}


def read(n: int | None = None) -> list[dict]:
    """The last n records (all of them if n is None), oldest first."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    return records if n is None else records[-n:]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Print recent FitFindr run records")
    parser.add_argument("-n", type=int, default=10, help="how many records")
    args = parser.parse_args()
    rows = read(args.n)
    if not rows:
        print(f"No records yet in {LOG_FILE}")
    for row in rows:
        print(json.dumps(row, ensure_ascii=False))
