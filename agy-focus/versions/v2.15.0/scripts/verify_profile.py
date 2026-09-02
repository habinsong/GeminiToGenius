#!/usr/bin/env python3
"""Read-only integrity check for the active agy-focus Antigravity profile."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import sys
from pathlib import Path


USER_HOME = Path(os.environ.get("AGY_INSTALL_HOME", Path.home()))
HOME = USER_HOME / ".gemini"
CONFIG = HOME / "config"
PROFILE = CONFIG / "agy-focus"
CURRENT = PROFILE / "current"
LEGACY_WORKFLOW_LINKS = (
    HOME / "antigravity/global_workflows/agy-run.md",
    HOME / "antigravity-ide/global_workflows/agy-run.md",
)
MAX_ENTRYPOINT_CHARACTERS = 6_000
SKILL_FIELDS = {"name", "description", "license", "allowed-tools", "metadata"}
SKILL_NAME_RE = re.compile(r"^[a-z0-9-]+$")
LOCAL_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


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
        ast.parse((CURRENT / "scripts/assemble_gemini.py").read_text(encoding="utf-8"))
        for script_name in ("verify_ui_render.py", "verify_plan.py", "verify_multi_page.py"):
            script_text = (CURRENT / "scripts" / script_name).read_text(encoding="utf-8")
            ast.parse(script_text)
            if script_name == "verify_ui_render.py" and not re.search(r"\b768\b", script_text):
                failures.append("UI render verifier is missing the medium 768 CSS px viewport")
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
        if manifest.get("target") != "Gemini 3.8 Flash (High)":
            failures.append("MANIFEST target is not Gemini 3.8 Flash (High)")
        if manifest.get("model_id") != "gemini-3.8-flash":
            failures.append("MANIFEST model_id is not gemini-3.8-flash")
        if manifest.get("ui_render_check") != "scripts/verify_ui_render.py":
            failures.append("MANIFEST ui_render_check is missing")
        if manifest.get("plan_check") != "scripts/verify_plan.py":
            failures.append("MANIFEST plan_check is missing")
        if manifest.get("multi_page_check") != "scripts/verify_multi_page.py":
            failures.append("MANIFEST multi_page_check is missing")
        compatibility = set(manifest.get("compatibility", []))
        if not {
            "Antigravity global customization paths",
            "Antigravity IDE global customization paths",
        }.issubset(compatibility):
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
    if len(hooks) != 0:
        failures.append(f"expected 0 hooks, found {len(hooks)}")
    if len(skills) != 11:
        failures.append(f"expected 11 custom skills, found {len(skills)}")
    if workflows:
        failures.append(f"active profile must not contain workflows, found {len(workflows)}")
    for workflow_link in LEGACY_WORKFLOW_LINKS:
        if workflow_link.exists() or workflow_link.is_symlink():
            failures.append(f"prompt-only profile must not expose legacy workflow: {workflow_link}")
    for field, actual in (
        ("rules", len(rules)),
        ("hooks", len(hooks)),
        ("custom_skills", len(skills)),
        ("workflows", len(workflows)),
    ):
        if manifest.get(field) != actual:
            failures.append(f"MANIFEST {field} does not match profile")
    expected_skills = {
        "agy-one-tap",
        "architecture-boundaries",
        "focus-session",
        "gemini-38-flash-high",
        "gtg",
        "human-copy",
        "interface-implementation",
        "interface-planning",
        "official-research",
        "ui-evidence-review",
        "workspace-intake",
    }

    try:
        gemini_text = (HOME / "GEMINI.md").read_text(encoding="utf-8")
        if len(gemini_text) >= MAX_ENTRYPOINT_CHARACTERS:
            failures.append("GEMINI.md exceeds 6000 characters")
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
            unsupported = set(data) - SKILL_FIELDS
            if unsupported:
                failures.append(f"unsupported skill frontmatter fields: {skill}: {sorted(unsupported)}")
            name = data.get("name", "")
            description = data.get("description", "")
            if not name:
                failures.append(f"skill name missing: {skill}")
            if (
                not SKILL_NAME_RE.fullmatch(name)
                or name.startswith("-")
                or name.endswith("-")
                or "--" in name
                or len(name) > 64
            ):
                failures.append(f"invalid skill name: {skill}: {name}")
            if not description:
                failures.append(f"skill description missing: {skill}")
            if len(description) > 1024 or "<" in description or ">" in description:
                failures.append(f"invalid skill description: {skill}")
            if name != skill.parent.name:
                failures.append(f"skill name mismatch: {skill}")
            skill_text = skill.read_text(encoding="utf-8")
            if len(skill_text) >= 12000:
                failures.append(f"skill exceeds 12000 characters: {skill}")
            for relative_link in LOCAL_MARKDOWN_LINK_RE.findall(skill_text):
                target = (skill.parent / relative_link).resolve()
                if not target.is_file():
                    failures.append(f"broken local skill reference: {skill}: {relative_link}")
            skill_names.append(name)
        except (OSError, ValueError) as error:
            failures.append(str(error))

    if set(skill_names) != expected_skills:
        failures.append(f"skill names do not match the 11-skill contract: {skill_names}")

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
