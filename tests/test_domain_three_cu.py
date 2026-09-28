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


blob = _lesson("12_cu_blob_preflight.py")
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


video_analyzer = _lesson("17_cu_custom_video_analyzer.py")


class CustomVideoAnalyzerTests(TestCase):
    def test_definition_rules_for_video_fields_and_segments(self) -> None:
        video_analyzer.validate_definition(video_analyzer._DEFINITION)
        broken = {
            "config": {"enableSegment": True, "contentCategories": {"a": {}, "b": {}}},
            "fieldSchema": {"fields": {}},
        }
        with self.assertRaisesRegex(ValueError, "exactly one contentCategories"):
            video_analyzer.validate_definition(broken)
        extract = {"config": {}, "fieldSchema": {"fields": {"logo": {"type": "string", "method": "extract"}}}}
        with self.assertRaisesRegex(ValueError, "generate or classify"):
            video_analyzer.validate_definition(extract)
        classify = {"config": {}, "fieldSchema": {"fields": {"scene": {"type": "string", "method": "classify"}}}}
        with self.assertRaisesRegex(ValueError, "needs an enum"):
            video_analyzer.validate_definition(classify)

    def test_segment_rows_flatten_time_ranges_and_fields(self) -> None:
        result = {
            "result": {
                "contents": [
                    {"startTimeMs": 0, "endTimeMs": 900, "fields": {}},
                    {
                        "startTimeMs": 1000,
                        "endTimeMs": 4000,
                        "fields": {
                            "colorScheme": {"valueString": "Warm orange tones"},
                            "sceneType": {"valueString": "product close-up"},
                        },
                    },
                ]
            }
        }
        self.assertEqual(
            video_analyzer.segment_rows(result),
            [{"start_ms": 1000, "end_ms": 4000, "colorScheme": "Warm orange tones", "sceneType": "product close-up"}],
        )

    def test_default_is_local_and_apply_needs_a_video(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            video_analyzer.main([])
        self.assertIn("no Azure call", output.getvalue())
        with patch.dict("os.environ", {"SAMPLE_VIDEO_URL": ""}), self.assertRaises(SystemExit):
            video_analyzer.main(["--apply"])
        with patch("_shared.cu_client.delete_analyzer", return_value=False) as delete, redirect_stdout(io.StringIO()):
            video_analyzer.main(["--delete"])
        delete.assert_called_once_with(video_analyzer.ANALYZER_ID)
