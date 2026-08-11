# Run: uv run python 07-production-platform-other/06_ha_dr_preflight.py
"""Locally validate HA/DR guidance in the README; no automated apply.

Confirms the README HA/DR section states three critical facts: (1) Foundry
has no automatic failover, (2) warm standby is the model (not active-active
promotion), (3) at least two supported regions are required. If any is
missing, guidance is silently wrong and the lab fails.

Foundry projects are regional. Cross-region agent state migration,
active-active replication, and thread recovery are NOT supported.
User-uploaded thread files can be lost. Warm standby means reconstruction —
redeploy cell, recreate agents, rebuild indexes from source, test private
DNS/RBAC, then move traffic.

No `--apply` mode. Deploying a second regional cell uses lesson 01/02
`--apply` with a different region + prefix + globally-unique account/KV/
Storage names.

Code path:
  `entrypoint_preflight("ha-dr")` reads README.md; asserts the three required
  strings are present. Prints `HA/DR guidance requires independent regional
  cells and a tested traffic switch`.

What to watch. Preflight only. Missing guidance surfaces as `HA/DR guidance
missing: <list>` — restore the phrases to README before promoting docs.

Prerequisites / env vars:
  none — local read-only check
"""
from scripts.preflight import entrypoint_main


if __name__ == "__main__":
    entrypoint_main("ha-dr")
