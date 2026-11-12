# Free models + automatic failover — full setup

Two independent keyless pools make this work:

| Pool | Models | Key needed |
| --- | --- | --- |
| OpenCode | `opencode/*-free` | none |
| OpenRouter free tier | `openrouter/*:free` | none (higher limits with a key) |

Because the pools are independent, one running dry does not stop the chain.

## 1. Install the fallback plugin

```bash
opencode plugin add opencode-runtime-fallback
```

This adds the plugin to the global config:

```jsonc
{
  "plugins": ["opencode-runtime-fallback"]
}
```

## 2. Create the chain

Save as `opencode-fallback.json` in the OpenCode config directory (same folder as
`opencode.json`):

```jsonc
{
  "enabled": true,
  "timeout_seconds": 60,
  "cooldown_seconds": 600,
  "max_fallback_attempts": 20,
  "notify_on_fallback": true,
  "foreground_task_fallback": true,
  "retry_on_errors": [401, 402, 403, 429, 500, 502, 503, 504, 529],
  "retryable_error_patterns": [
    "quota",
    "credit balance",
    "usage limit",
    "rate limit",
    "insufficient",
    "billing",
    "allowance",
    "daily free",
    "token allowance",
    "exhausted",
    "capacity",
    "temporarily",
    "subscription",
    "available only",
    "no access",
    "not entitled",
    "upgrade",
    "permission denied",
    "unauthorized",
    "api key",
    "authentication",
    "forbidden",
    "not available in your country",
    "provider returned error"
  ],
  "fallback_models": [
    "opencode/glm-5.3-flash-free",
    "opencode/beam-free",
    "opencode/minimax-m3.1-flash-free",
    "opencode/big-pickle",
    "opencode/flint-40b-free",
    "openrouter/recursive/flint-v1.0:free",
    "openrouter/thinkingmachines/inkling-2-small:free",
    "opencode/nemotron-3.5-lightning-free",
    "openrouter/baidu/ernie-5.5-flash-preview:free",
    "openrouter/liquid/lfm-3-1.7b:free",
    "openrouter/cohere/north-mini-code:free",
    "openrouter/nvidia/nemotron-3.5-lightning:free",
    "openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "opencode/iceman-free",
    "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
    "opencode/longcat-2.5-free",
    "openrouter/nvidia/nemotron-3.5-super-vl:free",
    "opencode/deepseek-v4.1-flash-free",
    "opencode/mimo-v2.6-flash-free",
    "openrouter/liquid/lfm-2.5-2.6b:free"
  ]
}
```

Then:

```bash
opencode reload
```

## 3. Set the default model

`opencode.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode/glm-5.3-flash-free"
}
```

## 4. Verify

```bash
opencode run "Reply with exactly: OK"
```

Then force a failing model and watch it recover:

```bash
opencode run "Reply with exactly: OK" -m opencode/inkling-2-small-free
```

Expect two `> build · …` lines: the failing model, then a working one, followed by `OK`.

Log: `<config>/opencode-fallback.log`.

## Verified acting models

Tested on 2026-11-12; all answered directly with no key. Times are first-response latency.

| Model | Time |
| --- | --- |
| `opencode/big-pickle` | 3.6 s |
| `opencode/beam-free` | 3.7 s |
| `opencode/nemotron-3.5-super-vl-free` | 3.7 s |
| `opencode/flint-40b-free` | 3.9 s |
| `opencode/minimax-m3.1-flash-free` | 3.9 s |
| `openrouter/liquid/lfm-2.5-2.6b:free` | 3.2 s |
| `openrouter/liquid/lfm-3-1.7b:free` | 3.5 s |
| `openrouter/baidu/ernie-5.5-flash-preview:free` | 4.0 s |
| `openrouter/nvidia/nemotron-3.5-lightning:free` | 4.0 s |
| `openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | 4.0 s |
| `openrouter/thinkingmachines/inkling-2-small:free` | 4.1 s |
| `opencode/nemotron-3.5-lightning-free` | 4.2 s |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | 4.7 s |
| `openrouter/cohere/north-mini-code:free` | 4.8 s |
| `opencode/longcat-2.5-free` | 5.1 s |
| `openrouter/recursive/flint-v1.0:free` | 5.0 s |
| `opencode/iceman-free` | 6.2 s |
| `opencode/glm-5.3-flash-free` | 8.3 s |
| `openrouter/nvidia/nemotron-3.5-super-vl:free` | 10.2 s |
| `opencode/deepseek-v4.1-flash-free` | 13.3 s |
| `opencode/mimo-v2.6-flash-free` | 23.9 s |

Known-bad at test time: `opencode/inkling-2-small-free` (country block),
`openrouter/google/gemma-4-26b-a4b-it:free` and `openrouter/google/gemma-4-31b-it:free`
(provider error / timeout). Do not put them in the chain.

Free model availability changes. Re-check with:

```bash
opencode models | grep -E 'opencode/.*-free$|openrouter/.*:free$'
opencode run "Reply with exactly: OK" -m <model>
```

## Tuning

| Key | Effect |
| --- | --- |
| `timeout_seconds` | how long to wait for the first token before switching |
| `cooldown_seconds` | how long a failed model is skipped |
| `max_fallback_attempts` | cap on switches per request |
| `retryable_error_patterns` | text fragments that count as "switch now" |
| `notify_on_fallback` | show a note when a switch happens |

Per-agent overrides use an `agents` object:

```jsonc
{
  "agents": {
    "build": { "fallback_models": ["opencode/glm-5.3-flash-free", "opencode/beam-free"] },
    "plan":  { "fallback_models": ["opencode/beam-free", "openrouter/baidu/ernie-5.5-flash-preview:free"] }
  }
}
```
