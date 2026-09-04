---
sidebar_position: 5
title: Sessions
description: What is kept between runs, how to pick a session back up, and what a resume restores.
---

# Sessions

A session belongs to the directory it ran in. Records live under `~/.bravebot/sessions`, one
directory per working directory, so the list worth seeing when you resume in one project is not the
list from another.

Each session is two files, named after a version 4 UUID:

| File | What it holds |
|---|---|
| `<id>.json` | the record: the conversation, what the picker shows, and what a resume needs |
| `<id>.audit.jsonl` | the trail, appended a turn at a time — one JSON object per line |

The name is random rather than counted or clocked, so two sessions cannot collide however many are
running, and it is opaque because the name gets printed on a screen and pasted into a command.

## Picking one back up

```sh
bravebot --resume          # choose from the sessions in this directory
bravebot --resume <id>     # name one outright
bravebot -r <id>           # the same
```

The list is sorted on what each record says it was last written, not by id.

**Leaving a session prints the command that resumes it**, after the terminal is handed back, so it
stays on the screen you are left looking at. A session that never wrote a record prints nothing.

### A manifest run is recorded, but cannot be continued

A [plan-then-execute run](headless.md#planning-the-whole-run-first) writes its goal, its proposed
plan, its frozen steps and what each one did into the record, finished or not. Its conversation is
empty, because a session is turns over one conversation and a manifest run has none.

So the picker marks the row and refuses Enter, rather than loading an empty session and asking the
model to carry on from nothing. Naming one on the command line prints what it produced, and still
does not continue it.

## What a resume restores

The conversation, the plan each turn was working to, what the session has spent, the branch it ran
on, and the **standing permissions its user granted**:

- the [trust map](../security/trust.md) — including any rule a write recorded, which is what stops a
  resumed turn reading back a file an earlier turn of the same session poisoned;
- the list of [commands you said to stop asking about](../security/permissions.md#vouching-for-a-command).

Nothing else survives. A single-use endorsement is created by one approval, is bound to one value and
is never written down, so a resumed turn cannot replay a write or a run an earlier turn was allowed.
Answers to the planner's own questions live only in the running session, so a resumed session asks
them again.

A resume does **not** ask the startup trust question, because the answer honoured is the one that
session's own user gave. A record from before maps were kept has none, and is asked about. Resuming a
session recorded by a different build says so, beside the note about a changed branch.

## What the record accounts for

The record keeps the model that answered and what **each turn** spent, alongside the total — so a
session with one turn that ran away can be told from one that was evenly expensive.

The name recorded is the one that **answered**, not the one you asked for, since an endpoint may
serve something other than the name it was given.

## What is never written down

**Nothing untrusted.** Every message in the record has already passed the gate that decides what the
planner may see, so what lands on disk is what the planner was allowed to hold — by construction
rather than by filtering. Quarantined content is not written at all, and the trail is labels and gate
names with no content in it.

The reason is direct: a record is read back into a later turn's context, so anything written that the
planner could not have held would enter that context on the next resume.

A pasted picture *is* written down, because it was never quarantined — it is part of your own
message, and a session that turned on a screenshot would be no use resumed without it.

## Naming a session

A session's title is the first line of what you asked, cut rather than mangled if it is long. A
prompt with nothing in it still has a title.

```
/rename dependency audit
```

Renaming rewrites the record immediately, and a chosen name survives the next turn. An empty name is
refused.

## Starting over

```
/clear
```

`/clear` begins a new session in the same directory and keeps the current one resumable. Because it
is a new session it asks the trust question again, restores no standing permissions, and closes any
directory `/add-dir` had opened.

## Prompt history

Up walks backwards from the most recent prompt and stops at the oldest; Down walks forwards again.
Leaving the newest entry puts back the half-written line you were on, so pressing Up out of curiosity
cannot destroy it. Submitting leaves the mode, and a prompt arriving while you browse does not shift
the view.

History persists across runs under `~/.bravebot/history` and is capped. Consecutive duplicates
collapse into one, and a prompt you cancelled is removed again.

## Long conversations

A conversation that grows past its token budget is **compacted**: an older stretch of it is replaced
by a summary, in the request only. The record and the transcript keep the whole thing — the replaced
messages go to an archive that both still read.

```
/compact
```

asks for that work on demand, at any size, without consulting the budget. See
[Configuration](../customize/configuration.md#context-budget) for the budget itself.

Compaction never touches three things: the quarantine, which holds the only copy of what a surviving
reference names; the reference counter, since a slot name handed out twice would collide; and the
context's integrity, since nothing here has un-read what the conversation read. The cut never lands
inside a round, so a call is never separated from its results.

## When it cannot be written down

A missing home directory, a full disk, a corrupt record, a stored time in the future: everything here
degrades to doing nothing. A session that cannot be written down still runs, one that cannot be read
is left out of the list, and a corrupt history reads as no history rather than as an error.

:::note
Two working directories can share a session store. The directory name is derived by mapping every
character outside a small set to `-`, which is lossy, so `/a/b`, `/a-b` and `/a b` all reduce to the
same name — and because a resume restores standing permissions, permissions granted in one of those
directories would be offered in another. This is
[a known bug](https://github.com/brave-experiments/brave-bot/issues), not a design decision.
:::
