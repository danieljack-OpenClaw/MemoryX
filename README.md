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
| ⚡ **90% Token 节省** | 智能记忆压缩 + LLM 摘要 |
| 🧠 **多层级记忆** | User / Session / Agent / Skill / Project |
| 🔍 **语义搜索** | 真实向量嵌入 (all-MiniLM-L6-v2) |
| 🔄 **技能进化** | 基于 GEP 协议的自动进化引擎 |
| 🤖 **多 Agent 协作** | 记忆共享与隔离 |
| 💾 **自动备份** | 本地 + 云端备份 |

## 📊 性能指标

- Token 节省: **60-90%**
- 语义相似度: **0.69+** (相关文本)
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

## 🏗️ 系统架构

```
MemoryX
├── core/              # 核心功能
│   ├── memory.py     # 记忆系统
│   ├── compressor.py # Token 压缩
│   ├── search.py    # 语义搜索
│   ├── graph.py     # 知识图谱
│   └── storage.py   # 存储管理
├── evolution/        # 进化引擎
├── backup/          # 备份管理
├── agent/           # 多 Agent
└── api/            # REST API
```

## 📖 文档目录

- [安装指南](docs/installation.md)
- [快速开始](docs/quickstart.md)
- [API 参考](docs/api.md)
- [配置说明](docs/config.md)
- [OpenClaw 集成](docs/openclaw.md)
- [部署指南](docs/deployment.md)
- [故障排除](docs/troubleshooting.md)

## 🤝 贡献

欢迎贡献！请提交 Issue 或 Pull Request。

## 📜 License

Apache License 2.0

---

*让 AI Agent 拥有真正的长期记忆 🧠*
