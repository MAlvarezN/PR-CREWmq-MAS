import os
from openai import OpenAI

# using LM studio
client = OpenAI(
    base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
    api_key="lm-studio",
)

models = client.models.list()
print("Loaded models:", [m.id for m in models.data])

resp = client.chat.completions.create(
    model=models.data[0].id,
    messages=[{"role": "user", "content": "Reply with exactly: PONG"}],
    temperature=0,
    max_tokens=10,
)
print("Model says:", resp.choices[0].message.content)
print("Usage:", resp.usage)