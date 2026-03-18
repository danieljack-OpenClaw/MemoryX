# MemoryX OpenClaw Plugin

## 功能完整

作为 OpenClaw 插件使用时，**拥有与独立部署完全相同的功能**：

| 功能 | 独立部署 | OpenClaw 插件 |
|------|---------|--------------|
| 添加记忆 | ✅ | ✅ |
| 语义搜索 | ✅ | ✅ |
| Token 压缩 | ✅ | ✅ |
| 多层级记忆 | ✅ | ✅ |
| **Web Dashboard** | ✅ | ✅ |
| 多语言界面 | ✅ | ✅ |
| 本地存储 | ✅ | ✅ |
| 云端存储配置 | ✅ | ✅ |
| 自动备份 | ✅ | ✅ |

## 快速安装

```bash
# 1. 复制插件
mkdir -p ~/.openclaw/skills/memoryx
cp -r openclaw-plugin/* ~/.openclaw/skills/memoryx/

# 2. 安装依赖
pip install memoryx

# 3. 重启 OpenClaw
openclaw restart
```

## 使用方法

### 对话中使用

```
记住我喜欢蓝色
搜索颜色偏好
获取记忆上下文
```

### 打开 Web Dashboard

**方式一**：在对话中说「打开 Dashboard」或「打开 MemoryX」

**方式二**：直接访问
- 默认地址：`http://localhost:19876`
- 可在 skill.json 中配置端口

## Web Dashboard 功能

访问 Dashboard 后可使用：

1. **记忆管理** - 查看、搜索、删除记忆
2. **添加记忆** - 手动添加新记忆
3. **语义搜索** - 搜索相关内容
4. **备份同步** - 本地备份、云端同步
5. **云端配置** - 配置阿里云/腾讯云/AWS 等
6. **设置** - 修改配置

### 多语言支持

Dashboard 支持 6 种语言：
- 简体中文 (默认)
- 繁体中文
- English
- Español
- Português
- Deutsch

## 配置

编辑 `~/.openclaw/skills/memoryx/skill.json`:

```json
{
  "config": {
    "storage_path": "~/.memoryx",
    "max_context_tokens": 4000,
    "dashboard_enabled": true,
    "dashboard_port": 19876,
    "auto_backup": true
  }
}
```

## 云端存储配置

在 Dashboard 中配置云端存储：

1. 访问 Dashboard → 设置
2. 启用「云端存储」开关
3. 选择云厂商（阿里云/腾讯云/华为云/百度云/AWS/GCS）
4. 填写 Access Key、Secret Key、Bucket
5. 测试连接 → 保存

配置后，添加记忆会自动同时保存到本地和云端。

## 卸载

```bash
rm -rf ~/.openclaw/skills/memoryx
openclaw restart
```
