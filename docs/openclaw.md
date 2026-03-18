# MemoryX OpenClaw 插件

## 状态：✅ 已完成

MemoryX 已完整支持 OpenClaw，包含所有功能。

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

# 可选 - LLM摘要
export OPENAI_API_KEY=your-openai-key

# 可选 - 云端同步 (选择需要的)
# AWS
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/json

# 阿里云
export ALIYUN_ACCESS_KEY_ID=xxx
export ALIYUN_ACCESS_KEY_SECRET=xxx

# 腾讯云
export TENCENT_SECRET_ID=xxx
export TENCENT_SECRET_KEY=xxx

# 华为云
export HUAWEI_ACCESS_KEY_ID=xxx
export HUAWEI_ACCESS_KEY_SECRET=xxx
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

### 1. Python API

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

# 备份
memory.backup(remote=True)  # 云端备份
```

### 2. Web Dashboard

```bash
# 启动 Dashboard
python -m memoryx.dashboard
```

访问 http://localhost:8080

功能：
- 📊 统计面板
- 📚 记忆管理
- ➕ 添加记忆
- 🔍 语义搜索
- 💾 备份管理
- ⚙️ 系统设置

### 3. REST API

```bash
# 启动 API
python -m memoryx.api.server --port 8000
```

API 端点：

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/stats | 统计信息 |
| GET | /api/memory | 记忆列表 |
| POST | /api/memory | 添加记忆 |
| POST | /api/memory/search | 语义搜索 |
| DELETE | /api/memory/{id} | 删除记忆 |
| POST | /api/backup | 创建备份 |
| GET | /api/backup | 备份列表 |

---

## 功能特性

### ✅ 已实现

| 功能 | 说明 |
|------|------|
| 多层级记忆 | User/Session/Agent/Skill/Project |
| 语义搜索 | 多语言嵌入 (83% 准确率) |
| Token 压缩 | 90% 压缩 (无需 LLM) |
| 自动备份 | 本地/云端 |
| 云端同步 | AWS/GCS/阿里云/腾讯云/华为云/百度云 |
| Web Dashboard | 可视化管理界面 |
| 技能进化 | GEP 协议 |
| 多 Agent | 记忆共享与隔离 |

### 支持的云存储

| 服务 | 前缀 | 状态 |
|------|------|------|
| AWS S3 | s3:// | ✅ |
| Google Cloud Storage | gs:// | ✅ |
| 阿里云 OSS | oss:// | ✅ |
| 腾讯云 COS | cos:// | ✅ |
| 华为云 OBS | obs:// | ✅ |
| 百度云 BOS | bos:// | ✅ |

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
    max_context_tokens=2000
)
```

---

## 相关文档

- [API 参考](../docs/api.md)
- [配置说明](../docs/config.md)
- [安装指南](../docs/installation.md)
- [云端同步](../docs/cloud.md)
- [Web Dashboard](../docs/dashboard.md)
