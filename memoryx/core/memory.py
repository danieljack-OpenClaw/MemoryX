"""
MemoryX 核心记忆系统
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict

from .config import Config
from .storage import StorageManager
from .compressor import TokenCompressor
from .search import SemanticSearch
from .graph import KnowledgeGraph
from .models import Memory, MemoryLevel


class MemoryX:
    """MemoryX 核心类"""
    
    def __init__(self, config: Config = None, api_key: str = None):
        """
        初始化 MemoryX
        
        Args:
            config: 配置对象
            api_key: API 密钥 (cloud 模式需要)
        """
        self.config = config or Config()
        if api_key:
            self.config.api_key = api_key
        
        # 初始化存储
        self.storage = StorageManager(self.config)
        
        # 初始化压缩器
        self.compressor = TokenCompressor(self.config)
        
        # 初始化语义搜索
        self.search = SemanticSearch(self.config)
        
        # 初始化知识图谱
        self.graph = KnowledgeGraph(self.config)
        
    def add(self, user_id: str, content: str, level: str = MemoryLevel.USER,
            metadata: Dict = None, agent_id: str = None, skill_id: str = None,
            project_id: str = None) -> Memory:
        """
        添加记忆
        
        Args:
            user_id: 用户 ID
            content: 记忆内容
            level: 记忆层级
            metadata: 额外元数据
            agent_id: Agent ID (level=agent 时需要)
            skill_id: Skill ID (level=skill 时需要)
            project_id: Project ID (level=project 时需要)
            
        Returns:
            Memory: 创建的记忆对象
        """
        # 构建元数据
        mem_metadata = metadata or {}
        if agent_id:
            mem_metadata["agent_id"] = agent_id
        if skill_id:
            mem_metadata["skill_id"] = skill_id
        if project_id:
            mem_metadata["project_id"] = project_id
        
        # 创建记忆
        memory = Memory.create(
            user_id=user_id,
            content=content,
            level=level,
            metadata=mem_metadata
        )
        
        # 生成向量嵌入
        embedding = self.search.encode(content)
        memory.embedding = embedding
        
        # 存储
        self.storage.save(memory)
        
        # 更新知识图谱
        self.graph.add_memory(memory)
        
        return memory
    
    def search(self, user_id: str, query: str, level: str = None,
               limit: int = 5, agent_id: str = None) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            user_id: 用户 ID
            query: 查询内容
            level: 记忆层级过滤
            limit: 返回数量限制
            agent_id: Agent ID 过滤
            
        Returns:
            List[Dict]: 记忆列表
        """
        # 语义搜索
        results = self.search.search(
            query=query,
            user_id=user_id,
            level=level,
            agent_id=agent_id,
            limit=limit
        )
        
        return results
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """获取单条记忆"""
        return self.storage.get(memory_id)
    
    def update(self, memory_id: str, content: str = None, 
               metadata: Dict = None) -> Optional[Memory]:
        """更新记忆"""
        memory = self.storage.get(memory_id)
        if not memory:
            return None
        
        if content:
            memory.content = content
            # 重新生成嵌入
            memory.embedding = self.search.encode(content)
        
        if metadata:
            memory.metadata.update(metadata)
        
        memory.updated_at = datetime.utcnow().isoformat()
        
        # 保存
        self.storage.save(memory)
        
        return memory
    
    def delete(self, memory_id: str) -> bool:
        """删除记忆"""
        return self.storage.delete(memory_id)
    
    def get_context(self, user_id: str, agent_id: str = None,
                    max_tokens: int = 4000) -> str:
        """
        获取压缩后的上下文
        
        Args:
            user_id: 用户 ID
            agent_id: Agent ID
            max_tokens: 最大 token 数
            
        Returns:
            str: 压缩后的上下文
        """
        # 获取所有相关记忆
        memories = self.storage.get_by_user(user_id, agent_id=agent_id)
        
        if not memories:
            return ""
        
        # Token 压缩
        context = self.compressor.compress(
            memories=memories,
            max_tokens=max_tokens
        )
        
        return context
    
    def evolve(self, agent_id: str = None) -> Dict:
        """
        技能进化
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dict: 进化结果
        """
        from ..evolution.engine import EvolutionEngine
        
        engine = EvolutionEngine(self.config)
        result = engine.evolve(agent_id=agent_id)
        
        return result
    
    def backup(self, remote: bool = False) -> str:
        """
        备份
        
        Args:
            remote: 是否远程备份
            
        Returns:
            str: 备份 ID
        """
        from ..backup.manager import BackupManager
        
        manager = BackupManager(self.config)
        backup_id = manager.backup(remote=remote)
        
        return backup_id
    
    def restore(self, backup_id: str) -> bool:
        """恢复备份"""
        from ..backup.manager import BackupManager
        
        manager = BackupManager(self.config)
        return manager.restore(backup_id)
    
    def get_stats(self, user_id: str = None) -> Dict:
        """获取统计信息"""
        return {
            "total_memories": self.storage.count(user_id),
            "storage_size": self.storage.get_size(),
            "vector_dim": self.search.embedding_dim,
        }
    
    def close(self):
        """关闭连接"""
        self.storage.close()
        self.search.close()
        self.graph.close()
