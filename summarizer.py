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

def summarize_cluster(items, cluster, client_type, client, model):
    idx = cluster.get("indices", [])
    members = [items[i] for i in idx if i < len(items)]
    if not members:
        return None

    titles = "\n".join(f"- [{m['source']}] {m.get('title', '')}" for m in members)
    content_snippet = "\n".join(f"- {m.get('content','')[:200]}" for m in members[:3])

    prompt = f"""You are an AI news analyst. The following news items are all about the same topic: "{cluster.get('topic', '')}".

Titles:
{titles}

Content excerpts:
{content_snippet}

Write a COMBINED Korean summary that covers ALL these items together in 2-3 sentences. Include the key facts from each source. Then assign an overall impact level (HIGH/MED/LOW).
Return ONLY:
{{"cluster_summary": "통합 한국어 요약", "impact": "HIGH|MED|LOW", "topic_ko": "한국어 주제명"}}"""

    text = _llm_call(client_type, client, prompt, model)
    result = extract_json(text)
    if not result:
        return {
            "cluster_summary": "요약 실패",
            "impact": "LOW",
            "topic_ko": cluster.get("topic", ""),
            "members": [{"source": m["source"], "title": m.get("title",""), "source_url": m.get("source_url",""), "source_tier": m.get("source_tier",3)} for m in members]
        }

    result["members"] = [{"source": m["source"], "title": m.get("title",""), "source_url": m.get("source_url",""), "source_tier": m.get("source_tier",3)} for m in members]
    return result

def main():
    input_file = "raw_items.json"
    output_file = "summarized_items.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
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
        print(f"Error: {e}")
        return

    model = os.getenv("LLM_MODEL", "gpt-4o")

    print(f"Clustering {len(items)} items by topic...")
    groups = cluster_items(items, client_type, client, model)
    print(f"Found {len(groups)} clusters")

    clusters = []
    for g in groups:
        result = summarize_cluster(items, g, client_type, client, model)
        if result:
            category = "release"
            for idx in g.get("indices", []):
                if idx < len(items):
                    cat = items[idx].get("category", "")
                    if cat == "pricing":
                        category = "pricing"
                    elif cat == "policy" and category != "pricing":
                        category = "policy"
            result["category"] = category
            clusters.append(result)
            print(f"  [{result.get('impact','?')}] {result.get('topic_ko','')[:40]}")

    clusters.sort(key=lambda c: {"HIGH": 0, "MED": 1, "LOW": 2}.get(c.get("impact", "LOW"), 3))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
    print(f"Done. {len(clusters)} clusters → {output_file}.")

def summarize(raw_items: list[dict], config: dict | None = None) -> list[dict]:
    client_type, client = get_llm_client()
    model = os.getenv("LLM_MODEL", "gpt-4o")
    groups = cluster_items(raw_items, client_type, client, model)
    clusters = []
    for g in groups:
        result = summarize_cluster(raw_items, g, client_type, client, model)
        if result:
            category = "release"
            for idx in g.get("indices", []):
                if idx < len(raw_items):
                    cat = raw_items[idx].get("category", "")
                    if cat == "pricing":
                        category = "pricing"
                    elif cat == "policy" and category != "pricing":
                        category = "policy"
            result["category"] = category
            clusters.append(result)
    clusters.sort(key=lambda c: {"HIGH": 0, "MED": 1, "LOW": 2}.get(c.get("impact", "LOW"), 3))
    return clusters

if __name__ == "__main__":
    main()
