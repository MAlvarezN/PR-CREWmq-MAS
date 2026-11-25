"""Coordinator agent: routes the user query and synthesizes the final answer.

Month 1: the LEG (layer execution graph) is a single hardcoded track
coordinator -> data_specialist -> coordinator, per the two-agent scope.
LLM-driven LEG design by the coordinator is future work (cf. Graph
Architect, Zhao et al. 2026).
"""

import json


class CoordinatorAgent:
    def __init__(self, llm, registry_entry: dict):
        self.llm = llm
        self.system_prompt = registry_entry["system_prompt"]

    def plan_tool_call(self, user_query: str):
        """Step 1: turn the user query into a structured tool-call request."""
        msg = ("User query: " + user_query +
               "\nProduce ONLY the JSON tool-call request, no prose.")
        result = self.llm.chat(self.system_prompt, msg)
        raw = result.content.strip()
        try:
            # tolerate markdown code fences around the JSON
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            call = json.loads(raw)
        except json.JSONDecodeError:
            call = {"tool": None, "arguments": {}, "raw": raw,
                    "error": "coordinator did not return valid JSON"}
        return call, result.usage

    def synthesize(self, user_query: str, specialist_answer: str):
        """Step 3: final user-facing answer from the specialist's findings."""
        msg = (f"User query: {user_query}\nSpecialist's findings: {specialist_answer}\n"
               "Synthesize the final concise answer for the user.")
        result = self.llm.chat(self.system_prompt, msg)
        return result.content, result.usage
