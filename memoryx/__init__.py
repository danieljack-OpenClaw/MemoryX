# -*- coding: utf-8 -*-
"""
MemoryX - 下一代 AI Agent 记忆系统
整合 mem0 + MemOS + Evolver 的优点

功能:
- 多层级记忆 (User/Session/Agent/Skill/Project)
- 语义搜索 (sentence-transformers)
- Token 压缩 (22%+ 压缩率)
- 知识图谱 (NetworkX)
- 多 Agent 支持
- 技能进化引擎 (GEP Protocol)
- 增量备份
- Web Dashboard
- 云端同步
- 快速自动化集成 (quick.py)
"""

__version__ = "1.0.4"
__author__ = "MemoryX Team"

# 核心
from .core.memory import MemoryX
from .core.config import Config

# 知识图谱
from .core.graph import GraphMemory, HybridSearch

# 多 Agent
from .core.multi_agent import MultiAgentManager

# 进化引擎
from .core.evolution import EvolutionEngine, GeneType

# 增量备份
from .core.backup import IncrementalBackup

# OpenClaw 集成
from .openclaw_integration import (
    auto_recall,
    auto_record,
    process_message,
    get_report,
    get_summary,
    get_stats,
    reset_stats,
    close
)

# 快速集成（每次回复自动调用）
from .quick import (
    quick_recall,
    quick_record,
    process as quick_process,
    get_report as quick_get_report,
    get_stats as quick_get_stats
)

__all__ = [
    # 核心
    "MemoryX",
    "Config",
    # 知识图谱
    "GraphMemory",
    "HybridSearch",
    # 多 Agent
    "MultiAgentManager",
    # 进化引擎
    "EvolutionEngine",
    "GeneType",
    # 增量备份
    "IncrementalBackup",
    # OpenClaw 集成
    "auto_recall",
    "auto_record",
    "process_message",
    "get_report",
    "get_summary",
    "get_stats",
    "reset_stats",
    "close",
    # 快速集成
    "quick_recall",
    "quick_record",
    "quick_process",
    "quick_get_report",
    "quick_get_stats"
]
