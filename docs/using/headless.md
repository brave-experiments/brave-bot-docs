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

## Planning the whole run first

```sh
bravebot --mode manifest "collect every TODO comment into notes/todos.md"
```

The default, `--mode turn`, is what an unqualified `bravebot "task"` has always been: observe,
decide, act, and decide again after each thing it reads. `--mode manifest` decides **everything
first**. The planner emits a step list, that list is refused or frozen, and a driver walks it with
no model anywhere in the control path.

This is not a stricter policy — the gates are exactly the same ones. What changes is the scope of
the precommitment, from one turn to a whole run.

**A plan is a program, so every field in it is a decision.** The planner may write one only from a
context holding your task and the driver's own words, having been shown nothing else. A plan built
from anything an attacker wrote would be an attacker choosing the steps, and there is no repairing
that. So a plan that fails validation fails the run whole: nothing is half adopted, no step is
patched to make a plan usable, and **nothing re-plans** once a step has read something.

Where every effect will land is locked in before the first byte is read. Steps take their
destinations from that lock rather than from themselves, and the driver adds nothing — it cannot
insert, skip, reorder or invent a step.

### What a plan cannot use

- **`edit_file`**, because locating a passage means having read the file, and the planner has read
  nothing.
- **`todo_write`**, because the manifest is already the task list.
- **`run`, and any shell.** A command string is destination and payload at once.
- **Piped stdin**, which is refused rather than dropped: a pipe is observed context, and this mode
  does not observe before it plans. Name a workspace file with `--file` instead.

Everything a step produces is quarantined, whatever its label — there is no planner left to show it
to. The ways out of a step's result are a later processor, a write back into the workspace, and a
release the plan named in advance. Nothing widens that set while the run is going.

### What comes back

The plain-words goal, the proposed plan verbatim, the frozen steps, and what each one did. They
come back on success **and on failure** — an artefact is never dropped on the error path, and
inspecting one is never behind a flag. A plan that would not parse has no rendered form, so the
model's own words are the only thing left to look at, and those come back too.

A failed plan is printed on stderr even without `--trace`, because otherwise a one-line complaint
is all that survives of a document nobody can see. The plan never shares stdout with the reply.

An unknown mode name is refused rather than guessed: guessing wrong here would silently run the
mode you did not ask for.

## A one-shot turn is bounded

A one-shot run carries a limit of 200 rounds of tool calls, where an interactive turn carries none.
Nobody is watching an unattended loop, and nothing else would end it; interactively you can see what
a turn is doing and stop it mid-round. On the limiting round the planner is offered no tools and
told it has none left, so it answers with what it has.

The default is bounded because a default cannot know whether anybody is watching, and being wrong
that way is the cheaper mistake.

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
