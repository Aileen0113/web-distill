"""通用网页提取器 — 适用于任意网页"""

import re

from bs4 import BeautifulSoup
from readability import Document

from web_distill.platforms.base import BaseExtractor
from web_distill.core.types import ExtractedContent


class GenericExtractor(BaseExtractor):
    """通用网页提取：Mozilla Readability + BeautifulSoup 兜底"""

    platform_name = "generic"

    def extract(self, url: str) -> ExtractedContent:
        try:
            html = self._fetch_html(url)
            return self._parse(html, url)
        except Exception as e:
            return self._make_content(
                url=url,
                title="提取失败",
                description=f"错误: {e}",
                body="",
            )

    def _parse(self, html: str, url: str) -> ExtractedContent:
        try:
            doc = Document(html)
            title = doc.title() or ""
            summary_html = doc.summary()
            summary_text = self._html_to_text(summary_html)
        except Exception:
            title = ""
            summary_text = ""

        soup = BeautifulSoup(html, "lxml")
        if not title:
            title = (soup.title.string if soup.title else "") or ""

        description = ""
        author = ""
        date = ""

        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            prop = meta.get("property", "").lower()
            content = meta.get("content", "")
            if name in ("description",) or prop in ("og:description",):
                description = content
            if name in ("author",) or prop in ("og:author", "article:author"):
                author = content
            if name in ("date", "pubdate") or prop in ("article:published_time",):
                date = content[:10]

        body = summary_text.strip()
        if not body or len(body) < 50:
            body = soup.get_text(separator="\n", strip=True)
            body = re.sub(r"\n{3,}", "\n\n", body)

        return self._make_content(
            url=url,
            title=title.strip(),
            body=body[:10000],
            description=description or self._first_paragraph(body),
            author=author,
            date=date,
            content_type="article",
        )

    @staticmethod
    def _html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        for pre in soup.find_all("pre"):
            pre.string = f"\n```\n{pre.get_text()}\n```\n"
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return re.sub(r"\n{3,}", "\n\n", text)

    @staticmethod
    def _first_paragraph(text: str, max_len: int = 200) -> str:
        if not text:
            return ""
        para = text.split("\n\n")[0] if "\n\n" in text else text[:max_len]
        return para[:max_len].strip()
