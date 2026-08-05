# Run: uv run python 06-model-customization-other/05_submit_training.py --kind sft --train train.jsonl --model <base> --apply
"""Upload reviewed data and submit SFT, DPO, or RFT only with --apply."""
from __future__ import annotations

import argparse
from pathlib import Path

from _shared.openai_client import openai_client
from lab_common import print_preflight
from importlib import import_module


def validators(kind: str):
    names = {
        "sft": ("01_sft_dataset", "validate_sft"),
        "dpo": ("02_dpo_dataset", "validate_dpo"),
        "rft": ("03_rft_dataset_grader", "validate_rft"),
    }
    module, function = names[kind]
    return getattr(import_module(module), function)


def submit(args: argparse.Namespace) -> None:
    client = openai_client()
    with args.train.open("rb") as source:
        training = client.files.create(file=source, purpose="fine-tune")
    validation_id = None
    if args.validation:
        with args.validation.open("rb") as source:
            validation_id = client.files.create(file=source, purpose="fine-tune").id
    kwargs: dict = {"model": args.model, "training_file": training.id, "suffix": args.suffix}
    if validation_id:
        kwargs["validation_file"] = validation_id
    if args.kind == "sft":
        kwargs["method"] = {"type": "supervised"}
    elif args.kind == "dpo":
        kwargs["method"] = {"type": "dpo", "dpo": {"beta": args.beta, "l2_multiplier": args.l2_multiplier}}
    else:
        kwargs["method"] = {
            "type": "reinforcement",
            "reinforcement": {
                "grader": {
                    "type": "python",
                    "name": "reviewed_python_grader",
                    "source": args.grader.read_text(encoding="utf-8"),
                }
            },
        }
    if args.training_type:
        kwargs["extra_body"] = {"trainingType": args.training_type}
    job = client.fine_tuning.jobs.create(**kwargs)
    print(f"Uploaded training file: {training.id}")
    print(f"Submitted {args.kind.upper()} job: {job.id} ({job.status})")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Submit a reviewed Foundry customization job.")
    parser.add_argument("--kind", choices=("sft", "dpo", "rft"), required=True)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path)
    parser.add_argument("--grader", type=Path, help="Required for RFT.")
    parser.add_argument("--model", required=True, help="Supported base model and version.")
    parser.add_argument("--suffix", default="northwind-custom")
    parser.add_argument("--beta", type=float, default=0.1)
    parser.add_argument("--l2-multiplier", type=float, default=0.1)
    parser.add_argument("--training-type", choices=("GlobalStandard", "Standard", "Developer"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.kind == "rft":
        if args.validation is None or args.grader is None:
            parser.error("RFT requires --validation and --grader.")
        validators("rft")(args.train, args.grader)
        validators("rft")(args.validation, args.grader)
    else:
        validator = validators(args.kind)
        validator(args.train)
        if args.validation:
            validator(args.validation)
    if not args.apply:
        print_preflight([
            f"Validated {args.kind.upper()} input locally.",
            "Would upload each supplied file with purpose fine-tune, then submit one training job.",
            "Training type is optional because supported choices depend on model, region, residency, and current catalog.",
        ])
        return
    submit(args)


if __name__ == "__main__":
    main()
