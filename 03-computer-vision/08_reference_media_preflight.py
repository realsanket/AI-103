# Run: uv run python 03-computer-vision/08_reference_media_preflight.py
"""Opt-in Sora 2 reference-image video generation — preflight + explicit `--apply`.

Run without flags for a local preflight. To submit a job, pass an owned,
consented reference image and `--apply`. Sora 2 accepts one JPEG, PNG, or
WebP reference image as its first-frame visual anchor. The reference and
output must be exactly `1280x720` or `720x1280`.

Reference media is an external input boundary. Confirm that you have rights
to use it, do not submit personal images without an appropriate basis, and
do not use images containing human faces: Sora 2 currently rejects them.
This lab creates a billable preview job and does not download or retain its
output locally.
"""
import argparse
from pathlib import Path

from PIL import Image

from _shared.config import settings
from _shared.openai_client import openai_client

_SUPPORTED_SIZES = {(1280, 720), (720, 1280)}
_SUPPORTED_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}


def reference_image(path: str) -> Path:
    """Validate documented Sora 2 reference-image constraints locally."""
    image_path = Path(path)
    if not image_path.is_file():
        raise SystemExit(f"Reference image does not exist: {image_path}")
    if image_path.suffix.lower() not in _SUPPORTED_SUFFIXES:
        raise SystemExit("Reference image must be JPEG, PNG, or WebP.")
    with Image.open(image_path) as image:
        if image.size not in _SUPPORTED_SIZES:
            raise SystemExit(
                "Reference image must be exactly 1280x720 or 720x1280; "
                f"received {image.width}x{image.height}."
            )
    return image_path


def preflight() -> None:
    print("Reference-media preflight only. No cloud calls made.")
    print("Use one owned, consented JPEG, PNG, or WebP image at 1280x720 or 720x1280.")
    print("Sora 2 rejects input images containing human faces; do not submit personal images.")
    print("Use --apply --reference-image PATH only after reviewing rights, privacy, prompt, and cost.")


def apply(reference_path: str) -> None:
    image_path = reference_image(reference_path)
    with image_path.open("rb") as image:
        video = openai_client().videos.create(
            model=settings().video_model,
            prompt=(
                "Animate this product image with a slow, steady camera move. "
                "Preserve the product identity and use a clean studio setting."
            ),
            size="1280x720",
            seconds="8",
            input_reference=image,
        )
    print(f"Submitted reference-media job: {video.id} ({video.status})")
    print("Retrieve or delete the job through the documented Sora 2 video API.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Preflight or submit a Sora 2 reference-image job.")
    parser.add_argument("--apply", action="store_true", help="Submit a billable Sora 2 job.")
    parser.add_argument("--reference-image", help="Owned, consented 1280x720 or 720x1280 image.")
    args = parser.parse_args(argv)
    if not args.apply:
        preflight()
        return
    if not args.reference_image:
        raise SystemExit("--apply requires --reference-image.")
    apply(args.reference_image)


if __name__ == "__main__":
    main()
