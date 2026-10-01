---
title: Vim Motions Everywhere
date: 2026-09-24
tags: tooling
---

Vim motions have been a huge part of how I work. I have them enabled or installed in every environment that supports them. But there's a specific bad feeling that comes from landing in an app that *doesn't* — Discord, a random GTK dialog, a browser text field — and suddenly your fingers don't know what to do. That feeling sent me down a rabbit hole.

I came out the other side with something simpler than global Vim: a small set of text controls that works across apps without trying to recreate Vim everywhere.

## It's Not About hjkl

My first instinct was to just use arrow keys instead of fighting broken Vim emulation everywhere. That's when I noticed the real bottleneck: it was never the *keys*, it was the *distance*. Reaching off the home row to hit an arrow key costs real time, every single press. That's the actual reason Vim's hjkl caught on in the first place — not the modal editing, just that your hand never leaves home row.

So the goal became: get arrow-key navigation and selection onto the home row, without depending on any single app's Vim plugin being any good.

## Kanata

[Kanata](https://github.com/jtroo/kanata) is a free, open-source key remapper written in Rust. It intercepts keypresses and sends the keys or shortcuts you configure:

`Key press -> kanata intercepts -> kanata sends the configured shortcut -> OS`

On my Linux setup, Kanata reads keyboard events and emits keypresses through the kernel's input system. That means the same bindings work across apps, whether I'm in Discord, a terminal, or a browser field. Text actions still depend on the app supporting the ordinary operating-system shortcut being sent, but they don't rely on that app implementing Vim motions.

## The Setup: Caps Lock as a Held Modifier

I use Caps Lock as a modifier. While I hold it, Kanata activates a layer of text controls. When I release it, typing returns to normal. The layer isn't meant to be Vim's normal mode; it just puts common movement and selection shortcuts under my left hand.

| Key while holding Caps | Action |
|---|---|
| `h` `j` `k` `l` | Move left / down / up / right |
| `w` / `b` | Jump forward / backward by a word |
| `n` / `m` | Select the current word, then extend the selection backward / forward with repeated presses |
| `e` | Select the current line |
| `o` | Move to the end of the line and insert a line break below |
| `0` / `Shift+4` (`$`) | Move to the start / end of the line |
| `u` / `p` / `del` | Undo / paste / delete |

For larger selections, I hold **Caps+V** and use:

| Keys while holding Caps+V | Action |
|---|---|
| `h` `j` `k` `l` | Extend the selection left / down / up / right |
| `w` / `b` | Extend the selection forward / backward by a word |

Release **V** to return to the regular Caps layer. This lets me make larger selections without changing how the usual word-selection keys work.

The word and line actions use ordinary OS shortcuts. For example, word movement sends Ctrl+Left or Ctrl+Right on Linux, while word selection adds Shift. Kanata isn't reimplementing Vim's text-object engine; it sends shortcuts that apps already understand.

## Try It

The config and install script are in [Kanata-OS-VimMotions](https://github.com/Nickaphy/Kanata-OS-VimMotions).