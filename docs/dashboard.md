# MemoryX Web Dashboard 指南

## 概述

MemoryX 提供可视化的 Web 管理界面，方便管理记忆、搜索、备份等操作。

## 快速开始

### 启动 Dashboard

```bash
# 默认端口 8080
python -m memoryx.dashboard

# 自定义端口
python -m memoryx.dashboard --port 9000
```

### 访问

打开浏览器访问：http://localhost:8080

---

## 功能介绍

### 1. 仪表盘 (首页)

- 总记忆数量
- 存储大小
- 向量维度
- 用户数量

### 2. 记忆管理

- 查看所有记忆
- 按用户ID筛选
- 删除记忆

### 3. 添加记忆

- 输入用户ID
- 输入记忆内容
- 选择记忆层级 (user/session/project/agent/skill)

### 4. 语义搜索

- 输入查询内容
- 指定用户ID
- 查看相似记忆

### 5. 备份管理

- 创建本地备份
- 同步到云端
- 查看备份列表

### 6. 设置

- 存储路径
- 最大Token数
- 自动备份开关

---

## REST API

Dashboard 内置 REST API，可独立使用：

```bash
# 启动 API 服务
python -m memoryx.api.server --port 8000
```

### API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /api/stats | 获取统计 |
| GET | /api/memory | 列出记忆 |
| POST | /api/memory | 添加记忆 |
| POST | /api/memory/search | 搜索 |
| DELETE | /api/memory/{id} | 删除 |
| POST | /api/backup | 创建备份 |
| GET | /api/backup | 列出备份 |

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
