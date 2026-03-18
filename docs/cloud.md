# MemoryX 云端同步指南

## 概述

MemoryX 支持将数据同步到云端存储，实现跨设备数据共享和备份。

## 支持的云服务

### ✅ 已支持

| 服务 | 状态 | 前缀 | 说明 |
|------|------|------|------|
| AWS S3 | ✅ | s3:// | Amazon Simple Storage Service |
| Google Cloud Storage | ✅ | gs:// | Google Cloud Storage |

### 🚧 国内厂商 (开发中)

| 服务 | 状态 | 前缀 | 说明 |
|------|------|------|------|
| 阿里云 OSS | 🚧 | oss:// | 阿里云对象存储 |
| 腾讯云 COS | 🚧 | cos:// | 腾讯云对象存储 |
| 华为云 OBS | 🚧 | obs:// | 华为云对象存储 |
| 百度云 BOS | 🚧 | bos:// | 百度云对象存储 |
| 字节火山引擎 | 🚧 | ve:// | 火山引擎对象存储 |
| 京东云 | 🚧 | jd:// | 京东云对象存储 |

---

## 用户反馈

### 提交希望支持的云厂商

如果您希望 MemoryX 支持某个云厂商，请提交反馈：

```python
from memoryx.cloud import CloudSync

# 初始化
cloud = CloudSync(config)

# 提交反馈
cloud.submit_feedback(
    provider="阿里云",          # 云厂商名称
    user_email="you@example.com",  # 您的邮箱
    note="需要支持海外区域"     # 备注
)
```

### 查看支持状态

```python
# 查看所有支持的云厂商
providers = cloud.get_supported_providers()
for key, info in providers.items():
    print(f"{info['name']}: {info['status']}")

# 查看热门需求
pending = cloud.get_pending_providers()
print(f"热门需求: {pending}")
```

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

### 国内厂商

国内云厂商支持正在开发中，请提交反馈告诉我们您需要的厂商！
