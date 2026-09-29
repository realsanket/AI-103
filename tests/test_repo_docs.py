"""No-cloud checks that the repository's indexes match the lesson folders.

docs/learning-path.md orders every numbered lesson for learning, and the root
README and AGENTS.md count lessons per domain. Both drift when a lesson is
added or retitled, so compare them with the files on disk.
"""
from collections import Counter
import importlib.util
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LESSONS = sorted(ROOT.glob("0[1-9]-*/[0-9]*_*.py"))
LEARNING_PATH = ROOT / "docs" / "learning-path.md"


def _generator():
    spec = importlib.util.spec_from_file_location("learning_path", ROOT / "scripts" / "learning_path.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


learning_path = _generator()


class LearningPathTests(unittest.TestCase):
    def test_committed_path_matches_the_generator(self) -> None:
        self.assertEqual(
            LEARNING_PATH.read_text(encoding="utf-8"),
            learning_path.render(),
            "docs/learning-path.md is out of date. Run: uv run python scripts/learning_path.py",
        )

    def test_every_numbered_lesson_appears_exactly_once(self) -> None:
        text = LEARNING_PATH.read_text(encoding="utf-8")
        linked = Counter(re.findall(r"\]\(\.\./(0[1-9]-[^/)]+/[0-9][^/)]*\.py)\)", text))
        self.assertEqual(linked, Counter(path.relative_to(ROOT).as_posix() for path in LESSONS))
        steps = [int(step) for step in re.findall(r"^\| (\d+) \| D\d ", text, flags=re.MULTILINE)]
        self.assertEqual(steps, list(range(1, len(LESSONS) + 1)))

    def test_links_reach_files_and_headings(self) -> None:
        text = LEARNING_PATH.read_text(encoding="utf-8")
        anchors: dict[Path, set[str]] = {}
        for target, anchor in re.findall(r"\]\(([^)#\s]*)(?:#([^)\s]+))?\)", text):
            path = (LEARNING_PATH.parent / target).resolve() if target else LEARNING_PATH
            self.assertTrue(path.is_file(), f"broken link: {target}")
            if anchor:
                if path not in anchors:
                    headings = learning_path.heading_anchors(path.read_text(encoding="utf-8"))
                    anchors[path] = {slug for _, slug in headings}
                self.assertIn(anchor, anchors[path], f"no heading for {target}#{anchor}")

    def test_github_anchor_rules(self) -> None:
        headings = learning_path.heading_anchors(
            "# Part 1 — Foundations\n```\n# not a heading\n```\n"
            "### 05 — Split + Embedding Skillset\n### 10 — CU `prebuilt-layout` (Structure-Preserving)\n"
            "### 06 — HA/DR guidance markers\n### Notes\n### Notes\n"
        )
        self.assertEqual(
            [slug for _, slug in headings],
            ["part-1--foundations", "05--split--embedding-skillset",
             "10--cu-prebuilt-layout-structure-preserving", "06--hadr-guidance-markers", "notes", "notes-1"],
        )


class LessonCountTests(unittest.TestCase):
    def test_readme_and_agents_counts_match_the_folders(self) -> None:
        per_domain = dict(Counter(path.parent.name for path in LESSONS))
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for text in (readme, agents):
            self.assertIn(f"**{len(LESSONS)} numbered Python lessons**", text)
        readme_counts = re.findall(
            r"^\| \[\d{2} [^\]]+\]\((0[1-9]-[^/]+)/README\.md\) \| [^|]+ \| (\d+) \|", readme, flags=re.MULTILINE
        )
        self.assertEqual({folder: int(count) for folder, count in readme_counts}, per_domain)
        agents_counts = re.findall(
            r"^\| \d{2} [^|]+ \| (\d+) \| `(0[1-9]-[^/]+)/README\.md` \|", agents, flags=re.MULTILINE
        )
        self.assertEqual({folder: int(count) for count, folder in agents_counts}, per_domain)


if __name__ == "__main__":
    unittest.main()
