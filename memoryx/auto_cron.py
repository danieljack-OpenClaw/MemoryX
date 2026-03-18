# -*- coding: utf-8 -*-
"""
MemoryX 自动处理脚本 - 由 cron 定期调用
"""
import sys
sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/projects/MemoryX')

from memoryx.quick import quick_recall, quick_record
from memoryx.stats import record_query
from memoryx.core.memory import MemoryX
from pathlib import Path
import json
import hashlib
from datetime import datetime

def process_latest_message():
    """处理最新的一条用户消息"""
    sessions_dir = Path('C:/Users/Yijiayi/.openclaw/agents/main/sessions')
    
    if not sessions_dir.exists():
        return {"status": "no_sessions"}
    
    # 找最新的会话文件
    session_files = list(sessions_dir.glob('*.jsonl'))
    if not session_files:
        return {"status": "no_files"}
    
    latest = max(session_files, key=lambda p: p.stat().st_mtime)
    
    try:
        lines = latest.read_text(encoding='utf-8').strip().split('\n')
        if not lines:
            return {"status": "empty"}
        
        # 找最后一条用户消息
        last_msg = None
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'message' and entry.get('message', {}).get('role') == 'user':
                    content = entry.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        for c in content:
                            if c.get('type') == 'text':
                                last_msg = c.get('text', '')
                                break
                    elif isinstance(content, str):
                        last_msg = content
                    break
            except:
                continue
        
        if not last_msg or len(last_msg.strip()) < 2:
            return {"status": "no_message"}
        
        # 检查是否已处理
        msg_hash = hashlib.md5(last_msg.encode()).hexdigest()[:12]
        cache_file = Path('C:/Users/Yijiayi/.memoryx/processed_cache.json')
        
        processed = {}
        if cache_file.exists():
            try:
                processed = json.loads(cache_file.read_text(encoding='utf-8'))
            except:
                pass
        
        if msg_hash in processed:
            return {"status": "already_processed", "hash": msg_hash}
        
        # 处理消息
        recall_result = quick_recall(last_msg, 'xiao_cao_ye')
        record_result = quick_record(last_msg, 'xiao_cao_ye')
        
        if recall_result.get('success'):
            record_query(
                tokens_saved=recall_result.get('tokens_saved', 0),
                memories_found=recall_result.get('memories_found', 0)
            )
        
        # 标记已处理
        processed[msg_hash] = {
            "time": datetime.now().isoformat(),
            "msg": last_msg[:30],
            "found": recall_result.get('memories_found', 0)
        }
        
        # 只保留最近100条
        if len(processed) > 100:
            processed = dict(list(processed.items())[-100:])
        
        cache_file.write_text(json.dumps(processed, ensure_ascii=False), encoding='utf-8')
        
        return {
            "status": "processed",
            "found": recall_result.get('memories_found', 0),
            "saved": recall_result.get('tokens_saved', 0),
            "recorded": record_result.get('recorded', 0)
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == '__main__':
    result = process_latest_message()
    print(json.dumps(result, ensure_ascii=False))
