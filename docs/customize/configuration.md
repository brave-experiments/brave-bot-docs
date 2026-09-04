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
  offers    Brave Leo
  endpoint  https://ai-chat.bsg.brave.com/v1/chat/completions
  premium   https://ai-chat-premium.bsg.brave.com/v1/chat/completions
  key id    …
  model     automatic (default)
  key       … (never transmitted)
  settings  no settings.json

confinement …
  mechanisms       …
```

`doctor` changes nothing. It exists to answer "what will this actually use", so it reports a choice
where one is in force rather than the default it overrode, and a configuration error makes it fail
rather than pass with a warning. The signing key is named as never transmitted.

It reports **every backend this build can reach**, not just one, so a machine with an AWS account
configured shows a second `offers` block with its region, profile and tiers — see
[Reaching Claude on AWS Bedrock](#reaching-claude-on-aws-bedrock). The `settings` line names which
keys your settings file set, and never their values: a settings file holds credentials on some
machines, and a diagnostic that prints one is a diagnostic people paste into issues.

## `~/.bravebot`

Everything that should outlive a session lives here:

| Path | What it holds |
|---|---|
| `~/.bravebot/AGENTS.md` | standing instructions for every project |
| `~/.bravebot/skills/<name>/SKILL.md` | skills available in every project |
| `~/.bravebot/sessions/<directory>/` | session records and audit trails |
| `~/.bravebot/history` | prompts you have sent |
| `~/.bravebot/model` | the model chosen with `/model` |
| `~/.bravebot/theme` | the theme chosen with `/theme` |
| `~/.bravebot/themes/<name>.json` | themes you wrote yourself |
| `~/.bravebot/settings.json` | an `env` block naming a backend — see [below](#settingsjson) |

An imported Leo Premium subscription is kept here too, in a file only you can read — see
[Leo Premium](premium.md#where-they-are-kept).

The directory rather than a per-project file, for the same reason in every case: a question worth
asking again is usually worth asking in another checkout too, and neither which model to think with
nor which colours to draw in is a property of a checkout.

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

With an AWS account configured the picker offers its tiers alongside this list rather than instead of
it, and each row says which service will answer — see
[Reaching Claude on AWS Bedrock](#reaching-claude-on-aws-bedrock).

## Choosing a theme

```
/theme
```

opens a picker that live-previews over your own transcript; `/theme <name>` applies one directly. The
choice is written to `~/.bravebot/theme`, so it outlives the session that made it and applies in every
directory, exactly as the model choice does. A name that matches no theme, and an empty or corrupt
file, is no choice at all and falls back to `brave`. A choice saved under the earlier name `system`
still finds `brave` rather than being silently lost.

A theme of your own is a JSON file under `~/.bravebot/themes/`, named for the theme: `nord.json` is
the theme `nord`. Each key is one role, and any you leave out inherits from `brave`:

```json
{
  "defs": { "ink": "#cdd6f4", "shell": "#1e1e2e" },
  "background": "shell",
  "text": "ink",
  "muted": "#6c7086",
  "ok": "#a6e3a1",
  "fail": "#f38ba8",
  "running": "#f9e2af",
  "accent": "#cba6f7",
  "note": "#fab387",
  "primary": "#89b4fa"
}
```

A value is a `#rrggbb` colour, a name from `defs`, or `none` to leave that role to your terminal's own
default. A `defs` entry that names another `defs` entry is refused rather than chased, so a palette
cannot loop. A file that will not parse is left out of the list rather than stopping the session.

:::note
Themes are read from `~/.bravebot/themes` and from nowhere else. A `.bravebot/themes` directory inside
a project is **not** consulted, because a workspace is content: a repository you have just cloned must
not be able to decide how your interface is painted, and colours are how you tell one thing on the
screen from another.
:::

See [Reading the transcript](../using/transcript.md#themes) for what each role paints.

## Choosing a language

Brave Bot reads the interface in your language where a translation for it has shipped, and in English
otherwise. It takes the first of `BRAVEBOT_LOCALE`, `LC_ALL`, `LC_MESSAGES` and `LANG` that is set, so
on a machine already set up for French there is nothing to do.

```sh
bravebot                          # whatever your shell says
BRAVEBOT_LOCALE=fr bravebot       # this once
export BRAVEBOT_LOCALE=fr         # from now on
```

`BRAVEBOT_LOCALE` is there so one program can be in a language the rest of your shell is not — which
is usually wanted the other way round, an English interface on an otherwise French machine.

A request widens rather than failing: `fr-CA` and `fr-BE` are answered by the French catalog where
they have none of their own, and a language nothing has shipped for reads in English. `LC_ALL=C` asks
for no translation at all. English and French are what ship today.

### What stays in English

- **The names of the slash commands**, so `/model` is `/model` everywhere.
- **The letters a question is answered with**, `y` and `n`. These are both the key drawn and the key
  matched, so a French reader is told to press `y` for *oui*. Changing that would mean changing what
  the interface listens for, not just what it says.
- **The audit trail.** It is a record rather than prose — fixed columns of gate and capability names
  that are identifiers, read against the specs that use those same names.
- **The words on the working indicator**, unless a language supplies its own list. They are chosen
  for tone and variety rather than meaning, and translating one word for word keeps neither.

Digit grouping and currency forms are not localized either; a catalog says only what separates a
whole number from its fraction. A partial imitation of the full rules reads worse than a plain
number, because it is wrong only sometimes.

**Nothing the model is sent changes with your language.** Tool descriptions, the preamble and the
sentence a refused tool answers with all stay as they are, because the words in them are load-bearing
on what the planner does. Translating them would make the agent *behave* differently in French, which
is a change nobody would find by reading the French. So switching language changes what you read and
never what the agent does.

## Environment variables

The environment wins when set — over both the built-in values and
[`settings.json`](#settingsjson) — which is how a released binary is pointed at a local backend
without rebuilding it.

| Variable | What it sets |
|---|---|
| `BRAVE_AI_CHAT_ENDPOINT` | the host requests go to |
| `BRAVE_AI_CHAT_PREMIUM_ENDPOINT` | the premium host, used once a subscription is imported |
| `SERVICES_KEY_AICHAT` | the services key requests are signed with |
| `BRAVE_SERVICES_KEY_ID` | the key id that goes with it |
| `BRAVE_AI_CHAT_DEFAULT_MODEL` | the model to request when nobody has chosen one |
| `BRAVEBOT_CONTEXT_BUDGET` | the token budget before a conversation is compacted |
| `BRAVEBOT_LOCALE` | the language the interface is read in |

Six more name an AWS account rather than this build — see
[Reaching Claude on AWS Bedrock](#reaching-claude-on-aws-bedrock).

To point a release build at a backend running locally:

```sh
BRAVE_AI_CHAT_ENDPOINT=http://127.0.0.1:8000 bravebot doctor
```

`BRAVE_AI_CHAT_DEFAULT_MODEL` is a **default rather than the setting**: `/model` picks one per user
and that choice wins, so this applies until somebody makes one.

`BRAVEBOT_CONTEXT_BUDGET` is deliberately never baked into a binary. The others are credentials and
hosts, which belong to the build; this is a knob one person turns while working, and a value someone
exported to debug a session should not ship to everyone who uses their release.

## `settings.json`

Long-lived configuration can go in a file instead of your shell profile:

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "us-west-2",
    "AWS_PROFILE": "my-profile",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "arn:aws:bedrock:…"
  }
}
```

Only the `env` block is read, and only string values in it: `1` and `true` are not obviously `"1"` and
`"true"` to whoever debugs this later, so a number or a boolean is skipped rather than coerced. Every
name in the block is read rather than a chosen subset.

**The file is the same shape as Claude Code's `~/.claude/settings.json`, down to the variable names**,
so a block that configures one configures the other unedited. That is deliberate rather than
incidental: the names below are `CLAUDE_CODE_*` and `ANTHROPIC_*` because a second spelling for the
same handful of values would be another thing to learn in exchange for nothing.

**The environment wins over the file.** A variable exported in your shell overrides the same name here,
which is what makes the file a place to keep a durable default rather than a thing to edit when you
want a one-off.

Two limits are worth knowing because they fail silently, by design. A file over 64 KB is refused
rather than parsed, and **every failure is treated as absence** — no file, a syntax error, an
unparseable value — because the built-in configuration still describes a working backend. Nothing
refuses to start over this; `bravebot doctor` is where a file nobody can parse shows up, since the
person who mistyped it is not necessarily the person watching a session begin.

:::note
**Nothing in this file grants a permission.** It names destinations — a region, a credential profile, a
model — and never vouches for a path or decides whether an effect is allowed. It does not become the
process environment either: a value is consulted where a variable would be, and reaches a subprocess
only where that subprocess is the thing it configures. The file is the easiest thing on the machine to
write to, so a permission grantable from here would be a permission granted by whatever last edited it.
:::

## Reaching Claude on AWS Bedrock

Two services can answer a request: the aichat endpoint Brave runs, and Claude on AWS Bedrock through
your own AWS account. Every build can reach Brave; Bedrock is what you configure.

| Variable | What it sets |
|---|---|
| `CLAUDE_CODE_USE_BEDROCK` | turns the backend on |
| `AWS_REGION` | which region to reach Bedrock in — **required** once it is on |
| `AWS_PROFILE` | which profile names the credentials to sign with (optional) |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | the model the Opus tier names |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | the model the Sonnet tier names |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | the model the Haiku tier names |

Each tier takes either a model id or an inference-profile ARN. With `AWS_PROFILE` unset the AWS CLI
resolves credentials as it would for any other command, which is what a machine on instance
credentials already relies on.

**Claude models only, despite Bedrock hosting many others.** A request is sent as the Anthropic
Messages API, which is the format Claude answers and other models on Bedrock do not. Nothing local
checks the name you set — an ARN for Llama, Mistral, Titan or Nova is signed and sent like any other,
and Bedrock rejects the request body. Point a tier at a non-Claude model and every request on it
fails remotely.

**A tier you do not name is left out rather than guessed at.** An ARN cannot be derived from a model
name, so an invented entry would be a row in the picker that fails at the far end for a reason nothing
local could explain. Set one tier and one tier is offered.

### What it changes, and what it does not

**Configuring Bedrock takes nothing away from Brave.** Both rosters are offered together in `/model`,
so this adds models rather than replacing them. It also does not move the default: what answers when
nobody has chosen stays what it was.

**The model names the service.** A request goes to whichever service offers the model it names, and
nothing else participates — not which configuration is present, not which service answered last.
Bedrock refuses a model it does not recognise rather than substituting one, and the aichat endpoint has
never heard of an inference-profile ARN.

Your tiers read as `Opus (your my-profile AWS profile)`, or `Opus (your AWS account)` with no profile
set. The profile is named because it is what decides which credentials sign the request, and because
Brave serves part of its own roster through Bedrock too — so the word "Bedrock" on a row would
distinguish nothing. Every configured tier is marked free: premium means a Leo subscription, and
reaching a model through your own account does not involve one.

There is no `automatic` among them. There it means "let the server choose", which Bedrock does not
offer — a request names one model and gets it or an error.

If one service cannot say what it offers, the models known from your configuration alone are still
offered; a choice is refused only when nothing is left to choose. That is the position somebody
offline is most likely to be in.

### Signing in

Where AWS has no usable session, the sign-in happens **before the turn starts**, and only for the
service the next request will actually go to — a turn served entirely by Brave never stops to
authenticate against AWS. The screen stays yours: the URL and code the AWS CLI prints appear line by
line where you are already reading, because those lines *are* the flow rather than a report of it, and
collected up and printed at the end they would arrive once the code had stopped working.

Credentials are resolved by running the AWS CLI, which is the tool you already sign in with. It holds
short-lived keys that expire during a session. `aws sso logout` clears them, and note it takes no
option to narrow itself: it removes every cached token, so other tools sharing that cache need a fresh
`aws sso login` afterwards.

### The assumed context window

Every configured tier is assumed to have a 131,072-token window. Nothing at AWS reports a context
window, and an inference-profile ARN does not say which model it resolves to, so one figure stands in
for all of them — deliberately a low one. Being wrong upward would not shorten a conversation late, it
would stop shortening it at all: every round asks, no round qualifies, and the session runs to
exhaustion looking like one with nothing to summarise. Set `BRAVEBOT_CONTEXT_BUDGET` if you know your
model's real window and want to use it.

## Context budget

A conversation is compacted when it grows past its token budget: an older stretch of it is replaced by
a summary, in the request only.

**The budget is the window the model advertises.** The model listing reports a figure per model, and
that figure is the budget for whichever model you chose. You do not normally set this at all.

A budget you set by hand outranks the advertised one. The built-in default of 24,000 prompt tokens
only stands in for two cases: `automatic`, whose model is resolved per request so no single window
describes it, and a model that advertises nothing.

An advertised figure is believed even where it is small, and never raised. A budget that makes no
sense falls back to the default rather than disabling compaction, so a misconfiguration cannot
quietly turn the mechanism off.

The window is looked up whenever a model is in force, not only when you pick one in the picker, so a
session starting on a model you chose earlier asks again. If that lookup fails the default stays in
place and nothing is said.

Setting it by hand is still there for when you want a shorter conversation than your model would
allow:

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
