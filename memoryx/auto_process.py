# -*- coding: utf-8 -*-
"""
MemoryX 自动处理脚本
通过 cron job 定期调用，处理最新会话消息
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/projects/MemoryX')

from memoryx.openclaw_integration import auto_recall, auto_record, get_stats
from memoryx.stats import record_query


def process_recent_messages():
    """
    处理最近的会话消息
    由 cron job 定期调用
    """
    # 读取最新的会话文件
    sessions_dir = Path('C:/Users/Yijiayi/.openclaw/agents/main/sessions')
    
    if not sessions_dir.exists():
        return {"status": "no_sessions", "processed": 0}
    
    # 找最新的会话文件
    session_files = list(sessions_dir.glob('*.jsonl'))
    if not session_files:
        return {"status": "no_files", "processed": 0}
    
    latest_file = max(session_files, key=lambda p: p.stat().st_mtime)
    
    # 读取最后一条用户消息
    try:
        lines = latest_file.read_text(encoding='utf-8').strip().split('\n')
        
        last_user_message = None
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'message' and entry.get('message', {}).get('role') == 'user':
                    content = entry.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        for c in content:
                            if c.get('type') == 'text':
                                last_user_message = c.get('text', '')
                                break
                    elif isinstance(content, str):
                        last_user_message = content
                    break
            except:
                continue
        
        if not last_user_message:
            return {"status": "no_user_message", "processed": 0}
        
        # 处理消息
        result = auto_recall(last_user_message, 'xiao_cao_ye')
        
        # 自动记录（如果需要）
        auto_record(last_user_message, 'xiao_cao_ye')
        
        # 记录统计
        if result.get('success'):
            record_query(
                tokens_saved=result.get('tokens_saved', 0),
                memories_found=result.get('memories_found', 0)
            )
        
        return {
            "status": "success",
            "processed": 1,
            "session": latest_file.name,
            "message_preview": last_user_message[:50],
            "memories_found": result.get('memories_found', 0),
            "tokens_saved": result.get('tokens_saved', 0)
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e), "processed": 0}


def main():
    result = process_recent_messages()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
