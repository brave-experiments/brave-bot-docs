---
sidebar_position: 3
title: The audit trail
description: What is recorded about every decision the system makes, and how to read it.
---

# The audit trail

Every gate decision is recorded — allowed **or** refused. A trail that logged only what happened
would not answer "why did it not do the thing I asked", which is most of what anyone asks it.

## Reading it

| Where | How |
|---|---|
| in a session, live | **Ctrl-T** toggles the trail |
| a one-shot run | `--trace`, which puts it on stderr |
| after the fact | `~/.bravebot/sessions/<directory>/<id>.audit.jsonl` |

```sh
bravebot "what does this do?" --file src/main.rs --trace
```

## What a trail looks like

Reading a file in a trusted directory, where the content reaches the model:

```
ok      precommit: routing fields ["task"] fixed before any observation
ok      promote: read_file.path proposed by the model, confined and non-destructive
ok      file_read.path [routing] (T,pub)
observe file_read produced (T,priv)
ok      trust: notes.md read as trusted, from a trusted path
ok      render: read_file: content reshaped for presentation, still (T,priv)
ok      present: tool_result: notes.md is (T,priv), so the planner may read it
```

Three pieces of notation appear throughout:

- `(T,pub)` and `(U,priv)` are the **label** on a value: trusted or untrusted on the first axis,
  public or private on the second.
- `ref:N` is a **slot** holding content the planner is not allowed to read, so it is handed the
  reference instead of the bytes.
- `routing` marks the part of a call that **decides where it lands**, as opposed to the part that is
  merely carried.

A *gate* is a check that has to pass before anything consequential happens: content reaching the
model, a file being written, a program being run, a request leaving the process. Each one decides a
single question and refuses rather than warning, so there is no path to a consequence that does not go
through one.

## The trail holds no content

Every field is a gate name, a capability, a label, a path or a slot id. That is exactly why it can be
put on your screen and written to a file without any release, and it is what makes the record safe to
keep for a workspace nobody vouched for.

## Assertions are recorded as assertions

Vouching for the output of a command you typed, labelling your configuration, and admitting a pasted
picture are each written down, because each is a claim a **human** made rather than something the
system worked out. These are the points where trust enters from outside, and a trail that recorded
only what the system deduced would omit exactly the decisions somebody might later want to account
for.

## On disk

One JSON object per line, appended a turn at a time, so a line-oriented file can be read with whatever
is to hand:

```sh
jq -r 'select(.gate == "present")' ~/.bravebot/sessions/*/…​.audit.jsonl
```

The labels are spelled out in words rather than abbreviated, because a file read months later has no
legend beside it, and each event keeps the time it happened. The compact form suits a terminal, where
the reader has the legend in front of them; a file has a different reader.
