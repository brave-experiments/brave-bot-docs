---
sidebar_position: 2
title: Slash commands
description: The nine commands the interface acts on itself, and the rules every one of them shares.
---

# Slash commands

A line beginning with `/` is acted on by the interface itself, in place of being sent anywhere.

| Command | Argument | What it does |
|---|---|---|
| `/status` | | Report this session, what it may touch, and what it has spent |
| `/model` | | Choose which model to think with |
| `/theme` | `[name]` | Choose the palette the interface is painted in |
| `/add-dir` | `<path>` | Open another directory, and trust it for this session |
| `/loop` | `[interval] <prompt>` | Send one prompt again and again until you stop it |
| `/rename` | `<name>` | Call this conversation something else |
| `/compact` | | Summarise the conversation so far, keeping the recent part |
| `/clear` | | Start a new session here, keeping this one resumable |
| `/exit` | | Leave |

Typing `/` offers the list, and Tab completes.

## `/status`

Everything the session knows about itself:

- the working directory, and anything opened with `/add-dir`;
- the model in force, and whether it was chosen or defaulted — with the model that actually answered
  shown beside it where the server substituted a different one;
- which deployment the endpoint names, and **which tier the last turn ran on**, rather than which
  tier the build was compiled to reach;
- the confinement available here;
- turns and tokens spent;
- **every trust rule in force**, listed in full, each marked trusted or untrusted;
- **every command you vouched for**, which now run unasked and whose output is read as trusted;
- what a [`/loop`](#loop-interval-prompt) is repeating and when the next tick is due, where one is
  running — what happens next without anybody typing anything being the one thing about a session that
  cannot be read off the transcript.

The last two are the point. Every other prompt in a session announces itself by appearing; a vouched
command is the one that stops appearing, so without this there would be nothing to tell you it now
runs unasked.

`/status` deliberately leaves out the endpoint host and the key id, though `bravebot doctor` prints
both. A status panel is the thing people paste into an issue or a screenshot.

## `/model`

Opens a picker on the model in use. The list comes from the endpoint rather than a set compiled in, so
it is whatever the backend offers today, and the choice is written to `~/.bravebot` — it outlives the
session and applies in every directory.

Typing narrows the list rather than walking it, and rows are grouped under the service that answers
them. See [Configuration](../customize/configuration.md#choosing-a-model).

## `/theme [name]`

Opens a picker on the palette in force. Up and Down move the cursor, and the theme under it is put in
force while it is selected, so you are comparing themes against your own transcript rather than
against a sample. Enter keeps the one on the cursor and Escape restores the one that was in force when
the picker opened. With a name, `/theme nord` applies it without opening the panel.

The choice is written to `~/.bravebot`, so it outlives the session and applies in every directory.
Themes of your own are JSON files under `~/.bravebot/themes/`, and nothing in a workspace is read. See
[Choosing a theme](../customize/configuration.md#choosing-a-theme) and
[Themes](../using/transcript.md#themes).

## `/add-dir <path>`

Makes a directory both reachable and trusted, for this session. `--resume` carries both halves and
`/clear` closes it. A directory already inside the project is refused. See
[Trusted directories](../security/trust.md#add-dir).

An added directory contributes **no** standing instructions and no skills, whatever it contains.

## `/loop [interval] <prompt>`

Sends one prompt again and again until you stop it.

```
/loop 5m check the deploy          # now, and every five minutes
/loop check the deploy every 20m   # the same, written the other way round
/loop watch the build              # now, and each turn says when the next is due
```

An interval is read off the front of the argument, or off an `every` clause at the end, in that order
and nowhere else. A leading token counts only when it is a number and one of `s`, `m`, `h` or `d`, and
a trailing clause only when a time expression is the whole of what follows `every` — which is what
keeps `/loop check every PR` a sentence rather than one with its last two words taken off. Given no
interval, each turn says when the next tick is due.

**The line a loop repeats is the one you typed.** It is settled the moment you press Enter and sent
unchanged for the life of the loop: nothing a turn reads, writes or returns can add to it, edit it or
replace it. A schedule a turn could write its next prompt into would be a turn rewriting its own
instructions, and the point of a loop is that it asks the same question again.

**A tick is a prompt, never a command.** `/loop 5m /status` sends the seven characters `/status` to
the planner every five minutes; it does not run the status command. A command is dispatched from a key
press, and a timer is not one.

The first tick goes at once, so you can see it happen while you are still watching and decide whether
it was the right thing to ask for. The gap is measured from the end of a tick rather than its start,
so `every 5m` means five minutes between runs. A due tick waits for an idle session and never
interrupts, and a prompt you type in the middle of a loop is not a tick of it.

| The wait | Shortest | Longest |
|---|---|---|
| an interval you gave | 5 seconds | 7 days |
| a delay a turn asked for | 1 minute | 1 hour |

A number outside those becomes the nearer bound, and you are told what it became rather than left
believing you are watching something ten times more closely than you are. A turn's number is held far
more tightly than yours because a turn that wants longer than an hour can say so in its answer, where
somebody reads it. Where you gave an interval, no turn can change it; a self-paced tick that says
nothing is woken once more twenty minutes later, and a second silence ends the loop.

Each tick is announced with its number, and with how many in a row have reported finding nothing —
which is the difference between a loop that is working and a loop with nothing to do. Four things end
one, and each says so:

| What | When |
|---|---|
| you interrupt | Ctrl-C, reached after the turn in flight and the half-typed line, and before leaving |
| a turn is stopped | any turn cancelled while a loop runs, tick or not |
| the session moves on | `/clear`, and leaving |
| age | seven days after it started |

**A loop is never written down.** It is not in the session record, so `--resume` restores none and it
does not outlive the process — a schedule that survived the session that set it would start sending
prompts at somebody who opened a conversation only to read it.

:::caution
**A loop keeps spending.** Every tick is a turn with the whole conversation re-sent, and nothing bounds
the total but the interval and the session's own life. A five-minute loop left open overnight is a
hundred and fifty turns nobody read.
:::

## `/rename <name>`

Renaming rewrites the session record immediately, and the chosen name survives the next turn. An empty
name is refused.

## `/compact`

Summarises the conversation so far and keeps the recent part, on demand, at any size, without
consulting the budget. The **request** is shortened, never the record: the replaced messages go to an
archive that the transcript still reads and the session record still stores. See
[Sessions](../using/sessions.md#long-conversations).

## `/clear`

Begins a new session in this directory and keeps the current one resumable. Because it is a new
session it asks the trust question again, restores no standing permissions, and closes any directory
`/add-dir` had opened.

## The rules every command shares

**Only a line a person typed into the box.** A command is dispatched from a key press and from nowhere
else: never a line the planner produced, never text read out of a file, never anything a processor
returned, never a line reconstructed from a transcript. A model that writes `/clear` has written four
characters, and they reach your screen as four characters.

Every command here decides something a turn is not allowed to decide on its own — which directories are
reachable, what the conversation consists of, which model thinks. The endorsement is the keystroke, so
the keystroke is the only thing that may produce one.

**The whole word, and an argument only after a space.** `/statusline` is not `/status`.

**In shell mode the line is a command line, not a command.** `! /usr/bin/env` runs a program.

**A command is never sent as a prompt.** A line that is a command is acted on and does not reach the
model.

**The argument is taken verbatim.**

**A command name is written in this program, never read from a directory.** There is no way to add one
by putting a file somewhere.

## Skills are not slash commands

Other agents let you type a skill's name after a slash. This one does not: a skill is advertised to
the planner by name and description, and its body is fetched by the planner asking for it. Nothing in
the input box knows skills exist, so `/commit-style` is a prompt like any other sentence. See
[Skills](../customize/skills.md#skills-are-not-slash-commands).

## Not a command, but typed in the same place

| | |
|---|---|
| `@<path>` | include a workspace file as trusted context — [Adding context](../using/context.md) |
| `!<line>` | run a line in your own shell — [Shell mode](../using/shell-mode.md) |
