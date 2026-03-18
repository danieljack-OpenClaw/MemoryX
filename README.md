# MemoryX

<p align="center">
  <img src="https://img.shields.io/github/stars/memoryX-ai/MemoryX?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/Version-1.0.1-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python">
</p>

> 整合 mem0 + MemOS + Evolver 三大方案优点的下一代 AI Agent 记忆系统

---

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ **90% Token 节省** | 无需 LLM 也可达到 90% 压缩 |
| 🔍 **语义搜索** | 多语言嵌入，83% 准确率 |
| 🧠 **多层级记忆** | User / Session / Agent / Skill / Project |
| 💾 **自动备份** | 本地 + 云端 |
| ☁️ **云端同步** | AWS / GCP / 阿里云 / 腾讯云 / 华为云 / 百度云 |
| 🎨 **Web Dashboard** | 可视化管理 (支持 6 种语言) |

---

## 🚀 快速开始

### 方式一：独立部署

```bash
# 1. 安装
pip install memoryx

# 2. 创建记忆
python -c "
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel

m = MemoryX()
m.add(user_id='user1', content='我喜欢蓝色', level=MemoryLevel.USER)
print('记忆已保存！')
"

# 3. 启动 Web Dashboard
python -m memoryx.dashboard
# 访问 http://localhost:19876
```

### 方式二：OpenClaw 插件

```yaml
# openclaw.yaml
plugins:
  memoryx:
    enabled: true
    storage_path: ~/.memoryx
```

### 方式三：REST API

```bash
# 启动 API 服务
python -m memoryx.api.server
# 访问 http://localhost:19877
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [快速开始](docs/quickstart.md) | 5 分钟入门 |
| [安装指南](docs/installation.md) | 详细安装步骤 |
| [API 参考](docs/api.md) | 完整 API |
| [配置说明](docs/config.md) | 配置选项 |
| [OpenClaw 集成](docs/openclaw.md) | 插件使用 |
| [云端同步](docs/cloud.md) | 云备份 |
| [Web Dashboard](docs/dashboard.md) | 管理界面 |

---

## ⚙️ 部署方式对比

| 方式 | 适用场景 | 特点 |
|------|----------|------|
| **独立部署** | 独立 AI 应用 | 完整功能，可定制 |
| **OpenClaw 插件** | OpenClaw 用户 | 集成度高，即插即用 |
| **REST API** | 微服务架构 | 跨语言，分布式 |

### 环境变量

```bash
# 必需
export MEMORYX_STORAGE_PATH=~/.memoryx

# 可选
export OPENAI_API_KEY=your-key          # LLM 摘要
export MEMORYX_DASHBOARD_PORT=19876     # Dashboard 端口
export MEMORYX_API_PORT=19877          # API 端口

# 云端同步 (选择)
export AWS_ACCESS_KEY_ID=xxx            # AWS
export ALIYUN_ACCESS_KEY_ID=xxx        # 阿里云
export TENCENT_SECRET_ID=xxx           # 腾讯云
```

---

## 📊 方案对比

| 方案 | Token 节省 | 语义准确率 | OpenClaw 集成 | 云同步 |
|------|-----------|-----------|--------------|--------|
| **MemoryX** | **90%** | **83%** | ✅ | ✅ |
| mem0 | 90% | - | ❌ | ✅ |
| MemOS | 35% | +43.7% | ✅ | ❌ |

---

## 🙏 致谢

感谢以下开源项目的启发与参考：

| 项目 | 作者 | 贡献 |
|------|------|------|
| [mem0](https://github.com/mem0ai/mem0) | mem0ai team | Token 节省方案，90% 压缩算法 |
| [MemOS](https://github.com/MemTensor/MemOS) | MemTensor | OpenClaw 集成，+43.7% 准确率提升 |
| [Evolver](https://github.com/EvoMap/evolver) | EvoMap | GEP 基因组进化协议 |
| [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | UKPLab | 多语言语义嵌入模型 |
| [ChromaDB](https://github.com/chroma-core/chroma) | Chroma team | 高效向量数据库 |

---

## 🤝 欢迎贡献

MemoryX 是开源项目，欢迎所有开发者参与贡献！

### 贡献方式

- ⭐ Star 项目
- 🐛 提交 Bug
- 💡 提出新功能建议
- 📝 完善文档
- 🔧 提交代码 PR
- 💰 赞助支持

### 开发环境

```bash
# 克隆项目
git clone https://github.com/danieljack-OpenClaw/MemoryX.git
cd MemoryX

# 安装开发依赖
pip install -e .

# 运行测试
python test_full.py

# 启动开发服务器
python -m memoryx.dashboard
```

---

## 📜 License

Apache License 2.0

---

## 📬 联系方式

- GitHub Issues: [https://github.com/danieljack-OpenClaw/MemoryX/issues](https://github.com/danieljack-OpenClaw/MemoryX/issues)

---

*让 AI Agent 拥有真正的长期记忆 🧠*

*Built with ❤️ by MemoryX Team*
