"""Single-track two-agent workflow (month-1 LEG).

Topology (fixed this month):
    user query -> [Coordinator] -> tool call -> [Data Specialist] -> [Coordinator] -> final answer

Mirrors the one-track LEG with a single specialist in Zhao et al. 2026, Fig. 2.
"""

from src.agents.coordinator import CoordinatorAgent
from src.agents.specialist import DataSpecialistAgent
from src.llm import get_llm
from src.registry import AgentRegistry
from src.tools.data_tool import TOOLS


def run_workflow(user_query: str, llm=None) -> dict:
    llm = llm or get_llm()
    registry = AgentRegistry()

    coordinator = CoordinatorAgent(llm, registry.get("coordinator"))
    specialist = DataSpecialistAgent(llm, registry.get("data_specialist"), TOOLS)

    call, u1 = coordinator.plan_tool_call(user_query)
    spec_answer, spec_trace = specialist.answer(user_query, call)
    u2 = spec_trace["usage"] if spec_trace else None
    final_answer, u3 = coordinator.synthesize(user_query, spec_answer)

    usages = [u for u in (u1, u2, u3) if u]
    return {
        "query": user_query,
        "tool_call": call,
        "tool_result": spec_trace["result"] if spec_trace else None,
        "specialist_answer": spec_answer,
        "final_answer": final_answer,
        "total_prompt_tokens": sum(u.prompt_tokens for u in usages),
        "total_completion_tokens": sum(u.completion_tokens for u in usages),
        "total_latency_s": round(sum(u.latency_s for u in usages), 3),
    }
