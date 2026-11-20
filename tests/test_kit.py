"""Tests for orchestrator_kit.py (stdlib only)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import orchestrator_kit as kit  # noqa: E402


def run(*args, cwd=ROOT):
    return subprocess.run(
        [sys.executable, "orchestrator_kit.py", *args],
        cwd=cwd, capture_output=True, text=True,
    )


class TestValidate(unittest.TestCase):
    def test_bundled_tasks_validate(self):
        result = run("validate")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("3/3 tasks valid", result.stdout)

    def test_bad_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "bad.json").write_text(json.dumps(
                {"name": "Bad Name!", "model": "gemini-4-hydrogen"}), encoding="utf-8")
            result = run("validate", "--tasks-dir", str(d))
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL", result.stdout)

    def test_empty_dir_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("validate", "--tasks-dir", tmp)
            self.assertEqual(result.returncode, 1)

    def test_invalid_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "broken.json").write_text("{not json", encoding="utf-8")
            result = run("validate", "--tasks-dir", str(d))
            self.assertEqual(result.returncode, 1)
            self.assertIn("FAIL", result.stdout)
            self.assertIn("invalid JSON", result.stdout)

    def test_optional_field_must_be_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "bad.json").write_text(json.dumps(
                {"name": "ok-name", "model": "gemini-4-hydrogen",
                 "role": "R", "goal": "G", "steps": ["do it"],
                 "inputs": "not-a-list"}), encoding="utf-8")
            result = run("validate", "--tasks-dir", str(d))
            self.assertEqual(result.returncode, 1)
            self.assertIn("inputs must be a list", result.stdout)


class TestRender(unittest.TestCase):
    def test_render_contains_goal_and_steps(self):
        result = run("render", "research-brief")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Model: gemini-4-hydrogen", result.stdout)
        self.assertIn("Goal:", result.stdout)
        self.assertIn("Steps:", result.stdout)

    def test_render_unknown_fails(self):
        result = run("render", "no-such-task")
        self.assertEqual(result.returncode, 1)

    def test_render_invalid_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "bad.json").write_text(json.dumps(
                {"name": "bad-task", "model": "gemini-4-hydrogen",
                 "role": "R", "steps": ["do it"]}), encoding="utf-8")
            result = run("render", "bad-task", "--tasks-dir", str(d))
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid", result.stderr.lower())

    def test_list_shows_three_tasks(self):
        result = run("list")
        self.assertEqual(result.returncode, 0)
        for name in ("research-brief", "build-feature", "code-review"):
            self.assertIn(name, result.stdout)


if __name__ == "__main__":
    unittest.main()
