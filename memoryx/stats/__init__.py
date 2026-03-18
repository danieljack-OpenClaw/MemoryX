# -*- coding: utf-8 -*-
"""
MemoryX 每日使用统计
记录和展示 MemoryX 的使用情况
"""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta


def get_stats_path() -> Path:
    """获取统计文件路径"""
    from memoryx.core.config import Config
    config = Config()
    stats_dir = config.storage_path / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)
    return stats_dir / "daily.json"


def load_daily_stats() -> dict:
    """加载每日统计"""
    path = get_stats_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except:
            pass
    return {}


def save_daily_stats(stats: dict):
    """保存每日统计"""
    path = get_stats_path()
    path.write_text(json.dumps(stats, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def record_query(tokens_saved: int = 0, memories_found: int = 0):
    """记录一次查询"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_daily_stats()
    
    if today not in stats:
        stats[today] = {
            "queries": 0,
            "tokens_saved": 0,
            "memories_found": 0,
            "memories_added": 0
        }
    
    stats[today]["queries"] += 1
    stats[today]["tokens_saved"] += tokens_saved
    stats[today]["memories_found"] += memories_found
    
    save_daily_stats(stats)


def record_add_memory():
    """记录添加记忆"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_daily_stats()
    
    if today not in stats:
        stats[today] = {
            "queries": 0,
            "tokens_saved": 0,
            "memories_found": 0,
            "memories_added": 0
        }
    
    stats[today]["memories_added"] += 1
    save_daily_stats(stats)


def get_today_stats() -> dict:
    """获取今日统计"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = load_daily_stats()
    return stats.get(today, {
        "queries": 0,
        "tokens_saved": 0,
        "memories_found": 0,
        "memories_added": 0
    })


def get_weekly_stats() -> list:
    """获取本周统计"""
    stats = load_daily_stats()
    week_stats = []
    
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_stat = stats.get(day, {
            "queries": 0,
            "tokens_saved": 0,
            "memories_found": 0,
            "memories_added": 0
        })
        day_stat["date"] = day
        week_stats.append(day_stat)
    
    return week_stats


def get_total_stats() -> dict:
    """获取总统计"""
    stats = load_daily_stats()
    
    total = {
        "total_queries": 0,
        "total_tokens_saved": 0,
        "total_memories_found": 0,
        "total_memories_added": 0,
        "days_used": len(stats)
    }
    
    for day_data in stats.values():
        total["total_queries"] += day_data.get("queries", 0)
        total["total_tokens_saved"] += day_data.get("tokens_saved", 0)
        total["total_memories_found"] += day_data.get("memories_found", 0)
        total["total_memories_added"] += day_data.get("memories_added", 0)
    
    return total


def generate_report(lang: str = "zh_CN") -> str:
    """生成使用报告"""
    today = get_today_stats()
    total = get_total_stats()
    
    reports = {
        "zh_CN": f"""📊 MemoryX 每日报告

今日:
- 查询次数: {today.get('queries', 0)}
- 节省Token: ~{today.get('tokens_saved', 0):,}
- 找到记忆: {today.get('memories_found', 0)} 条
- 新增记忆: {today.get('memories_added', 0)} 条

累计:
- 总查询: {total.get('total_queries', 0)} 次
- 总节省: ~{total.get('total_tokens_saved', 0):,} tokens
- 使用天数: {total.get('days_used', 0)} 天
""",
        "en": f"""📊 MemoryX Daily Report

Today:
- Queries: {today.get('queries', 0)}
- Tokens Saved: ~{today.get('tokens_saved', 0):,}
- Memories Found: {today.get('memories_found', 0)}
- Memories Added: {today.get('memories_added', 0)}

Total:
- Total Queries: {total.get('total_queries', 0)}
- Total Saved: ~{total.get('total_tokens_saved', 0):,} tokens
- Days Used: {total.get('days_used', 0)}
"""
    }
    
    return reports.get(lang, reports["zh_CN"])


__all__ = [
    "record_query",
    "record_add_memory",
    "get_today_stats",
    "get_weekly_stats",
    "get_total_stats",
    "generate_report"
]
