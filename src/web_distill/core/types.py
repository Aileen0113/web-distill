"""数据类型定义 — 避免循环导入"""

from dataclasses import dataclass, field


@dataclass
class ExtractedContent:
    """提取结果"""
    url: str
    title: str
    platform: str
    content_type: str = "article"  # article / video / course
    body: str = ""                 # 正文/字幕
    description: str = ""          # 描述/摘要
    author: str = ""
    date: str = ""
    duration: str = ""
    metadata: dict = field(default_factory=dict)
