# Run: uv run python 03-computer-vision/17_cu_custom_video_analyzer.py [--apply] [--delete]
# Practice-question coverage: Q105.
"""Custom Content Understanding video analyzer: segment a video and generate fields per segment.

Lesson 14 used the prebuilt `prebuilt-videoSearch`. A custom analyzer extends
the base `prebuilt-video` with your own `fieldSchema`; at run time the
generative model fills every field for every segment.

Choosing field type and method:
  string + generate   free-text description the model writes (color scheme,
                      summary of the action) — nothing to extract verbatim
  string + classify   one label from an `enum` you define (scene type)
  object / array      structured subfields when you need JSON with named parts
Video fields use `generate` or `classify`; `extract` is for documents.

Segmentation: `config.enableSegment: true` plus ONE `contentCategories`
entry whose description tells the model where to cut (video supports one
category). `enableSegment: false` treats the whole video as one segment.
Segmentation uses the generative model even when no fields are defined.

Code path:
  Default   print the analyzer JSON; no Azure call.
  --apply   create_analyzer() (persistent) → analyze(SAMPLE_VIDEO_URL) with a
            longer poll timeout → print each segment's time range and fields.
  --delete  delete_analyzer() — cleanup.

Prerequisites / env vars:
  CU_ENDPOINT, CU_API_VERSION=2025-11-01, default CU model deployments.
  SAMPLE_VIDEO_URL — runtime-only HTTPS Blob SAS URL of a short marketing video
  you have rights to (see lesson 12 for SAS rules). Roles: Cognitive Services
  Content Understanding Contributor (create) and Owner (delete).
  Limits: about one sampled frame per second at 512x512; speech only (no music).
"""
import argparse
import json

from _shared.config import env

ANALYZER_ID = "northwind-marketing-video"

_DEFINITION = {
    "description": "Segment Northwind marketing videos into scenes and describe each scene.",
    "baseAnalyzerId": "prebuilt-video",
    "config": {
        "returnDetails": True,
        "locales": ["en-US"],
        "enableSegment": True,
        "contentCategories": {
            "marketing-scene": {
                "description": (
                    "Split the video into scenes at each change of setting or subject. Use the timestamps "
                    "of the frames for start and end times; segments must not overlap."
                )
            }
        },
    },
    "fieldSchema": {
        "name": "MarketingScene",
        "fields": {
            "colorScheme": {
                "type": "string",
                "method": "generate",
                "description": "Dominant colors and the mood they create in this scene, in one sentence.",
            },
            "sceneType": {
                "type": "string",
                "method": "classify",
                "enum": ["product close-up", "people using product", "logo or title card", "other"],
                "description": "What the scene mainly shows.",
            },
        },
    },
}


def validate_definition(definition: dict) -> None:
    config = definition["config"]
    if config.get("enableSegment") and len(config.get("contentCategories", {})) != 1:
        raise ValueError("video segmentation supports exactly one contentCategories entry")
    for name, field in definition["fieldSchema"]["fields"].items():
        if field.get("method") not in ("generate", "classify"):
            raise ValueError(f"video field {name!r} must use generate or classify")
        if field["method"] == "classify" and not field.get("enum"):
            raise ValueError(f"classify field {name!r} needs an enum")


def segment_rows(result: dict) -> list[dict]:
    """Flatten per-segment content into time range plus field values."""
    rows = []
    for content in result.get("result", {}).get("contents", []):
        fields = content.get("fields") or {}
        if not fields:
            continue
        rows.append(
            {
                "start_ms": content.get("startTimeMs"),
                "end_ms": content.get("endTimeMs"),
                **{name: field.get("valueString") for name, field in fields.items()},
            }
        )
    return rows


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="Create the analyzer and analyze SAMPLE_VIDEO_URL.")
    parser.add_argument("--delete", action="store_true", help="Delete the custom analyzer.")
    args = parser.parse_args(argv)

    validate_definition(_DEFINITION)
    if args.delete:
        from _shared.cu_client import delete_analyzer

        print("deleted." if delete_analyzer(ANALYZER_ID) else "analyzer not found.")
        return
    if not args.apply:
        print(f"Analyzer '{ANALYZER_ID}' definition (validated; no Azure call):")
        print(json.dumps(_DEFINITION, indent=2))
        print("Re-run with --apply to create it and analyze SAMPLE_VIDEO_URL; --delete to clean up.")
        return

    source = env("SAMPLE_VIDEO_URL")
    if not source:
        raise SystemExit("Set SAMPLE_VIDEO_URL in your shell to a short video you have rights to.")
    from _shared.cu_client import analyze, create_analyzer

    create_analyzer(ANALYZER_ID, _DEFINITION)
    print(f"analyzer '{ANALYZER_ID}' ready; analyzing video (this can take several minutes)...")
    for row in segment_rows(analyze(ANALYZER_ID, source, poll_timeout=1200, poll_interval=10)):
        print(json.dumps(row))
    print("Delete when finished: uv run python 03-computer-vision/17_cu_custom_video_analyzer.py --delete")


if __name__ == "__main__":
    main()
