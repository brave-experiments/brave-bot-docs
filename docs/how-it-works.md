---
sidebar_position: 3
title: How Brave Bot works
description: The planner, the driver, labels, quarantine and processors.
---

# How Brave Bot works

Everything in Brave Bot is predicated on one statement:

> **Untrusted content never enters the driver's context or the planner's.**

The **planner** is the model deciding what to do next. The **driver** is the Rust code around it.
Both are held to the same rule, because moving a decision from one into the other does not remove
it.

## The two roles

| | What it is | What it may do with untrusted content |
|---|---|---|
| **Planner** | the model | never sees it — it is handed a reference instead |
| **Driver** | the program | may **carry** it and hand it to an effect, never **read** it |
| **Policy layer** | the gates inside the driver | the only code allowed to read untrusted bytes, and only at a gate |
| **Processor** | an isolated model call with no tools | reads it, rewrites it, and can direct nothing |

## Labels

Every value carries a label on two axes:

```
L = I × C      I ∈ {T, U}       trusted / untrusted
               C ∈ {pub, priv}  public  / private
```

Untrusted input degrades integrity. Private input raises confidentiality. `(U,priv)` and `(T,pub)`
are incomparable, so this is a lattice rather than a pair of booleans.

A derived value is labelled by taint over its inputs: one untrusted input taints the result, one
private input makes it private, the axes degrade independently and the order of the inputs does not
matter. **Labels only ever degrade.** Nothing constructs a label better than its inputs had, in any
crate — that is laundering, and if a value derived from untrusted input has to be trusted for
something to work, the design is wrong rather than the label.

A *first* label is different from an upgrade. Model output is a function of the model's context, so
when the context held only trusted input, what it produced is labelled accordingly. The same road
labels a program's output, a line you ran yourself in shell mode, your own configuration and a
picture you pasted. Each of those is a label a value receives for the first time, assigned from
provenance the policy layer tracked — never a relabelling of something that already had one.

## Quarantine and references

Untrusted content is never placed in a message to the model. It goes into a write-once slot and the
planner is given a **reference** instead:

```
ref:2  notes.md, 84 lines, 2.1 KiB, (U,priv)
```

The planner acts on content it cannot read by naming that reference, and the policy layer resolves
it when the write or the call actually happens. So the model can:

- read a file it may not see, by passing `path_ref` around;
- feed a quarantined file to a program's stdin, so `sed` and `awk` work on it;
- write quarantined content into a file with `contents_ref`;
- hand it to a processor to be changed.

What it cannot do is see the bytes, or take a decision from them.

## Processors

Where content has to be *changed* rather than moved, it goes to a processor: an isolated model call
with no tools, no memory and no conversation.

| | |
|---|---|
| Tools | none, and the request carries no tool list at all |
| Memory | none: the messages are built from nothing each time |
| Conversation | one request, one reply, no loop to steer |
| Reads | exactly the references it was given, and nothing else |
| Writes | at most one new reference, and nothing else |

A processor's answer is quarantined like anything else, and the planner never sees it either. The
output's label is computed **before** the processor runs, by taint over the inputs, so nothing it
writes has any say in how what it writes is labelled.

This is how a file the agent may not read still gets fixed: the planner names the file's reference,
says what has to be true of the file afterwards, and passes the reference that comes back to
`write_file` as `contents_ref`. You approve the write from the resulting diff.

A processor's answer is for **one** document, and may be written only to the file the planner said
the call was about. Everything before the document marker in its reply is a remark for the person
watching: it reaches your screen and stops there. No model reads it, it is part of no file, and it
cannot be another processor's input.

## Routing and content

Every effect splits in two:

- **Routing** — the part that decides where the effect lands: a path, a program name, its
  arguments, a URL. Routing must be `(T,pub)`, and must be endorsed by a person.
- **Content** — the part that is merely carried: a file body, a program's stdin, a request body.
  Content may be untrusted. It must not be private at the moment it is released.

This split is why the built-in tools are native rather than MCP calls: an opaque call erases the
distinction between the part that decides where something lands and the part that is carried, and
these tools depend on it.

It is also why the planner never gets a command line. `run` takes a pipeline of argv stages, so
`; rm -rf /` inside an argument is one argument and stays one — nothing splits it, because nothing
is passed to a shell.

## Gates

A gate is a check that has to pass before anything consequential happens: content reaching the
model, a file being written, a program being run, a request leaving the process. Each one decides a
single question and **refuses rather than warns**, so there is no path to a consequence that does
not go through one.

Every gate decision is recorded, allowed or refused, and the record holds no content — only gate
names, capabilities, labels, paths and slot ids. That is why it can be shown on your screen and
written to a file for a workspace nobody vouched for. See [The audit trail](security/audit-trail.md).

```
ok      precommit: routing fields ["task"] fixed before any observation
ok      promote: read_file.path proposed by the model, confined and non-destructive
ok      file_read.path [routing] (T,pub)
observe file_read produced (T,priv)
ok      trust: notes.md read as trusted, from a trusted path
ok      render: read_file: content reshaped for presentation, still (T,priv)
ok      present: tool_result: notes.md is (T,priv), so the planner may read it
```

## Where trust comes from

Nothing is trusted until a person grants it, and trust is never inferred from silence, from a
path's shape, or from anything a model or a file said. There are exactly a few gestures that grant
it, and each grants one thing:

| Gesture | What it grants |
|---|---|
| answering yes at startup | the working directory, for this session |
| `@path` in a prompt, or `--file` | that one file, for the rest of the session |
| dragging a file onto the terminal | that one file, wherever on disk it is |
| `/add-dir <path>` | that directory: reachable **and** trusted, for this session |
| answering yes at a quarantined read | that one path, for the rest of the session |
| `a` at a run prompt | that exact command: runs unasked, and its output is trusted |
| putting a file in `~/.bravebot` | trusted by provenance, as your own configuration |

Every one of them is a person's gesture. None of them is something the system worked out from
content. See [Trusted directories](security/trust.md).

## The limits of all this

Three things are worth saying plainly, because they are deliberate rather than oversights:

- **Trusting a directory trusts what lands in it.** A rule is about a path, not about the files that
  were there when the rule was made. `npm install`, `git pull`, your editor, or a program the agent
  was allowed to run can all put a file into a vouched-for tree, and it will be read as trusted.
- **A fresh session forgets what an earlier one poisoned.** The rule that untrusted data marks its
  destination untrusted holds within a session and across a resume of it, not across a fresh start.
- **A vouched-for command's output is trusted because you said so.** Nothing establishes that
  `git log` is free of influence — its output is whatever contributors wrote. It is trusted for the
  same reason a directory is: a person took responsibility.

Every one of these is written down in the specs under "Known costs", because an unlisted exception
is indistinguishable from a violation.
