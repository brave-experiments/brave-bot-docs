---
sidebar_position: 4
title: Leo Premium
description: Import a Leo Premium subscription so requests go to the premium tier.
---

# Leo Premium

If you have a Leo Premium subscription in a Brave install on this machine, Brave Bot can register
itself against it and spend its own credentials on the premium tier.

```sh
bravebot import-leo-creds            # from the stable Brave install
bravebot import-leo-creds beta
bravebot import-leo-creds nightly
bravebot import-leo-creds development
bravebot import-leo-creds --forget   # remove what was imported
```

Without a channel, `stable` is what importing means.

## What it does, and does not do

**This registers as a new device.** Only the subscription's *order id* is read from the browser
profile. The credentials themselves are generated here and signed by Brave, exactly as a second
browser on another machine would do it. The browser keeps its own, and nothing it holds is spent.

Before anything is registered, the order is checked: an unpaid order, one asking for no credentials,
one asking for an implausible number, and one without interval metadata are all refused. The Leo item
is picked out of a multi-item order rather than assumed to be the only one. A batch is then verified
against the issuer's key before it is stored, and tokens are matched by value rather than by position.

## How credentials are spent

Credentials arrive in batches covering a few days and are spent one per request. A spent credential is
never offered again, consecutive spends hand out different credentials, and spending past the end of a
batch is refused.

**A credential is never sent to the non-premium host.** The premium host and the credential travel
together, because a credential belongs to a deployment. A build with no premium host configured stays
on the free tier rather than sending one where it does not belong.

Nothing is written back unless a credential was actually spent, so a session that spends nothing never
touches the store.

## Where they are kept

In the system keychain, not in a file, and each channel is stored separately. A malformed or empty
entry is reported as such rather than treated as absent credentials, and a credential without a token
is rejected on load.

Importing, and the first request of a session, may ask for your keychain password.

## When a subscription cannot be read

Finding nothing has two causes, and they are not the same fact.

**Nothing imported** is the free tier working as intended, and nothing is said about it. An endpoint
belonging to no environment, such as a local one, is this case too — no credential belongs near it by
design.

**A batch that exists and could not be read** is reported to you, naming the channel and the reason.
That happens when the store refuses, or when another version wrote the entry.

The difference matters because of what happens next. The request goes out on the free tier, where the
endpoint answers a premium model name by **substituting a weaker model rather than failing** — a 200
and an ordinary reply. So a request that silently lost its credential still returns something that
reads like an answer, and nothing on your screen would connect that to the store. The downgrade has
to be said out loud, because its only other symptom is the agent appearing to get worse for no
reason.

## Which tier a turn actually ran on

**What `/status` says about the tier is what the last turn actually did**, not what the build was
compiled with. Before the first turn it says premium is *available*, rather than claiming it is or is
not in use.

The opening screen draws the tier beside the confinement, in the same words `/status` uses before a
turn has run. It deliberately does **not** open the credential store: naming the real tier means
unlocking it, which prompts for a password, and a dialog on every session opened before anybody has
typed anything is how people are trained to approve dialogs unread. A pane too narrow for the
wordmark still reports both.

Where the server reports using a model other than the one you asked for, **both are shown** — the
choice you made and the model that actually answered — said once when it starts happening rather than
every turn. `automatic` resolving to a concrete model is not a substitution: that is the server
choosing per request, which is what `automatic` means.

Every build that knows a premium host would otherwise report itself as premium, which is a fact about
compilation and not about any request. A session reported "premium configured" while ten consecutive
requests went out on the free tier and were answered by a model a third the size, which then
announced tool calls it never emitted and stalled the turn. A panel that cannot be trusted on this
point is worse than one that omits it.

## Requirements and limits

- **macOS and Linux.** Windows is not supported.
- The build must know the premium host. Without it, premium is unavailable.
- A credential only works against the deployment that issued it, so import from the Brave channel
  matching the environment the binary is configured for. Mismatching them returns a 401.
- Sign in to Leo in that Brave install first: a subscription that is not in the profile cannot be
  imported.

## Checking what you have

```sh
bravebot doctor
```

reports which channels have an imported subscription and how much of it is left:

```
  leo       stable subscription imported, 84 of 90 credentials unspent
```

Counts only. A credential is a bearer secret, so none of it is printed.
