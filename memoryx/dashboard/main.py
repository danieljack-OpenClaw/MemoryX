# -*- coding: utf-8 -*-
"""
MemoryX Web Dashboard
"""
import os
import json
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


# Create app
app = FastAPI(title="MemoryX Dashboard", version="1.0.0")
templates = Jinja2Templates(directory=None)


# HTML Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MemoryX Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        
        /* Stats */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .stat-card h3 { font-size: 14px; color: #666; margin-bottom: 8px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #333; }
        
        /* Sections */
        .section { background: white; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .section h2 { font-size: 18px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        
        /* Forms */
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .form-group textarea { min-height: 100px; }
        
        /* Buttons */
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn:hover { opacity: 0.9; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { font-weight: 600; color: #666; font-size: 13px; }
        tr:hover { background: #f9f9f9; }
        
        /* Tabs */
        .tabs { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 20px; }
        .tab { padding: 12px 20px; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #667eea; color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Messages */
        .message { padding: 12px; border-radius: 6px; margin-bottom: 10px; }
        .message-success { background: #d1fae5; color: #065f46; }
        .message-error { background: #fee2e2; color: #991b1b; }
        
        /* Search */
        .search-box { display: flex; gap: 10px; margin-bottom: 15px; }
        .search-box input { flex: 1; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🧠 MemoryX Dashboard</h1>
            <p>AI Agent 记忆管理系统</p>
        </div>
        
        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <h3>总记忆数</h3>
                <div class="value" id="totalMemories">-</div>
            </div>
            <div class="stat-card">
                <h3>存储大小</h3>
                <div class="value" id="storageSize">-</div>
            </div>
            <div class="stat-card">
                <h3>向量维度</h3>
                <div class="value" id="vectorDim">-</div>
            </div>
            <div class="stat-card">
                <h3>用户数</h3>
                <div class="value" id="userCount">-</div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('memories')">记忆管理</div>
            <div class="tab" onclick="switchTab('add')">添加记忆</div>
            <div class="tab" onclick="switchTab('search')">搜索</div>
            <div class="tab" onclick="switchTab('backup')">备份同步</div>
            <div class="tab" onclick="switchTab('settings')">设置</div>
        </div>
        
        <!-- Memories Tab -->
        <div id="memories" class="tab-content active">
            <div class="section">
                <h2>📚 记忆列表</h2>
                <div class="search-box">
                    <input type="text" id="userIdFilter" placeholder="输入用户ID筛选...">
                    <button class="btn btn-primary" onclick="loadMemories()">刷新</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>层级</th>
                            <th>内容</th>
                            <th>创建时间</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="memoriesTable">
                        <tr><td colspan="5">加载中...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Add Tab -->
        <div id="add" class="tab-content">
            <div class="section">
                <h2>➕ 添加记忆</h2>
                <form id="addForm">
                    <div class="form-group">
                        <label>用户ID</label>
                        <input type="text" id="addUserId" placeholder="user_001" required>
                    </div>
                    <div class="form-group">
                        <label>记忆内容</label>
                        <textarea id="addContent" placeholder="要记忆的内容..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label>记忆层级</label>
                        <select id="addLevel">
                            <option value="user">用户 (永久)</option>
                            <option value="session">会话 (临时)</option>
                            <option value="project">项目</option>
                            <option value="agent">代理</option>
                            <option value="skill">技能</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">添加</button>
                </form>
                <div id="addMessage"></div>
            </div>
        </div>
        
        <!-- Search Tab -->
        <div id="search" class="tab-content">
            <div class="section">
                <h2>🔍 语义搜索</h2>
                <div class="search-box">
                    <input type="text" id="searchQuery" placeholder="输入搜索内容...">
                    <input type="text" id="searchUserId" placeholder="用户ID">
                    <button class="btn btn-primary" onclick="doSearch()">搜索</button>
                </div>
                <div id="searchResults"></div>
            </div>
        </div>
        
        <!-- Backup Tab -->
        <div id="backup" class="tab-content">
            <div class="section">
                <h2>💾 备份与同步</h2>
                <div class="form-group">
                    <button class="btn btn-primary" onclick="createBackup()">创建本地备份</button>
                    <button class="btn btn-success" onclick="syncToCloud()">同步到云端</button>
                    <button class="btn" onclick="loadBackups()">查看备份</button>
                </div>
                <div id="backupMessage"></div>
            </div>
        </div>
        
        <!-- Settings Tab -->
        <div id="settings" class="tab-content">
            <div class="section">
                <h2>⚙️ 系统设置</h2>
                <div class="form-group">
                    <label>存储路径</label>
                    <input type="text" id="settingStoragePath" disabled>
                </div>
                <div class="form-group">
                    <label>上下文最大Token数</label>
                    <input type="number" id="settingMaxTokens" value="4000">
                </div>
                <div class="form-group">
                    <label>自动备份</label>
                    <select id="settingAutoBackup">
                        <option value="true">启用</option>
                        <option value="false">禁用</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="saveSettings()">保存设置</button>
            </div>
        </div>
    </div>
    
    <script>
        const API_BASE = '/api';
        
        function switchTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.add('active');
            
            if (tabId === 'memories') loadMemories();
            if (tabId === 'backup') loadBackups();
        }
        
        // Load stats
        async function loadStats() {
            try {
                const res = await fetch(API_BASE + '/stats');
                const data = await res.json();
                document.getElementById('totalMemories').textContent = data.stats.total_memories;
                document.getElementById('storageSize').textContent = (data.stats.storage_size / 1024 / 1024).toFixed(2) + ' MB';
                document.getElementById('vectorDim').textContent = data.stats.vector_dim;
            } catch(e) { console.error(e); }
        }
        
        // Load memories
        async function loadMemories() {
            const userId = document.getElementById('userIdFilter').value;
            const url = userId ? API_BASE + '/memory?user_id=' + encodeURIComponent(userId) : API_BASE + '/memory';
            const res = await fetch(url);
            const data = await res.json();
            
            const tbody = document.getElementById('memoriesTable');
            if (data.memories.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5">暂无记忆</td></tr>';
                return;
            }
            
            tbody.innerHTML = data.memories.map(m => `
                <tr>
                    <td>${m.id}</td>
                    <td><span style="background:#e0e7ff;padding:2px 8px;border-radius:4px;font-size:12px">${m.level}</span></td>
                    <td>${m.content.substring(0, 50)}${m.content.length > 50 ? '...' : ''}</td>
                    <td>${new Date(m.created_at).toLocaleString()}</td>
                    <td><button class="btn btn-danger" style="padding:4px 8px;font-size:12px" onclick="deleteMemory('${m.id}')">删除</button></td>
                </tr>
            `).join('');
        }
        
        // Add memory
        document.getElementById('addForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                user_id: document.getElementById('addUserId').value,
                content: document.getElementById('addContent').value,
                level: document.getElementById('addLevel').value
            };
            
            const res = await fetch(API_BASE + '/memory', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            const msg = document.getElementById('addMessage');
            if (result.success) {
                msg.innerHTML = '<div class="message message-success">记忆添加成功！</div>';
                document.getElementById('addForm').reset();
                loadStats();
            } else {
                msg.innerHTML = '<div class="message message-error">添加失败：' + result.error + '</div>';
            }
        };
        
        // Search
        async function doSearch() {
            const query = document.getElementById('searchQuery').value;
            const userId = document.getElementById('searchUserId').value;
            
            if (!query || !userId) {
                alert('请输入搜索内容和用户ID');
                return;
            }
            
            const res = await fetch(API_BASE + '/memory/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query, user_id: userId, limit: 10})
            });
            
            const data = await res.json();
            const results = document.getElementById('searchResults');
            
            if (!data.results || data.results.length === 0) {
                results.innerHTML = '<div class="message">未找到相关记忆</div>';
                return;
            }
            
            results.innerHTML = data.results.map(r => `
                <div style="background:#f9f9f9;padding:15px;margin-bottom:10px;border-radius:8px">
                    <div style="font-weight:600;color:#667eea">${r.id}</div>
                    <div style="margin-top:5px">${r.content || ''}</div>
                    <div style="color:#666;font-size:12px;margin-top:5px">相似度: ${(r.score || 0).toFixed(3)}</div>
                </div>
            `).join('');
        }
        
        // Delete memory
        async function deleteMemory(id) {
            if (!confirm('确定删除?')) return;
            await fetch(API_BASE + '/memory/' + id, {method: 'DELETE'});
            loadMemories();
            loadStats();
        }
        
        // Backup
        async function createBackup() {
            const res = await fetch(API_BASE + '/backup', {method: 'POST'});
            const data = await res.json();
            document.getElementById('backupMessage').innerHTML = 
                '<div class="message message-success">备份创建成功: ' + data.backup_id + '</div>';
        }
        
        async function loadBackups() {
            const res = await fetch(API_BASE + '/backup');
            const data = await res.json();
            console.log('Backups:', data);
        }
        
        // Init
        loadStats();
    </script>
</body>
</html>
"""


# API Models
class AddMemoryRequest(BaseModel):
    user_id: str
    content: str
    level: str = "user"
    metadata: dict = None


class SearchRequest(BaseModel):
    query: str
    user_id: str
    limit: int = 5


# Mount static files
import tempfile
temp_dir = tempfile.mkdtemp()
dashboard_path = Path(temp_dir) / "index.html"
dashboard_path.write_text(DASHBOARD_HTML, encoding='utf-8')


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML


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
    from memoryx.core.memory import MemoryX
    
    config = Config()
    memory = MemoryX(config)
    
    from memoryx.core.storage import StorageManager
    storage = StorageManager(config)
    memories = storage.get_by_user(user_id or "", limit=100)
    
    return {"memories": [m.to_dict() for m in memories]}


@app.post("/api/memory")
async def add_memory(req: AddMemoryRequest):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    
    config = Config()
    memory = MemoryX(config)
    
    try:
        mem = memory.add(
            user_id=req.user_id,
            content=req.content,
            level=req.level,
            metadata=req.metadata
        )
        return {"success": True, "memory": mem.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/memory/search")
async def search_memory(req: SearchRequest):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    
    config = Config()
    memory = MemoryX(config)
    
    results = memory.search(
        user_id=req.user_id,
        query=req.query,
        limit=req.limit
    )
    
    # Get full content for each result
    from memoryx.core.storage import StorageManager
    storage = StorageManager(config)
    
    enriched_results = []
    for r in results:
        mem = storage.get(r['id'])
        if mem:
            enriched_results.append({
                'id': r['id'],
                'score': r.get('score', 0),
                'content': mem.content,
                'level': mem.level
            })
    
    return {"results": enriched_results}


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


@app.get("/api/backup")
async def list_backups():
    from memoryx.core.config import Config
    from memoryx.backup.manager import BackupManager
    
    config = Config()
    manager = BackupManager(config)
    backups = manager.list_backups()
    
    return {"backups": backups}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "MemoryX Dashboard"}


def run_dashboard(host: str = "0.0.0.0", port: int = 8080):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
