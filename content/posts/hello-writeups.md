---
title: Hello, writeups
date: 2026-09-23
tags: meta, sample
---

This is a sample post to prove the build pipeline works. Write real writeups
as Markdown files under `content/posts/`, then run `python build.py`.

## Fenced code

Here is a short Python snippet so syntax highlighting has something to style:

```python
def greet(name: str) -> str:
    return f"hello, {name}"


if __name__ == "__main__":
    print(greet("world"))
```

## Inline code

Use `python build.py` to regenerate `docs/`.
