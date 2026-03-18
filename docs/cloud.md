# MemoryX 云端同步

## 本地 + 云端双存储模式

MemoryX 支持**同时使用本地存储和云端存储**：

- **默认**：本地存储 (`~/.memoryx/`)
- **配置云端后**：自动同时保存到本地和云端

### 工作原理

```
用户添加记忆
    ↓
同时写入:
  ├─ 本地 SQLite (~/.memoryx/memoryx.db)
  └─ 云端存储 (如果已配置)
```

### 配置文件

配置保存在 `~/.memoryx/settings.json`:

```json
{
  "cloud_enabled": true,
  "cloud_provider": "aliyun",
  "cloud_region": "cn-hangzhou",
  "cloud_bucket": "my-memoryx"
}
```

---

## 支持的云服务

| 服务 | 前缀 | 说明 |
|------|------|------|
| AWS S3 | s3:// | Amazon Simple Storage Service |
| Google Cloud Storage | gs:// | Google Cloud Storage |
| 阿里云 OSS | oss:// | 阿里云对象存储 |
| 腾讯云 COS | cos:// | 腾讯云对象存储 |
| 华为云 OBS | obs:// | 华为云对象存储 |
| 百度云 BOS | bos:// | 百度云对象存储 |

---

## 快速配置 (Web Dashboard)

1. 访问 Dashboard (默认 http://localhost:19876)
2. 进入「设置」标签
3. 启用「云端存储」开关
4. 选择云厂商
5. 填写 Access Key、Secret Key、Bucket
6. 点击「测试连接」
7. 点击「保存」

---

## 环境变量配置

### 阿里云 OSS

```bash
export ALIYUN_ACCESS_KEY_ID=your_key
export ALIYUN_ACCESS_KEY_SECRET=your_secret
```

### 腾讯云 COS

```bash
export TENCENT_SECRET_ID=your_id
export TENCENT_SECRET_KEY=your_secret
```

### AWS S3

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

---

## 使用示例

### 添加记忆 (自动双写)

```python
from memoryx import MemoryX

memory = MemoryX()  # 自动同时保存到本地+云端

memory.add(
    user_id="user1",
    content="我喜欢蓝色",
    level="user"
)
```

### 手动同步

```python
from memoryx.core.storage import StorageManager
from memoryx.core.config import Config

storage = StorageManager(Config())
storage.sync_all_to_cloud()
```

---

## 检查状态

```python
from memoryx.cloud import CloudSync
from memoryx.core.config import Config

cloud = CloudSync(Config())
status = cloud.get_status()
print(status)
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
