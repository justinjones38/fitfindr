"""
Unit 5 test run: scores the five criteria in criteria.md ("Unit 5 criteria")
once, and writes everything it saw to results/.

    python eval_unit5.py --label run1

One invocation = one run (one column of the run log). Run it three times.

What each criterion needs, and how it's produced here:

  1–3  The 5 matching queries × 2 tries = 10 full runs, example wardrobe,
       cache off. Scored from each run's logs/runs.jsonl record and session.
  4    The same 5 queries × 1, EMPTY wardrobe (the extension's bad input),
       cache off. Scored from the record.
  5    5 tries of a deliberately bad API key, each in its own subprocess
       (`AI201_CACHE=0 GEMINI_API_KEY=bad python app.py ask ... --trace`), so
       the failure is real and the CLI's actual output is what's checked.
       Scored from the subprocess's stdout/stderr and the one new log line.

Every model call is real: AI201_CACHE=0 is set before config is imported, and
asserted.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

os.environ["AI201_CACHE"] = "0"

import config  # noqa: E402
import generate  # noqa: E402
import runlog  # noqa: E402
from agent import run_agent  # noqa: E402
from tools import PICK_TOP_N  # noqa: E402
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe  # noqa: E402
from measure_cost import QUERIES  # noqa: E402

BAD_KEY_QUERY = "vintage graphic tee under $30"

TARGETS = {
    1: ("The pick is always one of the real top 3 search results", 10, 10),
    2: ("With a full wardrobe, the model actually makes the pick", 9, 10),
    3: ("The reason names a real wardrobe piece", 8, 10),
    4: ("An empty wardrobe falls back without a model call for the pick", 5, 5),
    5: ("A failed run leaves a record, not an absence", 5, 5),
}

WARDROBE_NAMES = [i["name"].split(",")[0].strip().lower()
                  for i in get_example_wardrobe()["items"]]


def _last_record() -> dict:
    return runlog.read(1)[0]


def _line_count() -> int:
    return len(runlog.read())


# ── criteria 1–3 ──────────────────────────────────────────────────────────────

def full_wardrobe_tries(out):
    tries = []
    for i in range(10):
        query = QUERIES[i % len(QUERIES)]
        session = run_agent(query, get_example_wardrobe())
        rec = _last_record()
        expected = [r["id"] for r in (session["search_results"] or [])[:PICK_TOP_N]]
        selected_id = (rec["selected"] or {}).get("id")

        c1 = (rec["status"] == "ok" and rec["candidates"] == expected
              and selected_id in expected)
        made_pick = rec["pick_fallback"] is None
        reason = (rec["pick_reason"] or "").lower()
        named = [n for n in WARDROBE_NAMES if n in reason]
        c3 = made_pick and bool(named)

        tries.append({"query": query, "c1": c1, "c2": made_pick, "c3": c3,
                      "made_pick": made_pick, "named": named, "rec": rec,
                      "expected": expected})
        out.append(f"### Full wardrobe, try {i + 1}: `{query}`\n")
        out.append(f"- C1 {'PASS' if c1 else 'FAIL'}: candidates {rec['candidates']} "
                   f"vs first {PICK_TOP_N} of search_results {expected}; selected {selected_id}")
        out.append(f"- C2 {'PASS' if made_pick else 'FAIL'}: pick_fallback = {rec['pick_fallback']!r}")
        out.append(f"- C3 {'PASS' if c3 else ('n/a (fallback)' if not made_pick else 'FAIL')}: "
                   f"wardrobe names found in reason: {named}")
        out.append(f"\n```\n{json.dumps(rec, ensure_ascii=False)}\n```\n")
    return tries


# ── criterion 4 ───────────────────────────────────────────────────────────────

def empty_wardrobe_tries(out):
    tries = []
    for i, query in enumerate(QUERIES):
        session = run_agent(query, get_empty_wardrobe())
        rec = _last_record()
        first = (session["search_results"] or [{}])[0].get("id")
        checks = {
            "selected is first result": (rec["selected"] or {}).get("id") == first,
            "fallback text": rec["pick_fallback"] == "empty wardrobe, nothing to match against",
            "status ok": rec["status"] == "ok",
            "has fit card": bool(rec["fit_card"]),
            "model_calls == 2": rec["model_calls"] == 2,
        }
        ok = all(checks.values())
        tries.append({"query": query, "ok": ok, "checks": checks, "rec": rec})
        out.append(f"### Empty wardrobe, try {i + 1}: `{query}`: {'PASS' if ok else 'FAIL'}\n")
        out.append("- " + ", ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in checks.items())
                   + f" (model_calls={rec['model_calls']}, first result {first})")
        out.append(f"\n```\n{json.dumps(rec, ensure_ascii=False)}\n```\n")
    return tries


# ── criterion 5 ───────────────────────────────────────────────────────────────

def bad_key_tries(out):
    tries = []
    env = dict(os.environ, AI201_CACHE="0", GEMINI_API_KEY="bad", FITFINDR_SOURCE="eval5")
    for i in range(5):
        before = _line_count()
        proc = subprocess.run(
            [sys.executable, "app.py", "ask", BAD_KEY_QUERY, "--trace"],
            cwd=config.ROOT, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
        )
        after = _line_count()
        text = proc.stdout + proc.stderr
        new = runlog.read(after - before) if after > before else []
        rec = new[-1] if new else {}
        checks = {
            "message, no traceback": "Couldn't finish:" in text and "Traceback" not in text,
            "pick fell back": str(rec.get("pick_fallback") or "").startswith("model call failed"),
            "ended at suggest_outfit": ("suggest_outfit" in str(rec.get("error"))
                                        and rec.get("fit_card") is None),
            "exactly 1 new log line": after - before == 1,
            "status error + duration": rec.get("status") == "error"
                                       and isinstance(rec.get("duration_s"), (int, float)),
        }
        ok = all(checks.values())
        tries.append({"ok": ok, "checks": checks, "rec": rec, "text": text})
        out.append(f"### Bad key, try {i + 1}: {'PASS' if ok else 'FAIL'}\n")
        out.append("- " + ", ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in checks.items())
                   + f" (exit code {proc.returncode}, new log lines {after - before})")
        out.append("\nTerminal output (`app.py ask`):\n\n```\n" + text.strip() + "\n```\n")
        out.append(f"Log line:\n\n```\n{json.dumps(rec, ensure_ascii=False)}\n```\n")
    return tries


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="run")
    args = parser.parse_args()
    assert not config.CACHE_ENABLED, "cache must be off"
    runlog.set_source("eval5")

    started = datetime.now()
    detail = []
    detail.append("## Criteria 1–3: full wardrobe, 10 tries\n")
    full = full_wardrobe_tries(detail)
    detail.append("## Criterion 4: empty wardrobe, 5 tries\n")
    empty = empty_wardrobe_tries(detail)
    detail.append("## Criterion 5: bad API key, 5 tries (subprocess)\n")
    bad = bad_key_tries(detail)

    made = [t for t in full if t["made_pick"]]
    scores = {
        1: (sum(t["c1"] for t in full), len(full)),
        2: (sum(t["c2"] for t in full), len(full)),
        3: (sum(t["c3"] for t in made), len(made)),
        4: (sum(t["ok"] for t in empty), len(empty)),
        5: (sum(t["ok"] for t in bad), len(bad)),
    }

    lines = [f"# Unit 5 run: {args.label}", "",
             f"- started {started:%Y-%m-%d %H:%M:%S}, finished {datetime.now():%H:%M:%S}",
             f"- model `{config.MODEL}`, cache off, produced by `eval_unit5.py::main`",
             f"- {generate.usage()} (in-process; the 5 bad-key subprocesses are extra)", "",
             "| Criterion | Target | This run | Met this run? |", "|---|---|---|---|"]
    for n, (name, need, of) in TARGETS.items():
        got, denom = scores[n]
        met = got >= need if n == 3 else got >= need and denom == of
        target = f"{need} of {of}" + (" (of the model-made picks)" if n == 3 else "")
        lines.append(f"| {n}. {name} | {target} | {got}/{denom} | {'yes' if met else 'NO'} |")
    lines.append("")
    text = "\n".join(lines + detail) + "\n"

    path = config.RESULTS_DIR / f"unit5_{started:%Y-%m-%d_%H%M}_{args.label}.md"
    path.write_text(text, encoding="utf-8")
    print("\n".join(lines))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
