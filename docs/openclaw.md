# MemoryX OpenClaw 插件

## 状态：✅ 已完成

MemoryX 已可以作为 OpenClaw 插件使用。

---

## 安装

### 方式一：pip 安装

```bash
pip install memoryx
```

### 方式二：GitHub 安装

```bash
pip install git+https://github.com/danieljack-OpenClaw/MemoryX.git
```

---

## 配置

### 1. 环境变量

```bash
# 必需
export MEMORYX_STORAGE_PATH=~/.memoryx

# 可选 (用于LLM摘要)
export OPENAI_API_KEY=your-openai-key
export LLM_API_KEY=your-llm-key
```

### 2. OpenClaw 配置

在 OpenClaw 配置文件中添加：

```yaml
# openclaw.yaml
plugins:
  memoryx:
    enabled: true
    storage_path: ~/.memoryx
    compression_enabled: true
    max_context_tokens: 4000
    auto_backup: true
    vector_db: chroma
```

---

## 使用方法

### 在对话中直接使用

```
用户: 记住我喜欢蓝色
AI: 已记住！你喜欢蓝色

用户: 我之前说过什么?
AI: 你喜欢蓝色，还提到...

用户: 给我最近的上下文
AI: (返回压缩后的记忆上下文)
```

### Python API

```python
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel

# 初始化
memory = MemoryX()

# 存储记忆
memory.add(
    user_id="user_123",
    content="用户喜欢简洁的回答",
    level=MemoryLevel.USER
)

# 搜索
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

### REST API

启动服务：

```bash
python -m memoryx.api.server --port 8000
```

API 端点：

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /memory | 添加记忆 |
| GET | /memory/{id} | 获取记忆 |
| POST | /memory/search | 搜索 |
| DELETE | /memory/{id} | 删除 |
| POST | /context | 获取上下文 |
| POST | /evolve | 技能进化 |
| POST | /backup | 备份 |
| POST | /backup/{id}/restore | 恢复 |

---

## 功能特性

### ✅ 已实现

- 多层级记忆 (User/Session/Agent/Skill/Project)
- 语义搜索 (真实向量嵌入)
- Token 压缩
- 自动备份
- 技能进化引擎
- 多 Agent 管理

### 🔄 即将支持

- 云端同步
- Web Dashboard

---

## 故障排除

### 导入错误

```bash
pip install memoryx
```

### 向量模型下载慢

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### Token 消耗过高

```python
config = Config(
    max_context_tokens=2000  # 降低
)
```

---

## 相关文档

- [API 参考](../docs/api.md)
- [配置说明](../docs/config.md)
- [安装指南](../docs/installation.md)
