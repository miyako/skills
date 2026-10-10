#!/usr/bin/env python3
"""Validate the 4D skillset under 4d-skills/.

Checks:
  * every skills/<name>/SKILL.md has YAML front matter with `name` (equal to
    the folder name, lowercase letters/digits/hyphens) and a non-empty
    `description`;
  * front matter of reference files (if any) is valid YAML;
  * relative Markdown links in AGENTS.md, README.md and skill files resolve;
  * backtick paths `skills/...` and `schemas/...` resolve against the
    skillset root;
  * MIGRATION.json is valid and points to existing skills.

Usage: python3 .github/scripts/validate_skills.py [repo-root]
Requires PyYAML.
"""
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKILLSET = ROOT / "4d-skills"
SKILLS = SKILLSET / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
TICK_RE = re.compile(r"`((?:skills|schemas)/[^`\s]+)`")
FENCE_RE = re.compile(r"^(```|~~~)")

errors = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def front_matter(path, text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        err(path, "unterminated front matter")
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as e:
        err(path, f"invalid YAML front matter: {e}")
        return None
    if not isinstance(data, dict):
        err(path, "front matter is not a mapping")
        return None
    return data


def prose(text):
    """Yield lines outside fenced code blocks."""
    fenced = False
    for line in text.splitlines():
        if FENCE_RE.match(line.lstrip()):
            fenced = not fenced
            continue
        if not fenced:
            yield line


def check_links(path, text):
    for line in prose(text):
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            if not (path.parent / target).exists():
                err(path, f"broken link: {target}")
        if path.is_relative_to(SKILLSET):
            for target in TICK_RE.findall(line):
                if any(c in target for c in "<>{}*?$|"):
                    continue
                target = target.rstrip(".,:;)")
                if not (SKILLSET / target).exists():
                    err(path, f"missing path: `{target}`")


def main():
    if not SKILLS.is_dir():
        sys.exit(f"{SKILLS} not found")
    names = set()
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        skill = d / "SKILL.md"
        if not skill.is_file():
            err(d, "missing SKILL.md")
            continue
        fm = front_matter(skill, skill.read_text(encoding="utf-8"))
        if fm is None:
            err(skill, "missing front matter")
            continue
        name = fm.get("name")
        if name != d.name:
            err(skill, f"name {name!r} does not match folder {d.name!r}")
        if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
            err(skill, f"invalid name {name!r}")
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            err(skill, "missing description")
        elif len(desc) > 1024:
            err(skill, f"description is {len(desc)} characters (max 1024)")
        names.add(d.name)

    files = [ROOT / "README.md", SKILLSET / "AGENTS.md"] + sorted(SKILLS.rglob("*.md"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        if f.name != "SKILL.md":
            front_matter(f, text)
        check_links(f, text)

    mig = SKILLSET / "MIGRATION.json"
    base = "https://github.com/miyako/skills/tree/main/4d-skills/skills/"
    try:
        data = json.loads(mig.read_text(encoding="utf-8"))
        for old, entry in data["instructions"].items():
            status = entry.get("status")
            if status not in ("skill", "instruction", "deleted"):
                err(mig, f"{old}: bad status {status!r}")
            skill = entry.get("skill")
            if skill is not None and skill not in names:
                err(mig, f"{old}: unknown skill {skill!r}")
            url = entry.get("url")
            if status == "skill":
                if url != base + str(skill):
                    err(mig, f"{old}: url should be {base}{skill}")
            elif url is not None:
                err(mig, f"{old}: url must be null for status {status}")
            if status == "instruction" and not entry.get("path"):
                err(mig, f"{old}: missing path")
        for old, entry in data["skills"].items():
            skill = entry.get("skill")
            if skill not in names:
                err(mig, f"skills.{old}: unknown skill {skill!r}")
            if entry.get("url") != base + str(skill):
                err(mig, f"skills.{old}: url should be {base}{skill}")
    except (OSError, ValueError, KeyError, AttributeError) as e:
        err(mig, f"invalid: {e!r}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"OK: {len(names)} skills, {len(files)} Markdown files checked")


main()
