#!/usr/bin/env python3
"""
Build static HTML into docs/ for GitHub Pages.

Layout:
  content/     — pages and writeups you edit
  site/        — templates + assets (look & chrome)
  docs/        — generated output (do not hand-edit)

Never hand-edit docs/ — this script regenerates it.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
POSTS_DIR = CONTENT / "writeups" / "posts"
TEMPLATES = ROOT / "site" / "templates"
ASSETS = ROOT / "site" / "assets"
DOCS = ROOT / "docs"

FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z",
    re.DOTALL,
)
# Strip simple markdown markers for excerpts
MD_STRIP_RE = re.compile(r"[#*_`\[\]()]")


@dataclass
class Post:
    slug: str
    title: str
    date: str
    tags: list[str]
    body_html: str
    excerpt: str


def read_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Post is missing frontmatter delimited by ---")

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()

    return meta, match.group(2).lstrip("\n")


def make_excerpt(body_md: str, limit: int = 160) -> str:
    """First non-empty paragraph, plain-ish text, trimmed to limit."""
    for block in body_md.split("\n\n"):
        line = block.strip()
        if not line or line.startswith("```") or line.startswith("#"):
            continue
        plain = MD_STRIP_RE.sub("", line)
        plain = re.sub(r"\s+", " ", plain).strip()
        if len(plain) > limit:
            return plain[: limit - 1].rstrip() + "…"
        return plain
    return ""


def md_to_html(body: str) -> str:
    return markdown.markdown(
        body,
        extensions=["fenced_code", "codehilite", "tables"],
        extension_configs={
            "codehilite": {
                "css_class": "codehilite",
                "guess_lang": False,
            }
        },
    )


def load_posts() -> list[Post]:
    posts: list[Post] = []
    if not POSTS_DIR.is_dir():
        return posts

    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        tags_raw = meta.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        posts.append(
            Post(
                slug=path.stem,
                title=meta.get("title", path.stem),
                date=meta.get("date", ""),
                tags=tags,
                body_html=md_to_html(body),
                excerpt=make_excerpt(body),
            )
        )
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def tags_html(tags: list[str]) -> str:
    if not tags:
        return ""
    items = "".join(f"<li>{tag}</li>" for tag in tags)
    return f'<ul class="tags" aria-label="Tags">{items}</ul>'


def nav_attrs(current: str | None) -> dict[str, str]:
    """aria-current only on the active top-level nav item."""
    keys = ("home", "projects", "writeups", "contact")
    out = {f"nav_{k}": "" for k in keys}
    if current in keys:
        out[f"nav_{current}"] = ' aria-current="page"'
    return out


def render_chrome(root: str, current: str | None) -> tuple[str, str]:
    attrs = nav_attrs(current)
    header = read_template("header.html").replace("{{ root }}", root)
    for key, value in attrs.items():
        header = header.replace("{{ " + key + " }}", value)
    footer = read_template("footer.html").replace("{{ root }}", root)
    return header, footer


def render_page(
    *,
    title: str,
    content: str,
    root: str,
    current: str | None,
) -> str:
    header, footer = render_chrome(root, current)
    content = content.replace("{{ root }}", root)
    return (
        read_template("base.html")
        .replace("{{ title }}", title)
        .replace("{{ root }}", root)
        .replace("{{ header }}", header)
        .replace("{{ content }}", content)
        .replace("{{ footer }}", footer)
    )


def write_home() -> None:
    content = (CONTENT / "home.html").read_text(encoding="utf-8")
    html = render_page(
        title="Nicklas — portfolio",
        content=content,
        root="",
        current="home",
    )
    (DOCS / "index.html").write_text(html, encoding="utf-8")


def write_projects() -> None:
    content = (CONTENT / "projects.html").read_text(encoding="utf-8")
    out_dir = DOCS / "projects"
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render_page(
        title="Projects — Nicklas",
        content=content,
        root="../",
        current="projects",
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def write_post(post: Post) -> None:
    content = (
        read_template("post.html")
        .replace("{{ title }}", post.title)
        .replace("{{ date }}", post.date)
        .replace("{{ tags_html }}", tags_html(post.tags))
        .replace("{{ body }}", post.body_html)
    )
    html = render_page(
        title=f"{post.title} — Nicklas",
        content=content,
        root="../",
        current="writeups",
    )
    (DOCS / "writeups" / f"{post.slug}.html").write_text(html, encoding="utf-8")


def write_writeups_index(posts: list[Post]) -> None:
    if posts:
        items = []
        for post in posts:
            tags = tags_html(post.tags)
            excerpt = (
                f'<p class="post-list__excerpt">{post.excerpt}</p>'
                if post.excerpt
                else ""
            )
            items.append(
                f'<li class="post-list__item fade-in" data-tags="{" ".join(post.tags)}">'
                f'<h2 class="post-list__title">'
                f'<a href="{post.slug}.html">{post.title}</a></h2>'
                f'<div class="meta"><time datetime="{post.date}">{post.date}</time></div>'
                f"{excerpt}{tags}</li>"
            )
        post_list = "\n  ".join(items)
    else:
        post_list = '<li class="post-list__item">No writeups yet.</li>'

    all_tags = sorted({t for p in posts for t in p.tags})
    tag_filters = "\n  ".join(
        f'<button type="button" class="tag-filter" data-tag="{t}">{t}</button>'
        for t in all_tags
    )

    content = (CONTENT / "writeups" / "index.html").read_text(encoding="utf-8")
    content = content.replace("{{ post_list }}", post_list)
    content = content.replace("{{ tag_filters }}", tag_filters)
    html = render_page(
        title="Writeups — Nicklas",
        content=content,
        root="../",
        current="writeups",
    )
    (DOCS / "writeups" / "index.html").write_text(html, encoding="utf-8")


def copy_assets() -> None:
    dest = DOCS / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSETS, dest)


def clean_docs() -> None:
    if DOCS.exists():
        for child in DOCS.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        DOCS.mkdir(parents=True)

    (DOCS / "writeups").mkdir(parents=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


def main() -> None:
    clean_docs()
    copy_assets()

    posts = load_posts()
    write_home()
    write_projects()
    write_writeups_index(posts)
    for post in posts:
        write_post(post)

    print(f"Built {len(posts)} post(s) into {DOCS}")


if __name__ == "__main__":
    main()
