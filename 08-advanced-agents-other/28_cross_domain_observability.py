# Run: uv run python 08-advanced-agents-other/28_cross_domain_observability.py [--apply --workspace-id <guid>]
"""Query non-content operational health signals across AI-103 workloads.

Observability is a release system, not one SDK switch. Model, agent, Search,
Speech, extraction, customization, infrastructure, and Document Intelligence
workloads emit different signals and need separate owners. This lesson provides
one common Log Analytics health query for volume, failure, and latency without
request/response content.

Flows:
  Default - print the Domain 01-09 signal/owner map and KQL; no cloud call.
  --apply --workspace-id - run the read-only 24-hour query with
  LogsQueryClient(DefaultAzureCredential).

What to watch. Empty results mean no matching telemetry was ingested into this
workspace; they do not prove health. This query intentionally excludes
AppGenAIContent and cannot replace domain-specific quality, safety, cost,
retention, or permission-trimming evaluation.

Prerequisites / env vars:
  --workspace-id  - Log Analytics workspace GUID
  --apply         - perform one read-only query
  Role            - Log Analytics Reader at workspace scope
"""
import argparse
from datetime import timedelta


DOMAIN_SIGNALS = {
    "01": "evaluation, safety, red-team, tracing, quota, control-plane inventory",
    "02": "agent/model latency, tool calls, failures, tokens, evaluation, traces",
    "03": "vision/CU job state, media policy, provenance, latency, retained outputs",
    "04": "Language/Speech/Translator/Voice jobs, audio consent, latency, failures",
    "05": "Search indexer health, query latency/relevance, CU extraction provenance",
    "06": "training/evaluation jobs, quota/capacity, latency, cost, rollback version",
    "07": "resource diagnostics, policy/locks, private endpoint health, DR evidence",
    "08": "hosted-agent/tool/A2A/routine/gateway/optimizer health and identity",
    "09": "Document Intelligence operation status, confidence review, latency, cost",
}


KQL = r"""
union isfuzzy=true withsource=TableName AppRequests, AppDependencies, AppTraces, AppEvents
| where TimeGenerated > ago(24h)
| extend
    operation = tostring(column_ifexists("Name", "")),
    duration_ms = todouble(column_ifexists("DurationMs", 0.0)),
    succeeded = tobool(column_ifexists("Success", true))
| summarize
    operations = count(),
    failures = countif(succeeded == false),
    avg_duration_ms = avgif(duration_ms, duration_ms > 0)
    by TableName, operation
| order by failures desc, operations desc
| take 50
""".strip()


def preflight() -> None:
    print("No cloud calls made.")
    print("Cross-domain operational signal map:")
    for domain, signals in DOMAIN_SIGNALS.items():
        print(f"- Domain {domain}: {signals}")
    print()
    print("Read-only, non-content KQL:")
    print(KQL)
    print()
    print("Excluded: AppGenAIContent, prompts, outputs, tool arguments, and documents.")
    print("Empty query output is missing evidence, not proof of health.")


def apply(workspace_id: str) -> None:
    from azure.identity import DefaultAzureCredential
    from azure.monitor.query import LogsQueryClient, LogsQueryStatus

    result = LogsQueryClient(DefaultAzureCredential()).query_workspace(
        workspace_id=workspace_id,
        query=KQL,
        timespan=timedelta(hours=24),
    )
    if result.status == LogsQueryStatus.PARTIAL:
        raise RuntimeError(f"Partial Log Analytics query: {result.partial_error}")
    if result.status != LogsQueryStatus.SUCCESS:
        raise RuntimeError(f"Log Analytics query failed with status {result.status}.")
    if not result.tables:
        print("No matching operational telemetry found in the last 24 hours.")
        return
    for table in result.tables:
        print("\t".join(column.name for column in table.columns))
        for row in table.rows:
            print("\t".join(str(value) for value in row))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read cross-domain operational health telemetry.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--workspace-id")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.workspace_id:
        parser.error("--apply requires --workspace-id.")
    apply(args.workspace_id)


if __name__ == "__main__":
    main()
