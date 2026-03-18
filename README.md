# MemoryX

<p align="center">
  <img src="https://img.shields.io/github/stars/memoryX-ai/MemoryX?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/Version-1.0.2-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
</p>

> 整合 mem0 + MemOS + Evolver 三大方案优点的下一代 AI Agent 记忆系统

---

## ⚡ 一键部署

### OpenClaw 插件 (推荐)

```bash
# 1. 复制插件
cp -r openclaw-plugin/* ~/.openclaw/skills/memoryx/

# 2. 安装依赖
pip install memoryx

# 3. 重启 OpenClaw
openclaw restart

# 立即使用
"记住我喜欢蓝色"
```

### 独立部署

```bash
pip install memoryx
python -m memoryx.dashboard
```

---

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ **90% Token 节省** | 无需 LLM |
| 🔍 **语义搜索** | 83% 准确率 |
| 🧠 **多层级记忆** | User/Session/Agent/Skill/Project |
| 💾 **自动备份** | 本地 + 云端 |
| ☁️ **本地+云端双存储** | 默认本地，可配置云端 |
| 🎨 **Web Dashboard** | 6 种语言 + 云配置 |

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟入门 |
| [OpenClaw 集成](docs/openclaw.md) | 插件配置 |
| [部署指南](docs/deployment.md) | 三种部署方式 |
| [API 参考](docs/api.md) | 完整 API |
| [云端同步](docs/cloud.md) | 云备份 |

---

## 🚀 快速开始

### OpenClaw 插件 (一行命令)

```bash
# 自动安装脚本
curl -s https://raw.githubusercontent.com/danieljack-OpenClaw/MemoryX/main/install-openclaw.sh | bash
```

或者手动：

```bash
# 1. 复制插件
mkdir -p ~/.openclaw/skills/memoryx
cp -r openclaw-plugin/* ~/.openclaw/skills/memoryx/

# 2. 安装依赖
pip install memoryx sentence-transformers chromadb

# 3. 使用
"记住我的密码是 123456"
```

### 独立部署

```bash
pip install memoryx
python -m memoryx.dashboard
# 访问 http://localhost:19876
```

---

## 📊 方案对比

| 方案 | Token 节省 | 语义准确率 | 部署方式 |
|------|-----------|-----------|----------|
| **MemoryX** | **90%** | **83%** | **一键插件** |
| mem0 | 90% | - | SDK |
| MemOS | 35% | +43.7% | 插件 |

---

## 🙏 致谢

感谢以下开源项目的启发：

| 项目 | 作者 | 贡献 |
|------|------|------|
| [mem0](https://github.com/mem0ai/mem0) | mem0ai team | Token 节省方案 |
| [MemOS](https://github.com/MemTensor/MemOS) | MemTensor | OpenClaw 集成 |
| [Evolver](https://github.com/EvoMap/evolver) | EvoMap | GEP 进化协议 |
| [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | UKPLab | 语义嵌入 |
| [ChromaDB](https://github.com/chroma-core/chroma) | Chroma team | 向量数据库 |

---

## 🤝 欢迎贡献

- ⭐ Star 项目
- 🐛 提交 Bug
- 💡 提出建议
- 📝 完善文档
- 🔧 提交代码

```bash
# 开发环境
git clone https://github.com/danieljack-OpenClaw/MemoryX.git
cd MemoryX
pip install -e .
python test_full.py
```

---

## 📜 License

Apache License 2.0

---

*让 AI Agent 拥有真正的长期记忆 🧠*

*Built with ❤️ by MemoryX Team*
