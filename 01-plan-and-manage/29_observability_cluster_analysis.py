# Run: uv run python 01-plan-and-manage/29_observability_cluster_analysis.py [--apply --workspace-id <guid>]
"""Read recent trace clusters from Application Insights for Foundry cluster analysis.

Cluster analysis (Observability → Analyze in portal) groups similar failed or
low-quality runs so operators can triage patterns instead of individual
traces. Portal computes clusters — this CLI lab reads the underlying
`AppTraces` + `AppDependencies` records via Log Analytics KQL and prints a
count by operation for quick triage.

Default preflight validates env; `--apply` runs a KQL summary query against
the workspace and prints (operation_name, count, avg_duration_ms). Not a
replacement for portal cluster analysis — that also applies embedding
similarity to prompt/output text. This CLI is triage-first.

Caller needs `Log Analytics Reader` on the workspace. Recorded content
attributes (`gen_ai.input.messages`, etc.) can contain PII — do NOT print
raw content in this lab.

Code path:
  --apply: LogsQueryClient(cred).query_workspace(workspace_id,
  query="AppDependencies | where Type == 'GenAI' | summarize count(),
  avg(DurationMs) by Name | order by count_ desc | take 20", timespan=P1D).
  Print result table.

What to watch. Preflight: env status. `--apply`: top-20 operation names by
count in last 24h. High counts + high avg latency = triage target. Zero rows
= no GenAI dependency traces in workspace yet.

Prerequisites / env vars:
  --workspace-id GUID  — Log Analytics workspace ID (required with --apply)
  --apply              — perform KQL read
"""
import argparse

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta

_QUERY = """
AppDependencies
| where Type == "InProc" or Name startswith "chat" or Name startswith "gen_ai"
| summarize count=count(), avg_ms=avg(DurationMs), fail_rate=avg(iff(Success == false, 1.0, 0.0)) by Name
| order by count desc
| take 20
"""


def preflight() -> None:
    print("Cluster analysis preflight (no cloud calls).")
    print("- Portal path: Foundry → Observability → Analyze → Cluster analysis.")
    print("- This CLI is triage-first: run --apply --workspace-id <guid> for KQL summary.")
    print("- Portal adds embedding similarity on prompt/output; this CLI is aggregate only.")


def apply(workspace_id: str) -> None:
    response = LogsQueryClient(DefaultAzureCredential()).query_workspace(
        workspace_id=workspace_id, query=_QUERY, timespan=timedelta(days=1)
    )
    if not response.tables or not response.tables[0].rows:
        print("No GenAI dependency traces in last 24h.")
        return
    table = response.tables[0]
    print(f"{'operation':<45} {'count':>8} {'avg_ms':>10} {'fail_rate':>10}")
    print("-" * 76)
    for row in table.rows:
        print(f"{str(row[0]):<45} {int(row[1]):>8} {float(row[2]):>10.1f} {float(row[3]):>10.3f}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read cluster-analysis triage summary.")
    parser.add_argument("--apply", action="store_true", help="Run KQL summary.")
    parser.add_argument("--workspace-id", help="Log Analytics workspace ID.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.workspace_id:
        parser.error("--apply requires --workspace-id.")
    apply(args.workspace_id)


if __name__ == "__main__":
    main()
