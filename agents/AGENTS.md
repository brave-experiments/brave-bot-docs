# bravebot-docs

The documentation site for [bravebot](https://github.com/brave-experiments/bravebot), a
general-purpose agent with structural resistance to indirect prompt injection. Docusaurus,
deployed to GitHub Pages from `main`.

## The rule that overrides everything

**bravebot's `docs/specs` is the source of truth for behaviour. This site is downstream of
it.** Where the two disagree, this site is wrong: fix the page rather than documenting
around the clause.

That has a consequence worth stating plainly. Nothing here is a place to decide what
bravebot does. A page that describes behaviour no spec pins down has invented it, and
somebody will read it as a promise. If a spec does not settle a question, the answer is to
raise it against bravebot, not to write something reasonable here.

[`docs-updated-to-sha`](../docs-updated-to-sha) records the bravebot commit this site was
last brought up to. `make docs-changes` shows what has landed since, and the
[update-docs](skills/update-docs/SKILL.md) skill folds it in and moves the record. Only
that skill rewrites the record.

## Writing for this site

The reader is somebody using bravebot, not somebody working on it. They have no checkout.

- Say what happens and why it is safe. Do not name Rust types, crates, modules, or spec
  clause ids.
- Explain the reasoning behind a restriction. A rule with no stated reason reads as
  arbitrary, and this project's rules are anything but.
- Prefer a sentence on the right page to a new page. A new page needs `sidebar_position`
  front matter and a place in the reading order, and a thin one is worse than a paragraph
  where a reader was already looking.
- Links between pages are relative and end in `.md`.
- Match the voice already on the page you are editing.

`onBrokenLinks` and `onBrokenAnchors` are both `throw`. A wrong link fails the build
instead of shipping, which is the whole reason they are set that way.

## Structure

- `docs/` is the site content. The sidebar is generated from the folder structure: each
  directory is a category described by its `_category_.json`, and each page's place comes
  from its own front matter.
- `agents/` is the checked-in source of truth for skills and this file. No tool reads it
  directly. `make init` symlinks it into `.claude/` and `.bravebot/`, which are gitignored.
- `static/` is copied verbatim. `.nojekyll` in there is load-bearing: without it GitHub
  Pages hides every path beginning with an underscore.

## Building

`make build` must pass before every commit. It is the whole of what CI checks, and it is
fast. There is no exemption for a change that only touched prose: a broken relative link
fails the build as readily as anything else.

Read what it exits with rather than piping it into a filter. `make build | grep -i error`
reports success on a thrown broken link, because the failure text does not match and grep
exited happily.

## Committing

No co-attribution markers for Claude Code or other tools, in commits or pull requests: a
commit is authored by the person running the tool and by nobody else. Where that is
enforced differs by tool, and this file is the last word for only one of them.

- **Claude Code** appends a trailer unless a setting says otherwise, so `make init` links
  `agents/claude-settings.json` to `.claude/settings.json` and its empty `attribution`
  strings settle it before a session starts. That is what makes the rule hold on a
  scheduled runner that has not read this file yet.
- **bravebot** reads `.bravebot/settings.json`, which `make init` links from
  `agents/bravebot-settings.json`. It carries the same `attribution` block and bravebot
  ignores it: the keys it reads are `env`, `permissions`, `model`, `editorMode` and
  `provider`, and it appends no trailer of its own. The file is there for the day that
  changes; until then the rule above is the whole of it.
- **Codex** resolves attribution from the signed-in account, not from a file: there is no
  `config.toml` key for it, and where the account has it on, Codex is told to ignore
  instructions like this one. A Codex run that adds a trailer is turned off in the account
  settings rather than in this repository.

**One change per commit.** A commit is the unit somebody reads, reverts, and bisects on, so
it has to stand up alone. If the message needs an "and" to describe what the commit does,
it is usually two commits. Keep them small, and leave the tree building at every one.

Never commit anything from `build/`, `.docusaurus/`, `node_modules/`, or the generated
`.claude/`, `.bravebot/` and root `AGENTS.md` symlinks. All are gitignored; if one shows up
in `git status`, something is wrong with the ignore rules rather than with the rule against
committing it.

## Conventions

- This site's prose uses em-dashes and the surrounding pages are written that way. That is
  a deliberate difference from bravebot's own convention, which forbids them. Match the
  file you are in.
- British or American spelling: match the page.
- Comments in the build config and scripts explain **why**, never what.
- No new dependencies without a reason that survives scrutiny. This is a static site, and
  every dependency is something that ships to a reader's browser or runs in CI.
