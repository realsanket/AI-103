# 08 — Advanced agents and current Foundry operations

These labs cover current Microsoft Foundry agent capabilities that supplement the AI-103 objectives. They do not replace the exam-domain lessons. Each default command is a local preflight and makes no cloud call. Every remote write requires `--apply`.

This directory uses the current agent object model. New agents have a stable endpoint and unique agent identity when created. Do not create an Agent Application or use an application endpoint in these labs.

## Scope and feature status

| Lab | Current capability | Default | `--apply` effect |
|---|---|---|---|
| `01_foundry_iq_connection_preflight.py` | Foundry IQ knowledge-base MCP connection | Validates identifiers and endpoint shape. | Creates or updates a keyless project connection. |
| `02_toolbox_publish_preflight.py` | Toolbox version and MCP endpoints | Validates a credential-free manifest. | Creates toolbox and first immutable version. |
| `03_a2a_agent_card_preflight.py` | Incoming A2A v1.0 and agent card | Prints v1.0 base and card URLs. | Enables Responses and A2A protocols and writes the card. |
| `04_routines_preflight.py` | Project-native scheduled agent invocation | Validates a disabled schedule manifest. | Creates routine; optional `--dispatch` runs once. |
| `05_gateway_publishing_preflight.py` | AI Gateway review and stable-endpoint release | Prints gateway and channel-publishing checks. | Pins endpoint to one reviewed agent version. |
| `06_agent_optimizer_preflight.py` | Hosted Python Agent Optimizer lifecycle | Checks local optimizer assets. | Starts an optimization job or applies one selected candidate locally. |

Foundry IQ is partially generally available, but its portal and agentic retrieval surfaces can remain preview-dependent. Toolbox tool search, A2A, and routines are preview features. Confirm region, subscription, model, and feature availability immediately before applying changes.

## Prerequisites

Install repository dependencies and authenticate without adding secrets:

```bash
uv sync
az login
azd auth login
azd ext install microsoft.foundry
```

Routines require the separate preview extension:

```bash
azd extension install azure.ai.routines
```

For each remote action, your signed-in identity needs **Foundry User** on the project. Grant least-privilege roles to agent and project identities rather than storing keys. Some actions need more:

| Operation | Additional access or decision |
|---|---|
| Foundry IQ indexing and retrieval | Assign `Search Index Data Reader` to project managed identity. Add `Search Index Data Contributor` only for writes. |
| Toolbox runtime | Assign **Foundry User** to agent identity; use project connections for remote-tool authentication. |
| Incoming A2A caller | Assign **Foundry Agent Consumer** to calling identity on hosted project or agent scope. |
| Routines | Use an agent that authenticates with its own configured identity; routines can't delegate an end-user identity. |
| AI Gateway | Use an eligible APIM v2 instance and required Foundry/APIM roles. |
| Microsoft 365 Copilot or Teams | Review data flow, Bot Service permissions, tenant policy, and administrator approval. |
| Agent Optimizer | Use only Python hosted-agent source in an azd project. |

Copy only non-secret names and endpoints to `.env`. This repository's `.env.example` includes the domain-eight values. Keep secrets in project connections, managed identity, Key Vault, or your CI secret store. Never add them to manifests, prompts, agent cards, or routine inputs.

## Preflight first

Run every lab with no flag. A successful local preflight does not prove role assignment, feature availability, access to a private endpoint, remote operation success, or billing approval.

```bash
uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py
uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py
uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py
uv run python 08-advanced-agents-other/04_routines_preflight.py
uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py --agent-root <hosted-agent-root>
```

Preflights deliberately don't read Azure. They validate local inputs, show current endpoint patterns, and state the next guarded operation.

## Lab 01: Foundry IQ through a keyless connection

Foundry IQ in Foundry Tools is a managed knowledge layer built on Azure AI Search agentic retrieval. A knowledge base can combine sources, enforce supported permissions, plan retrieval, and return citations. Connect it to an agent through its MCP endpoint, not through embedded Search credentials.

Set these non-secret values:

```bash
export PROJECT_ENDPOINT="https://<account>.services.ai.azure.com/api/projects/<project>"
export FOUNDRY_IQ_SEARCH_ENDPOINT="https://<search>.search.windows.net"
export FOUNDRY_IQ_KNOWLEDGE_BASE="<knowledge-base>"
export FOUNDRY_IQ_CONNECTION_NAME="foundry-iq-kb"
```

Preflight checks the current knowledge-base MCP URL:

```text
https://<search>.search.windows.net/knowledgebases/<knowledge-base>/mcp?api-version=2026-05-01-preview
```

After Search access and data-boundary review:

```bash
uv run python 08-advanced-agents-other/01_foundry_iq_connection_preflight.py --apply
```

This creates a `remote-tool` project connection with `project-managed-identity` authentication and the `https://search.azure.com/` audience. It doesn't create the knowledge base. Create and validate knowledge sources and the knowledge base separately before this step.

## Lab 02: Toolbox version, test endpoint, and consumer endpoint

Toolbox centralizes approved tools behind one MCP-compatible endpoint. Connections own authentication and token renewal. Toolbox versions are immutable. Test a version-specific developer endpoint before exposing the default consumer endpoint to an agent.

Copy `toolbox.example.yaml` outside source control, replace its connection name, and keep it credential-free:

```bash
cp 08-advanced-agents-other/toolbox.example.yaml toolbox.local.yaml
uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py \
  --manifest toolbox.local.yaml
```

Create the first version only after reviewing tool descriptions, authentication, approval policy, region/model support, data flows, owner, cost, and cleanup:

```bash
uv run python 08-advanced-agents-other/02_toolbox_publish_preflight.py \
  --apply --toolbox-name support-knowledge --manifest toolbox.local.yaml
```

Use these endpoint roles:

```text
# Test exact immutable version.
{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/versions/{VERSION}/mcp?api-version=v1

# Consumer endpoint always resolves current default version.
{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1
```

Use tool search for larger catalogs. It reduces tool-definition context but doesn't authorize a tool or make a tool safe.

## Lab 03: Incoming A2A agent card and endpoint

Incoming A2A requires a current agent with the Responses protocol. New callers should target A2A v1.0. The agent card is protected by Microsoft Entra ID; it isn't anonymously discoverable.

```bash
export FOUNDRY_AGENT_NAME="support-agent"

uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py
uv run python 08-advanced-agents-other/03_a2a_agent_card_preflight.py \
  --apply --verify
```

The lab PATCHes the agent card and enables Responses plus A2A. It doesn't grant caller access. Grant **Foundry Agent Consumer** to each caller identity, choose on-behalf-of versus service-identity authentication deliberately, and test only v1.0 clients for new integrations.

```text
{PROJECT_ENDPOINT}/agents/{AGENT}/endpoint/protocols/a2a
{PROJECT_ENDPOINT}/agents/{AGENT}/endpoint/protocols/a2a/agentCard/v1.0
```

Do not assume a Responses endpoint is A2A-capable until the A2A protocol and card are configured.

## Lab 04: Routines

A routine has one trigger and one action. Use it for timers, recurring schedules, or supported events that invoke one agent. Use a workflow for branching, approvals, multiple agents, or stateful coordination.

Copy `routine.example.yaml` outside source control and replace the agent name. It starts disabled so you can inspect it before enabling it:

```bash
cp 08-advanced-agents-other/routine.example.yaml routine.local.yaml
uv run python 08-advanced-agents-other/04_routines_preflight.py \
  --manifest routine.local.yaml
uv run python 08-advanced-agents-other/04_routines_preflight.py \
  --apply --routine-name weekday-support-summary --manifest routine.local.yaml
```

To make one controlled test invocation, add `--dispatch` to the final command. Then inspect:

```bash
azd ai routine show weekday-support-summary --project-endpoint "$PROJECT_ENDPOINT"
azd ai routine run list weekday-support-summary --project-endpoint "$PROJECT_ENDPOINT"
```

Review trace, output, tool behavior, data exposure, and cost before enabling the schedule. A routine executes unattended, so routine input must not include secrets, personal access tokens, or delegated user credentials.

## Lab 05: Gateway and channel publishing

AI Gateway uses API Management to apply governance, quotas, token limits, and observability. Enable it in the Foundry portal **Operate** > **Admin console** before production traffic. Confirm both gateway and target project show **Enabled**. Existing projects require explicit addition to a configured gateway.

```bash
uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py
uv run python 08-advanced-agents-other/05_gateway_publishing_preflight.py \
  --apply --agent-name "$FOUNDRY_AGENT_NAME" --agent-version 2
```

The guarded action pins 100% of stable-endpoint traffic to an immutable, reviewed agent version. It does not distribute to channels.

Current Foundry publishing means distributing an existing agent stable endpoint to Microsoft 365 Copilot or Teams. Complete it in the Foundry portal after you verify response quality, tool permissions, gateway behavior, end-user data handling, Bot Service permissions, tenant policy, and approval scope. Do not use the deprecated Agent Application publishing model.

## Lab 06: Agent Optimizer

Agent Optimizer targets Python hosted agents in an azd project. It needs `azure.yaml`, `eval.yaml`, and `.agent_configs/baseline/` in that agent root. The lab rejects non-ready source instead of generating unreviewed assets.

```bash
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root>

uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root> --apply \
  --optimize-model <approved-optimizer-deployment>
```

Monitor the operation and compare candidate scores. Apply a specific reviewed candidate to local source only:

```bash
uv run python 08-advanced-agents-other/06_agent_optimizer_preflight.py \
  --agent-root <hosted-agent-root> --apply \
  --apply-candidate <candidate-id>
```

Review the diff, evaluator results, safety behavior, tool changes, latency, and cost before a separate `azd deploy`. This lab never deploys automatically.

## Operational runbook

1. Preflight local inputs.
1. Confirm region, preview access, billing, network path, and role assignments.
1. Apply one small, named change.
1. Validate immutable Toolbox version or pinned agent version before consumer rollout.
1. Exercise a bounded canary request or one manual routine dispatch.
1. Inspect responses, citations, traces, tool calls, latency, errors, and cost.
1. Promote default Toolbox version, enable routine, or distribute channel endpoint only after review.
1. Keep a rollback target: previous Toolbox version, prior agent version, disabled routine, or disabled project gateway association.

## Current local reference set

These checked-in docs are the local technical basis for this directory:

- [Foundry IQ concepts](../.context/azure-ai-docs/articles/foundry/agents/concepts/what-is-foundry-iq.md)
- [Foundry IQ agent connection](../.context/azure-ai-docs/articles/foundry/agents/how-to/foundry-iq-connect.md)
- [Toolbox concepts](../.context/azure-ai-docs/articles/foundry/agents/concepts/toolbox-overview.md)
- [Toolbox management](../.context/azure-ai-docs/articles/foundry/agents/how-to/tools/toolbox.md)
- [Incoming A2A](../.context/azure-ai-docs/articles/foundry/agents/how-to/enable-agent-to-agent-endpoint.md)
- [Routines](../.context/azure-ai-docs/articles/foundry/agents/how-to/use-routines.md)
- [AI Gateway](../.context/azure-ai-docs/articles/foundry/configuration/enable-ai-api-management-gateway-portal.md)
- [Current endpoint configuration](../.context/azure-ai-docs/articles/foundry/agents/how-to/configure-agent.md)
- [Current publishing model](../.context/azure-ai-docs/articles/foundry/agents/how-to/migrate-agent-applications.md)

Documentation changes independently from this lab. Recheck feature state, region support, REST/API version, and CLI help before applying remote changes.
