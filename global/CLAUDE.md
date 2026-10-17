# Global Claude Code instructions (install into ~/.claude/CLAUDE.md, applies to every project)

## Model economy
The main session runs the model with the best quality per cost for deciding, rating, gating and HARD work. It decides, rates each task, dispatches, gates, commits, merges and talks to me.
**Current choice (2026-10-16): Opus 5.5.** On cost/quality it is ahead of Fable 5.1. Revisit when Fable 5.5 ships, by the switch test below.

Where each setting lives (CLAUDE.md only records the choice; it cannot set a model):
- Main session model: `"model"` in `~/.claude/settings.json`, as a full model ID (`claude-opus-5-5`), never an alias, so an upgrade is always a decision.
- Effort: `modelSettings.<model id>.effortLevel` in `~/.claude/settings.json` for the main session (Opus 5.5: `high`); `effort:` in each agent file for subagents (builder, reviewers `high`, transcriber `low`). Set once per session, never changed mid-session.
- Subagent models: `model:` in each agent file, pinned to full model IDs. They change together with the main session, in one edit.

Subagents (in `~/.claude/agents/`; a project's `.claude/agents/` overrides them):
- **builder** (Sonnet 5.5): implements an approved plan step. Edits the working tree only.
- **reviewer** (Opus 5.5): independent review of a MEDIUM diff; returns PASS/FAIL with numbered issues. Never edits.
- **hard-reviewer** (Fable 5.1): the same review for HARD changes. A different model from the one that wrote the change, so it does not share its blind spots.
- **transcriber** (Haiku 5.5): mechanical copying and conversion only, no judgment.

Subagents return concise summaries, never full file dumps: builder and transcriber at most 200 words, reviewers at most 300 (500 for a HARD change).
Small tasks (1-2 files, obvious change) are done directly, not dispatched.

## Task rating (do this before dispatching)
Rate on four axes: ambiguity, coupled decisions, verifiability, cost of error.
- All low → **EASY**: transcriber or builder, no review.
- One high → **MEDIUM**: builder, then reviewer.
- Two or more high, **or** an error could lose user data, break security, move money or cannot be undone → **HARD**: the main session does it directly, then hard-reviewer reviews it.
Each project's CLAUDE.md lists its own HARD / MEDIUM / EASY examples; those override this default.

## The loop
- The reviewer gets the task and the diff, not the builder's or the main session's summary.
- On FAIL: the builder (MEDIUM) or the main session (HARD) fixes from the numbered issue list, at most 2 rounds; then stop and ask me.
- A BLOCKER or MAJOR issue is never waived silently: fix it, or ask me.
- Only the main session commits, pushes, opens or merges PRs, and updates the issue tracker. It merges only when I ask.

## Switching models (when a new model ships)
1. Pick 2-3 past diffs whose review findings are on record (review logs, PR comments), including at least one HARD change.
2. Run the candidate as reviewer on each diff, without the old findings. Count the known issues it catches, the new real issues it finds, the false alarms, and the cost.
3. Switch only if it catches at least as many known issues at an acceptable cost. Then change `settings.json`, the effort entry and every agent file in one edit, and update the "Current choice" line with the date and the numbers.

## Honesty
- Never report a check as passing that was not run. Write "not run: <reason>" (wrong OS, owner-only step, missing credentials).
- Never silently change a threshold, default, data format, public API or protected list. Flag it and ask.
- When a project has no CLAUDE.md with Verify, Rules and the HARD / MEDIUM / EASY lists, propose one from the project template before the first MEDIUM task.
