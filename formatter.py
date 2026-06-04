from __future__ import annotations
import os
import json
from datetime import datetime
from jinja2 import Template

def _cluster_section(cluster):
    imp = cluster.get("impact", "LOW")
    cat = cluster.get("category", "tool")
    if imp == "HIGH":
        return "주요 발표"
    if cat in ["pricing", "policy"]:
        return "가격·정책"
    if cat in ["release", "tool"]:
        return "모델/도구 출시"
    return "선택 읽을거리"

def organize_clusters(clusters):
    sections = {"주요 발표": [], "모델/도구 출시": [], "가격·정책": [], "선택 읽을거리": []}
    for c in clusters:
        sections[_cluster_section(c)].append(c)
    return sections

def generate_markdown(date_str, sections):
    md = f"# AI 뉴스 요약 — {date_str}\n\n"
    for section_name, clusters in sections.items():
        if not clusters:
            continue
        md += f"## {section_name}\n"
        for c in clusters:
            topic = c.get("topic_ko", c.get("cluster_topic", ""))
            md += f"### {topic}\n"
            md += f"{c.get('cluster_summary', '')}\n\n"
            md += f"- 영향도: {c.get('impact', 'LOW')}\n"
            for m in c.get("members", []):
                src_url = m.get("source_url", "")
                src_name = m.get("source", "")
                title = m.get("title_ko", m.get("title", ""))
                if src_url:
                    md += f"  - [{src_name}]({src_url}): {title}\n"
                else:
                    md += f"  - {src_name}: {title}\n"
            md += "\n"
    return md

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #e67e22; margin-top: 30px; border-left: 4px solid #e67e22; padding-left: 10px; }
        h3 { color: #2980b9; margin-top: 20px; }
        .cluster { background: #f9f9f9; padding: 12px; border-radius: 6px; margin: 12px 0; }
        .sources { margin-top: 8px; font-size: 0.9em; color: #7f8c8d; }
        .impact { font-weight: bold; }
        .impact-HIGH { color: #c0392b; }
        .impact-MED { color: #d35400; }
        .impact-LOW { color: #7f8c8d; }
        .source-link { display: block; margin: 2px 0; }
    </style>
</head>
<body>
    <h1>AI 뉴스 요약 — {{ date_str }}</h1>
    {% for section_name, clusters in sections.items() %}
        {% if clusters %}
            <h2>{{ section_name }}</h2>
            {% for c in clusters %}
                <div class="cluster">
                    <h3>{{ c.topic_ko or c.cluster_topic }}</h3>
                    <p>{{ c.cluster_summary }}</p>
                    <p class="impact impact-{{ c.impact }}">{{ c.impact }}</p>
                    <div class="sources">
                    {% for m in c.members %}
                        <span class="source-link">- <a href="{{ m.source_url }}">{{ m.source }}</a>: {{ m.title_ko or m.title }}</span>
                    {% endfor %}
                    </div>
                </div>
            {% endfor %}
        {% endif %}
    {% endfor %}
</body>
</html>
"""

def main():
    input_file = "summarized_items.json"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().hour
    period = "morning" if hour < 14 else "evening"
    
    sections = organize_clusters(clusters)
    markdown_content = generate_markdown(today, sections)
    
    template = Template(HTML_TEMPLATE)
    html_content = template.render(date_str=today, sections=sections)
    
    output_dir = os.path.join("output", today)
    os.makedirs(output_dir, exist_ok=True)
    
    md_path = os.path.join(output_dir, f"{period}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    html_path = os.path.join(output_dir, f"{period}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    archive_data = {
        "date": today,
        "period": period,
        "clusters": clusters,
        "generated_at": datetime.now().isoformat() + "Z"
    }
    archive_path = os.path.join(output_dir, "archive.json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
    print(f"Generated output to {output_dir}")

def format_markdown(clusters: list[dict], period: str, date: datetime) -> str:
    sections = organize_clusters(clusters)
    date_str = date.strftime("%Y-%m-%d")
    return generate_markdown(date_str, sections)

def format_html(clusters: list[dict], period: str, date: datetime) -> str:
    sections = organize_clusters(clusters)
    date_str = date.strftime("%Y-%m-%d")
    template = Template(HTML_TEMPLATE)
    return template.render(date_str=date_str, sections=sections)

if __name__ == "__main__":
    main()
