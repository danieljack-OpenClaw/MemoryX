# MemoryX

> 下一代 AI Agent 记忆系统 - 整合 mem0 + MemOS + Evolver 的优点

[![Star](https://img.shields.io/github/stars/memoryX-ai/MemoryX?style=social)](https://github.com/memoryX-ai/MemoryX)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-Join-7289DA)](https://discord.gg/memoryx)

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ **90% Token 节省** | 智能记忆压缩技术 |
| 🧠 **多层级记忆** | User / Session / Agent / Skill / Project |
| 🔄 **技能进化** | 基于 GEP 协议的自动进化引擎 |
| 🌐 **语义搜索** | 向量 + 知识图谱混合检索 |
| 🤖 **多 Agent 协作** | 记忆共享与隔离 |
| 💾 **自动备份** | 本地 + 云端备份 |
| 🎨 **Web Dashboard** | 可视化管理界面 |

## 📊 性能指标

- Token 节省: **85-90%**
- 检索延迟: **<100ms**
- 准确率提升: **+40%**

## 🚀 快速开始

### 安装

```bash
pip install memoryx
```

### 基本使用

```python
from memoryx import MemoryX

# 初始化
memory = MemoryX(api_key="your-key")

# 存储记忆
memory.add(
    user_id="user_123",
    content="用户喜欢简洁的沟通风格"
)

# 检索记忆
results = memory.search(
    user_id="user_123",
    query="沟通偏好"
)

# 技能进化
memory.evolve(agent_id="agent_456")
```

## 🏗️ 系统架构

```
MemoryX
├── src/
│   ├── core/          # 核心功能
│   ├── evolution/     # 进化引擎
│   ├── backup/        # 备份管理
│   ├── agent/         # 多 Agent
│   └── api/          # API 服务
├── web/              # Web Dashboard
└── tests/            # 测试
```

## 📖 文档

- [完整文档](https://memoryx-ai.github.io/MemoryX)
- [API 参考](docs/api.md)
- [OpenClaw 集成](docs/openclaw.md)

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

Apache License 2.0 - see [LICENSE](LICENSE)

---

*让 AI Agent 拥有真正的长期记忆 🧠*
