# Run: uv run python 03-computer-vision/questions/01_image_edit_fidelity_preflight.py
# Practice-question coverage: Q11, Q20, Q60.
"""Question supplement: preserve input identity while editing an image.

Maps PDF questions 11, 20, and 60. The plan reflects the current image-edit
surface: use an input image with high fidelity for preservation, and provide a
mask only when the requested change is region-bounded. It does not generate an
image or make a billable call.
"""
from __future__ import annotations


def image_edit_plan(*, preserve_subject: bool, selected_region_only: bool) -> dict[str, object]:
    plan: dict[str, object] = {
        "operation": "images.edit",
        "input_image": "required",
        "prompt": "Describe the requested change and what must remain unchanged.",
        "input_fidelity": "high" if preserve_subject else "low",
        "requires_mask": selected_region_only,
    }
    if selected_region_only:
        plan["mask_rule"] = "transparent pixels are editable; opaque pixels must be preserved"
    return plan


def main() -> None:
    print("No cloud calls made. Review the image-edit plan:")
    print(image_edit_plan(preserve_subject=True, selected_region_only=True))


if __name__ == "__main__":
    main()
