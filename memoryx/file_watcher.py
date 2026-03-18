# -*- coding: utf-8 -*-
"""
MemoryX 文件监听器 - 监听会话文件变化
当检测到新消息时立即处理，无需轮询
"""
import sys
import time
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger('MemoryX')

sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/projects/MemoryX')


class MemoryXFileWatcher:
    """
    监听 OpenClaw 会话文件变化
    当检测到新消息时立即自动调用 MemoryX
    """
    
    def __init__(self):
        self.session_path = Path('C:/Users/Yijiayi/.openclaw/agents/main/sessions')
        self.processed_file = Path('C:/Users/Yijiayi/.memoryx/processed_messages.json')
        
        # 加载已处理的消息
        self.processed = self._load_processed()
        
        # 跟踪文件状态
        self.file_states = {}  # {file_path: (last_size, last_mtime, last_line_hash)}
        
        # MemoryX 导入
        self._memoryx = None
        
        # 是否运行
        self.running = False
        
        logger.info("MemoryX File Watcher initialized")
    
    def _load_processed(self) -> dict:
        """加载已处理的消息"""
        if self.processed_file.exists():
            try:
                return json.loads(self.processed_file.read_text(encoding='utf-8'))
            except:
                pass
        return {"messages": [], "last_check": None}
    
    def _save_processed(self):
        """保存已处理的消息"""
        self.processed_file.parent.mkdir(parents=True, exist_ok=True)
        self.processed_file.write_text(json.dumps(self.processed, ensure_ascii=False), encoding='utf-8')
    
    def _get_memoryx(self):
        """获取 MemoryX 实例"""
        if self._memoryx is None:
            try:
                from memoryx.quick import quick_recall, quick_record
                from memoryx.stats import record_query
                self._mx_recall = quick_recall
                self._mx_record = quick_record
                self._mx_stats = record_query
                logger.info("MemoryX module loaded")
            except Exception as e:
                logger.error(f"Failed to load MemoryX: {e}")
                return False
        return True
    
    def _get_line_hash(self, line: str) -> str:
        """获取行的哈希"""
        return hashlib.md5(line.encode('utf-8')).hexdigest()[:16]
    
    def _extract_user_message(self, line: str) -> str:
        """从 JSONL 行提取用户消息"""
        if not line or not line.strip():
            return None
        
        try:
            entry = json.loads(line)
            
            # 检查是否是消息类型
            if entry.get('type') != 'message':
                return None
            
            msg = entry.get('message', {})
            
            # 检查是否是用户消息
            if msg.get('role') != 'user':
                return None
            
            # 提取内容
            content = msg.get('content', '')
            
            # 处理内容（可能是字符串或数组）
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'text':
                        return c.get('text', '')
            elif isinstance(content, str):
                return content
            
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.debug(f"Extract error: {e}")
        
        return None
    
    def _process_message(self, message: str) -> dict:
        """处理消息"""
        if not message or len(message.strip()) < 2:
            return {"status": "skipped", "reason": "empty"}
        
        # 加载 MemoryX
        if not self._get_memoryx():
            return {"status": "error", "reason": "MemoryX not loaded"}
        
        try:
            # 自动检索
            recall_result = self._mx_recall(message, 'xiao_cao_ye')
            
            # 自动记录
            record_result = self._mx_record(message, 'xiao_cao_ye')
            
            # 记录统计
            if recall_result.get('success'):
                self._mx_stats(
                    tokens_saved=recall_result.get('tokens_saved', 0),
                    memories_found=recall_result.get('memories_found', 0)
                )
                
                result = {
                    "status": "processed",
                    "message": message[:50],
                    "memories_found": recall_result.get('memories_found', 0),
                    "tokens_saved": recall_result.get('tokens_saved', 0),
                    "recorded": record_result.get('recorded', 0)
                }
                
                logger.info(f"Processed: {message[:30]}... | Found: {result['memories_found']} | Saved: {result['tokens_saved']:,}")
                
                return result
            
            return {"status": "no_result"}
            
        except Exception as e:
            logger.error(f"Process error: {e}")
            return {"status": "error", "reason": str(e)}
    
    def _check_file(self, file_path: Path) -> list:
        """检查文件是否有新消息"""
        if not file_path.exists():
            return []
        
        try:
            stat = file_path.stat()
            current_size = stat.st_size
            current_mtime = stat.st_mtime
            
            # 获取之前的状态
            prev_state = self.file_states.get(str(file_path))
            
            # 如果文件没有变化，跳过
            if prev_state:
                prev_size, prev_mtime, _ = prev_state
                if current_size <= prev_size:
                    return []
            
            # 读取新内容
            if prev_state:
                prev_size = prev_state[0]
            else:
                prev_size = 0
            
            content = file_path.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            
            # 只处理新增的行
            new_lines = lines[prev_size:] if prev_size > 0 else lines
            
            # 更新状态
            last_line_hash = self._get_line_hash(lines[-1]) if lines else None
            self.file_states[str(file_path)] = (current_size, current_mtime, last_line_hash)
            
            # 处理新行
            results = []
            for line in new_lines:
                if not line.strip():
                    continue
                
                line_hash = self._get_line_hash(line)
                
                # 检查是否已处理
                if line_hash in self.processed.get('messages', []):
                    continue
                
                # 提取用户消息
                message = self._extract_user_message(line)
                
                if message:
                    # 处理消息
                    result = self._process_message(message)
                    result['hash'] = line_hash
                    results.append(result)
                    
                    # 标记已处理
                    self.processed.setdefault('messages', []).append(line_hash)
            
            # 保存已处理记录（只保留最近500条）
            if len(self.processed['messages']) > 500:
                self.processed['messages'] = self.processed['messages'][-500:]
            self.processed['last_check'] = datetime.now().isoformat()
            self._save_processed()
            
            return results
            
        except Exception as e:
            logger.error(f"Check file error: {e}")
            return []
    
    def watch(self, interval: float = 0.5):
        """
        监听会话文件变化
        
        Args:
            interval: 检查间隔（秒），默认0.5秒
        """
        logger.info(f"Starting watch on {self.session_path}")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        self.last_process_count = 0
        
        while self.running:
            try:
                if not self.session_path.exists():
                    time.sleep(interval)
                    continue
                
                # 获取所有会话文件
                session_files = list(self.session_path.glob('*.jsonl'))
                
                # 检查最新的文件
                if session_files:
                    latest = max(session_files, key=lambda p: p.stat().st_mtime)
                    results = self._check_file(latest)
                    
                    if results:
                        self.last_process_count += len(results)
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Watch error: {e}")
                time.sleep(interval)
        
        self.running = False
        logger.info(f"Watch stopped. Total processed: {self.last_process_count}")
    
    def stop(self):
        """停止监听"""
        self.running = False


def main():
    watcher = MemoryXFileWatcher()
    
    try:
        watcher.watch(interval=0.5)  # 每0.5秒检查一次
    except KeyboardInterrupt:
        watcher.stop()


if __name__ == '__main__':
    main()
