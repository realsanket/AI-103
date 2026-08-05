import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, patch

from _shared.config import SAMPLE_DATA


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(
        file_name.replace(".py", ""), Path("04-text-and-speech") / file_name
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


speech_mcp = _lesson("21_speech_mcp_preflight.py")
translator = _lesson("22_translator_secure_config.py")
batch = _lesson("23_translator_batch_operations.py")
voice_live = _lesson("24_voice_live_audio_flow.py")
governance = _lesson("25_text_speech_governance_preflight.py")


class DomainFourAdvancedTests(TestCase):
    def test_default_paths_make_no_cloud_calls(self) -> None:
        for lesson in (speech_mcp, translator, batch, voice_live, governance):
            output = io.StringIO()
            with redirect_stdout(output):
                lesson.main([])
            self.assertIn("No cloud calls made.", output.getvalue())

    def test_speech_mcp_requires_versioned_https_endpoint(self) -> None:
        with self.assertRaisesRegex(SystemExit, "HTTPS"):
            speech_mcp.speech_mcp_url("http://example.test/speech/mcp?api-version=2025-11-15-preview")
        with self.assertRaisesRegex(SystemExit, "api-version"):
            speech_mcp.speech_mcp_url("https://example.test/speech/mcp")
        self.assertEqual(
            speech_mcp.speech_mcp_url("https://example.test/speech/mcp?api-version=2025-11-15-preview"),
            "https://example.test/speech/mcp?api-version=2025-11-15-preview",
        )

    def test_translator_run_uses_existing_keyless_client(self) -> None:
        result = [{"translations": [{"to": "fr", "text": "Bonjour"}]}]
        with patch.object(translator, "translate", return_value=result) as send, redirect_stdout(io.StringIO()):
            translator.main(["--run", "--text", "Hello", "--targets", "fr"])
        send.assert_called_once_with("Hello", targets=["fr"], source_language="en")
        with self.assertRaisesRegex(SystemExit, "--source"):
            translator.main(["--run", "--source", "not a language"])
        with self.assertRaisesRegex(SystemExit, "--source"):
            translator.main(["--run", "--source", "en,fr"])

    def test_batch_submission_uses_document_operation_location(self) -> None:
        response = MagicMock()
        response.headers = {
            "operation-location": "https://translator.example.test/translator/document/batches/job-1?api-version=2026-03-01"
        }
        with patch.object(batch.httpx, "post", return_value=response) as post:
            operation_url = batch.submit(
                "https://translator.example.test",
                "runtime-key",
                "https://storage.blob.core.windows.net/source?sp=rl&sig=source",
                "https://storage.blob.core.windows.net/target?sp=wl&sig=target",
                "fr",
            )
        self.assertEqual(operation_url, response.headers["operation-location"])
        self.assertEqual(post.call_args.kwargs["params"], {"api-version": "2026-03-01"})
        self.assertEqual(post.call_args.kwargs["json"]["inputs"][0]["targets"][0]["language"], "fr")
        with self.assertRaisesRegex(SystemExit, "list"):
            batch._blob_sas(
                "https://storage.blob.core.windows.net/source?sp=r&sig=source",
                "source",
            )
        with self.assertRaisesRegex(SystemExit, "this Translator endpoint"):
            batch.operation(
                "https://translator.example.test",
                "runtime-key",
                "https://elsewhere.example.test/translator/document/batches/job-1",
                False,
            )

    def test_voice_live_builds_supported_pcm_session(self) -> None:
        audio, rate = voice_live.pcm_wav(SAMPLE_DATA / "audio" / "northwind_support_message.wav")
        self.assertTrue(audio)
        self.assertEqual(rate, 16000)
        session = voice_live.session_update(rate)["session"]
        self.assertEqual(session["input_audio_format"], "pcm16")
        self.assertEqual(session["input_audio_sampling_rate"], 16000)
        self.assertIn("api-version=2026-04-10", voice_live.voice_live_url(
            "wss://resource.services.ai.azure.com/voice-live/realtime", "gpt-realtime"
        ))

    def test_governance_preflight_only_reads_configuration(self) -> None:
        configured = SimpleNamespace(
            app_insights_connection_string="",
            speech_endpoint="https://speech.example.test",
            voice_live_endpoint="",
            speech_mcp_url="https://mcp.example.test",
        )
        with patch.object(governance, "settings", return_value=configured):
            self.assertEqual(
                governance.preflight(),
                {
                    "application_insights_configured": False,
                    "speech_endpoint_configured": True,
                    "voice_live_endpoint_configured": False,
                    "speech_mcp_endpoint_configured": True,
                },
            )
