import importlib.util
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from _shared import config, cu_client, openai_client, translator_client

_video_spec = importlib.util.spec_from_file_location(
    "video_generation", Path("03-computer-vision/05_video_generation.py")
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
            "https://example.services.ai.azure.com/contentunderstanding/analyzers/invoice:analyze?api-version=2025-11-15-preview",
            headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
            json={"inputs": [{"url": "https://example.test/file.pdf"}]},
            timeout=60.0,
        )

    @patch("_shared.cu_client.httpx.post")
    @patch("_shared.cu_client.DefaultAzureCredential")
    def test_cu_analyze_accepts_multiple_input_urls(self, credential, post) -> None:
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

    @patch("_shared.translator_client.httpx.post")
    @patch("_shared.translator_client.DefaultAzureCredential")
    def test_translator_uses_direct_v3_contract(self, credential, post) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: [{"translations": [{"to": "fr", "text": "Bonjour"}]}],
        )
        credential.return_value.get_token.return_value.token = "token"

        self.assertEqual(
            translator_client.translate("Hello", ["fr", "ja"]),
            [{"translations": [{"to": "fr", "text": "Bonjour"}]}],
        )

        post.assert_called_once_with(
            "https://api.cognitive.microsofttranslator.com/translate",
            params=[("api-version", "3.0"), ("from", "en"), ("to", "fr"), ("to", "ja")],
            headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
            json=[{"Text": "Hello"}],
            timeout=30.0,
        )

    @patch.object(video_generation.Path, "write_bytes")
    @patch.object(video_generation.httpx, "get")
    @patch.object(video_generation.httpx, "post")
    @patch.object(video_generation, "_token", return_value="token")
    def test_sora_uses_direct_video_job_contract(
        self, _token, post, get, write_bytes
    ) -> None:
        post.return_value = SimpleNamespace(
            raise_for_status=lambda: None, json=lambda: {"id": "job-1"}
        )
        get.side_effect = [
            SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"status": "succeeded", "generations": [{"id": "gen-1"}]},
            ),
            SimpleNamespace(raise_for_status=lambda: None, content=b"video"),
        ]
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com"},
            clear=True,
        ):
            video_generation.main()

        self.assertEqual(
            post.call_args.args[0],
            "https://example.openai.azure.com/openai/v1/video/generations/jobs?api-version=preview",
        )
        body = post.call_args.kwargs["json"]
        self.assertTrue(body["prompt"])
        self.assertEqual(
            {name: value for name, value in body.items() if name != "prompt"},
            {
                "model": "sora",
                "width": 1280,
                "height": 720,
                "n_seconds": 5,
            },
        )
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer token")
        self.assertEqual(
            get.call_args_list[1].args[0],
            "https://example.openai.azure.com/openai/v1/video/generations/gen-1/content/video?api-version=preview",
        )
        write_bytes.assert_called_once_with(b"video")


if __name__ == "__main__":
    unittest.main()
