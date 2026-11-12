# Command reference

OpenCode v2.x. Run `opencode <command> --help` for the authoritative list.

## Top level

```text
opencode [directory]     TUI for a folder (default: current)
opencode run ...         one-shot, non-interactive
opencode mini ...        minimal interactive UI
opencode serve           start the API/web server
opencode api             call the running server
opencode models          list models
opencode session ...     list / export / import / delete sessions
opencode auth ...        integrations and credentials
opencode mcp ...         MCP servers
opencode plugin ...      plugins (add / list / update / remove)
opencode service ...     background server (status / restart / stop)
opencode reload          reload configuration
opencode debug ...       paths, config, agents, heap-dump
opencode upgrade         update the CLI
opencode uninstall       remove the CLI, keep data
```

Global flags: `--help`, `--version`, `--standalone` (private server), `--server <url>`,
`--log-level <level>`, `--print-logs`, `--completions <shell>`, `--wizard`.

## run

```text
opencode run [message...] [flags]
```

| Flag | Meaning |
| --- | --- |
| `-m, --model provider/model#variant` | force a model |
| `--agent <name>` | `build` (edits) or `plan` (read-only) |
| `--auto` | auto-approve permissions not explicitly denied |
| `--format default\|json` | output format |
| `-c, --continue` | continue the last session |
| `-s, --session <id>` | continue or create a session by id |
| `--fork` | fork the session before continuing |
| `-w, --worktree [name]` | run in a new git worktree |
| `-f, --file <path>` | attach a file |
| `--title <text>` | session title |
| `--archived` | keep the session out of session lists (CI) |
| `--thinking` | print thinking blocks |

Notes:

- Without `--auto`, permission prompts block a non-interactive run.
- `--format json` is the safe choice for parsing.
- A run exits non-zero when the request fails; OpenCode may also print a harmless
  `NativeCommandError` wrapper in PowerShell.

## Interactive TUI

Slash commands:

| Command | Action | Keybind |
| --- | --- | --- |
| `/models` | pick a model | `ctrl+x m` |
| `/new` (`/clear`) | new session | `ctrl+x n` |
| `/sessions` (`/resume`) | switch session | `ctrl+x l` |
| `/compact` (`/summarize`) | shrink context | `ctrl+x c` |
| `/undo` | undo last turn + file changes | `ctrl+x u` |
| `/redo` | re-apply undo | `ctrl+x r` |
| `/export` | export to Markdown | `ctrl+x x` |
| `/editor` | compose in `$EDITOR` | `ctrl+x e` |
| `/themes` | change theme | `ctrl+x t` |
| `/thinking` | show/hide reasoning | |
| `/init` | create/update `AGENTS.md` | |
| `/connect` | add a provider | |
| `/exit` (`/quit`, `/q`) | quit | `ctrl+x q` |
| `/help` | help dialog | |

Input tricks: `@path` attaches files, `!command` runs a shell command, Enter sends,
Shift+Enter adds a newline. `ctrl+p` opens the command palette.

`/undo` and `/redo` restore file changes through Git, so the project must be a Git repository.

## Sessions

```bash
opencode session list
opencode session export <id> > session.json
opencode session import session.json
opencode session delete <id>
opencode -c
```

## Plugins

```bash
opencode plugin add opencode-runtime-fallback
opencode plugin list
opencode plugin check
opencode plugin update
opencode plugin remove opencode-runtime-fallback
```

## Service and diagnostics

```bash
opencode service status
opencode service restart
opencode service stop
opencode debug paths
opencode debug config
opencode debug agents
```

## Configuration

Main file: `<config>/opencode.json` (JSON or JSONC). Common keys:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/glm-5.3-flash-free",
  "plugins": ["opencode-runtime-fallback"],
  "provider": { }
}
```

After editing: `opencode reload`. If the change affects the background server, restart it.

## Exit codes and noise

`opencode run` writes its UI to stderr. In PowerShell that surfaces as a red
`NativeCommandError` block even when the answer is fine. Filter with:

```powershell
& opencode run "hi" 2>&1 | ForEach-Object { $_ -replace "`e\[[0-9;]*m",'' }
```
