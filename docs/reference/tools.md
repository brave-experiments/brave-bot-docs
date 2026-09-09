---
sidebar_position: 3
title: Tools
description: Every tool the model may call, what it takes, and what it is allowed to touch.
---

# Tools

There are thirteen tools, and no way to add another from a configuration file. Each one splits its
arguments into **routing**, the part that decides where the effect lands, and **content**, the part
that is merely carried.

| Tool | Routing | Content | Asks you? |
|---|---|---|---|
| [`read_file`](#read_file) | `path`, `path_ref` | none | only to trust a quarantined file |
| [`list_files`](#list_files) | `directory`, `pattern`, `depth` | none | no |
| [`search`](#search) | `pattern`, `directory`, `include` | none | no |
| [`write_file`](#write_file) | `path`, `path_ref` | `contents`, `contents_ref` | **yes, every time** |
| [`edit_file`](#edit_file) | `path`, `path_ref` | `old_text`, `new_text` | **yes, every time** |
| [`run`](#run) | `command`, compiled to a plan | stdin | **yes, unless vouched for** |
| [`read_output`](#read_output) | `ref` | none | **yes** |
| [`fetch_url`](#fetch_url) | `url` | none | **yes, unless a rule names the host** |
| [`spawn_processor`](#spawn_processor) | `about` | `reads`, `instruction` | no |
| [`spawn_agent`](#spawn_agent) | `kind` | `task`, `each` | not the call, but its writes and runs do |
| [`load_skill`](#load_skill) | `name` | none | no |
| [`ask_user`](#ask_user) | the questions | none | it *is* the question |
| [`todo_write`](#todo_write) | none | `todos` | no |

A fourteenth, [`schedule_next`](#schedule_next), is offered to a turn inside a self-paced
[`/loop`](commands.md#loop-interval-prompt) and to no other turn.

An unknown tool is reported to the planner rather than ignored.

There is **no shell tool**, and there never will be. Nothing the planner writes is handed to an
interpreter. [`run`](#run) takes a command line, and bravebot compiles it itself. See
[Shell mode](../using/shell-mode.md).

---

## `read_file`

Reads a UTF-8 text file from the workspace and returns its lines.

| Parameter | |
|---|---|
| `path` | workspace-relative path |
| `path_ref` | a reference to a file whose name the planner was not shown, e.g. `ref:2` |
| `offset` | 1-based line to start at |
| `limit` | maximum lines to return, capped so one read cannot fill the conversation |

Long files come back one page at a time. The result says so and gives the offset to continue from. A
file that is not text is reported as binary.

**A read the planner may not see does not open the file.** Where the content would be quarantined,
you are offered the chance to vouch for that one file at the moment it matters. See
[the quarantined-read prompt](../security/trust.md#the-quarantined-read-prompt).

## `list_files`

Lists files under a directory.

| Parameter | |
|---|---|
| `directory` | workspace-relative; `.` for the root |
| `pattern` | optional glob: `*`, `?` and `**` are supported, brace groups are not |
| `depth` | optional; how many directory levels below `directory` to walk, `1` being that directory and no further |

Set a `depth`. Without one the walk reaches every file underneath, which in a real repository is
thousands of paths. You pay for them in the planner's context, again on every round that resends it,
and again in each delegate handed the same question.

A **bounded** listing names the directories it did not descend into alongside the files, so what
comes back describes the shape of the tree. The pattern does not hide those directories: it says
which files are wanted, and a directory is where the answer might be rather than an answer.

A listing of a directory nobody vouched for is quarantined, because a filename is content. It returns
**one reference per entry**, not one for the listing. That is what lets the planner read a file,
process it and write it back without ever being told what it is called.

The glob is literal and the matcher does not backtrack. A truncated listing says it was truncated.

## `search`

Finds lines matching a **regular expression** in workspace files.

| Parameter | |
|---|---|
| `pattern` | a regular expression. May be a list, in which case a line matches if it matches any of them |
| `directory` | workspace-relative, defaults to `.` |
| `include` | optional glob limiting which files are searched: `*`, `?`, `**` and brace groups like `**/*.{cc,h,mm}` |
| `case_sensitive` | defaults to true |

Supported: literals, `.`, `*`, `+`, `?`, `|`, `(...)`, `[...]` with ranges and negation, `\d`, `\w`,
`\s` and their negations, `^`, `$`, `\b`, `\B`, and a backslash before a metacharacter to match it
literally.

Two things are absent. **Counted repetition** (`a{2,9}`) is not supported and `{` is an ordinary
character. **Backreferences** are not supported. Captures are never extracted, since a search reports
the whole line.

The engine does not backtrack, so a pattern like `(a+)+$` that is exponential elsewhere costs nothing
unusual here: matching is the line's length times the pattern's size, whatever the pattern. That bound
is why the two missing constructs are missing. Counted repetition nested twice multiplies the states a
short pattern expands to, and backreferences cannot be matched without backtracking.

A list of patterns is alternation, one more expression to try per line, so the work is the sum of the
patterns rather than a power of anything. A pattern that is too long or nested too deeply is refused.
Brace groups in `include` are expanded before the walk. Case is folded by the engine rather than by
lowercasing the pattern, which would turn `\D`, `\W` and `\S` into the classes they negate, and a line
is reported as written rather than as it was folded to match.

**Version control, build output, caches and vendored dependencies are not walked**, by name and
without reading anything to decide it. The project's own `.gitignore` is not consulted either: it
would decide what to walk from a file in the tree being walked, and a tree that can hide files from a
search can hide them from review.

A result touching several files is trusted only if **every one of them** is. A truncated search tells
the planner it is incomplete. A search that found nothing says which kind of nothing it is: no
matching lines in the files it read, or an `include` that selected no files at all. Those are
opposite facts, and drawn identically the planner reads one as the other. A glob leaning on syntax the
matcher does not have is named for the same reason.

## `write_file`

Writes a UTF-8 text file in the workspace. **You approve every write before it happens.**

| Parameter | |
|---|---|
| `path` | workspace-relative destination |
| `path_ref` | a reference to the file to write, for a file the planner was never shown the name of |
| `contents` | the complete new contents |
| `contents_ref` | a reference whose quarantined content becomes the whole file |

Contents **or** a reference, never both. A reference that names no file is not a destination. The
planner never chooses a destination on its own, and a write through a `path_ref` is always shown,
since you are the only one who sees which file it is.

See [Trusted directories](../security/trust.md#what-a-write-does) for what a write does to the trust
map.

## `edit_file`

Replaces an exact passage in an existing file. **You approve every edit, as a diff.** The agent
prefers this to rewriting a whole body.

| Parameter | |
|---|---|
| `path` / `path_ref` | the file |
| `old_text` | the exact text to replace, matched byte for byte |
| `new_text` | what goes in its place |
| `replace_all` | replace every occurrence instead of requiring exactly one |

`old_text` must occur exactly once unless `replace_all` is set. An edit **refuses rather than
guesses**.

An edit requires a **trusted** file, because locating a passage to replace is a decision and a
decision may be taken only from trusted content. To change a file the agent may not read, the route
is `spawn_processor` plus `write_file`.

## `run`

Runs a command line. **You approve the compiled plan before anything runs.**

| Parameter | |
|---|---|
| `command` | one command line; a newline is refused, since this is a line and not a script |

```
git log --oneline -50 | head -20
```

The line is **compiled, never interpreted**. No shell sees it at any point: bravebot's own grammar is
the only thing that reads it. What comes out is an ordered plan, each step a resolved binary and a
literal argument vector, together with every file the line would write. That plan is what runs. A
`;` or `|` inside quotes is part of an argument and stays part of it.

A name is looked up on `PATH`; a path is taken relative to the workspace.

### What the grammar takes

| | |
|---|---|
| pipelines and sequencing | <code>\|</code>, `&&`, <code>\|\|</code>, `;`, and `( … )` to group |
| redirection | `>`, `>>`, `<`, `2>`, `2>>`, `2>&1`, `&>`, each naming one literal file |
| patterns | `*`, `?`, `[…]`, `**` |
| brace expansion | `{a,b}`, `{1..9}` |
| home | a leading `~` |
| per-command environment | `NAME=literal cmd` |

Everything else is refused, as an error naming the part of the line that caused it, and **a refusal
runs nothing**. There is no falling back to a shell and no running the prefix that did compile.

| Refused | Why |
|---|---|
| `$(…)`, backticks | a command whose text is computed is a destination nobody saw |
| `$VAR`, `${…}` | the value is not in the line, so the plan is not in the line |
| `$((…))` | arithmetic needs an interpreter |
| `<(…)`, `>(…)` | the same, plus a file descriptor nobody named |
| `&` | backgrounding is a parameter of a call, not a token in a line |
| `<<`, `<<<` | a here-document is content, not syntax |
| `eval`, `source`, `.`, `exec`, `trap` | they put an interpreter back in the plan |
| `if`, `while`, `for`, `case`, `function` | control flow is a program |
| `!` | history expansion is text you typed reaching a line the planner wrote |

Quoted, every one of them is an ordinary argument: `'$HOME'` is six characters that reach the program
as one word.

### Your answer binds to the plan, not to the line

The prompt draws the plan: each step as the line wrote it, the binary that will actually run
underneath, the directory it runs in, and **every file the line would create or replace**, listed
rather than left to be worked out from the steps above. The line the planner wrote is shown above it
and marked as context. Compare the two to catch a compiler that read the line wrong, but the line is
not what you are agreeing to.

Two lines that compile alike are one thing to agree to. One approval cannot be reused for the same
steps joined differently, for the same steps writing somewhere else, or for the same steps in another
directory.

**Every branch is endorsed before anything runs.** `a && b` may run `b`, `a || b` may run `b`, and
`a ; b` will, so all of them are in the plan and all of them are approved up front. Nothing is put to
you part-way through a running line, where you could not tell what state the first half had left
behind.

### Patterns become the files they match

Expansion happens against the tree at approval time, so what you read at the prompt is the file list
rather than the pattern. A pattern matching nothing is an error rather than an argument passed
through unchanged. `**` steps over the directories a listing steps over, so it does not descend into
`.git` or `node_modules`.

Expansion is bounded in both directions: a word standing for more than 100 arguments is refused with
the count, and the walk gives up after 4,096 directories. An approval prompt nobody reads grants
everything and asks nothing.

### A redirection is a write

`> out.txt` is a file this line creates or truncates. It appears in the plan's write set, it is shown
at the prompt, and it takes every rule a write takes: the permission rules, the trust map's answer
for that path, and the confinement that keeps a write inside the workspace. `>>` is a write, `<` is a
read, and `2>&1` renames a stream and touches no file.

A target must compile to exactly one literal path. A pattern is refused even where it matches one
file today, because a destination worked out from what is on disk moves when the tree does, and the
plan would stop saying where the bytes go.

**A line that writes is put to you every time**, whatever you have vouched for. Vouching is keyed on
a program and its arguments, and a destination is neither, so a remembered command cannot pick one up
unseen.

### Something that wants a terminal is refused before it starts

`git rebase -i`, `git add -i`, an editor, a pager without `--no-pager`: refused when the line is
compiled, with the thing to do instead. The list is a convenience rather than a guarantee. Something
interactive that is not on it reaches [the time limit](#a-line-has-five-minutes) and comes back with
what it printed.

Standard input is empty, so a step that reads it gets nothing rather than the terminal.

### The output

| | Label |
|---|---|
| the plan (programs, arguments, and the files it writes) | `(T,pub)`, because a person approves the compiled plan |
| standard input | may be untrusted; a person approves when it is private |
| standard output and error | `(U,priv)`, quarantined |
| …for a line every step of which a person vouched for | `(T,priv)` |

**Output nobody vouched for is not shown to the planner.** It comes back as a reference, like a file
it may not read, and can be passed to `spawn_processor` or written to a file with `write_file`. It is
not capped, since none of it enters the conversation.

That result also tells the planner what would lift the quarantine: output comes back as text once a
person has vouched for every stage of the exact command, and a single file is read with `read_file`.
Only where a command produced it, so a quarantined *read* carries no advice about vouching for a
command nobody ran. Without that sentence a planner reads one quarantined result as proof that
programs are unreadable and stops running them, which is not what happened: the label is about who
answered for the command.

**Every result says how the run ended**, in front of what the program printed: that every step
exited zero, which step did not and with what code, or that the line outstayed
[its five minutes](#a-line-has-five-minutes) and was stopped. It is said for quarantined output too,
where the planner holds a reference it may not read. The verdict is read off the processes and the
clock, never out of a byte the program printed, so it is structure exactly as a line count is and
puts nothing in the planner's context that a program chose.

Output the planner **may** read comes back as text, capped at 16 KiB. Past the cap the head and the
tail are kept and the middle dropped, with a line in between saying how much went. The cap is on what
enters the conversation rather than on what the command printed, and the whole of it stays available
as a reference.

### What a program is handed

A step gets the environment bravebot is running in, **less the credentials bravebot authenticates to
its own backend with**: `SERVICES_KEY_AICHAT` and `BRAVE_SERVICES_KEY_ID`. Every step, not only the
first, and removed rather than blanked, so a program that tells an unset variable from an empty one
sees what a machine that never held the credential sees. You approve the plan, the resolved binaries
and the directory. The environment is not among them.

**The rest of your environment stays, and that is not an oversight.** `run aws s3 ls` and `run gh pr
list` are ordinary requests, and no rule matching variable names can tell one of those from an
exfiltration, so `AWS_PROFILE`, `GITHUB_TOKEN` and `NPM_TOKEN` are left where they are. What the run
prompt tells you about the remainder is the truth: a run has the access your own shell has. Name
anything of your own you want withheld in
[`run.scrubEnv`](../customize/configuration.md#runscrubenv).

:::note
**This is not confinement.** A program that reaches the network is unpoliced and can send anything it
can read: a file, the workspace, a credential of your own. What closes here is the narrow part of the
gap, the credentials you could not have been shown at the prompt and had no way to withhold. Nothing
is established about what the program then does, and the label on its output is unaffected.
:::

A line you typed yourself in [shell mode](../using/shell-mode.md) is not this and keeps your whole
environment, since it is meant to behave as your own terminal does.

### A line has five minutes

Every line is given 300 seconds. When that runs out the steps are killed, and **what they printed
before that comes back exactly as it would from a line that ended on its own**, under the same
label. Reaching the limit ends a run rather than failing it, so a program that never exits, like a
server told to serve a page, still gives you everything it printed. The result says it was stopped,
which is how you tell the two apart.

Being cut short neither raises nor lowers the label on the output. Finishing inside the limit says
nothing about what a program did.

See [Vouching for a command](../security/permissions.md#vouching-for-a-command) for what `a` grants.

## `read_output`

Asks to be shown what a command printed. You see the output and decide; if you agree, it comes back to
the planner as text.

| Parameter | |
|---|---|
| `ref` | the reference a `run` handed back |

It works only for output from `run`. A quarantined *file* is not readable this way. This is why
`which`, `find` and `uname` tell the planner nothing until it asks.

## `fetch_url`

Fetches an `http` or `https` URL. **You approve every fetch, unless a rule names the host.**

| Parameter | |
|---|---|
| `url` | the one URL to fetch |

**What comes back is quarantined however you answer.** The body is a reference: the planner may hand
it to [`spawn_processor`](#spawn_processor) or write it to a file with
[`write_file`](#write_file), and it cannot read it or be told what it says. A page saying "ignore
your previous instructions" says it to a processor with no tools.

There is no answer at this prompt that trusts a body, because approving a fetch is consent to talk to
a host and says nothing about what that host returns. `a` at a run prompt can trust output: you read
one command and answered for both its effect and what it printed. A host answers every later request
however it likes.

The prompt draws the URL, and on a line of its own the host it will reach. The host is read out of the
URL by the parser rather than taken from what the string looks like, so
`https://example.com@evil.test/` cannot name one site to somebody skimming it and reach another.

**Your answer is bound to that one URL and nothing is remembered.** The next fetch asks again, even
on the same host. Standing permission is a
[`WebFetch(domain:…)` rule](../customize/configuration.md#permissions) you wrote down in advance,
which is naming a host rather than answering a question about one page. See
[A fetch is approved one URL at a time](../security/permissions.md#a-fetch-is-approved-one-url-at-a-time).

**A redirect may not leave the approved host.** Every hop goes through the same gate, and a hop
elsewhere is refused unless a rule allows that host too, since the end of a redirect chain is
somewhere nobody was shown. That check applies only while a fetch is in flight: reaching the model
endpoint is this program operating rather than something a turn asked for, so a rule about a website
cannot stop bravebot talking to its own backend.

A body that is not valid UTF-8 is carried anyway rather than reported as an error, since nothing here
reads it. Bodies are size-capped, and a truncated one says so.

## `spawn_processor`

Transforms quarantined content the planner was not shown. It spawns an isolated model with no tools,
no memory and nothing to read but the references named. Its output is quarantined as a new reference,
which the planner does not see either.

| Parameter | |
|---|---|
| `reads` | the references to give it, e.g. `["ref:0", "ref:1"]`; at least one |
| `about` | which of those references this call is about; required when `reads` names more than one |
| `instruction` | what to do with them and what to produce |

An answer is for **one** document and may be written **only** to the file the call was about. Where the
planner said nothing and there was more than one input, the answer belongs nowhere and may be written
nowhere.

Everything before the document marker in a processor's reply is a remark for you: it reaches your
screen and stops there, is part of no file, and cannot be another processor's input. An answer with no
marker names no document and can be written nowhere.

See [How Brave Bot works](../how-it-works.md#processors).

## `spawn_agent`

Hands a sub-task to a [delegate](../how-it-works.md#delegates), a second planner with a narrower set
of capabilities, and gets back one report.

| Parameter | |
|---|---|
| `kind` | `reader`, `checker` or `worker` |
| `task` | the whole of what the delegate is told |
| `each` | optional; starts one delegate per entry, each told `task` followed by its own entry |

| Kind | Holds | For |
|---|---|---|
| `reader` | reading | finding something out |
| `checker` | reading, and running programs | finding out whether something works |
| `worker` | reading, running programs, and writing files | finishing a sub-task |

The call answers as soon as the delegate has been approved, so the planner has its round back while
the work goes on behind it, and what the delegate says arrives on its own later. Several delegates
can be going at once, each numbered in the order the turn started them, and every report says whose
work it describes.

A delegate holds its kind's capabilities **narrowed by its parent's**, so delegation redistributes
authority and never creates it, and a kind asking for more gets a delegate without it. The planner
supplies the task and nothing else. What a delegate is told about itself is a constant its kind
chose, so there is no sentence the planner can write that changes what a delegate *is* rather than
what it is doing.

**`each` fans one task out**, so the shared half is written once and only the differing part (one
path per entry, say) is repeated. Every delegate it starts is one like any other: it is approved on
its own, takes its own number, and holds its own copy of what you vouched for, so a fan-out is
several runs rather than one run several times. A call naming more than eight, or naming none, is
refused and starts nothing.

The delegate cannot see the conversation the task came from, so a task that leaves something out is a
delegate that never learns it. It cannot come back for more, since there is no channel to ask
along. A run whose own context has met something untrusted cannot delegate at all.

**Delegation saves context, never an approval.** Every write and every run a delegate makes reaches you
with its own single-use endorsement, so you see the path and the diff whoever proposed them. What you
vouched for inside one comes back to the session, because that answer was about your machine rather
than about the run that happened to be going.

Nothing but the report crosses back: the exchange, the tool results and the quarantine end with the
delegate, and a reference minted inside one names nothing afterwards. A delegate is offered neither
this tool nor [`ask_user`](#ask_user) nor a task list, so it cannot delegate again and puts no question
of its own to you. What it could not settle goes in the report, and the planner asks.

:::note
The confirmation for a write shows the path and the diff, as it always does, but it does not say that
a delegate rather than the turn is asking. With several running, reading only the prompt means
approving a change whose reason is one of the tasks you did not read.
:::

## `load_skill`

Reads one of the skills the planner was listed.

| Parameter | |
|---|---|
| `name` | the name exactly as it was listed, e.g. `commit-style` |

The name selects from a set fixed before the turn started and **never becomes a path**: a name holding
`../` matches nothing and the call is refused. A name close to a real one is refused rather than
guessed at. See [Skills](../customize/skills.md).

## `ask_user`

Puts up to four questions to you and waits. More than four is refused whole rather than trimmed.

| Parameter | |
|---|---|
| `questions` | at most four, each with a `header`, a `question`, optional `options`, and `multiple` |

Questions are put one at a time. You may choose an option, answer in your own words, or skip. A
skipped question is an answer to work with rather than a reason to ask again. An answer is remembered
for the session, question by question.

**Asking stops once the planner's context has met something untrusted**, because at that point the
question itself could have been shaped by content nobody vouched for. A quarantined read does not stop
it asking, since a reference carries no instruction. Where nobody can be asked, as in a one-shot run,
every question is declined rather than answered on your behalf.

This tool is for what the planner cannot find out itself: which of two approaches, whether something
is in scope, which of two plausible files you meant. Never for a fact about the machine.

## `todo_write`

Records the task list for what the planner is doing.

| Parameter | |
|---|---|
| `todos` | the complete list, each with `content` and `status` |

The whole list every time: it replaces the previous one. There is no routing here, because nothing is
touched. An unrecognised status reads as outstanding work.

## `schedule_next`

Says when a self-paced [`/loop`](commands.md#loop-interval-prompt) should run again. It is offered to
a tick of a self-paced loop and to nothing else; a call from any other turn is answered the way any
unoffered name is.

| Parameter | |
|---|---|
| `delay_seconds` | how long to wait; routing, and required |
| `noop` | whether this tick found anything; routing, and required |
| `reason` | what the turn is waiting on, in its own words; content |

**There is no argument for what the next run asks.** The prompt is the line you typed when you started
the loop, and it is sent again unchanged.

The wait is held between a minute and an hour **before** it is reported back, so the number the
planner is told is the number it is getting. A call missing the delay or the verdict is refused rather
than filled in, since the count of quiet ticks you are shown is built from the verdict. `reason`
reaches your screen and stops there.

---

## Before adding a tool

Every new tool must have a routing field. A tool whose destination cannot be separated from its
payload does not belong on this surface. That is also why the built-in tools stay native rather than
arriving over MCP: an opaque call erases the split between the part that decides where a call lands
and the part that is merely carried, and these tools depend on it.
