#!/usr/bin/env python3
"""Installs the guide on this machine.

  python scripts/install.py            copy agents/ to ~/.claude/agents and skills/ to ~/.claude/skills
                                       (a differing file is backed up first), with templates/project-CLAUDE.md
                                       copied into the starter-kit skill
  python scripts/install.py --global   also put global/CLAUDE.md into ~/.claude/CLAUDE.md, between markers
  python scripts/install.py --check    change nothing; exit 1 if the installed copy differs from this repo

It never edits settings.json: it only reports the main session model and its effort there.
It never deletes: a file in an installed skill's folder that the guide does not have is reported and left alone.
It refuses (exit 2, nothing written) when ~/.claude/CLAUDE.md is not UTF-8 or its markers are not exactly one
begin followed by one end: replacing text between broken markers could delete the owner's own instructions.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home() / ".claude"
BEGIN, END = "<!-- claudecode-guide:begin -->", "<!-- claudecode-guide:end -->"
check_only = "--check" in sys.argv
with_global = "--global" in sys.argv
differs = []


def backup(path):
    """Copies path to a backup name that does not exist yet; never overwrites an earlier backup."""
    stem = f"{path.name}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    target, n = path.with_name(stem), 1
    while target.exists():
        target, n = path.with_name(f"{stem}-{n}"), n + 1
    shutil.copy2(path, target)
    return target


def refuse(msg):
    print(f"refused    {msg}")
    sys.exit(2)


def install_file(src, dst):
    """Copies src to dst unless they are equal; a differing dst is backed up first. --check only reports."""
    if dst.exists() and dst.read_bytes() == src.read_bytes():
        print(f"unchanged  {dst}")
        return
    differs.append(str(dst))
    if check_only:
        print(f"differs    {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    note = f" (backup: {backup(dst).name})" if dst.exists() else ""
    shutil.copyfile(src, dst)
    print(f"installed  {dst}{note}")


# Agents
for src in sorted((ROOT / "agents").glob("*.md")):
    install_file(src, HOME / "agents" / src.name)

# Skills: every file of each skills/<name>/, plus the project template inside the starter kit
TEMPLATE_IN_KIT = Path("starter-kit") / "project-CLAUDE.md"
skill_dirs = (ROOT / "skills").iterdir() if (ROOT / "skills").is_dir() else []
for skill in sorted(p for p in skill_dirs if p.is_dir()):
    wanted = {src.relative_to(skill) for src in skill.rglob("*") if src.is_file()}
    for rel in sorted(wanted):
        install_file(skill / rel, HOME / "skills" / skill.name / rel)
    if skill.name == TEMPLATE_IN_KIT.parts[0]:
        wanted.add(Path(TEMPLATE_IN_KIT.name))
        install_file(ROOT / "templates" / "project-CLAUDE.md", HOME / "skills" / TEMPLATE_IN_KIT)
    installed_dir = HOME / "skills" / skill.name
    if installed_dir.is_dir():
        for extra in sorted(installed_dir.rglob("*")):
            if extra.is_file() and extra.relative_to(installed_dir) not in wanted and ".bak-" not in extra.name:
                print(f"extra      {extra} (not in the guide; left alone)")

# Global instructions, between markers, keeping everything else in the file byte for byte
claude_md = HOME / "CLAUDE.md"
raw = claude_md.read_bytes() if claude_md.exists() else b""
try:
    current = raw.decode("utf-8")
except UnicodeDecodeError:
    current = None
if current is None:
    if with_global or check_only:
        refuse(f"{claude_md} is not UTF-8; convert it first")
    print(f"skipped    {claude_md} (not UTF-8; the global block was not checked)")
else:
    nl = "\r\n" if "\r\n" in current else "\n"
    guide = (ROOT / "global" / "CLAUDE.md").read_text(encoding="utf-8").rstrip()
    block = nl.join([BEGIN, *guide.splitlines(), END])
    b, e = current.count(BEGIN), current.count(END)
    if b == 0 and e == 0:
        installed = False
        updated = (current.rstrip("\r\n") + nl + nl if current.strip() else "") + block + nl
    elif b == 1 and e == 1 and current.index(BEGIN) < current.index(END):
        installed = True
        before, _, rest = current.partition(BEGIN)
        _, _, after = rest.partition(END)
        updated = before + block + after
    else:
        installed = None
        updated = current
    if installed is None:
        msg = f"{claude_md} has {b} begin and {e} end markers, or end before begin; fix them by hand"
        if with_global or check_only:
            refuse(msg)
        print(f"skipped    {msg}")
    elif updated == current:
        print(f"unchanged  {claude_md} (global block)")
    elif not installed and not with_global:
        print(f"not set    {claude_md} (global block not installed; optional, run with --global)")
    elif check_only:
        differs.append(f"{claude_md} (global block)")
        print(f"differs    {claude_md} (global block)")
    elif not with_global:
        print(f"skipped    {claude_md} (global block differs; run with --global to update it)")
    else:
        HOME.mkdir(parents=True, exist_ok=True)
        note = f" (backup: {backup(claude_md).name})" if claude_md.exists() else ""
        claude_md.write_bytes(updated.encode("utf-8"))
        print(f"installed  {claude_md} (global block){note}")

# Settings: report only
settings = HOME / "settings.json"
if settings.exists():
    try:
        data = json.loads(settings.read_text(encoding="utf-8-sig"))
        model = data.get("model") if isinstance(data.get("model"), str) else None
        per_model = (data.get("modelSettings") or {}).get(model or "", {}) or {}
        effort = per_model.get("effortLevel") or data.get("effortLevel") or "(not set)"
        hint = "" if model and model.startswith("claude-") else "  <- not a pinned model ID (see global/CLAUDE.md)"
        print(f"settings   model={model or '(not set)'} effort={effort}{hint}")
    except (ValueError, UnicodeDecodeError, AttributeError) as error:
        print(f"settings   could not read {settings}: {error}")

if check_only and differs:
    sys.exit(1)
