#!/usr/bin/env python3
"""Build static HTML for the portfolio + writeups site into docs/."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
POSTS_DIR = CONTENT / "posts"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"

FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z",
    re.DOTALL,
)


@dataclass
class Post:
    slug: str
    title: str
    date: str
    tags: list[str]
    body_html: str


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


def md_to_html(body: str) -> str:
    return markdown.markdown(
        body,
        extensions=["fenced_code", "codehilite"],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,
            }
        },
    )


def load_posts() -> list[Post]:
    posts: list[Post] = []
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
            )
        )
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def tags_html(tags: list[str]) -> str:
    if not tags:
        return ""
    items = "".join(f"<li>{tag}</li>" for tag in tags)
    return f'<ul class="tags">{items}</ul>'


def render_page(
    *,
    title: str,
    content: str,
    assets_prefix: str,
    home_href: str,
    writeups_href: str,
) -> str:
    header = (
        read_template("header.html")
        .replace("{{ home_href }}", home_href)
        .replace("{{ writeups_href }}", writeups_href)
    )
    footer = read_template("footer.html")
    return (
        read_template("base.html")
        .replace("{{ title }}", title)
        .replace("{{ assets_prefix }}", assets_prefix)
        .replace("{{ header }}", header)
        .replace("{{ content }}", content)
        .replace("{{ footer }}", footer)
    )


def write_home() -> None:
    content = (CONTENT / "home.html").read_text(encoding="utf-8")
    html = render_page(
        title="Nicklas",
        content=content,
        assets_prefix="",
        home_href="./",
        writeups_href="writeups/",
    )
    (DOCS / "index.html").write_text(html, encoding="utf-8")


def write_post(post: Post) -> None:
    content = (
        read_template("post.html")
        .replace("{{ title }}", post.title)
        .replace("{{ date }}", post.date)
        .replace("{{ tags_html }}", tags_html(post.tags))
        .replace("{{ body }}", post.body_html)
    )
    html = render_page(
        title=post.title,
        content=content,
        assets_prefix="../",
        home_href="../",
        writeups_href="./",
    )
    out = DOCS / "writeups" / f"{post.slug}.html"
    out.write_text(html, encoding="utf-8")


def write_writeups_index(posts: list[Post]) -> None:
    if posts:
        items = []
        for post in posts:
            tag_bits = ", ".join(post.tags) if post.tags else ""
            meta = post.date
            if tag_bits:
                meta = f"{post.date} · {tag_bits}"
            items.append(
                f'<li><a href="{post.slug}.html">{post.title}</a>'
                f'<div class="meta">{meta}</div></li>'
            )
        post_list = "\n    ".join(items)
    else:
        post_list = "<li>No writeups yet.</li>"

    content = read_template("writeups_index.html").replace(
        "{{ post_list }}", post_list
    )
    html = render_page(
        title="Writeups",
        content=content,
        assets_prefix="../",
        home_href="../",
        writeups_href="./",
    )
    (DOCS / "writeups" / "index.html").write_text(html, encoding="utf-8")


def copy_assets() -> None:
    dest = DOCS / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSETS, dest)


def write_pygments_css() -> None:
    """Generate a dark-friendly Pygments stylesheet into assets (then copied)."""
    css = HtmlFormatter(style="monokai").get_style_defs(".highlight")
    out = ASSETS / "css" / "pygments.css"
    out.write_text(
        "/* Auto-generated by build.py — do not hand-edit */\n" + css + "\n",
        encoding="utf-8",
    )


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
    # Tell GitHub Pages not to run Jekyll on the docs/ tree
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


def main() -> None:
    write_pygments_css()
    clean_docs()
    copy_assets()

    posts = load_posts()
    write_home()
    write_writeups_index(posts)
    for post in posts:
        write_post(post)

    print(f"Built {len(posts)} post(s) into {DOCS}")


if __name__ == "__main__":
    main()
