#!/bin/bash
# MemoryX OpenClaw 一键安装脚本

echo "MemoryX OpenClaw Plugin Installer"
echo "================================"

# 检查 OpenClaw
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw 未安装"
    exit 1
fi

# 创建目录
echo "📁 创建 skill 目录..."
mkdir -p ~/.openclaw/skills/memoryx

# 复制文件
echo "📦 复制插件文件..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd"
cp -r "$SCRIPT_DIR"/* ~/.openclaw/skills/memoryx/ 2>/dev/null || cp -r ./* ~/.openclaw/skills/memoryx/

# 安装依赖
echo "📚 安装 Python 依赖..."
pip install memoryx sentence-transformers chromadb --quiet

# 重启
echo "🔄 重启 OpenClaw..."
openclaw restart

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方式："
echo '  "记住我喜欢蓝色"'
echo '  "搜索颜色偏好"'
echo '  "获取上下文"'
echo ""
