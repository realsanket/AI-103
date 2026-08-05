# Responses hosted-agent sample

Contained Domain 2 source-deployment sample. It uses Foundry Agent Server's
Responses adapter rather than building HTTP plumbing itself.

## Contract and scope

- `codeConfiguration.dependencyResolution: remote_build` builds source in the
  Foundry Linux x86_64 (amd64) runtime. Do not bundle macOS or Windows wheels.
- Adapter listens on `0.0.0.0:${PORT:-8088}`, serves `GET /readiness` and
  `POST /responses`, and handles graceful `SIGTERM` shutdown.
- Platform injects `FOUNDRY_PROJECT_ENDPOINT`; `azure.yaml` intentionally does
  not override it. Set only `FOUNDRY_MODEL_NAME` in the selected azd environment.
- No keys, tokens, connection strings, or platform-injected identifiers belong
  in source control.

## Preflight and local run

Prerequisites: Python 3.13+, `azd` 1.25.3+, authenticated `azd auth login`,
and `azd ext install azure.ai.agents`.

```bash
cd 02-generative-ai-and-agents/hosted_agent_responses
python preflight.py
azd ai agent run
# separate terminal
azd ai agent invoke --local "Give a one-line deployment status."
curl -sS http://localhost:8088/readiness
```

The active azd environment must contain `FOUNDRY_PROJECT_ENDPOINT` and
`FOUNDRY_MODEL_NAME`; keep `.azure/` uncommitted. `azd ai agent run` injects
platform endpoint settings for local hosting.

## Deployment

Choose an existing Foundry project, set its non-secret azd environment values,
then validate before changing Azure:

```bash
azd env new dev --no-prompt
azd env set FOUNDRY_PROJECT_ENDPOINT "https://<resource>.services.ai.azure.com/api/projects/<project>"
azd env set FOUNDRY_MODEL_NAME "<model-deployment-name>"
python preflight.py
python deploy.py                    # prints plan; no mutation
python deploy.py --apply            # deploy source as a new agent version
python deploy.py --provision --apply # provision, then deploy
azd ai agent invoke "Reply with a deployment confirmation."
```

`--apply` is required for every provisioning or deployment mutation performed
by this sample. Use `azd ai agent monitor --follow` for deployed logs.

## Responses versus A2A

This agent exposes only Responses protocol `POST /responses`. That is a
user/application OpenAI-compatible request contract, not A2A. A2A orchestration
requires a separately declared `a2a` protocol plus explicit agent discovery,
caller identity, delegated-authority, and data-sharing design. Confirm boundary:

```bash
python preflight.py --a2a
```

## CI/CD reference

`hosted-agent-cd.yml` follows current Foundry guidance: GitHub OIDC, `azd`,
deploy, and an invoke smoke test. It is deliberately contained here rather than
an active repository workflow. Copy it to `.github/workflows/` only after
configuring OIDC, repository variables, and an existing azd environment. Keep
credentials out of repository variables and source; use GitHub OIDC and
platform identity.

Sources: [runtime contract](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-contract),
[local run](https://learn.microsoft.com/azure/foundry/agents/how-to/run-hosted-agent-locally),
[invoke](https://learn.microsoft.com/azure/foundry/agents/how-to/invoke-hosted-agent), and
[CI/CD](https://learn.microsoft.com/azure/foundry/agents/quickstarts/set-up-cicd-hosted-agent).
