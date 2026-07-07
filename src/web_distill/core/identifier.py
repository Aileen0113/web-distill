"""URL 平台识别器 — 根据 URL 判断来源平台"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Platform:
    """平台信息"""
    name: str           # 平台名称
    key: str            # 平台标识
    extractor: str      # 对应提取器模块名
    needs_browser: bool  # 是否需要浏览器环境


# 平台匹配规则 (regex, platform_key, needs_browser)
PLATFORM_RULES: list[tuple[str, str, bool]] = [
    # 视频平台
    (r"bilibili\.com/(video|bangumi)", "bilibili", True),
    (r"space\.bilibili\.com", "bilibili", True),
    (r"youtube\.com/(watch|playlist|@|channel)", "youtube", False),
    (r"youtu\.be/", "youtube", False),
    # 文档站
    (r"d2l\.ai", "sphinx", False),
    (r"readthedocs\.io", "sphinx", False),
    # 技术博客
    (r"lilianweng\.github\.io", "blog", True),
    (r"jalammar\.github\.io", "blog", True),
    (r"karpathy\.github\.io", "blog", True),
    (r"distill\.pub", "blog", True),
    (r"huyenchip\.com", "blog", True),
    # 学术
    (r"arxiv\.org/(abs|pdf)", "arxiv", False),
    (r"openreview\.net", "openreview", True),
    # 研究机构
    (r"anthropic\.com/research", "generic", False),
    (r"openai\.com/research", "generic", False),
    (r"deepmind\.google", "generic", False),
    # GitHub
    (r"github\.com/[^/]+/[^/]+", "generic", False),
    # 兜底
    (r"https?://", "generic", False),
]


def identify(url: str) -> Platform:
    """识别 URL 所属平台"""
    for pattern, platform_key, needs_browser in PLATFORM_RULES:
        if re.search(pattern, url, re.IGNORECASE):
            return Platform(
                name=_platform_name(platform_key),
                key=platform_key,
                extractor=platform_key,
                needs_browser=needs_browser,
            )
    return Platform(name="未知", key="generic", extractor="generic", needs_browser=False)


def _platform_name(key: str) -> str:
    names = {
        "bilibili": "B站",
        "youtube": "YouTube",
        "sphinx": "Sphinx文档",
        "blog": "技术博客",
        "arxiv": "arXiv",
        "openreview": "OpenReview",
        "generic": "通用网页",
    }
    return names.get(key, key)
