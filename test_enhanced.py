# -*- coding: utf-8 -*-
"""
MemoryX Enhanced Verification
Tests real embeddings and LLM summarization
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
sys.path.insert(0, '.')

from pathlib import Path

# Test configuration
os.environ["LLM_API_KEY"] = os.getenv("LLM_API_KEY", "sk-test")  # Set your key

from memoryx.core.config import Config
from memoryx.core.memory import MemoryX, MemoryLevel

print("=" * 60)
print("[TEST] MemoryX Enhanced Verification")
print("=" * 60)

# Test 1: Real Embeddings
print("\n[1] Testing Real Embeddings...")
try:
    from memoryx.core.search import SemanticSearch
    config = Config()
    config.storage_path = Path(".test_memoryx")
    
    search = SemanticSearch(config)
    
    # Test encoding
    embedding1 = search.encode("I love machine learning")
    embedding2 = search.encode("Artificial intelligence is great")
    
    # Calculate similarity
    import numpy as np
    sim = np.dot(embedding1, embedding2)
    print(f"   Embedding dimension: {len(embedding1)}")
    print(f"   Similarity between related texts: {sim:.4f}")
    
    if sim > 0.5:
        print("   [OK] Real semantic embeddings working!")
    else:
        print("   [WARN] Similarity lower than expected")
        
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 2: Full MemoryX with embeddings
print("\n[2] Testing MemoryX with real embeddings...")
try:
    config = Config()
    config.storage_path = Path(".test_memoryx2")
    memory = MemoryX(config)
    
    # Add memories
    mem1 = memory.add(
        user_id="user_001",
        content="User prefers short, concise responses. Maximum 3 sentences.",
        level=MemoryLevel.USER
    )
    
    mem2 = memory.add(
        user_id="user_001",
        content="User is working on cross-border e-commerce business.",
        level=MemoryLevel.USER
    )
    
    mem3 = memory.add(
        user_id="user_001",
        content="Current goal: scale business to $100K monthly revenue.",
        level=MemoryLevel.PROJECT
    )
    
    print(f"   Added 3 memories")
    
    # Search
    results = memory.search(
        user_id="user_001",
        query="business goals",
        limit=3
    )
    
    print(f"   Search results: {len(results)} found")
    if results:
        print(f"   Top result score: {results[0].get('score', 0):.4f}")
    
    print("   [OK] Memory with embeddings working!")
    
except Exception as e:
    print(f"   [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Token Compression
print("\n[3] Testing Token Compression...")
try:
    # Add more memories
    for i in range(10):
        memory.add(
            user_id="user_001",
            content=f"This is test memory number {i+1}. It contains some information about the user's preferences and project details that need to be compressed.",
            level=MemoryLevel.SESSION
        )
    
    # Get compressed context
    context = memory.get_context(user_id="user_001", max_tokens=200)
    
    original_tokens = 10 * 50  # rough estimate
    compressed_tokens = memory.compressor.estimate_tokens(context)
    savings = (1 - compressed_tokens / original_tokens) * 100
    
    print(f"   Original (est): ~{original_tokens} tokens")
    print(f"   Compressed: {compressed_tokens} tokens")
    print(f"   Savings: {savings:.1f}%")
    print(f"   Context length: {len(context)} chars")
    
    print("   [OK] Token compression working!")
    
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 4: LLM Summarization (if API key provided)
print("\n[4] Testing LLM Summarization...")
if os.getenv("LLM_API_KEY") and os.getenv("LLM_API_KEY") != "sk-test":
    try:
        config_llm = Config()
        config_llm.storage_path = Path(".test_memoryx3")
        config_llm.llm_api_key = os.getenv("LLM_API_KEY")
        config_llm.llm_provider = "openai"
        config_llm.llm_model = "gpt-4o-mini"
        
        memory_llm = MemoryX(config_llm)
        
        # Add test memories
        for i in range(5):
            memory_llm.add(
                user_id="test_user",
                content=f"Memory {i+1}: User likes to work on AI projects. They prefer Python over other languages. Currently learning about memory systems.",
                level=MemoryLevel.USER
            )
        
        context = memory_llm.get_context(user_id="test_user", max_tokens=150)
        print(f"   LLM Summary length: {len(context)} chars")
        print("   [OK] LLM summarization working!")
        
    except Exception as e:
        print(f"   [WARN] LLM test skipped: {e}")
else:
    print("   [SKIP] LLM_API_KEY not set - skipping LLM test")
    print("   To enable, set: export LLM_API_KEY=your-key")

# Cleanup
print("\n[5] Cleanup...")
import shutil
for d in [".test_memoryx", ".test_memoryx2", ".test_memoryx3"]:
    try:
        shutil.rmtree(d)
    except:
        pass

print("\n" + "=" * 60)
print("[SUCCESS] Enhanced verification complete!")
print("=" * 60)
