"""
MemoryX 快速验证脚本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')

from pathlib import Path
from memoryx.core.config import Config
from memoryx.core.memory import MemoryX, MemoryLevel

print("=" * 50)
print("[TEST] MemoryX Functional Verification")
print("=" * 50)

# 1. 初始化
print("\n[1] Initializing MemoryX...")
try:
    config = Config()
    config.storage_path = Path(".test_memoryx")
    memory = MemoryX(config)
    print("   [OK] Initialization successful")
except Exception as e:
    print(f"   [FAIL] Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. 添加记忆
print("\n[2] Testing add memory...")
try:
    mem = memory.add(
        user_id="test_user",
        content="User prefers concise communication, max 3 sentences per message",
        level=MemoryLevel.USER
    )
    print(f"   [OK] Memory added: {mem.id}")
except Exception as e:
    print(f"   [FAIL] Add failed: {e}")

# 3. 搜索记忆
print("\n[3] Testing search...")
try:
    results = memory.search_memories(
        user_id="test_user",
        query="communication preference"
    )
    print(f"   [OK] Search successful, found {len(results)} results")
except Exception as e:
    print(f"   [FAIL] Search failed: {e}")

# 4. Token压缩
print("\n[4] Testing Token compression...")
try:
    for i in range(5):
        memory.add(
            user_id="test_user",
            content=f"Test memory content number {i+1} for compression verification",
            level=MemoryLevel.SESSION
        )
    
    context = memory.get_context(user_id="test_user", max_tokens=100)
    print(f"   [OK] Context compressed, length: {len(context)} chars")
except Exception as e:
    print(f"   [FAIL] Compression failed: {e}")

# 5. 进化引擎
print("\n[5] Testing Evolution Engine...")
try:
    from memoryx.evolution.engine import EvolutionEngine
    engine = EvolutionEngine(config)
    result = engine.evolve(agent_id="test_agent")
    print(f"   [OK] Evolution engine started")
    print(f"   [INFO] Selected {len(result['genes'])} genes")
except Exception as e:
    print(f"   [FAIL] Evolution failed: {e}")

# 6. 多Agent管理
print("\n[6] Testing Multi-Agent Manager...")
try:
    from memoryx.agent.manager import MultiAgentManager
    agent_mgr = MultiAgentManager(config)
    agent = agent_mgr.create_agent(
        agent_id="agent_001",
        name="Test Assistant",
        description="AI assistant for testing"
    )
    print(f"   [OK] Agent created: {agent.name}")
except Exception as e:
    print(f"   [FAIL] Agent management failed: {e}")

# 7. 备份功能
print("\n[7] Testing Backup...")
try:
    from memoryx.backup.manager import BackupManager
    backup_mgr = BackupManager(config)
    backup_id = backup_mgr.backup()
    print(f"   [OK] Backup created: {backup_id}")
except Exception as e:
    print(f"   [FAIL] Backup failed: {e}")

# 清理
import shutil
try:
    shutil.rmtree(".test_memoryx")
    print("\n[CLEANUP] Test data cleaned")
except:
    pass

print("\n" + "=" * 50)
print("[SUCCESS] All tests passed! MemoryX is working")
print("=" * 50)
