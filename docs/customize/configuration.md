---
sidebar_position: 3
title: Configuration
description: What is baked into the binary, what lives in ~/.bravebot, and the environment variables that override either.
---

# Configuration

Configuration is built into the released binary, so a fresh install needs nothing set up. What it
will actually use is reported by:

```sh
bravebot doctor
```

```
configuration OK
  endpoint  https://ai-chat.bsg.brave.com/v1/chat/completions
  premium   https://ai-chat-premium.bsg.brave.com/v1/chat/completions
  key id    …
  model     automatic (default)
  key       … (never transmitted)

confinement …
  mechanisms       …
```

`doctor` changes nothing. It exists to answer "what will this actually use", so it reports a choice
where one is in force rather than the default it overrode, and a configuration error makes it fail
rather than pass with a warning. The signing key is named as never transmitted.

## `~/.bravebot`

Everything that should outlive a session lives here:

| Path | What it holds |
|---|---|
| `~/.bravebot/AGENTS.md` | standing instructions for every project |
| `~/.bravebot/skills/<name>/SKILL.md` | skills available in every project |
| `~/.bravebot/sessions/<directory>/` | session records and audit trails |
| `~/.bravebot/history` | prompts you have sent |
| `~/.bravebot/model` | the model chosen with `/model` |

The directory rather than a per-project file, for the same reason in both cases: a question worth
asking again is usually worth asking in another checkout too, and which model to think with is not a
property of a checkout.

Every operation here degrades to doing nothing. A missing home directory, a read-only disk or a
corrupt file is not worth refusing to start over, because the session works without any of it.

:::note
What comes back from `~/.bravebot` is not fed straight to a turn. A recalled prompt is placed in the
input box, where you read it and press Enter — that keystroke is what makes it trusted, exactly as
typing it would have. A model name the server does not recognise is reset to `automatic` rather than
obeyed.
:::

`~/.bravebot` is the directory the environment names, and there is no fallback. When there is no
home, or the name is empty, everything kept there is simply absent.

## Choosing a model

```
/model
```

opens a picker on the model currently in use. The list comes from the endpoint rather than from a set
compiled in, so it is whatever the backend actually offers today. The choice is written to
`~/.bravebot/model`, so it outlives the session that made it and applies in every directory.

`automatic` lets the server triage per request, and is what an unrecognised name is reset to. Note
that the model requested is not necessarily the model used: some entries are weighted ensembles that
resolve per request, and `automatic` itself picks per request.

The names never reach a model. They are drawn for a person, who picks one, and what they picked
becomes the `model` field of later requests — a routing field, endorsed by a person choosing it off a
list they read.

## Environment variables

The environment wins when set, which is how a released binary is pointed at a local backend without
rebuilding it.

| Variable | What it sets |
|---|---|
| `BRAVE_AI_CHAT_ENDPOINT` | the host requests go to |
| `BRAVE_AI_CHAT_PREMIUM_ENDPOINT` | the premium host, used once a subscription is imported |
| `SERVICES_KEY_AICHAT` | the services key requests are signed with |
| `BRAVE_SERVICES_KEY_ID` | the key id that goes with it |
| `BRAVE_AI_CHAT_DEFAULT_MODEL` | the model to request when nobody has chosen one |
| `BRAVEBOT_CONTEXT_BUDGET` | the token budget before a conversation is compacted |

To point a release build at a backend running locally:

```sh
BRAVE_AI_CHAT_ENDPOINT=http://127.0.0.1:8000 bravebot doctor
```

`BRAVE_AI_CHAT_DEFAULT_MODEL` is a **default rather than the setting**: `/model` picks one per user
and that choice wins, so this applies until somebody makes one.

`BRAVEBOT_CONTEXT_BUDGET` is deliberately never baked into a binary. The others are credentials and
hosts, which belong to the build; this is a knob one person turns while working, and a value someone
exported to debug a session should not ship to everyone who uses their release.

## Context budget

A conversation is compacted when it grows past its token budget: an older stretch of it is replaced by
a summary, in the request only. The default is 24,000 prompt tokens.

A budget that makes no sense falls back to the default rather than disabling compaction, so a
misconfiguration cannot quietly turn the mechanism off.

The default sits well below any real context window on purpose. A budget *above* the window never
fires, so being wrong upward does not make compaction late — it removes it. Anyone running a larger
model raises it rather than discovering it was never doing anything:

```sh
BRAVEBOT_CONTEXT_BUDGET=120000 bravebot
```

The figure compared is what the server said the **last** round's request came to, so the check is one
round late by construction and the budget has to sit below the window rather than at it. A turn that
has not measured anything yet compacts nothing.

`/compact` asks for the same work on demand, at any size, and does not consult the budget. See
[Sessions](../using/sessions.md#long-conversations).

## Building with different configuration

A source build captures whatever is set at build time, so the resulting binary works in any directory
rather than needing the environment wherever it is started. A build with nothing set **fails** rather
than producing a binary that only works in the tree it came from. See [Development](../development.md).
