# Coding 5.5

How to run Claude Code: one model economy for every repo, the subagents it relies on, the template each repo's `CLAUDE.md` follows, and the skills that set up a repo and keep its sessions' context small. Public.

## What is in it

| Path | Installs to | Purpose |
|---|---|---|
| `global/CLAUDE.md` | `~/.claude/CLAUDE.md`, between markers | Who does what (main session and subagents), task rating, the review loop, how to switch models, honesty rules |
| `agents/builder.md` | `~/.claude/agents/` | Sonnet 5.5: implements an approved plan step; edits the working tree only |
| `agents/reviewer.md` | `~/.claude/agents/` | Opus 5.5: independent review of a MEDIUM change; never edits |
| `agents/hard-reviewer.md` | `~/.claude/agents/` | Fable 5.1: the same review for HARD changes, by a different model from the one that wrote them |
| `agents/transcriber.md` | `~/.claude/agents/` | Haiku 5.5: mechanical copying and conversion only |
| `templates/project-CLAUDE.md` | a repo's `CLAUDE.md`, and `~/.claude/skills/starter-kit/` | The sections the agents read: What it does, Verify, HARD / MEDIUM / EASY, Rules, Read when, Session state |
| `global/settings-defaults.json` | `~/.claude/settings.json`, with `--settings` | The `enabledPlugins` and `skillOverrides` every machine shares: rarely used plugins off, skills unrelated to coding off or invoked by hand only. Every other value in `settings.json` keeps its value; the file is re-written as 2-space JSON, backed up first |
| `skills/starter-kit/` | `~/.claude/skills/` | `/starter-kit`, run once per repo: CLAUDE.md from the template, git identity, only the plugins, MCP servers and skills the repo needs, HANDOFF.md gitignored, tracker project. Invoked by hand only, so it costs no context |
| `skills/handoff/` | `~/.claude/skills/` | `/handoff`: `save` writes where the work stands to HANDOFF.md before `/clear`; `resume` reads only that file in the new session |
| `skills/market-research/` | `~/.claude/skills/` | `/market-research`: competitors, US/USD prices, 1-2 star reviews, TAM/SAM/SOM, company profiles, Value x Features chart (`assets/positioning_chart.py`) |
| `skills/teardown/` | `~/.claude/skills/` | `/teardown`: clean-room two-team product teardown, the wall test run as a loop until nothing blocks |
| `skills/sdlc/` | `~/.claude/skills/` | `/sdlc`: intent -> plan -> build -> verify -> ship, with ticket/PR/review conventions |
| `skills/orca-worktree-setup/` | `~/.claude/skills/` | `/orca-worktree-setup`: Orca Setup Script so a new worktree gets its gitignored local files |

Every model is pinned to a full model ID, never an alias, so an upgrade is always a decision (`global/CLAUDE.md`, "Switching models"). The main session's model and effort live in `~/.claude/settings.json` (`"model": "claude-opus-5-5"`, and `high` effort under `modelSettings`). The installer only reports them; the owner sets them.

The agents are universal: each reads the project's own `CLAUDE.md` at run time, so one set serves every repo.

## Install on a machine

```
python scripts/check.py              # the guide is consistent
python scripts/install.py            # agents and skills into ~/.claude (a differing file is backed up first)
python scripts/install.py --global   # also the global block in ~/.claude/CLAUDE.md
python scripts/install.py --settings # also merge global/settings-defaults.json into ~/.claude/settings.json (backed up first)
python scripts/install.py --check    # change nothing; exit 1 if this machine differs, 2 if ~/.claude/CLAUDE.md cannot be checked safely
```

Agents and skills load when a session starts: after installing, start a new session and check with `/agents` and `/skills`. The installer never deletes: a file in an installed skill's folder that the guide does not have is reported as `extra` and left alone.

### New machine (Windows, macOS or Linux)

1. Clone this repo, then `python scripts/install.py --global --settings` and `python scripts/install.py --check` (exit 0).
2. In `~/.claude/settings.json`, set `"model"` to the pinned ID in `global/CLAUDE.md` and its `modelSettings` effort; the installer reports both.
3. MCP servers stay per machine: user scope holds only what most repos use (the issue tracker). Others go in `~/.claude/mcp-catalog.json` and are added per repo with `claude mcp add-json --scope local`. Write each entry for that OS: on Windows an `npx` server runs through `cmd.exe /d /c npx ...`, on Linux and macOS as `npx ...` directly.
4. A new session: `/context` and `/skills` should match the other machines.

## Keeping context small

Plans, decisions and dead ends go in files, not in the chat; the chat holds only the current state. `/handoff` writes that state before `/clear`, and the template's "Session state" section makes every new session read it first. `/starter-kit` keeps the part sent on every turn short: a lean `CLAUDE.md` (module detail in `docs/`, listed under "Read when", never `@import`ed), and only the plugins, MCP servers and skills the repo uses. `skills/starter-kit/context-config.md` says what each turn carries and how to turn things off globally and on per repo.

## Sources

`market-research`, `teardown` and `sdlc` started from `bto-researchmarket`, `bto-teardown` and `bto-sdlc` in [sonpiaz/bto-skills](https://github.com/sonpiaz/bto-skills) (MIT, (c) 2026 Son Piaz; licence in `skills/LICENSE-bto-skills`), then changed from real use (history in `skills/CHANGELOG-claude-skills.md`).
