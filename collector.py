# -*- coding: utf-8 -*-
"""
collector.py - RSS + HTTP scraping, board, dedup, age filter, output raw_items.json
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
MAX_AGE_DAYS = 7
REQUEST_TIMEOUT = 15
REQUEST_RETRIES = 3
REQUEST_BACKOFF = [1, 2, 4]  # seconds between retries
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}
MAX_CONTENT_CHARS = 2000


def _retry_get(url: str, timeout: int, headers: dict | None = None,
               retries: int = REQUEST_RETRIES, backoff: list[int] | None = None) -> requests.Response | None:
    """GET with exponential backoff retry. Returns response on success, None after final failure."""
    if backoff is None:
        backoff = REQUEST_BACKOFF
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers or REQUEST_HEADERS)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                sleep = backoff[min(attempt, len(backoff) - 1)]
                import time
                time.sleep(sleep)
    reason = str(last_exc).split("\n")[0] if last_exc else "unknown"
    print(f"[collector] WARNING: {url} skipped after {retries} retries ({reason})", file=sys.stderr)
    return None


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
    resp = _retry_get(source["url"], REQUEST_TIMEOUT)
    if resp is None:
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


def fetch_board_arca(source: dict) -> list[dict]:
    """Parse an arca.live board listing page into individual article items.

    CSS pattern: each post is expected in an ``<a class="vrow column">``,
    with title, recommend count, view count, author, and published datetime.
    """
    resp = _retry_get(source["url"], REQUEST_TIMEOUT)
    if resp is None:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("a.vrow.column")
    if not rows:
        print(f"[collector] No board rows found for {source['name']}", file=sys.stderr)
        return []

    top_n = int(source.get("top_n", 7))

    items: list[dict] = []
    for row in rows:
        rel = row.get("href", "")
        abs_url = (
            f"https://arca.live{rel}" if rel.startswith("/") else rel
        )

        title_el = row.select_one(".col-title .title")
        title = title_el.get_text(strip=True) if title_el else ""

        id_el = row.select_one(".col-id span")
        post_num = id_el.get_text(strip=True) if id_el else ""

        time_el = row.select_one("time[datetime]")
        published_dt = None
        if time_el:
            try:
                published_dt = datetime.fromisoformat(
                    time_el["datetime"].replace("Z", "+00:00")
                )
            except (ValueError, KeyError):
                pass

        rate_el = row.select_one(".col-rate")
        recommend_count = 0
        if rate_el:
            try:
                recommend_count = int(rate_el.get_text(strip=True))
            except ValueError:
                pass

        view_el = row.select_one(".col-view")
        view_count = 0
        if view_el:
            try:
                view_count = int(view_el.get_text(strip=True))
            except ValueError:
                pass

        author_el = row.select_one(".col-author")
        author = author_el.get_text(" ", strip=True) if author_el else ""

        badge_el = row.select_one(".badge")
        category = badge_el.get_text(strip=True) if badge_el else ""

        if not title:
            continue

        items.append({
            "source": source["name"],
            "source_tier": source.get("tier", 3),
            "source_url": abs_url,
            "title": title,
            "content": "",
            "published": published_dt.isoformat() if published_dt else datetime.now(timezone.utc).isoformat(),
            "category": source.get("category", "community"),
            "region": source.get("region", "kr"),
            "language": source.get("language", "ko"),
            "recommend_count": recommend_count,
            "view_count": view_count,
            "author": author,
            "post_num": post_num,
            "board_category": category,
        })

    items.sort(key=lambda x: x.get("recommend_count", 0), reverse=True)
    items = items[:top_n]

    for item in items:
        _fetch_board_detail(item)

    return items


def fetch_board_discourse(source: dict) -> list[dict]:
    """Parse a Discourse forum via its /latest.json API.

    Source URL should point to the forum root or /latest page;
    the base is derived and ``/latest.json`` is fetched.
    """
    base = source["url"].rstrip("/")
    if base.endswith("/latest"):
        base = base[: -len("/latest")]
    json_url = f"{base}/latest.json"

    resp = _retry_get(json_url, REQUEST_TIMEOUT)
    if resp is None:
        return []

    try:
        data = resp.json()
    except Exception as exc:
        print(f"[collector] Discourse JSON parse error for {source['name']}: {exc}", file=sys.stderr)
        return []

    topics = data.get("topic_list", {}).get("topics", [])
    if not topics:
        print(f"[collector] No Discourse topics found for {source['name']}", file=sys.stderr)
        return []

    top_n = int(source.get("top_n", 7))
    items: list[dict] = []
    for topic in topics[:top_n]:
        tid = topic.get("id")
        slug = topic.get("slug", "")
        title = (topic.get("title") or "").strip()
        if not title or not tid:
            continue

        abs_url = f"{base}/t/{slug}/{tid}"
        created = topic.get("created_at", "")
        published_dt = None
        if created:
            try:
                published_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except (ValueError, KeyError):
                pass

        recommend_count = topic.get("like_count", 0)
        view_count = topic.get("views", 0)
        reply_count = topic.get("reply_count", 0)

        items.append({
            "source": source["name"],
            "source_tier": source.get("tier", 3),
            "source_url": abs_url,
            "title": title,
            "content": "",
            "published": published_dt.isoformat() if published_dt else datetime.now(timezone.utc).isoformat(),
            "category": source.get("category", "community"),
            "region": source.get("region", "kr"),
            "language": source.get("language", "ko"),
            "recommend_count": recommend_count,
            "view_count": view_count,
            "reply_count": reply_count,
            "post_num": "",
            "author": topic.get("posters", [{}])[0].get("description", "") if topic.get("posters") else "",
            "board_category": "",
        })

    return items


def fetch_board(source: dict) -> list[dict]:
    """Dispatch to the correct board parser based on ``board_type``."""
    board_type = source.get("board_type", "arca")
    if board_type == "discourse":
        return fetch_board_discourse(source)
    return fetch_board_arca(source)


def _fetch_board_detail(item: dict) -> None:
    """Fetch and append the full article body for a board post."""
    url = item.get("source_url", "")
    if not url:
        return
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[collector] Board detail fetch error for {url}: {exc}", file=sys.stderr)
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    content_el = soup.select_one(".article-content") or soup.select_one(".fr-view") or soup.select_one("article")
    if content_el:
        text = content_el.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)

    item["content"] = text[:MAX_CONTENT_CHARS]


def _parse_anthropic_date(text: str) -> datetime | None:
    """Parse date strings like 'Jun 3, 2026' or 'May 28, 2026'."""
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    m = re.search(r"([A-Za-z]+)\s+(\d+),\s+(\d{4})", text)
    if not m:
        return None
    month = months.get(m.group(1).lower()[:3])
    if not month:
        return None
    try:
        return datetime(int(m.group(3)), month, int(m.group(2)), tzinfo=timezone.utc)
    except ValueError:
        return None


def fetch_anthropic_news(source: dict) -> list[dict]:
    """Parse Anthropic /news into individual article items.

    The page has two sections:
    1) A featured grid (1 featured + side items).
    2) A publication list with ``<a class="...listItem">`` entries.
    """
    try:
        resp = requests.get(source["url"], timeout=REQUEST_TIMEOUT, headers=REQUEST_HEADERS)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[collector] Anthropic fetch error for {source['name']}: {exc}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    seen_urls: set[str] = set()
    items: list[dict] = []

    def _make_item(url: str, title: str, published: str, blurb: str = "", category: str = "") -> dict | None:
        if not title or url in seen_urls:
            return None
        seen_urls.add(url)
        abs_url = url if url.startswith("http") else f"https://www.anthropic.com{url}"
        return {
            "source": source["name"],
            "source_tier": source.get("tier", 1),
            "source_url": abs_url,
            "title": title,
            "content": blurb[:MAX_CONTENT_CHARS],
            "published": published,
            "category": source.get("category") or category or "release",
            "region": source.get("region", "us"),
            "language": source.get("language", "en"),
        }

    # Section 1: featured grid
    feat_link = soup.select_one("a[class*=\"featuredItem\"]")
    if feat_link:
        href = feat_link.get("href", "")
        h = feat_link.find("h2") or feat_link.find("h3")
        title = h.get_text(strip=True) if h else ""
        time_el = feat_link.find("time")
        date_str = time_el.get_text(strip=True) if time_el else ""
        dt = _parse_anthropic_date(date_str)
        published = dt.isoformat() if dt else datetime.now(timezone.utc).isoformat()
        p = feat_link.find("p")
        blurb = p.get_text(strip=True) if p else ""
        item = _make_item(href, title, published, blurb)
        if item:
            items.append(item)

    # Section 1: side items in featured grid
    side_items = soup.select("a[class*=\"sideLink\"]")
    for a in side_items:
        href = a.get("href", "")
        p = a.find("p")
        blurb = p.get_text(strip=True) if p else ""
        time_el = a.find("time")
        date_str = time_el.get_text(strip=True) if time_el else ""
        dt = _parse_anthropic_date(date_str)
        published = dt.isoformat() if dt else datetime.now(timezone.utc).isoformat()
        item = _make_item(href, blurb, published, blurb=blurb)
        if item:
            items.append(item)

    # Section 2: publication list
    list_items = soup.select("a[class*=\"listItem\"]")
    for a in list_items:
        href = a.get("href", "")
        title_el = a.select_one("span[class*=\"title\"]")
        title = title_el.get_text(strip=True) if title_el else ""
        time_el = a.find("time")
        date_str = time_el.get_text(strip=True) if time_el else ""
        dt = _parse_anthropic_date(date_str)
        published = dt.isoformat() if dt else datetime.now(timezone.utc).isoformat()
        item = _make_item(href, title, published)
        if item:
            items.append(item)

    return items


def filter_by_age(items: list[dict], max_age_days: int = MAX_AGE_DAYS) -> list[dict]:
    """Remove items whose ``published`` is older than ``max_age_days``."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    kept: list[dict] = []
    for item in items:
        pub_str = item.get("published", "")
        if not pub_str:
            kept.append(item)
            continue
        try:
            pub_dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if pub_dt >= cutoff:
                kept.append(item)
        except (ValueError, TypeError):
            kept.append(item)
    return kept


def _item_id(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{datetime.now(timezone.utc).strftime('%Y%m%d')}-{h}"


def load_sources(sources_dir: str) -> list[dict]:
    path = Path(sources_dir) / "sources.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def collect(sources_dir: str, output_dir: str) -> list[dict]:
    """Fetch all sources, dedup, age-filter, write raw_items.json."""
    sources = load_sources(sources_dir)
    cutoff_hours = CUTOFF_HOURS
    max_age_days = MAX_AGE_DAYS

    config_path = Path(sources_dir) / "config.yaml"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        collector_cfg = cfg.get("collector", {})
        cutoff_hours = int(collector_cfg.get("cutoff_hours", CUTOFF_HOURS))
        max_age_days = int(collector_cfg.get("max_age_days", MAX_AGE_DAYS))

    cutoff = datetime.now(timezone.utc) - timedelta(hours=cutoff_hours)

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
        elif src_type == "board":
            fetched = fetch_board(source)
        elif src_type == "anthropic_news":
            fetched = fetch_anthropic_news(source)
        else:
            print(f"[collector] Unknown source type '{src_type}' for {source['name']}", file=sys.stderr)
            continue

        for item in fetched:
            if item["source_url"] not in seen_urls:
                seen_urls.add(item["source_url"])
                item["id"] = _item_id(item["source_url"])
                new_items.append(item)

    age_filtered = filter_by_age(new_items, max_age_days)
    skipped = len(new_items) - len(age_filtered)
    if skipped:
        print(f"[collector] age filter: removed {skipped} items older than {max_age_days} days")

    all_items = existing + age_filtered
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"[collector] {len(age_filtered)} new (age-filtered), {len(all_items)} total → {raw_path}")
    return all_items


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect AI news items")
    parser.add_argument("--sources", default="sources", help="sources/ directory")
    parser.add_argument("--output", required=True, help="output directory for this run")
    args = parser.parse_args()

    items = collect(args.sources, args.output)
    print(f"[collector] Done: {len(items)} items")
