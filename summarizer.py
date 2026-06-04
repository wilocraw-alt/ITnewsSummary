from __future__ import annotations
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

def get_llm_client():
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        return "openai", OpenAI(**kwargs)
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic", Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    raise ValueError("No LLM API key found in .env (OPENAI_API_KEY or ANTHROPIC_API_KEY)")

def extract_json(text):
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def extract_json_array(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def _llm_call(client_type, client, prompt, model, expect_json=True):
    if client_type == "openai":
        kwargs = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        if expect_json and (model.startswith("gpt") or model.startswith("o")):
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    else:
        response = client.messages.create(
            model=model, max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

def cluster_items(items, client_type, client, model):
    lines = "\n".join(f"{i}. [{item['source']}] {item['title']}" for i, item in enumerate(items))
    prompt = f"""Group the following news items by topic. Items on the same topic (e.g. same model release, same company news) should be in one group.
Return a JSON array of groups. Each group has: "topic" (Korean topic name), "indices" (array of item numbers, 0-based).

Items:
{lines}

Return ONLY valid JSON array:
[{{"topic": "주제명", "indices": [0, 1, 2]}}]"""

    text = _llm_call(client_type, client, prompt, model, expect_json=False)
    groups = extract_json_array(text)
    if not groups:
        print("cluster: LLM returned nothing, using flat grouping")
        return [{"topic": item.get("title", "")[:40], "indices": [i]} for i, item in enumerate(items)]
    return groups

def translate_and_summarize_all(items, groups, client_type, client, model):
    group_blocks = []
    for g in groups:
        idx = g.get("indices", [])
        members = [items[i] for i in idx if i < len(items)]
        if not members:
            continue
        lines = []
        for m in members:
            snippet = (m.get("content", "") or "")[:150].replace("\n", " ")
            lines.append("    - [%s](%s): %s" % (m["source"], m.get("source_url",""), m.get("title","")))
            lines.append("      Content: %s" % snippet)
        block = "  Group \"%s\" (%d items):\n%s" % (g.get("topic",""), len(members), "\n".join(lines))
        group_blocks.append(block)

    all_groups = "\n\n".join(group_blocks)

    prompt = """You are an AI news analyst. Below are news items grouped by topic.

%s

For EACH group:
1. Translate the group topic to Korean
2. Write a combined Korean summary (2-3 sentences) covering all items in the group
3. For EACH item, translate its title to Korean
4. Assign an overall impact per group (HIGH/MED/LOW)
5. Assign a category per group: "pricing" if any item is about pricing, "policy" if any is about policy, otherwise "release"

Return ONLY a JSON array (one element per group, in order):
[
  {
    "topic_ko": "한국어 주제명",
    "cluster_summary": "통합 한국어 요약 (2-3문장)",
    "impact": "HIGH|MED|LOW",
    "category": "release|pricing|policy",
    "members": [
      {"source": "원래 소스명", "title_ko": "한국어 번역 제목", "title_en": "원문 제목", "source_url": "원본 URL"}
    ]
  }
]""" % all_groups

    text = _llm_call(client_type, client, prompt, model, expect_json=False)
    clusters = extract_json_array(text)
    if not clusters:
        print("translate+summarize: LLM returned nothing, building fallback")
        clusters = []
        for g in groups:
            idx = g.get("indices", [])
            members = [items[i] for i in idx if i < len(items)]
            clusters.append({
                "topic_ko": g.get("topic", ""),
                "cluster_summary": "요약 실패",
                "impact": "LOW",
                "category": "release",
                "members": [{"source": m["source"], "title_ko": m.get("title",""), "title_en": m.get("title",""), "source_url": m.get("source_url","")} for m in members]
            })
    return clusters

def main():
    input_file = "raw_items.json"
    output_file = "summarized_items.json"
    
    if not os.path.exists(input_file):
        print("Error: %s not found." % input_file)
        return

    with open(input_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        print("No items to summarize.")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    try:
        client_type, client = get_llm_client()
    except ValueError as e:
        print("Error: %s" % e)
        return

    model = os.getenv("LLM_MODEL", "gpt-4o")

    print("Clustering %d items by topic..." % len(items))
    groups = cluster_items(items, client_type, client, model)
    print("Found %d clusters" % len(groups))

    print("Translating + summarizing all clusters in one request...")
    clusters = translate_and_summarize_all(items, groups, client_type, client, model)

    clusters.sort(key=lambda c: {"HIGH": 0, "MED": 1, "LOW": 2}.get(c.get("impact", "LOW"), 3))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
    print("Done. %d clusters -> %s." % (len(clusters), output_file))

def summarize(raw_items: list[dict], config: dict | None = None) -> list[dict]:
    client_type, client = get_llm_client()
    model = os.getenv("LLM_MODEL", "gpt-4o")
    groups = cluster_items(raw_items, client_type, client, model)
    clusters = translate_and_summarize_all(raw_items, groups, client_type, client, model)
    clusters.sort(key=lambda c: {"HIGH": 0, "MED": 1, "LOW": 2}.get(c.get("impact", "LOW"), 3))
    return clusters

if __name__ == "__main__":
    main()
