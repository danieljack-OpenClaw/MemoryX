# MemoryX Web Dashboard 指南

## 概述

MemoryX 提供可视化的 Web 管理界面，支持本地+云端双存储配置，6种语言。

## 快速开始

### 启动 Dashboard

```bash
# 默认端口 19876
python -m memoryx.dashboard

# 自定义端口
python -m memoryx.dashboard --port 9000
```

### 访问

打开浏览器访问：http://localhost:19876

---

## 功能介绍

### 1. 仪表盘 (首页)

- 总记忆数量
- 存储大小
- 向量维度

### 2. 记忆管理

- 查看所有记忆
- 按用户ID筛选
- 删除记忆

### 3. 添加记忆

- 输入用户ID
- 输入记忆内容
- 选择记忆层级

### 4. 语义搜索

- 输入查询内容
- 指定用户ID
- 查看相似记忆

### 5. 备份同步

- 创建本地备份
- 同步到云端

### 6. 设置 (云端存储配置)

- 启用/禁用云端存储
- 选择云厂商 (阿里云/腾讯云/华为云/百度云/AWS/GCS)
- 配置 Access Key、Secret Key、Bucket、Region
- 测试连接

### 7. 反馈

- 提交希望支持的云厂商

---

## 多语言

Dashboard 支持 6 种语言：简体中文、繁体中文、English、Español、Português、Deutsch

---

## REST API

Dashboard 内置 REST API，可独立使用：

```bash
# 启动 API 服务 (端口 19877)
python -m memoryx.api.server
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
| POST | /api/cloud/sync | 云端同步 |
| GET | /api/settings | 获取设置 |
| POST | /api/settings/cloud | 保存云配置 |
| POST | /api/settings/cloud/test | 测试连接 |

---

## 示例

### 使用 curl

```bash
# 添加记忆
curl -X POST http://localhost:8080/api/memory \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "content": "测试", "level": "user"}'

# 搜索
curl -X POST http://localhost:8080/api/memory/search \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001", "query": "测试", "limit": 5}'
```
