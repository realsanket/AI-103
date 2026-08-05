import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


def _lesson(name: str):
    path = Path("03-computer-vision") / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


blob = _lesson("14_cu_blob_preflight.py")
handoff = _lesson("15_cu_visual_handoff.py")


class DomainThreeContentUnderstandingTests(TestCase):
    def test_preflights_make_no_cloud_calls(self) -> None:
        source = "https://account.blob.core.windows.net/media/demo.mp4?sp=r&se=tomorrow&sig=secret"
        for lesson in (blob, handoff):
            output = io.StringIO()
            with patch.object(handoff, "analyze") as analyze, redirect_stdout(output):
                lesson.main(["--source-url", source])
            analyze.assert_not_called()
            self.assertIn("no cloud calls made", output.getvalue().lower())

    def test_blob_preflight_redacts_sas_and_detects_read_access(self) -> None:
        source = "https://account.blob.core.windows.net/media/demo.png?sp=r&se=tomorrow&sig=secret"
        details = blob.preflight(source)
        self.assertEqual(details["source"]["blob_path"], "demo.png")
        self.assertFalse(any("read permission" in warning for warning in details["warnings"]))
        self.assertNotIn("secret", str(details))

    def test_analyzer_selection_and_bounded_normalization(self) -> None:
        source = "https://account.blob.core.windows.net/media/demo.mp4?sig=secret"
        self.assertEqual(handoff.select_analyzer(source), "prebuilt-videoSearch")
        result = {
            "status": "succeeded",
            "warnings": [{"message": "Retry with sig=secret"}],
            "result": {
                "contents": [
                    {
                        "startTimeMs": 100,
                        "endTimeMs": 200,
                        "fields": {
                            "Summary": {
                                "valueString": "Scene summary",
                                "source": "V(100,200)",
                            }
                        },
                    },
                    {"markdown": "fallback"},
                ]
            },
        }
        normalized = handoff.normalize_result(result, "prebuilt-videoSearch", source, max_segments=1)
        self.assertEqual(normalized["segments"][0]["summary"], "Scene summary")
        self.assertEqual(normalized["segments"][0]["source"], "V(100,200)")
        self.assertTrue(normalized["segments_truncated"])
        self.assertNotIn("secret", str(normalized))

    def test_apply_calls_cu_only_after_explicit_flag(self) -> None:
        source = "https://account.blob.core.windows.net/media/demo.png?sig=secret"
        with patch.object(handoff, "analyze", return_value={"status": "succeeded", "result": {}}) as analyze:
            response = handoff.production_handoff(source)
        analyze.assert_called_once_with("prebuilt-imageSearch", source)
        self.assertEqual(response["analyzer"], "prebuilt-imageSearch")
