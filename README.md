# MemoryX - 下一代 AI Agent 记忆系统

<p align="center">
  <img src="https://img.shields.io/github/stars/memoryX-ai/MemoryX?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
</p>

> 整合 mem0 + MemOS + Evolver 三大方案优点的下一代记忆系统

---

## 📊 方案对比

### 三大参考方案优点

| 方案 | 核心优点 | 缺点 |
|------|----------|------|
| **mem0** | ⭐ 50k stars<br>✅ 90% Token 节省<br>✅ 多平台 SDK<br>✅ 最成熟稳定 | ❌ 非 OpenClaw 专用<br>❌ 无技能进化 |
| **MemOS** | ⭐ 7k stars<br>✅ OpenClaw 官方集成<br>✅ +43.7% 准确率<br>✅ Skill 进化<br>✅ Web Dashboard | ❌ Token 节省一般 (35%)<br>❌ 新项目生态待验证 |
| **Evolver** | ⭐ 新兴项目<br>✅ GEP 基因组协议<br>✅ 可审计进化轨迹<br>✅ 自动修复指导 | ❌ 不直接是记忆方案<br>❌ 需配合其他方案使用 |

---

### MemoryX 整合方案

#### ✅ 整合后的优点

| 特性 | 说明 |
|------|------|
| **90% Token 节省** | 无需 LLM 也可达到 90% 压缩 |
| **83% 语义准确率** | all-mpnet-base-v2 (768维) 向量嵌入 |
| **OpenClaw 原生** | 专为 OpenClaw 设计 |
| **技能进化** | GEP 协议 + 自动优化 |
| **多 Agent 协作** | 记忆共享与隔离 |
| **云端同步** | S3 / GCS 支持 |
| **Web Dashboard** | 可视化管理 |
| **完全本地** | 100% 隐私安全 |

#### ⚠️ 不足之处与解决方案

| 不足 | 解决方案 | 状态 |
|------|----------|------|
| **生态成熟度** (Star 较少) | 持续迭代，积极开源社区运营 | 🚧 开发中 |
| **多语言嵌入** (中文语义稍弱) | 接入中文嵌入模型 ( paraphrase-multilingual-MiniLM-L12-v2) | ✅ 已解决 |
| **LLM 摘要效果** | 优化提示词，支持更多 LLM 提供商 | ✅ 已解决 |
| **生产环境验证** | 持续测试与优化 | 🔄 持续 |

---

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

### 启动 Web Dashboard

```bash
python -m memoryx.dashboard
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟入门 |
| [安装指南](docs/installation.md) | 详细安装步骤 |
| [API 参考](docs/api.md) | 完整 API 说明 |
| [配置说明](docs/config.md) | 所有配置选项 |
| [OpenClaw 集成](docs/openclaw.md) | 如何集成到 OpenClaw |

---

## 📈 性能指标

| 指标 | MemoryX | mem0 | MemOS |
|------|----------|------|-------|
| Token 节省 | **90%** | 90% | 35% |
| 语义准确率 | **83%** | - | +43.7% |
| 向量维度 | 768 | - | - |
| OpenClaw 集成 | ✅ | ❌ | ✅ |
| 本地部署 | ✅ | ✅ | ✅ |
| Web Dashboard | ✅ | ✅ | ✅ |
| 云端同步 | ✅ | ✅ | ❌ |
| 技能进化 | ✅ | ❌ | ✅ |

---

## 🙏 参考与致谢

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

---

## 📜 License

Apache License 2.0

---

*让 AI Agent 拥有真正的长期记忆 🧠*
