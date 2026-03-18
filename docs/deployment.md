# MemoryX 部署指南

本文档详细介绍 MemoryX 的三种部署方式。

---

## 方式一：独立部署

### 适用场景
- 独立的 AI 应用
- 需要完整控制权
- 自定义需求强

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

### 启动 Dashboard

```bash
# 默认端口 19876
python -m memoryx.dashboard

# 自定义端口
python -m memoryx.dashboard --port 9000
```

### 启动 API

```bash
# 默认端口 19877
python -m memoryx.api.server

# 自定义端口
python -m memoryx.api.server --port 9001
```

---

## 方式二：OpenClaw 插件

### 适用场景
- OpenClaw 用户
- 需要与 OpenClaw 深度集成
- 一站式管理

### 安装

```bash
pip install memoryx
```

### 配置 OpenClaw

在 `openclaw.yaml` 中添加：

```yaml
plugins:
  memoryx:
    enabled: true
    storage_path: ~/.memoryx
    compression_enabled: true
    max_context_tokens: 4000
    auto_backup: true
    vector_db: chroma
```

### 使用

在 OpenClaw 对话中直接使用：

```
用户: 记住我喜欢蓝色
AI: 已记住！

用户: 我喜欢什么?
AI: 你喜欢蓝色
```

---

## 方式三：REST API 服务

### 适用场景
- 微服务架构
- 多语言客户端
- 分布式部署

### 启动服务

```bash
python -m memoryx.api.server --host 0.0.0.0 --port 19877
```

### API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/stats | 统计信息 |
| GET | /api/memory | 记忆列表 |
| POST | /api/memory | 添加记忆 |
| POST | /api/memory/search | 搜索 |
| DELETE | /api/memory/{id} | 删除 |
| POST | /api/backup | 创建备份 |
| POST | /api/cloud/sync | 云同步 |
| POST | /api/feedback | 提交反馈 |

### 示例

```bash
# 添加记忆
curl -X POST http://localhost:19877/api/memory \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "content": "测试", "level": "user"}'

# 搜索
curl -X POST http://localhost:19877/api/memory/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "query": "测试", "limit": 5}'
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|---------|------|
| MEMORYX_STORAGE_PATH | ~/.memoryx | 存储路径 |
| MEMORYX_DASHBOARD_PORT | 19876 | Dashboard 端口 |
| MEMORYX_API_PORT | 19877 | API 端口 |
| OPENAI_API_KEY | - | LLM 摘要 |
| AWS_ACCESS_KEY_ID | - | AWS S3 |
| ALIYUN_ACCESS_KEY_ID | - | 阿里云 OSS |

---

## 云端同步配置

### AWS S3

```bash
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_REGION=us-east-1
```

### 阿里云

```bash
export ALIYUN_ACCESS_KEY_ID=xxx
export ALIYUN_ACCESS_KEY_SECRET=xxx
```

---

## 性能优化

### 生产环境建议

1. **使用 SSD 存储**：提升向量检索速度
2. **配置 LLM**：启用智能摘要
3. **定期备份**：防止数据丢失
4. **监控资源**：关注内存和 CPU 使用
