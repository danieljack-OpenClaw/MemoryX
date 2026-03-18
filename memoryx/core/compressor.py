# -*- coding: utf-8 -*-
"""
MemoryX Token Compressor with LLM Summarization
"""

import re
from typing import List

from .models import Memory
from .config import Config


class TokenCompressor:
    """Token Smart Compressor with LLM"""
    
    CHINESE_CHARS_PER_TOKEN = 1.5
    ENGLISH_CHARS_PER_TOKEN = 4
    
    def __init__(self, config: Config):
        self.config = config
        self.max_tokens = config.max_context_tokens
        self.llm_client = None
        
        # Initialize LLM if available
        if config.llm_api_key:
            self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM client"""
        try:
            if self.config.llm_provider == "openai":
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=self.config.llm_api_key)
                self.llm_model = self.config.llm_model
                print(f"[MemoryX] LLM initialized: {self.config.llm_provider}/{self.llm_model}")
        except Exception as e:
            print(f"[MemoryX] LLM init failed: {e}")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        other_chars = len(text) - chinese_chars - english_chars
        
        tokens = (
            chinese_chars / self.CHINESE_CHARS_PER_TOKEN +
            english_chars / self.ENGLISH_CHARS_PER_TOKEN +
            other_chars / 2
        )
        
        return int(tokens)
    
    def compress(self, memories: List[Memory], max_tokens: int = None) -> str:
        """Compress memories into summary context"""
        max_tokens = max_tokens or self.max_tokens
        
        if not memories:
            return ""
        
        # Sort by time (newest first)
        sorted_memories = sorted(memories, 
                                 key=lambda m: m.created_at, 
                                 reverse=True)
        
        # Check if within limit
        all_content = "\n".join([m.content for m in sorted_memories])
        if self.estimate_tokens(all_content) <= max_tokens:
            return all_content
        
        # Use LLM summarization if available
        if self.llm_client:
            return self._llm_summarize(sorted_memories, max_tokens)
        
        # Fallback: basic compression
        return self._basic_compress(sorted_memories, max_tokens)
    
    def _llm_summarize(self, memories: List[Memory], max_tokens: int) -> str:
        """LLM-powered intelligent summarization"""
        try:
            # Prepare memory content
            memory_texts = []
            for i, mem in enumerate(memories):
                memory_texts.append(f"[{i+1}. {mem.level}] {mem.content}")
            
            full_text = "\n".join(memory_texts)
            
            # Check if need summarization
            if self.estimate_tokens(full_text) <= max_tokens:
                return full_text
            
            # Ask LLM to summarize
            prompt = f"""Please summarize the following user memories into a concise context (max {max_tokens} tokens). 
保留关键信息：用户偏好、重要事实、任务进度。

Memories:
{full_text}

Summary:"""
            
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_tokens, 1000)
            )
            
            summary = response.choices[0].message.content
            print(f"[MemoryX] LLM Summary: {len(summary)} chars")
            return summary
            
        except Exception as e:
            print(f"[MemoryX] LLM summarization failed: {e}")
            return self._basic_compress(memories, max_tokens)
    
    def _basic_compress(self, memories: List[Memory], max_tokens: int) -> str:
        """Basic compression without LLM"""
        by_level = {}
        for mem in memories:
            if mem.level not in by_level:
                by_level[mem.level] = []
            by_level[mem.level].append(mem)
        
        compressed = []
        total_tokens = 0
        
        level_priority = ["user", "skill", "agent", "project", "session"]
        
        for level in level_priority:
            if level not in by_level:
                continue
            
            for mem in by_level[level]:
                mem_tokens = self.estimate_tokens(mem.content)
                
                if total_tokens + mem_tokens <= max_tokens:
                    compressed.append(f"[{level.upper()}] {mem.content}")
                    total_tokens += mem_tokens
                else:
                    remaining = max_tokens - total_tokens
                    if remaining > 50:
                        summary = mem.content[:remaining * 3] + "..."
                        compressed.append(f"[{level.upper()}] {summary}")
                    break
            
            if total_tokens >= max_tokens:
                break
        
        return "\n\n".join(compressed)
    
    def expand(self, memory_str: str, query: str) -> str:
        """Expand memory based on query"""
        # Could use LLM to expand relevant parts
        return memory_str
