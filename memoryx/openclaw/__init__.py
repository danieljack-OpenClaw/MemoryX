# -*- coding: utf-8 -*-
"""
MemoryX OpenClaw 工具集成
提供对话式记忆检索功能
"""
from .integration import (
    MEMORYX_AVAILABLE,
    search_memory,
    get_context,
    add_memory
)


def remember(content: str, user_id: str = "xiao_cao_ye") -> str:
    """记住内容"""
    if not MEMORYX_AVAILABLE:
        return "❌ MemoryX 未安装"
    
    result = add_memory(
        content=content,
        user_id=user_id,
        level="user"
    )
    
    if result:
        return f"✅ 已记住: {content[:50]}..."
    return "❌ 记忆失败"


def recall(query: str, user_id: str = "xiao_cao_ye") -> str:
    """回忆相关内容"""
    if not MEMORYX_AVAILABLE:
        return "❌ MemoryX 未安装"
    
    results = search_memory(query=query, user_id=user_id, limit=3)
    
    if not results:
        return "🔍 未找到相关记忆"
    
    lines = [f"找到 {len(results)} 条相关记忆:\n"]
    for i, r in enumerate(results, 1):
        score = r.get('score', 0)
        content = r.get('content', '')[:100]
        lines.append(f"{i}. [{score:.2f}] {content}...")
    
    return "\n".join(lines)


def context(user_id: str = "xiao_cao_ye", max_tokens: int = 300) -> str:
    """获取记忆上下文"""
    if not MEMORYX_AVAILABLE:
        return "❌ MemoryX 未安装"
    
    ctx = get_context(user_id=user_id, max_tokens=max_tokens)
    
    if not ctx:
        return "📝 无记忆"
    
    return f"📝 记忆上下文 ({len(ctx)} 字符):\n\n{ctx}"


def status() -> str:
    """MemoryX 状态"""
    if not MEMORYX_AVAILABLE:
        return "❌ MemoryX 未安装"
    
    return "✅ MemoryX 已就绪"


# 导出工具函数
TOOLS = {
    "remember": remember,
    "recall": recall,
    "context": context,
    "status": status
}


__all__ = ["TOOLS", "remember", "recall", "context", "status", "MEMORYX_AVAILABLE"]
