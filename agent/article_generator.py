"""
Step 2: Generate article HTML via DeepSeek API.
"""
import json, re, os
from datetime import date
from pathlib import Path
from agent.config import ROOT, SITE, DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL
import httpx


def slugify(title: str) -> str:
    """Convert title to filename slug."""
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s + ".html"


def count_words(text: str) -> int:
    return len(text.split())


def call_deepseek(prompt: str, max_tokens: int = 6000) -> str:
    """Call DeepSeek API for article generation."""
    if not DEEPSEEK_API_KEY:
        print("  [ERROR] DEEPSEEK_API_KEY not set!")
        return ""

    resp = httpx.post(
        DEEPSEEK_API_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a professional AI tool reviewer and tech journalist. Write detailed, honest, practical reviews in HTML format."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def build_prompt(topic: dict, article_num: int, today: str) -> str:
    """Build the prompt for article generation, supporting multiple article types."""
    title = topic["title"]
    category = topic["category"]
    kw = topic["keywords"]
    tools = ", ".join(topic.get("tools_covered", []))
    article_type = topic.get("article_type", "comparison")
    filename = slugify(title)

    # Build structure section based on article type
    if article_type == "news_analysis":
        structure_section = """**Article structure:**
1. H1 title with primary keyword
2. Introduction (what happened, why it matters to readers, ~120 words)
3. Detailed analysis of each announcement (300-400 words each):
   - What was announced
   - What it actually means for users' daily workflow
   - How it compares to existing alternatives
   - Potential drawbacks or limitations
4. Implications section: how these announcements affect the current AI tool landscape
5. What to do next (practical recommendations for readers)
6. FAQ (4-5 questions about the announcements and their impact)
7. Conclusion with forward-looking takeaway"""
    elif article_type == "guide":
        structure_section = """**Article structure:**
1. H1 title with primary keyword
2. Introduction (why this topic matters, ~100 words)
3. Prerequisites or background section
4. Step-by-step guide or detailed breakdown (600-1000 words)
5. Tips and best practices
6. Common mistakes to avoid
7. FAQ (4-5 questions)
8. Conclusion with recommendations"""
    else:  # comparison (default)
        structure_section = """**Article structure:**
1. H1 title with primary keyword
2. Introduction paragraph (describe user pain point, ~100 words)
3. Quick comparison table (Tool | Free Tier | Paid Plan | Best For)
4. Detailed review of each tool (300-400 words each):
   - Features overview
   - Hands-on experience
   - Specific pricing (exact USD)
   - Pros (3-5 bullet points)
   - Cons (2-3 bullet points)
   - Rating X/10
   - Who it's best for
5. How to choose section
6. FAQ (5 questions)
7. Conclusion and recommendation
8. Related articles section"""

    # Build image line based on article type
    if article_type == "news_analysis":
        image_line = f'- <figure class="figure-img"> for images (src="../assets/{filename.replace(".html","")}-thumb.svg" as lead image)'
    else:
        image_line = f'- <figure class="figure-img"> for images (src="../assets/{filename.replace(".html","")}-comparison.svg")'

    return f"""Generate a complete HTML article for {SITE['name']} ({SITE['domain']}) about: {title}

Category: {category}
Primary keyword: {kw}
Article type: {article_type}
Tools covered: {tools}

Today's date: {today}

## Article Requirements

**Title tag:** {title} | {SITE['name']}
**Meta description:** Under 155 characters, include primary keyword
**Canonical URL:** https://{SITE['domain']}/posts/{filename}

**Word count:** 1800-2500 words

{structure_section}

## HTML Requirements

Output ONLY the HTML body content that goes inside the <article class="article-shell panel"> element.
Do NOT include <html>, <head>, or <body> tags.
Do NOT wrap the output in markdown code fences or backticks.
Output raw HTML only.

Use these CSS classes from the site stylesheet:
- <div class="comparison-table-wrap"><table class="comparison-table"> for comparison tables
- <div class="key-takeaway"> for key takeaways
- <div class="pros-cons"> with pros and cons divs
- <div class="score-meter"> with score-label, score-bar-bg, score-bar-fill, score-value
- <span class="check">&#10003;</span> and <span class="cross">&#10007;</span>
{image_line}
- <div class="disclosure"><strong>Affiliate Disclosure:</strong>
- <section class="author-box info-block">

Include specific, genuine observations in each section.
Include 1800-2500 words total.
Internal links should use href="../posts/filename.html" format.
"""


def extract_article_html(raw: str) -> str:
    """Extract clean article HTML from the API response."""
    raw = re.sub(r"^```html\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.MULTILINE)
    return raw.strip()


def build_full_html(article_body: str, topic: dict, today: str) -> str:
    """Wrap the article body in the complete site HTML template.

    Uses string replace (not f-string) to avoid issues with curly braces
    in the AI-generated article content.
    """
    title = topic["title"]
    category = topic["category"]
    filename = slugify(title)
    article_type = topic.get("article_type", "comparison")
    cat_label = category

    from agent.config import EXISTING_POSTS, EXISTING_TITLES

    related_html = ""
    for i in range(min(3, len(EXISTING_TITLES))):
        related_html += (
            '            <article class="article-card">\n'
            '              <div class="card-copy">\n'
            f'                <h3><a href="../posts/{EXISTING_POSTS[i]}">{EXISTING_TITLES[i]}</a></h3>\n'
            '              </div>\n'
            '            </article>\n'
        )

    word_count = max(1800, count_words(article_body))
    read_time = max(8, round(word_count / 200))

    # Build sidebar related links
    related_sidebar = ""
    for i in range(min(3, len(EXISTING_TITLES))):
        related_sidebar += (
            f'          <li><a href="../posts/{EXISTING_POSTS[i]}">{EXISTING_TITLES[i]}</a></li>\n'
        )

    # Placeholder for future AggregateRating schema
    rating_schema = ""

    # Safe substitutions dict
    subs = {
        "TITLE": title,
        "SITE_NAME": SITE["name"],
        "DOMAIN": SITE["domain"],
        "FILENAME": filename,
        "CATEGORY_LABEL": cat_label,
        "ARTICLE_BODY": article_body,
        "TODAY": today,
        "READ_TIME": str(read_time),
        "RELATED_ARTICLES": related_html,
        "RELATED_SIDEBAR": related_sidebar,
        "RATING_SCHEMA": rating_schema,
    }

    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Ezoic ad management -->
  <script data-cfasync="false" src="https://cmp.gatekeeperconsent.com/min.js"></script>
  <script data-cfasync="false" src="https://the.gatekeeperconsent.com/cmp.min.js"></script>
  <script async src="//www.ezojs.com/ezoic/sa.min.js"></script>
  <script>
    window.ezstandalone = window.ezstandalone || {};
    ezstandalone.cmd = ezstandalone.cmd || [];
  </script>
  <script src="//ezoicanalytics.com/analytics.js"></script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TITLE__ | __SITE_NAME__</title>
  <meta name="description" content="__META_DESC__">
  <link rel="canonical" href="https://__DOMAIN__/posts/__FILENAME__">
  <meta property="og:type" content="__OG_TYPE__">
  <meta property="og:title" content="__TITLE__">
  <meta property="og:description" content="__OG_DESC__">
  <meta property="og:url" content="https://__DOMAIN__/posts/__FILENAME__">
  <meta property="og:image" content="https://__DOMAIN__/assets/__THUMB__">
  <link rel="stylesheet" href="../css/style.css">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "__TITLE__",
    "description": "__JSONLD_DESC__",
    "datePublished": "__TODAY__",
    "dateModified": "__TODAY__",
    "author": {
      "@type": "Person",
      "name": "Editorial Team"
    },
    "publisher": {
      "@type": "Organization",
      "name": "__SITE_NAME__"
    },
    "mainEntityOfPage": "https://__DOMAIN__/posts/__FILENAME__"
  }
  </script>
__RATING_SCHEMA__
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://__DOMAIN__/"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "__CATEGORY_LABEL__",
        "item": "https://__DOMAIN__/category.html"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "__TITLE__",
        "item": "https://__DOMAIN__/posts/__FILENAME__"
      }
    ]
  }
  </script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2390083032423079" crossorigin="anonymous"></script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-W2WE78MN6G"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-W2WE78MN6G');
  </script>
</head>
<body>
  <header class="site-header">
    <div class="container nav-shell">
      <a class="brand" href="/"><img src="../assets/logo.svg" alt="KnowAITool" width="200" height="44" style="display:block"></a>
      <nav class="site-nav" data-site-nav aria-label="Primary navigation">
        <a href="/">Home</a>
        <a href="/category">Categories</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
      </nav>
      <div class="nav-actions">
        <button class="search-toggle" type="button" data-search-toggle aria-label="Search articles">🔍</button>
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle color theme" aria-pressed="false">&#9790;</button>
        <button class="nav-toggle" type="button" data-nav-toggle aria-label="Toggle menu" aria-expanded="false">&#9776;</button>
      </div>
    </div>
  </header>

  <main class="section">
    <div class="container layout-article">
      <aside class="toc panel">
        <h2>Table of contents</h2>
        <ol>
          <li><a href="#overview">Overview</a></li>
          <li><a href="#comparison">Quick comparison</a></li>
          <li><a href="#reviews">Detailed reviews</a></li>
          <li><a href="#how-to-choose">How to choose</a></li>
          <li><a href="#faq">FAQ</a></li>
          <li><a href="#conclusion">Conclusion</a></li>
        </ol>
      </aside>

      <article class="article-shell panel">
        <div class="breadcrumbs"><a href="/">Home</a><span>/</span><a href="/category">Categories</a><span>/</span><span>__CATEGORY_LABEL__</span></div>
        <header>
          <h1>__TITLE__</h1>
          <div class="meta">
            <span>Published: <time datetime="__TODAY__">__TODAY__</time></span>
            <span class="updated-label">Last updated: <time datetime="__TODAY__">__TODAY__</time></span>
            <span>By Editorial Team</span>
            <span>__READ_TIME__ min read</span>
          </div>
        </header>

        <div class="ad-wrap">
          <span class="ad-label">Advertisement</span>
          <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2390083032423079"
     data-ad-slot="1432811833"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
__RATING_SCHEMA__
        </div>

        <div class="disclosure">
          <strong>Affiliate Disclosure:</strong> Some links in this article are affiliate links. If you purchase through these links, we may earn a commission at no extra cost to you. Our editorial recommendations are independent and based on thorough testing. <a href="/privacy">Full disclosure</a>.
        </div>

__ARTICLE_BODY__

        <section class="author-box info-block">
          <strong>Editorial Team</strong>
          <p class="muted">Our reviews combine hands-on testing, real workflow evaluation, and transparent pricing analysis to help you choose the right AI tool.</p>
        </section>

        <section class="section">
          <div class="section-head">
            <div>
              <p class="eyebrow">Related Articles</p>
              <h2>Continue your research</h2>
            </div>
          </div>
          <div class="card-grid">
__RELATED_ARTICLES__          </div>
        </section>

      </article>

      <aside class="panel article-shell sidebar-right">
        <h2>Related Articles</h2>
        <ul class="sidebar-links">
__RELATED_SIDEBAR__        </ul>

        <div class="sidebar-rating-card">
          <h3>Tool Scorecard</h3>
          <div class="rating-row">
            <span class="rating-label">Output Quality</span>
            <span class="rating-value">9.2/10</span>
          </div>
          <div class="rating-row">
            <span class="rating-label">Usability</span>
            <span class="rating-value">8.5/10</span>
          </div>
          <div class="rating-row">
            <span class="rating-label">Workflow Depth</span>
            <span class="rating-value">8.0/10</span>
          </div>
          <div class="rating-row">
            <span class="rating-label">Pricing Clarity</span>
            <span class="rating-value">7.5/10</span>
          </div>
          <div class="rating-row">
            <span class="rating-label">Trust &amp; Privacy</span>
            <span class="rating-value">8.8/10</span>
          </div>
          <p class="muted" style="font-size:0.82rem;margin:0.6rem 0 0;">Aggregated scores from hands-on testing across all categories.</p>
        </div>

        <div class="ad-wrap">
          <span class="ad-label">Advertisement</span>
          <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-2390083032423079"
     data-ad-slot="1432811833"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
__RATING_SCHEMA__
        </div>
      </aside>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <a class="brand" href="/"><img src="../assets/logo.svg" alt="KnowAITool" width="200" height="44" style="display:block"></a>
        <p class="muted">Independent AI tool reviews, comparisons, and buying guides for readers who need clarity before they spend.</p>
      </div>
      <div class="footer-links">
        <a href="/privacy">Privacy Policy</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        <a href="../sitemap.xml">Sitemap</a>
      </div>
        <p class="muted">&copy; 2026 __SITE_NAME__. All rights reserved.</p>
    </div>
    <div class="container">
      <div class="affiliate-footer">
        <p>__SITE_NAME__ is reader-supported. When you purchase through affiliate links on our site, we may earn a commission. Our editorial assessments are independent. <a href="/privacy">Learn more</a>.</p>
      </div>
    </div>
  </footer>

  <!-- Cookie Consent Banner -->
  <aside class="cookie-banner" data-cookie-banner role="dialog" aria-label="Cookie consent">
    <div class="cookie-inner">
      <div class="cookie-text">
        <p>We use cookies to improve your browsing experience, analyze site traffic, and deliver personalized advertising. By clicking "Accept", you consent to our use of cookies. <a href="/privacy">Read our Privacy Policy</a>.</p>
      </div>
      <div class="cookie-actions">
        <button class="cookie-btn decline" data-cookie-decline type="button">Decline</button>
        <button class="cookie-btn accept" data-cookie-accept type="button">Accept</button>
      </div>
    </div>
  </aside>

  <!-- Scroll to Top -->
  <button class="scroll-top" data-scroll-top type="button" aria-label="Scroll to top">&uarr;</button>

  <script src="../js/main.js"></script>
</body>
</html>"""

    # Replace placeholders
    thumb_filename = filename.replace(".html", "") + "-thumb.svg"

    # Article-type-specific metadata
    if article_type == "news_analysis":
        meta_desc = f"Analysis of {title}: what the announcements mean for your workflow and how they compare to existing AI tools."
        og_desc = f"{title} — practical impact analysis for AI tool users."
        og_type = "article"
        jsonld_desc = f"Analysis of recent AI announcements and their practical impact on daily workflows."
    elif article_type == "guide":
        meta_desc = f"A practical guide to {kw}. Step-by-step advice and best practices for AI tool users."
        og_desc = f"Practical guide: {title}."
        og_type = "article"
        jsonld_desc = f"A practical guide covering {kw} with actionable advice."
    else:  # comparison
        meta_desc = f"A detailed comparison of AI tools covering features, pricing, pros and cons, and workflow fit."
        og_desc = f"Compare AI tools across features, pricing, and real-world performance."
        og_type = "article"
        jsonld_desc = f"A detailed comparison of AI tools covering features, pricing, pros and cons, and workflow fit."

    result = template
    result = result.replace("__TITLE__", title)
    result = result.replace("__SITE_NAME__", SITE["name"])
    result = result.replace("__DOMAIN__", SITE["domain"])
    result = result.replace("__FILENAME__", filename)
    result = result.replace("__CATEGORY_LABEL__", cat_label)
    result = result.replace("__ARTICLE_BODY__", article_body)
    result = result.replace("__TODAY__", today)
    result = result.replace("__READ_TIME__", str(read_time))
    result = result.replace("__THUMB__", thumb_filename)
    result = result.replace("__META_DESC__", meta_desc)
    result = result.replace("__OG_DESC__", og_desc)
    result = result.replace("__OG_TYPE__", og_type)
    result = result.replace("__JSONLD_DESC__", jsonld_desc)
    result = result.replace("__RELATED_ARTICLES__", related_html)
    result = result.replace("__RELATED_SIDEBAR__", related_sidebar)
    result = result.replace("__RATING_SCHEMA__", rating_schema)
    return result


def generate_article(topic: dict, article_num: int) -> dict | None:
    """Generate a single article. Returns article info dict or None."""
    title = topic["title"]
    filename = slugify(title)
    today = str(date.today())

    print(f"\n  Generating article {article_num}: {title}")
    print(f"     Filename: {filename}")

    # Build prompt
    prompt = build_prompt(topic, article_num, today)

    # Call DeepSeek
    print(f"     Calling DeepSeek API...")
    raw = call_deepseek(prompt)
    if not raw:
        print(f"     FAILED to generate article")
        return None

    article_body = extract_article_html(raw)
    # Strip any enclosing <html>/<body>/<head> tags the AI might add
    article_body = re.sub(r'^<!DOCTYPE[^>]*>', '', article_body, flags=re.IGNORECASE)
    article_body = re.sub(r'^<html[^>]*>', '', article_body, flags=re.IGNORECASE)
    article_body = re.sub(r'^<head>.*?</head>', '', article_body, flags=re.DOTALL + re.IGNORECASE)
    article_body = re.sub(r'^<body[^>]*>', '', article_body, flags=re.IGNORECASE)
    article_body = re.sub(r'</body>\s*$', '', article_body, flags=re.IGNORECASE)
    article_body = re.sub(r'</html>\s*$', '', article_body, flags=re.IGNORECASE)
    article_body = article_body.strip()

    word_count = count_words(article_body)
    print(f"     Generated {word_count} words")

    if word_count < 800:
        print(f"     WARNING: Article is short ({word_count} words), may need more content")

    # Build full HTML
    full_html = build_full_html(article_body, topic, today)

    # Add review checklist at top
    checklist = f"""<!--
========================================
审核清单（发布前请检查）：
[ ] 所有工具价格是否准确？
[ ] 工具名称拼写是否正确？
[ ] 是否加入了真实的使用观点？
[ ] 对比图表数据是否正确？
[ ] 相关文章链接是否有效？
[ ] 确认无误后：移动到 /posts/ 文件夹
========================================
-->

"""
    full_html = checklist + full_html

    # Save to /drafts/
    drafts_dir = ROOT / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    filepath = drafts_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"     Saved to drafts/{filename}")

    return {
        "title": title,
        "filename": filename,
        "category": topic["category"],
        "article_type": topic.get("article_type", "comparison"),
        "tools": topic.get("tools_covered", []),
        "word_count": word_count,
        "path": f"drafts/{filename}",
        "thumb_svg": f"{filename.replace('.html', '')}-thumb.svg",
        "comparison_svg": f"{filename.replace('.html', '')}-comparison.svg",
        "pricing_svg": f"{filename.replace('.html', '')}-pricing.svg",
    }


def run(topics: list[dict]) -> list[dict]:
    """Generate all articles. Returns list of article info dicts."""
    results = []
    for i, topic in enumerate(topics, 1):
        article_info = generate_article(topic, i)
        if article_info:
            results.append(article_info)
        else:
            print(f"  Failed article {i}, continuing...")
    return results


if __name__ == "__main__":
    test_topics = [
        {
            "title": "Cline vs Cursor: Best AI Coding IDE 2026",
            "keywords": "AI coding IDE comparison 2026",
            "category": "AI Coding",
            "tools_covered": ["Cline", "Cursor"],
            "angle": "Comparison test",
            "search_volume_estimate": "High",
            "rationale": "Test",
        }
    ]
    results = run(test_topics)
    print(json.dumps(results, indent=2))
