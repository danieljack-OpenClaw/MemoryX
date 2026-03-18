# MemoryX 配置说明

## Config 类

```python
from memoryx.core.config import Config
```

## 参数

### API 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| api_key | str | None | API 密钥 (云端模式需要) |

### 存储配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| storage_path | Path | ~/.memoryx | 本地存储路径 |
| mode | str | "local" | 运行模式: local/cloud |

### 向量数据库

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| vector_db_type | str | "chroma" | 向量数据库类型: chroma/qdrant/pinecone |

### Token 压缩

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| compression_enabled | bool | True | 启用压缩 |
| compression_threshold | int | 1000 | 超过此值启用压缩 |
| max_context_tokens | int | 4000 | 最大上下文 token |

### 备份

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| auto_backup | bool | True | 启用自动备份 |
| backup_interval_hours | int | 24 | 备份间隔 (小时) |
| backup_retention_days | int | 30 | 备份保留天数 |
| remote_backup_enabled | bool | False | 启用远程备份 |
| remote_backup_path | str | None | 远程备份路径 (s3://...) |

### 进化

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| evolution_enabled | bool | True | 启用技能进化 |
| evolution_interval_hours | int | 168 | 进化间隔 (小时) |
| evolution_strategy | str | "balanced" | 策略: balanced/innovate/harden/repair |

### 多 Agent

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| default_isolation | bool | True | 默认记忆隔离 |
| allow_memory_sharing | bool | True | 允许记忆共享 |

### LLM

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| llm_provider | str | "openai" | LLM 提供商 |
| llm_model | str | "gpt-4" | LLM 模型 |
| llm_api_key | str | None | LLM API 密钥 |

---

## 环境变量

也可以通过环境变量配置:

```bash
export MEMORYX_API_KEY=your-key
export MEMORYX_MODE=cloud
export MEMORYX_STORAGE_PATH=~/.memoryx
export MEMORYX_LLM_PROVIDER=openai
export LLM_API_KEY=your-llm-key
```

---

## 配置文件

从 JSON 文件加载:

```python
config = Config.from_file("memoryx_config.json")
```

配置文件格式:

```json
{
  "api_key": "your-key",
  "storage_path": "~/.memoryx",
  "mode": "local",
  "compression_enabled": true,
  "max_context_tokens": 4000,
  "auto_backup": true,
  "llm_provider": "openai",
  "llm_model": "gpt-4o-mini",
  "llm_api_key": "your-key"
}
```

---

## 示例

### 本地模式 (推荐)

```python
config = Config(
    storage_path="~/.memoryx",
    compression_enabled=True,
    max_context_tokens=4000,
    auto_backup=True
)
```

### 云端模式

```python
config = Config(
    api_key="memoryx_xxx",
    mode="cloud",
    cloud_endpoint="https://api.memoryx.ai"
)
```

### 生产环境

```python
config = Config(
    storage_path="/data/memoryx",
    vector_db_type="qdrant",
    compression_enabled=True,
    max_context_tokens=8000,
    auto_backup=True,
    backup_interval_hours=12,
    remote_backup_enabled=True,
    remote_backup_path="s3://my-bucket/backups",
    llm_provider="openai",
    llm_model="gpt-4o",
    llm_api_key="sk-..."
)
```
