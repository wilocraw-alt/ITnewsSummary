"""
collector.py — RSS + HTTP scraping, dedup, output raw_items.json
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup


CUTOFF_HOURS = 24
REQUEST_TIMEOUT = 15
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}
MAX_CONTENT_CHARS = 2000

CATEGORY_KEYWORDS = {
    "pricing": ["price", "pricing", "cost", "subscription", "discount", "promo",
                "free", "plan", "billing", "tier", "token price", "api cost",
                "가격", "요금", "프로모션", "할인", "구독"],
    "release": ["release", "launch", "announc", "introduc", "new model", "version",
                "update", "upgrade", "출시", "발표", "업데이트"],
    "research": ["research", "paper", "study", "arxiv", "benchmark", "eval",
                 "논문", "연구", "벤치마크"],
    "policy": ["policy", "regulation", "law", "governance", "safety", "act",
               "정책", "규제", "법안", "안전"],
}


def detect_category(text: str) -> str:
    t = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return cat
    return "tool"


def _parse_published(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def fetch_rss(source: dict, cutoff: datetime) -> list[dict]:
    try:
        feed = feedparser.parse(source["url"])
    except Exception as exc:
        print(f"[collector] RSS parse error for {source['name']}: {exc}", file=sys.stderr)
        return []

    items = []
    for entry in feed.entries:
        published = _parse_published(entry)
        if published and published < cutoff:
            continue

        raw_content = ""
        if hasattr(entry, "summary"):
            raw_content = entry.summary
        elif hasattr(entry, "content"):
            raw_content = entry.content[0].value if entry.content else ""

        text = BeautifulSoup(raw_content, "html.parser").get_text(separator=" ", strip=True)
        # feedparser entries support both attribute and dict access
        title = str(getattr(entry, "title", "") or "").strip()
        url = str(getattr(entry, "link", "") or "").strip()
        if not url:
            continue

        items.append({
            "source": source["name"],
            "source_tier": source.get("tier", 2),
            "source_url": url,
            "title": title,
            "content": text[:MAX_CONTENT_CHARS],
            "published": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
            "category": source.get("category") if source.get("category") not in (None, "media") else detect_category(title + " " + text),
            "region": source.get("region", "us"),
            "language": source.get("language", "en"),
        })
    return items


def fetch_http(source: dict) -> list[dict]:
    try:
        resp = requests.get(source["url"], timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[collector] HTTP fetch error for {source['name']}: {exc}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)[:MAX_CONTENT_CHARS]

    return [{
        "source": source["name"],
        "source_tier": source.get("tier", 2),
        "source_url": source["url"],
        "title": f"{source['name']} 최신 정보",
        "content": text,
        "published": datetime.now(timezone.utc).isoformat(),
        "category": source.get("category") if source.get("category") not in (None, "media") else detect_category(source["name"] + " " + text),
        "region": source.get("region", "us"),
        "language": source.get("language", "en"),
    }]


def _item_id(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d')}-{h}"


def load_sources(sources_dir: str) -> list[dict]:
    path = Path(sources_dir) / "sources.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def collect(sources_dir: str, output_dir: str) -> list[dict]:
    """Fetch all sources, dedup, write raw_items.json. Returns combined item list."""
    sources = load_sources(sources_dir)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)

    raw_path = Path(output_dir) / "raw_items.json"
    if raw_path.exists():
        with open(raw_path, encoding="utf-8") as f:
            existing = json.load(f)
        seen_urls: set[str] = {item["source_url"] for item in existing}
    else:
        existing = []
        seen_urls = set()

    new_items: list[dict] = []
    for source in sources:
        src_type = source.get("type", "rss").lower()
        if src_type == "rss":
            fetched = fetch_rss(source, cutoff)
        elif src_type in ("http", "html"):
            fetched = fetch_http(source)
        else:
            print(f"[collector] Unknown source type '{src_type}' for {source['name']}", file=sys.stderr)
            continue

        for item in fetched:
            if item["source_url"] not in seen_urls:
                seen_urls.add(item["source_url"])
                item["id"] = _item_id(item["source_url"])
                new_items.append(item)

    all_items = existing + new_items
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"[collector] {len(new_items)} new, {len(all_items)} total → {raw_path}")
    return all_items


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect AI news items")
    parser.add_argument("--sources", default="sources", help="sources/ directory")
    parser.add_argument("--output", required=True, help="output directory for this run")
    args = parser.parse_args()

    items = collect(args.sources, args.output)
    print(f"[collector] Done: {len(items)} items")
