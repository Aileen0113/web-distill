# 示例：三行命令提取三个不同平台

echo "=== web-distill 快速演示 ===\n"

# 1. 通用网页
echo "--- 1. 通用网页 ---"
python -m web_distill.cli https://lilianweng.github.io/posts/2023-06-23-agent/ 2>&1 | head -20
echo ""

# 2. B站
echo "--- 2. B站 ---"
python -m web_distill.cli https://www.bilibili.com/video/BV1xx411c7mD 2>&1 | head -20
echo ""

# 3. YouTube (需要 yt-dlp)
echo "--- 3. YouTube ---"
python -m web_distill.cli https://www.youtube.com/watch?v=dQw4w9WgXcQ 2>&1 | head -20
echo ""

echo "=== 演示完成 ==="
