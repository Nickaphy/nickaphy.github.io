---
title: Vim Motions Everywhere
date: 2026-09-24
tags: tooling
---

Vim motions have been a huge part of how I work. I have them toggled on or
installed in every environment that supports it. But there's a specific bad
feeling that comes from landing in an app that *doesn't* — Discord, a random
GTK dialog, a browser text field — and suddenly your fingers don't know what
to do. That feeling sent me down a rabbit hole, and I came out the other
side with what I'd call the actual solution, not another half-measure.

## It's Not About hjkl
My first instinct was to just use arrow keys instead of fighting broken vim
emulation everywhere. That's when I noticed the real bottleneck: it was
never the *keys*, it was the *distance*. Reaching off the home row to hit an
arrow key costs real time, every single press. That's the actual reason
vim's hjkl caught on in the first place — not the modal editing, just that
your hand never leaves home row.

So the goal became: get arrow-key navigation onto the home row, without
depending on any single app's vim plugin being any good.

## Kanata
[Kanata](https://github.com/jtroo/kanata) is a free, open-source key
remapper written in Rust. It sits between your keyboard and your operating
system, intercepting every keypress before your OS ever sees it:

`Key press -> kanata intercepts -> kanata sends whatever you configured -> OS`

The part that makes this actually work everywhere: kanata operates at the
kernel's evdev/uinput level — *below* X11, Wayland, and your window manager
entirely. It doesn't know or care whether you're in Discord, a terminal, or
a browser field, because it's not talking to any of those. It's talking to
the kernel, the same way your physical keyboard does. That's the difference
between this and every app-level "vim mode" I'd tried before: those only
work if that specific app chose to implement them well. This works
regardless.

## The Setup: Caps Lock as a Mode Switch
With a modifier key — I used Caps Lock, since nobody needs its original job
— held down, kanata activates a second layer of key bindings. Release it,
and you're typing normally. Hold it, and you're effectively in vim's
"normal mode":

| Key (while holding Caps) | Action |
|---|---|
| `h` `j` `k` `l` | Left / Down / Up / Right |
| `w` | Jump forward one word |
| `b` | Jump backward one word |
| `u` | Undo |
| `y` | Copy (acts on the current selection) |
| `d`, `d` | Delete the current line |
| `d`, `i`, `w` | Delete the word under the cursor |
| `v` | Toggle visual mode — `hjkl`/`w`/`b` then extend a selection instead of just moving; `d`/`y` act on it and drop back out |

None of this reimplements vim's actual text-object engine. `d`, `i`, `w`
isn't a real "delete inner word" — it's "select the word under the cursor
using the same Ctrl+Left / Ctrl+Shift+Right shortcut every OS text field
already supports, then delete." It rides entirely on shortcuts apps already
implement, rather than trying to out-build vim's parser from scratch. That
constraint is exactly why it works in Discord and a browser field and not
just in a real editor.

## Try It
Config, install script: **[Kanata-OS-VimMotions](https://github.com/Nickaphy/Kanata-OS-VimMotions)**
