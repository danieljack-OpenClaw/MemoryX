# -*- coding: utf-8 -*-
"""
MemoryX 后台监听服务
监听 OpenClaw 会话变化，自动调用 MemoryX
"""
import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime
import threading

sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/projects/MemoryX')


class MemoryXListener:
    """
    监听 OpenClaw 会话文件变化
    当检测到新消息时自动调用 MemoryX
    """
    
    def __init__(self, session_path: str = None, poll_interval: float = 2.0):
        if session_path is None:
            session_path = 'C:/Users/Yijiayi/.openclaw/agents/main/sessions'
        
        self.session_path = Path(session_path)
        self.poll_interval = poll_interval
        
        # 记录已处理的消息哈希
        self.processed_file = Path('C:/Users/Yijiayi/.memoryx/processed_messages.json')
        self.processed = self._load_processed()
        
        # MemoryX 导入
        self._memoryx = None
        
        self.running = False
    
    def _load_processed(self) -> dict:
        if self.processed_file.exists():
            try:
                return json.loads(self.processed_file.read_text(encoding='utf-8'))
            except:
                pass
        return {"files": {}}
    
    def _save_processed(self):
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_file.write_text(json.dumps(self.processed, ensure_ascii=False), encoding='utf-8')
    
    def _get_memoryx(self):
        if self._memoryx is None:
            try:
                from memoryx.quick import _get_memoryx
                self._memoryx = _get_memoryx()
            except:
                pass
        return self._memoryx
    
    def _get_latest_session(self) -> tuple:
        """获取最新的会话文件及其最后一行"""
        if not self.session_path.exists():
            return None, None
        
        session_files = list(self.session_path.glob('*.jsonl'))
        if not session_files:
            return None, None
        
        latest = max(session_files, key=lambda p: p.stat().st_mtime)
        
        try:
            lines = latest.read_text(encoding='utf-8').strip().split('\n')
            last_line = lines[-1] if lines else None
            return latest, last_line
        except:
            return None, None
    
    def _extract_user_message(self, line: str) -> str:
        """从 JSONL 行提取用户消息"""
        if not line:
            return None
        
        try:
            entry = json.loads(line)
            if entry.get('type') == 'message':
                msg = entry.get('message', {})
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    if isinstance(content, list):
                        for c in content:
                            if c.get('type') == 'text':
                                return c.get('text', '')
                    elif isinstance(content, str):
                        return content
        except:
            pass
        return None
    
    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件内容的哈希"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return hashlib.md5(content.encode()).hexdigest()[:12]
        except:
            return None
    
    def process_message(self, message: str):
        """处理消息 - 调用 MemoryX"""
        if not message or len(message.strip()) < 2:
            return
        
        mx = self._get_memoryx()
        if mx is None:
            return
        
        try:
            # 调用 MemoryX
            from memoryx.quick import quick_recall, quick_record
            from memoryx.stats import record_query
            
            # 检索
            recall_result = quick_recall(message, 'xiao_cao_ye')
            
            # 自动记录（如果需要）
            record_result = quick_record(message, 'xiao_cao_ye')
            
            # 记录统计
            if recall_result.get('success'):
                record_query(
                    tokens_saved=recall_result.get('tokens_saved', 0),
                    memories_found=recall_result.get('memories_found', 0)
                )
                
                print(f"[MemoryX Listener] Processed: {message[:30]}...")
                print(f"  Memories found: {recall_result.get('memories_found', 0)}")
                print(f"  Tokens saved: {recall_result.get('tokens_saved', 0):,}")
                
        except Exception as e:
            print(f"[MemoryX Listener] Error: {e}")
    
    def poll(self):
        """轮询检查会话变化"""
        last_file_state = {}
        
        while self.running:
            try:
                latest_file, last_line = self._get_latest_session()
                
                if latest_file is None:
                    time.sleep(self.poll_interval)
                    continue
                
                file_path_str = str(latest_file)
                current_hash = self._get_file_hash(latest_file)
                
                if current_hash is None:
                    time.sleep(self.poll_interval)
                    continue
                
                # 检查文件是否有新内容
                if file_path_str not in last_file_state:
                    last_file_state[file_path_str] = current_hash
                
                if current_hash != last_file_state[file_path_str]:
                    # 文件有变化
                    last_file_state[file_path_str] = current_hash
                    
                    # 提取新消息
                    if last_line:
                        message = self._extract_user_message(last_line)
                        if message:
                            # 检查是否已处理
                            msg_hash = hashlib.md5(message.encode()).hexdigest()[:12]
                            
                            if msg_hash not in self.processed.get('files', {}):
                                self.process_message(message)
                                self.processed.setdefault('files', {})[msg_hash] = {
                                    'message': message[:50],
                                    'time': datetime.now().isoformat()
                                }
                                self._save_processed()
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"[MemoryX Listener] Poll error: {e}")
                time.sleep(self.poll_interval)
    
    def start(self):
        """启动监听"""
        print("[MemoryX Listener] Starting...")
        self.running = True
        
        # 在新线程中运行
        self.thread = threading.Thread(target=self.poll, daemon=True)
        self.thread.start()
        
        print("[MemoryX Listener] Running! Press Ctrl+C to stop.")
    
    def stop(self):
        """停止监听"""
        print("[MemoryX Listener] Stopping...")
        self.running = False


def main():
    listener = MemoryXListener()
    
    try:
        listener.start()
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[MemoryX Listener] Interrupted")
        listener.stop()


if __name__ == '__main__':
    main()
