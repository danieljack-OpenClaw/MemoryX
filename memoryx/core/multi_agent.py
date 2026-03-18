# -*- coding: utf-8 -*-
"""
MemoryX 多 Agent 记忆管理模块
实现记忆共享、隔离和知识合并
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set


class MultiAgentManager:
    """
    多 Agent 记忆管理器
    
    支持:
    - 记忆共享
    - 记忆隔离
    - 知识合并
    - 权限管理
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            from memoryx.core.config import Config
            config = Config()
            storage_path = str(config.storage_path / "multi_agent")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Agent 注册表
        self.agents_file = self.storage_path / "agents.json"
        self.shares_file = self.storage_path / "shares.json"
        
        self.agents = self._load_agents()
        self.shares = self._load_shares()
    
    def _load_agents(self) -> dict:
        if self.agents_file.exists():
            try:
                return json.loads(self.agents_file.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _load_shares(self) -> dict:
        if self.shares_file.exists():
            try:
                return json.loads(self.shares_file.read_text(encoding='utf-8'))
            except:
                pass
        return {}
    
    def _save_agents(self):
        self.agents_file.write_text(json.dumps(self.agents, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _save_shares(self):
        self.shares_file.write_text(json.dumps(self.shares, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def register_agent(self, agent_id: str, name: str = None, metadata: dict = None) -> bool:
        """
        注册 Agent
        
        Args:
            agent_id: Agent ID
            name: Agent 名称
            metadata: 额外信息
        """
        if agent_id in self.agents:
            return False
        
        self.agents[agent_id] = {
            "name": name or agent_id,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "shared_with": [],  # 共享给哪些 Agent
            "shared_from": []    # 从哪些 Agent 共享
        }
        
        self._save_agents()
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销 Agent"""
        if agent_id not in self.agents:
            return False
        
        del self.agents[agent_id]
        
        # 清理共享关系
        for aid, data in self.agents.items():
            if agent_id in data.get("shared_with", []):
                data["shared_with"].remove(agent_id)
            if agent_id in data.get("shared_from", []):
                data["shared_from"].remove(agent_id)
        
        self._save_agents()
        self._save_shares()
        return True
    
    def share_memory(self, from_agent: str, to_agent: str, memory_id: str, 
                    permission: str = "read") -> bool:
        """
        共享记忆给其他 Agent
        
        Args:
            from_agent: 源 Agent
            to_agent: 目标 Agent
            memory_id: 记忆 ID
            permission: 权限 (read/write)
        """
        if from_agent not in self.agents or to_agent not in self.agents:
            return False
        
        share_key = f"{from_agent}:{memory_id}"
        
        # 记录共享
        if share_key not in self.shares:
            self.shares[share_key] = {
                "from_agent": from_agent,
                "memory_id": memory_id,
                "shared_with": [],
                "permission": permission,
                "created_at": datetime.now().isoformat()
            }
        
        if to_agent not in self.shares[share_key]["shared_with"]:
            self.shares[share_key]["shared_with"].append(to_agent)
        
        # 更新 Agent 关系
        if to_agent not in self.agents[from_agent].get("shared_with", []):
            self.agents[from_agent].setdefault("shared_with", []).append(to_agent)
        
        if from_agent not in self.agents[to_agent].get("shared_from", []):
            self.agents[to_agent].setdefault("shared_from", []).append(from_agent)
        
        self._save_agents()
        self._save_shares()
        return True
    
    def revoke_share(self, from_agent: str, to_agent: str, memory_id: str) -> bool:
        """撤销共享"""
        share_key = f"{from_agent}:{memory_id}"
        
        if share_key not in self.shares:
            return False
        
        if to_agent in self.shares[share_key]["shared_with"]:
            self.shares[share_key]["shared_with"].remove(to_agent)
        
        if to_agent in self.agents[from_agent].get("shared_with", []):
            self.agents[from_agent]["shared_with"].remove(to_agent)
        
        self._save_agents()
        self._save_shares()
        return True
    
    def get_shared_memories(self, agent_id: str) -> List[dict]:
        """
        获取共享给指定 Agent 的所有记忆
        
        Args:
            agent_id: Agent ID
        """
        shared = []
        
        for share_key, data in self.shares.items():
            if agent_id in data.get("shared_with", []):
                memory_id = data["memory_id"]
                shared.append({
                    "memory_id": memory_id,
                    "from_agent": data["from_agent"],
                    "permission": data.get("permission", "read"),
                    "shared_at": data.get("created_at")
                })
        
        return shared
    
    def isolate_agent(self, agent_id: str) -> bool:
        """
        隔离 Agent - 移除所有共享关系
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self.agents:
            return False
        
        # 移除所有出去的共享
        for share_key, data in list(self.shares.items()):
            if data["from_agent"] == agent_id:
                for target in data.get("shared_with", []):
                    if target in self.agents:
                        if agent_id in self.agents[target].get("shared_from", []):
                            self.agents[target]["shared_from"].remove(agent_id)
                del self.shares[share_key]
        
        # 移除所有进来的共享
        for share_key, data in list(self.shares.items()):
            if agent_id in data.get("shared_with", []):
                data["shared_with"].remove(agent_id)
                from_agent = data["from_agent"]
                if from_agent in self.agents and agent_id in self.agents[from_agent].get("shared_with", []):
                    self.agents[from_agent]["shared_with"].remove(agent_id)
        
        # 重置 Agent 的共享列表
        self.agents[agent_id]["shared_with"] = []
        self.agents[agent_id]["shared_from"] = []
        
        self._save_agents()
        self._save_shares()
        return True
    
    def merge_knowledge(self, from_agents: List[str], to_agent: str, 
                       strategy: str = "union") -> List[str]:
        """
        合并多个 Agent 的知识
        
        Args:
            from_agents: 源 Agent 列表
            to_agent: 目标 Agent
            strategy: 合并策略 (union/intersection/latest)
        
        Returns:
            合并后的记忆 ID 列表
        """
        if not from_agents or to_agent not in self.agents:
            return []
        
        # 获取所有共享记忆
        all_memories = {}
        for agent in from_agents:
            shared = self.get_shared_memories(agent)
            for mem in shared:
                mid = mem["memory_id"]
                if mid not in all_memories:
                    all_memories[mid] = []
                all_memories[mid].append(mem)
        
        # 根据策略选择记忆
        merged = []
        for memory_id, sources in all_memories.items():
            if strategy == "union":
                # 合并所有
                merged.append(memory_id)
            elif strategy == "intersection":
                # 至少在两个 Agent 中共享
                if len(sources) > 1:
                    merged.append(memory_id)
            elif strategy == "latest":
                # 选择最新的
                latest = max(sources, key=lambda x: x.get("shared_at", ""))
                merged.append(latest["memory_id"])
        
        # 共享给目标 Agent
        for memory_id in merged:
            from_agent = all_memories[memory_id][0]["from_agent"]
            self.share_memory(from_agent, to_agent, memory_id)
        
        return merged
    
    def get_agent_info(self, agent_id: str) -> Optional[dict]:
        """获取 Agent 信息"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[dict]:
        """列出所有注册的 Agent"""
        return [
            {"agent_id": aid, **data}
            for aid, data in self.agents.items()
        ]
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_agents": len(self.agents),
            "total_shares": len(self.shares),
            "agents": list(self.agents.keys())
        }


# ============ 导出 ============

__all__ = [
    "MultiAgentManager"
]
