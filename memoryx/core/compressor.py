# -*- coding: utf-8 -*-
"""
MemoryX Token Compressor - 90% Savings Without LLM
"""

import re
from typing import List

from .models import Memory
from .config import Config


class TokenCompressor:
    """Ultra Compression - 90% Token Savings Target"""
    
    CHINESE_CHARS_PER_TOKEN = 1.5
    ENGLISH_CHARS_PER_TOKEN = 4
    
    def __init__(self, config: Config):
        self.config = config
        self.max_tokens = config.max_context_tokens
        self.llm_client = None
        self._init_llm()
    
    def _init_llm(self):
        if not self.config.llm_api_key:
            import os
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
            if api_key:
                self.config.llm_api_key = api_key
        
        if self.config.llm_api_key:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=self.config.llm_api_key)
                self.llm_model = self.config.llm_model or "gpt-4o-mini"
            except:
                pass
    
    def estimate_tokens(self, text: str) -> int:
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        english = len(re.findall(r'[a-zA-Z]', text))
        other = len(text) - chinese - english
        return max(1, int(
            chinese / 1.5 + english / 4 + other / 2
        ))
    
    def compress(self, memories: List[Memory], max_tokens: int = None) -> str:
        max_tokens = max_tokens or self.max_tokens
        
        if not memories:
            return ""
        
        # Sort by priority
        sorted_memories = self._prioritize(memories)
        original = sum(self.estimate_tokens(m.content) for m in sorted_memories)
        
        # If already within limit
        if original <= max_tokens:
            return self._format_simple(sorted_memories)
        
        # Ultra compression (90% target)
        target = max(max_tokens, int(original * 0.1))  # 10% of original = 90% savings
        
        if self.llm_client:
            return self._llm_compress(sorted_memories, target)
        
        # NO-LLM: Extract only key facts
        return self._ultra_compress(sorted_memories, target, original)
    
    def _prioritize(self, memories: List[Memory]) -> List[Memory]:
        priority = {"user": 5, "skill": 4, "project": 3, "agent": 2, "session": 1}
        return sorted(memories, key=lambda m: (priority.get(m.level, 0), m.created_at), reverse=True)
    
    def _format_simple(self, memories: List[Memory]) -> str:
        return "\n".join(m.content for m in memories)
    
    def _extract_key_facts(self, text: str, max_tokens: int) -> str:
        """Extract only key facts as bullet points"""
        sentences = re.split(r'[。.!?；\n]', text)
        facts = []
        used = 0
        
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            tokens = self.estimate_tokens(s)
            if used + tokens <= max_tokens:
                facts.append(s)
                used += tokens
            elif len(facts) < 3:  # At least 3 facts
                # Truncate
                remaining = max_tokens - used
                if remaining > 10:
                    facts.append(s[:remaining*3] + "...")
                    break
        
        return " | ".join(facts) if facts else text[:max_tokens*3]
    
    def _ultra_compress(self, memories: List[Memory], target: int, original: int) -> str:
        """90% compression without LLM"""
        result = []
        used = 0
        
        # Level priority
        level_names = {"user": "用户", "skill": "技能", "project": "项目", "agent": "代理", "session": "会话"}
        
        for mem in memories:
            mem_tokens = self.estimate_tokens(mem.content)
            
            if used + mem_tokens <= target:
                # Full content fits
                result.append(f"[{level_names.get(mem.level, mem.level)}] {mem.content}")
                used += mem_tokens
            else:
                # Extract key facts only
                remaining = target - used
                if remaining > 20:  # Minimum
                    key_facts = self._extract_key_facts(mem.content, remaining)
                    result.append(f"[{level_names.get(mem.level, mem.level)}] {key_facts}")
                    break
                else:
                    break
        
        output = "\n\n".join(result)
        compressed = self.estimate_tokens(output)
        savings = (1 - compressed / original) * 100 if original > 0 else 0
        
        print(f"[MemoryX] Compression: {savings:.1f}% savings ({original} -> {compressed} tokens)")
        
        return output
    
    def _llm_compress(self, memories: List[Memory], target: int) -> str:
        try:
            texts = [f"[{m.level}] {m.content}" for m in memories]
            prompt = f"压缩到最多 {target} tokens，保留关键信息：\n\n" + "\n".join(texts)
            
            resp = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(target, 2000)
            )
            return resp.choices[0].message.content
        except:
            return self._ultra_compress(memories, target, sum(self.estimate_tokens(m.content) for m in memories))
    
    def expand(self, text: str, query: str) -> str:
        return text
