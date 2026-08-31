---
sidebar_position: 3
title: Shell mode
description: Type `!` on an empty prompt to run a line in your own shell, and have its output reach the model in full.
---

# Shell mode

Type `!` on an empty prompt and the line becomes a command for your own shell.

```
! cargo test
! git log --oneline -20 | head
! ls build/*.o
```

The line goes to `$SHELL -c`, so globs, `$VAR`, redirection, `&&` and `$(...)` all work exactly as
they do in your terminal. `$SHELL` falls back to a POSIX shell when it is unset. An empty line is not
run.

The `!` is a mode rather than a character: the prompt changes colour, Backspace or Escape leaves it,
and the mode lasts one command.

## Nothing asks

`! rm -rf build` simply runs. The approval prompt exists so that a person endorses argv the
*planner* proposed — here you are the person it would have asked, so confirming your own keystroke
would be theatre.

## The output reaches the model in full

This is the difference from a program the planner ran itself. After `! cargo test` you can say "fix
the first failure" and the planner has already read the errors — the output is trusted and private,
not a reference. Output from a *failing* command reaches it too, since that is where the explanation
is. A cancelled command records nothing.

The label is a first label from provenance, exactly like the label on a program's output or on your
own configuration. It is admissible for the reason a vouched-for command's output is: a person took
responsibility, and nothing inspected anything.

## Only a line a human typed

Shell mode is reachable from one place — a key press in the input box — and nowhere else. Never argv
the planner proposed, never text read from a file, never anything a processor produced, never a line
reconstructed from a transcript.

**The planner gets no shell tool, ever.** Not behind a capability, not behind an approval prompt, not
via MCP. If it could ask for one, everything above is void. What it gets instead is
[`run`](../reference/tools.md#run), which takes a pipeline of argv stages and never a command string.

## The cost, stated plainly

`! cat notes-from-a-stranger.md` puts somebody else's words into the planner's context as though they
were yours. Nothing inspects the bytes to catch that, exactly as nothing inspects a directory that
was vouched for.

It is the same assertion you make by vouching for a command at a run prompt, made once for one
command. **If you would not press `a` for it, ask the agent to `run` it instead** and have the output
quarantined.
