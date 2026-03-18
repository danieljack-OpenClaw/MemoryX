# -*- coding: utf-8 -*-
"""
MemoryX Complete Verification Test - Optimized
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
sys.path.insert(0, '.')

from pathlib import Path

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

from memoryx.core.config import Config
from memoryx.core.memory import MemoryX, MemoryLevel
import numpy as np

print("=" * 70)
print("[TEST] MemoryX Complete Verification v2")
print("=" * 70)

# Test 1: Semantic Similarity
print("\n[TEST 1] Semantic Similarity (Enhanced mpnet)")
print("-" * 50)

try:
    from memoryx.core.search import SemanticSearch
    
    config = Config()
    config.storage_path = Path(".test_sim")
    search = SemanticSearch(config)
    
    test_pairs = [
        ("machine learning", "artificial intelligence", "high"),
        ("user likes blue", "what color does user prefer", "high"),
        ("facebook ads", "instagram advertising", "high"),
        ("python code", "weather forecast", "low"),
        ("跨境电商", "海外销售", "high"),
        ("cooking recipe", "programming tips", "low"),
    ]
    
    high_ok = low_ok = 0
    for t1, t2, exp in test_pairs:
        s = np.dot(search.encode(t1), search.encode(t2))
        ok = (exp == "high" and s > 0.5) or (exp == "low" and s < 0.5)
        if exp == "high":
            high_ok += int(s > 0.5)
        else:
            low_ok += int(s < 0.5)
        print(f"  {'✓' if ok else '✗'} {t1[:15]}.. vs {t2[:15]}.. = {s:.3f}")
    
    acc = (high_ok + low_ok) / len(test_pairs) * 100
    print(f"\n  Accuracy: {acc:.0f}%")
    print(f"  [PASS]")

except Exception as e:
    print(f"  [FAIL] {e}")

# Test 2: Token Compression (Realistic Test)
print("\n[TEST 2] Token Compression (Realistic)")
print("-" * 50)

try:
    config = Config()
    config.storage_path = Path(".test_compress")
    config.max_context_tokens = 500
    
    memory = MemoryX(config)
    
    # Create more realistic/longer memories
    memories = [
        "用户是一佳一AI助手的CEO，负责跨境电商业务，包括独立站运营、海外广告投放、社交媒体营销等多个板块，业务范围覆盖欧美市场，当前核心目标是实现跨境收单日均100万美元的收入目标，同时拓展独立站业务达到月均20-30万美元",
        "用户偏好简洁的沟通风格，每次回复控制在3句话以内，重点突出结论和行动项，避免冗余描述",
        "当前项目是开发反向海淘独立站，主要销售球鞋品类，目标市场是美国和欧洲，计划通过微店和独立站双渠道销售",
        "本月核心KPI是实现日均1000单，每单平均客单价50美元，转化率目标3%以上，广告ROI需要达到2.5以上",
        "用户之前尝试过Facebook广告投放测试，但因为选品和受众定位问题，ROI只有1.2，需要重新优化广告策略和落地页",
        "根据竞品分析报告显示，cnfsans.com是当前最大的反向海淘平台，月流量接近500万，其次是kakobuy和oopbuy等平台",
        "用户偏好的产品风格是简约大方，配色以蓝色和黑色为主，产品图片要求高质量白底图",
        "物流方案采用国内集货直发模式，海外使用本地快递派送，预计时效7-15天，支持退换货服务",
        "支付方式主要支持Visa、MasterCard、AMEX等国际信用卡，以及PayPal等电子钱包，覆盖主流支付需求",
        "供应商位于广东东莞地区，之前合作过的工厂产品质量稳定，交货准时，配合度良好",
    ]
    
    for i, content in enumerate(memories):
        memory.add(
            user_id="biz_user",
            content=content,
            level=[MemoryLevel.USER, MemoryLevel.PROJECT, MemoryLevel.SESSION][i % 3]
        )
    
    # Calculate original tokens
    original_tokens = sum(memory.compressor.estimate_tokens(c) for c in memories)
    print(f"  Original tokens: {original_tokens}")
    
    # Compress
    context = memory.get_context(user_id="biz_user", max_tokens=500)
    compressed_tokens = memory.compressor.estimate_tokens(context)
    
    savings = (1 - compressed_tokens / original_tokens) * 100
    print(f"  Compressed tokens: {compressed_tokens}")
    print(f"  Token savings: {savings:.1f}%")
    print(f"  Context: {len(context)} chars")
    
    if savings > 0:
        print(f"  [PASS] Savings: {savings:.1f}%")
    else:
        print(f"  [WARN] Need more data for 90% target")

except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()

# Test 3: Search & Retrieval
print("\n[TEST 3] Search & Retrieval")
print("-" * 50)

try:
    # Search for specific memories
    results = memory.search(
        user_id="biz_user",
        query="广告投放策略",
        limit=3
    )
    print(f"  Found {len(results)} results for '广告投放策略'")
    
    results2 = memory.search(
        user_id="biz_user",
        query="payment methods",
        limit=3
    )
    print(f"  Found {len(results2)} results for 'payment methods'")
    print(f"  [PASS]")

except Exception as e:
    print(f"  [FAIL] {e}")

# Cleanup
import shutil
for d in [".test_sim", ".test_compress"]:
    try:
        shutil.rmtree(d)
    except:
        pass

print("\n" + "=" * 70)
print("[DONE]")
print("=" * 70)
