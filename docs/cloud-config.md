# MemoryX 配置文件

## 云端存储配置

### 配置文件位置

云端存储配置保存在: `~/.memoryx/settings.json`

### 配置示例

```json
{
  "cloud_enabled": true,
  "cloud_provider": "aliyun",
  "cloud_region": "cn-hangzhou",
  "cloud_bucket": "my-memoryx-bucket"
}
```

### 支持的云厂商

| 厂商 | provider 值 | 示例区域 |
|------|-------------|---------|
| 阿里云 OSS | aliyun | cn-hangzhou, cn-shanghai |
| 腾讯云 COS | tencent | ap-shanghai, ap-guangzhou |
| 华为云 OBS | huawei | cn-north-4 |
| 百度云 BOS | baidu | bj |
| AWS S3 | aws | us-east-1 |
| Google Cloud | gcs | us-central1 |

### 环境变量方式

```bash
# 阿里云
export ALIYUN_ACCESS_KEY_ID=your-key
export ALIYUN_ACCESS_KEY_SECRET=your-secret

# 腾讯云
export TENCENT_SECRET_ID=your-key
export TENCENT_SECRET_KEY=your-secret

# AWS
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Web Dashboard 配置

访问 Dashboard 设置页面 (Settings) 可以可视化配置云端存储:

1. 进入「设置」标签
2. 启用「云端存储」开关
3. 选择云厂商
4. 填写 Access Key、Secret Key、Bucket 等信息
5. 点击「测试连接」验证
6. 点击「保存」

保存后，MemoryX 将同时支持本地存储和云端存储。
