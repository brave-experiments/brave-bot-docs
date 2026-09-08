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
| `<workspace>/AGENTS.md`, else `CLAUDE.md`, else `.claude/CLAUDE.md` | this project |
| `<workspace>/.bravebot/skills/<name>/SKILL.md` | this project |

And no others. There is **no search of parent directories** and no nested instructions file — a rule
that walked upwards would pick up instructions from whatever happened to be above a project on this
machine, which is a different set of instructions on the next machine. A file at any other path is an
ordinary file, read only when something asks for it by name, or when the source points at it.

**The project's file is looked for under three names, and the first that exists is the one.** Not all
three: a repository holding two of them holds one set of instructions under two names, and reading
both would say everything twice in a system prompt that goes out afresh every request. More than one
name is read because more than one is in use, and a project that wrote its conventions down should
not have them ignored over the spelling.

### A file that only names another is followed

Repositories supporting several agents often keep one real document and point the other names at it.
An `AGENTS.md` holding nothing but

```markdown
Refer to canonical agent instructions in `.claude/CLAUDE.md`.
```

is followed to the file it names, which is what reaches the planner. Otherwise the agent is handed
the pointer, reads it, and spends a whole round trip learning what it was about to be given anyway.

**Length is the whole test**, and it is what keeps this safe: anything past 500 bytes is a document
that happens to cite other files, so it is read as itself and its citations are left alone. Following
the first name in a real conventions file would swap your instructions for whatever they mentioned in
passing.

Once, not twice — what the named file names in turn is not followed. The pointer is opened by the
same route as any other path, so [confinement](../security/security.md#confinement) and the trust map
decide whether it may be read at all, and a pointer naming something outside the workspace is refused
there.

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
