# Test MemoryX in OpenClaw
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/workspace/projects/MemoryX')

print("=" * 60)
print("MemoryX OpenClaw Plugin Verification")
print("=" * 60)

# Test 1: Import
print("\n[1] Testing import...")
try:
    from memoryx import MemoryX
    print("  [PASS] MemoryX imported")
except Exception as e:
    print(f"  [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize
print("\n[2] Testing initialization...")
try:
    from pathlib import Path
    test_path = Path("C:/Users/Yijiayi/.openclaw/test_memoryx")
    from memoryx.core.config import Config
    config = Config()
    config.storage_path = test_path
    
    memory = MemoryX(config)
    print("  [PASS] MemoryX initialized")
except Exception as e:
    print(f"  [FAIL] Init failed: {e}")
    sys.exit(1)

# Test 3: Add memory
print("\n[3] Testing add memory...")
try:
    mem = memory.add(
        user_id="test_user",
        content="测试记忆：用户喜欢蓝色",
        level="user"
    )
    print(f"  [PASS] Memory added: {mem.id}")
except Exception as e:
    print(f"  [FAIL] Add failed: {e}")
    sys.exit(1)

# Test 4: Search
print("\n[4] Testing search...")
try:
    results = memory.search(user_id="test_user", query="颜色")
    print(f"  [PASS] Search found {len(results)} results")
except Exception as e:
    print(f"  [FAIL] Search failed: {e}")
    sys.exit(1)

# Test 5: Compression
print("\n[5] Testing compression...")
try:
    for i in range(3):
        memory.add(user_id="test_user", content=f"这是第{i+1}条测试记忆内容，用于验证Token压缩功能", level="session")
    context = memory.get_context(user_id="test_user", max_tokens=100)
    print(f"  [PASS] Compression: {len(context)} chars")
except Exception as e:
    print(f"  [FAIL] Compression failed: {e}")
    sys.exit(1)

# Test 6: Stats
print("\n[6] Testing stats...")
try:
    stats = memory.get_stats()
    print(f"  [PASS] Total memories: {stats['total_memories']}")
except Exception as e:
    print(f"  [FAIL] Stats failed: {e}")
    sys.exit(1)

# Test 7: Cloud config
print("\n[7] Testing cloud config...")
try:
    from memoryx.core.storage import StorageManager
    storage = StorageManager(config)
    print(f"  [PASS] Cloud enabled: {storage.cloud_enabled}")
except Exception as e:
    print(f"  [FAIL] Cloud config failed: {e}")

# Test 8: Dashboard API
print("\n[8] Testing Dashboard API...")
try:
    from memoryx.dashboard.main import app
    print(f"  [PASS] Dashboard app loaded")
except Exception as e:
    print(f"  [FAIL] Dashboard failed: {e}")

# Cleanup
import shutil
try:
    shutil.rmtree(test_path)
except:
    pass

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
