# Run: uv run python 08-advanced-agents-other/27_image_generation_tool_preflight.py
"""Build the preview image-generation agent tool without generating an image.

The image-generation tool lets an orchestrator agent call a compatible image
deployment in the same project and region. It is different from a direct image
API call: the model decides when to request the tool, while the application
still governs prompt content, approval, output storage, provenance, cost, and
user disclosure.

Flow:
  Default - build ImageGenTool locally and print the exact typed payload.

What to watch. The tool requires approved GPT Image access and a compatible
orchestrator model. A valid payload does not prove regional/model availability
or safe storage of generated media.

Prerequisites / env vars:
  IMAGE_MODEL  - image deployment alias; defaults through repository settings
"""
from azure.ai.projects.models import ImageGenTool

from _shared.config import settings


def image_generation_tool(model: str) -> ImageGenTool:
    if not model:
        raise ValueError("Image deployment name is required.")
    return ImageGenTool(
        model=model,
        quality="low",
        size="1024x1024",
    )


def main() -> None:
    model = settings().image_model
    print("No cloud calls made.")
    print(f"- Tool payload: {image_generation_tool(model).as_dict()}")
    print("- Preview; requires approved GPT Image access.")
    print("- Orchestrator and image deployment must be compatible and colocated.")
    print("- Review prompt safety, provenance, disclosure, output retention, and cost.")
    print("- This preflight does not create an agent or generate media.")


if __name__ == "__main__":
    main()
