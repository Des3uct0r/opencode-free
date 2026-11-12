#!/usr/bin/env python3
"""Validate the opencode-free skill against the Agent Skills specification.

Dependency-free (standard library only) so it runs in CI without setup.
Checks: frontmatter presence, name rules, description length, compatibility
length, body size, and that every relative markdown link resolves.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "opencode-free"
SKILL_MD = SKILL_DIR / "SKILL.md"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        fail("SKILL.md must start with YAML frontmatter (---)")
        return {}, text
    parts = re.split(r"\r?\n---\r?\n", text, maxsplit=1)
    if len(parts) != 2:
        fail("frontmatter is not terminated with a closing ---")
        return {}, text
    raw, body = parts
    fields: dict[str, str] = {}
    for line in raw.splitlines()[1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue  # nested map (metadata) — not required for validation
        if ":" not in line:
            fail(f"malformed frontmatter line: {line!r}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, body


def main() -> int:
    if not SKILL_MD.is_file():
        print(f"FAIL: missing {SKILL_MD}")
        return 1

    text = SKILL_MD.read_text(encoding="utf-8")
    fields, body = parse_frontmatter(text)

    # Stronger check when PyYAML is available (CI installs it).
    try:
        import yaml  # type: ignore
        fm = text[4:text.index("\n---\n", 3)]
        yaml.safe_load(fm)
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001
        fail(f"frontmatter is not valid YAML: {exc}")

    name = fields.get("name", "")
    description = fields.get("description", "")
    compatibility = fields.get("compatibility", "")

    if not name:
        fail("missing required field: name")
    else:
        if len(name) > 64:
            fail(f"name is {len(name)} chars (max 64)")
        if not NAME_RE.match(name):
            fail(f"name {name!r} must be lowercase letters, digits, single hyphens")
        if not name.isascii():
            fail("name must be ASCII")
        if name != SKILL_DIR.name:
            fail(f"name {name!r} must match folder {SKILL_DIR.name!r}")

    if not description:
        fail("missing required field: description")
    else:
        if len(description) > 1024:
            fail(f"description is {len(description)} chars (max 1024)")
        if "<" in description or ">" in description:
            warn("description contains angle brackets (XML tags are not allowed)")
        lowered = description.lower()
        if "use when" not in lowered and "use this" not in lowered:
            warn("description should say when to use the skill")

    if compatibility and len(compatibility) > 500:
        fail(f"compatibility is {len(compatibility)} chars (max 500)")

    body_lines = body.strip().splitlines()
    if len(body_lines) < 5:
        fail("SKILL.md body is too short to be useful")
    if len(body_lines) > 500:
        warn(f"SKILL.md body has {len(body_lines)} lines (>500 recommended)")

    for md in SKILL_DIR.rglob("*.md"):
        for match in LINK_RE.finditer(md.read_text(encoding="utf-8")):
            target = match.group(1).split("#")[0].strip()
            if not target:
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                fail(f"{md.relative_to(ROOT)}: broken link -> {target}")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        for w in warnings:
            print(f"  ! {w}")
        return 1

    print(f"OK  {name}: description {len(description)} chars, body {len(body_lines)} lines")
    for w in warnings:
        print(f"  ! {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
