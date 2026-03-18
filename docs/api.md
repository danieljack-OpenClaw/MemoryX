# MemoryX API 参考

## 核心类

### MemoryX

主类，提供所有记忆功能。

```python
from memoryx import MemoryX

memory = MemoryX(config=None, api_key=None)
```

#### 方法

##### add()

添加记忆

```python
memory.add(
    user_id: str,           # 用户 ID
    content: str,           # 记忆内容
    level: str = MemoryLevel.USER,  # 记忆层级
    metadata: dict = None,  # 额外元数据
    agent_id: str = None,  # Agent ID
    skill_id: str = None,  # Skill ID
    project_id: str = None  # Project ID
) -> Memory
```

**示例:**
```python
mem = memory.add(
    user_id="user_001",
    content="用户喜欢蓝色",
    level=MemoryLevel.USER,
    metadata={"source": "conversation"}
)
print(mem.id)  # mem_u_abc123
```

---

##### search()

语义搜索记忆

```python
memory.search(
    user_id: str,       # 用户 ID
    query: str,         # 查询内容
    level: str = None,  # 记忆层级过滤
    limit: int = 5,     # 返回数量
    agent_id: str = None  # Agent ID 过滤
) -> List[Dict]
```

**示例:**
```python
results = memory.search(
    user_id="user_001",
    query="用户颜色偏好",
    limit=3
)

for r in results:
    print(f"ID: {r['id']}, Score: {r['score']:.3f}")
```

---

##### get()

获取单条记忆

```python
memory.get(memory_id: str) -> Optional[Memory]
```

**示例:**
```python
mem = memory.get("mem_u_abc123")
if mem:
    print(mem.content)
```

---

##### update()

更新记忆

```python
memory.update(
    memory_id: str,
    content: str = None,
    metadata: dict = None
) -> Optional[Memory]
```

---

##### delete()

删除记忆

```python
memory.delete(memory_id: str) -> bool
```

---

##### get_context()

获取压缩后的上下文

```python
memory.get_context(
    user_id: str,
    agent_id: str = None,
    max_tokens: int = 4000
) -> str
```

**示例:**
```python
context = memory.get_context(
    user_id="user_001",
    max_tokens=1000
)
# context 是压缩后的记忆摘要
```

---

##### evolve()

执行技能进化

```python
memory.evolve(agent_id: str = None) -> Dict
```

**返回:**
```python
{
    "event_id": "ev_agent_001_20240318",
    "strategy": "balanced",
    "genes": ["memory_compress", "semantic_search"],
    "changes": {...},
    "status": "applied"
}
```

---

##### backup()

创建备份

```python
memory.backup(remote: bool = False) -> str
```

**示例:**
```python
backup_id = memory.backup()
print(f"Backup created: {backup_id}")
```

---

##### restore()

恢复备份

```python
memory.restore(backup_id: str) -> bool
```

---

##### get_stats()

获取统计信息

```python
memory.get_stats(user_id: str = None) -> Dict
```

**返回:**
```python
{
    "total_memories": 150,
    "storage_size": 2048576,
    "vector_dim": 384
}
```

---

##### close()

关闭连接

```python
memory.close()
```

---

## 记忆层级 (MemoryLevel)

```python
from memoryx.core.models import MemoryLevel

MemoryLevel.USER     # 用户级别 - 永久
MemoryLevel.SESSION  # 会话级别 - 会话期间
MemoryLevel.AGENT    # Agent 级别 - 永久
MemoryLevel.SKILL    # Skill 级别 - 技能存在期间
MemoryLevel.PROJECT  # 项目级别 - 项目期间
```

---

## 配置 (Config)

```python
from memoryx.core.config import Config

config = Config(
    # API 配置
    api_key="your-api-key",
    
    # 存储配置
    storage_path="~/.memoryx",
    
    # 模式: local / cloud
    mode="local",
    
    # 向量数据库
    vector_db_type="chroma",
    
    # Token 压缩
    compression_enabled=True,
    max_context_tokens=4000,
    
    # 备份
    auto_backup=True,
    backup_interval_hours=24,
    
    # LLM (用于摘要)
    llm_provider="openai",
    llm_model="gpt-4o-mini",
    llm_api_key="your-llm-key"
)
```

---

## REST API

启动 REST API 服务器:

```bash
python -m memoryx.api.server
```

### 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /memory | 添加记忆 |
| GET | /memory/{id} | 获取记忆 |
| POST | /memory/search | 搜索记忆 |
| DELETE | /memory/{id} | 删除记忆 |
| POST | /context | 获取压缩上下文 |
| POST | /evolve | 执行进化 |
| POST | /backup | 创建备份 |
| POST | /backup/{id}/restore | 恢复备份 |
| GET | /stats | 获取统计 |

### 示例

```bash
# 添加记忆
curl -X POST http://localhost:8000/memory \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "content": "测试", "level": "user"}'

# 搜索
curl -X POST http://localhost:8000/memory/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "query": "测试"}'
```
