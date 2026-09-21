# Run: uv run python 02-generative-ai-and-agents/47_mcp_available_tools_preflight.py [--apply]
"""Foundry MCP Server (preview) — available tools reference.

The Foundry-hosted MCP Server exposes 79 tools across 17 categories at
`https://mcp.ai.azure.com`. Any MCP-compliant client (GitHub Copilot Agent Mode,
Claude Desktop, VS Code MCP, etc.) can list, inspect, and call these tools using
the calling user's own Entra identity through the On-Behalf-Of flow — no API
keys, no per-tool credentials. Tools are classified `read` or `write`; write
operations affect live resources and billing immediately.

This lesson is a preflight-only catalog. It prints every category and every tool
with its access type, one-line purpose, and required RBAC role. Use it as a
study card before hooking an MCP client to a Foundry project. It never dials
the MCP server — actually invoking a tool is the MCP client's job.

Auth model (same across every tool):
  - Microsoft Entra ID via On-Behalf-Of flow — the calling user's Azure roles
    are enforced.
  - Read tools: Reader on the Foundry project or account.
  - Write tools: Contributor on the Foundry project or account.
  - Some tools need extra scopes (subscription quota reads need subscription
    Reader; conditional-access management needs Conditional Access Admin).

Code path:
  Preflight — print each category and its tools grouped by access type.
  --apply   — also print `az login` and Entra token-audience reminders and
              the public MCP endpoint the client will target. No HTTP call.

What to watch:
  Tool set is preview and can change without notice. This file mirrors the
  categories in `mcp/available-tools.md` at the doc date — reconcile against
  the live server output before relying on any specific tool name.

Prerequisites / env vars:
  (no env vars required — this is a local catalog)
  AZURE_SUBSCRIPTION_ID — echoed for the model_quota_list example only.
"""
import argparse

from _shared.config import settings

MCP_ENDPOINT = "https://mcp.ai.azure.com"

# Mirrors mcp/available-tools.md categories. Each entry: (tool, access, purpose).
CATALOG: dict[str, list[tuple[str, str, str]]] = {
    "Agent management": [
        ("agent_get", "read", "List agents or get one agent by name."),
        ("agent_update", "write", "Create, update, or clone an agent."),
        ("agent_invoke", "write", "Send a message to an agent and get a response."),
        ("agent_delete", "write", "Permanently delete an agent (deletes hosted container)."),
        ("agent_container_control", "write", "Start or stop a hosted agent container."),
        ("agent_container_status_get", "read", "Check hosted-agent container status."),
        ("agent_definition_schema_get", "read", "Return the full agent-definition JSON schema."),
    ],
    "Hosted agent sessions and files": [
        ("session_create", "write", "Create a new session for a hosted agent."),
        ("session_get", "read", "Get details for one hosted-agent session."),
        ("session_list", "read", "List hosted-agent sessions with pagination and sorting."),
        ("session_delete", "write", "Delete a session and release its compute."),
        ("session_logstream", "read", "Stream capped stdout/stderr logs from a session."),
        ("session_file_list", "read", "List files at a path in a session sandbox."),
        ("session_file_stat", "read", "Get metadata for one file or directory in a session."),
        ("session_file_mkdir", "write", "Create a directory in a session sandbox."),
        ("session_file_upload", "write", "Upload base64-encoded content to a session file."),
        ("session_file_download", "read", "Download a session file as base64."),
        ("session_file_delete", "write", "Delete a file or directory from a session sandbox."),
    ],
    "Toolbox management": [
        ("toolbox_get", "read", "Retrieve a toolbox and its default version."),
        ("toolbox_version_get", "read", "List versions or get a specific version."),
        ("toolbox_version_create", "write", "Create an immutable toolbox version (auto-creates toolbox)."),
        ("toolbox_update", "write", "Update a toolbox, including the default version pointer."),
        ("toolbox_delete", "write", "Delete a toolbox."),
        ("toolbox_version_delete", "write", "Delete a specific toolbox version."),
    ],
    "Dataset management": [
        ("evaluation_dataset_create", "write", "Create/update a dataset version from a Blob URI."),
        ("evaluation_dataset_get", "read", "Get a dataset by name/version or list all datasets."),
        ("evaluation_dataset_versions_get", "read", "List all versions of a dataset."),
        ("evaluation_dataset_sas_url_get", "read", "Get a short-lived SAS URL to download a dataset version."),
    ],
    "Data generation jobs": [
        ("data_generation_job_create", "write", "Start a data generation job for eval or fine-tuning."),
        ("data_generation_job_get", "read", "Get one job or list jobs when ID is omitted."),
        ("data_generation_job_cancel", "write", "Cancel a running data generation job."),
        ("data_generation_job_delete", "write", "Delete a data generation job."),
    ],
    "Evaluation operations": [
        ("evaluation_agent_batch_eval_create", "write", "Batch evaluate an agent with built-in/custom evaluators."),
        ("evaluation_dataset_batch_eval_create", "write", "Batch evaluate a JSONL dataset."),
        ("evaluation_get", "read", "List evaluation groups/runs or fetch a specific item."),
        ("evaluation_comparison_create", "write", "Compare a baseline run against treatment runs."),
        ("evaluation_comparison_get", "read", "Get or list evaluation comparison insights."),
    ],
    "Trace evaluation": [
        ("evaluation_agent_traces_batch_eval_create", "write", "Evaluate recent agent traces (multi-turn)."),
        ("evaluation_traces_batch_eval_create", "write", "Evaluate specific conversation or W3C trace IDs."),
    ],
    "Evaluation suites": [
        ("evaluation_suite_create", "write", "Create a suite version grouping evaluators/dataset/agent."),
        ("evaluation_suite_get", "read", "Get a suite version, list versions, or list suites."),
        ("evaluation_suite_update", "write", "Update display name, description, or tags."),
        ("evaluation_suite_run", "write", "Start an evaluation suite run."),
        ("evaluation_suite_delete", "write", "Delete a suite version."),
        ("evaluation_suite_generation_job_create", "write", "Start a suite generation job."),
        ("evaluation_suite_generation_job_get", "read", "Get one generation job or list jobs."),
        ("evaluation_suite_generation_job_cancel", "write", "Cancel a suite generation job."),
        ("evaluation_suite_generation_job_delete", "write", "Delete a suite generation job."),
    ],
    "Evaluator catalog": [
        ("evaluator_catalog_get", "read", "List evaluators or get one full definition."),
        ("evaluator_catalog_create", "write", "Create a custom prompt-based or code-based evaluator."),
        ("evaluator_catalog_update", "write", "Update metadata on a custom evaluator."),
        ("evaluator_catalog_delete", "write", "Delete a specific version of a custom evaluator."),
    ],
    "Evaluator generation jobs": [
        ("evaluator_generation_job_create", "write", "Start adaptive evaluator generation from prompt/agent/data."),
        ("evaluator_generation_job_get", "read", "Get one evaluator generation job or list them."),
        ("evaluator_generation_job_cancel", "write", "Cancel an evaluator generation job."),
    ],
    "Model catalog and details": [
        ("model_catalog_list", "read", "List Foundry catalog models with optional filters."),
        ("model_details_get", "read", "Get full model details, code samples, deployment templates."),
    ],
    "Model deployment management": [
        ("model_deploy_azure_direct_model", "write", "Deploy a Foundry Model sold by Azure."),
        ("model_deploy", "write", "DEPRECATED alias of model_deploy_azure_direct_model."),
        ("model_deploy_managed_compute", "write", "Deploy a Managed Compute model from a registry asset."),
        ("model_deployment_get", "read", "Get one deployment (ADM or Managed) or list all."),
        ("model_deployment_delete", "write", "Delete either deployment type by name."),
    ],
    "Model analytics and recommendations": [
        ("model_benchmark_get", "read", "Fetch Foundry model benchmark data."),
        ("model_benchmark_subset_get", "read", "Benchmark data for specific model name/version pairs."),
        ("model_similar_models_get", "read", "Find similar models to a deployment or model."),
        ("model_switch_recommendations_get", "read", "Recommend switches based on benchmark data."),
    ],
    "Model monitoring and operations": [
        ("model_monitoring_metrics_get", "read", "Request/latency/errors/quota metrics for a deployment."),
        ("model_deprecation_info_get", "read", "Deployment info with deprecation and retirement dates."),
        ("model_quota_list", "read", "List quota and usage per region, including MC accelerators."),
    ],
    "Project connections": [
        ("project_connection_list", "read", "List project connections with optional filters."),
        ("project_connection_get", "read", "Get a specific connection by name."),
        ("project_connection_list_metadata", "read", "List supported connection categories and auth types."),
        ("project_connection_create", "write", "Create or replace a project connection."),
        ("project_connection_update", "write", "Update an existing project connection."),
        ("project_connection_delete", "write", "Delete a project connection by name."),
    ],
    "Prompt optimization": [
        ("prompt_optimize", "write", "Optimize a system/developer prompt via Azure OpenAI optimizer."),
    ],
    "Continuous evaluation": [
        ("continuous_eval_create", "write", "Enable or update continuous eval for an agent."),
        ("continuous_eval_get", "read", "Get continuous eval config for an agent."),
        ("continuous_eval_delete", "write", "Delete a continuous eval configuration."),
    ],
}


def _print_catalog() -> None:
    total = 0
    for category, tools in CATALOG.items():
        print(f"[{category}]  ({len(tools)} tools)")
        for name, access, purpose in tools:
            marker = "R" if access == "read" else "W"
            print(f"  {marker}  {name:<48} {purpose}")
        total += len(tools)
        print()
    print(f"Total: {total} tools across {len(CATALOG)} categories.")


def preflight() -> None:
    print("No cloud calls made. Foundry MCP Server is preview; tools can change without notice.")
    print(f"Public MCP endpoint (all clients): {MCP_ENDPOINT}")
    print("Auth: Microsoft Entra ID via OBO — the calling user's Azure roles are enforced.")
    print()
    print("Access classes: R=read (needs Reader), W=write (needs Contributor).")
    print("Some tools additionally need subscription Reader (quotas) or")
    print("Conditional Access Administrator (tenant access policies).")
    print()
    _print_catalog()
    print()
    print("Preview limitations: public endpoint only (no Private Link), possible")
    print("cross-region processing (EU/US), no SLA. Not for production workloads.")
    print()
    print("Run with --apply to also echo the client wiring reminders (still no cloud call).")


def apply() -> None:
    s = settings()
    preflight()
    print()
    print("Client wiring reminders (this script does not open an MCP session):")
    print("  - Configure your MCP client with server URL:", MCP_ENDPOINT)
    print("  - Sign in with `az login` before the client acquires an OBO token.")
    print("  - Token audience must be `https://ai.azure.com` (scope .default).")
    if s.azure_subscription_id:
        print(f"  - model_quota_list example: use subscription {s.azure_subscription_id}.")
    else:
        print("  - Set AZURE_SUBSCRIPTION_ID to run model_quota_list examples.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Foundry MCP Server available-tools reference.")
    parser.add_argument("--apply", action="store_true", help="Also print client wiring reminders.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    apply()


if __name__ == "__main__":
    main()
