---
name: opencode-free
description: Run, configure, and troubleshoot OpenCode (terminal CLI and desktop app) using free, keyless models. Covers the TUI, one-shot `opencode run` tasks, model selection, a 20-model automatic failover chain, sessions, config locations, and delegating work to an OpenCode session from another agent. Use when the user asks how to use OpenCode, which model to pick, how to avoid rate limits without paying, how to set up free model fallback, or how to fix OpenCode errors.
license: MIT
compatibility: "OpenCode v2.x (CLI or desktop app). Optional: Claude Code or Codex for the same skill format. No API keys required."
metadata:
  version: "1.0.0"
  opencode/slash: "true"
---

# OpenCode with free models

OpenCode is a terminal/desktop AI coding agent. This skill explains how to drive it and how to
keep it running on free, keyless models with automatic failover.

## When to use this

- The user asks how to start OpenCode, run a task, or switch models.
- The user wants to stop hitting rate limits without paying.
- The user asks where OpenCode's config lives or how to change the default model.
- Another agent needs to delegate a task to OpenCode non-interactively.
- OpenCode errors need diagnosing.

Do **not** use this to configure unrelated editors or to add paid providers unless asked.

## Two front ends, one config

| Front end | How to start |
| --- | --- |
| Terminal CLI | `opencode` (in the project folder) |
| Desktop app | Launch the OpenCode app, open the folder |
| No UI / scripting | `opencode run "task"` |
| Minimal UI | `opencode mini` |

CLI, app, and scripts read the **same** config and skills, so anything configured once applies
everywhere.

## Quick start

```bash
cd /path/to/project
opencode              # interactive TUI
opencode /path/to/project
opencode -c           # continue the previous session
```

In the TUI: type the request, press Enter; approve tool actions with `y`/`n`.
`@file` attaches a file, `!command` runs a shell command, `/help` lists slash commands.

One-shot, for scripts and CI:

```bash
opencode run "fix the failing tests"
opencode run "review this diff" --agent plan
opencode run "list the API routes" --format json
```

## Core workflows

| Goal | Command |
| --- | --- |
| Understand a codebase | `opencode` → "explain the architecture" |
| Fix a bug | `opencode run "the login button does nothing, find and fix it" --auto` |
| Add a feature | `opencode` → "add dark mode following existing theme code" |
| Review changes | `git diff \| opencode run "review this diff for bugs"` |
| Refactor safely | `opencode` → "split utils.ts into modules, keep imports working" |
| Read-only analysis | `opencode run "..." --agent plan` |

## Free models (no API key)

Default: **`opencode/glm-5.3-flash-free`**.

| Need | Model |
| --- | --- |
| Fastest / high volume | `opencode/beam-free`, `opencode/big-pickle`, `openrouter/liquid/lfm-3-1.7b:free` |
| Balanced default | `opencode/glm-5.3-flash-free`, `opencode/minimax-m3.1-flash-free` |
| Harder reasoning | `openrouter/baidu/ernie-5.5-flash-preview:free`, `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` |
| Long context (~1M) | `openrouter/nvidia/nemotron-3.5-super-vl:free`, `openrouter/baidu/ernie-5.5-flash-preview:free` |
| Big code edits | `opencode/deepseek-v4.1-flash-free` (slower, stronger) |

```bash
opencode models                            # list everything installed
opencode run "hi" -m opencode/beam-free    # force one model
```

Free model IDs change over time. If one stops working, run `opencode models` and pick another,
or add a free-tier provider key (`docs/api-keys.md` pattern in the user's setup).

## Automatic failover (the important part)

Rate limits are the main failure mode of free models. Fix it with a fallback chain: a list of
free models, tried in order whenever the active one fails.

Signals that trigger a switch: HTTP 401/402/403/429/5xx, quota/credit/allowance errors,
subscription walls, country blocks, and no first token within a timeout.

Setup (one JSON file, no code):

1. Install the fallback plugin (OpenCode plugin system): `opencode-runtime-fallback`.
2. Create `opencode-fallback.json` next to `opencode.json` with `enabled: true`,
   `timeout_seconds: 60`, `cooldown_seconds: 600`, and a `fallback_models` array.
3. Run `opencode reload`.

A ready-to-copy 20-model template and the exact plugin/registration steps are in
[references/free-models.md](references/free-models.md).

Verify:

```bash
Get-Content ~/.config/opencode/opencode-fallback.log -Tail 20   # Windows
tail -20 ~/.config/opencode/opencode-fallback.log              # macOS/Linux
```

Failed models cool down for 10 minutes, then become eligible again. The TUI may print the failed
model's error before showing the recovered answer — cosmetic, not a failure.

## Delegating work to OpenCode (for agents)

When a task should run in a separate OpenCode session:

```bash
opencode run --auto -m opencode/beam-free --format json "task text"
```

Rules:

- Use the full path if `opencode` may not be on PATH.
- **Never** launch the bare interactive `opencode` from a tool call — the TUI blocks forever.
- One level of delegation only; do not let the child delegate again.
- Non-interactive runs need `--auto`, otherwise permission prompts hang.
- Use `--format json` when the caller parses the answer; cap runtime and kill on overrun.
- `--agent build` for repo edits, `--agent plan` for read-only analysis.

## Command reference

| Command | Purpose |
| --- | --- |
| `opencode [dir]` | TUI for a folder |
| `opencode run "msg"` | one-shot; flags: `-m`, `--agent`, `--auto`, `--format`, `-c`, `-f` |
| `opencode mini` | minimal interactive UI |
| `opencode models` | list available models |
| `opencode session list/export/delete` | manage sessions |
| `opencode auth list/login` | integrations and credentials |
| `opencode reload` | reload config after edits |
| `opencode service status/restart/stop` | background server |
| `opencode debug paths` | config/data/cache locations |
| `opencode upgrade` | update the CLI |

TUI slash commands: `/models` (`ctrl+x m`), `/new` (`ctrl+x n`), `/sessions` (`ctrl+x l`),
`/compact` (`ctrl+x c`), `/undo` (`ctrl+x u`), `/redo` (`ctrl+x r`), `/export` (`ctrl+x x`),
`/exit` (`ctrl+x q`), `/themes`, `/init`, `/help`.

More detail: [references/commands.md](references/commands.md).

## Config locations

| What | Windows | macOS / Linux |
| --- | --- | --- |
| Config | `%USERPROFILE%\.config\opencode` | `~/.config/opencode` |
| Skills | `<config>\skills\<name>\SKILL.md` | `~/.config/opencode/skills/<name>/SKILL.md` |
| Sessions/data | `%USERPROFILE%\.local\share\opencode` | `~/.local/share/opencode` |

Confirm with `opencode debug paths`. Main files: `opencode.json` (providers, default model,
plugins) and `opencode-fallback.json` (failover chain).

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `opencode` not recognized | open a new terminal, or call the binary by full path |
| New skill not visible in the app | restart the desktop app |
| Response slow (10–30 s) | free models; try `-m opencode/beam-free` |
| Constantly asks permission | `--auto` (CLI) or `/auto` (TUI) |
| Config edit ignored | `opencode reload` |
| Server stuck | `opencode service restart` |
| "not available in your country" | expected; the chain should skip it |
| Every model fails | check `opencode models`, JSON validity, and the fallback log |

## Guardrails

- Keep the chain free and keyless unless the user asks for paid providers.
- Never commit API keys; reference them from env vars or a key file.
- Free tiers change; treat model IDs as examples, verify with `opencode models`.
