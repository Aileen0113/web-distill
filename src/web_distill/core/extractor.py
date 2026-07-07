"""内容提取器 — 统一接口，根据平台分发"""

from web_distill.core.identifier import Platform, identify as identify_platform
from web_distill.core.types import ExtractedContent
from web_distill.platforms.base import BaseExtractor
from web_distill.platforms.generic import GenericExtractor
from web_distill.platforms.bilibili import BilibiliExtractor

# YouTube 可选导入
try:
    from web_distill.platforms.youtube import YoutubeExtractor
    _has_youtube = True
except ImportError:
    _has_youtube = False


def get_extractor(platform: Platform) -> BaseExtractor:
    """根据平台获取对应的提取器"""
    extractors = {
        "generic": GenericExtractor,
        "bilibili": BilibiliExtractor,
    }
    if _has_youtube:
        extractors["youtube"] = YoutubeExtractor

    cls = extractors.get(platform.key, GenericExtractor)
    return cls()


def extract(url: str) -> ExtractedContent:
    """提取 URL 内容的主入口"""
    platform = identify_platform(url)
    extractor = get_extractor(platform)
    return extractor.extract(url)
