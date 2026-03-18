# -*- coding: utf-8 -*-
"""
MemoryX - 下一代 AI Agent 记忆系统
整合 mem0 + MemOS + Evolver 的优点
"""

__version__ = "0.1.0"
__author__ = "MemoryX Team"

from .core.memory import MemoryX
from .core.config import Config

__all__ = ["MemoryX", "Config"]
