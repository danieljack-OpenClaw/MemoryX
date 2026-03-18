# MemoryX 云端同步指南

## 概述

MemoryX 支持将数据同步到云端存储，实现跨设备数据共享和备份。

## 支持的云服务

| 服务 | 支持状态 | 说明 |
|------|----------|------|
| AWS S3 | ✅ | Amazon Simple Storage Service |
| Google Cloud Storage | ✅ | Google Cloud Storage (GCS) |

---

## AWS S3 配置

### 1. 安装依赖

```bash
pip install boto3
```

### 2. 配置环境变量

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### 3. 代码配置

```python
from memoryx.core.config import Config

config = Config(
    remote_backup_enabled=True,
    remote_backup_path="s3://your-bucket/memoryx-backup"
)
```

### 4. 使用

```python
from memoryx import MemoryX

memory = MemoryX()

# 同步到云端
memory.backup(remote=True)

# 或使用 CloudSync
from memoryx.cloud import CloudSync
sync = CloudSync(config)
sync.sync_to_cloud()
```

---

## Google Cloud Storage 配置

### 1. 安装依赖

```bash
pip install google-cloud-storage
```

### 2. 配置环境变量

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GCS_PROJECT=your-project-id
```

### 3. 代码配置

```python
config = Config(
    remote_backup_enabled=True,
    remote_backup_path="gs://your-bucket/memoryx-backup"
)
```

---

## 自动同步

### 配置自动同步

```python
config = Config(
    auto_backup=True,
    backup_interval_hours=24,
    remote_backup_enabled=True,
    remote_backup_path="s3://your-bucket/memoryx"
)
```

### 手动同步

```python
# 上传
sync.sync_to_cloud()

# 下载
sync.sync_from_cloud()
```

---

## 故障排除

### S3 权限问题

确保 IAM 用户有以下权限：
- s3:PutObject
- s3:GetObject
- s3:ListBucket

### GCS 权限问题

确保服务账号有以下权限：
- Storage Object Admin
- Storage Object Creator
