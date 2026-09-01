---
sidebar_position: 1
title: Interactive mode
description: The input box, every key, and what a running turn refuses.
---

# Interactive mode

```sh
bravebot
```

The input box grows with what you type, up to ten rows, and then scrolls to the caret rather than
growing further. It keeps growing while a turn runs.

## Sending and editing

| Key | What it does |
|---|---|
| Enter | send |
| Shift-Enter, Ctrl-J | start a new line without sending |
| Ctrl-G | compose in `$VISUAL` or `$EDITOR` and take back what you saved |
| Escape | discard a half-typed prompt, or stop a running turn |
| Ctrl-C | stop the nearest thing there is to stop, and leave when there is nothing left |
| Up / Down | walk back through prompts you have sent |
| Tab | complete a slash command or an `@path` |
| `?` | on an empty line, list every key |

Enter on an empty line does nothing. Shift-Enter needs a terminal that reports the modifier
(Ghostty, Kitty, WezTerm) or one configured to send a newline; **Ctrl-J is the fallback that always
works**, in every terminal and in shell mode too.

## Composing in your editor

**Ctrl-G** opens your editor on what is already in the box, so it continues a prompt rather than
starting it again, and what you save replaces the line. It does nothing while a turn runs: handing
the terminal to an editor mid-turn would take the screen from the turn drawing on it.

Every path that does not end in a save ends in the line untouched. Quitting without saving leaves it
exactly as it was, and so does an editor that failed or was killed — neither says anything about what
you wanted, and the failure worth designing against is the one that blanks a paragraph you have just
written. The newline an editor leaves at the end is dropped, one only. The file it opened holds your
own words, is readable by nobody else, and does not outlive the edit.

Which editor opens: `$VISUAL`, then `$EDITOR`, then the first of `vim`, `vi`, `emacs`, `nano` that is
installed. An empty value is not an answer, since exporting a variable to nothing is how a profile
takes one back. `nano` is the last resort because somebody with `vim` or `emacs` on their machine
chose to install it and will not thank a guess for opening something else. An editor you named that
will not start is reported as such and nothing else is tried: falling back past it would run an
editor you did not ask for, and blame your configuration for it.

An editor is started under the name it was asked for, rather than under the file a symbolic link
behind that name points at. MacVim is why. It installs `vim`, `vi` and `gvim` as links to a single
program that reads the name it was called by, staying in the terminal for the `vi` spellings and
forking off a detached GUI window for the others; reached through the resolved path it is always the
GUI one, so asking for `vim` opened a window, returned at once, and put the prompt back unedited with
nothing saying why. The name is kept only while it still reaches the same program — a link that now
points elsewhere is started by resolved path instead.

That is the editor alone. Wherever a program is approved before it runs, the approval names the file
that actually ran, because a name can be repointed afterwards. An editor is started rather than
approved, and for it the name is part of what you asked for.

A GUI editor that would otherwise return the moment its window opens is told to wait, but only where
you wrote no arguments of your own.

## Looking up the keys

`?` on an empty line puts up every key and what it does. A second `?` takes the list down, as does
Escape, or typing anything at all. It is a mode rather than a character, the way `!` is: nothing
lands in the box, so there is nothing to delete afterwards.

Only on an empty line. A `?` part-way through a sentence is the punctuation you are asking a
question with, and in shell mode it is a glob for your shell to expand.

The list is not a completion — there is nothing in it to choose, so Tab and the arrows go on meaning
what they mean everywhere else while it is up. It folds into as many columns as the width holds, and
no row runs past the edge. It is the one place the keys are written down, which is what stops it
advertising a binding that has since changed.

The row beneath the box carries what the session is doing — the trail, the confinement, and how full
the context is — and then `? for shortcuts`. It names no binding of its own. The two used to share
one line, and the line was wider than the terminal, so the end of it was cut: everything you could
look up was taking room from the figures you had no other way to see. A binding cut off is one you
learn once, and a context reading cut off is gone.

## Stopping and leaving

Escape only ever stops, and never leaves. Ctrl-C is read against what is happening:

| What is happening | What Ctrl-C does |
|---|---|
| a turn in flight, or a command running | stops it, and the session stays where it was |
| nothing running, a line in the box | takes the line, and offers the way out |
| nothing running, an empty box | ends the session |

Taking the line says so, on the row beneath the box, and names the key that ends the session. That
offer lives for exactly one press.

Stopping is silent. A reply still arriving stops arriving, the prompt that was sent comes back to
the box for editing, and that is the whole of the answer — there is nothing to wait through. What
still finishes is a tool call already running, because stopping one part way could leave a file half
written.

The prompt stays in the transcript, marked stopped, rather than coming back to the box, when either
the turn had already done something visible or there are prompts waiting behind it. Both mean there
is an order to keep.

## Sending while a turn runs

Typing, editing, pasting, dropping a file, completing, walking back through earlier prompts and
scrolling the transcript all do exactly what they do at rest. **The only thing a running turn
refuses is sending.**

Enter mid-turn takes the line out of the box and holds it. It is drawn under the box, marked, so you
can see that what you sent went somewhere. Waiting prompts run in the order you typed them, one turn
each, as soon as the session is free. A waiting prompt is not in the transcript — it moves there
when its own turn begins.

What a queued prompt names is settled when it is queued, so a file you took off the line afterwards
was never part of it.

Stopping a turn leaves the queue alone: the next waiting prompt starts as it would after any turn.

## The rows beneath the box

They run in one order, nearest the box first:

1. what the line in the box carries — attached files and pictures;
2. prompts waiting for the turn in flight;
3. what a half-typed line could still become — slash-command or `@path` completions.

## Markers

A folded paste, a pasted picture and a dropped file each fold to a marker in the line, like
`[Pasted text #2 +40 lines]` or `[Image #1]`. A marker behaves as one thing:

- Backspace or Delete takes the whole marker in one press, and deleting it takes the attachment off.
- Left or Right crosses it whole; the caret never rests inside one.
- The caret is drawn over every cell of the marker it is on, including the part that wrapped.

Square brackets you typed yourself are still deleted a character at a time.

See [Adding context](context.md) for what each kind of attachment does.

## Slash commands and `@path`

Typing `/` offers the commands, and typing `@` opens a picker over the workspace with directories
first: a prefix narrows it, a slash descends, Tab completes without disturbing the rest of the
sentence, and version-control and build directories are not offered. Sending a prompt that ends in a
half-typed reference completes it rather than sending the fragment.

See [Slash commands](../reference/commands.md) and [Adding context](context.md).

## Reading back

Ctrl-O opens the scroller over the transcript, and Ctrl-T toggles the audit trail. See
[Reading the transcript](transcript.md) and [The audit trail](../security/audit-trail.md).

## Long turns

A turn may make 40 rounds of tool calls. On the fortieth the next request offers no tools and the
planner is told it has none left, so it answers with what it has. This is a bound on futility rather
than a safety property: a gate refuses on the thousandth round what it refuses on the first.
