"""Smoke test: run the two-agent workflow on simple queries and log
token usage + latency per run (appended to logs/smoke_test.jsonl).

Usage:
    python -m scripts.smoke_test            # needs LM Studio running
    MAS_MOCK=1 python -m scripts.smoke_test # test-double mode
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.workflow import run_workflow

QUERIES = [
    "Which sol had the hottest maximum temperature?",
    "Which sol had the coldest minimum temperature?",
    "What was the average temperature across all sols?",
    "List the first 3 sols with their pressure.",
]

LOG = Path(__file__).resolve().parent.parent / "logs" / "smoke_test.jsonl"


def main():
    for q in QUERIES:
        out = run_workflow(q)
        entry = {"ts": datetime.now(timezone.utc).isoformat(),
                 "mock": out["total_latency_s"] < 0.01, **out}
        with LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[{out['total_latency_s']:>6.3f}s | "
              f"{out['total_prompt_tokens']:>4} in / {out['total_completion_tokens']:>3} out tok] {q}")
        print(f"    tool: {out['tool_call']} -> {out['tool_result']}")
        print(f"    final: {out['final_answer'][:140]}")


if __name__ == "__main__":
    main()
