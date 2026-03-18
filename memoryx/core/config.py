"""
MemoryX 配置管理
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """MemoryX 配置"""
    
    # API 配置
    api_key: Optional[str] = None
    
    # 存储配置
    storage_path: Path = field(default_factory=lambda: Path.home() / ".memoryx")
    
    # 模式: local / cloud
    mode: str = "local"
    
    # 云端配置
    cloud_endpoint: str = "https://api.memoryx.ai"
    
    # 向量数据库
    vector_db_type: str = "chroma"  # chroma / qdrant / pinecone
    
    # Token 压缩配置
    compression_enabled: bool = True
    compression_threshold: int = 1000  # 超过此 token 数启用压缩
    max_context_tokens: int = 4000    # 最大上下文 token
    
    # 备份配置
    auto_backup: bool = True
    backup_interval_hours: int = 24
    backup_retention_days: int = 30
    remote_backup_enabled: bool = False
    remote_backup_path: Optional[str] = None  # S3 / GCS 路径
    
    # 进化配置
    evolution_enabled: bool = True
    evolution_interval_hours: int = 168  # 每周一次
    evolution_strategy: str = "balanced"  # balanced / innovate / harden / repair
    
    # 多 Agent 配置
    default_isolation: bool = True
    allow_memory_sharing: bool = True
    
    # OpenClaw 集成
    openclaw_enabled: bool = False
    
    # LLM 配置 (用于压缩和进化)
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_api_key: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保存储目录存在
        self.storage_path = Path(self.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 从环境变量加载
        self.api_key = self.api_key or os.getenv("MEMORYX_API_KEY")
        self.llm_api_key = self.llm_api_key or os.getenv("LLM_API_KEY")
        
    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量加载配置"""
        return cls(
            api_key=os.getenv("MEMORYX_API_KEY"),
            storage_path=Path(os.getenv("MEMORYX_STORAGE_PATH", "~/.memoryx")),
            mode=os.getenv("MEMORYX_MODE", "local"),
            cloud_endpoint=os.getenv("MEMORYX_CLOUD_ENDPOINT", "https://api.memoryx.ai"),
        )
    
    @classmethod
    def from_file(cls, path: str) -> "Config":
        """从配置文件加载"""
        import json
        with open(path) as f:
            data = json.load(f)
        return cls(**data)
