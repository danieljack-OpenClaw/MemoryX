# -*- coding: utf-8 -*-
"""Test multilingual embeddings"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
sys.path.insert(0, '.')

from pathlib import Path
from memoryx.core.config import Config
from memoryx.core.search import SemanticSearch
import numpy as np

print("[TEST] Multilingual Embeddings")
print("=" * 50)

config = Config()
config.storage_path = Path(".test_multi")
search = SemanticSearch(config)

# Test Chinese pairs
pairs = [
    ("跨境电商", "海外销售", "high"),
    ("用户喜欢蓝色", "什么颜色偏好", "high"),
    ("Facebook广告", "广告投放", "high"),
    ("机器学习", "天气预测", "low"),
    ("电子商务", "烹饪食谱", "low"),
    ("市场营销", "编程开发", "low"),
]

high_ok = low_ok = 0
for t1, t2, exp in pairs:
    s = np.dot(search.encode(t1), search.encode(t2))
    ok = (exp == "high" and s > 0.5) or (exp == "low" and s < 0.5)
    if exp == "high":
        high_ok += int(s > 0.5)
    else:
        low_ok += int(s < 0.5)
    print(f"  {'✓' if ok else '✗'} {t1} vs {t2} = {s:.3f}")

acc = (high_ok + low_ok) / len(pairs) * 100
print(f"\n  Accuracy: {acc:.0f}%")

import shutil
shutil.rmtree(".test_multi", ignore_errors=True)
print("\n[DONE]")
