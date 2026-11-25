"""The specialist agent's tool: query the sample NASA dataset.

Month 1: a single local JSON file stands in for the real archive/API.
The tool surface is deliberately small and bulk-oriented (cf. the token
store's design note that agents should prefer bulk queries).
"""

import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "sample_nasa_data.json"

_OPERATIONS = {"max", "min", "avg", "list"}


def query_sample_data(operation: str, field: str, n: int = 3) -> dict:
    records = json.loads(DATA_PATH.read_text())["records"]

    if operation not in _OPERATIONS:
        return {"error": f"unknown operation '{operation}', expected one of {sorted(_OPERATIONS)}"}
    if field not in records[0]:
        return {"error": f"unknown field '{field}', available: {sorted(records[0])}"}

    if operation == "list":
        return {"operation": operation, "field": field, "records": records[:n]}

    best = max(records, key=lambda r: r[field]) if operation == "max" else \
           min(records, key=lambda r: r[field]) if operation == "min" else None
    if best is not None:
        return {"operation": operation, "field": field, "record": best}
    return {"operation": "avg", "field": field,
            "value": round(sum(r[field] for r in records) / len(records), 3)}


TOOLS = {"query_sample_data": query_sample_data}
