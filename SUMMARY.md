# ITnewsSummary — Clustering Refactor (2026-06-04)

## What Changed

### summarizer.py — Per-item translation → topic clustering + grouped summary

**Before:**
- 40 items sent individually to LLM → 40 separate calls
- Same-topic news scattered across output, redundant summaries
- ~40 min runtime (Ollama gemma4:e4b)

**After:**
1. `cluster_items()` — sends all item titles to LLM in one call → groups by topic
2. `translate_and_summarize_all()` — sends all groups to LLM in a single call → translates titles to Korean + writes grouped Korean summaries + assigns impact/category
3. Result: **40 calls → 2 calls** (1 clustering + 1 translation/summary)
4. Runtime: ~40 min → ~30 seconds

**New functions:**
- `_llm_call()` — shared OpenAI/Anthropic invocation wrapper
- `cluster_items()` — LLM-based topic clustering
- `translate_and_summarize_all()` — single-request translation + summarization for all clusters
- `extract_json_array()` — JSON array extraction from LLM output

### formatter.py — Cluster-aware output format

- `organize_items()` → `organize_clusters()`: section assignment per cluster
- `generate_markdown()`: per-cluster topic heading + combined summary + source list with Korean titles
- HTML template: cluster-based layout (topic, summary, translated source titles)

## Example Clusters (2026-06-04)

| Cluster | Items | Impact |
|---|---|---|
| OpenAI tech expansion & AI governance policy | 5 | HIGH |
| Big tech AI platform integration & industry shift | 8 | HIGH |
| Local LLM & open-source model personalization/optimization | 25 | HIGH |
| Official blog/newsroom update activity | 2 | HIGH |

## Project Structure

```
ITnewsSummary/
├── summarizer.py      # clustering + grouped summary
├── formatter.py       # cluster-aware output
├── main.py            # pipeline orchestrator (unchanged)
├── collector.py       # data collection (unchanged)
├── sender.py          # email sending (unchanged)
├── scripts/
│   ├── run_and_open.sh      # wrapper: run + open HTML in browser
│   ├── schedule_install.sh  # cron/systemd timer installer
│   ├── schedule_uninstall.sh# cron/systemd timer remover
│   └── schedule_check.sh    # verify schedule is active
└── output/YYYY-MM-DD/ # generated Markdown / HTML / JSON
```

## LLM Call Optimization

- **Before**: 40 items × 1 call = 40 calls, ~10-15s each
- **After**: 1 clustering call + 1 translation/summary call = **2 calls total**
- **Savings**: ~95% fewer API calls, ~98% time reduction

## Quick Start

```bash
# Run morning digest
./run.sh morning

# Run evening digest
./run.sh evening

# Auto-detect period (morning before 14:00, evening after)
./run.sh
```

The script sources `.env`, defaults to local Ollama (gemma4:e4b), and runs the full pipeline.

## 스케줄러 (하루 2회 자동 실행)

`scripts/schedule_install.sh` 로 cron 또는 systemd user timer를 설치합니다. 파이프라인 완료 후 HTML을 Windows 기본 브라우저로 엽니다.

```bash
# 설치
scripts/schedule_install.sh

# 상태 확인
scripts/schedule_check.sh

# 제거
scripts/schedule_uninstall.sh

# 수동 실행 (period 생략 시 시간에 따라 자동 선택)
scripts/run_and_open.sh morning
scripts/run_and_open.sh evening

# 크론 환경 시뮬레이션 테스트
env -i HOME=$HOME SHELL=/bin/bash PATH=/usr/local/bin:/usr/bin:/bin scripts/run_and_open.sh morning
```

### 설치 동작

| 시나리오 | 동작 |
|---|---|
| systemd (init 1 = systemd) | user timer: `08:00`, `20:00` |
| 그 외 (cron) | `0 8 * * *` + `0 20 * * *` (기존 crontab 유지) |

### 검증

```bash
# cron 확인
crontab -l

# systemd timer 확인
systemctl --user list-timers

# 실행 로그
tail -f output/cron.log
```

### 주의사항

- cron 서비스가 중지된 상태면 설치 스크립트가 자동으로 건너뛰고 수동 안내를 출력합니다.
- WSL interop이 없는 환경(cron 등)에서는 `WSL_INTEROP`를 `/run/WSL/`에서 자동 탐지합니다.
- 이메일 발송을 원하지 않으면 `EMAIL_RECIPIENTS`를 비워두세요. (`main.py`가 자동 건너뜀)

## Environment

| Variable | Default | Description |
|---|---|---|
| `OPENAI_BASE_URL` | *auto-detected* | `run.sh` probes `localhost:11435` first, falls back to `11434` |
| `OPENAI_API_KEY` | `ollama` | API key |
| `LLM_MODEL` | `gemma4:e4b` | Model name |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS) |
| `SMTP_USER` | — | SMTP login |
| `SMTP_PASSWORD` | — | SMTP password or app password |
| `EMAIL_RECIPIENTS` | — | Comma-separated recipient list |
