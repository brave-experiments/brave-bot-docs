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

This site documents brave-bot, and it goes stale the moment brave-bot's behaviour moves.
[`docs-updated-to-sha`](../../../docs-updated-to-sha) records the brave-bot commit the
site was last brought up to. This skill closes the gap between that commit and brave-bot's
head, then moves the record forward.

- **Default run**: everything that landed under `docs/` or `README.md` since the baseline.
- **Scoped run** (`/update-docs <rev>`): stop at `<rev>` instead of head. Use this to fold
  a long backlog in a few reviewable passes.
- `--all` widens the review to commits that touched only code, for when a behaviour change
  arrived without its spec.
- `dry-run` reports what would change and writes nothing.

Two files carry state between runs: `docs-updated-to-sha`, the commit the site is current as of,
and `docs-deferred`, the commits reviewed and consciously postponed. The second exists because the
first cannot express "seen, not yet written".

---

## The one direction this update runs in

**brave-bot's specs are the source of truth. When this site and a spec disagree, this site
is wrong.** Fix the page, never the spec, and never document around a clause by describing
what the site already says more carefully.

This skill does not edit anything in the brave-bot repository. It reads that checkout and
writes only here. If a spec looks wrong, say so in the summary and leave it alone: that is
a change to brave-bot, made there, by a person who asked for it.

It also never invents behaviour. Every sentence added has to be traceable to a clause or a
commit in the span being folded in. A gap the commits do not settle is reported as an open
question, not filled with a plausible guess.

---

## What the script does, so you do not

`docs-ref.py` handles every deterministic part at zero model cost:

```sh
python3 agents/skills/update-docs/docs-ref.py show              # where the docs stand
python3 agents/skills/update-docs/docs-ref.py changes           # commits to fold in
python3 agents/skills/update-docs/docs-ref.py changes --full    # with bodies and file lists
python3 agents/skills/update-docs/docs-ref.py set <rev>         # record a new baseline
python3 agents/skills/update-docs/docs-ref.py defer <rev> <why> # leave one for a later run
python3 agents/skills/update-docs/docs-ref.py resolve <rev>     # that one is now documented
```

`make docs-updated-to-sha` and `make docs-changes` are the same first two commands.

It finds the brave-bot checkout at `$BRAVE_BOT_REPO`, or at `../brave-bot` beside this
repository. If neither exists it says how to clone one. It reads brave-bot's `origin/main`
rather than whatever branch that checkout is sitting on, so a colleague's work in progress
is never documented as shipped.

---

## The job

### 1. Establish the span

```sh
python3 agents/skills/update-docs/docs-ref.py show
```

If it says up to date, stop and say so. Nothing else in this skill runs.

Otherwise fetch first, so head means head:

```sh
git -C "${BRAVE_BOT_REPO:-../brave-bot}" fetch origin
```

Note the `new ref once folded in` sha that `changes` prints. That is the value the baseline
moves to at the end, and it is fixed now: a commit landing in brave-bot mid-run does not
belong to this pass.

### 2. Read what landed

```sh
python3 agents/skills/update-docs/docs-ref.py changes --full
```

Read the commit bodies. In brave-bot they explain **why** a behaviour changed, which is
usually the part this site is missing, and they name the specs that moved. Then read those
specs at the new head, not at the baseline:

```sh
git -C ../brave-bot show <new-ref>:docs/specs/<spec>.md
```

The spec as it now stands is what the page must match. A diff tells you what to look at; it
does not tell you what to write.

### 3. Decide what each change touches here

**Every change passes a gate before it reaches a page.** Ask one question about it, and answer it
out loud in the summary:

> Does somebody using bravebot need to know this?

**The default is no.** It passes only if you can finish the sentence *"a reader who did not know
this would ___"* with something real: do the wrong thing, hit a limit they cannot explain, fail to
find a feature they would want, or trust a page that is now wrong. If the honest ending is "read
one more paragraph", it fails.

The reader is a developer **using** bravebot on their own project, not one working on bravebot
itself. Both are developers, which is what makes this easy to get wrong: a commit about tooling,
editors or agent configuration reads as relevant right up until you ask whose repository it is
about.

These fail the gate every time:

- how the project is built, released, tested, reviewed, or specified;
- how a contributor sets up their checkout, their editor, or the agents that work on brave-bot;
- a refactor, a rename, or an internal boundary moving;
- a fix that makes something behave the way a reader already assumed it did;
- a behaviour landed but not yet reachable — the commit body reads exactly like a feature, and
  documenting it means inventing the surface. Leave it whole for the run that lands the rest, and
  **`defer` it** so that run is offered it.

[development.md](../../../docs/development.md) is not an escape hatch: a change that fails the gate
fails it whatever page would have accepted it.

### Deferring is a written record, never a note in the summary

A span boundary can land mid-feature: the configuration arrives in one commit and the interface that
exposes it in the next, and the honest call on the first is to wait. That call has to be **recorded**:

```sh
python3 agents/skills/update-docs/docs-ref.py defer <sha> "config landed, no picker yet"
```

**Saying it only in the summary loses the feature permanently.** The baseline claims everything
before it was folded in, and the next span starts *after* it, so a commit skipped mid-span is never
offered again. `changes` replays the ledger ahead of each new span; drop an entry with `resolve
<sha>` once its behaviour is on a page. This is not bookkeeping — it is the difference between "later"
and "never".

Anything still in that ledger is a live obligation. If the commits that complete it have since
landed, the feature is now documentable, and the deferral is what tells you so.

### Configuration outranks the gate

**A change that adds or renames something a person must write in a file or export is user-facing, and
the gate does not get to drop it.** Backends, settings keys, credential and region names, model
selection, authentication: somebody who does not know the spelling cannot use the feature at all.
This is the failure mode the gate produces most reliably, because a settings key reads as plumbing.

**Read the source for a key name when the specs do not carry one.** A spec often argues what a
settings file may say without naming a single variable, and a configuration page that omits its key
names is not usable. Recovering an exact spelling is not inventing — it is the opposite — so read
`crates/config/` and write the names down. What you must not do is reconstruct a *story* out of the
source: if the specs and commit bodies do not settle what a person sees or why, that part is an open
question, and the key names are still not.

Check the span against [coverage.md](coverage.md) before deciding it is finished. It lists the
subjects readers expect documented, and it exists because the gate judges commits one at a time and
so cannot notice that an entire topic never arrived.

Expect most commits in a span to fail the gate. A span that yields one corrected number is a good
result, not a thin one.

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

A change with no page to land on is the interesting case. Prefer adding a section to the
page that already covers its neighbourhood over creating a page: a new page needs
`sidebar_position` front matter and a place in the reading order, and a thin one is worse
than a paragraph in the right place. Say in the summary when you judged a new page was
warranted and did not add it.

Defaults and tables go stale silently. Whenever a commit changes a default, check
[reference/cli.md](../../../docs/reference/cli.md) and
[customize/configuration.md](../../../docs/customize/configuration.md) for a stated number,
even if the commit body does not mention documentation.

### 4. Write the changes

Match the voice already on the page. This site explains behaviour to somebody using
bravebot, so it says what happens and why it is safe, not which function does it. It does
not name Rust types, crates, modules, or spec clause ids: a reader here has no checkout.

**Write the least that leaves the page correct.** The reader is busy and is here to get
something done. A sentence earns its place only if they would do something differently for
having read it, or would be surprised or misled without it. Nothing else does, however true
it is and however well the commit explains it.

Three habits to resist, in the order they cost the most:

- **Do not transcribe the spec's "Why."** A spec argues its decisions because it has to
  justify them to somebody who could change them. A reader here cannot and has no stake in
  it. The history of a fix — what the figure used to be, what broke, what was tried — is the
  commonest way a page doubles in length without gaining anything. Rationale belongs on the
  page where a rule **constrains the reader**: why a thing is refused, why they must approve
  something, why a limit exists they will hit. Not behind every behaviour.
- **Say nothing about behaviour a reader already assumes.** A fix that makes something work
  the way anybody would have expected it to leaves the page alone. If a theme applies to the
  interface, it applies to a prompt too, and a clause pinning that is a promise to the
  implementer rather than news to a reader.
- **Do not restate the mechanism twice**, once plainly and once in the spec's own words.
  Pick the plain one.

Prefer amending a sentence that is already there to adding a paragraph, and prefer adding a
sentence to adding a section. Most spans should leave most pages shorter than a full
accounting of them would. A span that ends with one corrected number and nothing else is a
good outcome, not a thin one.

Keep the site's own conventions:

- Front matter stays as it is. Do not renumber `sidebar_position` to slot something in
  unless the reading order genuinely changed.
- Links between pages are relative and end in `.md`.
- `onBrokenLinks` and `onBrokenAnchors` are `throw`, so a wrong link fails the build rather
  than shipping. This is the safety net: use it.

### 5. Verify

```sh
make build
```

This must pass. It is the whole of what CI checks, and a broken link or anchor fails it.

### 6. Commit, then move the baseline

One documentation change per commit, in the order a reader would meet them. Then the
baseline moves in a commit of its own, touching nothing else:

```sh
python3 agents/skills/update-docs/docs-ref.py set <new-ref>
git add docs-updated-to-sha
git commit -m "docs: track brave-bot up to <short-sha>"
```

If this run documented something an earlier one deferred, clear it in the same commit:

```sh
python3 agents/skills/update-docs/docs-ref.py resolve <sha>
```

The baseline commit goes **last**. It is the claim that everything before it has been
folded in, so it must not land while a page is still wrong. If the run stops early, having
folded in part of the span, record the last commit actually covered rather than head, and
say so. A baseline ahead of the pages is worse than one behind them: the next run will skip
what this one missed.

Do not push. Whoever asked for the update decides that.

---

## Reporting

End with a short summary:

- the span folded in, as `<baseline> -> <new ref>`, and how many commits;
- the pages changed, one line each, saying what behaviour moved;
- **what failed the gate**, one line each, so the decisions are reviewable rather than silent.
  This list is normally the longer of the two;
- **what was deferred and what was resolved**, naming the shas, so the ledger and the summary agree;
- which [coverage.md](coverage.md) rows this span touched, and any row it showed to be missing;
- open questions the commits did not settle. A key name is never one of these — read it from the
  source instead.

If nothing needed changing because the span touched no documented behaviour, say that and
still move the baseline. A span reviewed and found irrelevant is a real result, and leaving
the baseline behind means re-reading it next time.
