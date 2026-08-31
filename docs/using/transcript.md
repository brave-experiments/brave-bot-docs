---
sidebar_position: 4
title: Reading the transcript
description: What is drawn back, and the scroller Ctrl-O opens over it.
---

# Reading the transcript

## What is drawn

The end of a reply is visible when it arrives, so scrolling back is always deliberate. A reply is
drawn as it arrives, and the round that ends replaces it. A resumed session redraws what the earlier
turns did.

**Untrusted content is shown to you on purpose.** You are the one party allowed to read it, and the
whole point of quarantine is that the decision comes to you rather than to the model. It is drawn
inside a margin it cannot forge, and never drawn as structure — so untrusted bytes cannot paint
themselves as a heading, a prompt, or a message from the program.

The margin is on every drawn **row**, not every line of the content. A line wider than the box is
broken to the width by the same step that draws the margin, and each row it breaks into carries a bar
of its own.

Where a result went is drawn only where that is not the ordinary answer — so a quarantined read says
so, and an ordinary one does not clutter the transcript saying what always happens.

A tiny terminal still renders.

## Scrolling at rest

| Key | Where the view goes |
|---|---|
| the wheel | up and down, stopping at the ends |
| PageUp / PageDown | a screen at a time |
| Home / End | the start, or the latest |

All of these work while a turn is running, and the view does not jump to follow the turn.

## The scroller

**Ctrl-O** opens the scroller on the view already on the screen. Opening moves nothing: the row you
were looking at when you pressed the key is the row under your eyes afterwards. It is one view with
two sets of keys over it, not a second copy of the transcript.

While it is open the keys are the scroller's. A character does not reach the input box, Enter sends
nothing, and the line you were half-way through keeps its text, its caret and whatever is attached to
it, coming back exactly as it was when the scroller closes.

### Moving

| Keys | Where the view goes |
|---|---|
| Up / Down, `k` / `j` | one line back / on |
| Ctrl-U / Ctrl-D | half a screen back / on |
| Space / `b`, Ctrl-F / Ctrl-B | a whole screen on / back |
| `g` / `G`, Home / End | the first row / the last |
| `{` / `}` | the prompt before this one / the prompt after |
| the wheel | as it does at rest |

Both dialects are there because the people who reach for a pager have `less` or `vi` in their hands
already. Each end is a stop rather than a count that keeps going, so a held key comes to rest
somewhere the next press can move away from.

`{` and `}` land on the row a turn begins at, which is a prompt you typed.

### Searching

`/` searches what is drawn. The needle is typed at the foot of the screen, Enter runs it, and it is
matched as a **substring, character for character, never as a pattern**: case-insensitive while the
needle is all lower case, exact from the moment it holds a capital. `n` and `N` walk the matches.

What is searched is the text of the rows as they are drawn, so a match is always something you can
see. A search matches untrusted content too, and never lifts it out of its block.

### Leaving

`q`, Escape and Ctrl-O each close the scroller, and the view stays where it left it. Escape clears a
standing search first, since that is the nearer thing to stop; the press after that closes.

Ctrl-C closes the scroller and does nothing else — a turn in flight goes on running, and the press
that reaches it is the next one. Each press answers the nearest thing there is to stop, and the
screen says which.

`?` says what the scroller takes, and the scroller says that it is open.

`v` opens the transcript in your editor, and reads nothing back.

A turn goes on underneath while the scroller is open, and the view does not move to follow it.
