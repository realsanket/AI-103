# Run: uv run python 02-generative-ai-and-agents/31_openai_embeddings.py [--apply --model <embeddings-deployment>]
"""Call an Azure OpenAI embeddings deployment; print vector dim + first values.

Embeddings turn text into fixed-length vectors for semantic search + RAG.
Different from a chat/completion deployment — needs a dedicated embeddings
model deployment (`text-embedding-3-small`, `text-embedding-3-large`, ada).

Default preflight validates env. `--apply` sends ONE batch (default 3
strings) via `openai_client().embeddings.create()` and prints (input, dim,
first-4 values, magnitude). Vectors themselves are truncated — the goal is
proving deployment + dimensions before wiring to Search/vector-store.

Same dimensions across inputs = same index/table. Different embedding
deployment = separate vector-store (do NOT mix).

Code path:
  --apply: openai_client().embeddings.create(model=deployment, input=[texts])
  → per response.data[i]: len(embedding) + embedding[:4] + sum(x*x)**0.5.

What to watch. `dim: 1536` (or 3072 for large). Magnitudes near 1.0 (models
return normalized vectors). Different inputs → different first-4 values but
same dim.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT     — Azure OpenAI resource URL
  --model NAME              — embeddings deployment (required with --apply)
  --apply                   — send billable batch
"""
import argparse

from _shared.openai_client import openai_client

_SAMPLES = [
    "Northwind support policy",
    "Refund window is 30 days",
    "Model catalog listing agents",
]


def preflight() -> None:
    print("Embeddings preflight (no cloud calls).")
    print("- Needs a dedicated embeddings deployment, not a chat deployment.")
    print("- Vector dims differ by model: 1536 (small/ada), 3072 (large).")


def apply(model: str) -> None:
    response = openai_client().embeddings.create(model=model, input=_SAMPLES)
    for text, item in zip(_SAMPLES, response.data):
        vec = item.embedding
        mag = sum(v * v for v in vec) ** 0.5
        print(f"{text!r}: dim={len(vec)} first4={[round(v, 4) for v in vec[:4]]} mag={mag:.4f}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Call an embeddings deployment.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", help="Embeddings deployment name.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.model:
        parser.error("--apply requires --model.")
    apply(args.model)


if __name__ == "__main__":
    main()
