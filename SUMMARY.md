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
└── output/YYYY-MM-DD/ # generated Markdown / HTML / JSON
```

## LLM Call Optimization

- **Before**: 40 items × 1 call = 40 calls, ~10-15s each
- **After**: 1 clustering call + 1 translation/summary call = **2 calls total**
- **Savings**: ~95% fewer API calls, ~98% time reduction
