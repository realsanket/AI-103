import contextlib
import asyncio
import importlib.util
import io
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from _shared import config, language_client, speech_config


def _lesson(name: str):
    spec = importlib.util.spec_from_file_location(name, Path("04-text-and-speech") / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


batch = _lesson("13_stt_batch")
voice_live = _lesson("18_voice_live_prompt_agent")
health = _lesson("10_health_text_analytics")
ssml = _lesson("15_tts_ssml_hd")


class DomainFourRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        config.settings.cache_clear()

    def tearDown(self) -> None:
        config.settings.cache_clear()

    @patch("_shared.language_client.TextAnalyticsClient")
    @patch("_shared.language_client.DefaultAzureCredential")
    def test_language_client_uses_language_endpoint_and_entra_credential(
        self, credential, client
    ) -> None:
        with patch.dict(
            os.environ, {"LANGUAGE_ENDPOINT": "https://language.example.test"}, clear=True
        ):
            language_client.language_client()

        client.assert_called_once_with(
            endpoint="https://language.example.test", credential=credential.return_value
        )

    def test_healthcare_analysis_reports_per_document_errors(self) -> None:
        error = SimpleNamespace(is_error=True, error=SimpleNamespace(code="InvalidDocument"))
        client = SimpleNamespace(
            begin_analyze_healthcare_entities=Mock(
                return_value=SimpleNamespace(result=lambda: [error])
            )
        )
        output = io.StringIO()
        with (
            patch.object(health, "language_client", return_value=client),
            contextlib.redirect_stdout(output),
        ):
            health.main()

        self.assertIn("Document 1 failed: InvalidDocument", output.getvalue())

    def test_regional_speech_hostname_rejects_invalid_region(self) -> None:
        with patch.dict(os.environ, {"SPEECH_REGION": "eastus/path"}, clear=True):
            with self.assertRaisesRegex(ValueError, "SPEECH_REGION"):
                batch._base_url()

    def test_audio_output_preparation_creates_parent_and_removes_stale_file(self) -> None:
        output = Path("04-text-and-speech/generated/runtime-test.wav")
        with (
            patch.object(Path, "mkdir") as mkdir,
            patch.object(Path, "unlink") as unlink,
        ):
            self.assertEqual(speech_config.prepare_audio_output(output), output)

        mkdir.assert_called_once_with(parents=True, exist_ok=True)
        unlink.assert_called_once_with(missing_ok=True)

    def test_ssml_uses_phoneme_and_keeps_hd_voice_to_supported_elements(self) -> None:
        hd = ssml.build_ssml("hd")
        self.assertIn('<phoneme alphabet="ipa"', hd)
        self.assertIn("en-US-Ava:DragonHDLatestNeural", hd)
        self.assertEqual(ssml.unsupported_hd_elements(hd), [])
        self.assertEqual(ssml.unsupported_hd_elements(ssml.build_ssml("neural")), ["express-as", "prosody"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            ssml.main(["--voice", "neural", "--print-ssml"])
        self.assertIn("en-US-JennyNeural", output.getvalue())

    def test_batch_polling_uses_retry_after_then_bounded_backoff(self) -> None:
        pending = SimpleNamespace(
            headers={"Retry-After": "120"},
            raise_for_status=lambda: None,
            json=lambda: {"status": "Running"},
        )
        complete = SimpleNamespace(
            headers={},
            raise_for_status=lambda: None,
            json=lambda: {"status": "Succeeded"},
        )
        with (
            patch.object(batch, "_headers", return_value={}),
            patch.object(batch.httpx, "get", side_effect=[pending, complete]),
            patch.object(batch.time, "sleep") as sleep,
        ):
            self.assertEqual(batch._wait("https://example.test/job"), {"status": "Succeeded"})

        sleep.assert_called_once_with(120)
        self.assertEqual(batch._poll_delay({}, 2), 240)

    def test_batch_reports_empty_transcription_results(self) -> None:
        files = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {
                "values": [
                    {
                        "name": "empty.json",
                        "kind": "Transcription",
                        "links": {"contentUrl": "https://example.test/result"},
                    }
                ]
            },
        )
        result = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"combinedRecognizedPhrases": []},
        )
        output = io.StringIO()
        with (
            patch.object(batch, "_headers", return_value={}),
            patch.object(batch.httpx, "get", side_effect=[files, result]),
            contextlib.redirect_stdout(output),
        ):
            batch._print_transcripts("https://example.test/files")

        self.assertIn("empty.json: (no recognized speech)", output.getvalue())

    def test_batch_deletes_service_results_after_success(self) -> None:
        with (
            patch.dict(os.environ, {"BATCH_STT_CONTAINER_SAS": "https://example.test/audio"}, clear=True),
            patch.object(batch, "_submit", return_value="https://example.test/job"),
            patch.object(batch, "_wait", return_value={"status": "Succeeded", "links": {"files": "files"}}),
            patch.object(batch, "_print_transcripts"),
            patch.object(batch, "_delete") as delete,
        ):
            batch.main()

        delete.assert_called_once_with("https://example.test/job")

    def test_voice_live_waits_for_agent_readiness(self) -> None:
        creating = SimpleNamespace(
            id="agent-id", name="agent", version="1", status="creating"
        )
        active = SimpleNamespace(id="agent-id", name="agent", version="1", status="active")
        agents = SimpleNamespace(
            create_version=Mock(return_value=creating),
            get_version=Mock(return_value=active),
        )
        project = SimpleNamespace(agents=agents)
        with (
            patch.object(voice_live, "active_agent_reference") as reference,
            patch.object(voice_live.time, "sleep") as sleep,
        ):
            self.assertIs(voice_live._ensure_agent(project), active)

        sleep.assert_called_once_with(2)
        agents.get_version.assert_called_once_with("agent", "1")
        reference.assert_called_once_with(active)

    def test_voice_live_deletes_its_agent_version_after_session(self) -> None:
        agent = SimpleNamespace(id="agent-id", name="agent", version="1")
        agents = SimpleNamespace(delete_version=Mock())
        project = SimpleNamespace(agents=agents)

        class Socket:
            async def send(self, _message) -> None:
                pass

            def __aiter__(self):
                return self

            async def __anext__(self):
                if getattr(self, "done", False):
                    raise StopAsyncIteration
                self.done = True
                return '{"type": "response.done"}'

        class Connection:
            async def __aenter__(self):
                return Socket()

            async def __aexit__(self, *_args) -> None:
                pass

        settings = SimpleNamespace(
            require=lambda name: {
                "PROJECT_ENDPOINT": "https://example.test/api/projects/project",
                "VOICE_LIVE_ENDPOINT": "wss://example.test/voice-live/realtime",
            }[name]
        )
        credential = Mock()
        credential.get_token.return_value = SimpleNamespace(token="token")
        with (
            patch.object(voice_live, "project_client", return_value=project),
            patch.object(voice_live, "_ensure_agent", return_value=agent),
            patch.object(voice_live, "settings", return_value=settings),
            patch.object(voice_live, "_read_pcm16_mono", return_value=b"audio"),
            patch.object(voice_live, "DefaultAzureCredential", return_value=credential),
            patch.object(voice_live.websockets, "connect", return_value=Connection()),
        ):
            asyncio.run(voice_live._run())

        agents.delete_version.assert_called_once_with("agent", "1")


if __name__ == "__main__":
    unittest.main()
