# Run: uv run python 01-plan-and-manage/02_deployment_types.py
"""Choose a deployment type — decision helper + cheatsheet.

Prints a matrix comparing Global Standard / Standard Regional / Provisioned
Throughput (PTU) / Serverless API. Same content as the slides, just runnable
so you can pipe it into notes.
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
