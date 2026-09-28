# Run: uv run python 02-generative-ai-and-agents/39_openai_webhooks_preflight.py
"""Register an Azure OpenAI webhook endpoint to receive async event notifications.

Webhooks push events (response.completed, realtime.call.incoming) to a public HTTPS URL
you control. Registration uses a REST API — there is no SDK wrapper. The service signs
each delivery with an HMAC secret; verify with client.webhooks.unwrap(data, headers).

This is NOT polling. NOT a WebSocket. The service POSTs to your URL when events fire;
your server must be reachable from Azure.

Flows:
  Default  — dry-run: prints the registration payload that would be sent.
  --apply  — registers the webhook endpoint via POST to /openai/v1/dashboard/webhook_endpoints.

What to watch in the output (--apply):
  webhook_id  — save this for later deletion or updates.
  secret      — shown once; store it in Key Vault or env var immediately.
  status      — "active" = registered and delivery will begin.

Prerequisites / env vars:
  AZURE_OPENAI_ENDPOINT  — https://<resource>.openai.azure.com
  AZURE_OPENAI_API_KEY   — used for this REST call (management plane)
  WEBHOOK_URL            — public HTTPS URL of your listener (e.g. https://myapp.azurewebsites.net/webhook)
  WEBHOOK_NAME           — friendly name for the endpoint (default: ai-103-webhook-probe)
  --apply                — actually POST the registration (creates a persistent cloud resource)
  --event-types          — comma-separated event types (default: response.completed)
"""

import argparse
import json
import os
import sys
import urllib.request

from _shared.config import load_env


def preflight(webhook_url: str, webhook_name: str, event_types: list[str]) -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<resource>.openai.azure.com").rstrip("/")
    registration_url = f"{endpoint}/openai/v1/dashboard/webhook_endpoints"
    payload = {
        "name": webhook_name,
        "url": webhook_url,
        "event_types": event_types,
    }
    print("[DRY-RUN] Would POST to:")
    print(f"  {registration_url}")
    print()
    print("Request body:")
    print(json.dumps(payload, indent=2))
    print()
    print("Listener skeleton (app.py):")
    print("  from flask import Flask, request, Response")
    print("  from openai import OpenAI, InvalidWebhookSignatureError")
    print("  client = OpenAI(api_key='placeholder', webhook_secret=os.environ['OPENAI_WEBHOOK_SECRET'])")
    print("  @app.route('/webhook', methods=['POST'])")
    print("  def webhook():")
    print("      event = client.webhooks.unwrap(request.data, request.headers)")
    print("      if event.type == 'response.completed': ...")
    print("      return Response(status=200)")
    print()
    print("Supported event types: response.completed, realtime.call.incoming")
    print()
    print("Run with --apply to register the endpoint (requires WEBHOOK_URL to be public HTTPS).")


def apply(webhook_url: str, webhook_name: str, event_types: list[str]) -> None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    if not endpoint:
        print("[FAIL] AZURE_OPENAI_ENDPOINT not set")
        sys.exit(1)
    if not api_key:
        print("[FAIL] AZURE_OPENAI_API_KEY not set (webhook registration uses key auth)")
        sys.exit(1)
    if not webhook_url or not webhook_url.startswith("https://"):
        print("[FAIL] WEBHOOK_URL must be a public HTTPS URL")
        sys.exit(1)

    registration_url = f"{endpoint}/openai/v1/dashboard/webhook_endpoints"
    payload = json.dumps({
        "name": webhook_name,
        "url": webhook_url,
        "event_types": event_types,
    }).encode()

    req = urllib.request.Request(
        registration_url,
        data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
        print("[OK] Webhook registered")
        print(f"  id:          {body.get('id', '?')}")
        print(f"  name:        {body.get('name', '?')}")
        print(f"  url:         {body.get('url', '?')}")
        print(f"  event_types: {body.get('event_types', [])}")
        secret = body.get("secret")
        if secret:
            print(f"  secret:      {secret}  ← store in Key Vault immediately; not shown again")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[FAIL] HTTP {e.code}: {body}")
        sys.exit(1)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--webhook-url", default=os.environ.get("WEBHOOK_URL", ""))
    parser.add_argument("--webhook-name", default=os.environ.get("WEBHOOK_NAME", "ai-103-webhook-probe"))
    parser.add_argument("--event-types", default="response.completed")
    args = parser.parse_args()
    event_types = [e.strip() for e in args.event_types.split(",")]
    if args.apply:
        apply(args.webhook_url, args.webhook_name, event_types)
    else:
        preflight(args.webhook_url, args.webhook_name, event_types)


if __name__ == "__main__":
    main()
