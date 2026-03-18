# MemoryX 配置说明

## 快速配置

### 本地存储 (默认)

```python
from memoryx import MemoryX
memory = MemoryX()  # 默认本地存储
```

### 云端存储配置

```python
from memoryx import MemoryX
from memoryx.cloud import CloudSync

# 方式一：代码配置
memory = MemoryX()
cloud = CloudSync(memory.config)

# 配置云存储
cloud.configure_provider("aliyun", {
    "access_key_id": "your-key",
    "access_key_secret": "your-secret",
    "bucket": "your-bucket",
    "region": "cn-hangzhou"
})

# 启用云端存储
cloud.enable_cloud_storage()
```

### Web Dashboard 配置 (推荐)

1. 访问 Dashboard (默认 http://localhost:19876)
2. 进入「设置」标签
3. 配置云存储厂商
4. 启用云端存储

---

## Config 类

```python
from memoryx.core.config import Config
```

## 参数

### 存储配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| storage_path | Path | ~/.memoryx | 本地存储路径 |
| mode | str | "local" | 模式: local/cloud |
| cloud_enabled | bool | False | 启用云端存储 |
| cloud_provider | str | None | 云厂商: aliyun/tencent/huawei/baidu/aws/gcs |

### 向量数据库

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| vector_db_type | str | "chroma" | 类型: chroma/qdrant/pinecone |

### Token 压缩

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| compression_enabled | bool | True | 启用压缩 |
| max_context_tokens | int | 4000 | 最大上下文 token |

### 备份

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| auto_backup | bool | True | 启用自动备份 |
| backup_interval_hours | int | 24 | 备份间隔 (小时) |
| remote_backup_enabled | bool | False | 启用远程备份 |

### LLM (可选)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| llm_provider | str | None | LLM 提供商 |
| llm_api_key | str | None | LLM API 密钥 |

---

## 环境变量

```bash
# 本地存储 (默认)
export MEMORYX_STORAGE_PATH=~/.memoryx

# 云端存储
export MEMORYX_CLOUD_ENABLED=true
export MEMORYX_CLOUD_PROVIDER=aliyun

# 阿里云
export ALIYUN_ACCESS_KEY_ID=xxx
export ALIYUN_ACCESS_KEY_SECRET=xxx
export ALIYUN_BUCKET=xxx
export ALIYUN_REGION=cn-hangzhou

# 腾讯云
export TENCENT_SECRET_ID=xxx
export TENCENT_SECRET_KEY=xxx
export TENCENT_BUCKET=xxx
export TENCENT_REGION=ap-shanghai

# AWS
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_BUCKET=xxx
export AWS_REGION=us-east-1
```

---

## 配置文件

```json
{
  "storage_path": "~/.memoryx",
  "mode": "local",
  "cloud_enabled": false,
  "compression_enabled": true,
  "max_context_tokens": 4000,
  "auto_backup": true
}
```

云端存储配置:

```json
{
  "storage_path": "~/.memoryx",
  "cloud_enabled": true,
  "cloud_provider": "aliyun",
  "cloud_config": {
    "access_key_id": "xxx",
    "bucket": "my-bucket",
    "region": "cn-hangzhou"
  }
}
```

---

## 云厂商支持

| 厂商 | 前缀 | 状态 |
|------|------|------|
| 阿里云 OSS | oss:// | ✅ |
| 腾讯云 COS | cos:// | ✅ |
| 华为云 OBS | obs:// | ✅ |
| 百度云 BOS | bos:// | ✅ |
| AWS S3 | s3:// | ✅ |
| Google Cloud | gs:// | ✅ |

---

## 示例

### 本地模式 (默认)

```python
from memoryx import MemoryX

memory = MemoryX()  # 默认 ~/.memoryx
memory.add(user_id="u1", content="测试")
```

### 本地 + 云端双存储

```python
from memoryx import MemoryX
from memoryx.cloud import CloudSync

# 初始化
memory = MemoryX()

# 配置云端
cloud = CloudSync(memory.config)
cloud.configure_provider("aliyun", {
    "access_key_id": "xxx",
    "access_key_secret": "xxx", 
    "bucket": "my-memoryx",
    "region": "cn-hangzhou"
})
cloud.enable_cloud_storage()

# 自动同步到云端
memory.add(user_id="u1", content="测试")  # 同时保存到本地和云端
```

### 生产环境

```python
config = Config(
    storage_path="/data/memoryx",
    compression_enabled=True,
    max_context_tokens=8000,
    auto_backup=True,
    cloud_enabled=True,
    cloud_provider="aliyun"
)
```
