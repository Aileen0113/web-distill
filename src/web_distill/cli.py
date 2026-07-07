#!/usr/bin/env python3
"""web-distill CLI — 把任意 URL 变成知识库条目

Usage:
  web-distill <url>                    提取并输出到终端
  web-distill <url> --save             提取并保存到 distill-output/
  web-distill <url> -o <dir>           指定输出目录
  web-distill <url> --topic <name>     指定话题名称
  web-distill <url> --json             以 JSON 格式输出
  web-distill <url> --config <file>    使用自定义话题配置
  web-distill --platforms              列出所有支持的平台
"""

import argparse
import json
import os
import sys

from web_distill import __version__
from web_distill.core.identifier import identify, PLATFORM_RULES
from web_distill.core.extractor import get_extractor
from web_distill.core.types import ExtractedContent
from web_distill.core.formatter import format_markdown
from web_distill.core.topic_router import (
    route_to_topic, get_output_path, append_or_create, load_topics,
)


def main():
    parser = argparse.ArgumentParser(
        prog="web-distill",
        description="把任意 URL 变成知识库条目 — 自动识别平台、提取内容、按话题落盘",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  web-distill https://example.com/article
  web-distill https://www.bilibili.com/video/BV1xx411c7mD --save
  web-distill https://www.youtube.com/watch?v=xxx --topic "ai" --save
  web-distill https://example.com --json | jq .
  web-distill --platforms
""",
    )
    parser.add_argument("url", nargs="?", help="要提取的网页 URL")
    parser.add_argument("--save", "-s", action="store_true", help="保存到文件")
    parser.add_argument("--topic", "-t", help="手动指定话题名称")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--output-dir", "-o", default="./distill-output",
                        help="输出目录 (默认: ./distill-output)")
    parser.add_argument("--config", "-c", default=None,
                        help="自定义话题配置文件 (JSON)")
    parser.add_argument("--platforms", "-p", action="store_true", help="列出支持的平台")
    parser.add_argument("--version", "-v", action="version", version=f"web-distill v{__version__}")

    args = parser.parse_args()

    if args.platforms:
        _list_platforms()
        return

    if not args.url:
        parser.print_help()
        sys.exit(1)

    url = args.url

    # 1. 识别平台
    platform = identify(url)
    print(f"🔍 {platform.name}", file=sys.stderr)

    # 2. 提取
    extractor = get_extractor(platform)
    content = extractor.extract(url)

    if not content.title or content.title == "提取失败":
        print(f"❌ 提取失败: {content.description}", file=sys.stderr)
        sys.exit(1)

    print(f"📄 {content.title}", file=sys.stderr)

    # 3. 格式化
    markdown = format_markdown(content, url)

    # 4. 输出
    if args.json:
        _output_json(content, markdown)
    elif args.save:
        _save_to_file(content, markdown, url, args)
    else:
        print(markdown)


def _save_to_file(content: ExtractedContent, markdown: str, url: str, args):
    base_dir = os.path.abspath(args.output_dir)
    topics_config = load_topics(args.config)

    topic = args.topic or route_to_topic(content.title, content.body, topics_config)
    filepath = get_output_path(base_dir, topic, content.title)
    action = append_or_create(filepath, markdown, url)

    print(f"📁 {topic}/", file=sys.stderr)
    print(f"{'🆕' if action == 'new' else '📎'} {filepath}", file=sys.stderr)


def _output_json(content: ExtractedContent, markdown: str):
    output = {
        "url": content.url,
        "title": content.title,
        "platform": content.platform,
        "content_type": content.content_type,
        "author": content.author,
        "date": content.date,
        "duration": content.duration,
        "description": content.description,
        "body_preview": content.body[:500],
        "metadata": content.metadata,
        "markdown": markdown,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def _list_platforms():
    print("支持的平台:\n")
    seen = set()
    for pattern, key, needs_browser in PLATFORM_RULES:
        if key in seen:
            continue
        seen.add(key)
        label = _platform_name(key)
        browser = " (需浏览器)" if needs_browser else ""
        print(f"  {label:12s}  {browser}")
    print(f"\n共 {len(seen)} 个平台")


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


if __name__ == "__main__":
    main()
