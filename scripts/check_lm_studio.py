"""Checker: verify LM Studio is up and the loaded model answers.

Usage:  python scripts/check_lm_studio.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key="lm-studio",
)

models = client.models.list()
print("Loaded models:", [m.id for m in models.data])

resp = client.chat.completions.create(
    model=os.getenv("MAS_MODEL") or models.data[0].id,
    messages=[{"role": "user", "content": "Reply with exactly: PONG"}],
    temperature=0,
    max_tokens=10,
)
print("Model says:", resp.choices[0].message.content)
print("Usage:", resp.usage)
