import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from _shared.config import SAMPLE_DATA
from _shared.vision_inputs import image_data_url, validate_edit_inputs


def _lesson(name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path("03-computer-vision") / f"{name}.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


video_generation = _lesson("07_video_generation")
alt_text = _lesson("02_alt_text_captions")


class DomainThreeRuntimeTests(unittest.TestCase):
    def test_local_image_inputs_are_valid_before_cloud_calls(self) -> None:
        source = SAMPLE_DATA / "images" / "product_photo.png"
        mask = SAMPLE_DATA / "images" / "mask.png"
        validate_edit_inputs(source, mask)
        self.assertTrue(image_data_url(source).startswith("data:image/png;base64,"))

    def test_sora_failure_includes_service_reason(self) -> None:
        queued = SimpleNamespace(id="video_9", status="queued", progress=0)
        failed = SimpleNamespace(
            id="video_9", status="failed", progress=0, error=SimpleNamespace(code="content_policy_violation", message=None)
        )
        client = SimpleNamespace(videos=SimpleNamespace(retrieve=lambda video_id: failed))
        with patch.object(video_generation.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "content_policy_violation"):
                video_generation.wait_for_video(client, queued)

    def test_accessibility_draft_flags_invalid_labeling(self) -> None:
        response = SimpleNamespace(output_text="Description without required labels")
        self.assertIn("REVIEW:", alt_text._accessibility_draft(response))

    def test_accessibility_draft_keeps_valid_labeled_output(self) -> None:
        response = SimpleNamespace(
            output_text="ALT: Chart showing quarterly sales.\nDESCRIPTION: Sales rise each quarter."
        )
        self.assertEqual(
            alt_text._accessibility_draft(response),
            "ALT: Chart showing quarterly sales.\nDESCRIPTION: Sales rise each quarter.",
        )


if __name__ == "__main__":
    unittest.main()
