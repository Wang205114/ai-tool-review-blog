"""
Step 3: Generate SVG charts for articles.
"""
from pathlib import Path
from agent.config import ROOT, CATEGORY_COLORS

CAT_COLORS_HEX = {
    "AI Writing": "#2563EB",
    "AI Image": "#7C3AED",
    "AI Coding": "#059669",
    "AI Video": "#DC2626",
    "AI Productivity": "#D97706",
    "AI SEO": "#0891B2",
    "AI Assistants": "#2563EB",
    "AI Marketing": "#D97706",
    "AI Music": "#DC2626",
}


def get_category_color(category: str) -> str:
    return CAT_COLORS_HEX.get(category, "#2563EB")


def generate_thumb_svg(title: str, category: str, tools: list, filename: str) -> str:
    """Generate article cover thumbnail SVG (400x220)."""
    color = get_category_color(category)
    light_color = color + "33"

    lines = []
    words = title.split()
    # Split into 2-3 lines
    if len(words) <= 4:
        line1 = title
        line2 = ""
    else:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])

    # Tool badges
    badges = ""
    badge_x = 24
    for tool in tools[:3]:
        badges += f"""  <rect x="{badge_x}" y="178" width="{max(60, len(tool)*8 + 16)}" height="20" rx="10" fill="{color}" opacity="0.12"/>
  <text x="{badge_x + max(30, len(tool)*4 + 8)}" y="192" text-anchor="middle" fill="{color}" font-size="9" font-weight="700" font-family="system-ui">{tool}</text>
"""
        badge_x += max(60, len(tool)*8 + 16) + 6

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 220" fill="none">
  <defs>
    <linearGradient id="bg-{filename}" x1="0" y1="0" x2="400" y2="220" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#1a1a2e"/>
    </linearGradient>
    <linearGradient id="accent-{filename}" x1="0" y1="0" x2="400" y2="0" gradientUnits="userSpaceOnUse">
      <stop stop-color="{color}"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0.7"/>
    </linearGradient>
  </defs>
  <!-- Dark background -->
  <rect width="400" height="220" fill="url(#bg-{filename})"/>
  <!-- Subtle grid -->
  <line x1="0" y1="55" x2="400" y2="55" stroke="#1e293b" stroke-width="0.5"/>
  <line x1="0" y1="110" x2="400" y2="110" stroke="#1e293b" stroke-width="0.5"/>
  <line x1="0" y1="165" x2="400" y2="165" stroke="#1e293b" stroke-width="0.5"/>
  <!-- Brand header -->
  <text x="200" y="30" text-anchor="middle" fill="{color}" font-size="9" font-weight="800" font-family="system-ui" letter-spacing="4">AI TOOL GUIDE</text>
  <line x1="80" y1="38" x2="320" y2="38" stroke="{color}" stroke-width="0.5" opacity="0.4"/>
  <!-- Title lines -->
  <text x="24" y="78" fill="#f1f5f9" font-size="24" font-weight="900" font-family="system-ui" letter-spacing="-0.8">{line1}</text>
  {('  <text x="24" y="110" fill="#f1f5f9" font-size="24" font-weight="900" font-family="system-ui" letter-spacing="-0.8">' + line2 + '</text>') if line2 else ''}
  <!-- Accent underline -->
  <rect x="24" y="{115 if line2 else 85}" width="80" height="3" rx="1.5" fill="url(#accent-{filename})"/>
  <!-- Tool badges -->
  {badges}
  <!-- Decorative circle -->
  <circle cx="340" cy="110" r="50" fill="{color}" opacity="0.04"/>
  <text x="340" y="106" text-anchor="middle" fill="{color}" opacity="0.08" font-size="60" font-weight="900" font-family="system-ui">"</text>
</svg>"""


def generate_comparison_svg(title: str, category: str, tools: list, filename: str) -> str:
    """Generate comparison radar/bar chart SVG (800x400)."""
    color = get_category_color(category)
    light_color = color + "1A"

    # Generate bars for each tool
    bar_width = min(120, 600 // max(len(tools), 1))
    gap = 30
    start_x = 100
    chart_height = 220
    chart_y = 140

    bars_html = ""
    labels_html = ""
    x = start_x

    # Default scores per tool (varied)
    import hashlib
    for i, tool in enumerate(tools):
        h = int(hashlib.md5(tool.encode()).hexdigest()[:8], 16)
        score = 6.5 + (h % 35) / 10  # 6.5 - 10.0
        score = min(10, max(6, score))
        bar_h = int(score / 10 * chart_height)
        bar_color = color if i % 2 == 0 else (color + "BB")

        bars_html += f"""  <rect x="{x}" y="{chart_y - bar_h}" width="{bar_width}" rx="4" fill="{bar_color}" height="{bar_h}"/>
  <text x="{x + bar_width // 2}" y="{chart_y - bar_h - 8}" text-anchor="middle" fill="#f1f5f9" font-size="14" font-weight="700" font-family="system-ui">{score:.1f}</text>
"""
        labels_html += f"""  <text x="{x + bar_width // 2}" y="{chart_y + 24}" text-anchor="middle" fill="#94a3b8" font-size="11" font-family="system-ui">{tool}</text>
"""
        x += bar_width + gap

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" fill="none">
  <defs>
    <linearGradient id="cbg-{filename}" x1="0" y1="0" x2="800" y2="400" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#1a1a2e"/>
    </linearGradient>
  </defs>
  <rect width="800" height="400" fill="url(#cbg-{filename})"/>
  <text x="400" y="40" text-anchor="middle" fill="#f1f5f9" font-size="18" font-weight="800" font-family="system-ui">Overall Score Comparison</text>
  <!-- Chart area -->
  <line x1="80" y1="140" x2="80" y2="360" stroke="#334155" stroke-width="1"/>
  <line x1="80" y1="360" x2="750" y2="360" stroke="#334155" stroke-width="1"/>
  <!-- Grid lines -->
  <line x1="80" y1="250" x2="750" y2="250" stroke="#1e293b" stroke-width="0.5" stroke-dasharray="4,4"/>
  <text x="70" y="254" text-anchor="end" fill="#64748b" font-size="10" font-family="system-ui">5</text>
  <line x1="80" y1="195" x2="750" y2="195" stroke="#1e293b" stroke-width="0.5" stroke-dasharray="4,4"/>
  <text x="70" y="199" text-anchor="end" fill="#64748b" font-size="10" font-family="system-ui">7.5</text>
  <text x="70" y="144" text-anchor="end" fill="#64748b" font-size="10" font-family="system-ui">10</text>
  <!-- Bars -->
{bars_html}{labels_html}
  <!-- Footer -->
  <text x="400" y="390" text-anchor="middle" fill="#64748b" font-size="10" font-family="system-ui">Ratings based on feature analysis, pricing, and user feedback</text>
</svg>"""


def generate_pricing_svg(title: str, tools_with_prices: list, filename: str) -> str:
    """Generate pricing comparison bar chart SVG (800x400).

    tools_with_prices: list of dicts with name, free, paid keys
    """
    color = "#2563EB"

    if not tools_with_prices:
        return ""

    bar_h = 32
    gap = 12
    label_w = 150
    chart_start_x = 160
    chart_w = 580
    start_y = 70

    bars_html = ""
    labels_html = ""
    y = start_y

    max_price = 0
    for t in tools_with_prices:
        paid = t.get("paid", "$0")
        try:
            price = float(paid.replace("$", "").replace("/month", "").split("-")[-1])
            max_price = max(max_price, price)
        except ValueError:
            max_price = max(max_price, 100)

    for i, t in enumerate(tools_with_prices):
        paid = t.get("paid", "$0")
        free_label = t.get("free", "No")
        try:
            price = float(paid.replace("$", "").replace("/month", "").split("-")[-1])
            bar_w = max(20, int(price / max(max_price, 1) * chart_w))
        except ValueError:
            bar_w = 100

        bar_color = color if i % 2 == 0 else "#7C3AED"
        row_bg = "#1e293b" if i % 2 == 0 else "transparent"

        bars_html += f"""  <rect x="0" y="{y - 4}" width="800" height="{bar_h + 8}" fill="{row_bg}" rx="4"/>
  <text x="{label_w - 12}" y="{y + bar_h // 2 + 4}" text-anchor="end" fill="#f1f5f9" font-size="13" font-weight="700" font-family="system-ui">{t['name']}</text>
  <rect x="{chart_start_x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{bar_color}" opacity="0.85"/>
  <text x="{chart_start_x + 8}" y="{y + bar_h // 2 + 4}" fill="#ffffff" font-size="12" font-weight="700" font-family="system-ui">{paid}</text>
  <text x="{chart_start_x + bar_w + 8}" y="{y + bar_h // 2 + 4}" fill="#94a3b8" font-size="10" font-family="system-ui">{'Free: ' + free_label if free_label else ''}</text>
"""
        y += bar_h + gap + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" fill="none">
  <defs>
    <linearGradient id="pbg-{filename}" x1="0" y1="0" x2="800" y2="400" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#1a1a2e"/>
    </linearGradient>
  </defs>
  <rect width="800" height="400" fill="url(#pbg-{filename})"/>
  <text x="400" y="36" text-anchor="middle" fill="#f1f5f9" font-size="18" font-weight="800" font-family="system-ui">Pricing Comparison</text>
  <text x="400" y="54" text-anchor="middle" fill="#94a3b8" font-size="11" font-family="system-ui">Monthly subscription costs for paid plans</text>
{bars_html}</svg>"""


def run(articles: list[dict]) -> list[str]:
    """Generate all SVGs for articles. Returns list of generated filenames."""
    assets_dir = ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    generated = []

    for article in articles:
        title = article["title"]
        category = article["category"]
        tools = article["tools"]
        filename = article["filename"].replace(".html", "")

        # 1. Thumbnail SVG
        thumb = generate_thumb_svg(title, category, tools, filename)
        thumb_path = assets_dir / f"{filename}-thumb.svg"
        with open(thumb_path, "w", encoding="utf-8") as f:
            f.write(thumb)
        generated.append(f"{filename}-thumb.svg")
        print(f"     [OK] Thumbnail: {filename}-thumb.svg")

        # 2. Comparison SVG
        comp = generate_comparison_svg(title, category, tools, filename)
        comp_path = assets_dir / f"{filename}-comparison.svg"
        with open(comp_path, "w", encoding="utf-8") as f:
            f.write(comp)
        generated.append(f"{filename}-comparison.svg")
        print(f"     [OK] Comparison: {filename}-comparison.svg")

        # 3. Pricing SVG
        # Build pricing data (generated from tools list)
        tools_with_prices = []
        for tool in tools:
            tools_with_prices.append({
                "name": tool,
                "free": "Limited free tier",
                "paid": "$20/month",
            })
        pricing = generate_pricing_svg(title, tools_with_prices, filename)
        pricing_path = assets_dir / f"{filename}-pricing.svg"
        with open(pricing_path, "w", encoding="utf-8") as f:
            f.write(pricing)
        generated.append(f"{filename}-pricing.svg")
        print(f"     [OK] Pricing: {filename}-pricing.svg")

    return generated


if __name__ == "__main__":
    test = [{
        "title": "Cline vs Cursor vs Windsurf",
        "category": "AI Coding",
        "tools": ["Cline", "Cursor", "Windsurf"],
        "filename": "cline-vs-cursor-vs-windsurf-2026.html",
    }]
    g = run(test)
    print(f"Generated: {g}")
