# -*- coding: utf-8 -*-
"""
MemoryX 自动集成 - 每次回复自动调用
在 AI 回复前自动执行，无需手动调用
"""
import sys
from pathlib import Path

# 添加路径
_proj_path = Path(__file__).parent.parent.parent
if str(_proj_path) not in sys.path:
    sys.path.insert(0, str(_proj_path))

# 预加载 MemoryX
def _warmup():
    """预热 MemoryX，加快首次调用"""
    try:
        from memoryx.quick import _get_memoryx, quick_recall
        mx = _get_memoryx()
        if mx:
            # 执行一次预热查询
            quick_recall("初始化", "xiao_cao_ye")
            print("[MemoryX] 自动集成已就绪")
    except Exception as e:
        print(f"[MemoryX] 预热失败: {e}")

# 启动时自动预热
_warmup()

# 导出主要函数
from memoryx.quick import (
    quick_recall as recall,
    quick_record as record, 
    process,
    get_report,
    get_stats
)

__all__ = ["recall", "record", "process", "get_report", "get_stats"]
