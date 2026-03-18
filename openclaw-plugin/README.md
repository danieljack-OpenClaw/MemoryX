# MemoryX OpenClaw Plugin

## 安装

在 OpenClaw 工作空间创建 skills 目录：

```bash
mkdir -p ~/.openclaw/skills/memoryx
```

## 配置

### 1. 复制插件文件

将 `openclaw/` 目录复制到 skills：

```bash
cp -r openclaw/* ~/.openclaw/skills/memoryx/
```

### 2. 安装依赖

```bash
pip install memoryx sentence-transformers chromadb
```

### 3. 配置 OpenClaw

在 `~/.openclaw/skills/memoryx/SKILL.md` 中配置：

```markdown
# MemoryX Skill

提供长期记忆存储和检索功能。

## 触发词
- 记住
- 记忆
- 保存到记忆
- 从记忆获取

## 配置
@config
{
  "storage_path": "~/.memoryx",
  "max_context_tokens": 4000,
  "auto_backup": true
}
```

## 使用

在对话中直接使用：

```
用户: 记住我的密码是 123456
AI: 已记住！

用户: 我的密码是什么?
AI: 你的密码是 123456

用户: 给我最近的上下文
AI: (返回压缩后的记忆)
```

## 功能

- 添加记忆
- 语义搜索
- 上下文压缩
- 自动备份

## API

可通过 OpenClaw 工具调用：

```python
# 添加记忆
@memoryx.add(user_id="user1", content="内容", level="user")

# 搜索
@memoryx.search(user_id="user1", query="关键词")

# 获取上下文
@memoryx.context(user_id="user1", max_tokens=1000)
```
