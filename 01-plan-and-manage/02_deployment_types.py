# Run: uv run python 01-plan-and-manage/02_deployment_types.py
"""Choose a deployment type — decision helper + cheatsheet.

Beginner note:
  When you deploy a model, you pick a SKU. The SKU decides HOW you pay
  (per-token vs reserved capacity vs batch) and WHERE inference runs
  (any region / EU-US-APAC zone / one specific region). Nine common types,
  plus Instant / Developer / Managed Compute for edge cases.

  This file prints a compact matrix so you can eyeball the trade-offs
  without leaving the terminal. See the README table for the full 10-row grid.

What to watch:
  Each block shows billing / residency / throughput / cost / when-to-use for
  one deployment type. Beginner default is Global Standard.
"""

_MATRIX = [
    {
        "type": "Global Standard",
        "billing": "pay-per-token",
        "residency": "data at rest in region; inference anywhere",
        "throughput": "highest initial limits",
        "cost": "lowest per-token",
        "when": "default — most workloads",
    },
    {
        "type": "Standard (Regional)",
        "billing": "pay-per-token",
        "residency": "inference stays in deploy region",
        "throughput": "lower than global",
        "cost": "slightly higher per-token",
        "when": "data must stay in a single region",
    },
    {
        "type": "Provisioned (PTU)",
        "billing": "reserved capacity, hourly fixed",
        "residency": "regional",
        "throughput": "guaranteed rate limits",
        "cost": "up to ~70% savings at high volume",
        "when": "predictable latency, no transient 429s",
    },
    {
        "type": "Serverless API (MaaS)",
        "billing": "pay-per-token via Marketplace",
        "residency": "regional (varies by model)",
        "throughput": "auto-managed",
        "cost": "per-model pricing",
        "when": "partner models (Llama, Mistral, Cohere, Claude MaaS)",
    },
]


def main() -> None:
    for row in _MATRIX:
        print(f"\n[{row['type']}]")
        for key in ("billing", "residency", "throughput", "cost", "when"):
            print(f"  {key:<10} {row[key]}")


if __name__ == "__main__":
    main()
