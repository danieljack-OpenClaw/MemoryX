# MemoryX 快速开始

## 5 分钟入门

### 1. 安装

```bash
pip install memoryx
```

### 2. 基本使用

```python
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel

# 初始化
memory = MemoryX()

# 添加记忆
memory.add(
    user_id="user_001",
    content="用户喜欢蓝色",
    level=MemoryLevel.USER
)

# 搜索
results = memory.search(
    user_id="user_001",
    query="颜色偏好"
)

# 获取压缩上下文
context = memory.get_context(
    user_id="user_001",
    max_tokens=1000
)
```

---

## 完整示例

```python
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel
from memoryx.core.config import Config

# 配置
config = Config(
    storage_path="~/.memoryx",
    vector_db_type="chroma",
    compression_enabled=True,
    max_context_tokens=4000
)

# 初始化
memory = MemoryX(config)

# === 添加记忆 ===

# 用户偏好 (永久)
memory.add(
    user_id="user_001",
    content="用户是跨境电商从业者，主要销售运动鞋到欧美市场",
    level=MemoryLevel.USER,
    metadata={"topic": "business"}
)

# 当前任务 (会话级)
memory.add(
    user_id="user_001",
    content="正在分析 Facebook 广告数据，优化投放策略",
    level=MemoryLevel.SESSION,
    metadata={"task": "ad_optimization"}
)

# 项目信息
memory.add(
    user_id="user_001",
    content="本月目标：跨境收单日均 100万 USD",
    level=MemoryLevel.PROJECT,
    metadata={"project": "cross_border", "target": "100k"}
)

# === 搜索记忆 ===
results = memory.search(
    user_id="user_001",
    query="本月目标",
    limit=3
)

print(f"找到 {len(results)} 条相关记忆")
for r in results:
    print(f"- {r['id']}: {r.get('score', 0):.3f}")

# === 获取压缩上下文 ===
context = memory.get_context(
    user_id="user_001",
    max_tokens=500  # 压缩到 500 tokens
)

print(f"\n压缩后上下文 ({len(context)} 字符):")
print(context)

# === 技能进化 ===
result = memory.evolve(agent_id="ad_agent")
print(f"\n进化结果: {result['status']}")

# === 备份 ===
backup_id = memory.backup()
print(f"备份已创建: {backup_id}")

# 关闭
memory.close()
```

---

## 配置选项

### 基础配置

```python
config = Config(
    storage_path="~/.memoryx",  # 存储路径
    mode="local",               # local 或 cloud
)
```

### Token 压缩

```python
config = Config(
    compression_enabled=True,
    max_context_tokens=4000,  # 最大上下文
    compression_threshold=1000 # 超过则压缩
)
```

### 向量搜索

```python
config = Config(
    vector_db_type="chroma",  # chroma / qdrant / pinecone
)
```

### LLM 摘要

```python
config = Config(
    llm_provider="openai",
    llm_model="gpt-4o-mini",
    llm_api_key="sk-..."
)
```

### 自动备份

```python
config = Config(
    auto_backup=True,
    backup_interval_hours=24,
    backup_retention_days=30,
    remote_backup_enabled=False
)
```

---

## 下一步

- [API 参考](api.md)
- [OpenClaw 集成](openclaw.md)
- [配置说明](config.md)
