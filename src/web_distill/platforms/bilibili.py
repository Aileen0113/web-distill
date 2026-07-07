"""B站提取器 — 通过 B站 API 获取视频信息"""

import json
import re

import requests

from web_distill.platforms.base import BaseExtractor
from web_distill.core.types import ExtractedContent


BILIBILI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com/",
}


class BilibiliExtractor(BaseExtractor):
    """B站内容提取"""

    platform_name = "bilibili"

    def extract(self, url: str) -> ExtractedContent:
        bvid = self._extract_bvid(url)
        if not bvid:
            return self._make_content(
                url=url,
                title="B站链接格式错误",
                description="无法从 URL 中提取 BV 号",
            )

        info = self._get_video_info(bvid)
        if not info:
            return self._make_content(
                url=url,
                title="获取视频信息失败",
                description="可能被风控拦截，试试在浏览器中打开",
            )

        desc = info.get("desc", "")
        body_parts = []
        if desc:
            body_parts.append(f"## 视频描述\n\n{desc}")

        return self._make_content(
            url=url,
            title=info.get("title", ""),
            body="\n\n".join(body_parts),
            description=desc[:500] if desc else f"B站视频 | {info.get('owner', {}).get('name', '')}",
            author=info.get("owner", {}).get("name", ""),
            date=self._ts_to_date(info.get("pubdate", 0)),
            duration=self._format_duration(info.get("duration", 0)),
            content_type="video",
            metadata={
                "bvid": bvid,
                "view": info.get("stat", {}).get("view", 0),
                "danmaku": info.get("stat", {}).get("danmaku", 0),
                "cover": info.get("pic", ""),
            },
        )

    def _get_video_info(self, bvid: str) -> dict | None:
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        try:
            resp = requests.get(api_url, headers=BILIBILI_HEADERS, timeout=15)
            data = resp.json()
            if data.get("code") == 0:
                return data["data"]
            return None
        except Exception:
            return None

    @staticmethod
    def _extract_bvid(url: str) -> str | None:
        m = re.search(r"/video/(BV[\w]+)", url)
        if m:
            return m.group(1)
        m = re.search(r"b23\.tv/(\w+)", url)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _ts_to_date(ts: int) -> str:
        if not ts:
            return ""
        from datetime import datetime
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if not seconds:
            return ""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
