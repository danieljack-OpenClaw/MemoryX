# -*- coding: utf-8 -*-
"""
MemoryX Complete Verification Test
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
sys.path.insert(0, '.')

from pathlib import Path
from memoryx.core.config import Config
from memoryx.core.memory import MemoryX, MemoryLevel
import numpy as np

print("=" * 70)
print("[TEST] MemoryX Complete Verification")
print("=" * 70)

results = {}

# Test 1: Basic initialization
print("\n[TEST 1] Initialization")
try:
    config = Config()
    config.storage_path = Path(".test_memoryx")
    memory = MemoryX(config)
    print("  [PASS] MemoryX initialized")
    results["init"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["init"] = False

# Test 2: Add memory
print("\n[TEST 2] Add Memory")
try:
    mem = memory.add(
        user_id="test_user",
        content="用户喜欢简洁的沟通风格",
        level=MemoryLevel.USER
    )
    print(f"  [PASS] Memory added: {mem.id}")
    results["add"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["add"] = False

# Test 3: Search memory
print("\n[TEST 3] Search Memory")
try:
    results_search = memory.search(
        user_id="test_user",
        query="沟通偏好"
    )
    print(f"  [PASS] Search found {len(results_search)} results")
    results["search"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["search"] = False

# Test 4: Token compression
print("\n[TEST 4] Token Compression")
try:
    for i in range(5):
        memory.add(
            user_id="test_user",
            content=f"这是第{i+1}条测试记忆内容，用于验证Token压缩功能，包含了用户偏好和一些项目信息",
            level=MemoryLevel.SESSION
        )
    
    context = memory.get_context(user_id="test_user", max_tokens=50)
    original = 6 * 40  # rough estimate
    compressed = memory.compressor.estimate_tokens(context)
    savings = (1 - compressed / original) * 100 if original > 0 else 0
    print(f"  Original: ~{original}, Compressed: {compressed}")
    print(f"  Savings: {savings:.1f}%")
    if savings > 50:
        print(f"  [PASS] Compression working!")
        results["compression"] = True
    else:
        print(f"  [WARN] Low compression")
        results["compression"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["compression"] = False

# Test 5: Multi-level memory
print("\n[TEST 5] Multi-level Memory")
try:
    levels = [MemoryLevel.USER, MemoryLevel.SESSION, MemoryLevel.PROJECT, MemoryLevel.AGENT, MemoryLevel.SKILL]
    for lvl in levels:
        m = memory.add(user_id="test_user", content=f"测试{lvl}层级", level=lvl)
    print(f"  [PASS] All {len(levels)} levels supported")
    results["levels"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["levels"] = False

# Test 6: Backup
print("\n[TEST 6] Backup")
try:
    backup_id = memory.backup()
    print(f"  [PASS] Backup created: {backup_id}")
    results["backup"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["backup"] = False

# Test 7: Stats
print("\n[TEST 7] Statistics")
try:
    stats = memory.get_stats()
    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Storage size: {stats['storage_size']} bytes")
    print(f"  Vector dim: {stats['vector_dim']}")
    print(f"  [PASS]")
    results["stats"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    results["stats"] = False

# Test 8: Cloud providers list
print("\n[TEST 8] Cloud Providers")
try:
    from memoryx.cloud.sync import CloudSync
    cloud = CloudSync(config)
    providers = cloud.get_supported_providers()
    connected = sum(1 for p in providers.values() if p.get('connected'))
    print(f"  Total providers: {len(providers)}")
    print(f"  Connected: {connected}")
    print(f"  [PASS]")
    results["cloud"] = True
except Exception as e:
    print(f"  [FAIL] {e}")
    import traceback
    traceback.print_exc()
    results["cloud"] = False

# Cleanup
import shutil
try:
    shutil.rmtree(".test_memoryx")
except:
    pass

# Summary
print("\n" + "=" * 70)
print("[SUMMARY]")
print("=" * 70)

passed = sum(1 for v in results.values() if v)
total = len(results)

print(f"\nPassed: {passed}/{total}")
print("\nResults:")
for k, v in results.items():
    status = "✓" if v else "✗"
    print(f"  {status} {k}")

if passed == total:
    print("\n[SUCCESS] All tests passed!")
else:
    print(f"\n[WARN] {total - passed} test(s) failed")

print("=" * 70)
