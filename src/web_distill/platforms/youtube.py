"""YouTube 提取器 — 通过 yt-dlp 获取视频信息和字幕

依赖: pip install web-distill[youtube]  # 安装 yt-dlp
"""

import json
import subprocess
import tempfile
import os

from web_distill.platforms.base import BaseExtractor
from web_distill.core.types import ExtractedContent
class YoutubeExtractor(BaseExtractor):
    """YouTube 视频提取（需要 yt-dlp）"""

    platform_name = "youtube"

    def extract(self, url: str) -> ExtractedContent:
        info = self._get_video_info(url)
        if not info:
            return self._make_content(
                url=url,
                title="提取失败",
                description="请确认已安装 yt-dlp: pip install yt-dlp",
            )

        title = info.get("title", "")
        description = info.get("description", "")
        uploader = info.get("uploader", info.get("channel", ""))

        # 字幕
        subtitles = self._get_subtitles(url) or ""

        body_parts = []
        if description:
            body_parts.append(f"## 视频描述\n\n{description}")
        if subtitles:
            body_parts.append(f"## 字幕\n\n{subtitles}")

        return self._make_content(
            url=url,
            title=title,
            body="\n\n".join(body_parts),
            description=description[:500] if description else f"YouTube 视频 | {uploader}",
            author=uploader,
            date=info.get("upload_date", ""),
            duration=self._format_duration(info.get("duration", 0)),
            content_type="video",
            metadata={
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "channel": uploader,
                "thumbnail": info.get("thumbnail"),
            },
        )

    @staticmethod
    def _get_video_info(url: str) -> dict | None:
        """通过 yt-dlp 获取视频元数据"""
        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--dump-json",
                    "--no-playlist",
                    "--no-warnings",
                    "--skip-download",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return None

    @staticmethod
    def _get_subtitles(url: str, lang: str = "zh-Hans,en") -> str | None:
        """下载字幕"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "--write-subs",
                        "--write-auto-subs",
                        f"--sub-lang", lang,
                        "--skip-download",
                        "--convert-subs", "srt",
                        "--no-warnings",
                        "-o", f"{tmpdir}/%(id)s",
                        url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                # 找字幕文件
                for f in os.listdir(tmpdir):
                    if f.endswith((".srt", ".vtt")):
                        filepath = os.path.join(tmpdir, f)
                        with open(filepath, "r", encoding="utf-8") as sf:
                            return YoutubeExtractor._clean_srt(sf.read())
                return None
        except Exception:
            return None

    @staticmethod
    def _clean_srt(srt: str) -> str:
        """清理 SRT 格式，只保留文本"""
        import re
        # 移除序号和时间戳
        text = re.sub(r"^\d+\s*$", "", srt, flags=re.MULTILINE)
        text = re.sub(
            r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}",
            "",
            text,
        )
        # 移除空行和多余换行
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return "\n".join(lines)

    @staticmethod
    def _format_duration(seconds: int) -> str:
        if not seconds:
            return ""
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
