"""格式化器 — 将提取内容格式化为干净的 Markdown"""

from datetime import datetime

from web_distill.core.types import ExtractedContent


def format_markdown(content: ExtractedContent, source_url: str) -> str:
    """将提取内容格式化为 Markdown"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    platform_label = _platform_label(content.platform)

    lines = [
        f"# {content.title}",
        "",
        f"> 来源: {source_url}",
        f"> 平台: {platform_label}",
        f"> 提取时间: {now}",
    ]

    if content.author:
        lines.append(f"> 作者: {content.author}")
    if content.date:
        lines.append(f"> 发布日期: {content.date}")
    if content.duration:
        lines.append(f"> 时长: {content.duration}")

    lines.extend([
        "",
        "---",
        "",
    ])

    # 摘要
    if content.description:
        lines.append(content.description)
        lines.append("")

    # 正文
    if content.body:
        body = content.body[:8000]
        if len(content.body) > 8000:
            body += "\n\n> ... 内容过长，已截断。完整内容请访问原文。"
        lines.append(body)
    else:
        lines.append("> 无法提取正文，请访问原文。")

    return "\n".join(lines)


def _platform_label(key: str) -> str:
    labels = {
        "bilibili": "B站",
        "youtube": "YouTube",
        "xiaoeknow": "小鹅通",
        "sphinx": "文档站",
        "blog": "技术博客",
        "arxiv": "arXiv",
        "generic": "网页",
    }
    return labels.get(key, key)
