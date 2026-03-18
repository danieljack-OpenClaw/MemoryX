# -*- coding: utf-8 -*-
"""
MemoryX OpenClaw 集成模块
实现真正的每次对话自动集成
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# 添加路径
_proj_path = Path(__file__).parent.parent.parent
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

# 关键词触发记忆
MEMORY_KEYWORDS = [
    "记住", "请记住", "帮我记住", "记一下", "别忘了",
    "我喜欢", "我讨厌", "我的名字", "我叫",
    "目标", "目的是", "要完成", "日均", "月均",
    "公司", "业务", "项目", "偏好", "习惯",
    "不要", "别", "禁止", "联系方式",
    "地址", "电话", "邮箱", "账号", "密码"
]


def get_memoryx():
    """获取 MemoryX 实例（单例）"""
    global _memoryx
    if _memoryx is None:
        from memoryx import MemoryX
        _memoryx = MemoryX()
    return _memoryx


def auto_recall(user_message: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    自动检索相关记忆
    每次回复前调用
    """
    global _stats
    
    start_time = time.time()
    
    try:
        mx = get_memoryx()
        if mx is None:
            return {"success": False, "error": "MemoryX not available"}
        
        # 1. 语义搜索相关记忆
        results = mx.search(user_id=user_id, query=user_message, limit=5)
        
        # 2. 获取压缩上下文
        context = mx.get_context(user_id=user_id, max_tokens=200)
        
        # 3. 计算节省
        elapsed_ms = int((time.time() - start_time) * 1000)
        old_tokens = 250000  # 传统上下文约 250k tokens
        new_tokens = len(context) // 4 if context else 0
        tokens_saved = max(0, old_tokens - new_tokens)
        
        # 4. 更新统计
        _stats["queries"] += 1
        _stats["total_time_ms"] += elapsed_ms
        _stats["total_tokens_saved"] += tokens_saved
        
        result = {
            "success": True,
            "results": results,
            "context": context,
            "time_ms": elapsed_ms,
            "tokens_saved": tokens_saved,
            "memories_found": len(results)
        }
        
        _stats["last_result"] = result
        
        # 5. 记录统计
        try:
            from memoryx.stats import record_query
            record_query(tokens_saved=tokens_saved, memories_found=len(results))
        except:
            pass
        
        return result
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def should_remember(message: str) -> bool:
    """判断是否需要记忆"""
    msg_lower = message.lower()
    for keyword in MEMORY_KEYWORDS:
        if keyword in msg_lower:
            return True
    return False


def auto_record(user_message: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    自动记录重要信息
    对话后调用
    """
    global _stats
    
    if not should_remember(user_message):
        return {"success": False, "recorded": 0, "reason": "not relevant"}
    
    try:
        mx = get_memoryx()
        if mx is None:
            return {"success": False, "error": "MemoryX not available"}
        
        # 清理触发词
        content = user_message
        for kw in ["记住", "请记住", "帮我记住", "记一下"]:
            content = content.replace(kw, "").strip()
        
        if len(content) < 3:
            return {"success": False, "recorded": 0, "reason": "content too short"}
        
        # 保存记忆
        from memoryx.core.models import MemoryLevel
        mem = mx.add(
            user_id=user_id,
            content=content,
            level=MemoryLevel.USER,
            metadata={
                "source": "auto_record",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        _stats["memories_recorded"] += 1
        
        # 记录统计
        try:
            from memoryx.stats import record_add_memory
            record_add_memory()
        except:
            pass
        
        return {
            "success": True,
            "recorded": 1,
            "memory_id": mem.id,
            "content_preview": content[:50]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_report(last_input_tokens: int = 0, last_output_tokens: int = 0) -> str:
    """
    生成 MemoryX 使用报告
    """
    global _stats
    
    r = _stats.get("last_result")
    if not r or not r.get("success"):
        return ""
    
    # 计算节省
    if last_input_tokens > 0:
        input_saved = max(0, 250000 - last_input_tokens)
    else:
        input_saved = r.get("tokens_saved", 0)
    
    output_saved = 0
    total_saved = input_saved + output_saved
    
    reason = "语义搜索直接返回结果，无需读取大量历史消息"
    
    return f"""
📊 MemoryX 报告:
- 找到记忆: {r.get('memories_found', 0)} 条
- 输入Token: {last_input_tokens:,} (传统约250,000)
- 节省输入: ~{input_saved:,} tokens ({input_saved*100/250000:.1f}%)
- 耗时: {r.get('time_ms', 0)/1000:.2f}s
- 节省原因: {reason}
"""


def get_summary() -> str:
    """累计统计"""
    global _stats
    
    if _stats["queries"] == 0:
        return ""
    
    avg_time = _stats["total_time_ms"] / _stats["queries"] / 1000
    
    return f"""
📊 MemoryX 累计:
- 查询次数: {_stats['queries']}
- 总节省Token: ~{_stats['total_tokens_saved']:,}
- 自动记录: {_stats['memories_recorded']} 条
- 平均耗时: {avg_time:.2f}s
"""


def get_stats() -> dict:
    """获取当前统计"""
    return {
        "queries": _stats["queries"],
        "total_tokens_saved": _stats["total_tokens_saved"],
        "memories_recorded": _stats["memories_recorded"],
        "last_result": _stats.get("last_result")
    }


def process_message(user_message: str, user_id: str = "xiao_cao_ye") -> dict:
    """
    处理消息：自动检索 + 自动记录
    在每次对话时调用
    """
    # 1. 自动检索
    recall_result = auto_recall(user_message, user_id)
    
    # 2. 自动记录
    record_result = auto_record(user_message, user_id)
    
    # 3. 生成报告
    report = get_report()
    
    return {
        "recall": recall_result,
        "record": record_result,
        "report": report
    }


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


# ============ MCP Server 支持 ============

class MCPServer:
    """MemoryX MCP 服务器 - 支持 OpenClaw 工具调用"""
    
    def __init__(self):
        self.memoryx = None
    
    def get_memoryx(self):
        if self.memoryx is None:
            from memoryx import MemoryX
            self.memoryx = MemoryX()
        return self.memoryx
    
    def handle_request(self, request: dict) -> dict:
        """处理 MCP 请求"""
        method = request.get("method", "")
        params = request.get("params", {})
        msg_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "memoryx", "version": "1.0.0"}
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "memoryx_search",
                            "description": "搜索 MemoryX 记忆库，找到与当前对话相关的记忆",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "搜索查询"},
                                    "user_id": {"type": "string", "description": "用户ID", "default": "xiao_cao_ye"},
                                    "limit": {"type": "number", "description": "返回数量", "default": 5}
                                }
                            }
                        },
                        {
                            "name": "memoryx_add",
                            "description": "添加新记忆",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string", "description": "记忆内容"},
                                    "user_id": {"type": "string", "description": "用户ID", "default": "xiao_cao_ye"}
                                }
                            }
                        },
                        {
                            "name": "memoryx_process",
                            "description": "处理消息：自动检索+自动记录",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string", "description": "用户消息"},
                                    "user_id": {"type": "string", "description": "用户ID", "default": "xiao_cao_ye"}
                                }
                            }
                        },
                        {
                            "name": "memoryx_stats",
                            "description": "获取 MemoryX 统计"
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {}) or {}
            
            try:
                if tool_name == "memoryx_search":
                    mx = self.get_memoryx()
                    results = mx.search(
                        user_id=arguments.get("user_id", "xiao_cao_ye"),
                        query=arguments.get("query", ""),
                        limit=arguments.get("limit", 5)
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps({
                                "memories_found": len(results),
                                "results": [{"id": r.get("id"), "score": r.get("score")} for r in results]
                            }, ensure_ascii=False)}]
                        }
                    }
                
                elif tool_name == "memoryx_add":
                    mx = self.get_memoryx()
                    from memoryx.core.models import MemoryLevel
                    mem = mx.add(
                        user_id=arguments.get("user_id", "xiao_cao_ye"),
                        content=arguments.get("content", ""),
                        level=MemoryLevel.USER
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps({"success": True, "memory_id": mem.id}, ensure_ascii=False)}]
                        }
                    }
                
                elif tool_name == "memoryx_process":
                    result = process_message(
                        arguments.get("message", ""),
                        arguments.get("user_id", "xiao_cao_ye")
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                        }
                    }
                
                elif tool_name == "memoryx_stats":
                    stats = get_stats()
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(stats, ensure_ascii=False)}]
                        }
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
            
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)}
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }


def run_stdio_server():
    """运行 MCP STDIO 服务器"""
    server = MCPServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = server.handle_request(request)
            
            print(json.dumps(response), flush=True)
        
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }), flush=True)


if __name__ == "__main__":
    run_stdio_server()


__all__ = [
    "auto_recall",
    "auto_record",
    "should_remember",
    "process_message",
    "get_report",
    "get_summary",
    "get_stats",
    "reset_stats",
    "close",
    "MCPServer"
]
