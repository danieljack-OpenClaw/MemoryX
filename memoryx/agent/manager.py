"""
MemoryX 多 Agent 管理
支持记忆共享、隔离、合并
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from ..core.config import Config


@dataclass
class Agent:
    """Agent"""
    id: str
    name: str
    description: str = ""
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class MemorySharing:
    """记忆共享记录"""
    id: str
    from_agent: str
    to_agent: str
    memory_id: str
    shared_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MultiAgentManager:
    """多 Agent 管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path / "agents"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._load_agents()
    
    def _load_agents(self):
        """加载 Agent 数据"""
        agents_file = self.storage_path / "agents.json"
        
        if agents_file.exists():
            with open(agents_file) as f:
                agents_data = json.load(f)
                self.agents = {a["id"]: Agent(**a) for a in agents_data}
        else:
            self.agents = {}
        
        # 加载共享记录
        sharing_file = self.storage_path / "sharing.json"
        if sharing_file.exists():
            with open(sharing_file) as f:
                self.sharing_records = json.load(f)
        else:
            self.sharing_records = []
    
    def _save_agents(self):
        """保存 Agent 数据"""
        agents_file = self.storage_path / "agents.json"
        
        agents_data = [agent.__dict__ for agent in self.agents.values()]
        with open(agents_file, "w") as f:
            json.dump(agents_data, f, ensure_ascii=False, indent=2)
    
    def _save_sharing(self):
        """保存共享记录"""
        sharing_file = self.storage_path / "sharing.json"
        
        with open(sharing_file, "w") as f:
            json.dump(self.sharing_records, f, ensure_ascii=False, indent=2)
    
    def create_agent(self, agent_id: str, name: str, description: str = "",
                    metadata: Dict = None) -> Agent:
        """创建 Agent"""
        agent = Agent(
            id=agent_id,
            name=name,
            description=description,
            metadata=metadata or {}
        )
        
        self.agents[agent_id] = agent
        self._save_agents()
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取 Agent"""
        return self.agents.get(agent_id)
    
    def update_agent(self, agent_id: str, name: str = None,
                    description: str = None, metadata: Dict = None) -> Optional[Agent]:
        """更新 Agent"""
        agent = self.agents.get(agent_id)
        
        if not agent:
            return None
        
        if name:
            agent.name = name
        if description:
            agent.description = description
        if metadata:
            agent.metadata.update(metadata)
        
        agent.updated_at = datetime.utcnow().isoformat()
        
        self._save_agents()
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """删除 Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save_agents()
            return True
        return False
    
    def list_agents(self) -> List[Agent]:
        """列出所有 Agent"""
        return list(self.agents.values())
    
    def share_memory(self, from_agent: str, to_agent: str, memory_id: str) -> bool:
        """
        共享记忆
        
        Args:
            from_agent: 源 Agent ID
            to_agent: 目标 Agent ID
            memory_id: 记忆 ID
            
        Returns:
            bool: 是否成功
        """
        if not self.config.allow_memory_sharing:
            return False
        
        # 验证 Agent 存在
        if from_agent not in self.agents or to_agent not in self.agents:
            return False
        
        # 创建共享记录
        sharing = MemorySharing(
            id=f"share_{from_agent}_{to_agent}_{memory_id}",
            from_agent=from_agent,
            to_agent=to_agent,
            memory_id=memory_id
        )
        
        self.sharing_records.append(sharing.__dict__)
        self._save_sharing()
        
        return True
    
    def get_shared_memories(self, agent_id: str) -> List[str]:
        """获取共享给 Agent 的记忆"""
        memory_ids = []
        
        for record in self.sharing_records:
            if record["to_agent"] == agent_id:
                memory_ids.append(record["memory_id"])
        
        return memory_ids
    
    def isolate_agent(self, agent_id: str) -> bool:
        """
        隔离 Agent 的记忆
        
        Args:
            agent_id: Agent ID
            
        Returns:
            bool: 是否成功
        """
        if agent_id not in self.agents:
            return False
        
        # 更新 Agent 配置
        agent = self.agents[agent_id]
        agent.metadata["isolated"] = True
        agent.updated_at = datetime.utcnow().isoformat()
        
        self._save_agents()
        return True
    
    def unisolate_agent(self, agent_id: str) -> bool:
        """取消 Agent 隔离"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent.metadata["isolated"] = False
        agent.updated_at = datetime.utcnow().isoformat()
        
        self._save_agents()
        return True
    
    def merge_knowledge(self, from_agents: List[str], to_agent: str) -> Dict:
        """
        合并多个 Agent 的知识到目标 Agent
        
        Args:
            from_agents: 源 Agent ID 列表
            to_agent: 目标 Agent ID
            
        Returns:
            Dict: 合并结果
        """
        if to_agent not in self.agents:
            return {"success": False, "error": "Target agent not found"}
        
        merged_count = 0
        
        for from_agent in from_agents:
            if from_agent not in self.agents:
                continue
            
            # 获取源 Agent 的所有共享记录
            for record in self.sharing_records:
                if record["from_agent"] == from_agent and record["to_agent"] == to_agent:
                    merged_count += 1
        
        return {
            "success": True,
            "from_agents": from_agents,
            "to_agent": to_agent,
            "merged_count": merged_count,
            "merged_at": datetime.utcnow().isoformat()
        }
    
    def get_agent_graph(self) -> Dict:
        """获取 Agent 关系图"""
        nodes = []
        edges = []
        
        for agent in self.agents.values():
            nodes.append({
                "id": agent.id,
                "name": agent.name,
                "isolated": agent.metadata.get("isolated", False)
            })
        
        for record in self.sharing_records:
            edges.append({
                "from": record["from_agent"],
                "to": record["to_agent"],
                "memory_id": record["memory_id"]
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
