---
name: update-docs
description:
  'Bring this documentation site up to date with brave-bot. Reads the recorded
  baseline in docs-updated-to-sha, reviews what has landed in brave-bot since,
  folds the missing behaviour into the pages it belongs on, then records the new
  baseline and commits it. Triggers on: update docs, /update-docs, make
  docs-changes, docs are out of date, sync docs with brave-bot, docs drift,
  bump the docs ref.'
argument-hint: '[rev] [--all] [dry-run]'
allowed-tools: Bash(python3 agents/skills/update-docs/*), Bash(make docs-changes*), Bash(make docs-updated-to-sha*), Bash(make build*), Bash(git*), Bash(grep*), Bash(rg*), Read
---

# Bring the docs up to date with brave-bot

[`docs-updated-to-sha`](../../../docs-updated-to-sha) records the brave-bot commit this site
was last updated to. This skill documents what landed since then, then moves that record
forward.

- **Default run**: everything that landed under `docs/` or `README.md` since the baseline.
- **Scoped run** (`/update-docs <rev>`): stop at `<rev>` instead of head. Use this to work
  through a long backlog in a few reviewable passes.
- `--all` also reviews commits that touched only code, for when a behaviour change landed
  without a spec.
- `dry-run` reports what would change and writes nothing.

Two files carry state between runs: `docs-updated-to-sha`, the commit the site is current
as of, and `docs-deferred`, the commits reviewed and postponed on purpose.

---

## Writing style

These rules apply to every page this skill writes or edits.

**BLUF. The answer goes first.** A section's first sentence states what happens. Conditions,
reasons, and exceptions come after it. Never build up to the point.

- **Never use an em dash or an en dash.** Use a period, a comma, a colon, or parentheses.
  If a sentence needs a dash to hold together, split it into two sentences.
- Plain English. Say what happens in the shortest sentence that is accurate.
- Short declarative sentences. Not long ones with clauses hanging off them.
- Describe how things are. Not how they came to be, or what was considered instead.
- No fluff. Cut any sentence the reader would not act on or be surprised by.
- No filler words: "simply", "of course", "essentially", "in order to", "it should be noted".
- No headings that only announce what follows. A heading earns its place if a reader would
  scan for it.
- Explain a rule's reason only when the rule limits what the reader can do.

---

## Direction of the update

brave-bot's specs are the source of truth. When this site and a spec disagree, this site is
wrong. Fix the page, not the spec.

This skill does not edit anything in the brave-bot repository. It reads that checkout and
writes only here. If a spec looks wrong, say so in the summary and leave it alone.

Do not invent behaviour. Every sentence added must trace to a clause or a commit in the span
being folded in. Report a gap the commits do not settle as an open question.

---

## What the script handles

`docs-ref.py` does the deterministic work:

```sh
python3 agents/skills/update-docs/docs-ref.py show              # where the docs stand
python3 agents/skills/update-docs/docs-ref.py changes           # commits to fold in
python3 agents/skills/update-docs/docs-ref.py changes --full    # with bodies and file lists
python3 agents/skills/update-docs/docs-ref.py set <rev>         # record a new baseline
python3 agents/skills/update-docs/docs-ref.py defer <rev> <why> # leave one for a later run
python3 agents/skills/update-docs/docs-ref.py resolve <rev>     # that one is now documented
```

`make docs-updated-to-sha` and `make docs-changes` run the first two.

The script finds the brave-bot checkout at `$BRAVE_BOT_REPO`, or at `../brave-bot` beside
this repository. If neither exists it says how to clone one. It reads brave-bot's
`origin/main` rather than whatever branch that checkout is on, so unmerged work is never
documented as shipped.

---

## The job

### 1. Establish the span

```sh
python3 agents/skills/update-docs/docs-ref.py show
```

If it says up to date, stop and say so.

Otherwise fetch first, so head means head:

```sh
git -C "${BRAVE_BOT_REPO:-../brave-bot}" fetch origin
```

Note the `new ref once folded in` sha that `changes` prints. The baseline moves to that value
at the end. It is fixed now: a commit that lands in brave-bot mid-run is not part of this pass.

### 2. Read what landed

```sh
python3 agents/skills/update-docs/docs-ref.py changes --full
```

Read the commit bodies. They explain why a behaviour changed and name the specs that moved.
Then read those specs at the new head, not at the baseline:

```sh
git -C ../brave-bot show <new-ref>:docs/specs/<spec>.md
```

The spec as it now stands is what the page must match. A diff tells you where to look, not
what to write.

### 3. Decide what each change touches here

Every change passes a gate before it reaches a page. Answer this in the summary:

> Does somebody using bravebot need to know this?

**The default is no.** It passes only if you can finish the sentence "a reader who did not
know this would ___" with something real: do the wrong thing, hit a limit they cannot
explain, miss a feature they would want, or trust a page that is now wrong. If the honest
ending is "read one more paragraph", it fails.

The reader is a developer using bravebot on their own project, not one working on bravebot
itself. Both are developers, which is what makes this easy to get wrong. A commit about
tooling, editors, or agent configuration reads as relevant until you ask whose repository it
is about.

These fail the gate every time:

- how the project is built, released, tested, reviewed, or specified;
- how a contributor sets up their checkout, their editor, or the agents that work on brave-bot;
- a refactor, a rename, or an internal boundary moving;
- a fix that makes something behave the way a reader already assumed it did;
- a behaviour that landed but is not yet reachable. The commit body reads like a feature, but
  documenting it means inventing the surface. Leave it for the run that lands the rest, and
  `defer` it so that run is offered it.

[development.md](../../../docs/development.md) is not an escape hatch. A change that fails
the gate fails it whatever page would have accepted it.

### Deferring must be recorded, not mentioned

A span boundary can land mid-feature: the configuration arrives in one commit and the
interface that exposes it in the next. Waiting is often the right call, but record it:

```sh
python3 agents/skills/update-docs/docs-ref.py defer <sha> "config landed, no picker yet"
```

Saying it only in the summary loses the feature permanently. The baseline claims everything
before it was folded in, and the next span starts after it, so a commit skipped mid-span is
never offered again. `changes` replays the ledger before each new span. Drop an entry with
`resolve <sha>` once its behaviour is on a page.

Anything still in that ledger is a live obligation. If the commits that complete it have
landed since, the feature is now documentable.

### Configuration outranks the gate

A change that adds or renames something a person must write in a file or export is
user-facing, and the gate does not get to drop it. Backends, settings keys, credential and
region names, model selection, authentication: somebody who does not know the spelling cannot
use the feature at all. This is the gate's most common failure, because a settings key reads
as plumbing.

Read the source for a key name when the specs do not carry one. A spec often argues what a
settings file may say without naming a variable, and a configuration page without its key
names is not usable. Recovering an exact spelling is not inventing. Read `crates/config/` and
write the names down. What you must not do is reconstruct a story from source: if the specs
and commit bodies do not settle what a person sees or why, that part is an open question.

Check the span against [coverage.md](coverage.md) before deciding it is finished. It lists the
subjects readers expect documented, and the gate judges commits one at a time, so it cannot
notice that an entire topic never arrived.

Expect most commits in a span to fail the gate. A span that yields one corrected number is a
good result.

For every change that passes, find the page that owns it. The mapping is stable:

| A brave-bot spec about | Belongs on |
|---|---|
| labels, who may read what | [security/trust.md](../../../docs/security/trust.md) |
| routing, where an effect may land | [security/permissions.md](../../../docs/security/permissions.md) |
| the trust map, vouched paths | [security/trust.md](../../../docs/security/trust.md), [customize/skills.md](../../../docs/customize/skills.md) |
| a tool's arguments, refusals, results | [reference/tools.md](../../../docs/reference/tools.md) |
| shell mode, `run` | [using/shell-mode.md](../../../docs/using/shell-mode.md) |
| terminal input, the transcript | [using/interactive-mode.md](../../../docs/using/interactive-mode.md), [using/transcript.md](../../../docs/using/transcript.md) |
| sessions, compaction | [using/sessions.md](../../../docs/using/sessions.md), [using/context.md](../../../docs/using/context.md) |
| prompting, when a person is asked | [security/permissions.md](../../../docs/security/permissions.md) |
| skills, AGENTS.md | [customize/skills.md](../../../docs/customize/skills.md), [customize/instructions.md](../../../docs/customize/instructions.md) |
| the trace | [security/audit-trail.md](../../../docs/security/audit-trail.md) |
| flags, environment variables, defaults | [reference/cli.md](../../../docs/reference/cli.md), [customize/configuration.md](../../../docs/customize/configuration.md) |
| backends, which service answers, model rosters | [customize/configuration.md](../../../docs/customize/configuration.md) |
| `settings.json`, its keys, what wins over what | [customize/configuration.md](../../../docs/customize/configuration.md) |
| reaching a model through the user's own cloud account, and signing in to it | [customize/configuration.md](../../../docs/customize/configuration.md) |
| slash commands | [reference/commands.md](../../../docs/reference/commands.md) |
| premium, credentials | [customize/premium.md](../../../docs/customize/premium.md) |

A change with no page to land on is the interesting case. Prefer adding a section to the page
that already covers its neighbourhood over creating a page. A new page needs
`sidebar_position` front matter and a place in the reading order, and a thin page is worse
than a paragraph in the right place. Say in the summary when you judged a new page was
warranted and did not add it.

Defaults and tables go stale silently. When a commit changes a default, check
[reference/cli.md](../../../docs/reference/cli.md) and
[customize/configuration.md](../../../docs/customize/configuration.md) for a stated number,
even if the commit body does not mention documentation.

### 4. Write the changes

Follow the writing style rules above. Match the voice already on the page. This site explains
behaviour to somebody using bravebot, so it says what happens and why it is safe, not which
function does it. It does not name Rust types, crates, modules, or spec clause ids: a reader
here has no checkout.

Write the least that leaves the page correct. A sentence earns its place only if the reader
would do something differently for having read it, or would be misled without it.

Three habits to resist, worst first:

- **Do not transcribe the spec's "Why".** A spec argues its decisions because it must justify
  them to somebody who could change them. A reader here cannot. The history of a fix (what
  the figure used to be, what broke, what was tried) is the most common way a page doubles in
  length without gaining anything. Rationale belongs where a rule limits the reader: why a
  thing is refused, why they must approve something, why a limit exists.
- **Say nothing about behaviour a reader already assumes.** A fix that makes something work
  the way anybody expected it to leaves the page alone.
- **Do not restate the mechanism twice**, once plainly and once in the spec's words. Keep the
  plain one.

Prefer amending an existing sentence to adding a paragraph, and adding a sentence to adding a
section. Most spans should leave the pages shorter than a full accounting of them would.

Keep the site's conventions:

- Front matter stays as it is. Do not renumber `sidebar_position` unless the reading order
  genuinely changed.
- Links between pages are relative and end in `.md`.
- `onBrokenLinks` and `onBrokenAnchors` are `throw`, so a wrong link fails the build.

### 5. Verify

```sh
make build
```

This must pass. It is all CI checks, and a broken link or anchor fails it.

Then check your own edits for dashes:

```sh
git diff -U0 | grep -n '^+.*[—–]'
```

This must return nothing. A hit needs the sentence rewritten, not a hyphen swapped in.

### 6. Commit, then move the baseline

One documentation change per commit, in the order a reader would meet them. Then the baseline
moves in a commit of its own, touching nothing else:

```sh
python3 agents/skills/update-docs/docs-ref.py set <new-ref>
git add docs-updated-to-sha
git commit -m "docs: track brave-bot up to <short-sha>"
```

If this run documented something an earlier one deferred, clear it in the same commit:

```sh
python3 agents/skills/update-docs/docs-ref.py resolve <sha>
```

The baseline commit goes last. It claims everything before it has been folded in, so it must
not land while a page is still wrong. If the run stops early, record the last commit actually
covered rather than head, and say so. A baseline ahead of the pages is worse than one behind
them: the next run will skip what this one missed.

Do not push. Whoever asked for the update decides that.

---

## Reporting

End with a short summary:

- the span folded in, as `<baseline> -> <new ref>`, and how many commits;
- the pages changed, one line each, saying what behaviour moved;
- what failed the gate, one line each, so the decisions are reviewable. This list is normally
  the longer of the two;
- what was deferred and what was resolved, with shas, so the ledger and the summary agree;
- which [coverage.md](coverage.md) rows this span touched, and any row it showed to be missing;
- open questions the commits did not settle. A key name is never one of these. Read it from
  the source instead.

If nothing needed changing because the span touched no documented behaviour, say that and
still move the baseline.
