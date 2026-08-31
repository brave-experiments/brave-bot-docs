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
