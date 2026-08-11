# Run: uv run python 03-computer-vision/16_image_generation_dalle.py [--apply] [--prompt "<text>"] [--size 1024x1024]
"""Generate images from text prompts using DALL-E 3 via Azure OpenAI.

DALL-E 3 converts natural-language prompts into pixel images. Azure OpenAI
hosts DALL-E 3 as a named deployment; access is via images.generate(). The API
returns either a temporary URL (expires ~1h) or base64-encoded PNG data. This
lesson uses b64_json to avoid URL expiry in CI contexts.

Default preflight checks the DALL_E_MODEL deployment env var. --apply sends
the prompt and saves the image to disk as generated_image.png. revised_prompt
shows how DALL-E rewrote the request for safety/clarity.

Code path:
  --apply: openai_client().images.generate(model=DALL_E_MODEL, prompt=prompt,
  n=1, size=size, response_format="b64_json")
  → base64.b64decode(response.data[0].b64_json) → write PNG to disk.

What to watch. revised_prompt in output shows DALL-E's reinterpretation.
HTTP 400 = prompt content policy rejection — rephrase the prompt.
b64_json is ~0.7 MB per 1024x1024 image.

Prerequisites / env vars:
  PROJECT_ENDPOINT  — Foundry project HTTPS URL (used by openai_client())
  DALL_E_MODEL      — DALL-E 3 deployment name (e.g. dall-e-3)
  --prompt          — image description text
  --size            — 1024x1024 | 1024x1792 | 1792x1024 (default: 1024x1024)
  --out             — output file path (default: generated_image.png)
  --apply           — generate and save image
"""
import argparse
import base64
import os
from pathlib import Path

from _shared.openai_client import openai_client

_DEFAULT_PROMPT = "A photorealistic aerial view of Azure data centers surrounded by green forest at sunset, dramatic lighting."
_DEFAULT_OUT = Path("generated_image.png")


def preflight(prompt: str, size: str, out: Path) -> None:
    model = os.environ.get("DALL_E_MODEL", "")
    print("Image generation preflight (no cloud calls).")
    print(f"- DALL_E_MODEL: {model or 'MISSING — set to your dall-e-3 deployment name'}")
    print(f"- prompt: {prompt!r}")
    print(f"- size: {size}")
    print(f"- output: {out}")
    print("Run --apply to generate and save the image.")


def apply(prompt: str, size: str, out: Path) -> None:
    model = os.environ.get("DALL_E_MODEL", "")
    if not model:
        raise SystemExit("Set DALL_E_MODEL to your DALL-E 3 deployment name.")
    client = openai_client()
    print(f"Generating with {model!r}, size={size} ...")
    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size=size,
        response_format="b64_json",
    )
    item = response.data[0]
    revised = getattr(item, "revised_prompt", None)
    if revised:
        print(f"Revised prompt: {revised}")
    img_bytes = base64.b64decode(item.b64_json)
    out.write_bytes(img_bytes)
    print(f"Image saved: {out} ({len(img_bytes):,} bytes)")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate image from text using DALL-E 3.")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--prompt", default=_DEFAULT_PROMPT)
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1024x1792", "1792x1024"])
    parser.add_argument("--out", type=Path, default=_DEFAULT_OUT)
    args = parser.parse_args(argv)
    if not args.apply:
        preflight(args.prompt, args.size, args.out)
        return
    apply(args.prompt, args.size, args.out)


if __name__ == "__main__":
    main()
