# Run: uv run python 02-generative-ai-and-agents/02_model_behavior.py [--model <deployment>]
# Practice-question coverage: Q99, Q108.

"""Temperature parameter — same prompt, three generation regimes.

The `temperature` parameter controls how deterministically the model samples
from its probability distribution. 0.0 → reproducible outputs; 2.0 → high
entropy and creative divergence. This lesson runs the same prompt through
three values so you can compare outputs side by side.

Note: temperature is model-dependent. Non-reasoning chat models such as the
GPT-4.1 family accept the full 0–2 range; reasoning models (o-series, GPT-5
family) reject or ignore it and are steered with `reasoning.effort` instead.
Pass `--model` with a non-reasoning deployment name if DEFAULT_MODEL points
at a reasoning model.

What to watch:
  Temperature 0.0 output is nearly identical on repeated runs.
  Temperature 2.0 output changes significantly between runs.
  Temperature is NOT a safety, truth, grounding, or quality control.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT — Azure OpenAI-compatible base URL
  DEFAULT_MODEL         — non-reasoning chat deployment (or pass --model)
"""
import argparse

from _shared.openai_client import openai_client
from _shared.config import settings


def creative_tagline(temperature: float, model: str) -> str:
    client = openai_client()
    r = client.responses.create(
        model=model,
        instructions="You are a creative copywriter.",
        input="Write a two-sentence tagline for a new AI-powered productivity app.",
        temperature=temperature,
    )
    return r.output_text


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", help="Non-reasoning chat deployment name (defaults to DEFAULT_MODEL).")
    args = parser.parse_args(argv)
    model = args.model or settings().default_model
    print(f"Deployment: {model}")
    for t in (0.0, 1.0, 2.0):
        print(f"\n--- temperature={t} ---")
        print(creative_tagline(t, model))


if __name__ == "__main__":
    main()
