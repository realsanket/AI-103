# Run: uv run python 07-production-platform-other/05_diagnostics_preflight.py
# Practice-question coverage: Q23.
"""Locally validate diagnostic configuration in Bicep and Terraform; no automated apply.

Confirms both `bicep/main.bicep` and `terraform/main.tf` configure the
reviewed Foundry diagnostic categories: `Audit`, `RequestResponse`,
`AzureOpenAIRequestUsage`, `AllMetrics`. Logs route to Log Analytics.

`RequestResponse` can contain prompt + completion content. Set workspace
retention, RBAC, export, and query access per organization policy. Do NOT
add prompt or completion text to custom application telemetry by default —
combine with domain 01 lesson 25's `AppGenAIContent` protected-table pattern
for sensitive attributes.

No `--apply` mode. The diagnostic setting is provisioned by lesson 01 or 02
`--apply`; this lab only validates the templates.

Code path:
  `entrypoint_preflight("diagnostics")` reads both template files; asserts
  each of the four category strings appears in each. Prints `Bicep and
  Terraform configure reviewed Foundry diagnostic categories`.

What to watch. Preflight only. Missing category names surface as
`diagnostic categories missing: <list>` — add them to whichever template
lacks them.

Prerequisites / env vars:
  none — local read-only check
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("diagnostics")
