"""
Step 4: Update sitemap.xml and index.html with new articles.
"""
import re
from datetime import date
from pathlib import Path
from agent.config import ROOT, SITE


def update_sitemap(articles: list[dict]) -> None:
    """Add new article URLs to sitemap.xml."""
    sitemap_path = ROOT / "sitemap.xml"
    today = str(date.today())

    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_entries = ""
    for article in articles:
        filename = article["filename"]
        new_entries += f"""  <url>
    <loc>{SITE['canonical_base']}/posts/{filename}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
"""

    if "</urlset>" in content:
        content = content.replace("</urlset>", new_entries + "</urlset>")
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"     sitemap.xml updated with {len(articles)} new entries")
    else:
        print(f"     Could not find </urlset> in sitemap.xml")


def update_index(articles: list[dict]) -> None:
    """Insert new article cards at the top of Featured Articles on index.html."""
    index_path = ROOT / "index.html"

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    cards_html = ""
    for i, article in enumerate(articles):
        title = article["title"]
        filename = article["filename"]
        category = article["category"]
        thumb = article.get("thumb_svg", f"{filename.replace('.html', '')}-thumb.svg")
        read_time = max(8, article.get("word_count", 2000) // 200)
        today = str(date.today())
        desc = f"A detailed review and comparison of {', '.join(article['tools'][:3])}."
        featured_class = " featured" if i < 2 else ""

        cards_html += f"""          <article class="article-card{featured_class}">
            <img src="assets/{thumb}?v=1" width="400" height="220" alt="" aria-hidden="true" loading="lazy">
            <div class="card-copy">
              <span class="kicker">{category}</span>
              <h3><a href="posts/{filename}">{title}</a></h3>
              <p>{desc}</p>
              <div class="meta">
                <span>Updated {today}</span>
                <span>{read_time} min read</span>
              </div>
            </div>
          </article>
"""

    # Insert after <div class="card-grid">
    pattern = r'(<div class="card-grid">\s*\n)'
    match = re.search(pattern, content)
    if not match:
        # Fallback: try finding card-grid differently
        pattern = r'(<div class="card-grid">)'
        match = re.search(pattern, content)

    if match:
        insertion_point = match.end()
        content = content[:insertion_point] + "\n" + cards_html + content[insertion_point:]
        print(f"     index.html updated with {len(articles)} new article cards")

        # Trim to max 12 articles if needed
        card_count = content.count('<article class="article-card')
        article_blocks = list(re.finditer(
            r'<article class="article-card[^>]*>.*?</article>',
            content, re.DOTALL
        ))
        if len(article_blocks) > 12:
            # Keep only the first 12 article blocks
            last_keep = article_blocks[11]
            first_remove = article_blocks[12]
            cut_pos = first_remove.start()
            # Find the next section heading after the last kept article
            # Remove everything from first excess article to end of card-grid section
            section_end = content.find('</section>', cut_pos)
            if section_end > cut_pos:
                content = content[:cut_pos] + content[section_end:]
            else:
                content = content[:cut_pos]
            print(f"     Trimmed to 12 articles (removed {len(article_blocks) - 12} old ones)")
    else:
        print("     Could not find card-grid in index.html")
        return

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)


def run(articles: list[dict]) -> None:
    """Update sitemap.xml and index.html."""
    print("  Updating sitemap.xml...")
    update_sitemap(articles)

    print("  Updating index.html...")
    update_index(articles)


if __name__ == "__main__":
    test = [{
        "title": "Cline vs Cursor vs Windsurf",
        "category": "AI Coding",
        "filename": "cline-vs-cursor-vs-windsurf-2026.html",
        "thumb_svg": "cline-vs-cursor-vs-windsurf-2026-thumb.svg",
        "tools": ["Cline", "Cursor", "Windsurf"],
        "word_count": 2000,
    }]
    run(test)
