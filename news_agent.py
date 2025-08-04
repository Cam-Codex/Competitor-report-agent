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
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Iterable, List

import feedparser
import jinja2
import yaml
import re
from html import unescape
from typing import Optional

try:
    import openai
except Exception:  # pragma: no cover - openai is optional
    openai = None


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
                lines.append(f"- {art.title}")
                if art.summary:
                    lines.append(f"  {art.summary}")
                lines.append(
                    f"  Potential drawback: {suggest_drawback(art.title, art.summary, art.source)}"
                )
                lines.append(f"  {art.link}")
                lines.append("")
        return "\n".join(lines).strip()


def load_feeds(path: str | Path) -> List[Feed]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    feeds = [Feed(**item) for item in data.get("feeds", [])]
    return feeds


def fetch_feed(feed: Feed) -> Iterable[Article]:
    parsed = feedparser.parse(feed.url)
    for entry in parsed.entries[: feed.max_items]:
        summary = extract_summary(entry)
        yield Article(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            summary=summary,
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


VENDOR_WEAKNESSES = {
    "Databricks": "Databricks Genie emphasizes data engineering but lacks ThoughtSpot's live search-driven analytics.",
    "Snowflake": "Snowflake Cortex targets developers and misses ThoughtSpot's easy natural language queries.",
    "Microsoft": "Power BI and Copilot tie insights to predefined models, unlike ThoughtSpot's flexible search-first UX.",
    "Salesforce": "Tableau dashboards require curation whereas ThoughtSpot enables ad-hoc natural language exploration.",
    "Sigma Computing": "Sigma delivers spreadsheet-style analytics but fewer governed search features than ThoughtSpot.",
    "Qlik": "Qlik's script-heavy approach complicates setup compared to ThoughtSpot's intuitive search.",
    "Looker": "Looker and Gemini depend on LookML modeling while ThoughtSpot queries data directly.",
    "Google": "Google's BI stack is less search-centric than ThoughtSpot's AI-driven analytics.",
}


def suggest_drawback(
    title: str, summary: str | None = None, source: str | None = None
) -> str:
    """Return drawback based on article context, using LLM when available."""
    combined = f"{title} {summary or ''}".strip()
    llm = llm_drawback(combined, source)
    if llm:
        return llm
    hint = extract_drawback_hint(combined)
    if source and source in VENDOR_WEAKNESSES:
        if hint:
            return f"{VENDOR_WEAKNESSES[source]} {hint}"
        return VENDOR_WEAKNESSES[source]
    if hint:
        return hint
    return "Consider cost, adoption effort, and governance implications."


def extract_drawback_hint(text: str) -> Optional[str]:
    """Derive a weakness clue from article text."""
    lower = text.lower()
    if any(k in lower for k in ["security", "breach", "privacy", "compliance"]):
        return "Security and compliance risks remain, an area where ThoughtSpot stresses governance."
    if any(k in lower for k in ["cost", "pricing", "expensive"]):
        return "Pricing could be a concern compared with ThoughtSpot's consumption model."
    if any(k in lower for k in ["complex", "complicated", "learning curve", "training"]):
        return "Complexity may slow adoption versus ThoughtSpot's ease of use."
    if any(k in lower for k in ["integration", "migration", "silo"]):
        return "Integration effort could be higher than ThoughtSpot's straightforward connectivity."
    if any(k in lower for k in ["performance", "latency", "slow"]):
        return "Performance limitations might impede real-time insight, unlike ThoughtSpot's speed."
    return None


def extract_summary(entry: feedparser.FeedParserDict) -> str | None:
    """Pull a longer plain-text summary from common RSS fields."""
    parts: List[str] = []
    for key in ("summary", "description"):
        val = entry.get(key)
        if val:
            parts.append(val)
    if entry.get("content"):
        for c in entry.content:
            if isinstance(c, dict) and c.get("value"):
                parts.append(c["value"])
    if not parts:
        return None
    text = strip_html(" ".join(parts))
    llm = llm_summarize(text)
    if llm:
        return llm
    sentences = re.split(r"(?<=[.!?]) +", text)
    return " ".join(sentences[:2]).strip()


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape entities."""
    clean = re.sub(r"<[^>]+>", "", text)
    return unescape(clean).strip()


def llm_summarize(text: str) -> Optional[str]:
    """Use an LLM to generate a concise summary if an API key is configured."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or openai is None:
        return None
    try:
        # Support both openai v1 and legacy versions
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following article in 2-3 sentences.",
                    },
                    {"role": "user", "content": text[:4000]},
                ],
                max_tokens=120,
                temperature=0.5,
            )
            return resp.choices[0].message.content.strip()
        else:  # legacy API
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following article in 2-3 sentences.",
                    },
                    {"role": "user", "content": text[:4000]},
                ],
                max_tokens=120,
                temperature=0.5,
            )
            return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def llm_drawback(text: str, source: str | None = None) -> Optional[str]:
    """Use an LLM to highlight weaknesses in context of ThoughtSpot."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or openai is None:
        return None
    prompt = (
        "You are an expert on analytics platforms. From the article text, "
        "describe a concrete weakness or challenge for the vendor and, when "
        "relevant, contrast it with ThoughtSpot's capabilities. Respond in 1-2 sentences."
    )
    user_text = f"Vendor: {source or 'Unknown'}\n\n{text[:4000]}"
    try:
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=120,
                temperature=0.5,
            )
            return resp.choices[0].message.content.strip()
        else:
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=120,
                temperature=0.5,
            )
            return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def write_json(digest: Digest, output: Path) -> None:
    """Merge new articles with existing JSON and tag fetch dates."""

    today = date.today().isoformat()
    existing: Dict[str, Dict] = {}

    if output.exists():
        try:
            current = json.loads(output.read_text(encoding="utf-8"))
            for item in current:
                if item.get("link"):
                    existing[item["link"]] = item
        except json.JSONDecodeError:
            pass

    for source, articles in digest.feeds.items():
        for art in articles:
            existing[art.link] = {
                "title": art.title,
                "link": art.link,
                "summary": art.summary,
                "published": art.published,
                "source": art.source,
                "category": art.category,
                "drawbacks": suggest_drawback(art.title, art.summary, art.source),
                "fetched": today,
            }

    merged = list(existing.values())
    merged.sort(key=lambda x: x.get("fetched", ""), reverse=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")


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

