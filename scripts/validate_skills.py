#!/usr/bin/env python3
"""Validate skills/*/SKILL.md frontmatter and scan the repository for leaked secrets."""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Slack token": re.compile(r"\bxox[abpors]-[A-Za-z0-9-]{10,}\b"),
}
TEXT_SUFFIXES = {".md", ".py", ".js", ".ts", ".sh", ".ps1", ".json", ".yml", ".yaml", ".txt", ""}


def validate_skill(skill_md: Path) -> list[str]:
    errors = []
    rel = skill_md.relative_to(ROOT)
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return [f"{rel}: missing YAML frontmatter delimited by '---'"]
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return [f"{rel}: invalid YAML frontmatter: {exc}"]

    name = meta.get("name")
    description = meta.get("description")
    folder = skill_md.parent.name
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{rel}: 'name' must be kebab-case, max 64 chars (got {name!r})")
    elif name != folder:
        errors.append(f"{rel}: 'name' ({name}) must match folder name ({folder})")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{rel}: 'description' is required")
    elif len(description) > 1024:
        errors.append(f"{rel}: 'description' has {len(description)} chars, max is 1024")
    if not text[match.end():].strip():
        errors.append(f"{rel}: body with instructions is empty")
    return errors


def scan_secrets() -> list[str]:
    errors = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(ROOT)}: possible {label} committed")
    return errors


def main() -> int:
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    errors = [] if skills else ["no skills found under skills/*/SKILL.md"]
    for skill_md in skills:
        errors.extend(validate_skill(skill_md))
    errors.extend(scan_secrets())

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: {len(skills)} skill(s) valid, no secrets found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
