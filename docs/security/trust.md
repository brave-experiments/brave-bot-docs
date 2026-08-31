---
sidebar_position: 1
title: Trusted directories
description: The question at startup, every other way a path comes to be trusted, and how long an answer lasts.
---

# Trusted directories

At startup you are asked whether you trust the working directory.

- **Trust it** and a rule covering the whole tree is written, so ordinary work proceeds without a
  prompt for every edit.
- **Decline** and nothing is written, so nothing is trusted and every write is shown to you first.
- **Leaving at the question starts no session.**

That record is the **trust map**, and it is the thing every read and every write consults.

## Nothing is trusted until it is granted

An empty map trusts no path. Trust is granted by a person, and never inferred from silence, from a
path's shape, or from anything a model or a file said. That is what makes declining at startup mean
something — a default of trusted would make the answer decorative.

## How a path is matched

Rules are keyed by path prefix and matched by whole segments, and **the longest matching prefix
decides**. Both polarities are expressible, so a trusted tree may hold an untrusted subtree, which may
hold a trusted path again. Equivalent spellings of a path are one rule, and a later decision replaces
an earlier one.

That is what lets `@vendor/lib.js` be trusted inside a `vendor` you marked untrusted, without the
answer leaking to its siblings.

A rule is about a **path**, not about the files that were in it when the rule was made, and it is
consulted when a file is read rather than when the rule is written. A file that appears in a trusted
directory afterwards is therefore read as trusted, whoever put it there.

Relative and absolute rules are separate namespaces. A rule under the working directory decides
nothing about a directory opened by absolute path, and the reverse. The working directory's own rule
is the *empty* prefix, since every path in the project is named relative to it — match absolute paths
against that same map and answering yes at startup would silently vouch for every directory opened
later.

## What a write does

Every row here is exact. A write matching a row does what that row says and nothing else.

| data | destination | prompt? | effect on the map |
|---|---|---|---|
| trusted | trusted | no | unchanged |
| untrusted | trusted | **yes** | that path becomes untrusted |
| trusted | untrusted | no | that path becomes trusted |
| untrusted | untrusted | no | unchanged |
| either | never mentioned | **yes** | that path takes the data's trust |

A prompt here asks one question and only this one: **may this path stop being trusted?** That is the
only consequence a later step cannot undo, since a path recorded as untrusted can no longer be
examined or edited.

- **Writing trusted data never asks.** Trusted data means the turn observed nothing untrusted, so it
  holds no byte an attacker influenced, and the destination only ever gains trust.
- **Untrusted data into a trusted path must mark it untrusted.** This closes the round trip: written
  into a trusted tree and read back as trusted, untrusted bytes would launder injected text into
  trusted input, and the map would become a bypass for the gate it exists to support.
- **A path nobody has mentioned asks either way**, because there is no decision behind it yet, and the
  first write there is the moment to ask.

Reconciliation marks the exact path written, never the parent. One untrusted file does not taint its
siblings, and marking the parent would turn a single fetched page into a project nobody may edit.

## Every way a rule gets written

Each grants exactly one thing, and grants it because a person made a gesture — never because anything
inspected content.

| Gesture | What it grants |
|---|---|
| yes at the startup question | the whole working directory, for this session |
| [`@path`](../using/context.md#naming-a-file-path) or `--file` | that one file, for the rest of the session |
| [dropping a file](../using/context.md#dropping-a-file) | that one file, wherever on disk it is, plus reach to it |
| `/add-dir <path>` | that directory: reachable **and** trusted, for this session |
| yes at a quarantined read | that one path, for the rest of the session |

### The quarantined-read prompt

When a turn reads a file nobody has vouched for, you are shown the path and the first lines of it and
asked whether to trust it:

```
╭ let the model read this file? ────────────────────────────╮
│Trust game.js                                              │
│                                                           │
│  the model cannot read this file, so it is working blind  │
│  on it. Vouching lets it read this file for the rest of   │
│  this session, here and in every later read.              │
│                                                           │
│┃ const SPEED = 100;                                       │
│                                                           │
│  y trust it    n leave it quarantined    ctrl-c stop      │
╰───────────────────────────────────────────────────────────╯
```

Yes writes exactly the rule `@` would have written. It is asked once per path per turn, and only where
the read is quarantined. Declining leaves the file as it was and the turn carries on with a reference.

This is the map's own decision offered where it matters, not a second route to trusting content, so a
yes stays consistent for every later read.

### `/add-dir`

```
/add-dir ~/notes
```

records an absolute rule that does two things together: the directory becomes reachable, since an
absolute path is otherwise refused whatever the map says, and it is recorded as trusted. Either half
alone is no use — one leaves a rule about files nothing can open, the other a directory that prompts
on every edit.

It lasts the session, `--resume` carries both halves, and `/clear` closes it. A directory already
inside the project is refused. A directory a resume cannot open again, because it has moved or gone,
says so rather than being passed over.

## Reach stays confined

No rule extends reach. Reading, writing, editing, listing and searching are confined to the working
directory and to whatever `/add-dir` has opened. `..` and absolute paths outside those are refused
rather than resolved — in an added directory exactly as in the project — and a symlink leaving one is
refused. A relative path always means the project, so no file has two spellings.

## How long an answer lasts

**The map belongs to the session, not the directory.** Every session start asks, whatever any earlier
session in that directory answered. `/clear` begins a session and therefore asks.

`--resume` does not ask: it restores the map from the record of the session you chose, because the
answer honoured is the one that session's own user gave — and it carries the rules that session's
writes recorded, which is what stops a resumed turn reading back a file an earlier turn of the same
session poisoned.

The question grants standing permission. Honouring last week's answer would grant it on behalf of a
user who was never asked, and trust assumed from silence is not trust granted.

## Reading the map back

```
/status
```

lists every rule in force, so what a line vouched for does not have to be remembered.

## `~/.bravebot` is not governed by this

Your own directory is read as trusted **by provenance** rather than by any rule here, because the map
is keyed by workspace-relative paths and has nothing to say about a path outside the workspace. A
project's own files are *not* covered by that and are read through the map, whatever their names. See
[Instructions](../customize/instructions.md#trust).

## Known costs

Both of these are deliberate.

- **A fresh session forgets what an earlier one poisoned.** The rule that untrusted data marks its
  destination untrusted holds within a session and across a resume of it. Across a fresh start it
  cannot, because the map it was recorded in is gone. The alternative is a per-directory map, which is
  a directory that trusts itself. If a file holds content you do not trust, say no to the directory —
  or do not leave it there.

- **A file another process drops into a trusted directory is trusted.** A rule is about the path, so
  `npm install`, `git pull`, an editor, a background daemon, or a program the agent was allowed to run
  can all put a file inside a vouched-for tree and it will be read as trusted. This cannot be closed by
  watching the filesystem: by the time anything noticed, the question would be whether to distrust a
  file you may have created yourself, and asking that on every change would make the map useless.

  Said plainly: **trusting a directory trusts what lands in it**, so a tree that a build or a
  dependency manager writes into is a tree you are vouching for ahead of time.
