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

**What the session says in its own voice is drawn in an ink of its own** — the trust question, a
confinement that is unavailable, a status report. Never the ink that marks untrusted content, which
is spoken for twice over already: a call still running, and the margin down every block the planner
may not read. Drawing a note in it said the trust question was quarantined.

Colour is never what makes that marking hold. A colour can be imitated by the content beside it,
which is exactly why quarantine stands on the margin instead: no ink tells you whether something is
quarantined, and a note drawn in the wrong one would still be outside a block.

Where a result went is drawn only where that is not the ordinary answer — so a quarantined read says
so, and an ordinary one does not clutter the transcript saying what always happens.

A tiny terminal still renders.

## The end of a turn is said

A finished turn gets a row of its own: which turn it was, what it cost, and how long it took. A turn
that failed is reported as stopped, without a cost, since that figure is settled as a turn is
abandoned rather than as it finishes. The row lasts until the next turn starts, and a session that
has not run one shows nothing.

The working indicator going out used to be the only thing that said a turn was over, and an
announcement made by something disappearing is one nobody reads. It matters most for the turn that
ends on a sentence like `now let me look at the dispatch code`: the planner asked for no tool, so
the turn ended there, and the last thing on your screen was a promise with nothing to distinguish it
from a hang.

The cost is on the row because a turn that spent forty rounds and one that spent a single round look
identical in scrollback, and the difference is most of the explanation.

## Themes

`/theme` opens a picker on the palette the interface is painted in. Up and Down — or `k` and `j` —
move the cursor, Enter keeps the theme under it, and Escape puts back the one that was in force when
the picker opened. `/theme <name>` applies a theme without opening the panel at all.

The picker is a bordered panel in the middle of the screen rather than a full-screen list, because a
full-screen list hides the thing a theme is for. Your session stays visible behind it and is redrawn
every time the cursor moves, so what you are previewing is your own transcript rather than an empty
page. On a tiny terminal the panel shrinks to stay inside the frame.

Under the list is a row for whatever a theme does that its name does not say. Only `brave` has
anything there — it is the only theme whose inks depend on your terminal, and its name says who it is
from rather than what it does. The row is drawn empty for the rest, so the list does not shift under
the cursor as it moves.

### What a theme decides

Where a colour is what tells one thing on the screen from another, `brave` uses a shade it mixes
itself rather than one of the sixteen named colours. A named colour is a slot your terminal repaints,
so it is a request rather than a colour: the same code drew something different in every profile,
which is how one slot came to carry two meanings at once without anybody choosing that. The named
slots are kept only where the meaning is your terminal's own — green for finished, red for failed,
dim grey for an aside — which you read against whatever palette you chose rather than against each
other. A mixed shade that has to stay legible against the background is picked for the background
sensed at startup, and a terminal that will not say which it has is treated as dark.

A theme you choose by name paints every role from its own palette, including the background and the
default text. No named slots are used there, so two roles cannot collapse into one because your
terminal remapped green.

:::note
The question about your background colour is asked once, before the first frame, and the answer is
read straight off the terminal. Anything typed or pasted into the window before it arrives is read by
that same question and discarded, and a terminal that answers with nothing holds the window open for
its full 80 milliseconds. It happens once a session, before there is a box to type into.
:::

The palette never changes what a marking means. Quarantine stands on the margin, not on a colour, in
every theme.

See [Configuration](../customize/configuration.md#choosing-a-theme) for where the choice is stored
and how to write one of your own.

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

The transcript gets every row of the screen but the last, which is the footer. The input box goes,
the working indicator above it goes, and anything being offered beneath it goes; all of them come
back the moment you close it. Each one is something you are invited to type at, and no key reaches
any of them from in here — a box drawn under a mode that cannot reach it is rows spent inviting a
keystroke that would do nothing, and a caret blinking in it says the opposite of what is true. What
they cost goes to the transcript, which is the whole of what you opened a pager to look at.

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

### Getting the text out

`v` opens the transcript in your editor. What goes is the rows as they are drawn, margins and all,
so untrusted content is marked in the file exactly the way it is marked on the screen. It is written
to a temporary file **outside the workspace**, opened with `$VISUAL` or `$EDITOR` the same way a
prompt is, and the file goes when the editor exits. The key does nothing while a turn is running:
an editor needs the screen, and a running turn is drawing it.

**Nothing comes back.** The key that edits a prompt takes back what you saved, because a prompt is
something you are still writing. A transcript is a record of what happened, and a record you can
edit back into the session is not one. No later turn reads that file, and no path in your workspace
gains anything from its having existed.

A pager can search a screen. Everything past that — reading two passages side by side, keeping a
copy, grepping the lot — is a text editor's job, and you have one.

A turn goes on underneath while the scroller is open, and the view does not move to follow it. What
arrives joins the transcript without dragging you to the tail, and the footer says that more has
come in below and how much, so holding your place costs you no knowledge that it did. `G` reaches
it. The footer also says that a turn is still running, in the word the indicator would have used,
since the indicator is not on the screen to say so itself.

Holding the view is the whole of what the scroller is for. Somebody reading back through a turn
that is going wrong is reading precisely because it is going wrong, and a view yanked to the bottom
by the next line the model writes takes away the only thing they were trying to do.
