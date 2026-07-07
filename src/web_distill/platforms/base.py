"""提取器基类"""

from abc import ABC, abstractmethod

from web_distill.core.types import ExtractedContent


class BaseExtractor(ABC):
    """所有平台提取器的基类"""

    platform_name: str = "unknown"

    @abstractmethod
    def extract(self, url: str) -> ExtractedContent:
        """提取 URL 的内容"""
        ...

    def _make_content(self, url: str, title: str = "", body: str = "",
                      description: str = "", content_type: str = "article",
                      **kwargs) -> ExtractedContent:
        return ExtractedContent(
            url=url,
            title=title or "未命名",
            platform=self.platform_name,
            content_type=content_type,
            body=body,
            description=description,
            **kwargs,
        )

    def _fetch_html(self, url: str, timeout: int = 15) -> str:
        """获取页面 HTML"""
        import requests
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.text
