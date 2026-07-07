# web-distill

> 把任意 URL 变成知识库条目 — 一行命令，自动识别平台、提取内容、按话题落盘

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 安装

```bash
# 基础安装（通用网页 + B站）
pip install git+https://github.com/Aileen0113/web-distill.git

# 含 YouTube 支持
pip install "git+https://github.com/Aileen0113/web-distill.git#egg=web-distill[all]"
```

## 快速开始

```bash
# 提取到终端
web-distill https://lilianweng.github.io/posts/2023-06-23-agent/

# 保存到文件（自动按话题分类）
web-distill https://www.bilibili.com/video/BV1xx411c7mD --save

# 指定输出目录
web-distill https://example.com/article --save -o ./my-notes

# 手动指定话题
web-distill https://www.youtube.com/watch?v=xxx --topic ai --save

# JSON 输出（供管道消费）
web-distill https://example.com --json | jq .
```

## 支持的平台

| 平台 | 提取内容 |
|------|---------|
| **通用网页** | 正文（Readability）+ 元数据 |
| **B站** | 标题 / 描述 / UP主 / 时长 / 播放量 |
| **YouTube** | 元数据 + 字幕（需 yt-dlp） |

更多平台开发中：小鹅通、Sphinx 文档、arXiv、技术博客。

## 话题自动分类

根据内容关键词自动归类到子目录：

```
distill-output/
├── ai-ml/          # AI / 大模型 / 深度学习
├── finance/        # 投资 / 金融 / 区块链
├── engineering/    # 编程 / 开发 / 架构
├── design/         # 设计 / UI / 交互
├── business/       # 产品 / 商业 / 出海
├── research/       # 学术 / 论文
├── thinking/       # 哲学 / 心理 / 认知
├── health/         # 健康 / 医学
├── humanities/     # 历史 / 文化
├── media/          # 视频 / 教程 / 播客
└── uncategorized/  # 未匹配
```

**自定义话题映射**：创建 JSON 配置文件，用 `--config` 指定：

```json
{
  "topics": {
    "AI|Agent|LLM": "ai",
    "投资|股票|基金": "investing"
  }
}
```

## 输出格式

每个 URL 生成一个 Markdown 文件，包含完整元数据和正文。

## 配置

**不内置任何 API 密钥。** 所有认证信息由用户自己提供：

```bash
# 环境变量
export WEB_DISTILL_LLM_KEY=sk-xxx      # LLM 摘要（未来功能）
export XIAOEKNOW_KO_TOKEN=xxx           # 小鹅通 cookie

# 命令行参数
web-distill <url> --config ./my-topics.json
```

详见 `.env.example`。

## 设计原则

- **平台自动识别** — 根据 URL 匹配最适合的提取策略
- **可扩展** — 每个平台一个 extractor，社区可贡献
- **可配置** — 输出目录、话题分类均可自定义
- **管道友好** — 支持 JSON 输出，方便与其他工具组合

## License

MIT
