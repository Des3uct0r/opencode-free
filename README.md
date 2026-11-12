# opencode-free

An [Agent Skill](https://agentskills.io) that teaches an AI agent how to run **OpenCode** — the
terminal and desktop AI coding agent — on **free, keyless models** with **automatic failover**, so
work continues when a free tier runs dry.

Works in **OpenCode** (CLI + desktop app), **Claude Code**, **Codex / ChatGPT desktop**, and
**claude.ai** — one `SKILL.md`, no code, no API keys.

---

## The problem it solves

Free model tiers have one failure mode: the quota runs out mid-task. You get a 429, a
"daily free tokens exhausted" message, or a country block, and the agent stops.

This skill documents a fixed setup:

- **20 free models** in an ordered chain across two independent keyless pools
  (OpenCode's built-in `:free` models and OpenRouter's `:free` models).
- A **60-second first-token timeout** and error-pattern matching so the next model takes over
  automatically — the task finishes without you touching anything.
- **Zero API keys, zero billing.** If you never add a key, nothing can charge you.

## Features

| | |
|---|---|
| **Keyless** | Works with no provider account; the default model needs no key |
| **Self-healing** | Rate limit, quota, subscription wall, country block, 5xx, or a stalled stream → next model |
| **Two pools** | OpenCode free models + OpenRouter free models; one pool failing does not stop the chain |
| **Verified** | Every model in the chain was live-tested; bad ones are listed so you can avoid them |
| **Portable** | Same skill file for OpenCode, Claude Code, Codex, and claude.ai |
| **No scripts required** | Pure instructions + config templates; optional installers included |

## Compatibility

| Host | Where the skill goes | How to invoke |
| --- | --- | --- |
| **OpenCode CLI** | `~/.config/opencode/skills/opencode-free/` | `/opencode-free` or automatic |
| **OpenCode desktop app** | same config directory as the CLI | automatic, or `/opencode-free` |
| **Claude Code** | `~/.claude/skills/` (personal) or `.claude/skills/` (project) | automatic, or `/opencode-free` |
| **Codex CLI / ChatGPT desktop** | `~/.agents/skills/` or `<repo>/.agents/skills/` | `$opencode-free` or automatic |
| **claude.ai** | upload the zipped skill folder in Settings → Capabilities → Skills | automatic |

Format compliance:

- Agent Skills spec: `name` ≤ 64 chars, lowercase/hyphens, matches the folder; `description`
  ≤ 1024 chars; optional `license`, `compatibility`, `metadata`.
- Claude stores extra fields safely; `metadata` is a string→string map (used here for the OpenCode
  slash-command flag).
- Codex uses the same standard and additionally reads `agents/openai.yaml` for UI metadata.

> OpenCode-specific parts (the `/opencode-free` slash command, the fallback plugin) only apply
> where OpenCode is installed. Model IDs, commands, and troubleshooting apply anywhere the
> `opencode` binary exists.

## Install

### OpenCode (CLI or desktop)

```powershell
# Windows
git clone https://github.com/Des3uct0r/opencode-free.git
Copy-Item -Recurse .\opencode-free\skills\opencode-free "$env:USERPROFILE\.config\opencode\skills\"
opencode reload
```

```bash
# macOS / Linux
git clone https://github.com/Des3uct0r/opencode-free.git
mkdir -p ~/.config/opencode/skills
cp -r opencode-free/skills/opencode-free ~/.config/opencode/skills/
opencode reload
```

Restart the desktop app once so it re-scans skills.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r opencode-free/skills/opencode-free ~/.claude/skills/
```

### Codex / ChatGPT desktop

```bash
mkdir -p ~/.agents/skills
cp -r opencode-free/skills/opencode-free ~/.agents/skills/
```

Or use the installer, which handles all targets:

```powershell
.\scripts\install.ps1                 # all detected hosts
.\scripts\install.ps1 -Target claude  # opencode | claude | codex
```

```bash
./scripts/install.sh                  # all detected hosts
./scripts/install.sh claude           # opencode | claude | codex
```

### claude.ai

Zip the skill directory and upload it under **Settings → Capabilities → Skills**:

```bash
cd skills && zip -r opencode-free.zip opencode-free
```

## Usage

```
/opencode-free                                  # OpenCode / Claude Code
$opencode-free                                  # Codex
```

Or just ask naturally — the description is written to trigger on questions like:

- "how do I use opencode?"
- "which free model should I use?"
- "opencode keeps hitting rate limits"
- "where is opencode's config?"
- "run this task through opencode from my script"

## What the skill contains

| File | Purpose |
| --- | --- |
| `SKILL.md` | The instructions: quick start, workflows, model picks, failover, delegation, troubleshooting |
| `references/free-models.md` | Copy-paste 20-model failover config + verified timings + tuning |
| `references/commands.md` | Full CLI flag reference, TUI keybinds, sessions, plugins, config |
| `agents/openai.yaml` | Codex/ChatGPT UI metadata |
| `scripts/install.ps1` / `install.sh` | Install into OpenCode, Claude Code, and Codex skill folders |
| `scripts/validate.py` | Spec validation (used by CI) |

## The chain

Ordered fastest-first, alternating the two pools. All entries verified answering with no key
(2026-11-12):

```text
opencode/glm-5.3-flash-free                  (default)
opencode/beam-free
opencode/minimax-m3.1-flash-free
opencode/big-pickle
opencode/flint-40b-free
openrouter/recursive/flint-v1.0:free
openrouter/thinkingmachines/inkling-2-small:free
opencode/nemotron-3.5-lightning-free
openrouter/baidu/ernie-5.5-flash-preview:free
openrouter/liquid/lfm-3-1.7b:free
openrouter/cohere/north-mini-code:free
openrouter/nvidia/nemotron-3.5-lightning:free
openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
opencode/iceman-free
openrouter/nvidia/nemotron-3-ultra-550b-a55b:free
opencode/longcat-2.5-free
openrouter/nvidia/nemotron-3.5-super-vl:free
opencode/deepseek-v4.1-flash-free
opencode/mimo-v2.6-flash-free
openrouter/liquid/lfm-2.5-2.6b:free
```

Known-bad at test time, intentionally excluded: `opencode/inkling-2-small-free` (country block),
`openrouter/google/gemma-4-26b-a4b-it:free`, `openrouter/google/gemma-4-31b-it:free` (provider
error / timeout).

Free catalogs change. Re-check yours with:

```bash
opencode models
```

## How failover works

1. A request starts on the active model.
2. If it returns 401/402/403/429/5xx, matches a quota/allowance/subscription pattern, or produces
   no first token within `timeout_seconds`, the plugin marks it failed for `cooldown_seconds` and
   retries on the next model.
3. The first model that answers completes the task.
4. `opencode-fallback.log` records every switch.

The TUI can print the failed model's error before the recovered answer. That is cosmetic.

Full configuration and tuning: [`references/free-models.md`](skills/opencode-free/references/free-models.md).

## Verify the setup

```bash
opencode run "Reply with exactly: OK"
```

Force a failure to see recovery:

```bash
opencode run "Reply with exactly: OK" -m opencode/inkling-2-small-free
```

Expected: two `> build · …` lines, then `OK`.

## Repository layout

```text
.
├── README.md
├── LICENSE
├── .github/workflows/validate.yml
├── scripts/
│   ├── install.ps1
│   ├── install.sh
│   └── validate.py
└── skills/
    └── opencode-free/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/
            ├── free-models.md
            └── commands.md
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Skill not listed | verify the folder name matches `name` (`opencode-free`) and `SKILL.md` is at its root |
| Not visible in the desktop app | restart the app |
| `/opencode-free` unknown | the host may not support slash-style skill invocation; ask naturally instead |
| Everything fails | run `opencode models`; check config JSON validity; read `opencode-fallback.log` |
| Model "not available in your country" | expected for some free models; keep them out of the chain |

## FAQ

**Is it actually free?** Yes — every model in the chain answered without a key. Free tiers are
rate-limited, which is exactly what the chain is for.

**Does my code leave my machine?** Yes. `opencode` sends the files you attach or that the agent
reads to the model provider — same as any hosted coding agent. Local Ollama models exist but do not
support tool calling, so they are not in the chain.

**Will it work forever?** Model IDs age out. The instructions tell the agent to re-check with
`opencode models` and swap in working free models; the config shape stays the same.

**Can I add paid providers?** Yes, but deliberately: get a key, add the model to the chain, and
keep paid entries last so free models are tried first.

## Contributing

Issues and PRs welcome. Please run the validator before pushing:

```bash
python scripts/validate.py
```

Optional CI: a ready-to-use workflow is at `scripts/github-workflow-validate.yml`.
Copy it to `.github/workflows/validate.yml` (requires the `workflow` scope on your
GitHub token) to run validation on every push and pull request.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Not affiliated with OpenCode, Anthropic, or OpenAI. Free tiers, model names, and pricing change
without notice; the verified list is a snapshot, not a guarantee.
