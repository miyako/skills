#!/usr/bin/env python3
"""Cross-file integrity checks for the 4D skillset (complements validate_skills.py).

validate_skills.py checks that each file is well formed and that links and
paths resolve. This script checks that the files agree with each other:

  * section references -- `skills/x/SKILL.md` "Heading", `skill` "Heading",
    see "Heading" in `file`, and see/under "Heading" -- name a heading (or a
    bold run-in label) that exists, and Markdown #anchors resolve;
  * no heading appears twice at the same place in a file (same parent path);
  * every skill folder is listed in README.md and AGENTS.md, and neither
    lists a skill that does not exist;
  * the root .gitignore carries every /tools/<skill>/ entry of the canonical
    .gitignore in 4dproject, and never ignores the whole tools/ folder;
  * keys in ```json form-object examples under skills/4dform exist in
    schemas/4dform/formsSchema.json;
  * no project-specific names or phrasing (DENYLIST below) leak into skills:
    a skill states the general rule, the repository it came from keeps its
    own notes.

Usage: python3 .github/scripts/check_skill_integrity.py [repo-root]
"""
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKILLSET = ROOT / "4d-skills"
SKILLS = SKILLSET / "skills"
SCHEMA = SKILLSET / "schemas/4dform/formsSchema.json"

# Names of individual demo/host repositories and phrasing that ties a rule to
# one project. Matched case-insensitively against prose (not code blocks).
# Add an entry when a review generalises a new project-specific note.
DENYLIST = [
    r"\bHDI_Embeddings\b",
    r"\bDisplayScale\b",
    r"\bformobj\b",
    r"\bldap-demo\b",
    r"\bthis user's\b",
    r"\bin this (?:workspace|session)\b",
    r"\bfor this form\b",
]

FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# `target` "Heading"  /  `target` section "Heading"
TARGET_REF_RE = re.compile(r"`([^`\s]+)`[*]*\s+(?:section\s+)?\"([^\"]{3,100})\"")
# see "Heading" in `target`
IN_REF_RE = re.compile(r"\b(?:[Ss]ee|under)\s+\"([A-Z`][^\"]{2,100})\"\s+(?:section\s+)?in\s+`([^`\s]+)`")
# see "Heading" / under "Heading" (current file or skill)
SEE_REF_RE = re.compile(r"\b(?:[Ss]ee|under)\s+\"([A-Z`][^\"]{2,100})\"")

errors = []


def err(path, line, msg):
    rel = path.relative_to(ROOT)
    errors.append(f"{rel}:{line}: {msg}" if line else f"{rel}: {msg}")


def norm(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[`*_]", "", text)
    text = text.replace("…", "").replace("...", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def slug(text):
    """GitHub-style heading anchor."""
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def prose_lines(text):
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield n, line


_headings = {}


def headings(path):
    if path not in _headings:
        hs = []
        for n, line in prose_lines(path.read_text(encoding="utf-8")):
            m = HEADING_RE.match(line)
            if m:
                hs.append((n, len(m.group(1)), m.group(2)))
        _headings[path] = hs
    return _headings[path]


LABEL_RE = re.compile(r"^\s*(?:[-*]\s+)?\*\*([^*]{3,100}?)[.:]?\*\*")


def heading_set(paths):
    """Headings plus bold run-in labels ("**Matching quirk.** ...")."""
    out = set()
    for p in paths:
        for _, _, h in headings(p):
            out.add(norm(h))
        for _, line in prose_lines(p.read_text(encoding="utf-8")):
            m = LABEL_RE.match(line)
            if m:
                out.add(norm(m.group(1)).rstrip(".:"))
    return out


def anchors(path):
    seen, out = {}, set()
    for _, _, h in headings(path):
        s = slug(h)
        k = seen.get(s, 0)
        out.add(s if k == 0 else f"{s}-{k}")
        seen[s] = k + 1
    return out


def has_heading(name, paths):
    want = norm(name)
    hs = heading_set(paths)
    # Allow a reference to quote the start of a long heading ("Smoke-testing…").
    return any(h == want or h.startswith(want) for h in hs)


def skill_of(path):
    try:
        return path.relative_to(SKILLS).parts[0]
    except ValueError:
        return None


def skill_files(skill):
    return sorted((SKILLS / skill).rglob("*.md"))


def resolve_target(src, target, skill_names):
    """Map a backticked reference to the Markdown files it may point into."""
    target = target.rstrip(".,:;)")
    if target in skill_names:
        return skill_files(target)
    if not target.endswith(".md"):
        return None
    cands = [SKILLSET / target]
    sk = skill_of(src)
    if sk:
        cands.append(SKILLS / sk / target)
    cands.append(src.parent / target)
    for c in cands:
        if c.is_file():
            return [c]
    return None


def check_sections(path, text, skill_names):
    sk = skill_of(path)
    local = skill_files(sk) if sk else [path]
    lines = list(prose_lines(text))
    for i, (n, line) in enumerate(lines):
        if HEADING_RE.match(line):
            continue
        # A reference may wrap onto the next line; only report matches that
        # start on this one.
        nxt = lines[i + 1][1] if i + 1 < len(lines) and lines[i + 1][0] == n + 1 else ""
        window = line + " " + nxt
        limit = len(line)
        spans = []
        for rx, ti, hi in ((TARGET_REF_RE, 1, 2), (IN_REF_RE, 2, 1)):
            for m in rx.finditer(window):
                if m.start() >= limit:
                    continue
                files = resolve_target(path, m.group(ti), skill_names)
                if files is None:
                    continue
                spans.append(m.span(hi))
                if not has_heading(m.group(hi), files):
                    err(path, n, f'section "{m.group(hi)}" not found in `{m.group(ti)}`')
        for m in SEE_REF_RE.finditer(window):
            if m.start() >= limit or any(a <= m.start(1) < b for a, b in spans):
                continue
            if not has_heading(m.group(1), local):
                err(path, n, f'section "{m.group(1)}" not found in this skill')
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or "#" not in target:
                continue
            file_part, anchor = target.split("#", 1)
            dest = (path.parent / file_part) if file_part else path
            if dest.suffix != ".md" or not dest.is_file():
                continue
            if anchor.lower() not in anchors(dest):
                err(path, n, f"broken anchor: {target}")


def check_duplicate_headings(path):
    stack, seen = [], {}
    for n, level, h in headings(path):
        stack = [s for s in stack if s[0] < level]
        key = tuple(norm(x[1]) for x in stack) + (level, norm(h))
        if key in seen:
            err(path, n, f'duplicate heading "{h}" (first at line {seen[key]})')
        else:
            seen[key] = n
        stack.append((level, h))


def check_denylist(path, text):
    pats = [re.compile(p, re.I) for p in DENYLIST]
    for n, line in prose_lines(text):
        for p in pats:
            m = p.search(line)
            if m:
                err(path, n, f"project-specific wording {m.group(0)!r}: "
                             "state the general rule instead")


def check_skill_tables(skill_names):
    for f in (ROOT / "README.md", SKILLSET / "AGENTS.md"):
        text = f.read_text(encoding="utf-8")
        listed = set(re.findall(r"skills/([a-z0-9-]+)/SKILL\.md", text))
        for s in sorted(skill_names - listed):
            err(f, 0, f"skill `{s}` is not listed")
        for s in sorted(listed - skill_names):
            err(f, 0, f"lists unknown skill `{s}`")


def check_gitignore():
    proj = SKILLS / "4dproject/SKILL.md"
    m = re.search(r"```gitignore\n(.*?)```", proj.read_text(encoding="utf-8"), re.S)
    if not m:
        err(proj, 0, "canonical ```gitignore block not found")
        return
    canon = {l.strip() for l in m.group(1).splitlines() if l.strip().startswith("/tools/")}
    gi = ROOT / ".gitignore"
    have = {l.strip() for l in gi.read_text(encoding="utf-8").splitlines()}
    for e in sorted(canon - have):
        err(gi, 0, f"missing canonical entry {e}")
    for bad in ("tools/", "/tools/", "tools", "/tools"):
        if bad in have:
            err(gi, 0, f"ignores the whole tools/ folder ({bad}); list /tools/<skill>/ entries")


def schema_keys():
    data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    keys, types = set(), set()

    def walk(node):
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict):
                keys.update(props)
                t = props.get("type")
                if isinstance(t, dict) and isinstance(t.get("enum"), list):
                    types.update(x for x in t["enum"] if isinstance(x, str))
                if isinstance(t, dict) and isinstance(t.get("const"), str):
                    types.add(t["const"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    return keys, types


def check_form_examples(keys, types):
    for f in sorted((SKILLS / "4dform").rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"^```json\s*\n(.*?)^```", text, re.S | re.M):
            try:
                doc = json.loads(m.group(1))
            except ValueError:
                continue  # abbreviated example ("...") -- not checkable
            line = text.count("\n", 0, m.start()) + 1

            def walk(node):
                if isinstance(node, dict):
                    if node.get("type") in types:
                        for k in node:
                            if k not in keys:
                                err(f, line, f"key {k!r} on a {node['type']!r} object "
                                             "is not in formsSchema.json")
                    for v in node.values():
                        walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)

            walk(doc)


def main():
    if not SKILLS.is_dir():
        sys.exit(f"{SKILLS} not found")
    skill_names = {p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file()}
    files = [ROOT / "README.md", SKILLSET / "AGENTS.md"] + sorted(SKILLS.rglob("*.md"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        check_sections(f, text, skill_names)
        check_duplicate_headings(f)
        check_denylist(f, text)
    check_skill_tables(skill_names)
    check_gitignore()
    check_form_examples(*schema_keys())
    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} integrity error(s)")
        sys.exit(1)
    print(f"OK: integrity of {len(skill_names)} skills, {len(files)} Markdown files")


main()
