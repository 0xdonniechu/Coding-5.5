#!/usr/bin/env python3
"""Checks the guide's files: agent frontmatter, pinned models, reviewer bodies, global and template sections, skills, settings defaults.

Run: python scripts/check.py   (exit 0 = PASS, 1 = FAIL). Standard library only.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINNED = re.compile(r"^claude-[a-z]+-\d+-\d+(-\d{8})?$")  # optional date suffix
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
TOOLS = {"Read", "Write", "Edit", "Glob", "Grep", "Bash", "PowerShell", "WebFetch", "WebSearch", "NotebookEdit"}
AGENTS = {"builder", "reviewer", "hard-reviewer", "transcriber"}
TEMPLATE_SECTIONS = ["## What it does", "## Verify", "## HARD", "## MEDIUM", "## EASY", "## Rules", "## Read when", "## Session state"]
SKILLS = {"starter-kit", "handoff", "market-research", "teardown", "sdlc", "orca-worktree-setup"}
DEFAULT_KEYS = {"enabledPlugins", "skillOverrides"}
OVERRIDES = {"on", "name-only", "user-invocable-only", "off"}
DESCRIPTION_LIMIT = 1024  # the Agent Skills spec maximum; Claude Code's own cut-off is higher

failures = []


def fail(msg):
    failures.append(msg)


def read(rel):
    path = ROOT / rel
    if not path.exists():
        fail(f"{rel}: missing")
        return ""
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def split_frontmatter(rel):
    """Returns (fields, body). A file whose frontmatter is not opened and closed by '---' lines fails."""
    text = read(rel)
    if not text.startswith("---\n"):
        fail(f"{rel}: no frontmatter")
        return {}, None
    head, fence, body = text[4:].partition("\n---\n")
    if not fence:
        fail(f"{rel}: frontmatter is not closed by a '---' line")
        return {}, None
    fields = {}
    for line in head.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip().strip("\"'")
    return fields, body


def model_label(model_id):
    """claude-sonnet-5-5 -> 'Sonnet 5.5', the way global/CLAUDE.md names it."""
    _, family, major, minor = model_id.split("-")[:4]
    return f"{family.capitalize()} {major}.{minor}"


agents = {}
for path in sorted((ROOT / "agents").glob("*.md")):
    rel = f"agents/{path.name}"
    fields, body = split_frontmatter(rel)
    name = path.stem
    agents[name] = (fields, body)
    if fields.get("name") != name:
        fail(f"{rel}: name '{fields.get('name')}' does not match the file name")
    if not fields.get("description"):
        fail(f"{rel}: no description")
    if not PINNED.match(fields.get("model", "")):
        fail(f"{rel}: model '{fields.get('model')}' is not a pinned full model ID (aliases upgrade silently)")
    if fields.get("effort") not in EFFORTS:
        fail(f"{rel}: effort '{fields.get('effort')}' is not one of {sorted(EFFORTS)}")
    if "tools" in fields:
        unknown = {t.strip() for t in fields["tools"].split(",")} - TOOLS
        if unknown:
            fail(f"{rel}: unknown tools {sorted(unknown)}")

if set(agents) != AGENTS:
    fail(f"agents/: expected {sorted(AGENTS)}, found {sorted(agents)}")

rev, hard = agents.get("reviewer", ({}, None)), agents.get("hard-reviewer", ({}, None))
if rev[1] is None or hard[1] is None or rev[1] != hard[1]:
    fail("agents/hard-reviewer.md body differs from agents/reviewer.md body (edit reviewer.md, then copy its body)")
for name, (fields, _) in agents.items():
    writers = {"Write", "Edit", "NotebookEdit"} & {t.strip() for t in fields.get("tools", "Write").split(",")}
    if "reviewer" in name and writers:
        fail(f"agents/{name}.md: a reviewer needs an explicit tools list without {sorted(writers)}")

global_md = read("global/CLAUDE.md")
for name in sorted(AGENTS & set(agents)):
    model = agents[name][0].get("model", "")
    if PINNED.match(model) and f"**{name}** ({model_label(model)})" not in global_md:
        fail(f"global/CLAUDE.md: does not list '**{name}** ({model_label(model)})', the model pinned in agents/{name}.md")
efforts = {n: agents[n][0].get("effort") for n in AGENTS & set(agents)}
if efforts.get("reviewer") == efforts.get("hard-reviewer"):
    line = f"builder, reviewers `{efforts.get('builder')}`, transcriber `{efforts.get('transcriber')}`"
    if efforts.get("builder") == efforts.get("reviewer"):
        if line not in global_md:
            fail(f"global/CLAUDE.md: the effort line does not read '{line}' (the agent files' efforts)")
    else:
        fail("agents/: builder and reviewers have different efforts; update global/CLAUDE.md's effort line and check.py together")
else:
    fail("agents/: reviewer and hard-reviewer have different efforts (they must review alike)")
if "Current choice" not in global_md:
    fail("global/CLAUDE.md: no 'Current choice' line for the main session model")

template = read("templates/project-CLAUDE.md")
for section in TEMPLATE_SECTIONS:
    if section not in template:
        fail(f"templates/project-CLAUDE.md: missing section '{section}'")
if "## HARD" in template and "hard-reviewer" not in template.split("## HARD", 1)[1].split("\n", 1)[0]:
    fail("templates/project-CLAUDE.md: the HARD heading does not name hard-reviewer")

defaults_text = read("global/settings-defaults.json")
try:
    defaults = json.loads(defaults_text) if defaults_text else {}
except ValueError as error:
    fail(f"global/settings-defaults.json: not valid JSON ({error})")
    defaults = {}
if not isinstance(defaults, dict) or set(defaults) - DEFAULT_KEYS:
    fail(f"global/settings-defaults.json: only {sorted(DEFAULT_KEYS)} may be set; the rest of settings.json is the owner's")
elif any(not isinstance(defaults.get(key, {}), dict) for key in DEFAULT_KEYS):
    fail(f"global/settings-defaults.json: {sorted(DEFAULT_KEYS)} must each be an object")
else:
    for name, value in (defaults.get("enabledPlugins") or {}).items():
        if not isinstance(value, bool):
            fail(f"global/settings-defaults.json: enabledPlugins.{name} must be true or false")
    for name, value in (defaults.get("skillOverrides") or {}).items():
        if value not in OVERRIDES:
            fail(f"global/settings-defaults.json: skillOverrides.{name} '{value}' is not one of {sorted(OVERRIDES)}")
    if "starter-kit" in (defaults.get("skillOverrides") or {}) or "handoff" in (defaults.get("skillOverrides") or {}):
        fail("global/settings-defaults.json: must not override the guide's own skills")

skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir()) if (ROOT / "skills").is_dir() else []
if set(skills) != SKILLS:
    fail(f"skills/: expected {sorted(SKILLS)}, found {skills}")
for name in skills:
    rel = f"skills/{name}/SKILL.md"
    fields, _ = split_frontmatter(rel)
    description = fields.get("description", "")
    if fields.get("name") != name:
        fail(f"{rel}: name '{fields.get('name')}' does not match the folder name")
    if not description:
        fail(f"{rel}: no description")
    if len(description) > DESCRIPTION_LIMIT:
        fail(f"{rel}: description is {len(description)} characters, over {DESCRIPTION_LIMIT}")
    if ": " in description:
        fail(f"{rel}: description contains ': ', which breaks YAML")
if "starter-kit" in skills:
    if split_frontmatter("skills/starter-kit/SKILL.md")[0].get("disable-model-invocation") != "true":
        fail("skills/starter-kit/SKILL.md: needs 'disable-model-invocation: true' (it must cost no context)")
    if (ROOT / "skills" / "starter-kit" / "project-CLAUDE.md").exists():
        fail("skills/starter-kit/project-CLAUDE.md: the template lives only in templates/; install.py copies it")

if failures:
    print("FAIL")
    for f in failures:
        print(f"- {f}")
    sys.exit(1)
print(f"PASS: {len(agents)} agents pinned, reviewer bodies equal, global matches the pinned models, template sections present, {len(skills)} skills valid, settings defaults valid")
