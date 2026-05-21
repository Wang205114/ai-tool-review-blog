#!/usr/bin/env python3
"""
AI Tool Guide — Automated Article Generation Agent

Usage:
    python run-agent.py

Environment:
    DEEPSEEK_API_KEY must be set in .env file
"""
import sys, os

# Force UTF-8 for console output
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent import research, article_generator, svg_generator, site_updater, report_generator


def print_header(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def eprint(text: str):
    """Print with proper encoding fallback."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(sys.stdout.encoding, errors="replace").decode(sys.stdout.encoding))


def main():
    try:
        print(f"\n{'#'*60}")
        eprint(f"#  AI Tool Guide - Content Agent")
        eprint(f"#  {date.today()}")
        print(f"{'#'*60}")

        # ========================================
        # Step 1: Research
        # ========================================
        print_header("[1/7] Researching trending AI topics...")
        try:
            topics = research.run()
            if not topics:
                print("  No topics found, using fallback topics")
                topics = research.fallback_topics()
        except Exception as e:
            print(f"  Research failed: {e}")
            topics = research.fallback_topics()

        print(f"\n  Selected topics:")
        for i, t in enumerate(topics, 1):
            eprint(f"     {i}. {t['title']}")
            print(f"        Category: {t['category']} | Keywords: {t['keywords']}")
            print(f"        Search Volume: {t.get('search_volume_estimate', 'N/A')}")

        # ========================================
        # Step 2: Generate articles
        # ========================================
        print_header("[2/7] Generating article drafts...")
        articles = article_generator.run(topics)

        if not articles:
            print("  No articles were generated. Aborting.")
            sys.exit(1)

        # ========================================
        # Step 3: Generate SVG charts
        # ========================================
        print_header("[3/7] Generating SVG charts...")
        svgs = svg_generator.run(articles)

        # ========================================
        # Step 4: Update site files
        # ========================================
        print_header("[4/7] Updating sitemap.xml and index.html...")
        site_updater.run(articles)

        # ========================================
        # Step 5: Save drafts
        # ========================================
        print_header("[5/7] Drafts saved to /drafts/ folder...")
        for article in articles:
            print(f"     File: {article['path']}")

        # ========================================
        # Step 6: Generate report
        # ========================================
        print_header("[6/7] Generating weekly report...")
        report_generator.run(topics, articles, svgs)

        # ========================================
        # Step 7: Summary
        # ========================================
        print_header("[7/7] Summary")

        total_words = sum(a.get("word_count", 0) for a in articles)
        print(f"""
  [OK] {len(articles)} article drafts generated
  [OK] {len(svgs)} SVG charts created
  [OK] sitemap.xml updated
  [OK] index.html updated
  [OK] Weekly report saved

  [Drafts]  /drafts/
  [Report]  /drafts/weekly-report.md
  [Assets]  /assets/

  Articles generated:
""")
        for a in articles:
            eprint(f"     - {a['title']}")
            a_type = a.get('article_type', 'comparison')
            print(f"       File: {a['path']} ({a.get('word_count', 0)} words) [{a_type}]")
            print(f"       Charts: {a['thumb_svg']}{', ' + a.get('comparison_svg', '') + ', ' + a.get('pricing_svg', '') if a_type == 'comparison' else ', (no comparison charts)'}")

        print(f"""
  {'='*60}
  NEXT STEPS:
  1. Review drafts in /drafts/ folder
  2. Check pricing accuracy in each article
  3. Verify SVG charts render correctly
  4. If approved, move files from /drafts/ to /posts/
  5. Run:
     git add .
     git commit -m "Weekly update {date.today()}: add {len(articles)} new articles"
     git push origin main
  {'='*60}
""")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
