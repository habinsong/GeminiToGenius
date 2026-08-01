#!/usr/bin/env python3
"""Read-only integrity check for the active agy-focus Antigravity profile."""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path


HOME = Path.home() / ".gemini"
CONFIG = HOME / "config"
PROFILE = CONFIG / "agy-focus"
CURRENT = PROFILE / "current"
LEGACY_WORKFLOW_LINKS = (
    HOME / "antigravity/global_workflows/agy-run.md",
    HOME / "antigravity-ide/global_workflows/agy-run.md",
)
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
        ast.parse((CURRENT / "scripts/assemble_gemini.py").read_text(encoding="utf-8"))
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
    if workflows:
        failures.append(f"active profile must not contain workflows, found {len(workflows)}")
    for workflow_link in LEGACY_WORKFLOW_LINKS:
        if workflow_link.exists() or workflow_link.is_symlink():
            failures.append(f"prompt-only profile must not expose legacy workflow: {workflow_link}")
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
    try:
        gemini_text = (HOME / "GEMINI.md").read_text(encoding="utf-8")
        if len(gemini_text) >= 12000:
            failures.append("GEMINI.md exceeds 12000 characters")
        assembler_path = CURRENT / "scripts/assemble_gemini.py"
        spec = importlib.util.spec_from_file_location("agy_focus_assembler", assembler_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {assembler_path}")
        assembler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(assembler)
        expected = assembler.render_profile(CURRENT)
        if (CURRENT / "GEMINI.md").read_text(encoding="utf-8") != expected:
            failures.append("GEMINI.md is out of sync with versioned rules")
    except OSError as error:
        failures.append(f"GEMINI.md read: {error}")
    except (ImportError, AttributeError, ValueError) as error:
        failures.append(f"GEMINI.md generation check: {error}")

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
        "generatedEntrypoint": not any("out of sync" in failure for failure in failures),
        "target": manifest.get("target", ""),
        "geminiCharacters": len((HOME / "GEMINI.md").read_text(encoding="utf-8")) if (HOME / "GEMINI.md").exists() else None,
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
