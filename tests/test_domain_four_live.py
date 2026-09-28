"""No-cloud tests for the GPT-Live session, delegation, and WebRTC lessons."""
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import unittest
from unittest.mock import patch


def _lesson(file_name: str):
    spec = importlib.util.spec_from_file_location(file_name.removesuffix(".py"), Path("04-text-and-speech") / file_name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


session = _lesson("28_gpt_live_session.py")
delegation = _lesson("29_gpt_live_delegation.py")
webrtc = _lesson("30_gpt_live_webrtc_preflight.py")
ENDPOINT = "https://northwind.openai.azure.com/"


class GptLiveTests(unittest.TestCase):
    def test_websocket_and_webrtc_urls_use_the_right_scheme(self) -> None:
        for module in (session, delegation):
            self.assertEqual(module._live_url(ENDPOINT), "wss://northwind.openai.azure.com/openai/v1/live/sessions")
        self.assertEqual(webrtc._sessions_url(ENDPOINT), "https://northwind.openai.azure.com/openai/v1/live/sessions")

    def test_session_and_delegation_shapes(self) -> None:
        config = session._session_config("gpt-live-1")
        self.assertEqual(config["model"], "gpt-live-1")
        self.assertIsNone(config["delegation"])
        self.assertEqual(delegation._client_delegation(), {"type": "client"})
        responses = delegation._responses_delegation("reasoner")["responses"]
        self.assertEqual(responses["model"], "reasoner")
        function = next(tool for tool in responses["tools"] if tool["type"] == "function")
        self.assertFalse(function["parameters"]["additionalProperties"])
        body = webrtc._creation_body_shape("gpt-live-1")
        self.assertEqual(body["transport"]["type"], "webrtc")
        self.assertEqual(body["session"]["delegation"], {"type": "client"})

    def test_preflights_make_no_cloud_calls(self) -> None:
        with patch.dict("os.environ", {"AZURE_OPENAI_ENDPOINT": ENDPOINT}):
            for module in (session, delegation, webrtc):
                output = io.StringIO()
                with redirect_stdout(output):
                    module.main([])
                self.assertIn("no cloud calls", output.getvalue())


if __name__ == "__main__":
    unittest.main()
