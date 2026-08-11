# Run: uv run python 09-current-ai-services-other/07_healthcare_ai_preflight.py [--apply] [--model cxr|medimage]
"""Validate healthcare AI model deployment and probe the endpoint.

Azure AI Foundry provides specialized healthcare AI models: CXRReportGen
(chest X-ray → radiology report generation) and MedImageInsight (radiology
image → embedding / classification). Both deploy as premium serverless
endpoints — billing is per-image, not per-token. They are NOT general-purpose
vision models; they require DICOM-sourced or standard medical imaging input.

Default preflight checks env vars and explains the two model types. --apply
sends a minimal probe payload to verify the endpoint is reachable and
authenticated. A 400 response on a minimal payload = reachable but expects
valid medical image data (expected behavior for probe).

Code path:
  preflight: check HEALTHCARE_AI_ENDPOINT + HEALTHCARE_AI_KEY.
  --apply: urllib.request.urlopen(POST endpoint, minimal JSON payload,
  headers with Bearer token) → print HTTP status.
  401 = bad key/credential. 200 or 400 = endpoint reachable.

What to watch. HTTP 200 or 400 = endpoint reachable and authed.
HTTP 401 = wrong HEALTHCARE_AI_KEY or Entra credential not authorized.
HTTP 404 = wrong endpoint URL or model not deployed.

Prerequisites / env vars:
  HEALTHCARE_AI_ENDPOINT  — full HTTPS endpoint URL for the deployed model
  HEALTHCARE_AI_KEY       — managed endpoint key (omit for DefaultAzureCredential)
  --model                 — cxr | medimage (informational label only)
  --apply                 — probe the endpoint
"""
import argparse
import json
import os
import urllib.error
import urllib.request


def preflight(model: str) -> None:
    endpoint = os.environ.get("HEALTHCARE_AI_ENDPOINT", "")
    key = os.environ.get("HEALTHCARE_AI_KEY", "")
    print(f"Healthcare AI preflight — model: {model} (no cloud calls).")
    print(f"- HEALTHCARE_AI_ENDPOINT: {'configured' if endpoint else 'MISSING'}")
    print(f"- HEALTHCARE_AI_KEY: {'configured' if key else 'not set (DefaultAzureCredential)'}")
    print()
    print("Model types:")
    print("  cxr      — CXRReportGen: chest X-ray DICOM → radiology report text")
    print("  medimage — MedImageInsight: radiology image → embeddings / classification")
    print()
    print("Deploy: Foundry portal → Model Catalog → Healthcare AI → Deploy.")
    print("Input: DICOM or medical PNG/JPG. NOT general photos.")
    print("Run --apply to probe endpoint health.")


def apply(model: str) -> None:
    endpoint = os.environ.get("HEALTHCARE_AI_ENDPOINT", "")
    key = os.environ.get("HEALTHCARE_AI_KEY", "")
    if not endpoint:
        raise SystemExit("Set HEALTHCARE_AI_ENDPOINT.")

    payload = json.dumps({"input_data": {"columns": ["image"], "data": [[""]]}}).encode()
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    else:
        from azure.identity import DefaultAzureCredential
        token = DefaultAzureCredential().get_token("https://ml.azure.com/.default").token
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    print(f"Probing {model} endpoint ...")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            print(f"HTTP {resp.status}: endpoint reachable")
            print(f"Response: {body[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 400:
            print(f"HTTP 400: endpoint reachable (400 expected — probe payload lacks real image data)")
        elif e.code == 401:
            print("HTTP 401: auth failed — check HEALTHCARE_AI_KEY or Entra credential.")
        elif e.code == 404:
            print("HTTP 404: endpoint not found — verify HEALTHCARE_AI_ENDPOINT URL and model deployed.")
        else:
            print(f"HTTP {e.code}: {body[:200]}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Probe healthcare AI model endpoint.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--model", default="cxr", choices=["cxr", "medimage"])
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.model)
        return
    apply(args.model)


if __name__ == "__main__":
    main()
