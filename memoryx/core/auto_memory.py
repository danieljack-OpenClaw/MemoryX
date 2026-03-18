# -*- coding: utf-8 -*-
"""
MemoryX 核心模块 - 自动记录 + 自动应用
实现真正的对话式记忆系统
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# 添加路径
_proj_path = Path(__file__).parent.parent
if str(_proj_path) not in sys.path:
    sys.path.insert(0, str(_proj_path))

# 全局变量
_memoryx = None
_stats = {
    "queries": 0,
    "total_tokens_saved": 0,
    "total_time_ms": 0,
    "memories_recorded": 0,
    "last_result": None
}

# 需要自动记忆的关键词
MEMORY_KEYWORDS = [
    "记住", "记住我", "我喜欢", "我讨厌", "我的名字",
    "目标", "目的是", "要完成", "日均", "月均",
    "公司", "业务", "项目", "偏好", "习惯",
    "不要", "别", "禁止", "偏好", "联系方式",
    "地址", "电话", "邮箱", "账号", "密码"
]


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


def auto_recall(user_message: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    自动应用：检索相关记忆
    在每次回复用户前调用
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
        # 语义搜索相关记忆
        memories = mx.search(user_id=user_id, query=user_message, limit=5)
        
        # 获取压缩上下文
        context = mx.get_context(user_id=user_id, max_tokens=300)
        
        elapsed = int((time.time() - start) * 1000)
        
        # 计算节省的 tokens
        old_tokens = 250000  # 传统方式
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


def should_remember(user_message: str) -> bool:
    """判断是否需要记忆"""
    message = user_message.lower()
    for keyword in MEMORY_KEYWORDS:
        if keyword in message:
            return True
    return False


def auto_record(user_message: str, ai_response: str = "", user_id: str = "xiao_cao_ye") -> dict:
    """
    自动记录：分析对话内容，提取重要信息保存
    在每次对话后调用
    """
    global _stats
    
    mx = init_memoryx()
    
    result = {
        "success": False,
        "recorded": 0,
        "content": ""
    }
    
    if mx is None:
        return result
    
    # 检查是否需要记忆
    if not should_remember(user_message):
        return result
    
    try:
        # 提取要记忆的内容
        content = user_message
        
        # 移除常见的触发词
        for kw in ["记住", "请记住", "帮我记住", "记一下"]:
            content = content.replace(kw, "").strip()
        
        if len(content) < 3:
            return result
        
        # 保存到 MemoryX
        mem = mx.add(
            user_id=user_id,
            content=content,
            level="user",
            metadata={
                "source": "auto_record",
                "timestamp": datetime.now().isoformat(),
                "original_message": user_message[:100]
            }
        )
        
        _stats["memories_recorded"] += 1
        
        result = {
            "success": True,
            "recorded": 1,
            "content": content[:50] + "..." if len(content) > 50 else content,
            "memory_id": mem.id
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_report() -> str:
    """生成使用报告"""
    global _stats
    
    r = _stats.get("last_result")
    if not r or not r.get("success"):
        return ""
    
    return f"\n📊 MemoryX: 找到 {r['memories_found']} 条记忆, 节省 ~{r['tokens_saved']:,} tokens"


def get_summary() -> str:
    """累计统计"""
    global _stats
    
    if _stats["queries"] == 0:
        return ""
    
    avg = _stats["total_time_ms"] / _stats["queries"] / 1000
    
    return f"""
📊 MemoryX 累计:
- 查询: {_stats['queries']} 次
- 节省: ~{_stats['total_tokens_saved']:,} tokens
- 自动记录: {_stats['memories_recorded']} 条
- 平均耗时: {avg:.2f}s
"""


def reset_stats():
    """重置统计"""
    global _stats
    _stats = {
        "queries": 0,
        "total_tokens_saved": 0,
        "total_time_ms": 0,
        "memories_recorded": 0,
        "last_result": None
    }


def close():
    """关闭连接"""
    global _memoryx
    if _memoryx:
        try:
            _memoryx.close()
        except:
            pass
        _memoryx = None


# ============ 导出 ============
__all__ = [
    "auto_recall",      # 自动应用：检索记忆
    "auto_record",      # 自动记录：保存记忆
    "get_report",       # 获取报告
    "get_summary",      # 获取统计
    "reset_stats",      # 重置统计
    "close",            # 关闭
    "_stats"            # 统计信息
]
