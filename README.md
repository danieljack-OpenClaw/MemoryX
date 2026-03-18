# MemoryX - 下一代 AI Agent 记忆系统

<p align="center">
  <img src="https://img.shields.io/github/stars/memoryX-ai/MemoryX?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/Version-0.1.0-blue" alt="Version">
</p>

> 整合 mem0 + MemOS + Evolver 三大方案的优点

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ **90% Token 节省** | + LLM 摘要 |
| 🧠 **多 智能记忆压缩层级记忆** | User / Session / Agent / Skill / Project |
| 🔍 **语义搜索** | 真实向量嵌入 (all-mpnet-base-v2) |
| 🔄 **技能进化** | 基于 GEP 协议的自动进化引擎 |
| 🤖 **多 Agent 协作** | 记忆共享与隔离 |
| 💾 **自动备份** | 本地 + 云端备份 |

## 📊 性能指标

- 语义相似度: **83%** 准确率
- Token 节省: **60-90%**
- 向量维度: **768维**
- 检索延迟: **<100ms**

## 🚀 快速开始

### 安装

```bash
pip install memoryx
```

### 基本使用

```python
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel

# 初始化
memory = MemoryX()

# 添加记忆
memory.add(
    user_id="user_123",
    content="用户喜欢简洁的沟通风格",
    level=MemoryLevel.USER
)

# 搜索记忆
results = memory.search(
    user_id="user_123",
    query="沟通偏好"
)

# 获取压缩上下文
context = memory.get_context(
    user_id="user_123",
    max_tokens=1000
)
```

## 📖 文档

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟入门 |
| [安装指南](docs/installation.md) | 详细安装步骤 |
| [API 参考](docs/api.md) | 完整 API 说明 |
| [配置说明](docs/config.md) | 所有配置选项 |
| [OpenClaw 集成](docs/openclaw.md) | 如何集成到 OpenClaw |

## 🙏 参考与致谢

MemoryX 整合并改进了以下优秀开源项目：

### 核心灵感来源

| 项目 | GitHub | 说明 |
|------|--------|------|
| **mem0** | [mem0ai/mem0](https://github.com/mem0ai/mem0) | 通用 AI 记忆层，90% Token 节省方案 |
| **MemOS** | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | OpenClaw 官方记忆系统，+43.7% 准确率 |
| **Evolver** | [EvoMap/evolver](https://github.com/EvoMap/evolver) | GEP 基因组进化协议 |

### 技术依赖

| 库 | 用途 |
|----|------|
| [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | 语义向量嵌入 |
| [ChromaDB](https://github.com/chroma-core/chroma) | 向量数据库 |
| [OpenAI](https://github.com/openai/openai-python) | LLM 摘要生成 |

### 相关项目

| 项目 | GitHub | 说明 |
|------|--------|------|
| **OpenViking** | [volcengine/OpenViking](https://github.com/volcengine/OpenViking) | 字节跳动上下文数据库 |
| **agency-agents** | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | 80+ AI Agent 专家团队 |

---

## 📜 License

Apache License 2.0

---

*让 AI Agent 拥有真正的长期记忆 🧠*
