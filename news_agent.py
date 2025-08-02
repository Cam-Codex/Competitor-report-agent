#!/usr/bin/env python3
"""Daily news aggregation agent for analytics competitors and trends.

This script fetches articles from a configurable list of RSS feeds,
creates an HTML report, and optionally emails a TLDR digest.

Environment variables for email configuration:
    SMTP_HOST: SMTP server host
    SMTP_PORT: SMTP server port (default: 587)
    SMTP_USER: username for SMTP authentication
    SMTP_PASS: password for SMTP authentication
    EMAIL_FROM: email address of the sender
    EMAIL_TO: comma-separated list of recipients

Usage:
    python news_agent.py --config feeds.yaml --output public/index.html \
        --json frontend/public/articles.json --send-email
"""
from __future__ import annotations

import argparse
import json
import os
import smtplib
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Iterable, List

import feedparser
import jinja2
import yaml


@dataclass
class Article:
    """Representation of a news article."""

    title: str
    link: str
    summary: str | None = None
    published: str | None = None
    source: str | None = None
    category: str | None = None


@dataclass
class Feed:
    """Configuration for a single RSS feed."""

    name: str
    url: str
    max_items: int = 5
    category: str = "vendor"


@dataclass
class Digest:
    """Collection of articles grouped by source."""

    feeds: Dict[str, List[Article]] = field(default_factory=dict)

    def add(self, article: Article) -> None:
        self.feeds.setdefault(article.source or "Unknown", []).append(article)

    def to_text(self) -> str:
        lines: List[str] = []
        for source, articles in self.feeds.items():
            lines.append(f"{source}:")
            for art in articles:
                lines.append(f" - {art.title} ({art.link})")
            lines.append("")
        return "\n".join(lines)


def load_feeds(path: str | Path) -> List[Feed]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    feeds = [Feed(**item) for item in data.get("feeds", [])]
    return feeds


def fetch_feed(feed: Feed) -> Iterable[Article]:
    parsed = feedparser.parse(feed.url)
    for entry in parsed.entries[: feed.max_items]:
        yield Article(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            summary=entry.get("summary"),
            published=entry.get("published"),
            source=feed.name,
            category=feed.category,
        )


def build_digest(feeds: List[Feed]) -> Digest:
    digest = Digest()
    for feed in feeds:
        for article in fetch_feed(feed):
            digest.add(article)
    return digest


def suggest_drawback(title: str) -> str:
    """Generate a simple potential drawback for an article."""
    title_l = title.lower()
    if "ai" in title_l:
        return "May require high compute resources and raise bias concerns."
    if "partnership" in title_l or "integration" in title_l:
        return "Integration complexity and possible vendor lock-in."
    return "Could introduce extra costs or change management challenges."


def write_json(digest: Digest, output: Path) -> None:
    data = []
    for source, articles in digest.feeds.items():
        for art in articles:
            data.append(
                {
                    "title": art.title,
                    "link": art.link,
                    "summary": art.summary,
                    "published": art.published,
                    "source": art.source,
                    "category": art.category,
                    "drawbacks": suggest_drawback(art.title),
                }
            )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(digest: Digest, output: Path) -> None:
    template_str = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <title>Daily Analytics Digest</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        h2 { border-bottom: 1px solid #ccc; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin-bottom: 0.5em; }
      </style>
    </head>
    <body>
    <h1>Daily Analytics Digest</h1>
    {% for source, articles in digest.feeds.items() %}
    <h2>{{ source }}</h2>
    <ul>
      {% for art in articles %}
      <li><a href="{{ art.link }}">{{ art.title }}</a>{% if art.published %} - {{ art.published }}{% endif %}</li>
      {% endfor %}
    </ul>
    {% endfor %}
    </body>
    </html>
    """
    env = jinja2.Environment(autoescape=True)
    tmpl = env.from_string(template_str)
    html = tmpl.render(digest=digest)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def send_email(digest: Digest, subject: str = "Daily Analytics Digest") -> None:
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    sender = os.environ.get("EMAIL_FROM", user)
    recipients = os.environ.get("EMAIL_TO")
    port = int(os.environ.get("SMTP_PORT", "587"))

    if not all([host, user, password, sender, recipients]):
        raise RuntimeError("Missing SMTP or email configuration environment variables")

    msg = MIMEText(digest.to_text())
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipients

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, recipients.split(","), msg.as_string())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analytics news aggregation agent")
    parser.add_argument(
        "--config", default="feeds.yaml", help="Path to YAML file with feed configuration"
    )
    parser.add_argument(
        "--output", default="public/index.html", help="Where to write the HTML report"
    )
    parser.add_argument(
        "--json", help="Path to write JSON data for the React app"
    )
    parser.add_argument(
        "--send-email", action="store_true", help="Email the digest using SMTP settings"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feeds = load_feeds(args.config)
    digest = build_digest(feeds)
    render_html(digest, Path(args.output))
    if args.json:
        write_json(digest, Path(args.json))
    if args.send_email:
        send_email(digest)


if __name__ == "__main__":
    main()

