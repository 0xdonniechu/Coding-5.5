# Coding 5.5: how every repo runs Claude Code (GitHub 0xdonniechu/Coding-5.5)

## What it is
The global instructions, four subagents, the project `CLAUDE.md` template and two skills (`starter-kit`, `handoff`) that every repo works with, plus a check script and an installer. Private. Standard library Python only. Owner decisions are in `intent/2026-10-16-claudecode-guide.md`.
Cost of a bug: every session on every machine follows these files. A wrong rule rates HARD work as EASY, lets an unreviewed change through, or swaps a model without a decision. The bar: `check.py` green, the installed copy equal to the repo, and the owner's approval for any change of model, rating or review rule.

## Verify
- `python scripts/check.py`: agent frontmatter, models pinned to full IDs, `hard-reviewer` body equal to `reviewer` body, the global agent list, the template's sections, skill frontmatter (name, description length, no `: `, `starter-kit` invoked by hand only, the template kept only in `templates/`), `global/settings-defaults.json` (only `enabledPlugins` and `skillOverrides`, valid values, not the guide's own skills).
- `python scripts/install.py --check`: this machine's `~/.claude/agents`, `~/.claude/skills` (and the global block and settings defaults, if installed) equal the repo (a file only in an installed skill folder is reported as `extra`, not counted); exit 0 equal, 1 differs, 2 refused (`~/.claude/CLAUDE.md` is not UTF-8 or its markers are broken, or with `--settings` `settings.json` is not a JSON object: fix by hand). Run after every merge, on every machine.
- A change to an agent's behaviour: start a new session, `/agents`, run the agent once on a known diff, and record what it returned in the PR.
- A change to a skill's steps: run it once in a fresh agent on a scratch repo, given only the skill, and record in the PR where it had to guess.

## HARD: the main session does it directly, then hard-reviewer
- The model choice and switching: the "Current choice" line, any agent's `model:` or `effort:`, the switch test.
- Task rating (EASY / MEDIUM / HARD), the review loop, who may commit or merge, the honesty rules.
- The reviewers' checklist and their PASS/FAIL rule.
- The installer's writes to `~/.claude` (backups, the marker block, skill folders, and with `--settings` the entries of `global/settings-defaults.json` in `settings.json`, nothing else there; it never sets the model and never deletes).
- `global/settings-defaults.json`: what is off or hand-invoked on every machine.

## MEDIUM: builder builds, reviewer reviews
- Builder and transcriber wording that changes what they do or when they stop; the template's sections; a skill's steps or stop points; `check.py`.

## EASY: transcriber or builder, no review
- README wording, typos, examples that do not change a rule.

## Rules
- Models are pinned to full model IDs (`claude-opus-5-5`), never aliases. A model change edits `settings.json` (by the owner), every agent file and the "Current choice" line in one PR, with the switch test's numbers.
- The body of `hard-reviewer.md` is the body of `reviewer.md`: edit `reviewer.md`, then copy its body; `check.py` fails otherwise.
- Universal only: no project's paths, commands or names in `agents/`, `global/` or `skills/`. Project rules live in each project's `CLAUDE.md`.
- Nothing secret: no keys, tokens, hosts or ids.
- Git: English only; the `0xdonniechu` account (check with `gh api user --jq .login` before the first PR of a session; if it is not `0xdonniechu`, stop and ask; never `gh auth switch`); repo-local author `0xdonniechu`; branches `feat/...` or `fix/...`, never a push to `main` (the first commit was the only one); commit messages end with the Co-Authored-By trailer; do not merge without being asked. Cross-link the PR with its tracker item when there is one.

## Open
- The switch test runs when Fable 5.5 ships.
- Builder's and the reviewers' limits are prompt-only: they keep `Bash`, so `git commit` or `sed -i` stays possible in principle (review round 1, issue 8). A deny rule or hook would enforce it; not done yet.
