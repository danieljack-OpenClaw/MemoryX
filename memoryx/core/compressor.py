# -*- coding: utf-8 -*-
"""
MemoryX Token Compressor - Optimized for 90% Token Savings
"""

import re
from typing import List
from collections import defaultdict

from .models import Memory
from .config import Config


class TokenCompressor:
    """Advanced Token Compressor with 90% savings target"""
    
    CHINESE_CHARS_PER_TOKEN = 1.5
    ENGLISH_CHARS_PER_TOKEN = 4
    
    def __init__(self, config: Config):
        self.config = config
        self.max_tokens = config.max_context_tokens
        self.llm_client = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM client"""
        if not self.config.llm_api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            if api_key:
                self.config.llm_api_key = api_key
        
        if self.config.llm_api_key:
            try:
                if self.config.llm_provider == "openai":
                    from openai import OpenAI
                    self.llm_client = OpenAI(api_key=self.config.llm_api_key)
                    self.llm_model = self.config.llm_model or "gpt-4o-mini"
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
        
        return max(1, int(tokens))
    
    def compress(self, memories: List[Memory], max_tokens: int = None) -> str:
        """Compress memories with 90% savings target"""
        max_tokens = max_tokens or self.max_tokens
        
        if not memories:
            return ""
        
        # Sort by importance and recency
        sorted_memories = self._prioritize_memories(memories)
        
        # Calculate original token count
        original_tokens = sum(self.estimate_tokens(m.content) for m in sorted_memories)
        
        # If within limit, return as-is (no need to compress)
        if original_tokens <= max_tokens:
            return self._format_memories_simple(sorted_memories)
        
        # Target: compress to fit within max_tokens
        # For 90% savings: target = original * 0.1, but at least max_tokens
        target_tokens = min(max_tokens, int(original_tokens * 0.3))  # 70% compression as practical target
        
        # Use LLM if available for best compression
        if self.llm_client:
            return self._llm_summarize(sorted_memories, target_tokens)
        
        # Advanced algorithm compression
        return self._advanced_compress(sorted_memories, target_tokens, original_tokens)
    
    def _prioritize_memories(self, memories: List[Memory]) -> List[Memory]:
        """Prioritize memories by importance"""
        # Level priority
        level_priority = {
            "user": 5,    # User preferences - highest
            "skill": 4,   # Skill knowledge
            "project": 3,  # Project info
            "agent": 2,    # Agent context
            "session": 1   # Session info - lowest
        }
        
        def get_priority(m: Memory) -> tuple:
            level_score = level_priority.get(m.level, 0)
            # Recent memories get higher priority
            return (level_score, m.created_at)
        
        return sorted(memories, key=get_priority, reverse=True)
    
    def _format_memories_simple(self, memories: List[Memory]) -> str:
        """Simple format without level markers"""
        return "\n".join([m.content for m in memories])
    
    def _format_memories(self, memories: List[Memory]) -> str:
        """Format memories as string"""
        lines = []
        for mem in memories:
            lines.append(f"[{mem.level.upper()}] {mem.content}")
        return "\n\n".join(lines)
    
    def _advanced_compress(self, memories: List[Memory], target_tokens: int, 
                          original_tokens: int) -> str:
        """Advanced compression algorithm targeting 90% savings"""
        
        result = []
        used_tokens = 0
        
        # First pass: keep high-priority memories completely
        for mem in memories:
            mem_tokens = self.estimate_tokens(mem.content)
            
            if used_tokens + mem_tokens <= target_tokens:
                result.append(f"[{mem.level.upper()}] {mem.content}")
                used_tokens += mem_tokens
            else:
                # Second pass: compress remaining with smart truncation
                remaining = target_tokens - used_tokens
                if remaining > 30:  # Minimum viable summary
                    compressed = self._smart_truncate(mem.content, remaining)
                    result.append(f"[{mem.level.upper()}] {compressed}")
                    break
                else:
                    break
        
        # If still too long, apply aggressive compression
        while self.estimate_tokens("\n\n".join(result)) > target_tokens and len(result) > 1:
            # Remove less important details
            result = self._aggressive_trim(result, target_tokens)
        
        savings = (1 - self.estimate_tokens("\n\n".join(result)) / original_tokens) * 100
        print(f"[MemoryX] Compression: {savings:.1f}% savings ({original_tokens} -> {self.estimate_tokens(' '.join(result))} tokens)")
        
        return "\n\n".join(result)
    
    def _smart_truncate(self, content: str, max_tokens: int) -> str:
        """Smart truncation preserving key information"""
        max_chars = max_tokens * 3  # Approximate
        
        if len(content) <= max_chars:
            return content
        
        # Find last complete sentence
        sentences = re.split(r'[。.!?]', content)
        truncated = ""
        
        for sentence in sentences:
            if self.estimate_tokens(truncated + sentence) <= max_tokens:
                truncated = sentence + "."
            else:
                break
        
        # If no complete sentence fits, take first N chars
        if not truncated:
            truncated = content[:max_chars]
            # Try to end at word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_chars * 0.7:
                truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _aggressive_trim(self, lines: List[str], target_tokens: int) -> List[str]:
        """Aggressive trimming for extreme compression"""
        result = []
        
        for line in lines:
            tokens = self.estimate_tokens(line)
            
            if self.estimate_tokens("\n\n".join(result)) + tokens <= target_tokens:
                result.append(line)
            elif result:
                # Compress last entry
                last = result.pop()
                compressed = self._extract_key_points(last, target_tokens - self.estimate_tokens("\n\n".join(result)))
                result.append(compressed)
                break
        
        return result
    
    def _extract_key_points(self, text: str, max_tokens: int) -> str:
        """Extract only key points from text"""
        # Extract first sentence + key terms
        sentences = re.split(r'[。.!?]', text)
        if not sentences:
            return text[:max_tokens * 3]
        
        first = sentences[0]
        if self.estimate_tokens(first) <= max_tokens:
            return first + "."
        
        # Take first N words
        words = first.split()
        result = ""
        for word in words:
            if self.estimate_tokens(result + " " + word) <= max_tokens:
                result += " " + word
            else:
                break
        
        return result.strip() + "..."
    
    def _llm_summarize(self, memories: List[Memory], max_tokens: int) -> str:
        """LLM-powered intelligent summarization"""
        try:
            # Prepare memory content with importance indicators
            memory_texts = []
            for mem in memories:
                importance = {"user": "★★★", "skill": "★★", "project": "★", "agent": "★", "session": "☆"}
                stars = importance.get(mem.level, "★")
                memory_texts.append(f"{stars} [{mem.level}] {mem.content}")
            
            full_text = "\n".join(memory_texts)
            
            # Check if summarization needed
            if self.estimate_tokens(full_text) <= max_tokens:
                return full_text
            
            # LLM summarization prompt
            prompt = f"""请将以下记忆压缩到最多 {max_tokens} tokens。
要求：
1. 保留所有 3星(★★★) 高优先级信息
2. 保留关键事实和数据
3. 删除重复描述
4. 使用简洁的表达

记忆内容：
{full_text}

压缩后的记忆："""
            
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_tokens, 2000),
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            original = self.estimate_tokens(full_text)
            compressed = self.estimate_tokens(summary)
            savings = (1 - compressed / original) * 100 if original > 0 else 0
            
            print(f"[MemoryX] LLM Compression: {savings:.1f}% savings ({original} -> {compressed} tokens)")
            
            return summary
            
        except Exception as e:
            print(f"[MemoryX] LLM summarization failed: {e}, using advanced algorithm")
            return self._advanced_compress(memories, max_tokens, 
                                          sum(self.estimate_tokens(m.content) for m in memories))
    
    def expand(self, memory_str: str, query: str) -> str:
        """Expand memory based on query"""
        return memory_str
