# -*- coding: utf-8 -*-
"""Test 90% compression"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
os.environ["OPENAI_API_KEY"] = ""
sys.path.insert(0, '.')

from pathlib import Path
from memoryx.core.config import Config
from memoryx.core.memory import MemoryX, MemoryLevel

print("[TEST] 90% Token Compression Test")
print("=" * 50)

config = Config()
config.storage_path = Path(".test_90")
config.max_context_tokens = 500
memory = MemoryX(config)

# Add test memories
memories = [
    "用户是一佳一AI助手的CEO，负责跨境电商业务，包括独立站运营、海外广告投放、社交媒体营销等多个板块，业务范围覆盖欧美市场，当前核心目标是实现跨境收单日均100万美元的收入目标",
    "用户偏好简洁的沟通风格，每次回复控制在3句话以内，重点突出结论和行动项",
    "当前项目是开发反向海淘独立站，主要销售球鞋品类，目标市场是美国和欧洲",
    "本月核心KPI是实现日均1000单，每单平均客单价50美元，转化率目标3%以上",
    "用户之前尝试过Facebook广告投放测试，但因为选品和受众定位问题ROI较低",
    "根据竞品分析显示，cnfsans.com是当前最大的反向海淘平台，月流量接近500万",
    "用户偏好的产品风格是简约大方，配色以蓝色和黑色为主",
    "物流方案采用国内集货直发模式，海外使用本地快递派送，预计时效7-15天",
    "支付方式主要支持Visa、MasterCard、AMEX等国际信用卡以及PayPal等电子钱包",
    "供应商位于广东东莞地区，之前合作过的工厂产品质量稳定，交货准时",
]

for c in memories:
    memory.add(user_id="test", content=c, level=MemoryLevel.USER)

original_tokens = sum(memory.compressor.estimate_tokens(c) for c in memories)
print(f"Original: {original_tokens} tokens")

# Test different compression levels
for target_pct in [0.5, 0.3, 0.2, 0.1]:
    target = int(original_tokens * target_pct)
    context = memory.get_context(user_id="test", max_tokens=target)
    compressed = memory.compressor.estimate_tokens(context)
    savings = (1 - compressed / original_tokens) * 100 if original_tokens > 0 else 0
    print(f"Target {int(target_pct*100)}% -> Compressed: {compressed} tokens, Savings: {savings:.1f}%")

import shutil
shutil.rmtree(".test_90", ignore_errors=True)

print("\n[DONE]")
