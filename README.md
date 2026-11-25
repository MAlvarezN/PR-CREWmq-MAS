# MAS over NASA Data — Month 1 Prototype

Two-agent single-track workflow running on a local LLM (LM Studio + Qwen2.5-7B),
following the architecture of the cited papers (see `docs/ipr_design.md`).

## Topology (month-1 LEG)

```
user query -> [Coordinator] -> tool call -> [Data Specialist] -> [Coordinator] -> answer
```

Mirrors the one-track LEG with a single specialist (Zhao et al. 2026, Fig. 2).
LEG design by the coordinator LLM is future work; the track is hardcoded this
month.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

1. Start LM Studio, load **qwen2.5-7b**, and start the local server (default
   port 1234).
2. Verify the connection:

```bash
python scripts/check_lm_studio.py
```

## Run

```bash
python -m scripts.smoke_test     # 4 queries, logs tokens + latency to logs/smoke_test.jsonl
python -m scripts.ipr_loop       # IPR skeleton: test -> feedback -> prompt refinement
```

Test the pipeline without LM Studio (deterministic test double):

```bash
MAS_MOCK=1 python -m scripts.smoke_test
MAS_MOCK=1 python -m scripts.ipr_loop
```

## Structure

```
registry/agents.json    agent registry (id, kind, system_prompt, router_capabilities, tool_names)
src/llm.py              LM Studio client + mock test double
src/registry.py         registry loader
src/workflow.py         single-track workflow runner
src/agents/             coordinator + data specialist
src/tools/data_tool.py  query_sample_data over data/sample_nasa_data.json
scripts/                checker, smoke test, IPR loop
data/                   sample NASA-style dataset (month-1 placeholder)
logs/                   smoke test + IPR runs (JSONL)
docs/                   design notes
```

## Known month-1 limitations

- Topology hardcoded; no LLM-driven LEG generation (Graph Architect).
- One dataset, one tool, four operations — the real archive/API integration and
  the token store come in month 2.
- IPR refines prompts in memory only; persistence back to `registry/agents.json`
  is month-2 work.
