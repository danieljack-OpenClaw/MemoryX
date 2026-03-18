"""
MemoryX 数据模型
"""

import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict


# 记忆层级
class MemoryLevel:
    USER = "user"
    SESSION = "session"
    AGENT = "agent"
    SKILL = "skill"
    PROJECT = "project"


@dataclass
class Memory:
    """记忆条目"""
    id: str
    user_id: str
    content: str
    level: str  # user / session / agent / skill / project
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    
    @classmethod
    def create(cls, user_id: str, content: str, level: str = MemoryLevel.USER, 
               metadata: Dict = None) -> "Memory":
        """创建记忆"""
        # 生成唯一 ID
        content_hash = hashlib.md5(f"{user_id}{content}{datetime.utcnow()}".encode()).hexdigest()[:12]
        mem_id = f"mem_{level[0]}_{content_hash}"
        
        return cls(
            id=mem_id,
            user_id=user_id,
            content=content,
            level=level,
            metadata=metadata or {}
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Memory":
        """从字典创建"""
        return cls(**data)
