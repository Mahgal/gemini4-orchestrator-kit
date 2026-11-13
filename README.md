# gemini4-orchestrator-kit

Ready-to-use task templates for **Gemini 4 Hydrogen** in Google Antigravity's
**Orchestrator** (multi-agent) mode — plus a tiny validator so a bad template
never reaches the model.

## The problem

Orchestrator tasks are just structured prompts, but a missing field, a vague
step, or a typo'd model name wastes a whole multi-agent run. This kit gives
you three copy-paste task recipes with a strict schema and a CLI that checks
them before you paste.

## What's inside

- `tasks/research-brief.json` — sourced one-page research brief
- `tasks/build-feature.json` — implement one small feature, tests first
- `tasks/code-review.json` — severity-ordered PR review
- `orchestrator_kit.py` — `validate` / `list` / `render` (stdlib only)

## Quick start

```bash
python orchestrator_kit.py validate
# OK   research-brief (research-brief.json)
# OK   build-feature (build-feature.json)
# OK   code-review (code-review.json)
# 3/3 tasks valid

python orchestrator_kit.py render research-brief
# Model: gemini-4-hydrogen
# Role: Research agent
# Goal: Produce a sourced, one-page research brief ...
```

## Example output

```
$ python orchestrator_kit.py list
research-brief               gemini-4-hydrogen    Research agent
build-feature                gemini-4-hydrogen    Implementation agent
code-review                  gemini-4-hydrogen    Review agent
```

## Write your own task

Copy any file in `tasks/`, keep the `name` a lowercase slug, and keep
`goal` to one sentence. Run `validate` — a task with a missing `goal` or an
empty `steps` list fails loudly instead of silently under-performing.

## Notes

- Model name follows the Gemini 4 Hydrogen announcement (Nov 2026).
- Templates are prompts, not API calls — no key, no cost, no network.
