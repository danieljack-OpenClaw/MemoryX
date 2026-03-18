# -*- coding: utf-8 -*-
"""
MemoryX Core Memory System
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from .config import Config
from .models import Memory, MemoryLevel
from .storage import StorageManager
from .compressor import TokenCompressor
from .search import SemanticSearch
from .graph import KnowledgeGraph


class MemoryX:
    """MemoryX Core"""
    
    def __init__(self, config: Config = None, api_key: str = None):
        self.config = config or Config()
        if api_key:
            self.config.api_key = api_key
        
        # Initialize storage
        self.storage = StorageManager(self.config)
        
        # Initialize compressor
        self.compressor = TokenCompressor(self.config)
        
        # Initialize semantic search
        self.search_engine = SemanticSearch(self.config)
        
        # Initialize knowledge graph
        self.graph = KnowledgeGraph(self.config)
        
    def add(self, user_id: str, content: str, level: str = MemoryLevel.USER,
            metadata: Dict = None, agent_id: str = None, skill_id: str = None,
            project_id: str = None) -> Memory:
        """Add memory"""
        mem_metadata = metadata or {}
        if agent_id:
            mem_metadata["agent_id"] = agent_id
        if skill_id:
            mem_metadata["skill_id"] = skill_id
        if project_id:
            mem_metadata["project_id"] = project_id
        
        memory = Memory.create(
            user_id=user_id,
            content=content,
            level=level,
            metadata=mem_metadata
        )
        
        # Generate embedding
        embedding = self.search_engine.encode(content)
        memory.embedding = embedding
        
        # Save to storage
        self.storage.save(memory)
        
        # Add to search index
        self.search_engine.add(
            memory_id=memory.id,
            embedding=embedding,
            user_id=user_id,
            level=level
        )
        
        # Update knowledge graph
        self.graph.add_memory(memory)
        
        return memory
    
    def search(self, user_id: str, query: str, level: str = None,
               limit: int = 5, agent_id: str = None) -> List[Dict]:
        """Search memories"""
        results = self.search_engine.search(
            query=query,
            user_id=user_id,
            level=level,
            agent_id=agent_id,
            limit=limit
        )
        return results
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get memory by ID"""
        return self.storage.get(memory_id)
    
    def update(self, memory_id: str, content: str = None, 
               metadata: Dict = None) -> Optional[Memory]:
        """Update memory"""
        memory = self.storage.get(memory_id)
        if not memory:
            return None
        
        if content:
            memory.content = content
            memory.embedding = self.search_engine.encode(content)
        
        if metadata:
            memory.metadata.update(metadata)
        
        memory.updated_at = datetime.utcnow().isoformat()
        
        self.storage.save(memory)
        return memory
    
    def delete(self, memory_id: str) -> bool:
        """Delete memory"""
        return self.storage.delete(memory_id)
    
    def get_context(self, user_id: str, agent_id: str = None,
                    max_tokens: int = 4000) -> str:
        """Get compressed context"""
        memories = self.storage.get_by_user(user_id, agent_id=agent_id)
        
        if not memories:
            return ""
        
        context = self.compressor.compress(
            memories=memories,
            max_tokens=max_tokens
        )
        
        return context
    
    def evolve(self, agent_id: str = None) -> Dict:
        """Skill evolution"""
        from ..evolution.engine import EvolutionEngine
        
        engine = EvolutionEngine(self.config)
        result = engine.evolve(agent_id=agent_id)
        
        return result
    
    def backup(self, remote: bool = False) -> str:
        """Backup"""
        from ..backup.manager import BackupManager
        
        manager = BackupManager(self.config)
        backup_id = manager.backup(remote=remote)
        
        return backup_id
    
    def restore(self, backup_id: str) -> bool:
        """Restore backup"""
        from ..backup.manager import BackupManager
        
        manager = BackupManager(self.config)
        return manager.restore(backup_id)
    
    def get_stats(self, user_id: str = None) -> Dict:
        """Get statistics"""
        return {
            "total_memories": self.storage.count(user_id),
            "storage_size": self.storage.get_size(),
            "vector_dim": self.search_engine.embedding_dim,
        }
    
    def close(self):
        """Close connections"""
        self.storage.close()
        self.search_engine.close()
        self.graph.close()
