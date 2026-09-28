import importlib.util
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from _shared import config, cu_client, openai_client, translator_client

_video_spec = importlib.util.spec_from_file_location(
    "video_generation", Path("03-computer-vision/07_video_generation.py")
)
assert _video_spec and _video_spec.loader
video_generation = importlib.util.module_from_spec(_video_spec)
_video_spec.loader.exec_module(video_generation)


class SharedRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        config.settings.cache_clear()

    def tearDown(self) -> None:
        config.settings.cache_clear()

    def test_settings_only_validates_requested_endpoint(self) -> None:
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com"},
            clear=True,
        ):
            current = config.settings()
            self.assertEqual(
                current.require("AZURE_OPENAI_ENDPOINT"),
                "https://example.openai.azure.com",
            )
            with self.assertRaisesRegex(RuntimeError, "PROJECT_ENDPOINT"):
                current.require("PROJECT_ENDPOINT")

    def test_template_placeholders_are_treated_as_unset(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://<resource>.openai.azure.com",
                "AZURE_SUBSCRIPTION_ID": "<your-subscription-id>",
                "DEFAULT_MODEL": "   ",
                "SEARCH_INDEX": "<index>",
            },
            clear=True,
        ):
            current = config.settings()
            self.assertEqual(current.azure_openai_endpoint, "")
            self.assertEqual(current.azure_subscription_id, "")
            self.assertEqual(current.default_model, "gpt-4.1-mini")
            self.assertEqual(current.search_index, "northwind-docs")
            self.assertEqual(config.env("AZURE_OPENAI_ENDPOINT", "fallback"), "fallback")
            with self.assertRaisesRegex(RuntimeError, "AZURE_OPENAI_ENDPOINT"):
                current.require("AZURE_OPENAI_ENDPOINT")

    def test_load_env_drops_placeholders_but_keeps_shell_values(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as folder:
            env_file = Path(folder) / ".env"
            env_file.write_text(
                "PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>\n"
                "SEARCH_ENDPOINT=https://search.example.test\n"
                "AZURE_RESOURCE_GROUP=<your-resource-group>\n"
                "REALTIME_MODEL=\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {"AZURE_RESOURCE_GROUP": "rg-shell"}, clear=True):
                config.load_env(env_file)
                self.assertNotIn("PROJECT_ENDPOINT", os.environ)
                self.assertEqual(os.environ.get("REALTIME_MODEL", "gpt-realtime"), "gpt-realtime")
                self.assertEqual(os.environ["SEARCH_ENDPOINT"], "https://search.example.test")
                self.assertEqual(os.environ["AZURE_RESOURCE_GROUP"], "rg-shell")

    @patch("_shared.openai_client.get_bearer_token_provider")
    @patch("_shared.openai_client.DefaultAzureCredential")
    @patch("_shared.openai_client.OpenAI")
    def test_openai_client_uses_direct_v1_entra_scope(
        self, client, credential, token_provider
    ) -> None:
        provider = object()
        token_provider.return_value = provider
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com"},
            clear=True,
        ):
            openai_client.openai_client()

        token_provider.assert_called_once_with(
            credential.return_value, "https://ai.azure.com/.default"
        )
        client.assert_called_once_with(
            base_url="https://example.openai.azure.com/openai/v1", api_key=provider
        )

    @patch("_shared.cu_client.httpx.post")
    @patch("_shared.cu_client.DefaultAzureCredential")
    def test_cu_analyze_sends_bearer_token_and_inputs_body(self, credential, post) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None, headers={}, json=lambda: {"accepted": True}
        )
        credential.return_value.get_token.return_value.token = "token"
        with patch.dict(
            os.environ,
            {"CU_ENDPOINT": "https://example.services.ai.azure.com"},
            clear=True,
        ):
            self.assertEqual(
                cu_client.analyze("invoice", "https://example.test/file.pdf"),
                {"accepted": True},
            )

        post.assert_called_once_with(
            "https://example.services.ai.azure.com/contentunderstanding/analyzers/invoice:analyze?api-version=2025-11-01",
            headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
            json={"inputs": [{"url": "https://example.test/file.pdf"}]},
            timeout=60.0,
        )

    @patch("_shared.cu_client.httpx.post")
    @patch("_shared.cu_client.DefaultAzureCredential")
    def test_cu_analyze_sends_each_pro_mode_input(self, credential, post) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None, headers={}, json=lambda: {"accepted": True}
        )
        credential.return_value.get_token.return_value.token = "token"
        with patch.dict(
            os.environ,
            {"CU_ENDPOINT": "https://example.services.ai.azure.com"},
            clear=True,
        ):
            cu_client.analyze(
                "mortgage-package-review",
                ["https://example.test/application.pdf", "https://example.test/paystub.pdf"],
            )

        self.assertEqual(
            post.call_args.kwargs["json"],
            {
                "inputs": [
                    {"url": "https://example.test/application.pdf"},
                    {"url": "https://example.test/paystub.pdf"},
                ]
            },
        )

    @patch("_shared.cu_client.httpx.get")
    @patch("_shared.cu_client.httpx.post")
    @patch("_shared.cu_client.DefaultAzureCredential")
    def test_cu_polling_honors_retry_after_without_cloud(
        self, credential, post, get
    ) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None,
            headers={
                "Operation-Location": (
                    "https://example.services.ai.azure.com/contentunderstanding/analyzerResults/id"
                )
            },
        )
        get.side_effect = [
            SimpleNamespace(
                raise_for_status=lambda: None,
                headers={"Retry-After": "3"},
                json=lambda: {"status": "running"},
            ),
            SimpleNamespace(
                raise_for_status=lambda: None,
                headers={},
                json=lambda: {"status": "succeeded", "result": {}},
            ),
        ]
        credential.return_value.get_token.return_value.token = "token"
        with (
            patch.dict(
                os.environ,
                {"CU_ENDPOINT": "https://example.services.ai.azure.com"},
                clear=True,
            ),
            patch.object(cu_client.time, "sleep") as sleep,
        ):
            self.assertEqual(
                cu_client.analyze("invoice", "https://example.test/invoice.pdf")["status"],
                "succeeded",
            )

        sleep.assert_called_once_with(3.0)

    def test_cu_validates_https_and_complete_blob_sas_urls(self) -> None:
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            cu_client.validate_source_url("http://example.test/file.pdf")
        with self.assertRaisesRegex(ValueError, "sv, se, sp, and sig"):
            cu_client.validate_source_url(
                "https://account.blob.core.windows.net/container/file.png?sig=token"
            )

    @patch("_shared.translator_client.httpx.post")
    @patch("_shared.translator_client.DefaultAzureCredential")
    def test_translator_uses_direct_v3_contract(self, credential, post) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: [{"translations": [{"to": "fr", "text": "Bonjour"}]}],
        )
        credential.return_value.get_token.return_value.token = "token"
        with patch.dict(
            os.environ,
            {
                "TRANSLATOR_RESOURCE_ID": (
                    "/subscriptions/sub/resourceGroups/rg/providers/"
                    "Microsoft.CognitiveServices/accounts/translator"
                )
            },
            clear=True,
        ):
            self.assertEqual(
                translator_client.translate("Hello", ["fr", "ja"]),
                [{"translations": [{"to": "fr", "text": "Bonjour"}]}],
            )

        post.assert_called_once_with(
            "https://api.cognitive.microsofttranslator.com/translate",
            params=[("api-version", "3.0"), ("from", "en"), ("to", "fr"), ("to", "ja")],
            headers={
                "Authorization": "Bearer token",
                "Ocp-Apim-ResourceId": (
                    "/subscriptions/sub/resourceGroups/rg/providers/"
                    "Microsoft.CognitiveServices/accounts/translator"
                ),
                "Content-Type": "application/json",
            },
            json=[{"Text": "Hello"}],
            timeout=30.0,
        )

    def test_sora_uses_v1_videos_create_retrieve_download(self) -> None:
        import tempfile

        queued = SimpleNamespace(id="video_1", status="queued", progress=0)
        done = SimpleNamespace(id="video_1", status="completed", progress=100)
        content = SimpleNamespace(write_to_file=lambda path: Path(path).write_bytes(b"mp4"))
        client = SimpleNamespace(
            videos=SimpleNamespace(
                create=lambda **kwargs: calls.append(("create", kwargs)) or queued,
                retrieve=lambda video_id: calls.append(("retrieve", video_id)) or done,
                download_content=lambda video_id, variant: calls.append(("download", video_id, variant)) or content,
                delete=lambda video_id: calls.append(("delete", video_id)),
            )
        )
        calls: list = []
        with tempfile.TemporaryDirectory() as folder, patch.object(
            video_generation, "OUTPUT", Path(folder) / "video.mp4"
        ), patch.object(video_generation.time, "sleep"):
            video_generation.generate(client, model="sora-2", size="1280x720", seconds="4", delete_remote=True)
            self.assertEqual((Path(folder) / "video.mp4").read_bytes(), b"mp4")
        create = calls[0][1]
        self.assertEqual({key: create[key] for key in ("model", "size", "seconds")}, {"model": "sora-2", "size": "1280x720", "seconds": "4"})
        self.assertEqual(calls[1:], [("retrieve", "video_1"), ("download", "video_1", "video"), ("delete", "video_1")])
        with self.assertRaisesRegex(ValueError, "seconds"):
            video_generation.generate(client, model="sora-2", size="1280x720", seconds="5")

    def test_sora_polling_reports_failure_and_timeout(self) -> None:
        failed = SimpleNamespace(id="video_2", status="failed", error=SimpleNamespace(message="blocked"), progress=0)
        with self.assertRaisesRegex(RuntimeError, "blocked"):
            video_generation.wait_for_video(SimpleNamespace(), failed)
        stuck = SimpleNamespace(id="video_3", status="in_progress", progress=5)
        client = SimpleNamespace(videos=SimpleNamespace(retrieve=lambda video_id: stuck))
        ticks = iter([0.0, 5.0, 11.0])
        with self.assertRaises(TimeoutError):
            video_generation.wait_for_video(
                client, stuck, timeout=10, interval=5, sleep=lambda _seconds: None, clock=lambda: next(ticks)
            )


if __name__ == "__main__":
    unittest.main()
