---
sidebar_position: 1
title: CLI reference
description: Every command, flag and key bravebot takes.
---

# CLI reference

```
bravebot 0.4.0: a general-purpose agent resistant to prompt injection

Usage:
  bravebot                               Start an interactive session
  bravebot "<task>" [--file <path>]...   Run a single task
  cat file | bravebot -p "<task>"        ...with piped input, never trusted
  bravebot --resume [id]                 Pick up a session in this directory
  bravebot --continue                    Pick up the most recent session in this directory
  bravebot --fork <id>                   Fork a session and start exploring a different path
  bravebot doctor                        Check configuration and confinement
  bravebot import-leo-creds [channel]    Import a Leo Premium subscription
```

## Commands

| Command | What it does |
|---|---|
| `bravebot` | start an interactive session in the current directory |
| `bravebot "<task>"` | run one task and print the reply |
| `bravebot --resume`, `-r` | choose a session in this directory to pick up |
| `bravebot --resume <id>` | resume that session by id |
| `bravebot --continue`, `-c` | pick up the most recent session in this directory |
| `bravebot --fork <id>`, `-f` | copy a session into one of its own and open that, to try a second approach |
| `bravebot doctor` | report configuration and confinement, changing nothing |
| `bravebot import-leo-creds [channel]` | import a Leo Premium subscription |
| `bravebot --version`, `-V` | print the build |
| `bravebot --help`, `-h` | print this |

Anything that is not a recognised flag or subcommand is treated as the task prompt.

## Options

| Option | What it does |
|---|---|
| `--file <path>` | include a workspace file as **trusted** context; repeatable |
| `-p`, `--print` | non-interactive; reads piped stdin as quarantined context |
| `--mode <turn\|manifest>` | how a one-shot is run; `turn` (the default) decides step by step, `manifest` plans the whole run first |
| `--trace` | print the audit trail to stderr |
| `--incognito` | write nothing to `~/.bravebot`: no history, no session record, no preference |
| `--dangerously-skip-permissions` | bypass every permission check; recommended only for a sandbox with no internet access |
| `-h`, `--help` | show the help |
| `-V`, `--version` | show the version |

`-p` may lead, as it does for other agents: `bravebot -p "task"`.

`--incognito` may lead too, and combines with everything else here. See
[an incognito session](../using/sessions.md#a-session-that-leaves-nothing-behind).

`--dangerously-skip-permissions` may go anywhere in the line and combines with everything else too.
It is the only way to reach the mode that answers every permission question, including the ones that
decide trust, and the only way a run nobody is watching may write. See
[modes](../security/permissions.md#answering-in-advance-modes) for what it costs.

## `import-leo-creds`

```sh
bravebot import-leo-creds [stable|beta|nightly|development] [--forget]
```

Without a channel, `stable` is what importing means. `--forget` removes what was imported. See
[Leo Premium](../customize/premium.md).

## Interactive keys

| Key | What it does |
|---|---|
| Enter | Send |
| Shift-Enter, Ctrl-J | New line without sending |
| Ctrl-G | Compose in `$VISUAL` or `$EDITOR` |
| Ctrl-S | Stash the line, or bring back the stashed one |
| Ctrl-V | Paste, including screenshots |
| Shift-Tab | Choose how much the session asks before it acts |
| Ctrl-T | Toggle the audit trail |
| Ctrl-O | Open the scroller over the transcript |
| Ctrl-L | Watch what a delegate is doing, and read what a command printed |
| Up / Down | Walk back through sent prompts |
| Ctrl-R | Search every prompt you have sent |
| Wheel, PageUp / PageDown | Scroll the transcript |
| Home / End | Jump to the start or the latest |
| Esc | Cancel a running turn, or clear the input |
| Ctrl-C | Stop the nearest thing; leave when there is nothing left |
| `?` | List every key, on an empty line |

The full behaviour is in [Interactive mode](../using/interactive-mode.md), and the scroller's own keys
are in [Reading the transcript](../using/transcript.md#the-scroller).

## Interactive commands

| Command | What it does |
|---|---|
| `/status` | Report this session, what it may touch, and what it has spent |
| `/model` | Choose which model to think with |
| `/theme [name]` | Choose the palette the interface is painted in |
| `/effort [level]` | Choose how hard to think before answering |
| `/add-dir <path>` | Open another directory, and trust it for this session |
| `/cd <path>` | Work in another directory from now on, and trust it for this session |
| `/loop [interval] <prompt>` | Send one prompt again and again until you stop it |
| `/goal <condition>` | Keep working until a condition you set is judged met |
| `/rename <name>` | Call this conversation something else |
| `/compact` | Summarise the conversation so far, keeping the recent part |
| `/clear` | Start a new session here, keeping this one resumable |
| `/export [path]` | Write the transcript out as a markdown file |
| `/undo` | Rewind the last turn, on disk and in the conversation |
| `/exit` | Leave |
| `@<path>` | Include a workspace file as trusted context |
| `!<line>` | Run a line in your own shell |

See [Slash commands](commands.md).

## The version string

```
bravebot 0.4.0 (f2a6e1a, modified)
```

The commit is what the binary was compiled from, and `modified` means the tree had uncommitted changes
at that point. A build with no git available says `(no git)` rather than naming a commit it cannot see.

Every session record carries the same string. That matters when reading a transcript back: a session
that behaved oddly is usually being read against code that has moved since.

## Exit codes

A failure exits non-zero: a configuration error, a refused argument, and a turn that could not run all
fail rather than exiting successfully with an explanation on stdout.

## Streams

Stdout carries the reply and nothing else. Progress, errors and the audit trail go to stderr, so a
one-shot run is pipeable.

## Limits

| | |
|---|---|
| piped input | 10 MiB, refused rather than truncated past that |
| a pasted picture | 10 MB |
| tool rounds in one turn | unbounded interactively; 200 for a one-shot or manifest run, after which the planner answers with what it has |
| context budget | the window your model advertises; 24,000 prompt tokens where it advertises none |
