# -*- coding: utf-8 -*-
"""
MemoryX OpenClaw Integration
提供 OpenClaw 工具接口
"""
import os
import sys
from typing import Dict, List, Any

from ..core.config import Config
from ..core.memory import MemoryX as MemoryXCore
from ..core.models import MemoryLevel


class MemoryX:
    """MemoryX OpenClaw Tool"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._init()
    
    def _init(self):
        """初始化"""
        storage_path = self.config.get("storage_path", "~/.memoryx")
        if storage_path.startswith("~"):
            storage_path = os.path.expanduser(storage_path)
        
        from ..core.config import Config
        cfg = Config(storage_path=storage_path)
        cfg.max_context_tokens = self.config.get("max_context_tokens", 4000)
        
        self.memory = MemoryXCore(cfg)
    
    def add(self, user_id: str, content: str, level: str = "user") -> Dict:
        """添加记忆"""
        level_map = {
            "user": MemoryLevel.USER,
            "session": MemoryLevel.SESSION,
            "project": MemoryLevel.PROJECT,
            "agent": MemoryLevel.AGENT,
            "skill": MemoryLevel.SKILL
        }
        
        mem = self.memory.add(
            user_id=user_id,
            content=content,
            level=level_map.get(level, MemoryLevel.USER)
        )
        
        return {
            "success": True,
            "id": mem.id,
            "content": content
        }
    
    def search(self, user_id: str, query: str, limit: int = 5) -> Dict:
        """搜索记忆"""
        results = self.memory.search(
            user_id=user_id,
            query=query,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    
    def context(self, user_id: str, max_tokens: int = 1000) -> Dict:
        """获取压缩上下文"""
        ctx = self.memory.get_context(
            user_id=user_id,
            max_tokens=max_tokens
        )
        
        return {
            "success": True,
            "context": ctx,
            "tokens": max_tokens
        }
    
    def delete(self, memory_id: str) -> Dict:
        """删除记忆"""
        success = self.memory.delete(memory_id)
        return {"success": success}
    
    def backup(self) -> Dict:
        """创建备份"""
        backup_id = self.memory.backup()
        return {"success": True, "backup_id": backup_id}
    
    def stats(self, user_id: str = None) -> Dict:
        """获取统计"""
        stats = self.memory.get_stats(user_id)
        return {"success": True, **stats}
    
    def close(self):
        """关闭连接"""
        self.memory.close()


# 全局实例
_memoryx = None


def get_memoryx(config: Dict = None) -> MemoryX:
    """获取 MemoryX 实例"""
    global _memoryx
    if _memoryx is None:
        _memoryx = MemoryX(config)
    return _memoryx


# OpenClaw 工具函数
def remember(user_id: str, content: str, level: str = "user") -> str:
    """记住内容"""
    mx = get_memoryx()
    result = mx.add(user_id, content, level)
    return f"✓ 已记住: {content[:50]}..." if result["success"] else "✗ 失败"


def recall(user_id: str, query: str) -> str:
    """回忆内容"""
    mx = get_memoryx()
    result = mx.search(user_id, query)
    
    if result["count"] == 0:
        return "未找到相关记忆"
    
    lines = [f"找到 {result['count']} 条记忆:"]
    for r in result["results"][:3]:
        lines.append(f"- {r.get('content', '')[:50]}...")
    
    return "\n".join(lines)


def context(user_id: str, max_tokens: int = 500) -> str:
    """获取上下文"""
    mx = get_memoryx()
    result = mx.context(user_id, max_tokens)
    return result["context"] or "无记忆"


# 导出
__all__ = ["MemoryX", "get_memoryx", "remember", "recall", "context"]
