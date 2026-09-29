"""No-cloud guard: every Responses and Chat Completions call uses parameters the SDK accepts.

The two APIs name the same ideas differently (for example structured output is
`text={"format": ...}` on Responses and `response_format=...` on Chat
Completions). A wrong keyword fails only at run time, after a learner has set
up Azure, so check it here against the installed `openai` SDK.
"""
import ast
import importlib.util
import inspect
from pathlib import Path
import unittest

from openai.resources.chat.completions import Completions
from openai.resources.responses import Responses

ROOT = Path(__file__).resolve().parents[1]
LESSON_DIRS = sorted(ROOT.glob("0[1-9]-*"))
RESPONSES_PARAMS = set(inspect.signature(Responses.create).parameters) | set(
    inspect.signature(Responses.parse).parameters
)
CHAT_PARAMS = set(inspect.signature(Completions.create).parameters) | set(
    inspect.signature(Completions.parse).parameters
)


def _calls():
    for folder in LESSON_DIRS:
        for path in sorted(folder.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("create", "parse", "stream"):
                        yield path, node, ast.unparse(node.func)


class OpenAIRequestShapeTests(unittest.TestCase):
    def test_literal_keywords_match_the_sdk(self) -> None:
        problems = []
        for path, node, chain in _calls():
            keywords = {keyword.arg for keyword in node.keywords if keyword.arg}
            if "responses." in chain or chain.startswith("responses"):
                unknown = keywords - RESPONSES_PARAMS
            elif "chat.completions" in chain:
                unknown = keywords - CHAT_PARAMS
            else:
                continue
            if unknown:
                problems.append(f"{path.relative_to(ROOT)}:{node.lineno} {chain} {sorted(unknown)}")
        self.assertEqual(problems, [])

    def test_json_mode_lesson_builds_a_responses_request(self) -> None:
        path = ROOT / "02-generative-ai-and-agents" / "32_openai_json_mode.py"
        spec = importlib.util.spec_from_file_location("json_mode", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        request = module.request_kwargs("gpt-4.1-mini")
        self.assertLessEqual(set(request), RESPONSES_PARAMS)
        self.assertNotIn("response_format", request)
        text_format = request["text"]["format"]
        self.assertEqual((text_format["type"], text_format["strict"]), ("json_schema", True))
        self.assertFalse(text_format["schema"]["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
