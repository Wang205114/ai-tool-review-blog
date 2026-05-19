"""
Step 1: Research trending AI topics via web search + DeepSeek analysis.
"""
import sys, json, re
from datetime import date
from ddgs import DDGS
from agent.config import EXISTING_TITLES, SITE

SEARCH_QUERIES = [
    "AI tools trending 2026 best new",
    "best AI tools this month comparison review",
    "AI tool review site most searched keywords",
    "top AI software 2026 compared",
    "new AI product launch this month rated",
    "best AI tool for productivity writing coding image",
]


def search_web(query: str, max_results: int = 10) -> list[dict]:
    """Search DuckDuckGo and return results."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "").strip()
                if title and len(title) > 5:
                    results.append({
                        "title": title,
                        "snippet": r.get("body", "")[:300],
                        "url": r.get("href", ""),
                    })
    except Exception as e:
        print(f"  Search error for '{query}': {e}")
    return results


def call_deepseek(prompt: str) -> str:
    """Call DeepSeek API."""
    import httpx
    from agent.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL

    if not DEEPSEEK_API_KEY:
        print("  DEEPSEEK_API_KEY not set!")
        sys.exit(1)

    resp = httpx.post(
        DEEPSEEK_API_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are an AI trend analyst. Output only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 2000,
            "temperature": 0.5,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def analyze_search_results(all_results: list[dict]) -> str:
    """Use DeepSeek to pick the best 3 topics from search results."""
    snippets = "\n".join(
        f"- {r['title']}: {r['snippet'][:200]}"
        for r in all_results[:30]
    )

    prompt = f"""You are a content strategist for {SITE['name']} ({SITE['domain']}).

Existing articles on the site:
{chr(10).join(f'- {t}' for t in EXISTING_TITLES)}

From the search results below, select 3 topics that:
1. Are NOT already covered by existing articles
2. Have high search volume / trending potential
3. Would drive organic traffic as comparison or review articles
4. Are about specific AI tools (not general AI news)

Search results:
{snippets}

Return a JSON array of exactly 3 topic objects:
[
  {{
    "title": "SEO-optimized article title with primary keyword",
    "keywords": "primary keyword phrase for SEO",
    "category": "AI Writing | AI Image | AI Coding | AI Video | AI Productivity | AI SEO | AI Assistants | AI Marketing",
    "angle": "The unique angle for this article",
    "tools_covered": ["Tool1", "Tool2", ...],
    "search_volume_estimate": "High | Medium | Low",
    "rationale": "Why this will drive traffic"
  }}
]

Return ONLY valid JSON, no other text."""
    return call_deepseek(prompt)


def fallback_topics() -> list[dict]:
    """Fallback topics if web search + DeepSeek fails."""
    return [
        {
            "title": "Cline vs Cursor vs Windsurf: Best AI Coding IDE 2026",
            "keywords": "AI coding IDE comparison 2026",
            "category": "AI Coding",
            "angle": "Compare Cline, Cursor and Windsurf on code quality, features, and pricing for developers",
            "tools_covered": ["Cline", "Cursor", "Windsurf"],
            "search_volume_estimate": "High",
            "rationale": "AI coding IDEs are highly searched; site only covers GitHub Copilot",
        },
        {
            "title": "Perplexity AI vs Google Gemini: Best AI Search Engine 2026",
            "keywords": "AI search engine comparison 2026",
            "category": "AI Productivity",
            "angle": "Compare Perplexity and Gemini on search accuracy, source quality, and research workflows",
            "tools_covered": ["Perplexity", "Google Gemini"],
            "search_volume_estimate": "High",
            "rationale": "AI-powered search is a rapidly growing category not yet covered",
        },
        {
            "title": "Suno AI vs Udio: Best AI Music Generator 2026",
            "keywords": "AI music generator comparison 2026",
            "category": "AI Video",
            "angle": "Compare Suno and Udio on audio quality, style control, and pricing for creators",
            "tools_covered": ["Suno", "Udio"],
            "search_volume_estimate": "Medium",
            "rationale": "AI music generation is a trending niche with growing search volume",
        },
    ]


def run() -> list[dict]:
    """Main research step. Returns list of 3 topic dicts."""
    print("  Searching for trending AI topics...")
    all_results = []
    seen_urls = set()
    for q in SEARCH_QUERIES:
        results = search_web(q)
        for r in results:
            if r["url"] and r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)
        print(f"    '{q}' -> {len(results)} results")

    print(f"\n  Total unique results: {len(all_results)}")
    print("  Analyzing with DeepSeek to select best 3 topics...")

    topics = None
    if all_results:
        try:
            raw = analyze_search_results(all_results)
            json_match = re.search(r"\[.*\]", raw, re.DOTALL)
            if json_match:
                topics = json.loads(json_match.group())
            else:
                topics = json.loads(raw)
        except Exception as e:
            print(f"  DeepSeek analysis failed: {e}")
            if 'raw' in dir():
                print(f"  Raw: {raw[:300]}")

    if not topics or len(topics) < 3:
        print("  Using fallback topics")
        topics = fallback_topics()

    topics = topics[:3]
    print(f"\n  Selected {len(topics)} topics:")
    for t in topics:
        print(f"    - {t['title']}")
        print(f"      Category: {t['category']} | Volume: {t.get('search_volume_estimate', 'N/A')}")
    return topics


if __name__ == "__main__":
    topics = run()
    print(json.dumps(topics, indent=2, ensure_ascii=False))
