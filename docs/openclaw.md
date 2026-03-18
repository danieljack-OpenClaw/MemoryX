# MemoryX OpenClaw 集成指南

本文档说明如何将 MemoryX 集成到 OpenClaw。

## 方式一：作为 Python 模块直接集成

### 1. 安装 MemoryX

```bash
pip install memoryx
```

### 2. 创建 OpenClaw 技能

在 OpenClaw 工作空间创建技能:

```bash
mkdir -p ~/.openclaw/skills/memoryx
```

创建 `SKILL.md`:

```markdown
# MemoryX Skill

提供长期记忆存储和检索功能。

## 触发词
- 记住
- 记忆
- 保存

## 功能
- add_memory: 添加记忆
- search_memory: 搜索记忆
- get_context: 获取上下文

## 使用
调用 memoryx Python 模块执行记忆操作。
```

### 3. 在 OpenClaw 中使用

在对话中:

```
用户: 记住我喜欢蓝色
AI: 已记住，你喜欢蓝色

用户: 我喜欢什么颜色?
AI: 你喜欢蓝色 (从记忆中检索)
```

---

## 方式二：REST API 集成

### 1. 启动 MemoryX API 服务

```bash
# 默认端口 8000
python -m memoryx.api.server

# 自定义端口
python -m memoryx.api.server --port 8080
```

### 2. 配置 OpenClaw

在 OpenClaw 配置中添加 HTTP 工具调用 MemoryX API:

```yaml
# openclaw.yaml
plugins:
  http:
    enabled: true
    endpoints:
      memoryx:
        url: http://localhost:8000
        headers:
          Content-Type: application/json
```

### 3. 使用

```
记住我的密码是 123456
(调用 POST /memory)

我的密码是什么?
(调用 POST /memory/search)
```

---

## 方式三：作为 OpenClaw 插件 (开发中)

```yaml
# 未来支持
plugins:
  memoryx:
    enabled: true
    storage_path: ~/.memoryx
    vector_db: chroma
    auto_backup: true
```

---

## 技能模板示例

创建一个记忆助手技能:

```bash
mkdir -p skills/memory-assistant
```

**SKILL.md:**
```markdown
# Memory Assistant

你的个人记忆助手。

## 功能

### 记住信息
- 触发: "记住"、"存储"、"记一下"
- 操作: 调用 memory.add()

### 回忆信息
- 触发: "我之前说过什么"、"记得吗"
- 操作: 调用 memory.search()

### 获取背景
- 触发: "之前聊过什么"
- 操作: 调用 memory.get_context()

## 记忆层级

- 用户偏好 (USER): 永久
- 当前任务 (SESSION): 会话期间
- 项目信息 (PROJECT): 项目期间
- 技能知识 (SKILL): 技能有效期间

## 示例

用户: "记住我喜欢简洁的回答"
AI: 已记住！你喜欢简洁的回答风格。

用户: "我之前说过什么?"
AI: 你之前说过你喜欢简洁的回答，还提到...
```

---

## 高级配置

### Token 压缩

```python
config = Config(
    compression_enabled=True,
    max_context_tokens=4000,  # 最大上下文 token 数
    compression_threshold=1000  # 超过此值启用压缩
)
```

### 向量搜索

```python
config = Config(
    vector_db_type="chroma",  # chroma / qdrant / pinecone
)
```

### 自动备份

```python
config = Config(
    auto_backup=True,
    backup_interval_hours=24,
    backup_retention_days=30,
    remote_backup_enabled=True,
    remote_backup_path="s3://your-bucket/backups"
)
```

### LLM 摘要

```python
config = Config(
    llm_provider="openai",
    llm_model="gpt-4o-mini",
    llm_api_key="your-key"
)
```

---

## 故障排除

### 记忆未保存

检查:
1. 存储目录权限
2. 数据库是否正常

### 搜索无结果

检查:
1. 嵌入模型是否加载
2. 向量数据库是否有数据

### Token 消耗过高

解决:
1. 降低 max_context_tokens
2. 启用 LLM 摘要

---

## 完整示例

```python
from memoryx import MemoryX
from memoryx.core.models import MemoryLevel

# 初始化
memory = MemoryX()

# 用户对话中记住偏好
memory.add(
    user_id="user_123",
    content="用户喜欢简洁的沟通风格，每次不超过3句话",
    level=MemoryLevel.USER,
    metadata={"source": "conversation"}
)

# 搜索相关记忆
results = memory.search(
    user_id="user_123",
    query="沟通风格偏好"
)

# 获取压缩上下文用于回复
context = memory.get_context(
    user_id="user_123",
    max_tokens=1000
)
```

---

## 相关文档

- [API 参考](api.md)
- [配置说明](config.md)
- [部署指南](deployment.md)
