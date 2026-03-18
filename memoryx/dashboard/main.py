# -*- coding: utf-8 -*-
"""
MemoryX Dashboard - 多语言 + 统计
"""
import os, json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="MemoryX Dashboard")

# 完整语言配置
LANG = {
    "zh_CN": {
        "title": "MemoryX 仪表盘", "subtitle": "AI Agent 记忆管理系统",
        "tab_stats": "统计", "tab_memories": "记忆", "tab_add": "添加", "tab_search": "搜索",
        "tab_backup": "备份", "tab_settings": "设置",
        "today": "今日", "week": "近7天", "month": "近30天", "total": "累计",
        "queries": "查询", "tokens": "节省Token", "found": "找到", "added": "新增",
        "avg_time": "平均耗时", "days": "使用天数", "memories": "记忆数", "size": "存储大小", "dim": "向量维度"
    },
    "zh_TW": {
        "title": "MemoryX 儀表盤", "subtitle": "AI Agent 記憶管理系統",
        "tab_stats": "統計", "tab_memories": "記憶", "tab_add": "添加", "tab_search": "搜索",
        "tab_backup": "備份", "tab_settings": "設置",
        "today": "今日", "week": "近7天", "month": "近30天", "total": "累計",
        "queries": "查詢", "tokens": "節省Token", "found": "找到", "added": "新增",
        "avg_time": "平均耗時", "days": "天數", "memories": "記憶數", "size": "存儲大小", "dim": "向量維度"
    },
    "en": {
        "title": "MemoryX Dashboard", "subtitle": "AI Agent Memory System",
        "tab_stats": "Stats", "tab_memories": "Memories", "tab_add": "Add", "tab_search": "Search",
        "tab_backup": "Backup", "tab_settings": "Settings",
        "today": "Today", "week": "7 Days", "month": "30 Days", "total": "Total",
        "queries": "Queries", "tokens": "Tokens Saved", "found": "Found", "added": "Added",
        "avg_time": "Avg Time", "days": "Days", "memories": "Memories", "size": "Size", "dim": "Dim"
    },
    "es": {
        "title": "MemoryX Panel", "subtitle": "Sistema de Memoria AI",
        "tab_stats": "Estadisticas", "tab_memories": "Recuerdos", "tab_add": "Agregar", "tab_search": "Buscar",
        "tab_backup": "Respaldo", "tab_settings": "Config",
        "today": "Hoy", "week": "7 Dias", "month": "30 Dias", "total": "Total",
        "queries": "Consultas", "tokens": "Tokens Ahorrados", "found": "Encontrados", "added": "Agregados",
        "avg_time": "Tiempo Prom", "days": "Dias", "memories": "Recuerdos", "size": "Tamano", "dim": "Dim"
    },
    "pt": {
        "title": "MemoryX Painel", "subtitle": "Sistema de Memoria AI",
        "tab_stats": "Estatisticas", "tab_memories": "Memorias", "tab_add": "Adicionar", "tab_search": "Buscar",
        "tab_backup": "Backup", "tab_settings": "Config",
        "today": "Hoje", "week": "7 Dias", "month": "30 Dias", "total": "Total",
        "queries": "Consultas", "tokens": "Tokens Economizados", "found": "Encontrados", "added": "Adicionados",
        "avg_time": "Tempo Medio", "days": "Dias", "memories": "Memorias", "size": "Tamanho", "dim": "Dim"
    },
    "de": {
        "title": "MemoryX Dashboard", "subtitle": "AI Agent Speichersystem",
        "tab_stats": "Statistiken", "tab_memories": "Erinnerungen", "tab_add": "Hinzufugen", "tab_search": "Suchen",
        "tab_backup": "Sicherung", "tab_settings": "Einstellungen",
        "today": "Heute", "week": "7 Tage", "month": "30 Tage", "total": "Gesamt",
        "queries": "Abfragen", "tokens": "Gesparrt", "found": "Gefunden", "added": "Hinzugefugt",
        "avg_time": "Durchschn Zeit", "days": "Tage", "memories": "Erinnerungen", "size": "Grosse", "dim": "Dim"
    }
}

# 语言选项
LANG_OPTIONS = [
    ("zh_CN", "简体中文"),
    ("zh_TW", "繁體中文"),
    ("en", "English"),
    ("es", "Español"),
    ("pt", "Português"),
    ("de", "Deutsch")
]


def get_html(lang="zh_CN"):
    t = LANG.get(lang, LANG["zh_CN"])
    lang_opts = "".join([f'<option value="{k}" {"selected" if k==lang else ""}>{v}</option>' for k,v in LANG_OPTIONS])
    
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.08); text-align: center; }}
        .stat-card h3 {{ font-size: 14px; color: #666; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; color: #333; }}
        .section {{ background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
        .tabs {{ display: flex; border-bottom: 1px solid #ddd; margin-bottom: 20px; }}
        .tab {{ padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent; }}
        .tab.active {{ border-bottom-color: #667eea; color: #667eea; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div><h1>{t['title']}</h1><p>{t['subtitle']}</p></div>
            <select onchange="window.location.href='?lang='+this.value">{lang_opts}</select>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="tab('stats')">{t['tab_stats']}</div>
            <div class="tab" onclick="tab('mem')">{t['tab_memories']}</div>
            <div class="tab" onclick="tab('add')">{t['tab_add']}</div>
            <div class="tab" onclick="tab('search')">{t['tab_search']}</div>
        </div>
        
        <div id="stats" class="tab-content active">
            <div class="section">
                <h2>{t['tab_stats']}</h2>
                
                <h3>{t['today']}</h3>
                <div class="stats">
                    <div class="stat-card"><h3>{t['queries']}</h3><div class="value" id="todayQueries">-</div></div>
                    <div class="stat-card"><h3>{t['tokens']}</h3><div class="value" id="todayTokens">-</div></div>
                    <div class="stat-card"><h3>{t['found']}</h3><div class="value" id="todayFound">-</div></div>
                    <div class="stat-card"><h3>{t['added']}</h3><div class="value" id="todayAdded">-</div></div>
                </div>
                
                <h3>{t['week']}</h3>
                <div class="stats">
                    <div class="stat-card"><h3>{t['queries']}</h3><div class="value" id="weekQueries">-</div></div>
                    <div class="stat-card"><h3>{t['tokens']}</h3><div class="value" id="weekTokens">-</div></div>
                    <div class="stat-card"><h3>{t['found']}</h3><div class="value" id="weekFound">-</div></div>
                </div>
                
                <h3>{t['month']}</h3>
                <div class="stats">
                    <div class="stat-card"><h3>{t['queries']}</h3><div class="value" id="monthQueries">-</div></div>
                    <div class="stat-card"><h3>{t['tokens']}</h3><div class="value" id="monthTokens">-</div></div>
                    <div class="stat-card"><h3>{t['found']}</h3><div class="value" id="monthFound">-</div></div>
                </div>
                
                <h3>{t['total']}</h3>
                <div class="stats">
                    <div class="stat-card"><h3>{t['queries']}</h3><div class="value" id="totalQueries">-</div></div>
                    <div class="stat-card"><h3>{t['tokens']}</h3><div class="value" id="totalTokens">-</div></div>
                    <div class="stat-card"><h3>{t['days']}</h3><div class="value" id="daysUsed">-</div></div>
                    <div class="stat-card"><h3>{t['memories']}</h3><div class="value" id="totalMem">-</div></div>
                </div>
            </div>
        </div>
        
        <div id="mem" class="tab-content">
            <div class="section"><h2>{t['tab_memories']}</h2>
                <div style="margin-bottom:15px">
                    <input id="uid" placeholder="User ID" style="padding:8px;border:1px solid #ddd;border-radius:6px">
                    <button onclick="load()" style="padding:8px 16px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer">{t['tab_search']}</button>
                </div>
                <div id="memList"></div>
            </div>
        </div>
        
        <div id="add" class="tab-content">
            <div class="section">
                <h2>{t['tab_add']}</h2>
                <form id="addf">
                    <input id="auid" placeholder="User ID" required style="width:100%;padding:10px;margin-bottom:10px;border:1px solid #ddd;border-radius:6px">
                    <textarea id="acont" placeholder="记忆内容" required rows="4" style="width:100%;padding:10px;margin-bottom:10px;border:1px solid #ddd;border-radius:6px"></textarea>
                    <button type="submit" style="padding:10px 20px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer">{t['tab_add']}</button>
                </form>
                <div id="amsg"></div>
            </div>
        </div>
        
        <div id="search" class="tab-content">
            <div class="section">
                <h2>{t['tab_search']}</h2>
                <input id="sq" placeholder="搜索内容" style="padding:10px;border:1px solid #ddd;border-radius:6px;width:100%;margin-bottom:10px">
                <button onclick="doSearch()" style="padding:10px 20px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer">{t['tab_search']}</button>
                <div id="sres" style="margin-top:15px"></div>
            </div>
        </div>
    </div>
    <script>
    const A='/api';
    function tab(x){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));event.target.classList.add('active');document.getElementById(x).classList.add('active');if(x==='stats')loadStats();if(x==='mem')load();}}
    async function loadStats(){{
        const r=await fetch(A+'/stats/all');const d=await r.json();
        // Today
        document.getElementById('todayQueries').textContent=d.today.queries||0;
        document.getElementById('todayTokens').textContent=(d.today.tokens_saved||0).toLocaleString();
        document.getElementById('todayFound').textContent=d.today.memories_found||0;
        document.getElementById('todayAdded').textContent=d.today.memories_added||0;
        // Week
        document.getElementById('weekQueries').textContent=d.week.queries||0;
        document.getElementById('weekTokens').textContent=(d.week.tokens_saved||0).toLocaleString();
        document.getElementById('weekFound').textContent=d.week.memories_found||0;
        // Month
        document.getElementById('monthQueries').textContent=d.month.queries||0;
        document.getElementById('monthTokens').textContent=(d.month.tokens_saved||0).toLocaleString();
        document.getElementById('monthFound').textContent=d.month.memories_found||0;
        // Total
        document.getElementById('totalQueries').textContent=d.total.queries||0;
        document.getElementById('totalTokens').textContent=(d.total.tokens_saved||0).toLocaleString();
        document.getElementById('daysUsed').textContent=d.total.days||0;
        document.getElementById('totalMem').textContent=d.memories||0;
    }}
    async function load(){{
        const u=document.getElementById('uid').value||'xiao_cao_ye';
        const r=await fetch(A+'/memory?user_id='+encodeURIComponent(u));
        const d=await r.json();
        document.getElementById('memList').innerHTML=d.memories.length?d.memories.map(m=>`<div style="padding:10px;border-bottom:1px solid #eee"><b>${{m.level}}</b>: ${{(m.content||'').substring(0,50)}}...</div>`).join(''):'暂无数据';
    }}
    document.getElementById('addf').onsubmit=async e=>{{e.preventDefault();
        const r=await fetch(A+'/memory',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:document.getElementById('auid').value||'xiao_cao_ye',content:document.getElementById('acont').value,level:'user'}})}});
        const d=await r.json();
        document.getElementById('amsg').innerHTML=d.success?'<span style="color:green">成功!</span>':'<span style="color:red">失败</span>';
    }};
    async function doSearch(){{
        const q=document.getElementById('sq').value;
        const r=await fetch(A+'/memory/search',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{query:q,user_id:'xiao_cao_ye',limit:5}})}});
        const d=await r.json();
        document.getElementById('sres').innerHTML=d.results&&d.results.length?d.results.map(r=>`<div style="background:#f9f9f9;padding:10px;margin-bottom:10px;border-radius:8px"><b>${{r.id}}</b><p>${{r.content||''}}</p><small>${{(r.score||0).toFixed(3)}}</small></div>`).join(''):'无结果';
    }};
    loadStats();
    </script>
</body>
</html>"""


@app.get("/")
async def dashboard(request: Request):
    lang = request.query_params.get("lang", "zh_CN")
    return HTMLResponse(get_html(lang))


# ============ API ============

@app.get("/api/stats/all")
async def all_stats():
    """获取所有统计"""
    from memoryx.stats import get_today_stats, get_total_stats
    from memoryx.stats import load_daily_stats
    from datetime import datetime, timedelta
    
    # Today
    today = get_today_stats()
    
    # Week (last 7 days)
    week_stats = load_daily_stats()
    week = {"queries": 0, "tokens_saved": 0, "memories_found": 0, "memories_added": 0}
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if day in week_stats:
            d = week_stats[day]
            week["queries"] += d.get("queries", 0)
            week["tokens_saved"] += d.get("tokens_saved", 0)
            week["memories_found"] += d.get("memories_found", 0)
            week["memories_added"] += d.get("memories_added", 0)
    
    # Month (last 30 days)
    month = {"queries": 0, "tokens_saved": 0, "memories_found": 0, "memories_added": 0}
    for i in range(30):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        if day in week_stats:
            d = week_stats[day]
            month["queries"] += d.get("queries", 0)
            month["tokens_saved"] += d.get("tokens_saved", 0)
            month["memories_found"] += d.get("memories_found", 0)
            month["memories_added"] += d.get("memories_added", 0)
    
    # Total
    total = get_total_stats()
    
    # Memory count
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    stats = memory.get_stats()
    memory.close()
    
    return {
        "today": today,
        "week": week,
        "month": month,
        "total": {"queries": total.get("total_queries", 0), "tokens_saved": total.get("total_tokens_saved", 0), "days": total.get("days_used", 0)},
        "memories": stats.get("total_memories", 0)
    }


@app.get("/api/memory")
async def list_memories(user_id: str = None):
    from memoryx.core.config import Config
    from memoryx.core.storage import StorageManager
    config = Config()
    storage = StorageManager(config)
    memories = storage.get_by_user(user_id or "", limit=100)
    return {"memories": [m.to_dict() for m in memories]}


@app.post("/api/memory")
async def add_memory(req: Request):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    from memoryx.core.models import MemoryLevel
    data = await req.json()
    config = Config()
    memory = MemoryX(config)
    try:
        mem = memory.add(user_id=data.get("user_id", "main"), content=data.get("content", ""), level=MemoryLevel.USER)
        from memoryx.stats import record_add_memory
        record_add_memory()
        return {"success": True, "memory": mem.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/memory/search")
async def search_memory(req: Request):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    data = await req.json()
    config = Config()
    memory = MemoryX(config)
    results = memory.search(user_id=data.get("user_id", "main"), query=data.get("query", ""), limit=data.get("limit", 5))
    from memoryx.core.storage import StorageManager
    storage = StorageManager(config)
    enriched = []
    for r in results:
        mem = storage.get(r['id'])
        if mem:
            enriched.append({'id': r['id'], 'score': r.get('score', 0), 'content': mem.content})
    from memoryx.stats import record_query
    record_query(memories_found=len(enriched))
    return {"results": enriched}


def run_dashboard(host="0.0.0.0", port=None):
    import uvicorn, os
    if port is None:
        port = int(os.getenv("MEMORYX_DASHBOARD_PORT", "19876"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
