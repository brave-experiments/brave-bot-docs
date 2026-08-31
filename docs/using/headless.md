---
sidebar_position: 6
title: Non-interactive use
description: One-shot tasks, piped input, and what changes when there is nobody to ask.
---

# Non-interactive use

```sh
bravebot "what does src/main.rs do?"          # one-shot
bravebot "explain this" --file notes.md       # with named context
bravebot -p "summarise this" < build.log      # with piped input
gh pr diff | bravebot -p "review this"        # the same, from a pipe
```

A one-shot run has nobody to ask, and most of what makes it different follows from that.

## Nothing is approved

**Where nobody can be asked, nothing is approved.** Effects are refused rather than applied unseen,
and the planner's own questions are declined rather than answered on your behalf.

The alternative to a person is not a default — it is a guess made in their name. The planner is told
that a reply came from a person, so inventing one would be worse than not asking at all.

So a one-shot run is for reading, explaining and summarising. If you want it to change something, run
it interactively.

## Piped input is untrusted and private, always

Nothing vouched for what a pipe carries. `gh pr diff` and `cat build-error.txt` both arrive the same
way and neither passed through the trust map, and a pipe has no path for the trust map to have an
opinion about. So piped bytes are quarantined, and the planner is given a reference rather than the
bytes.

That is not a dead end: the planner can pass the reference to a processor, feed it to a program's
stdin, or write it to a file — it simply cannot read it. See
[How Brave Bot works](../how-it-works.md#quarantine-and-references).

To give the agent something it can *read*, name a file instead:

```sh
bravebot "summarise this" --file build.log
```

Stdin is read only when it is not a terminal, so an interactive invocation does not sit waiting for
input nobody is sending.

Input over 10 MiB is refused rather than truncated, and says to write it to a file and name that
instead: a silently shortened input is one the planner would answer about having seen part of.

## Stdout carries the reply and nothing else

Progress, errors and the audit trail all go to stderr, so a one-shot run is pipeable:

```sh
bravebot "list the public functions in src/lib.rs" > functions.txt
```

`--trace` puts the audit trail on stderr beside it: which gate checked what, the label every value
carried, and what was released.

```sh
bravebot "what does this do?" --file src/main.rs --trace 2> trail.txt
```

## Exit codes

A failure exits non-zero. A configuration error, a refused argument, and a turn that could not run
all fail rather than exiting successfully with an explanation on stdout.

## Flags

| Flag | What it does |
|---|---|
| `--file <path>` | include a workspace file as trusted context; repeatable |
| `-p`, `--print` | non-interactive; reads piped stdin as quarantined context |
| `--trace` | print the audit trail to stderr |

The full set is in the [CLI reference](../reference/cli.md).
