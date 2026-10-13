#!/usr/bin/env python3
"""Zero-extra-cost GitHub software discovery (stdlib only)."""
import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
CATEGORIES = {
    "AI 与自动化": 'topic:ai-agent OR topic:automation',
    "UI 与开发工具": 'topic:developer-tools OR topic:design-system',
    "商业管理与营销": 'topic:crm OR topic:marketing-automation',
    "安全与平台基础设施": 'topic:authentication OR topic:security',
}
# Search syntax is kept simple to avoid dependence on external packages.
QUERIES = {
    "AI 与自动化": "topic:ai-agent",
    "UI 与开发工具": "topic:developer-tools",
    "商业管理与营销": "topic:crm",
    "安全与平台基础设施": "topic:authentication",
}
MAX_PER_CATEGORY = 15
MAX_REPORT = 12

def github_search(query):
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": MAX_PER_CATEGORY})
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-software-radar/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com/search/repositories?" + params, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response).get("items", [])

def main():
    now = dt.datetime.now(dt.timezone.utc)
    week_ago = (now - dt.timedelta(days=14)).date().isoformat()
    found = {}
    errors = []
    for category, topic in QUERIES.items():
        query = f"{topic} pushed:>={week_ago} archived:false fork:false stars:>=10"
        try:
            results = github_search(query)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            errors.append(f"{category}: {type(exc).__name__} ({str(exc)[:120]})")
            continue
        for item in results:
            key = item["full_name"].lower()
            if key not in found:
                found[key] = {
                    "name": item["full_name"],
                    "url": item["html_url"],
                    "category": category,
                    "description_original": item.get("description") or "",
                    "stars": item.get("stargazers_count", 0),
                    "updated_at": item.get("pushed_at"),
                    "license": (item.get("license") or {}).get("spdx_id") or "未确认",
                    "homepage": item.get("homepage") or "",
                    "language": item.get("language") or "未标注",
                }
    if not found:
        raise SystemExit("采集失败或无候选项目；不覆盖历史结果。 " + "; ".join(errors))
    # Stars are a discovery signal, NOT a quality/security endorsement.
    entries = sorted(found.values(), key=lambda x: (x["stars"], x["name"]), reverse=True)[:MAX_REPORT]
    date = now.date().isoformat()
    lines = [
        f"# GitHub 软件发现清单 · {date}",
        "",
        "> 自动采集的候选项目，不是人工验证或 AI 翻译结果。请勿将 Star 数视作安全、质量或商业授权证明。",
        "",
        f"采集范围：过去 14 天有代码更新，Star ≥ 10；共发现 {len(found)} 个去重候选，展示 {len(entries)} 个。",
        "",
    ]
    for i, p in enumerate(entries, 1):
        desc = (p["description_original"] or "暂无项目简介").replace("\n", " ").replace("|", "/")
        lines += [
            f"## {i}. {p['name']}",
            f"- 类别：{p['category']}",
            f"- 项目链接：{p['url']}",
            f"- 原始简介（可能是英文）：{desc}",
            f"- Star：{p['stars']}；最近提交：{p['updated_at'] or '未知'}",
            f"- 主要语言：{p['language']}；许可证：{p['license']}",
            "- 使用门槛/安全/适用性：**尚未审查，需中文简报进一步分析**。",
            "",
        ]
    if errors:
        lines += ["## 数据采集告警", *["- " + e for e in errors], ""]
    latest = ROOT / "reports" / "latest.md"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "reports" / "latest.json").write_text(json.dumps({
        "generated_at": now.isoformat(), "source": "GitHub Search API",
        "partial_errors": errors, "projects": entries
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(entries)} projects; {len(errors)} category errors")

if __name__ == "__main__":
    main()
