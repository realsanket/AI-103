---
ai-usage: ai-assisted
---

# Preview workflow definitions

- `wf_intake_schema.json` — JSON Schema the intake agent must fill in (used by lesson 15).
- `wf_triage.yml` — full YAML workflow: intake → conditional route to Knowledge or Ticket agent → end (used by lesson 16).

Microsoft Foundry retires workflows on December 1, 2026. Treat these files as
preview study assets and migrate new orchestration to Microsoft Agent Framework.
Save and version the YAML; after retirement, deploy workflow code or YAML as a
hosted agent instead of relying on the visual designer or in-portal execution.
