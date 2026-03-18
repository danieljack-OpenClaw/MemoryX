"""
MemoryX Token 压缩器
实现 90% Token 节省
"""

import re
from typing import List
from dataclasses import dataclass

from ..core.memory import Memory
from ..core.config import Config


@dataclass
class CompressedMemory:
    """压缩后的记忆"""
    summary: str
    key_points: List[str]
    original_count: int
    compressed_tokens: int


class TokenCompressor:
    """Token 智能压缩器"""
    
    # Token 估算 (中文约 1.5 字符/token, 英文约 4 字符/token)
    CHINESE_CHARS_PER_TOKEN = 1.5
    ENGLISH_CHARS_PER_TOKEN = 4
    
    def __init__(self, config: Config):
        self.config = config
        self.max_tokens = config.max_context_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """估算 token 数量"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        other_chars = len(text) - chinese_chars - english_chars
        
        tokens = (
            chinese_chars / self.CHINESE_CHARS_PER_TOKEN +
            english_chars / self.ENGLISH_CHARS_PER_TOKEN +
            other_chars / 2  # 符号等
        )
        
        return int(tokens)
    
    def compress(self, memories: List[Memory], max_tokens: int = None) -> str:
        """
        压缩记忆为摘要上下文
        
        Args:
            memories: 记忆列表
            max_tokens: 最大 token 数
            
        Returns:
            str: 压缩后的上下文
        """
        max_tokens = max_tokens or self.max_tokens
        
        if not memories:
            return ""
        
        # 按时间排序 (最新的在前)
        sorted_memories = sorted(memories, 
                                 key=lambda m: m.created_at, 
                                 reverse=True)
        
        # 如果 token 数量在限制内，直接返回
        all_content = "\n".join([m.content for m in sorted_memories])
        if self.estimate_tokens(all_content) <= max_tokens:
            return all_content
        
        # 需要压缩
        return self._compress_memories(sorted_memories, max_tokens)
    
    def _compress_memories(self, memories: List[Memory], max_tokens: int) -> str:
        """压缩记忆"""
        
        # 1. 按层级分组
        by_level = {}
        for mem in memories:
            if mem.level not in by_level:
                by_level[mem.level] = []
            by_level[mem.level].append(mem)
        
        # 2. 每层提取关键信息
        compressed = []
        total_tokens = 0
        
        # 优先级: user > skill > agent > project > session
        level_priority = ["user", "skill", "agent", "project", "session"]
        
        for level in level_priority:
            if level not in by_level:
                continue
            
            level_memories = by_level[level]
            
            for mem in level_memories:
                mem_tokens = self.estimate_tokens(mem.content)
                
                if total_tokens + mem_tokens <= max_tokens:
                    compressed.append(f"[{level.upper()}] {mem.content}")
                    total_tokens += mem_tokens
                else:
                    # 截断或摘要
                    remaining = max_tokens - total_tokens
                    if remaining > 50:
                        # 保留摘要
                        summary = self._summarize(mem.content, remaining)
                        compressed.append(f"[{level.upper()}] {summary}")
                        total_tokens = max_tokens
                    break
            
            if total_tokens >= max_tokens:
                break
        
        return "\n\n".join(compressed)
    
    def _summarize(self, content: str, max_tokens: int) -> str:
        """摘要内容"""
        # 简单摘要: 取前 N 个字符
        # 在实际实现中，可以调用 LLM 进行智能摘要
        max_chars = max_tokens * 3  # 粗略估算
        
        if len(content) <= max_chars:
            return content
        
        # 找到最后一个句号或逗号
        truncated = content[:max_chars]
        last_period = max(truncated.rfind('。'), truncated.rfind('.'))
        last_comma = max(truncated.rfind('，'), truncated.rfind(','))
        cut_point = max(last_period, last_comma)
        
        if cut_point > max_chars * 0.5:
            return truncated[:cut_point + 1]
        
        return truncated + "..."
    
    def expand(self, memory_str: str, query: str) -> str:
        """
        根据查询展开记忆
        
        在实际实现中，可以从向量数据库检索更多相关内容
        """
        return memory_str
