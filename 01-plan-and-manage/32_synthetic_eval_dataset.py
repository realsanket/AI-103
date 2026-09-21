# Run: uv run python 01-plan-and-manage/32_synthetic_eval_dataset.py [--apply]
"""Generate a synthetic evaluation dataset from an agent, prompt, or file (preview).

WHAT
────
Foundry's data generation service synthesizes evaluation rows when you have no
production traffic yet. Two task types:

  simple_qna       — single-turn question/answer pairs
                     Uses `SimpleQnADataGenerationJobOptions`, wire type
                     `simple_qna`. Rows carry `query` + `ground_truth`.
  simulation_seed  — multi-turn scenario descriptions
                     Uses `SimulationSeedDataGenerationJobOptions`, wire type
                     `simulation_seed`. Rows carry `test_case_description`
                     (required), and optional `id`, `category`,
                     `desired_num_turns`. These feed the Simulate conversations
                     flow (lesson group 22).

Three input source types (combinable in one job):

  AgentDataGenerationJobSource  — seed from a deployed agent's instructions
  PromptDataGenerationJobSource — inline text prompt
  FileDataGenerationJobSource   — uploaded reference document (>=1 KB,
                                   `.txt/.md/.csv/.json/.xml/.html/.pdf/.png/
                                   .jpg/.jpeg/.gif/.tiff/.tif/.svg`)

WHY
───
Fills the pre-launch or low-traffic gap where trace-based datasets don't yet
exist. Also useful for stable regression baselines and covering edge cases the
agent hasn't seen in production.

CODE PATH
─────────
  preflight (default): prints the resolved `DataGenerationJob` request body
                       (no cloud call).
  --apply:
    1. Build the source (Agent | Prompt | File) from env.
    2. If SYNTHETIC_INPUT_PATH points to a file, upload via
       `project.get_openai_client().files.create(purpose="user_data")` and
       wait until `status == "processed"`.
    3. Submit `project.beta.datasets.begin_create_generation_job(job)`.
    4. Poll `poller.status()` until done; then resolve the produced
       `DatasetDataGenerationJobOutput` and print `dataset.id`.
    5. Download rows to `01-plan-and-manage/data/<output>.jsonl`.

WHAT TO WATCH
─────────────
- `max_samples` must be 15..1000 per service.
- Reference files: must be in `processed` state and >= 1 KB.
- Preview: SDK surface is under `project_client.beta.datasets`; needs
  `azure-ai-projects >= 2.5.0`.
- Region: data generation supported in a limited region set — check
  `evaluation-regions-limits-virtual-network` before `--apply`.

ENV VARS
────────
  AZURE_AI_PROJECT_ENDPOINT  — Foundry project endpoint URL (required)
  AZURE_AI_AGENT_NAME        — agent name for AgentDataGenerationJobSource
  AZURE_AI_AGENT_VERSION     — agent version (default: "1")
  AZURE_AI_MODEL_DEPLOYMENT_NAME — generator model (Responses API capable)
  SYNTHETIC_TASK             — "simple_qna" | "simulation_seed"
                               (default: "simple_qna")
  SYNTHETIC_INPUT_PATH       — path to a file. If ends in `.txt` short enough
                               to be inline (< 4 KB), treated as prompt text;
                               otherwise uploaded as reference file.
                               If unset, source falls back to agent.
  SYNTHETIC_MAX_SAMPLES      — 15..1000 (default: 15)
  SYNTHETIC_OUTPUT_NAME      — dataset name (default: "synthetic-eval-set")
"""
from __future__ import annotations

import argparse
import io
import json
import os
import time
from pathlib import Path

_DEFAULT_TASK = "simple_qna"
_DEFAULT_MAX_SAMPLES = 15
_DEFAULT_OUTPUT_NAME = "synthetic-eval-set"
_INLINE_PROMPT_MAX_BYTES = 4096
_POLL_INTERVAL_SECONDS = 10


def _resolve_source_kind(input_path: str | None) -> str:
    """Return 'agent', 'prompt', or 'file' based on env."""
    if not input_path:
        return "agent"
    p = Path(input_path)
    if not p.is_file():
        return "agent"
    if p.suffix.lower() == ".txt" and p.stat().st_size < _INLINE_PROMPT_MAX_BYTES:
        return "prompt"
    return "file"


def _request_body(
    task: str,
    source_kind: str,
    agent_name: str,
    agent_version: str,
    input_path: str | None,
    model_name: str,
    max_samples: int,
    output_name: str,
) -> dict:
    """Doc-verbatim JSON shape for a DataGenerationJob request."""
    sources: list[dict] = []
    if source_kind == "agent":
        sources.append({
            "type": "agent",
            "description": "Agent definition used to seed generation.",
            "agent_name": agent_name,
            "agent_version": agent_version,
        })
    elif source_kind == "prompt":
        prompt_text = Path(input_path).read_text(encoding="utf-8") if input_path else ""
        sources.append({
            "type": "prompt",
            "description": f"Inline prompt from {input_path}",
            "prompt": prompt_text,
        })
    else:  # file
        sources.append({
            "type": "file",
            "description": f"Reference file: {input_path}",
            "id": "<uploaded-at-apply-time>",
        })
    options_type = "simple_qna" if task == "simple_qna" else "simulation_seed"
    return {
        "inputs": {
            "name": output_name,
            "scenario": "evaluation",
            "sources": sources,
            "options": {
                "type": options_type,
                "max_samples": max_samples,
                "model_options": {"model": model_name},
            },
            "output_options": {"name": output_name},
        }
    }


def preflight(args: argparse.Namespace) -> None:
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "<unset>")
    agent = os.environ.get("AZURE_AI_AGENT_NAME", "<unset>")
    agent_version = os.environ.get("AZURE_AI_AGENT_VERSION", "1")
    model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "<unset>")
    source_kind = _resolve_source_kind(args.input_path)
    body = _request_body(
        task=args.task,
        source_kind=source_kind,
        agent_name=agent,
        agent_version=agent_version,
        input_path=args.input_path,
        model_name=model,
        max_samples=args.max_samples,
        output_name=args.output_name,
    )
    print("PREVIEW: no cloud resources created.")
    print(f"Project endpoint : {endpoint}")
    print(f"Task type        : {args.task}  (preview)")
    print(f"Source type      : {source_kind}")
    print(f"Generator model  : {model}")
    print(f"Max samples      : {args.max_samples}  (service limit 15..1000)")
    print(f"Output dataset   : {args.output_name}")
    print()
    print("Request body (project_client.beta.datasets.begin_create_generation_job):")
    print(json.dumps(body, indent=2))
    print()
    print("Run again with --apply to submit the job and write rows locally.")


def _upload_file(project, path: Path):
    """Upload reference file and wait until status == 'processed'."""
    openai_client = project.get_openai_client()
    data = path.read_bytes()
    if len(data) < 1024:
        raise ValueError(f"Reference file must be >= 1 KB, got {len(data)} bytes.")
    uploaded = openai_client.files.create(
        file=(path.name, io.BytesIO(data)),
        purpose="user_data",
    )
    while uploaded.status not in ("processed", "error"):
        time.sleep(2)
        uploaded = openai_client.files.retrieve(file_id=uploaded.id)
    if uploaded.status != "processed":
        raise RuntimeError(f"File failed to process: {uploaded.status}")
    return uploaded


def apply(args: argparse.Namespace) -> None:
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import (
        AgentDataGenerationJobSource,
        DataGenerationJob,
        DataGenerationJobInputs,
        DataGenerationJobOutputOptions,
        DataGenerationJobScenario,
        DataGenerationModelOptions,
        DatasetDataGenerationJobOutput,
        FileDataGenerationJobSource,
        PromptDataGenerationJobSource,
        SimpleQnADataGenerationJobOptions,
        SimulationSeedDataGenerationJobOptions,
    )
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    source_kind = _resolve_source_kind(args.input_path)
    if source_kind == "agent":
        agent_name = os.environ["AZURE_AI_AGENT_NAME"]
        agent_version = os.environ.get("AZURE_AI_AGENT_VERSION", "1")
        sources = [AgentDataGenerationJobSource(
            description="Agent definition used to seed generation.",
            agent_name=agent_name,
            agent_version=agent_version,
        )]
    elif source_kind == "prompt":
        prompt_text = Path(args.input_path).read_text(encoding="utf-8")
        sources = [PromptDataGenerationJobSource(
            description=f"Inline prompt from {args.input_path}",
            prompt=prompt_text,
        )]
    else:  # file
        uploaded = _upload_file(project, Path(args.input_path))
        print(f"Uploaded reference file: {uploaded.id} (status={uploaded.status})")
        sources = [FileDataGenerationJobSource(
            description=f"Reference file: {args.input_path}",
            id=uploaded.id,
        )]

    options_cls = (
        SimpleQnADataGenerationJobOptions
        if args.task == "simple_qna"
        else SimulationSeedDataGenerationJobOptions
    )
    job = DataGenerationJob(
        inputs=DataGenerationJobInputs(
            name=args.output_name,
            scenario=DataGenerationJobScenario.EVALUATION,
            sources=sources,
            options=options_cls(
                max_samples=args.max_samples,
                model_options=DataGenerationModelOptions(model=model),
            ),
            output_options=DataGenerationJobOutputOptions(name=args.output_name),
        ),
    )
    poller = project.beta.datasets.begin_create_generation_job(job=job)
    print("Periodically check job status:")
    while not poller.done():
        print(f"\tstatus=`{poller.status()}`")
        time.sleep(_POLL_INTERVAL_SECONDS)
    result = poller.result()

    output_name, output_version = "", ""
    for output in (result.outputs if result is not None else None) or []:
        if isinstance(output, DatasetDataGenerationJobOutput):
            output_name = output.name or ""
            output_version = output.version or ""
            break
    if not output_name:
        raise RuntimeError("Job produced no dataset output.")

    dataset = project.datasets.get(name=output_name, version=output_version)
    print(f"Generated dataset: {dataset.name} v{dataset.version} (id: {dataset.id})")

    # Write rows locally for offline inspection.
    out_dir = Path("01-plan-and-manage/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{output_name}.jsonl"
    try:
        with out_path.open("w", encoding="utf-8") as fh:
            for row in project.datasets.list_rows(name=output_name, version=output_version):
                fh.write(json.dumps(row) + "\n")
        print(f"Wrote rows to: {out_path}")
    except Exception as exc:  # pragma: no cover - preview API surface may vary
        print(f"Row download skipped ({type(exc).__name__}): {exc}")
        print("Preview rows on the portal Data tab before evaluating.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate a synthetic evaluation dataset (preview).")
    parser.add_argument(
        "--task",
        default=os.environ.get("SYNTHETIC_TASK", _DEFAULT_TASK),
        choices=("simple_qna", "simulation_seed"),
        help="Task type. simulation_seed feeds the Simulate conversations flow.",
    )
    parser.add_argument(
        "--input-path",
        default=os.environ.get("SYNTHETIC_INPUT_PATH"),
        help="File path: .txt < 4KB → inline prompt; other files → uploaded reference. Omit to use agent source.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=int(os.environ.get("SYNTHETIC_MAX_SAMPLES", _DEFAULT_MAX_SAMPLES)),
        help="Generated rows (15..1000).",
    )
    parser.add_argument(
        "--output-name",
        default=os.environ.get("SYNTHETIC_OUTPUT_NAME", _DEFAULT_OUTPUT_NAME),
        help="Dataset name for output_options.",
    )
    parser.add_argument("--apply", action="store_true", help="Submit the data generation job.")
    args = parser.parse_args(argv)

    if not (15 <= args.max_samples <= 1000):
        parser.error("--max-samples must be between 15 and 1000 (service limit).")

    if not args.apply:
        preflight(args)
        return

    required = ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    if _resolve_source_kind(args.input_path) == "agent":
        required.append("AZURE_AI_AGENT_NAME")
    for var in required:
        if not os.environ.get(var):
            parser.error(f"{var} is required with --apply.")
    apply(args)


if __name__ == "__main__":
    main()
