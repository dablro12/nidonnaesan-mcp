#!/usr/bin/env python3
"""blogreviewzip.com/tips 팁 본문 동기화 → data/tips/*.md + index.json."""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
TIPS_DIR = ROOT / "data" / "tips"
INDEX_URL = "https://blogreviewzip.com/tips"
BASE_URL = "https://blogreviewzip.com"

LEGACY_ID_MAP = {
    "selection_rate": "selection-rate-tips",
    "blog_index": "blog-index-explained",
    "platform": "platform-comparison",
    "ad_disclosure": "advertising-disclosure",
    "posting_omission": "posting-missing",
    "naver_seo": "naver-seo-guide",
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "선정률": ["선정", "신청", "탈락", "초보", "당첨", "포트폴리오", "실수"],
    "리뷰작성": ["리뷰", "포스팅", "사진", "제목", "AI", "광고 글", "작성", "SEO", "네이버"],
    "플랫폼": ["플랫폼", "레뷰", "티블", "사이트", "등급", "네이버 플레이스"],
    "도구관리": ["관리", "마감", "반려", "애드포스트", "쿠팡", "수익", "알바", "댓글"],
    "규정": ["광고 표기", "공정위", "페이백", "표기", "누락"],
}

NAVER_SEO_SLUG = "naver-seo-guide"
NAVER_SEO_URL = "https://blogreviewzip.com/naver-seo"


def discover_slugs(client: httpx.Client) -> list[str]:
    page = client.get(INDEX_URL).text
    return sorted(set(re.findall(r'href="/tips/([a-z0-9-]+)"', page)))


def _html_to_text(fragment: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", fragment)
    text = re.sub(r"<li[^>]*>", "\n- ", text)
    text = re.sub(r"<h2[^>]*>", "\n\n## ", text)
    text = re.sub(r"<h3[^>]*>", "\n\n### ", text)
    text = re.sub(r"<p[^>]*>", "\n\n", text)
    text = re.sub(r"<strong[^>]*>", "**", text)
    text = re.sub(r"</strong>", "**", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_article_html(page_html: str) -> str:
    """RSC 스트림에 포함된 본문 HTML 조각 추출."""
    start = page_html.find("<h1")
    if start < 0:
        start = page_html.find("<h2 class=\"text-2xl")
    if start < 0:
        return ""
    end_markers = [
        page_html.find("<h2 class=\"text-lg font-semibold text-foreground mb-4\">다른 팁 보기", start),
        page_html.find("다른 팁 보기", start),
    ]
    end = min(x for x in end_markers if x > start) if any(x > start for x in end_markers) else len(page_html)
    chunk = page_html[start:end]
    chunk = re.sub(r"<h1[^>]*>.*?</h1>", "", chunk, count=1, flags=re.DOTALL)
    return chunk


def fetch_article(client: httpx.Client, slug: str) -> dict[str, str]:
    url = f"{BASE_URL}/tips/{slug}"
    page = client.get(url).text
    title_m = re.search(
        r'<h1[^>]*class="[^"]*text-3xl[^"]*"[^>]*>([^<]+)',
        page,
    )
    if not title_m:
        title_m = re.search(r"<title>([^<|]+)", page)
    title = html.unescape(title_m.group(1).strip()) if title_m else slug

    body_html = extract_article_html(page)
    body = _html_to_text(body_html)
    if len(body) < 200:
        desc_m = re.search(r'<meta name="description" content="([^"]+)"', page)
        body = html.unescape(desc_m.group(1)) if desc_m else body

    md = f"# {title}\n\n{body}\n"
    return {"slug": slug, "title": title, "markdown": md, "source_url": url}


def guess_category(title: str, slug: str) -> str:
    hay = f"{title} {slug}"
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in hay for k in kws):
            return cat
    return "도구관리"


def build_keywords(title: str, slug: str) -> list[str]:
    tokens = re.findall(r"[가-힣a-zA-Z0-9]+", title)
    kws = [t for t in tokens if len(t) >= 2][:12]
    kws.append(slug.replace("-", " "))
    return list(dict.fromkeys(kws))


def legacy_id_for_slug(slug: str) -> str | None:
    for legacy, mapped in LEGACY_ID_MAP.items():
        if mapped == slug:
            return legacy
    return None


def build_index(articles: list[dict[str, str]]) -> dict:
    legacy_order = list(LEGACY_ID_MAP.keys())
    topics = []
    for art in articles:
        slug = art["slug"]
        legacy = legacy_id_for_slug(slug)
        topic_id = legacy or slug.replace("-", "_")
        priority = legacy_order.index(legacy) + 1 if legacy in legacy_order else 50
        topics.append(
            {
                "id": topic_id,
                "slug": slug,
                "file": f"{slug}.md",
                "title": art["title"],
                "keywords": build_keywords(art["title"], slug),
                "category": guess_category(art["title"], slug),
                "priority": priority,
                "source_url": art["source_url"],
                "recommended_for": ["beginner"] if "초보" in art["title"] or legacy else ["intermediate"],
            }
        )
    topics.sort(key=lambda t: t["priority"])
    return {
        "version": "2.0.0",
        "source": "https://blogreviewzip.com/tips",
        "topics": topics,
        "auto_recommendation_order": {
            "none": ["selection_rate", "platform", "blog_index", "ad_disclosure", "posting_omission"],
            "beginner": ["selection_rate", "platform", "blog_index", "first_campaign_checklist", "campaign_sites_and_tips"],
            "intermediate": ["blog_index", "ad_disclosure", "posting_omission", "review_writing_guide", "photo_tips_by_category", "naver_seo"],
        },
    }


def fetch_naver_seo_page(client: httpx.Client) -> dict[str, str]:
    """blogreviewzip.com/naver-seo 단일 페이지 동기화."""
    page = client.get(NAVER_SEO_URL).text
    title_m = re.search(r"<title>([^<|]+)", page)
    title = html.unescape(title_m.group(1).strip()) if title_m else "네이버 블로그 SEO 가이드"
    body_html = extract_article_html(page)
    body = _html_to_text(body_html)
    if len(body) < 200:
        desc_m = re.search(r'<meta name="description" content="([^"]+)"', page)
        body = html.unescape(desc_m.group(1)) if desc_m else body
    md = f"# {title}\n\n{body}\n"
    return {"slug": NAVER_SEO_SLUG, "title": title, "markdown": md, "source_url": NAVER_SEO_URL}


def main() -> int:
    TIPS_DIR.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        slugs = discover_slugs(client)
        articles: list[dict[str, str]] = []
        for slug in slugs:
            try:
                art = fetch_article(client, slug)
                if len(art["markdown"]) < 150:
                    print(f"WARN short content: {slug}", file=sys.stderr)
                articles.append(art)
                (TIPS_DIR / f"{slug}.md").write_text(art["markdown"], encoding="utf-8")
                print(f"saved {slug} ({len(art['markdown'])} chars)")
            except Exception as exc:
                print(f"WARN {slug}: {exc}", file=sys.stderr)

        try:
            seo = fetch_naver_seo_page(client)
            if seo["slug"] not in {a["slug"] for a in articles}:
                articles.append(seo)
                (TIPS_DIR / f"{seo['slug']}.md").write_text(seo["markdown"], encoding="utf-8")
                print(f"saved {seo['slug']} ({len(seo['markdown'])} chars) [naver-seo]")
        except Exception as exc:
            print(f"WARN naver-seo: {exc}", file=sys.stderr)

    index = build_index(articles)
    (TIPS_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"index: {len(index['topics'])} topics")
    return 0 if len(articles) >= 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
