"""Image moderation via a Foundry agent + content filter inspection.

The `content_filters` block on the response tells you *why* something was
blocked (hate / sexual / violence / self-harm severity + block flag) — same
taxonomy the Guardrails/evaluators use.
"""
import base64

from _shared.config import SAMPLE_DATA
from _shared.foundry_client import project_client

AGENT_NAME = "northwind-support"


def main() -> None:
    img = SAMPLE_DATA / "images" / "support.png"
    b64 = base64.b64encode(img.read_bytes()).decode("utf-8")

    project = project_client()
    openai = project.get_openai_client()
    r = openai.responses.create(
        extra_body={"agent_reference": {"type": "agent_reference", "name": AGENT_NAME}},
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "I'm getting this error connecting to VPN. What does it mean?"},
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                ],
            }
        ],
    )
    print(r.output_text)
    filters = getattr(r, "model_extra", {}).get("content_filters") if hasattr(r, "model_extra") else None
    if filters:
        print("\n--- content filters ---")
        print(filters)


if __name__ == "__main__":
    main()
