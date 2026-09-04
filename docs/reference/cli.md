---
sidebar_position: 1
title: CLI reference
description: Every command, flag and key bravebot takes.
---

# CLI reference

```
bravebot 0.1.0: a general-purpose agent resistant to prompt injection

Usage:
  bravebot                               Start an interactive session
  bravebot "<task>" [--file <path>]...   Run a single task
  cat file | bravebot -p "<task>"        ...with piped input, never trusted
  bravebot --resume [id]                 Pick up a session in this directory
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
| `--trace` | print the audit trail to stderr |
| `-h`, `--help` | show the help |
| `-V`, `--version` | show the version |

`-p` may lead, as it does for other agents: `bravebot -p "task"`.

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
| Ctrl-T | Toggle the audit trail |
| Ctrl-O | Open the scroller over the transcript |
| Up / Down | Walk back through sent prompts |
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
| `/add-dir <path>` | Open another directory, and trust it for this session |
| `/rename <name>` | Call this conversation something else |
| `/compact` | Summarise the conversation so far, keeping the recent part |
| `/clear` | Start a new session here, keeping this one resumable |
| `/exit` | Leave |
| `@<path>` | Include a workspace file as trusted context |
| `!<line>` | Run a line in your own shell |

See [Slash commands](commands.md).

## The version string

```
bravebot 0.1.0 (f2a6e1a, modified)
```

The commit is what the binary was compiled from, and `modified` means the tree had uncommitted changes
at that point. Every session record carries the same string, which matters when reading a transcript
back: a session that behaved oddly is usually being read against code that has moved since. A build
with no git available says `(no git)` rather than naming a commit it cannot see.

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
| default context budget | 24,000 prompt tokens before compaction |
