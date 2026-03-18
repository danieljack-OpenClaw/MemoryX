# -*- coding: utf-8 -*-
"""
MemoryX 快速集成模块
在每次回复时自动调用，低延迟
"""
import sys
import time
import json
from pathlib import Path

# 添加路径
_proj_path = Path(__file__).parent.parent
if str(_proj_path) not in sys.path:
    sys.path.insert(0, str(_proj_path))

# 全局单例
_memoryx = None
_stats = {"queries": 0, "total_tokens_saved": 0, "last_context": ""}
_cache = {"last_result": None, "last_query": ""}


def _get_memoryx():
    """获取 MemoryX 单例"""
    global _memoryx
    if _memoryx is None:
        try:
            from memoryx import MemoryX
            _memoryx = MemoryX()
        except:
            return None
    return _memoryx


def quick_recall(query: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    快速检索 - 专为每次回复设计
    优化延迟，首次加载后使用缓存
    """
    global _stats, _cache
    
    # 缓存检查 - 相同查询直接返回
    if query == _cache.get("last_query"):
        return _cache.get("last_result", {"success": False})
    
    start = time.time()
    mx = _get_memoryx()
    
    if mx is None:
        return {"success": False, "error": "MemoryX unavailable"}
    
    try:
        # 语义搜索
        results = mx.search(user_id=user_id, query=query, limit=3)
        
        # 获取压缩上下文
        context = mx.get_context(user_id=user_id, max_tokens=150)
        
        # 计算节省
        elapsed = int((time.time() - start) * 1000)
        old_tokens = 250000
        new_tokens = len(context) // 4 if context else 0
        tokens_saved = max(0, old_tokens - new_tokens)
        
        # 更新统计
        _stats["queries"] += 1
        _stats["total_tokens_saved"] += tokens_saved
        _stats["last_context"] = context or ""
        
        # 更新缓存
        result = {
            "success": True,
            "results": results,
            "context": context,
            "time_ms": elapsed,
            "tokens_saved": tokens_saved,
            "memories_found": len(results)
        }
        _cache["last_result"] = result
        _cache["last_query"] = query
        
        # 异步记录统计（不阻塞）
        try:
            from memoryx.stats import record_query
            record_query(tokens_saved=tokens_saved, memories_found=len(results))
        except:
            pass
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def quick_record(message: str, user_id: str = "xiao_cao_ye") -> dict:
    """快速记录 - 检测关键词"""
    keywords = ["记住", "请记住", "帮我记住", "我喜欢", "我讨厌", "我的名字", 
                "目标", "日均", "月均", "公司", "密码", "地址", "电话"]
    
    msg_lower = message.lower()
    if not any(kw in msg_lower for kw in keywords):
        return {"success": False, "recorded": 0}
    
    mx = _get_memoryx()
    if mx is None:
        return {"success": False, "error": "MemoryX unavailable"}
    
    try:
        # 清理触发词
        content = message
        for kw in ["记住", "请记住", "帮我记住", "记一下"]:
            content = content.replace(kw, "").strip()
        
        if len(content) < 3:
            return {"success": False}
        
        from memoryx.core.models import MemoryLevel
        mem = mx.add(user_id=user_id, content=content, level=MemoryLevel.USER)
        
        try:
            from memoryx.stats import record_add_memory
            record_add_memory()
        except:
            pass
        
        return {"success": True, "recorded": 1, "memory_id": mem.id}
        
    except:
        return {"success": False}


def process(query: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    处理用户消息：检索 + 记录
    在每次回复时调用
    """
    recall_result = quick_recall(query, user_id)
    record_result = quick_record(query, user_id)
    
    return {
        "recall": recall_result,
        "record": record_result,
        "context": recall_result.get("context", "") if recall_result.get("success") else ""
    }


def get_report() -> str:
    """生成简短报告"""
    r = _cache.get("last_result")
    if not r or not r.get("success"):
        return ""
    
    return f"[MemoryX: {r.get('memories_found', 0)} 条记忆, 节省 ~{r.get('tokens_saved', 0):,} tokens]"


def get_stats() -> dict:
    """获取统计"""
    return _stats.copy()


__all__ = ["quick_recall", "quick_record", "process", "get_report", "get_stats"]
