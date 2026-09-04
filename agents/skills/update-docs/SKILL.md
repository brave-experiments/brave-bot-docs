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
allowed-tools: Bash(python3 agents/skills/update-docs/*), Bash(make docs-changes*), Bash(make docs-updated-to-sha*), Bash(make build*), Bash(git*)
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

**First decide whether it belongs here at all.** Most spans carry commits this site has nothing to
say about, and folding one in anyway is how a documentation site fills with text nobody came to
read. The test is whether somebody *using* bravebot would go looking for it in order to use the
thing better. If they would not, it does not go on a page, however clearly the commit explains
itself.

Things that routinely fail that test:

- how the project is built, released, tested, or reviewed;
- how a contributor adds a message, a language, a spec clause, or a crate;
- a refactor, a rename, or an internal boundary moving;
- a behaviour that has landed but that nothing a user can reach exposes yet.

That last one is the one worth being careful about, because the commit body reads exactly like a
feature. A capability wired up but not yet offered anywhere a person can see is not behaviour this
site can describe: the pages a user would need do not exist yet, and writing them means inventing
the surface. Leave it, say so in the summary, and let the run that lands the rest of it pick the
whole thing up.

**Never reconstruct a user-facing story out of the source.** If the specs and commit bodies in the
span do not settle what a person sees, that is the answer — report it as an open question. Reading
Rust to recover a flag name, a default, or a settings key is the point at which this skill has
started inventing.

For every change that survives that filter, find the page that owns it. The mapping is stable:

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
- anything deliberately not documented, and why;
- open questions the commits did not settle.

If nothing needed changing because the span touched no documented behaviour, say that and
still move the baseline. A span reviewed and found irrelevant is a real result, and leaving
the baseline behind means re-reading it next time.
