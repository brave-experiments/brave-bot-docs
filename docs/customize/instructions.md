---
sidebar_position: 1
title: Instructions
description: AGENTS.md — standing instructions for a project or for every project.
---

# Instructions

Put standing instructions in `AGENTS.md` and they apply to every task in that directory.

```markdown
# AGENTS.md

Run `make check` before saying a change is done.
Prefer `edit_file` over rewriting a file.
Commit subjects are imperative; the body explains why, never what.
```

## The four sources

| File | Applies to |
|---|---|
| `~/.bravebot/AGENTS.md` | every project |
| `~/.bravebot/skills/<name>/SKILL.md` | every project |
| `<workspace>/AGENTS.md` | this project |
| `<workspace>/.bravebot/skills/<name>/SKILL.md` | this project |

And no others. There is **no search of parent directories** and no nested `AGENTS.md` — a rule that
walked upwards would pick up instructions from whatever happened to be above a project on this
machine, which is a different set of instructions on the next machine. A file at any other path is an
ordinary file, read only when something asks for it by name.

The two roots are spelled differently on purpose. Your own directory is already `.bravebot`, so its
skills sit directly beneath it; a project keeps its own out of the way in a dotted directory, rather
than at the root where `AGENTS.md` sits.

`~/.bravebot` is `.bravebot` inside the home directory the environment gives, and there is **no
fallback**. When there is no home, or the name is empty, everything kept there is simply absent —
nothing is guessed and no other location is tried. Daemons and containers run without a home, and
everything kept there is optional, so absence is a case to do without rather than a reason to refuse
to start.

## What wins

Sources are read least specific first, so the project has the last word. Your own directory is read
before the project, **both** `AGENTS.md` files are read and both reach the planner in that order, and
a project skill replaces a global one of the same name. It is the same "most specific wins" rule the
trust map uses for paths.

A habit carried between projects should hold until the project says otherwise. Shadowing by name
rather than merging is what lets a project override one skill without restating the rest.

A directory opened with `/add-dir` during a session adds **no** standing instructions and no skills,
whatever it contains. Opening a directory to read one file out of it should not change how every
later turn behaves.

## Where they end up

What is resolved goes into the **system prompt**, never into the conversation. A session running many
turns carries one copy of its instructions however long it runs, rather than a copy per turn crowding
out the task — and the planner does not read its own conventions as though a person had just said
them.

Sources are resolved afresh every turn, so editing `AGENTS.md` mid-session takes effect on the next
thing you send. A source that is not there is not an error: no `AGENTS.md`, no skills directory, no
user directory at all — each is the ordinary case and offers nothing.

## Trust

`~/.bravebot` is trusted **by provenance**: it is your own directory, on the same footing as the
configuration that picks the model and the endpoint. Putting a file there is the grant, and an empty
directory offers nothing.

A project's own `AGENTS.md` is different. It is workspace content, so it is read through the
[trust map](../security/trust.md) like any other file — which means it loads when you vouched for the
directory and is left out when you did not:

```
AGENTS.md was not loaded: this directory is not trusted
2 skills in .bravebot/skills were not loaded: this directory is not trusted
```

A source that fails the trusted-content gate is **dropped entirely, never quarantined**. A reference
to an instruction is no use to anyone: an instruction is either followed or absent, and one from a
directory nobody vouched for has to be absent.

What was skipped is counted, never named. A directory in an untrusted project can be given a name
that reads like an instruction, and that name would otherwise be on your screen as though the agent
had written it.

The notice is said when it is learned — before the first request goes out — rather than when the turn
ends, so a turn that fails or is cancelled has already told you what it was working without.
