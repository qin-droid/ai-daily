#!/usr/bin/env python
"""
Auto-publish script for AI Daily Blog.
Reads articles from the daily AI news and GitHub trending outputs,
converts them to blog posts, and pushes to GitHub Pages.

Called by cron at 8:00 daily (after both AI news and GitHub trending are generated).

Usage:
  python auto_publish.py
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── config ──────────────────────────────────────────────────────────

BLOG_DIR = Path(r"D:\AI-Workspace\ai-daily-blog")
AI_NEWS_DIR = Path(r"D:\AI-Workspace\每日AI资讯")
GITHUB_TREND_DIR = Path(r"D:\AI-Workspace\GitHub趋势日报")
ARTICLES_DIR = BLOG_DIR / "articles"

GITHUB_USER = "AI-Daily-Bot"  # placeholder — update with real username
GITHUB_REPO = "ai-daily"

# ── helpers ──────────────────────────────────────────────────────────


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def read_file_safe(path: Path) -> str:
    """Read file content, return empty string if not found."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"  ⚠️  Error reading {path.name}: {e}")
        return ""


# ── article generation ────────────────────────────────────────────────


def find_latest_file(directory: Path) -> Path | None:
    """Find the most recently modified file in a directory."""
    if not directory.exists():
        return None
    files = [f for f in directory.iterdir() if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def generate_ai_news_post() -> dict | None:
    """Convert the latest AI news markdown to a blog post."""
    latest = find_latest_file(AI_NEWS_DIR)
    if not latest:
        print("  ⚠️  No AI news file found")
        return None

    content = read_file_safe(latest)
    if not content:
        return None

    # Extract title from first heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else f"AI 日报 · {today_str()}"

    # Extract first paragraph as description
    desc_match = re.search(r"\n\n(.+?)\n\n", content)
    desc = desc_match.group(1).strip()[:200] if desc_match else "今日 AI 资讯汇总"

    article_id = f"{today_str()}-ai-news"
    filename = f"{article_id}.html"

    # Generate HTML article
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI 日报</title>
<link rel="stylesheet" href="../style.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
body {{ font-family: 'Inter', 'Noto Sans SC', sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; padding: 0; margin: 0; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 40px 24px; }}
.back {{ display: inline-block; color: var(--accent); text-decoration: none; margin-bottom: 24px; font-size: 14px; }}
.back:hover {{ text-decoration: underline; }}
h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
.date {{ color: var(--text2); font-size: 14px; margin-bottom: 32px; }}
.content {{ font-size: 15px; }}
.content h2 {{ font-size: 20px; margin-top: 32px; margin-bottom: 12px; }}
.content h3 {{ font-size: 17px; margin-top: 24px; margin-bottom: 8px; }}
.content p {{ margin-bottom: 16px; }}
.content ul {{ margin-bottom: 16px; padding-left: 24px; }}
.content li {{ margin-bottom: 6px; }}
.content a {{ color: var(--accent); }}
.content hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}
</style>
</head>
<body>
<div class="container">
  <a class="back" href="../">← 返回首页</a>
  <h1>{title}</h1>
  <div class="date">{today_str()}</div>
  <div class="content">
{content}
  </div>
  <a class="back" href="../">← 返回首页</a>
</div>
</body>
</html>"""

    (ARTICLES_DIR / filename).write_text(html, encoding="utf-8")

    return {
        "date": today_str(),
        "title": title,
        "desc": desc,
        "tag": "AI 资讯",
        "tagType": "hot",
        "source": "AI 日报",
        "sourceUrl": "#",
        "contentUrl": f"/articles/{filename}",
    }


def generate_github_trend_post() -> dict | None:
    """Convert the latest GitHub trending markdown to a blog post."""
    latest = find_latest_file(GITHUB_TREND_DIR)
    if not latest:
        print("  ⚠️  No GitHub trending file found")
        return None

    content = read_file_safe(latest)
    if not content:
        return None

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else f"GitHub 趋势 · {today_str()}"

    desc_match = re.search(r"\n\n(.+?)\n\n", content)
    desc = desc_match.group(1).strip()[:200] if desc_match else "今日 GitHub 热门项目"

    article_id = f"{today_str()}-github-trending"
    filename = f"{article_id}.html"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI 日报</title>
<link rel="stylesheet" href="../style.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
body {{ font-family: 'Inter', 'Noto Sans SC', sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; padding: 0; margin: 0; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 40px 24px; }}
.back {{ display: inline-block; color: var(--accent); text-decoration: none; margin-bottom: 24px; font-size: 14px; }}
h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
.date {{ color: var(--text2); font-size: 14px; margin-bottom: 32px; }}
.content {{ font-size: 15px; }}
.content h2 {{ font-size: 20px; margin-top: 32px; }}
.content ul {{ margin-bottom: 16px; padding-left: 24px; }}
.content li {{ margin-bottom: 8px; }}
.content a {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="container">
  <a class="back" href="../">← 返回首页</a>
  <h1>{title}</h1>
  <div class="date">{today_str()}</div>
  <div class="content">
{content}
  </div>
  <a class="back" href="../">← 返回首页</a>
</div>
</body>
</html>"""

    (ARTICLES_DIR / filename).write_text(html, encoding="utf-8")

    return {
        "date": today_str(),
        "title": title,
        "desc": desc,
        "tag": "GitHub 趋势",
        "tagType": "trend",
        "source": "GitHub Trending",
        "sourceUrl": "#",
        "contentUrl": f"/articles/{filename}",
    }


# ── main ──────────────────────────────────────────────────────────────


def main():
    print("=" * 50)
    print(f"🔄 Auto-publishing blog for {today_str()}")
    print("=" * 50)

    # Ensure articles directory exists
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # Generate new articles
    print("\n📰 Generating AI news post...")
    news_post = generate_ai_news_post()
    if news_post:
        print(f"   ✅ {news_post['title'][:60]}...")
    else:
        print("   ⏭️  Skipped")

    print("\n📊 Generating GitHub trending post...")
    trend_post = generate_github_trend_post()
    if trend_post:
        print(f"   ✅ {trend_post['title'][:60]}...")
    else:
        print("   ⏭️  Skipped")

    # Update articles.json
    print("\n📝 Updating articles.json...")
    articles_path = BLOG_DIR / "articles.json"
    existing = []
    if articles_path.exists():
        try:
            existing = json.loads(articles_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    # Add new articles to front
    new_articles = []
    if news_post:
        new_articles.append(news_post)
    if trend_post:
        new_articles.append(trend_post)

    # Avoid duplicates
    existing_titles = {a["title"] for a in existing}
    fresh = [a for a in new_articles if a["title"] not in existing_titles]
    all_articles = fresh + existing

    # Keep max 100 articles
    all_articles = all_articles[:100]

    articles_path.write_text(
        json.dumps(all_articles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"   ✅ {len(fresh)} new, {len(all_articles)} total articles")

    # Update RSS feed
    print("\n📡 Updating RSS feed...")
    items = []
    for a in all_articles[:20]:  # RSS: last 20 items
        pub_date = datetime.strptime(a["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0800")
        items.append(f"""  <item>
    <title>{a['title']}</title>
    <link>https://{GITHUB_USER}.github.io/{GITHUB_REPO}{a.get('contentUrl', '')}</link>
    <guid>https://{GITHUB_USER}.github.io/{GITHUB_REPO}{a.get('contentUrl', '')}</guid>
    <pubDate>{pub_date}</pubDate>
    <description>{a['desc'][:200]}</description>
  </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>AI 日报</title>
  <link>https://{GITHUB_USER}.github.io/{GITHUB_REPO}/</link>
  <description>每日 AI 资讯与 GitHub 趋势汇总，自动更新</description>
  <language>zh-CN</language>
  <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0800')}</lastBuildDate>
  <atom:link href="https://{GITHUB_USER}.github.io/{GITHUB_REPO}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
</channel>
</rss>"""

    (BLOG_DIR / "feed.xml").write_text(rss, encoding="utf-8")
    print(f"   ✅ RSS feed updated with {len(items)} items")

    # Update blog style reference
    print("\n📦 Blog ready for deployment!")
    print(f"   📁 {BLOG_DIR}")
    print(f"   📝 {len(all_articles)} articles in index")
    print(f"   📡 RSS feed active")
    print("\n" + "=" * 50)
    print("✅ Blog auto-publish complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
