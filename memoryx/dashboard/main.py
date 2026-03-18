# -*- coding: utf-8 -*-
"""
MemoryX Web Dashboard - Multi-language Support
"""
import os
import json
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Multi-language translations
TRANSLATIONS = {
    "zh_CN": {
        "title": "MemoryX Dashboard",
        "subtitle": "AI Agent Memory Management",
        "total_memories": "Total Memories",
        "storage_size": "Storage Size",
        "vector_dim": "Vector Dimension",
        "user_count": "Users",
        "tab_memories": "Memories",
        "tab_add": "Add Memory",
        "tab_search": "Search",
        "tab_backup": "Backup",
        "tab_settings": "Settings",
        "tab_feedback": "Feedback",
        "add_memory": "Add Memory",
        "user_id": "User ID",
        "content": "Content",
        "level": "Level",
        "level_user": "User (Permanent)",
        "level_session": "Session (Temp)",
        "level_project": "Project",
        "level_agent": "Agent",
        "level_skill": "Skill",
        "submit": "Submit",
        "search": "Search",
        "search_query": "Search Query",
        "backup": "Create Backup",
        "sync_cloud": "Sync to Cloud",
        "refresh": "Refresh",
        "delete": "Delete",
        "confirm_delete": "Confirm delete?",
        "no_data": "No data",
        "similarity": "Similarity",
        "created_at": "Created",
        "storage_path": "Storage Path",
        "max_tokens": "Max Tokens",
        "auto_backup": "Auto Backup",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "save": "Save",
        "cloud_feedback": "Cloud Provider Feedback",
        "provider": "Provider",
        "email": "Email",
        "note": "Note",
        "submit_feedback": "Submit",
        "feedback_success": "Thank you!",
        "cloud_providers": "Supported Cloud Services",
        "loading": "Loading...",
        "success": "Success",
        "error": "Error",
        "language": "Language",
    },
    "zh_TW": {
        "title": "MemoryX 儀表盤",
        "subtitle": "AI Agent 記憶管理",
        "total_memories": "總記憶",
        "storage_size": "存儲大小",
        "vector_dim": "向量維度",
        "user_count": "用戶數",
        "tab_memories": "記憶",
        "tab_add": "添加",
        "tab_search": "搜索",
        "tab_backup": "備份",
        "tab_settings": "設置",
        "tab_feedback": "反饋",
        "add_memory": "添加記憶",
        "user_id": "用戶ID",
        "content": "內容",
        "level": "層級",
        "level_user": "用戶 (永久)",
        "level_session": "會話 (臨時)",
        "level_project": "項目",
        "level_agent": "代理",
        "level_skill": "技能",
        "submit": "提交",
        "search": "搜索",
        "search_query": "搜索內容",
        "backup": "創建備份",
        "sync_cloud": "雲同步",
        "refresh": "刷新",
        "delete": "刪除",
        "confirm_delete": "確認刪除?",
        "no_data": "無數據",
        "similarity": "相似度",
        "created_at": "創建時間",
        "storage_path": "路徑",
        "max_tokens": "最大Token",
        "auto_backup": "自動備份",
        "enabled": "啟用",
        "disabled": "禁用",
        "save": "保存",
        "cloud_feedback": "雲廠商反饋",
        "provider": "廠商",
        "email": "郵箱",
        "note": "備註",
        "submit_feedback": "提交",
        "feedback_success": "感謝!",
        "cloud_providers": "支持的雲服務",
        "loading": "加載中...",
        "success": "成功",
        "error": "錯誤",
        "language": "語言",
    },
    "en": {
        "title": "MemoryX Dashboard",
        "subtitle": "AI Agent Memory Management",
        "total_memories": "Total Memories",
        "storage_size": "Storage Size",
        "vector_dim": "Vector Dimension",
        "user_count": "Users",
        "tab_memories": "Memories",
        "tab_add": "Add Memory",
        "tab_search": "Search",
        "tab_backup": "Backup",
        "tab_settings": "Settings",
        "tab_feedback": "Feedback",
        "add_memory": "Add Memory",
        "user_id": "User ID",
        "content": "Content",
        "level": "Level",
        "level_user": "User (Permanent)",
        "level_session": "Session (Temp)",
        "level_project": "Project",
        "level_agent": "Agent",
        "level_skill": "Skill",
        "submit": "Submit",
        "search": "Search",
        "search_query": "Search Query",
        "backup": "Create Backup",
        "sync_cloud": "Sync to Cloud",
        "refresh": "Refresh",
        "delete": "Delete",
        "confirm_delete": "Confirm delete?",
        "no_data": "No data",
        "similarity": "Similarity",
        "created_at": "Created",
        "storage_path": "Storage Path",
        "max_tokens": "Max Tokens",
        "auto_backup": "Auto Backup",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "save": "Save",
        "cloud_feedback": "Cloud Provider Feedback",
        "provider": "Provider",
        "email": "Email",
        "note": "Note",
        "submit_feedback": "Submit",
        "feedback_success": "Thank you!",
        "cloud_providers": "Supported Cloud Services",
        "loading": "Loading...",
        "success": "Success",
        "error": "Error",
        "language": "Language",
    },
    "es": {
        "title": "MemoryX Panel",
        "subtitle": "Gestion de Memoria AI",
        "total_memories": "Total Recuerdos",
        "storage_size": "Almacenamiento",
        "vector_dim": "Dimension Vector",
        "user_count": "Usuarios",
        "tab_memories": "Recuerdos",
        "tab_add": "Agregar",
        "tab_search": "Buscar",
        "tab_backup": "Respaldo",
        "tab_settings": "Config",
        "tab_feedback": "Feedback",
        "add_memory": "Agregar Recuerdo",
        "user_id": "ID Usuario",
        "content": "Contenido",
        "level": "Nivel",
        "level_user": "Usuario (Permanente)",
        "level_session": "Sesion (Temp)",
        "level_project": "Proyecto",
        "level_agent": "Agente",
        "level_skill": "Habilidad",
        "submit": "Enviar",
        "search": "Buscar",
        "search_query": "Consulta",
        "backup": "Crear Backup",
        "sync_cloud": "Sincronizar",
        "refresh": "Actualizar",
        "delete": "Eliminar",
        "confirm_delete": "Confirmar?",
        "no_data": "Sin datos",
        "similarity": "Similitud",
        "created_at": "Creado",
        "storage_path": "Ruta",
        "max_tokens": "Max Tokens",
        "auto_backup": "Auto Backup",
        "enabled": "Activado",
        "disabled": "Desactivado",
        "save": "Guardar",
        "cloud_feedback": "Feedback Proveedor",
        "provider": "Proveedor",
        "email": "Email",
        "note": "Nota",
        "submit_feedback": "Enviar",
        "feedback_success": "Gracias!",
        "cloud_providers": "Servicios Soportados",
        "loading": "Cargando...",
        "success": "Exito",
        "error": "Error",
        "language": "Idioma",
    },
    "pt": {
        "title": "MemoryX Painel",
        "subtitle": "Gestao de Memoria AI",
        "total_memories": "Total de Memorias",
        "storage_size": "Armazenamento",
        "vector_dim": "Dimensao Vetor",
        "user_count": "Usuarios",
        "tab_memories": "Memorias",
        "tab_add": "Adicionar",
        "tab_search": "Buscar",
        "tab_backup": "Backup",
        "tab_settings": "Config",
        "tab_feedback": "Feedback",
        "add_memory": "Adicionar Memoria",
        "user_id": "ID Usuario",
        "content": "Conteudo",
        "level": "Nivel",
        "level_user": "Usuario (Permanente)",
        "level_session": "Sessao (Temp)",
        "level_project": "Projeto",
        "level_agent": "Agente",
        "level_skill": "Habilidade",
        "submit": "Enviar",
        "search": "Buscar",
        "search_query": "Consulta",
        "backup": "Criar Backup",
        "sync_cloud": "Sincronizar",
        "refresh": "Atualizar",
        "delete": "Excluir",
        "confirm_delete": "Confirmar?",
        "no_data": "Sem dados",
        "similarity": "Similaridade",
        "created_at": "Criado",
        "storage_path": "Caminho",
        "max_tokens": "Max Tokens",
        "auto_backup": "Auto Backup",
        "enabled": "Ativado",
        "disabled": "Desativado",
        "save": "Salvar",
        "cloud_feedback": "Feedback Provedor",
        "provider": "Provedor",
        "email": "Email",
        "note": "Nota",
        "submit_feedback": "Enviar",
        "feedback_success": "Obrigado!",
        "cloud_providers": "Servicos Suportados",
        "loading": "Carregando...",
        "success": "Sucesso",
        "error": "Erro",
        "language": "Idioma",
    },
    "de": {
        "title": "MemoryX Dashboard",
        "subtitle": "AI Agent Speicherverwaltung",
        "total_memories": "Gesamterinnerungen",
        "storage_size": "Speichergrosse",
        "vector_dim": "Vektordimension",
        "user_count": "Benutzer",
        "tab_memories": "Erinnerungen",
        "tab_add": "Hinzufugen",
        "tab_search": "Suchen",
        "tab_backup": "Sicherung",
        "tab_settings": "Einstellungen",
        "tab_feedback": "Feedback",
        "add_memory": "Erinnerung hinzufugen",
        "user_id": "Benutzer-ID",
        "content": "Inhalt",
        "level": "Ebene",
        "level_user": "Benutzer (Permanent)",
        "level_session": "Sitzung (Temp)",
        "level_project": "Projekt",
        "level_agent": "Agent",
        "level_skill": "Fahigkeit",
        "submit": "Absenden",
        "search": "Suchen",
        "search_query": "Suchanfrage",
        "backup": "Sicherung erstellen",
        "sync_cloud": "Synchronisieren",
        "refresh": "Aktualisieren",
        "delete": "Loschen",
        "confirm_delete": "Bestatigen?",
        "no_data": "Keine Daten",
        "similarity": "Ahnlichkeit",
        "created_at": "Erstellt",
        "storage_path": "Pfad",
        "max_tokens": "Max Tokens",
        "auto_backup": "Auto Sicherung",
        "enabled": "Aktiviert",
        "disabled": "Deaktiviert",
        "save": "Speichern",
        "cloud_feedback": "Anbieter Feedback",
        "provider": "Anbieter",
        "email": "E-Mail",
        "note": "Notiz",
        "submit_feedback": "Absenden",
        "feedback_success": "Danke!",
        "cloud_providers": "Unterstutzte Dienste",
        "loading": "Laden...",
        "success": "Erfolg",
        "error": "Fehler",
        "language": "Sprache",
    }
}

# Cloud providers
CLOUD_PROVIDERS = [
    {"id": "aws", "name": "AWS S3", "icon": "☁"},
    {"id": "gcs", "name": "Google Cloud", "icon": "G"},
    {"id": "aliyun", "name": "Aliyun OSS", "icon": "A"},
    {"id": "tencent", "name": "Tencent COS", "icon": "T"},
    {"id": "huawei", "name": "Huawei OBS", "icon": "H"},
    {"id": "baidu", "name": "Baidu BOS", "icon": "B"},
    {"id": "jd", "name": "JD Cloud", "icon": "J"},
    {"id": "other", "name": "Other", "icon": "?"},
]


def get_dashboard_html(lang: str = "zh_CN") -> str:
    t = TRANSLATIONS.get(lang, TRANSLATIONS["zh_CN"])
    
    lang_opts = "".join([
        f'<option value="{c}">{n}</option>'
        for c, n in [("zh_CN", "简体中文"), ("zh_TW", "繁體中文"), ("en", "English"), ("es", "Español"), ("pt", "Português"), ("de", "Deutsch")]
    ])
    
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{t['title']}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 28px; }}
        .header select {{ padding: 8px; border-radius: 6px; cursor: pointer; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .stat-card h3 {{ font-size: 14px; color: #666; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; color: #333; }}
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
        .provider-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }}
        .provider-item {{ padding: 15px; border: 1px solid #ddd; border-radius: 8px; text-align: center; cursor: pointer; }}
        .provider-item:hover {{ border-color: #667eea; background: #f5f5ff; }}
        .provider-item.selected {{ border-color: #667eea; background: #e0e7ff; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div><h1>MemoryX</h1><p>{t['subtitle']}</p></div>
            <select id="lang" onchange="window.location.href='?lang='+this.value"><option value="zh_CN">简体中文</option><option value="zh_TW">繁體中文</option><option value="en">English</option><option value="es">Español</option><option value="pt">Português</option><option value="de">Deutsch</option></select>
        </div>
        <script>document.getElementById('lang').value='{lang}';</script>
        
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
            <div class="tab" onclick="tab('feedback')">{t['tab_feedback']}</div>
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
                <h2>{t['add_memory']}</h2>
                <form id="addf">
                    <div class="form-group"><label>{t['user_id']}</label><input id="auid" required></div>
                    <div class="form-group"><label>{t['content']}</label><textarea id="acont" required></textarea></div>
                    <div class="form-group"><label>{t['level']}</label><select id="alvl"><option value="user">{t['level_user']}</option><option value="session">{t['level_session']}</option><option value="project">{t['level_project']}</option></select></div>
                    <button class="btn btn-primary">{t['submit']}</button>
                </form>
                <div id="amsg"></div>
            </div>
        </div>
        
        <div id="search" class="tab-content">
            <div class="section">
                <h2>{t['tab_search']}</h2>
                <div class="search-box">
                    <input id="sq" placeholder="{t['search_query']}">
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
        
        <div id="feedback" class="tab-content">
            <div class="section">
                <h2>{t['cloud_feedback']}</h2>
                <p style="margin-bottom:15px;color:#666">{t['cloud_providers']}:</p>
                <div class="provider-grid" id="pgrid">
                    {''.join([f'<div class="provider-item" onclick="sel(this)" data-p="{p["id"]}">{p["icon"]} {p["name"]}</div>' for p in CLOUD_PROVIDERS])}
                </div>
                <form id="ff" style="margin-top:20px">
                    <div class="form-group"><label>{t['provider']}</label><select id="fp"><option value="aws">AWS S3</option><option value="gcs">Google Cloud</option><option value="aliyun">Aliyun OSS</option><option value="tencent">Tencent COS</option><option value="huawei">Huawei OBS</option><option value="baidu">Baidu BOS</option><option value="jd">JD Cloud</option><option value="other">Other</option></select></div>
                    <div class="form-group"><label>{t['email']}</label><input id="fe" type="email"></div>
                    <div class="form-group"><label>{t['note']}</label><textarea id="fn"></textarea></div>
                    <button class="btn btn-primary">{t['submit_feedback']}</button>
                </form>
                <div id="fmsg"></div>
            </div>
        </div>
        
        <div class="footer">MemoryX v1.0.0</div>
    </div>
    <script>
    const A='/api';
    function tab(x){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));event.target.classList.add('active');document.getElementById(x==='mem'?'mem':x).classList.add('active');if(x==='mem')load();}}
    function sel(el){{document.querySelectorAll('.provider-item').forEach(p=>p.classList.remove('selected'));el.classList.add('selected');document.getElementById('fp').value=el.dataset.p;}}
    async function load(){{const u=document.getElementById('uid').value;const r=await fetch(A+'/memory'+(u?'?user_id='+encodeURIComponent(u):''));const d=await r.json();const tb=document.getElementById('tbody');if(!d.memories.length){{tb.innerHTML='<tr><td colspan="5">{t["no_data"]}</td></tr>';return;}}tb.innerHTML=d.memories.map(m=>`<tr><td>${{m.id}}</td><td><span style="background:#e0e7ff;padding:2px 8px;border-radius:4px;font-size:12px">${{m.level}}</span></td><td>${{m.content.substring(0,40)}}...</td><td>${{new Date(m.created_at).toLocaleDateString()}}</td><td><button class="btn btn-danger" style="padding:4px 8px" onclick="del('${{m.id}}')">{t['delete']}</button></td></tr>`).join('');}}
    async function stats(){{const r=await fetch(A+'/stats');const d=await r.json();document.getElementById('total').textContent=d.stats.total_memories;document.getElementById('size').textContent=(d.stats.storage_size/1024/1024).toFixed(2)+' MB';document.getElementById('dim').textContent=d.stats.vector_dim;}}
    document.getElementById('addf').onsubmit=async e=>{{e.preventDefault();const r=await fetch(A+'/memory',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:document.getElementById('auid').value,content:document.getElementById('acont').value,level:document.getElementById('alvl').value}})}});const d=await r.json();document.getElementById('amsg').innerHTML=d.success?'<div class="message message-success">{t["success"]}!</div>':'<div class="message message-error">'+d.error+'</div>';if(d.success){{document.getElementById('auid').value='';document.getElementById('acont').value='';stats();}}}};
    async function doSearch(){{const q=document.getElementById('sq').value,u=document.getElementById('su').value;if(!q||!u){{alert('Need query and user');return;}}const r=await fetch(A+'/memory/search',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{query:q,user_id:u,limit:5}})}});const d=await r.json();document.getElementById('sres').innerHTML=d.results&&d.results.length?d.results.map(r=>`<div style="background:#f9f9f9;padding:15px;margin-bottom:10px;border-radius:8px"><b>${{r.id}}</b><p>${{r.content||''}}</p><small style="color:#666">${{t['similarity']}}: ${{(r.score||0).toFixed(3)}}</small></div>`).join(''):'{t["no_data"]}';}};
    async function del(id){{if(!confirm('{t["confirm_delete"]}'))return;await fetch(A+'/memory/'+id,{{method:'DELETE'}});load();stats();}};
    async function backup(){{const r=await fetch(A+'/backup',{{method:'POST'}});const d=await r.json();document.getElementById('bmsg').innerHTML=d.backup_id?'<div class="message message-success">'+d.backup_id+'</div>':'';}};
    async function sync(){{const r=await fetch(A+'/cloud/sync',{{method:'POST'}});const d=await r.json();document.getElementById('bmsg').innerHTML=d.success?'<div class="message message-success">{t["success"]}</div>':'<div class="message message-error">'+d.error+'</div>';}};
    document.getElementById('ff').onsubmit=async e=>{{e.preventDefault();const r=await fetch(A+'/feedback',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{provider:document.getElementById('fp').value,user_email:document.getElementById('fe').value,note:document.getElementById('fn').value}})}});const d=await r.json();document.getElementById('fmsg').innerHTML=d.success?'<div class="message message-success">{t["feedback_success"]}</div>':'';}};
    stats();
    </script>
</body>
</html>"""


# Create app
app = FastAPI(title="MemoryX Dashboard")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    lang = request.query_params.get("lang", "zh_CN")
    if lang not in TRANSLATIONS:
        lang = "zh_CN"
    return get_dashboard_html(lang)


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


class FeedbackRequest(BaseModel):
    provider: str
    user_email: str = None
    note: str = None


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
async def add_memory(req: AddMemoryRequest):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    config = Config()
    memory = MemoryX(config)
    try:
        mem = memory.add(user_id=req.user_id, content=req.content, level=req.level, metadata=req.metadata)
        return {"success": True, "memory": mem.to_dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/memory/search")
async def search_memory(req: SearchRequest):
    from memoryx.core.config import Config
    from memoryx.core.memory import MemoryX
    from memoryx.core.storage import StorageManager
    config = Config()
    memory = MemoryX(config)
    results = memory.search(user_id=req.user_id, query=req.query, limit=req.limit)
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
    from memoryx.cloud import CloudSync
    config = Config()
    try:
        cloud = CloudSync(config)
        success = cloud.sync_to_cloud()
        return {"success": success}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    from memoryx.core.config import Config
    from pathlib import Path
    config = Config()
    feedback_file = config.storage_path / "cloud_feedback.json"
    import json
    feedback_file.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if feedback_file.exists():
        data = json.loads(feedback_file.read_text(encoding='utf-8'))
    data.append({"provider": req.provider, "user_email": req.user_email, "note": req.note, "timestamp": datetime.utcnow().isoformat()})
    feedback_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return {"success": True}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


def run_dashboard(host: str = "0.0.0.0", port: int = 8080):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
