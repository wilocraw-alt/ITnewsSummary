"""
main.py — ITnewsSummary pipeline entry point
Usage: python main.py morning|evening [--date YYYY-MM-DD] [--config PATH]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import openai
import yaml
from dotenv import load_dotenv

load_dotenv(override=True)


def load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _output_dir(base: str, date: datetime) -> Path:
    d = Path(base) / date.strftime("%Y-%m-%d")
    d.mkdir(parents=True, exist_ok=True)
    return d


def step_collect(sources_dir: str, out: Path) -> list[dict]:
    from collector import collect
    return collect(sources_dir, str(out))


def step_summarize(raw_items: list[dict], config: dict, out: Path) -> list[dict]:
    summarized_path = out / "summarized_items.json"
    if summarized_path.exists():
        print(f"[main] summarize: loading cached {summarized_path}")
        with open(summarized_path, encoding="utf-8") as f:
            return json.load(f)

    try:
        from summarizer import summarize
        items = summarize(raw_items, config)
    except ImportError:
        print("[main] summarizer.py not found — passing raw items through", file=sys.stderr)
        items = raw_items
    except (openai.AuthenticationError, openai.APIConnectionError):
        print("[main] LLM 연결에 실패했습니다.", file=sys.stderr)
        print("  ollama가 실행 중인지 확인하세요: `ollama serve`", file=sys.stderr)
        print("  .env의 OPENAI_BASE_URL / OPENAI_API_KEY / LLM_MODEL을 확인하세요.", file=sys.stderr)
        sys.exit(1)

    with open(summarized_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[main] summarize: {len(items)} items → {summarized_path}")
    return items


def step_format(items: list[dict], period: str, date: datetime, out: Path) -> Path:
    md_path = out / f"{period}.md"
    html_path = out / f"{period}.html"

    try:
        from formatter import format_markdown, format_html
        md_content = format_markdown(items, period, date)
        md_path.write_text(md_content, encoding="utf-8")
        print(f"[main] format: wrote {md_path}")

        html_content = format_html(items, period, date)
        html_path.write_text(html_content, encoding="utf-8")
        print(f"[main] format: wrote {html_path}")
    except ImportError:
        content = _minimal_markdown(items, period, date)
        md_path.write_text(content, encoding="utf-8")
        print(f"[main] format: wrote {md_path}")
        print("[main] format: skipping HTML (formatter not available)", file=sys.stderr)

    return md_path


def _minimal_markdown(items: list[dict], period: str, date: datetime) -> str:
    label = "오전" if period == "morning" else "오후"
    lines = [f"# AI 뉴스 요약 — {date.strftime('%Y-%m-%d')} {label}\n"]
    for item in items[:10]:
        title = item.get("title_ko") or item.get("title", "")
        summary = item.get("summary_ko") or item.get("content", "")[:300]
        impact = item.get("impact", "")
        tag = f" `{impact}`" if impact else ""
        lines.append(f"## {title}{tag}\n{summary}\n")
        if item.get("source_url"):
            lines.append(f"출처: {item['source_url']}\n")
    return "\n".join(lines)


def step_archive(items: list[dict], period: str, date: datetime, out: Path) -> None:
    archive = {
        "date": date.strftime("%Y-%m-%d"),
        "period": period,
        "items": items,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = out / "archive.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    print(f"[main] archive: {path}")


def step_send(md_path: Path, period: str, date: datetime) -> None:
    recipients_raw = os.getenv("EMAIL_RECIPIENTS", "").strip()
    if not recipients_raw:
        print("[main] send: EMAIL_RECIPIENTS not set — skipping")
        return

    from sender import send_email
    send_email(
        md_path=str(md_path),
        period=period,
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=os.getenv("SMTP_PORT", "587"),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        recipients=recipients_raw,
        date=date,
    )


def _clear_cache(out: Path) -> None:
    if os.environ.get("KEEP_CACHE") == "1":
        print("[main] cache: KEEP_CACHE=1 — preserving cache files")
        return
    removed = False
    for name in ("raw_items.json", "summarized_items.json"):
        p = out / name
        if p.exists():
            p.unlink()
            print(f"[main] cache: cleared {p}")
            removed = True
    if not removed:
        print("[main] cache: nothing to clear")


def run(period: str, config: dict, date: datetime, sources_dir: str, output_base: str) -> Path:
    out = _output_dir(output_base, date)
    print(f"[main] === {period.upper()} run | {date.strftime('%Y-%m-%d')} | output: {out} ===")

    try:
        raw_items = step_collect(sources_dir, out)
        summ_items = step_summarize(raw_items, config, out)
        md_path = step_format(summ_items, period, date, out)
        step_archive(summ_items, period, date, out)
        step_send(md_path, period, date)
    except SystemExit:
        raise
    except BaseException:
        print("[main] ERROR: run failed — cache preserved for debugging", file=sys.stderr)
        raise

    _clear_cache(out)
    print(f"[main] Done. Output directory: {out}/")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="ITnewsSummary — collect, summarize, format, send")
    parser.add_argument("period", choices=["morning", "evening"], help="Run period")
    parser.add_argument("--date", help="Override date (YYYY-MM-DD)", default=None)
    parser.add_argument("--config", default="sources/config.yaml", help="Config file path")
    parser.add_argument("--sources", default="sources", help="Sources directory")
    parser.add_argument("--output", default="output", help="Output base directory")
    args = parser.parse_args()

    config_path = args.config
    if not Path(config_path).exists():
        print(f"[main] ERROR: config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)

    date = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()

    run(args.period, config, date, args.sources, args.output)


if __name__ == "__main__":
    main()
