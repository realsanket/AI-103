# Run: uv run python 01-plan-and-manage/02_deployment_types.py
"""Print deployment types supported by Foundry Models.

Processing location and billing depend on deployment type. Stored data remains
in its designated geography; inference is global, data-zone, or single-region
as shown below. Availability varies by model and region.
"""

_MATRIX = [
    {
        "type": "Instant (preview)",
        "billing": "pay-per-token (separate global quota pool)",
        "residency": "inference can run in any Azure region",
        "throughput": "no deployment needed; platform-managed access",
        "cost": "pay-per-token",
        "when": "prototyping or trying an eligible model",
    },
    {
        "type": "Global Standard",
        "billing": "pay-per-token",
        "residency": "inference can run in any Azure region",
        "throughput": "highest default quota",
        "cost": "pay-per-token",
        "when": "variable general workloads",
    },
    {
        "type": "Data Zone Standard",
        "billing": "pay-per-token",
        "residency": "inference stays in US, EU, or APAC data zone",
        "throughput": "higher default quota than regional Standard",
        "cost": "pay-per-token",
        "when": "data-zone compliance",
    },
    {
        "type": "Standard",
        "billing": "pay-per-token",
        "residency": "inference stays in deploy region",
        "throughput": "model and region dependent",
        "cost": "pay-per-token",
        "when": "single-region processing",
    },
    {
        "type": "Global Provisioned",
        "billing": "reserved PTUs, billed hourly",
        "residency": "inference can run in any Azure region",
        "throughput": "dedicated capacity; predictable latency",
        "cost": "PTU hourly billing or reservation",
        "when": "high, predictable volume",
    },
    {
        "type": "Data Zone Provisioned",
        "billing": "reserved PTUs, billed hourly",
        "residency": "inference stays in US, EU, or APAC data zone",
        "throughput": "dedicated capacity; predictable latency",
        "cost": "PTU hourly billing or reservation",
        "when": "data-zone, high-volume workload",
    },
    {
        "type": "Regional Provisioned",
        "billing": "reserved PTUs, billed hourly",
        "residency": "inference stays in deploy region",
        "throughput": "dedicated capacity; predictable latency",
        "cost": "PTU hourly billing or reservation",
        "when": "single-region, high-volume workload",
    },
    {
        "type": "Global or Data Zone Batch",
        "billing": "discounted pay-per-token",
        "residency": "global or selected data zone",
        "throughput": "asynchronous; 24-hour target turnaround",
        "cost": "50% less than Global Standard",
        "when": "large, non-real-time jobs",
    },
    {
        "type": "Developer",
        "billing": "pay-per-token",
        "residency": "no residency guarantee",
        "throughput": "evaluation only; no SLA",
        "cost": "pay-per-token",
        "when": "fine-tuned model evaluation",
    },
]


def main() -> None:
    for row in _MATRIX:
        print(f"\n[{row['type']}]")
        for key in ("billing", "residency", "throughput", "cost", "when"):
            print(f"  {key:<10} {row[key]}")


if __name__ == "__main__":
    main()
