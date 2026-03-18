# MemoryX - OpenClaw Plugin

## 快速安装

```bash
# 1. 安装 MemoryX
pip install memoryx

# 2. 复制插件
mkdir -p ~/.openclaw/skills/memoryx
cp -r openclaw/* ~/.openclaw/skills/memoryx/

# 3. 重启 OpenClaw
openclaw restart
```

## 使用方法

### 基本命令

```
记住 [内容]     - 保存到记忆
搜索 [关键词]   - 语义搜索
记忆            - 获取上下文
```

### 示例

```
用户: 记住我喜欢蓝色
AI: ✓ 已记住

用户: 搜索颜色偏好
AI: 找到 3 条相关记忆...

用户: 获取记忆上下文
AI: [压缩后的记忆上下文]
```

## 配置

编辑 `~/.openclaw/skills/memoryx/config.json`:

```json
{
  "enabled": true,
  "storage_path": "~/.memoryx",
  "max_context_tokens": 4000,
  "auto_backup": true,
  "default_level": "user"
}
```

## 卸载

```bash
rm -rf ~/.openclaw/skills/memoryx
openclaw restart
```
