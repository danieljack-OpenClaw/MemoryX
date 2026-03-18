# -*- coding: utf-8 -*-
"""
MemoryX 预热脚本
在 OpenClaw 启动时自动运行，加快首次查询速度
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, 'C:/Users/Yijiayi/.openclaw/projects/MemoryX')

print("[MemoryX] 预热开始...")

start = time.time()

# 1. 导入并初始化 MemoryX
from memoryx.quick import _get_memoryx, quick_recall

print("[MemoryX] 初始化模型...")
mx = _get_memoryx()

if mx:
    # 2. 执行一次空查询来预热
    print("[MemoryX] 预热查询...")
    result = quick_recall("测试", "xiao_cao_ye")
    
    elapsed = time.time() - start
    
    if result.get("success"):
        print(f"[MemoryX] 预热完成! 耗时: {elapsed:.2f}s")
        print(f"[MemoryX] 模型已就绪，后续查询将使用缓存")
    else:
        print(f"[MemoryX] 预热失败: {result.get('error')}")
else:
    print("[MemoryX] 初始化失败")
