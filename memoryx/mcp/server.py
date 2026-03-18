# -*- coding: utf-8 -*-
"""
MemoryX MCP Server
让 MemoryX 通过 MCP 协议被 OpenClaw 自动调用
"""
import sys
import json
from pathlib import Path

# 添加路径
_proj_path = Path(__file__).parent.parent
if str(_proj_path) not in sys.path:
    sys.path.insert(0, str(_proj_path))

# 全局变量
_memoryx = None


def get_memoryx():
    """获取 MemoryX 实例"""
    global _memoryx
    if _memoryx is None:
        from memoryx import MemoryX
        _memoryx = MemoryX()
    return _memoryx


def handle_request(request: dict) -> dict:
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
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "memoryx",
                    "version": "1.0.0"
                }
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
                                "query": {
                                    "type": "string",
                                    "description": "搜索查询"
                                },
                                "user_id": {
                                    "type": "string",
                                    "description": "用户 ID",
                                    "default": "xiao_cao_ye"
                                },
                                "limit": {
                                    "type": "number",
                                    "description": "返回结果数量",
                                    "default": 5
                                }
                            }
                        }
                    },
                    {
                        "name": "memoryx_add",
                        "description": "添加新记忆到 MemoryX",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "记忆内容"
                                },
                                "user_id": {
                                    "type": "string",
                                    "description": "用户 ID",
                                    "default": "xiao_cao_ye"
                                },
                                "level": {
                                    "type": "string",
                                    "description": "记忆级别: user, session, agent",
                                    "default": "user"
                                }
                            }
                        }
                    },
                    {
                        "name": "memoryx_stats",
                        "description": "获取 MemoryX 使用统计",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        }
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        
        mx = get_memoryx()
        
        try:
            if tool_name == "memoryx_search":
                results = mx.search(
                    user_id=arguments.get("user_id", "xiao_cao_ye"),
                    query=arguments.get("query", ""),
                    limit=arguments.get("limit", 5)
                )
                context = mx.get_context(
                    user_id=arguments.get("user_id", "xiao_cao_ye"),
                    max_tokens=300
                )
                
                # 计算节省
                old_tokens = 250000
                new_tokens = len(context) // 4 if context else 0
                tokens_saved = max(0, old_tokens - new_tokens)
                
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "memories_found": len(results),
                                    "tokens_saved": tokens_saved,
                                    "context": context,
                                    "results": [{"id": r.get("id"), "score": r.get("score")} for r in results]
                                }, ensure_ascii=False)
                            }
                        ]
                    }
                }
            
            elif tool_name == "memoryx_add":
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
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"success": True, "memory_id": mem.id}, ensure_ascii=False)
                            }
                        ]
                    }
                }
            
            elif tool_name == "memoryx_stats":
                stats = mx.get_stats()
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(stats, ensure_ascii=False)
                            }
                        ]
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
    """运行 STDIO 服务器"""
    import sys
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = handle_request(request)
            
            print(json.dumps(response), flush=True)
        
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }), flush=True)


if __name__ == "__main__":
    run_stdio_server()
