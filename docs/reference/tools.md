---
sidebar_position: 3
title: Tools
description: Every tool the model may call, what it takes, and what it is allowed to touch.
---

# Tools

Eleven tools, and no way to add a twelfth from a configuration file. Each one splits its arguments
into **routing** — the part that decides where the effect lands — and **content** — the part that is
merely carried.

| Tool | Routing | Content | Asks you? |
|---|---|---|---|
| [`read_file`](#read_file) | `path`, `path_ref` | — | only to trust a quarantined file |
| [`list_files`](#list_files) | `directory`, `pattern` | — | no |
| [`search`](#search) | `directory`, `include` | `pattern` | no |
| [`write_file`](#write_file) | `path`, `path_ref` | `contents`, `contents_ref` | **yes, every time** |
| [`edit_file`](#edit_file) | `path`, `path_ref` | `old_text`, `new_text` | **yes, every time** |
| [`run`](#run) | `program`, `args` | stdin | **yes, unless vouched for** |
| [`read_output`](#read_output) | `ref` | — | **yes** |
| [`spawn_processor`](#spawn_processor) | `about` | `reads`, `instruction` | no |
| [`load_skill`](#load_skill) | `name` | — | no |
| [`ask_user`](#ask_user) | the questions | — | it *is* the question |
| [`todo_write`](#todo_write) | — | `todos` | no |

An unknown tool is reported to the planner rather than ignored.

There is **no shell tool**, and there never will be. See [Shell mode](../using/shell-mode.md).

---

## `read_file`

Reads a UTF-8 text file from the workspace and returns its lines.

| Parameter | |
|---|---|
| `path` | workspace-relative path |
| `path_ref` | a reference to a file whose name the planner was not shown, e.g. `ref:2` |
| `offset` | 1-based line to start at |
| `limit` | maximum lines to return, capped so one read cannot fill the conversation |

Long files come back one page at a time, and the result says so and gives the offset to continue from.
A file that is not text is reported as binary.

**A read the planner may not see does not open the file.** Where the content would be quarantined, you
are offered the chance to vouch for that one file at the moment it matters — see
[the quarantined-read prompt](../security/trust.md#the-quarantined-read-prompt).

## `list_files`

Lists files under a directory, recursively.

| Parameter | |
|---|---|
| `directory` | workspace-relative; `.` for the root |
| `pattern` | optional glob: `*`, `?` and `**` are supported, brace groups are not |

A filename is content, so a listing of a directory nobody vouched for is quarantined — and it returns
**one reference per entry**, not one for the listing. That is what lets the planner read a file,
process it and write it back without ever being told what it is called.

The glob is literal and the matcher does not backtrack. A truncated listing says it was truncated.

## `search`

Finds a **literal substring** in workspace files, and returns matching lines.

| Parameter | |
|---|---|
| `pattern` | literal text; **not** a regular expression |
| `directory` | workspace-relative, defaults to `.` |
| `include` | optional glob limiting which files are searched |

A result touching several files is trusted only if **every one of them** is. A truncated search tells
the planner it is incomplete, and a search that found nothing for a pattern written as a regular
expression says so, rather than letting the planner conclude the text is absent.

## `write_file`

Writes a UTF-8 text file in the workspace. **You approve every write before it happens.**

| Parameter | |
|---|---|
| `path` | workspace-relative destination |
| `path_ref` | a reference to the file to write, for a file the planner was never shown the name of |
| `contents` | the complete new contents |
| `contents_ref` | a reference whose quarantined content becomes the whole file |

Contents **or** a reference, never both. A reference that names no file is not a destination. The
planner never chooses a destination on its own, and a write through a `path_ref` is always shown,
since you are the only one who sees which file it is.

See [Trusted directories](../security/trust.md#what-a-write-does) for what a write does to the trust
map.

## `edit_file`

Replaces an exact passage in an existing file. **You approve every edit, as a diff** — which is why
the agent prefers this to rewriting a whole body.

| Parameter | |
|---|---|
| `path` / `path_ref` | the file |
| `old_text` | the exact text to replace, matched byte for byte |
| `new_text` | what goes in its place |
| `replace_all` | replace every occurrence instead of requiring exactly one |

An edit **refuses rather than guesses**: `old_text` must occur exactly once unless `replace_all` is
set.

An edit requires a **trusted** file. Locating a passage to replace is a comparison, and a comparison is
a decision — which may be taken only from trusted content. To change a file the agent may not read,
the route is `spawn_processor` plus `write_file`.

## `run`

Runs a program. **You approve the exact argv before anything runs.**

```json
{"pipeline": [
  {"program": "git", "args": ["log", "--oneline", "-50"]},
  {"program": "sed", "args": ["-n", "1,10p"]}
]}
```

Each stage's output feeds the next. **There is no shell**: no pipes, no redirection, no `&&`, no
`$(...)`. A `;` or `|` inside an argument is part of that argument and nothing splits it. Narrowing
output is a stage, not a pipe character.

A name is looked up on `PATH`; a path is taken relative to the workspace. `args` is what comes *after*
the program — there is no `argv[0]` to repeat.

**The planner is not shown the output.** It comes back as a reference, like a file it may not read,
and can be passed to `spawn_processor` or written to a file with `write_file`.

| | Label |
|---|---|
| program and arguments | `(T,pub)` — a person approves the exact argv |
| standard input | may be untrusted; a person approves when it is private |
| standard output and error | `(U,priv)` — quarantined |
| …for a command a person vouched for | `(T,priv)` |

Stdin is content: the planner names a quarantined reference and the policy layer supplies the bytes,
so `sed` and `awk` work on a file nobody vouched for without the planner or the driver ever reading
it. A stage that reads stdin and was given none receives nothing, never the terminal.

### What a program is handed

A stage gets the environment bravebot is running in, **less the credentials bravebot authenticates to
its own backend with** — `SERVICES_KEY_AICHAT` and `BRAVE_SERVICES_KEY_ID`. Every stage, not only the
first, and removed rather than blanked, so a program that tells an unset variable from an empty one
sees what a machine that never held the credential sees.

You approve the argv, the resolved binary and the directory. The environment is not among those, so a
credential travelling alongside them would be handed over without your ever having seen it, and "run
`git log`" would be approved as an inspection of the repository.

**The rest of your environment stays, and that is not an oversight.** `run aws s3 ls` and `run gh pr
list` are ordinary requests, and no rule matching variable names can tell one of those from an
exfiltration, so `AWS_PROFILE`, `GITHUB_TOKEN` and `NPM_TOKEN` are left where they are. What the run
prompt tells you about the remainder is the truth: a run has the access your own shell has. Anything
of your own you want withheld can be named in
[`run.scrubEnv`](../customize/configuration.md#runscrubenv).

:::note
**This is not confinement.** A program that reaches the network is unpoliced and can send anything it
can read — a file, the workspace, a credential of your own. What closes here is the narrow part of the
gap: the credentials you could not have been shown at the prompt and had no way to withhold. Nothing
is established about what the program then does, and the label on its output is unaffected.
:::

A line you typed yourself in [shell mode](../using/shell-mode.md) is not this and keeps your whole
environment, since it is meant to behave as your own terminal does.

### A pipeline has five minutes

Every pipeline is given 300 seconds. When that runs out the stages are killed, and **what they
printed before that comes back exactly as it would from a pipeline that ended on its own**, under
the same label — reaching the limit ends a run rather than failing it. So a program that never
exits, like a server told to serve a page, still gives you everything it printed. How long the run
took comes back with the output, which is how you tell the two apart.

Finishing inside the limit says nothing about what a program did, and being cut short neither
raises nor lowers the label on its output.

See [Vouching for a command](../security/permissions.md#vouching-for-a-command) for what `a` grants.

## `read_output`

Asks to be shown what a command printed. You see the output and decide; if you agree, it comes back to
the planner as text.

| Parameter | |
|---|---|
| `ref` | the reference a `run` handed back |

This is why `which`, `find` and `uname` tell the planner nothing until it asks. It is an assertion
about bytes rather than a relabelling, and it works only for output from `run` — a quarantined *file*
is not readable this way.

## `spawn_processor`

Transforms quarantined content the planner was not shown.

| Parameter | |
|---|---|
| `reads` | the references to give it, e.g. `["ref:0", "ref:1"]` — at least one |
| `about` | which of those references this call is about; required when `reads` names more than one |
| `instruction` | what to do with them and what to produce |

Spawns an isolated model with no tools, no memory and nothing to read but the references named. Its
output is quarantined as a new reference, which the planner does not see either.

An answer is for **one** document and may be written **only** to the file the call was about. Where the
planner said nothing and there was more than one input, the answer belongs nowhere and may be written
nowhere.

Everything before the document marker in a processor's reply is a remark for you: it reaches your
screen and stops there, is part of no file, and cannot be another processor's input. An answer with no
marker names no document and can be written nowhere.

See [How Brave Bot works](../how-it-works.md#processors).

## `load_skill`

Reads one of the skills the planner was listed.

| Parameter | |
|---|---|
| `name` | the name exactly as it was listed, e.g. `commit-style` |

The name selects from a set fixed before the turn started and **never becomes a path**: a name holding
`../` matches nothing and the call is refused. A name close to a real one is refused rather than
guessed at. See [Skills](../customize/skills.md).

## `ask_user`

Puts up to four questions to you and waits.

| Parameter | |
|---|---|
| `questions` | at most four, each with a `header`, a `question`, optional `options`, and `multiple` |

Questions are put one at a time. You may choose an option, answer in your own words, or skip — and a
skipped question is an answer to work with rather than a reason to ask again. An answer is remembered
for the session, question by question.

Refused whole rather than trimmed if there are more than four.

**Asking stops once the planner's context has met something untrusted**, because at that point the
question itself could have been shaped by content nobody vouched for. A quarantined read does not stop
it asking, since a reference carries no instruction. Where nobody can be asked — a one-shot run — every
question is declined rather than answered on your behalf.

This tool is for what the planner cannot find out itself: which of two approaches, whether something
is in scope, which of two plausible files you meant. Never for a fact about the machine.

## `todo_write`

Records the task list for what the planner is doing.

| Parameter | |
|---|---|
| `todos` | the complete list, each with `content` and `status` |

The whole list every time — it replaces the previous one. There is no routing here, because nothing is
touched. An unrecognised status reads as outstanding work.

---

## Before adding a tool

The question asked of every new tool is: **what is its routing field?** A tool whose destination cannot
be separated from its payload does not belong on this surface. That is also why the built-in tools stay
native rather than arriving over MCP: an opaque call erases the split between the part that decides
where a call lands and the part that is merely carried, and these tools depend on it.
