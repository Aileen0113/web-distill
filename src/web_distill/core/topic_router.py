"""话题路由器 — 按话题自动分类，使用可配置的关键词映射

默认使用内置通用分类，用户可通过 --config 指定自己的映射文件。
"""

import os
import re
from pathlib import Path
from typing import Optional


# 默认通用话题映射（开源版，不含个人知识库结构）
DEFAULT_TOPICS = {
    "AI|Agent|LLM|GPT|Claude|大模型|深度学习|机器学习|人工智能": "ai-ml",
    "投资|股票|A股|量化|交易|基金|ETF|金融|加密货币|区块链|Web3": "finance",
    "编程|代码|开发|Python|Rust|Go|架构|API|数据库|DevOps": "engineering",
    "设计|UI|UX|CSS|动画|前端|交互": "design",
    "产品|创业|商业|商业模式|增长|营销|品牌|出海": "business",
    "学术|论文|研究|arXiv": "research",
    "哲学|心理|认知|思维|习惯": "thinking",
    "健康|医学|生物": "health",
    "历史|文化|社会": "humanities",
    "视频|教程|课程|演讲|播客": "media",
}


def load_topics(config_path: Optional[str] = None) -> dict:
    """加载话题映射配置"""
    if config_path and os.path.exists(config_path):
        import json
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("topics", DEFAULT_TOPICS)
    return DEFAULT_TOPICS


def route_to_topic(title: str, body: str = "", config: Optional[dict] = None) -> str:
    """
    根据标题和正文匹配话题目录名。
    返回话题名称（用于子目录名）。
    """
    topics = config or DEFAULT_TOPICS
    text = f"{title} {body[:1000]}"

    for keywords, topic_name in topics.items():
        if re.search(keywords, text, re.IGNORECASE):
            return topic_name

    return "uncategorized"


def get_output_path(base_dir: str, topic: str, title: str) -> str:
    """生成输出文件路径"""
    safe_title = _sanitize_filename(title)
    filename = f"{safe_title}.md"
    return os.path.join(base_dir, topic, filename)


def append_or_create(filepath: str, content: str, source_url: str) -> str:
    """
    如果文件已存在 → 追加更新块
    如果不存在 → 创建新文件
    返回操作类型: 'new' | 'append'
    """
    from datetime import datetime

    if os.path.exists(filepath):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        append_block = f"""

---
## [更新: {now}]

> 来源: {source_url}

{content}
"""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(append_block)
        return "append"
    else:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return "new"


def _sanitize_filename(name: str, max_len: int = 80) -> str:
    """清理文件名"""
    name = re.sub(r"[\[\]\(\)\*#\|\\/:]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    if len(name) > max_len:
        name = name[:max_len]
    return name
