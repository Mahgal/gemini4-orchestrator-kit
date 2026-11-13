#!/usr/bin/env python3
"""gemini4-orchestrator-kit — task templates + validator for Gemini 4 Hydrogen
in Google Antigravity's Orchestrator (multi-agent) mode.

The task files in ``tasks/`` are plain JSON so they work without any
dependency. Use this CLI to validate them before pasting into Antigravity,
list what you have, and render a ready-to-paste orchestrator prompt.

Usage:
    python orchestrator_kit.py validate [--tasks-dir tasks]
    python orchestrator_kit.py list [--tasks-dir tasks]
    python orchestrator_kit.py render <task-name> [--tasks-dir tasks]

Task schema:
    {
      "name": "research-brief",          # slug, required
      "model": "gemini-4-hydrogen",      # required
      "role": "Research agent",          # required
      "goal": "One sentence.",           # required
      "steps": ["...", "..."],           # >= 1, required
      "inputs": ["..."],                 # optional
      "outputs": ["..."],                # optional
      "guardrails": ["..."]              # optional
    }
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = ("name", "model", "role", "goal", "steps")
OPTIONAL = ("inputs", "outputs", "guardrails")
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def load_tasks(tasks_dir: Path) -> list[dict]:
    tasks = []
    for path in sorted(tasks_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            tasks.append({"_file": path.name, "_error": f"invalid JSON: {exc}"})
            continue
        data["_file"] = path.name
        tasks.append(data)
    return tasks


def validate_task(task: dict) -> list[str]:
    errors = []
    if "_error" in task:
        return [task["_error"]]
    for field in REQUIRED:
        if field not in task or task[field] in (None, "", []):
            errors.append(f"missing or empty required field: {field}")
    if "name" in task and not SLUG.match(str(task["name"])):
        errors.append(f"name {task['name']!r} is not a lowercase slug")
    if "steps" in task:
        if not isinstance(task["steps"], list) or not task["steps"]:
            errors.append("steps must be a non-empty list")
        elif any(not isinstance(s, str) or not s.strip() for s in task["steps"]):
            errors.append("every step must be a non-empty string")
    for field in OPTIONAL:
        if field in task and not isinstance(task[field], list):
            errors.append(f"{field} must be a list of strings")
    return errors


def cmd_validate(tasks_dir: Path) -> int:
    tasks = load_tasks(tasks_dir)
    if not tasks:
        print(f"No task files found in {tasks_dir}", file=sys.stderr)
        return 1
    failed = 0
    for task in tasks:
        errors = validate_task(task)
        label = task.get("name", task["_file"])
        if errors:
            failed += 1
            print(f"FAIL {label} ({task['_file']}):")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"OK   {label} ({task['_file']})")
    print(f"{len(tasks) - failed}/{len(tasks)} tasks valid")
    return 1 if failed else 0


def cmd_list(tasks_dir: Path) -> int:
    tasks = load_tasks(tasks_dir)
    if not tasks:
        print(f"No task files found in {tasks_dir}", file=sys.stderr)
        return 1
    for task in tasks:
        if "_error" in task:
            print(f"{task['_file']:28s} INVALID: {task['_error']}")
            continue
        print(f"{task.get('name', '?'):28s} {task.get('model', '?'):20s} {task.get('role', '')}")
    return 0


def render_prompt(task: dict) -> str:
    lines = [
        f"Model: {task['model']}",
        f"Role: {task['role']}",
        "",
        f"Goal: {task['goal']}",
        "",
        "Steps:",
    ]
    lines += [f"  {i}. {step}" for i, step in enumerate(task["steps"], 1)]
    for field, title in (("inputs", "Inputs"), ("outputs", "Expected outputs"),
                         ("guardrails", "Guardrails")):
        if task.get(field):
            lines += ["", f"{title}:"]
            lines += [f"  - {item}" for item in task[field]]
    return "\n".join(lines) + "\n"


def cmd_render(tasks_dir: Path, name: str) -> int:
    for task in load_tasks(tasks_dir):
        if task.get("name") == name:
            errors = validate_task(task)
            if errors:
                print(f"Task {name!r} is invalid:", file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)
                return 1
            print(render_prompt(task), end="")
            return 0
    print(f"No task named {name!r} in {tasks_dir}", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("validate", "list"):
        p = sub.add_parser(cmd)
        p.add_argument("--tasks-dir", type=Path, default=Path("tasks"))
    p = sub.add_parser("render")
    p.add_argument("name")
    p.add_argument("--tasks-dir", type=Path, default=Path("tasks"))
    args = parser.parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args.tasks_dir)
    if args.command == "list":
        return cmd_list(args.tasks_dir)
    return cmd_render(args.tasks_dir, args.name)


if __name__ == "__main__":
    raise SystemExit(main())
