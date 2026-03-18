# -*- coding: utf-8 -*-
"""
MemoryX OpenClaw Integration - 自动记忆检索
"""
import os
from pathlib import Path

# 尝试导入 MemoryX
try:
    import sys
    proj_path = Path(__file__).parent.parent / "projects" / "MemoryX"
    if str(proj_path) not in sys.path:
        sys.path.insert(0, str(proj_path))
    
    from memoryx import MemoryX
    from memoryx.core.config import Config
    
    _memoryx = None
    
    def get_memoryx():
        """获取 MemoryX 实例"""
        global _memoryx
        if _memoryx is None:
            try:
                _memoryx = MemoryX()
            except:
                return None
        return _memoryx
    
    def search_memory(query: str, user_id: str = "xiao_cao_ye", limit: int = 3):
        """搜索记忆"""
        mx = get_memoryx()
        if mx is None:
            return []
        try:
            results = mx.search(user_id=user_id, query=query, limit=limit)
            return results
        except:
            return []
    
    def get_context(user_id: str = "xiao_cao_ye", max_tokens: int = 500):
        """获取压缩上下文"""
        mx = get_memoryx()
        if mx is None:
            return ""
        try:
            return mx.get_context(user_id=user_id, max_tokens=max_tokens)
        except:
            return ""
    
    def add_memory(content: str, user_id: str = "xiao_cao_ye", level: str = "user", metadata: dict = None):
        """添加记忆"""
        mx = get_memoryx()
        if mx is None:
            return None
        try:
            return mx.add(user_id=user_id, content=content, level=level, metadata=metadata)
        except:
            return None

    MEMORYX_AVAILABLE = True
    
except ImportError:
    MEMORYX_AVAILABLE = False
    get_memoryx = None
    search_memory = None
    get_context = None
    add_memory = None


# 导出
__all__ = [
    "MEMORYX_AVAILABLE",
    "get_memoryx", 
    "search_memory",
    "get_context",
    "add_memory"
]
