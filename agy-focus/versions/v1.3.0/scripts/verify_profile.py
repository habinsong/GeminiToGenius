#!/usr/bin/env python3
"""Read-only integrity check for the active agy-focus Antigravity profile."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


HOME = Path.home() / ".gemini"
CONFIG = HOME / "config"
PROFILE = CONFIG / "agy-focus"
CURRENT = PROFILE / "current"
GLOBAL_WORKFLOWS = HOME / "antigravity-ide/global_workflows"


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path}")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError(f"unterminated frontmatter: {path}")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    failures: list[str] = []

    try:
        manifest = json.loads((CURRENT / "MANIFEST.json").read_text(encoding="utf-8"))
        hooks = json.loads((CURRENT / "hooks/hooks.json").read_text(encoding="utf-8"))
        ast.parse((CURRENT / "hooks/hook_runner.py").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, SyntaxError) as error:
        failures.append(f"profile parse: {error}")
        manifest = {}
        hooks = {}

    try:
        active_version = (CURRENT / "VERSION").read_text(encoding="utf-8").strip()
        if active_version != manifest.get("version"):
            failures.append("VERSION does not match MANIFEST")
        if not CURRENT.is_symlink():
            failures.append("current profile is not a symlink")
        if manifest.get("target") != "Gemini 3.6 Flash (High)":
            failures.append("MANIFEST target is not Gemini 3.6 Flash (High)")
        compatibility = set(manifest.get("compatibility", []))
        if not {"Antigravity 2.4.x", "Antigravity IDE 2.1.x"}.issubset(compatibility):
            failures.append("MANIFEST compatibility is missing Antigravity targets")
        if (HOME / "GEMINI.md").resolve() != (CURRENT / "GEMINI.md").resolve():
            failures.append("GEMINI.md symlink mismatch")
        if (CONFIG / "hooks.json").resolve() != (CURRENT / "hooks/hooks.json").resolve():
            failures.append("hooks.json symlink mismatch")
        if (CONFIG / "skills").resolve() != (CURRENT / "skills").resolve():
            failures.append("skills symlink mismatch")
    except OSError as error:
        failures.append(f"profile paths: {error}")

    rules = sorted((CURRENT / "rules").glob("*.md"))
    skills = sorted((CURRENT / "skills").glob("*/SKILL.md"))
    workflows = sorted((CURRENT / "workflows").glob("*.md"))
    if len(rules) != 12:
        failures.append(f"expected 12 rules, found {len(rules)}")
    if len(hooks) != 8:
        failures.append(f"expected 8 hooks, found {len(hooks)}")
    if len(skills) != 3:
        failures.append(f"expected 3 custom skills, found {len(skills)}")
    if len(workflows) != 1:
        failures.append(f"expected 1 workflow, found {len(workflows)}")
    for field, actual in (("rules", len(rules)), ("hooks", len(hooks)), ("custom_skills", len(skills)), ("workflows", len(workflows))):
        if manifest.get(field) != actual:
            failures.append(f"MANIFEST {field} does not match profile")
    expected_hooks = {
        "focus-anchor",
        "mcp-purpose-gate",
        "destructive-command-gate",
        "external-input-gate",
        "tool-audit",
        "failure-anchor",
        "invocation-state",
        "stop-snapshot",
    }
    if set(hooks) != expected_hooks:
        failures.append("hook names do not match the 8-hook contract")
    workflow = CURRENT / "workflows/agy-run.md"
    global_workflow = GLOBAL_WORKFLOWS / "agy-run.md"
    try:
        if not global_workflow.is_symlink():
            failures.append("global workflow is not a symlink")
        if global_workflow.resolve() != workflow.resolve():
            failures.append("global workflow symlink mismatch")
        data = frontmatter(workflow)
        if not data.get("description"):
            failures.append(f"workflow description missing: {workflow}")
        if len(workflow.read_text(encoding="utf-8")) >= 12000:
            failures.append("agy-run workflow exceeds 12000 characters")
    except (OSError, ValueError) as error:
        failures.append(f"workflow check: {error}")
    try:
        if len((HOME / "GEMINI.md").read_text(encoding="utf-8")) >= 12000:
            failures.append("GEMINI.md exceeds 12000 characters")
    except OSError as error:
        failures.append(f"GEMINI.md read: {error}")

    skill_names: list[str] = []
    for skill in skills:
        try:
            data = frontmatter(skill)
            if not data.get("description"):
                failures.append(f"skill description missing: {skill}")
            if data.get("name", skill.parent.name) != skill.parent.name:
                failures.append(f"skill name mismatch: {skill}")
            if len(skill.read_text(encoding="utf-8")) >= 12000:
                failures.append(f"skill exceeds 12000 characters: {skill}")
            skill_names.append(data.get("name", skill.parent.name))
        except (OSError, ValueError) as error:
            failures.append(str(error))

    result = {
        "ok": not failures,
        "version": manifest.get("version", ""),
        "activeTarget": str(CURRENT),
        "rules": len(rules),
        "hooks": len(hooks),
        "skills": skill_names,
        "workflows": [workflow.stem for workflow in workflows],
        "target": manifest.get("target", ""),
        "geminiCharacters": len((HOME / "GEMINI.md").read_text(encoding="utf-8")) if (HOME / "GEMINI.md").exists() else None,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
