"""
MemoryX 存储管理
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from ..core.memory import Memory
from ..core.config import Config


class StorageManager:
    """存储管理器 - SQLite + 文件系统"""
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path
        
        # 确保目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.storage_path / "memoryx.db"
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                level TEXT NOT NULL,
                metadata TEXT,
                embedding BLOB,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT,
                INDEX idx_user_id (user_id),
                INDEX idx_level (level),
                INDEX idx_created (created_at)
            )
        """)
        
        # Agent 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Skill 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                name TEXT,
                version TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            )
        """)
        
        # 备份记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id TEXT PRIMARY KEY,
                backup_type TEXT,
                file_path TEXT,
                size INTEGER,
                created_at TEXT NOT NULL,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save(self, memory: Memory):
        """保存记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, user_id, content, level, metadata, embedding, created_at, updated_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.user_id,
            memory.content,
            memory.level,
            json.dumps(memory.metadata),
            json.dumps(memory.embedding) if memory.embedding else None,
            memory.created_at,
            memory.updated_at,
            memory.expires_at
        ))
        
        conn.commit()
        conn.close()
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """获取记忆"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Memory(
            id=row["id"],
            user_id=row["user_id"],
            content=row["content"],
            level=row["level"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            embedding=json.loads(row["embedding"]) if row["embedding"] else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            expires_at=row["expires_at"]
        )
    
    def get_by_user(self, user_id: str, level: str = None, 
                    agent_id: str = None, limit: int = 100) -> List[Memory]:
        """获取用户的所有记忆"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM memories WHERE user_id = ?"
        params = [user_id]
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if agent_id:
            query += " AND metadata LIKE ?"
            params.append(f'%"agent_id": "{agent_id}"%')
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memories.append(Memory(
                id=row["id"],
                user_id=row["user_id"],
                content=row["content"],
                level=row["level"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                embedding=json.loads(row["embedding"]) if row["embedding"] else None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                expires_at=row["expires_at"]
            ))
        
        return memories
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def count(self, user_id: str = None) -> int:
        """统计记忆数量"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("SELECT COUNT(*) FROM memories WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT COUNT(*) FROM memories")
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_size(self) -> int:
        """获取存储大小"""
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def close(self):
        """关闭连接"""
        # SQLite 自动管理
        pass
