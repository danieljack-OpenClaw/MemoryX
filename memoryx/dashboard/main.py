# -*- coding: utf-8 -*-
"""
MemoryX Dashboard with Stats
"""
import os, json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="MemoryX Dashboard")

# Language
LANG = {
    "zh_CN": {
        "title": "MemoryX 仪表盘", "subtitle": "AI Agent 记忆管理系统",
        "tab_stats": "统计", "tab_memories": "记忆", "tab_add": "添加", "tab_search": "搜索",
        "tab_backup": "备份", "tab_settings": "设置",
        "today_queries": "今日查询", "today_tokens": "节省Token", "today_found": "找到记忆", "today_added": "新增记忆",
        "total_stats": "累计统计", "total_queries": "总查询", "total_tokens": "总节省", "days_used": "使用天数",
        "total_memories": "总记忆数", "storage_size": "存储大小", "vector_dim": "向量维度"
    },
    "en": {
        "title": "MemoryX Dashboard", "subtitle": "AI Agent Memory",
        "tab_stats": "Stats", "tab_memories": "Memories", "tab_add": "Add", "tab_search": "Search",
        "tab_backup": "Backup", "tab_settings": "Settings",
        "today_queries": "Today Queries", "today_tokens": "Tokens Saved", "today_found": "Found", "today_added": "Added",
        "total_stats": "Total", "total_queries": "Total Queries", "total_tokens": "Total Saved", "days_used": "Days",
        "total_memories": "Total", "storage_size": "Size", "vector_dim": "Dim"
    }
}

def get_html(lang="zh_CN"):
    t = LANG.get(lang, LANG["zh_CN"])
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
        .stat-card gradient {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
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
            <div><h1>MemoryX</h1><p>{t['subtitle']}</p></div>
            <select onchange="window.location.href='?lang='+this.value">
                <option value="zh_CN" {"selected" if lang=="zh_CN" else ""}>简体中文</option>
                <option value="en" {"selected" if lang=="en" else ""}>English</option>
            </select>
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
                <div class="stats">
                    <div class="stat-card" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
                        <h3 style="color:rgba(255,255,255,0.8)">{t['today_queries']}</h3>
                        <div class="value" id="todayQueries">-</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #10b981, #059669); color: white;">
                        <h3 style="color:rgba(255,255,255,0.8)">{t['today_tokens']}</h3>
                        <div class="value" id="todayTokens">-</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white;">
                        <h3 style="color:rgba(255,255,255,0.8)">{t['today_found']}</h3>
                        <div class="value" id="todayFound">-</div>
                    </div>
                    <div class="stat-card" style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white;">
                        <h3 style="color:rgba(255,255,255,0.8)">{t['today_added']}</h3>
                        <div class="value" id="todayAdded">-</div>
                    </div>
                </div>
                <h3>{t['total_stats']}</h3>
                <div class="stats">
                    <div class="stat-card"><h3>{t['total_queries']}</h3><div class="value" id="totalQueries">-</div></div>
                    <div class="stat-card"><h3>{t['total_tokens']}</h3><div class="value" id="totalTokens">-</div></div>
                    <div class="stat-card"><h3>{t['days_used']}</h3><div class="value" id="daysUsed">-</div></div>
                    <div class="stat-card"><h3>{t['total_memories']}</h3><div class="value" id="totalMem">-</div></div>
                </div>
            </div>
        </div>
        
        <div id="mem" class="tab-content">
            <div class="section"><h2>{t['tab_memories']}</h2>
                <div style="margin-bottom:15px">
                    <input id="uid" placeholder="User ID" style="padding:8px;border:1px solid #ddd;border-radius:6px">
                    <button onclick="load()" style="padding:8px 16px;background:#667eea;color:white;border:none;border-radius:6px;cursor:pointer">刷新</button>
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
        const r=await fetch(A+'/stats/daily');const d=await r.json();
        document.getElementById('todayQueries').textContent=d.today.queries||0;
        document.getElementById('todayTokens').textContent=(d.today.tokens_saved||0).toLocaleString();
        document.getElementById('todayFound').textContent=d.today.memories_found||0;
        document.getElementById('todayAdded').textContent=d.today.memories_added||0;
        document.getElementById('totalQueries').textContent=d.total.total_queries||0;
        document.getElementById('totalTokens').textContent=(d.total.total_tokens_saved||0).toLocaleString();
        document.getElementById('daysUsed').textContent=d.total.days_used||0;
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


@app.get("/api/stats/daily")
async def daily_stats():
    from memoryx.stats import get_today_stats, get_total_stats
    return {"today": get_today_stats(), "total": get_total_stats()}


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
    from memoryx.core.storage import StorageManager
    data = await req.json()
    config = Config()
    memory = MemoryX(config)
    results = memory.search(user_id=data.get("user_id", "main"), query=data.get("query", ""), limit=data.get("limit", 5))
    storage = StorageManager(config)
    enriched = []
    for r in results:
        mem = storage.get(r['id'])
        if mem:
            enriched.append({'id': r['id'], 'score': r.get('score', 0), 'content': mem.content})
    from memoryx.stats import record_query
    record_query(memories_found=len(enriched))
    return {"results": enriched}


@app.get("/api/stats")
async def get_stats():
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    stats = memory.get_stats()
    memory.close()
    return {"stats": stats}


def run_dashboard(host="0.0.0.0", port=None):
    import uvicorn
    import os
    if port is None:
        port = int(os.getenv("MEMORYX_DASHBOARD_PORT", "19876"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
