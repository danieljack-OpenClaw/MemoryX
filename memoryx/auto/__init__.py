# -*- coding: utf-8 -*-
"""
MemoryX 自动检索工具 - 集成到对话流程
"""
import sys
import time
from pathlib import Path

# 添加路径
_proj = Path(__file__).parent.parent / "projects" / "MemoryX"
if str(_proj) not in sys.path:
    sys.path.insert(0, str(_proj))

# 全局实例
_memoryx = None
_stats = {"queries": 0, "total_time_ms": 0, "total_tokens_saved": 0, "last_result": None}


def init_memoryx():
    """初始化 MemoryX"""
    global _memoryx
    if _memoryx is None:
        try:
            from memoryx import MemoryX
            _memoryx = MemoryX()
        except:
            pass
    return _memoryx


def search_and_inject(user_message: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    核心函数：自动检索记忆并返回结果
    在每次回复用户时被调用
    """
    global _stats
    
    start = time.time()
    mx = init_memoryx()
    
    result = {
        "success": False,
        "memories": [],
        "context": "",
        "time_ms": 0,
        "tokens_saved": 0
    }
    
    if mx is None:
        return result
    
    try:
        # 1. 语义搜索
        memories = mx.search(user_id=user_id, query=user_message, limit=3)
        
        # 2. 获取压缩上下文
        context = mx.get_context(user_id=user_id, max_tokens=200)
        
        # 3. 计算统计
        elapsed = int((time.time() - start) * 1000)
        
        # 传统方式约 250k tokens
        old_tokens = 250000
        new_tokens = len(context) // 4 if context else 0
        tokens_saved = max(0, old_tokens - new_tokens)
        
        # 更新统计
        _stats["queries"] += 1
        _stats["total_time_ms"] += elapsed
        _stats["total_tokens_saved"] += tokens_saved
        
        result = {
            "success": True,
            "memories": memories,
            "context": context,
            "time_ms": elapsed,
            "tokens_saved": tokens_saved,
            "memories_found": len(memories)
        }
        
        _stats["last_result"] = result
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_report() -> str:
    """生成使用报告"""
    global _stats
    
    r = _stats.get("last_result")
    if not r or not r.get("success"):
        return ""
    
    return f"""
📊 MemoryX: 找到 {r['memories_found']} 条记忆, 节省 ~{r['tokens_saved']:,} tokens, {r['time_ms']/1000:.2f}s
"""


def get_summary() -> str:
    """累计统计"""
    global _stats
    
    if _stats["queries"] == 0:
        return ""
    
    avg = _stats["total_time_ms"] / _stats["queries"] / 1000
    
    return f"""
📊 MemoryX 累计: {_stats['queries']} 次查询, 节省 ~{_stats['total_tokens_saved']:,} tokens, 平均 {avg:.2f}s
"""


def close():
    """关闭连接"""
    global _memoryx
    if _memoryx:
        try:
            _memoryx.close()
        except:
            pass
        _memoryx = None


__all__ = [
    "search_and_inject",
    "get_report",
    "get_summary",
    "init_memoryx",
    "close",
    "_stats"
]
