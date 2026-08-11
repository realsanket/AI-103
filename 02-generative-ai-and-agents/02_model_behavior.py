# Run: uv run python 02-generative-ai-and-agents/02_model_behavior.py

"""Temperature parameter — same prompt, three generation regimes.

The `temperature` parameter controls how deterministically the model samples
from its probability distribution. 0.0 → reproducible outputs; 2.0 → high
entropy and creative divergence. This lesson runs the same prompt through
three values so you can compare outputs side by side.

Note: temperature is model-dependent. The code hard-codes `gpt-4.1` because
only specific models accept the full 0–2 range; check deployment capability
before using temperature > 1.0.

What to watch:
  Temperature 0.0 output is nearly identical on repeated runs.
  Temperature 2.0 output changes significantly between runs.
  Temperature is NOT a safety, truth, grounding, or quality control.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  (model is hard-coded to gpt-4.1; no DEFAULT_MODEL needed)
"""
from _shared.openai_client import openai_client
from _shared.config import settings


def creative_tagline(temperature: float) -> str:
    client = openai_client()
    r = client.responses.create(
        #hard coding model since temprature can be use with set of specific models.
        model="gpt-4.1",
        instructions="You are a creative copywriter.",
        input="Write a two-sentence tagline for a new AI-powered productivity app.",
        temperature=temperature,
    )
    return r.output_text


def main() -> None:
    for t in (0.0, 1.0, 2.0):
        print(f"\n--- temperature={t} ---")
        print(creative_tagline(t))


if __name__ == "__main__":
    main()
