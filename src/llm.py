"""LLM client factory: real LM Studio server, or a mock test double.

The mock lets the whole pipeline (workflow, smoke test, IPR loop) run without
LM Studio, e.g. in CI or on a machine without the model loaded. It is a test
double only -- it pattern-matches the prompts; it does not reason.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class CallUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_s: float = 0.0


@dataclass
class ChatResult:
    content: str
    usage: CallUsage = field(default_factory=CallUsage)


class LMStudioClient:
    """Thin wrapper over the OpenAI-compatible LM Studio server."""

    def __init__(self, base_url=None, model=None):
        from openai import OpenAI

        self.client = OpenAI(
            base_url=base_url or os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key="lm-studio",
        )
        self.model = model or os.getenv("MAS_MODEL")
        if not self.model:
            models = self.client.models.list()
            self.model = models.data[0].id

    def chat(self, system_prompt, user_message, temperature=0.0, max_tokens=512) -> ChatResult:
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency = time.perf_counter() - t0
        u = resp.usage
        return ChatResult(
            content=resp.choices[0].message.content,
            usage=CallUsage(
                prompt_tokens=getattr(u, "prompt_tokens", 0) or 0,
                completion_tokens=getattr(u, "completion_tokens", 0) or 0,
                latency_s=latency,
            ),
        )


class MockLLM:
    """Deterministic stand-in for the local model. Test double, not a model."""

    def chat(self, system_prompt, user_message, temperature=0.0, max_tokens=512) -> ChatResult:
        t0 = time.perf_counter()
        if "Synthesize the final concise answer" in user_message:
            content = self._fake_synthesis(user_message)
        elif "produce a JSON tool-call request" in system_prompt:
            content = json.dumps(self._fake_tool_call(user_message))
        elif "Data Specialist" in system_prompt:
            content = self._fake_specialist_answer(user_message)
        else:  # coordinator synthesis
            content = self._fake_synthesis(user_message)
        latency = time.perf_counter() - t0
        return ChatResult(
            content=content,
            usage=CallUsage(
                prompt_tokens=len((system_prompt + user_message).split()),
                completion_tokens=len(content.split()),
                latency_s=latency,
            ),
        )

    @staticmethod
    def _fake_tool_call(query: str) -> dict:
        q = query.lower()
        field = "avg_temp_c"
        for key, fld in [("hot", "max_temp_c"), ("cold", "min_temp_c"),
                         ("warm", "avg_temp_c"), ("pressure", "pressure_pa"),
                         ("wind", "wind_speed_ms")]:
            if key in q:
                field = fld
        operation = "min" if any(k in q for k in ("cold", "lowest", "least", "minimum")) else "max"
        return {"tool": "query_sample_data",
                "arguments": {"operation": operation, "field": field, "n": 1}}

    @staticmethod
    def _fake_specialist_answer(message: str) -> str:
        m = re.search(r"TOOL RESULT: (.+)", message)
        return f"Based on the tool result ({m.group(1) if m else 'no result'}), the answer is derived directly from the dataset."

    @staticmethod
    def _fake_synthesis(message: str) -> str:
        return "Final answer synthesized from the specialist's findings. " + message[:120]


def get_llm():
    """Return a real LM Studio client, or the mock when MAS_MOCK=1."""
    if os.getenv("MAS_MOCK", "0") == "1":
        return MockLLM()
    return LMStudioClient()
