"""
MemoryX 存储管理 - 支持本地+云端双存储
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import asdict


class StorageManager:
    """存储管理器 - SQLite + 文件系统 (本地+云端双模式)"""
    
    def __init__(self, config):
        self.config = config
        self.storage_path = config.storage_path
        
        # 确保目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.storage_path / "memoryx.db"
        self._init_db()
        
        # 加载云端配置
        self._load_cloud_config()
        
        # 初始化云端存储
        self._init_cloud()
    
    def _load_cloud_config(self):
        """加载云端配置"""
        import os
        settings_file = self.storage_path / "settings.json"
        self.cloud_enabled = False
        self.cloud_provider = None
        self.cloud_config = {}
        
        if settings_file.exists():
            try:
                data = json.loads(settings_file.read_text(encoding='utf-8'))
                self.cloud_enabled = data.get("cloud_enabled", False)
                self.cloud_provider = data.get("cloud_provider", "")
                self.cloud_config = {
                    "region": data.get("cloud_region", ""),
                    "bucket": data.get("cloud_bucket", "")
                }
                # 从环境变量加载密钥
                if self.cloud_provider == "aliyun":
                    self.cloud_config["access_key_id"] = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
                    self.cloud_config["access_key_secret"] = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
                elif self.cloud_provider == "tencent":
                    self.cloud_config["secret_id"] = os.getenv("TENCENT_SECRET_ID", "")
                    self.cloud_config["secret_key"] = os.getenv("TENCENT_SECRET_KEY", "")
                elif self.cloud_provider == "aws":
                    self.cloud_config["access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID", "")
                    self.cloud_config["secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            except:
                pass
    
    def _init_cloud(self):
        """初始化云端存储"""
        self.cloud_client = None
        if not self.cloud_enabled or not self.cloud_provider:
            return
        
        try:
            # 延迟导入，避免循环依赖
            from ..cloud.sync import CloudSync
            self.cloud_client = CloudSync(self.config)
        except Exception as e:
            print(f"Cloud init failed: {e}")
    
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
                embedding TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_level ON memories(level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
        
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
    
    def save(self, memory):
        """保存记忆 - 同时保存到本地和云端 (如果云端已启用)"""
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
        
        # 同时保存到云端 (如果启用)
        if self.cloud_enabled and self.cloud_client:
            try:
                self._sync_to_cloud(memory)
            except Exception as e:
                print(f"Cloud sync error: {e}")
    
    def _sync_to_cloud(self, memory):
        """同步单个记忆到云端"""
        if not self.cloud_client:
            return
        try:
            self.cloud_client.upload_memory(memory)
        except Exception as e:
            print(f"Cloud upload failed: {e}")
    
    def sync_all_to_cloud(self):
        """同步所有记忆到云端"""
        if not self.cloud_enabled or not self.cloud_client:
            return {"success": False, "error": "Cloud not enabled"}
        
        try:
            memories = self.get_all()
            for memory in memories:
                self._sync_to_cloud(memory)
            return {"success": True, "count": len(memories)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_from_cloud(self):
        """从云端加载记忆"""
        if not self.cloud_enabled or not self.cloud_client:
            return []
        
        try:
            return self.cloud_client.download_memories()
        except Exception as e:
            print(f"Cloud download failed: {e}")
            return []
    
    def get(self, memory_id: str):
        """获取记忆"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # 延迟导入避免循环
        from .models import Memory
        
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
                    agent_id: str = None, limit: int = 100):
        """获取用户的所有记忆"""
        from .models import Memory
        
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
