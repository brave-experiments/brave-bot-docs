---
sidebar_position: 2
title: Approvals and permissions
description: Every moment the system stops and asks you something, and exactly what your answer grants.
---

# Approvals and permissions

Every consequential effect stops and puts something to you. This page is what each of those prompts
grants, and what it does not.

## A prompt shows what is at stake

Not a summary of it:

| Prompt | What it shows |
|---|---|
| a write | the path and the body |
| an overwrite | what it replaces |
| an edit | the diff |
| a run | the argv, the resolved binary and the directory |
| reading a command's output | the bytes, and the command that printed them |
| trusting a file | the path and its first lines |

You cannot endorse a destination you were not shown.

A prompt also says what approving **does**, and what it does not. The run prompt says the command is
not sandboxed, asks for the side effects and the output together, and names the exact command it would
vouch for. The trust prompt explains the consequence and names both answers.

## Content in a prompt is still untrusted

An untrusted body is marked as such, and command output is drawn inside a margin it cannot forge. The
margin is on every drawn row, not every line of content, so a line wider than the box is broken to the
width by the same step that draws the margin and each row carries a bar of its own.

A review stays legible or says it could not: a long body keeps the question on screen and offers the
rest to scroll to, a small edit in a large file shows only the change, an empty output says so, and a
diff that cannot be computed says so rather than showing nothing.

## One answer is never taken for another

An approved write does not approve a run. A write approval is not an answer to a question, and an
answer to a question is not consent to a write. **Each endorsement is single-use and bound to the exact
value it was given for.** These are separate grants that happen to use the same keyboard.

## Declining is not cancelling

Saying no to a write does not stop the turn — the agent carries on and can try something else. That is
how you steer without starting over.

**Ctrl-C refuses and stops.** Declining, and Ctrl-C, vouch for nothing.

## Vouching for a command

The run prompt is the one place a standing permission is offered:

```
  y run it    a always    n don't    ctrl-c stop the turn
```

`a` grants two things together, and the prompt asks for both:

1. **the command runs again unasked**, side effects and all;
2. **what it prints becomes trusted**, so the planner reads it instead of a reference.

The second is a human assertion, not an inference. Nothing establishes that a vouched command is
side-effect-free or that its output is free of influence, and nothing tries — `git log` prints commit
messages whoever contributed wrote. It is trusted for exactly the reason a directory in the trust map
is trusted: you said so.

An entry is keyed by **resolved path and exact arguments**. `git log` says nothing about `git push`,
and nothing about `git log --all`. `$PATH` and aliases decide what a name means, so an assertion never
follows a name onto a different binary. In a pipeline, *every* stage must be vouched for or the whole
output is untrusted.

Every run asks unless every stage was vouched for. There is no read-only category: `foo --bar` might
write to disk and nothing here can tell, and a stage declaring itself harmless only helps if the
declaration is honest. An unprompted write is worse than an unwanted prompt.

**Private input asks every time**, whatever is vouched for, and `a` is not offered for those runs at
all. Untrusted input is fine, since carrying bytes decides nothing — but private input hands your data
to a program, and that releases it somewhere this policy stops governing. Vouching for what a file
contains is not consenting to send it somewhere.

:::note
The vouched-for list is **not an allowlist** and must never become one. It never decides what may run:
a command nobody vouched for still runs after a prompt, nothing is refused for being absent, and the
set is empty at the start of every session. What holds is the label on the output, not a belief about
the binary.
:::

Programs are not confined. They run with the access your own shell would give them, because `git push`
needs `~/.ssh` and the set of programs someone might ask for cannot be listed in advance. The one
exception is bravebot's **own** credentials, which are withheld from every program it runs: you
approve an argv, never an environment, so a credential travelling alongside one would be handed over
without your having seen it. See [`run`](../reference/tools.md#what-a-program-is-handed).

## Rules you write down in advance

The `permissions` block of `~/.bravebot/settings.json` holds three lists — `deny`, `ask` and `allow` —
saying which actions to refuse outright and which to stop and ask you about. They are the same three
lists Claude Code keeps, with the same spellings, so a block copied out of `~/.claude/settings.json`
governs bravebot unedited. See
[Configuration](../customize/configuration.md#permissions) for how a rule is written.

**A rule decides whether you are asked, and whether an action happens at all. Nothing else.**

**A deny rule refuses before the file is opened or the program is looked for.** A denied file is not
read, not enumerated, not searched and not written, and a `Read` deny rule also stops a write to the
path it covers — a file whose contents are off limits is not protected if it can be overwritten.
Naming the path through a reference reaches the same refusal, including on the one route allowed to
read what nobody vouched for: a processor is handed no denied file either. The planner is told the
rule refused and that retrying is not the answer.

A deny rule also holds against **a workspace you trusted**, which is what makes one worth writing:
saying yes at startup trusts the whole tree, and a rule is how one file is kept out of that answer
without declining the rest of it.

**An allow rule stops the asking and grants nothing else.** It does not make a command's output
trusted — output carries what it would have carried. Pressing `a` grants those two together because
you are looking at one command and can answer for both; a pattern covers commands nobody has read, so
it cannot carry the second claim. If a rule could trust output, one line in a settings file would turn
fetched bytes into routing, which is the whole thing labels exist to prevent. Nor does an allow rule
extend reach: it cannot open a path the workspace and the directories you opened do not already cover.

**Two prompts no rule can answer.** A run that would put your private data into a program asks
whatever the rules say, because a rule saying which commands may run is not consent to hand one your
data. A write whose destination is known only through a reference asks too: that prompt is the only
moment such a path is shown to anybody, so nothing a pattern says can stand in for having looked.

:::note
**A `deny` list is not a sandbox.** A rule is matched against a program's argv rather than against
what the program then does, so `Bash(git *)` covers `git -c core.fsmonitor=<script> diff`, which runs
a program the rule never named. And a path rule does not reach a program's own file access at all:
`run cat .env` is checked against the `Bash` rules and against the run prompt, not against a `Read`
rule covering `.env`. What confines a process is [confinement](security.md#confinement); what holds
regardless is the label on the output.
:::

## What survives, and what does not

Two grants are standing, and both are written into the session record and restored by `--resume`,
because the person resuming is the person who gave them:

- the [trust map](trust.md);
- the list of commands you said to stop asking about.

**Nothing else survives.** A single-use endorsement is created by one approval, is bound to one value,
and is never written down, so a resumed turn cannot replay a write or a run an earlier turn was
allowed. Answers to the planner's own questions are remembered only in the live session.

A fresh session in the same directory restores neither and asks again.

## Reading permissions back

```
/status
```

lists the trust rules in force and the commands that now run unasked. Every other prompt in a session
announces itself by appearing; this is the one that stops appearing, so `/status` is the only thing
that can tell you a command now runs unasked and that its output is being read as trusted.

## When the planner asks you something

The `ask_user` tool puts up to four questions to you, one at a time, with options to choose from — and
you can always answer in your own words, or skip.

An answer is trusted as a first label, and only for a trustworthy question. **Asking stops once the
planner's context has met something untrusted**, because at that point the question itself could have
been shaped by content nobody vouched for. A quarantined read does not stop the planner asking, since
a reference carries no instruction.

Skipping is an answer to work with rather than a reason to ask again, and an answer is remembered for
the session, question by question.

## Where nobody can be asked

A one-shot run refuses effects rather than applying them unseen, and declines every question rather
than inventing an answer. See [Non-interactive use](../using/headless.md).
