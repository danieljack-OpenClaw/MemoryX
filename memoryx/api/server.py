"""
MemoryX REST API
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn

from ..core.config import Config
from ..core.memory import MemoryX, MemoryLevel


# API 配置
app = FastAPI(title="MemoryX API", version="0.1.0")

# 全局 MemoryX 实例
memoryx: Optional[MemoryX] = None


def get_memoryx() -> MemoryX:
    """获取 MemoryX 实例"""
    global memoryx
    if memoryx is None:
        config = Config.from_env()
        memoryx = MemoryX(config)
    return memoryx


# ==== 请求模型 ====

class AddMemoryRequest(BaseModel):
    user_id: str
    content: str
    level: str = MemoryLevel.USER
    metadata: Optional[Dict] = None
    agent_id: Optional[str] = None
    skill_id: Optional[str] = None
    project_id: Optional[str] = None


class SearchRequest(BaseModel):
    user_id: str
    query: str
    level: Optional[str] = None
    agent_id: Optional[str] = None
    limit: int = 5


class GetContextRequest(BaseModel):
    user_id: str
    agent_id: Optional[str] = None
    max_tokens: int = 4000


class EvolveRequest(BaseModel):
    agent_id: Optional[str] = None
    strategy: Optional[str] = None


class BackupRequest(BaseModel):
    remote: bool = False
    incremental: bool = False


# ==== 记忆 API ====

@app.post("/memory")
async def add_memory(request: AddMemoryRequest, mx: MemoryX = Depends(get_memoryx)):
    """添加记忆"""
    try:
        memory = mx.add(
            user_id=request.user_id,
            content=request.content,
            level=request.level,
            metadata=request.metadata,
            agent_id=request.agent_id,
            skill_id=request.skill_id,
            project_id=request.project_id
        )
        return {"success": True, "memory": memory.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{memory_id}")
async def get_memory(memory_id: str, mx: MemoryX = Depends(get_memoryx)):
    """获取记忆"""
    memory = mx.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True, "memory": memory.to_dict()}


@app.post("/memory/search")
async def search_memory(request: SearchRequest, mx: MemoryX = Depends(get_memoryx)):
    """搜索记忆"""
    results = mx.search(
        user_id=request.user_id,
        query=request.query,
        level=request.level,
        agent_id=request.agent_id,
        limit=request.limit
    )
    return {"success": True, "results": results}


@app.get("/memory")
async def list_memories(
    user_id: str,
    level: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
    mx: MemoryX = Depends(get_memoryx)
):
    """列出记忆"""
    memories = mx.storage.get_by_user(user_id, level=level, agent_id=agent_id, limit=limit)
    return {
        "success": True,
        "memories": [m.to_dict() for m in memories]
    }


@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, mx: MemoryX = Depends(get_memoryx)):
    """删除记忆"""
    success = mx.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True}


@app.put("/memory/{memory_id}")
async def update_memory(
    memory_id: str,
    content: Optional[str] = None,
    metadata: Optional[Dict] = None,
    mx: MemoryX = Depends(get_memoryx)
):
    """更新记忆"""
    memory = mx.update(memory_id, content=content, metadata=metadata)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"success": True, "memory": memory.to_dict()}


# ==== 上下文 API ====

@app.post("/context")
async def get_context(request: GetContextRequest, mx: MemoryX = Depends(get_memoryx)):
    """获取压缩上下文"""
    context = mx.get_context(
        user_id=request.user_id,
        agent_id=request.agent_id,
        max_tokens=request.max_tokens
    )
    return {"success": True, "context": context}


# ==== 进化 API ====

@app.post("/evolve")
async def evolve(request: EvolveRequest, mx: MemoryX = Depends(get_memoryx)):
    """执行技能进化"""
    result = mx.evolve(agent_id=request.agent_id)
    return {"success": True, "result": result}


@app.get("/evolve/history/{agent_id}")
async def get_evolution_history(agent_id: str, mx: MemoryX = Depends(get_memoryx)):
    """获取进化历史"""
    from ..evolution.engine import EvolutionEngine
    engine = EvolutionEngine(mx.config)
    history = engine.get_evolution_history(agent_id)
    return {"success": True, "history": history}


# ==== 备份 API ====

@app.post("/backup")
async def create_backup(request: BackupRequest, mx: MemoryX = Depends(get_memoryx)):
    """创建备份"""
    backup_id = mx.backup(remote=request.remote, incremental=request.incremental)
    return {"success": True, "backup_id": backup_id}


@app.get("/backup")
async def list_backups(mx: MemoryX = Depends(get_memoryx)):
    """列出备份"""
    from ..backup.manager import BackupManager
    manager = BackupManager(mx.config)
    backups = manager.list_backups()
    return {"success": True, "backups": backups}


@app.post("/backup/{backup_id}/restore")
async def restore_backup(backup_id: str, mx: MemoryX = Depends(get_memoryx)):
    """恢复备份"""
    success = mx.restore(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found or restore failed")
    return {"success": True}


@app.delete("/backup/{backup_id}")
async def delete_backup(backup_id: str, mx: MemoryX = Depends(get_memoryx)):
    """删除备份"""
    from ..backup.manager import BackupManager
    manager = BackupManager(mx.config)
    success = manager.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=404, detail="Backup not found")
    return {"success": True}


# ==== 统计 API ====

@app.get("/stats")
async def get_stats(user_id: Optional[str] = None, mx: MemoryX = Depends(get_memoryx)):
    """获取统计信息"""
    stats = mx.get_stats(user_id=user_id)
    return {"success": True, "stats": stats}


# ==== 健康检查 ====

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "MemoryX"}


# ==== 运行服务 ====

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """运行 API 服务"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
