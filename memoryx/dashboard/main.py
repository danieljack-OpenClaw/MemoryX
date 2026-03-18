# -*- coding: utf-8 -*-
"""
MemoryX Web Dashboard - 完整版 (登录 + 多语言 + Agent选择)
"""
import os
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="MemoryX Dashboard")

# ============ 配置 ============
DEFAULT_LANG = "zh_CN"
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin123"

# 语言配置
LANGUAGES = {
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文", 
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "de": "Deutsch"
}

# 翻译 - 完整版
T = {
    "zh_CN": {
        "title": "MemoryX 仪表盘",
        "subtitle": "AI Agent 记忆管理系统",
        "login_title": "MemoryX 登录",
        "username": "用户名",
        "password": "密码",
        "login": "登录",
        "logout": "退出",
        "total_memories": "总记忆数",
        "storage_size": "存储大小",
        "vector_dim": "向量维度",
        "tab_memories": "记忆管理",
        "tab_add": "添加记忆",
        "tab_search": "搜索",
        "tab_backup": "备份同步",
        "tab_settings": "设置",
        "user_id": "用户ID",
        "content": "记忆内容",
        "level": "层级",
        "submit": "提交",
        "search": "搜索",
        "backup": "备份",
        "sync_cloud": "云同步",
        "refresh": "刷新",
        "delete": "删除",
        "confirm_delete": "确定删除?",
        "no_data": "暂无数据",
        "similarity": "相似度",
        "created_at": "创建时间",
        "save": "保存",
        "language": "语言",
        "select_agent": "选择 Agent",
        "cloud_settings": "云端设置",
        "enabled": "已启用",
        "disabled": "已禁用",
        "success": "成功",
        "error": "错误",
        "invalid_login": "用户名或密码错误",
    },
    "zh_TW": {
        "title": "MemoryX 儀表盤",
        "subtitle": "AI Agent 記憶管理系統",
        "login_title": "MemoryX 登入",
        "username": "用戶名",
        "password": "密碼",
        "login": "登入",
        "logout": "登出",
        "total_memories": "總記憶數",
        "storage_size": "存儲大小",
        "vector_dim": "向量維度",
        "tab_memories": "記憶管理",
        "tab_add": "添加記憶",
        "tab_search": "搜索",
        "tab_backup": "備份同步",
        "tab_settings": "設置",
        "user_id": "用戶ID",
        "content": "記憶內容",
        "level": "層級",
        "submit": "提交",
        "search": "搜索",
        "backup": "備份",
        "sync_cloud": "雲同步",
        "refresh": "刷新",
        "delete": "刪除",
        "confirm_delete": "確認刪除?",
        "no_data": "暫無數據",
        "similarity": "相似度",
        "created_at": "創建時間",
        "save": "保存",
        "language": "語言",
        "select_agent": "選擇 Agent",
        "cloud_settings": "雲端設置",
        "enabled": "已啟用",
        "disabled": "已禁用",
        "success": "成功",
        "error": "錯誤",
        "invalid_login": "用戶名或密碼錯誤",
    },
    "en": {
        "title": "MemoryX Dashboard",
        "subtitle": "AI Agent Memory Management",
        "login_title": "MemoryX Login",
        "username": "Username",
        "password": "Password",
        "login": "Login",
        "logout": "Logout",
        "total_memories": "Total Memories",
        "storage_size": "Storage Size",
        "vector_dim": "Vector Dim",
        "tab_memories": "Memories",
        "tab_add": "Add Memory",
        "tab_search": "Search",
        "tab_backup": "Backup",
        "tab_settings": "Settings",
        "user_id": "User ID",
        "content": "Content",
        "level": "Level",
        "submit": "Submit",
        "search": "Search",
        "backup": "Backup",
        "sync_cloud": "Cloud Sync",
        "refresh": "Refresh",
        "delete": "Delete",
        "confirm_delete": "Confirm delete?",
        "no_data": "No data",
        "similarity": "Similarity",
        "created_at": "Created",
        "save": "Save",
        "language": "Language",
        "select_agent": "Select Agent",
        "cloud_settings": "Cloud Settings",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "success": "Success",
        "error": "Error",
        "invalid_login": "Invalid username or password",
    }
}


def get_trans(lang: str) -> dict:
    """获取翻译"""
    return T.get(lang, T["zh_CN"])


def get_agents() -> list:
    """获取 Agent 列表"""
    agents = [
        {"id": "main", "name": "main (主Agent)", "users": [
            {"id": "xiao_cao_ye", "name": "小草爷"},
            {"id": "main", "name": "main"}
        ]}
    ]
    
    # 尝试读取其他 agents
    agents_dir = Path(os.path.expanduser("~/.openclaw/agents"))
    if agents_dir.exists():
        for d in agents_dir.iterdir():
            if d.is_dir() and d.name not in ["main"] and not d.name.startswith('_'):
                agents.append({
                    "id": d.name, 
                    "name": d.name,
                    "users": [{"id": d.name, "name": d.name}]
                })
    
    return agents


def get_users_for_agent(agent_id: str) -> list:
    """获取指定 Agent 下的用户列表"""
    for agent in get_agents():
        if agent["id"] == agent_id:
            return agent.get("users", [{"id": agent_id, "name": agent_id}])
    return [{"id": agent_id, "name": agent_id}]


def get_html(lang: str = "zh_CN", t: dict = None, error: str = "") -> str:
    """生成完整 HTML"""
    if t is None:
        t = get_trans(lang)
    
    # 语言选项
    lang_opts = "".join([
        f'<option value="{k}" {"selected" if k == lang else ""}>{v}</option>'
        for k, v in LANGUAGES.items()
    ])
    
    # Agent 和 User 选项 - 两级选择
    agents = get_agents()
    agent_opts = ""
    for a in agents:
        agent_opts += f'<option value="{a["id"]}">{a["name"]}</option>'
    
    # 默认选第一个 agent
    default_agent = agents[0]["id"] if agents else "main"
    default_users = agents[0]["users"] if agents else [{"id": "xiao_cao_ye", "name": "小草爷"}]
    user_opts = "".join([f'<option value="{u["id"]}">{u["name"]}</option>' for u in default_users])
    
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }}
        .header h1 {{ font-size: 24px; }}
        .header .right {{ display: flex; gap: 10px; align-items: center; }}
        .header select, .header button {{ padding: 8px 12px; border-radius: 6px; border: none; cursor: pointer; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .stat-card h3 {{ font-size: 14px; color: #666; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .section {{ background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .section h2 {{ font-size: 18px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: 500; }}
        .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }}
        .btn {{ padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }}
        .btn-primary {{ background: #667eea; color: white; }}
        .btn-success {{ background: #10b981; color: white; }}
        .btn-danger {{ background: #ef4444; color: white; }}
        .tabs {{ display: flex; border-bottom: 1px solid #ddd; margin-bottom: 20px; flex-wrap: wrap; }}
        .tab {{ padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent; }}
        .tab.active {{ border-bottom-color: #667eea; color: #667eea; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .message {{ padding: 12px; border-radius: 6px; margin-bottom: 10px; }}
        .message-success {{ background: #d1fae5; color: #065f46; }}
        .message-error {{ background: #fee2e2; color: #991b1b; }}
        .search-box {{ display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }}
        .search-box input {{ flex: 1; min-width: 150px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        
        /* Login */
        .login-page {{ display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea, #764ba2); }}
        .login-box {{ background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }}
        .login-box h2 {{ text-align: center; margin-bottom: 30px; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div><h1>🧠 {t['title']}</h1><p>{t['subtitle']}</p></div>
            <div class="right">
                <select id="agentSelect" onchange="changeAgent(this.value)">
                    {agent_opts}
                </select>
                <select id="userSelect" onchange="changeUser(this.value)">
                    {user_opts}
                </select>
                <select id="lang" onchange="changeLang(this.value)">
                    {lang_opts}
                </select>
                <button class="btn" style="background:rgba(255,255,255,0.2);color:white" onclick="logout()">{t['logout']}</button>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card"><h3>{t['total_memories']}</h3><div class="value" id="total">-</div></div>
            <div class="stat-card"><h3>{t['storage_size']}</h3><div class="value" id="size">-</div></div>
            <div class="stat-card"><h3>{t['vector_dim']}</h3><div class="value" id="dim">-</div></div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="tab('mem')">{t['tab_memories']}</div>
            <div class="tab" onclick="tab('add')">{t['tab_add']}</div>
            <div class="tab" onclick="tab('search')">{t['tab_search']}</div>
            <div class="tab" onclick="tab('backup')">{t['tab_backup']}</div>
            <div class="tab" onclick="tab('settings')">{t['tab_settings']}</div>
        </div>
        
        <div id="mem" class="tab-content active">
            <div class="section">
                <h2>{t['tab_memories']}</h2>
                <div class="search-box">
                    <input id="uid" placeholder="{t['user_id']}">
                    <button class="btn btn-primary" onclick="load()">{t['refresh']}</button>
                </div>
                <table><thead><tr><th>ID</th><th>{t['level']}</th><th>{t['content']}</th><th>{t['created_at']}</th><th></th></tr></thead><tbody id="tbody"></tbody></table>
            </div>
        </div>
        
        <div id="add" class="tab-content">
            <div class="section">
                <h2>{t['tab_add']}</h2>
                <form id="addf">
                    <div class="form-group"><label>{t['user_id']}</label><input id="auid" required></div>
                    <div class="form-group"><label>{t['content']}</label><textarea id="acont" required rows="4"></textarea></div>
                    <div class="form-group"><label>{t['level']}</label><select id="alvl">
                        <option value="user">User</option><option value="session">Session</option><option value="project">Project</option>
                    </select></div>
                    <button class="btn btn-primary">{t['submit']}</button>
                </form>
                <div id="amsg"></div>
            </div>
        </div>
        
        <div id="search" class="tab-content">
            <div class="section">
                <h2>{t['tab_search']}</h2>
                <div class="search-box">
                    <input id="sq" placeholder="{t['content']}">
                    <input id="su" placeholder="{t['user_id']}">
                    <button class="btn btn-primary" onclick="doSearch()">{t['search']}</button>
                </div>
                <div id="sres"></div>
            </div>
        </div>
        
        <div id="backup" class="tab-content">
            <div class="section">
                <h2>{t['tab_backup']}</h2>
                <button class="btn btn-primary" onclick="backup()">{t['backup']}</button>
                <button class="btn btn-success" onclick="sync()">{t['sync_cloud']}</button>
                <div id="bmsg"></div>
            </div>
        </div>
        
        <div id="settings" class="tab-content">
            <div class="section">
                <h2>{t['cloud_settings']}</h2>
                <div class="form-group">
                    <label>{t['language']}</label>
                    <select id="settingsLang" onchange="changeLang(this.value)">
                        {lang_opts}
                    </select>
                </div>
            </div>
        </div>
        
        <div class="footer">MemoryX v1.0.2</div>
    </div>
    
    <script>
    const A='/api';
    const DEFAULT_AGENT = '{default_agent}';
    const AGENTS = {json.dumps(agents)};
    
    function tab(x){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));event.target.classList.add('active');document.getElementById(x==='mem'?'mem':x).classList.add('active');if(x==='mem')load();}}
    function changeLang(l){{window.location.href='?lang='+l;}}
    function changeAgent(a){{
        localStorage.setItem('memoryx_agent',a);
        // 更新用户下拉
        const agent = AGENTS.find(x=>x.id===a);
        if(agent){{
            const userSel = document.getElementById('userSelect');
            userSel.innerHTML = agent.users.map(u=>'<option value="'+u.id+'">'+u.name+'</option>').join('');
        }}
        load();
    }}
    function changeUser(u){{localStorage.setItem('memoryx_user',u);load();}}
    function logout(){{window.location.href='/?logout=1';}}
    
    async function load(){{
        const agent = localStorage.getItem('memoryx_agent') || document.getElementById('agentSelect')?.value || DEFAULT_AGENT;
        const user = localStorage.getItem('memoryx_user') || document.getElementById('userSelect')?.value || agent;
        const u = document.getElementById('uid').value || user;
        const r = await fetch(A+'/memory?user_id='+encodeURIComponent(u));
        const d = await r.json();
        const tb = document.getElementById('tbody');
        if(!d.memories.length){{tb.innerHTML='<tr><td colspan="5">{t["no_data"]}</td></tr>';return;}}
        tb.innerHTML = d.memories.map(m=>'<tr><td>'+m.id+'</td><td><span style="background:#e0e7ff;padding:2px 8px;border-radius:4px;font-size:12px">'+m.level+'</span></td><td>'+(m.content||'').substring(0,40)+'...</td><td>'+new Date(m.created_at).toLocaleDateString()+'</td><td><button class="btn btn-danger" style="padding:4px 8px" onclick="del(\\''+m.id+'\\')">{t["delete"]}</button></td></tr>').join('');
    }}
    async function stats(){{
        const r = await fetch(A+'/stats');
        const d = await r.json();
        document.getElementById('total').textContent = d.stats.total_memories;
        document.getElementById('size').textContent = (d.stats.storage_size/1024/1024).toFixed(2)+' MB';
        document.getElementById('dim').textContent = d.stats.vector_dim;
    }}
    document.getElementById('addf').onsubmit = async e => {{
        e.preventDefault();
        const agent = localStorage.getItem('memoryx_agent') || DEFAULT_AGENT;
        const r = await fetch(A+'/memory',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:document.getElementById('auid').value||agent,content:document.getElementById('acont').value,level:document.getElementById('alvl').value}})}});
        const d = await r.json();
        document.getElementById('amsg').innerHTML = d.success?'<div class="message message-success">success!</div>':'<div class="message message-error">'+d.error+'</div>';
        if(d.success){{document.getElementById('auid').value='';document.getElementById('acont').value='';stats();load();}}
    }};
    async function doSearch(){{
        const q = document.getElementById('sq').value;
        const u = document.getElementById('su').value || localStorage.getItem('memoryx_agent') || DEFAULT_AGENT;
        if(!q||!u){{alert('Need query and user');return;}}
        const r = await fetch(A+'/memory/search',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{query:q,user_id:u,limit:5}})}});
        const d = await r.json();
        document.getElementById('sres').innerHTML = d.results&&d.results.length?d.results.map(r=>'<div style="background:#f9f9f9;padding:15px;margin-bottom:10px;border-radius:8px"><b>'+r.id+'</b><p>'+(r.content||'')+'</p><small style="color:#666">similarity: '+(r.score||0).toFixed(3)+'</small></div>').join(''):'no_data';
    }};
    async function del(id){{if(!confirm('confirm_delete'))return;await fetch(A+'/memory/'+id,{{method:'DELETE'}});load();stats();}}
    async function backup(){{const r=await fetch(A+'/backup',{{method:'POST'}});const d=await r.json();document.getElementById('bmsg').innerHTML=d.backup_id?'<div class="message message-success">'+d.backup_id+'</div>':'';}};
    async function sync(){{const r=await fetch(A+'/cloud/sync',{{method:'POST'}});const d=await r.json();document.getElementById('bmsg').innerHTML=d.success?'<div class="message message-success">success</div>':'<div class="message message-error">'+d.error+'</div>';}};
    
    // Init
    stats();
    // Set agent from localStorage
    const savedAgent = localStorage.getItem('memoryx_agent');
    if(savedAgent && document.getElementById('agentSelect')){{document.getElementById('agentSelect').value = savedAgent;}}
    load();
    </script>
</body>
</html>"""


# ============ 路由 ============

@app.get("/")
async def dashboard(request: Request):
    lang = request.query_params.get("lang", DEFAULT_LANG)
    if lang not in LANGUAGES:
        lang = DEFAULT_LANG
    
    t = get_trans(lang)
    return HTMLResponse(get_html(lang, t))


# ============ API ============

@app.get("/api/stats")
async def get_stats():
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    stats = memory.get_stats()
    memory.close()
    return {"stats": stats}


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
        level_map = {"user": MemoryLevel.USER, "session": MemoryLevel.SESSION, "project": MemoryLevel.PROJECT}
        mem = memory.add(user_id=data.get("user_id", "main"), content=data.get("content", ""), level=level_map.get(data.get("level", "user"), MemoryLevel.USER))
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
            enriched.append({'id': r['id'], 'score': r.get('score', 0), 'content': mem.content, 'level': mem.level})
    return {"results": enriched}


@app.delete("/api/memory/{memory_id}")
async def delete_memory(memory_id: str):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    success = memory.delete(memory_id)
    memory.close()
    return {"success": success}


@app.post("/api/backup")
async def create_backup():
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    backup_id = memory.backup()
    memory.close()
    return {"backup_id": backup_id}


@app.post("/api/cloud/sync")
async def cloud_sync():
    from memoryx.core.config import Config
    from memoryx.core.storage import StorageManager
    config = Config()
    try:
        storage = StorageManager(config)
        result = storage.sync_all_to_cloud()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/agents")
async def list_agents():
    """获取 Agent 列表（带用户）"""
    agents = get_agents()
    return {"agents": agents, "default_agent": agents[0]["id"] if agents else "main"}


@app.get("/api/users/{agent_id}")
async def list_users(agent_id: str):
    """获取指定 Agent 下的用户列表"""
    users = get_users_for_agent(agent_id)
    return {"users": users}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ============ 启动 ============
def run_dashboard(host: str = "0.0.0.0", port: int = None):
    import uvicorn
    import os
    if port is None:
        port = int(os.getenv("MEMORYX_DASHBOARD_PORT", "19876"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
