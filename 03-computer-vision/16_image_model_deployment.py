# Run: uv run python 03-computer-vision/16_image_model_deployment.py [--apply] [--generate]
# Practice-question coverage: Q136.
"""Deploy an image-generation model with the Azure CLI, then verify it with one image.

Image models are deployed like any other Foundry model: pick it in the Foundry
portal model catalog (Models → Deploy) or automate the same operation with the
Azure CLI `az cognitiveservices account deployment create`. Inference SDKs
(Python, JavaScript) *call* a deployment; they are not how you deploy the model.

DALL-E 3 was retired on March 4, 2026 and existing DALL-E deployments no longer
work. Current image models are the GPT-image series; this lesson defaults to
`gpt-image-2` (GA). Deployments are control-plane resources: `--apply` needs
Cognitive Services Contributor or Foundry Account Owner on the Foundry resource,
and generating an image needs a data-plane role such as Cognitive Services User.

Code path:
  Default      deployment_command() → print the az command; no Azure call.
  --apply      run the az command (requires `az login`); creates or updates the
               deployment named IMAGE_MODEL.
  --generate   openai_client().images.generate(model=IMAGE_MODEL, ...) → save a
               PNG under _shared/sample_data/generated/ (billed per image).

Prerequisites / env vars:
  AZURE_RESOURCE_GROUP, FOUNDRY_ENDPOINT (account name), IMAGE_MODEL (deployment
  name), AZURE_OPENAI_ENDPOINT for --generate.
"""
import argparse
import shlex
import subprocess

from _shared.config import SAMPLE_DATA, settings

MODEL_NAME = "gpt-image-2"
MODEL_VERSION = "2026-04-21"
OUTPUT = SAMPLE_DATA / "generated" / "deployment_check.png"
PROMPT = "A flat illustration of a warehouse robot sorting parcels, soft pastel palette."


def deployment_command(
    resource_group: str,
    account: str,
    deployment: str,
    *,
    model: str = MODEL_NAME,
    version: str = MODEL_VERSION,
    sku: str = "GlobalStandard",
    capacity: int = 1,
) -> list[str]:
    if model.startswith("dall-e"):
        raise ValueError("DALL-E models are retired; deploy a GPT-image model instead.")
    return [
        "az", "cognitiveservices", "account", "deployment", "create",
        "--resource-group", resource_group,
        "--name", account,
        "--deployment-name", deployment,
        "--model-format", "OpenAI",
        "--model-name", model,
        "--model-version", version,
        "--sku-name", sku,
        "--sku-capacity", str(capacity),
    ]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Run the az deployment command.")
    parser.add_argument("--generate", action="store_true", help="Generate one verification image.")
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--version", default=MODEL_VERSION)
    parser.add_argument("--sku", default="GlobalStandard")
    args = parser.parse_args(argv)

    s = settings()
    account = "<account>"
    if s.foundry_endpoint:
        from _shared.foundry_management import foundry_account_name

        account = foundry_account_name(s.foundry_endpoint)
    command = deployment_command(
        s.azure_resource_group or "<resource-group>",
        account,
        s.image_model,
        model=args.model,
        version=args.version,
        sku=args.sku,
    )
    print("Deployment command:")
    print("  " + shlex.join(command))

    if args.apply:
        if "<" in " ".join(command):
            raise SystemExit("Set AZURE_RESOURCE_GROUP and FOUNDRY_ENDPOINT before --apply.")
        subprocess.run(command, check=True)
        print(f"Deployment '{s.image_model}' created or updated.")
    if args.generate:
        from _shared.openai_client import openai_client
        from _shared.vision_inputs import save_generated_image

        response = openai_client().images.generate(
            model=s.image_model, prompt=PROMPT, n=1, size="1024x1024", quality="low", output_format="png"
        )
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        save_generated_image(response, OUTPUT)
        print(f"saved: {OUTPUT}")
    if not (args.apply or args.generate):
        print("Preflight only: nothing deployed. Use --apply to deploy and --generate to verify.")


if __name__ == "__main__":
    main()
