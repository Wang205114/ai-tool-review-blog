"""
Step 6: Generate weekly report in /drafts/weekly-report.md.
"""
from datetime import date
from agent.config import ROOT


def run(topics: list[dict], articles: list[dict], svgs: list[str]) -> str:
    """Generate weekly report markdown."""
    today = str(date.today())

    report = f"""# 本周内容报告 {today}

## 热点来源
- 本周搜索趋势：通过 DuckDuckGo 搜索 AI 工具热点关键词获取
- 选题理由：优先级为新工具、高搜索量对比、长尾关键词
- 参考来源：DuckDuckGo 搜索结果

## 本周生成文章

"""
    for i, article in enumerate(articles):
        rel_svgs = [s for s in svgs if article["filename"].replace(".html", "") in s]
        kw = topics[i]["keywords"] if i < len(topics) else "N/A"
        sv = topics[i]["search_volume_estimate"] if i < len(topics) else "N/A"
        report += f"""**{i + 1}. {article['title']}**
   - 目标关键词：{kw}
   - 预计月搜索量：{sv}
   - 文件路径：{article['path']}
   - 生成的图表：{', '.join(rel_svgs) if rel_svgs else 'None'}
   - 字数：{article.get('word_count', 0)} 字
   - 工具覆盖：{', '.join(article['tools'])}

"""

    report += """## 建议优化点
- [ ] 核实每个工具的最新价格（AI 生成的价格可能已过时）
- [ ] 补充真实的使用体验和截图
- [ ] 检查内部链接是否正确
- [ ] 确认所有 SVG 图表数据与文章内容一致

## 下周预计选题方向
- 关注 ProductHunt 最新 AI 产品发布
- 搜索量增长的 AI 工具品类
- 读者反馈和搜索数据驱动的选题
"""

    report_path = ROOT / "drafts" / "weekly-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  [OK] Weekly report saved to drafts/weekly-report.md")
    return report


if __name__ == "__main__":
    run([], [], [])
