# MemoryX 云端同步指南

## 概述

MemoryX 支持将数据同步到多种云端存储，实现跨设备数据共享和备份。

## 支持的云服务

### ✅ 全部支持

| 服务 | 前缀 | 说明 |
|------|------|------|
| AWS S3 | s3:// | Amazon Simple Storage Service |
| Google Cloud Storage | gs:// | Google Cloud Storage |
| 阿里云 OSS | oss:// | 阿里云对象存储 |
| 腾讯云 COS | cos:// | 腾讯云对象存储 |
| 华为云 OBS | obs:// | 华为云对象存储 |
| 百度云 BOS | bos:// | 百度云对象存储 |

---

## AWS S3 配置

### 环境变量

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

### 代码配置

```python
from memoryx.core.config import Config

config = Config(
    remote_backup_enabled=True,
    remote_backup_path="s3://your-bucket/memoryx-backup"
)
```

---

## Google Cloud Storage 配置

### 环境变量

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GCS_PROJECT=your-project-id
```

### 代码配置

```python
config = Config(
    remote_backup_path="gs://your-bucket/memoryx-backup"
)
```

---

## 阿里云 OSS 配置

### 环境变量

```bash
export ALIYUN_ACCESS_KEY_ID=your_access_key
export ALIYUN_ACCESS_KEY_SECRET=your_secret_key
```

### 代码配置

```python
config = Config(
    remote_backup_path="oss://your-bucket/memoryx-backup"
)
```

---

## 腾讯云 COS 配置

### 环境变量

```bash
export TENCENT_SECRET_ID=your_secret_id
export TENCENT_SECRET_KEY=your_secret_key
export TENCENT_REGION=ap-guangzhou
```

### 代码配置

```python
config = Config(
    remote_backup_path="cos://your-bucket"
)
```

---

## 华为云 OBS 配置

### 环境变量

```bash
export HUAWEI_ACCESS_KEY_ID=your_access_key
export HUAWEI_ACCESS_KEY_SECRET=your_secret_key
export HUAWEI_REGION=cn-north-4
```

### 代码配置

```python
config = Config(
    remote_backup_path="obs://your-bucket/memoryx"
)
```

---

## 百度云 BOS 配置

### 环境变量

```bash
export BAIDU_ACCESS_KEY_ID=your_access_key
export BAIDU_ACCESS_KEY_SECRET=your_secret_key
```

### 代码配置

```python
config = Config(
    remote_backup_path="bos://your-bucket/memoryx"
)
```

---

## 使用示例

### 基本使用

```python
from memoryx import MemoryX

memory = MemoryX()

# 同步到云端
memory.backup(remote=True)

# 或手动同步
from memoryx.cloud import CloudSync

cloud = CloudSync(config)
cloud.sync_to_cloud()
```

### 检查状态

```python
cloud = CloudSync(config)
status = cloud.get_status()

for key, info in status['providers'].items():
    print(f"{info['name']}: {'✓' if info['connected'] else '✗'}")
```

---

## 自动同步

### 配置自动备份

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

### 权限问题

确保云账号有以下权限：

**AWS S3**
- s3:PutObject
- s3:GetObject
- s3:ListBucket

**阿里云 OSS**
- oss:PutObject
- oss:GetObject
- oss:ListBucket

**腾讯云 COS**
- cos:PutObject
- cos:GetObject
- cos:ListBucket
