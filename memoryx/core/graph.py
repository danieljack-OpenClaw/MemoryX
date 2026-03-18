# -*- coding: utf-8 -*-
"""
MemoryX 知识图谱模块
实现向量 + 知识图谱混合存储和检索
"""
import json
import networkx as nx
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re


class GraphMemory:
    """
    知识图谱记忆模块
    使用 NetworkX 构建内存知识图谱
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            from memoryx.core.config import Config
            config = Config()
            storage_path = str(config.storage_path / "graph")
        elif hasattr(storage_path, 'storage_path'):
            storage_path = str(storage_path.storage_path / "graph")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.graph = nx.DiGraph()
        self._load_graph()
    
    def _get_graph_file(self) -> Path:
        return self.storage_path / "knowledge_graph.json"
    
    def _load_graph(self):
        graph_file = self._get_graph_file()
        if graph_file.exists():
            try:
                data = json.loads(graph_file.read_text(encoding='utf-8'))
                if "nodes" in data and "edges" in data:
                    self.graph.add_nodes_from(data["nodes"])
                    self.graph.add_edges_from(data["edges"])
            except:
                pass
    
    def _save_graph(self):
        graph_file = self._get_graph_file()
        data = {
            "nodes": list(self.graph.nodes(data=True)),
            "edges": list(self.graph.edges(data=True)),
            "saved_at": datetime.now().isoformat()
        }
        graph_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def add_node(self, node_id: str, node_type: str, content: str, metadata: dict = None) -> bool:
        if self.graph.has_node(node_id):
            return False
        metadata = metadata or {}
        self.graph.add_node(node_id, node_type=node_type, content=content, **metadata)
        self._save_graph()
        return True
    
    def add_edge(self, from_id: str, to_id: str, relation: str, weight: float = 1.0) -> bool:
        if not self.graph.has_node(from_id) or not self.graph.has_node(to_id):
            return False
        self.graph.add_edge(from_id, to_id, relation=relation, weight=weight)
        self._save_graph()
        return True
    
    def get_node(self, node_id: str) -> Optional[dict]:
        if not self.graph.has_node(node_id):
            return None
        return dict(self.graph.nodes[node_id])
    
    def get_related_nodes(self, node_id: str, max_depth: int = 1) -> List[Tuple[str, dict]]:
        if not self.graph.has_node(node_id):
            return []
        
        related = []
        visited = set()
        
        def dfs(current_id, depth):
            if depth > max_depth:
                return
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.append((neighbor, dict(self.graph.nodes[neighbor])))
                    dfs(neighbor, depth + 1)
        
        visited.add(node_id)
        dfs(node_id, 0)
        return related
    
    def find_path(self, from_id: str, to_id: str) -> List[str]:
        if not self.graph.has_node(from_id) or not self.graph.has_node(to_id):
            return []
        try:
            return nx.shortest_path(self.graph, from_id, to_id)
        except:
            return []
    
    def extract_entities(self, text: str) -> List[Dict]:
        entities = []
        
        names = re.findall(r'[\u4e00-\u9fa5]{2,4}(?:先生|女士|老板|总|哥|姐|爷)', text)
        for name in names:
            entities.append({"id": f"person_{name}", "name": name, "type": "person"})
        
        companies = re.findall(r'(?:公司|企业|集团)([\u4e00-\u9fa5]+)', text)
        for company in companies:
            entities.append({"id": f"company_{company}", "name": f"{company}公司", "type": "organization"})
        
        projects = re.findall(r'([\u4e00-\u9fa5]+(?:项目|业务|产品|平台))', text)
        for project in projects:
            entities.append({"id": f"project_{project}", "name": project, "type": "project"})
        
        return entities
    
    def add_memory_to_graph(self, memory_id: str, content: str, level: str = "user"):
        self.add_node(
            node_id=f"memory_{memory_id}",
            node_type="memory",
            content=content,
            metadata={"level": level, "created_at": datetime.now().isoformat()}
        )
        
        entities = self.extract_entities(content)
        for entity in entities:
            self.add_node(
                node_id=entity["id"],
                node_type=entity["type"],
                content=entity["name"]
            )
            self.add_edge(
                from_id=entity["id"],
                to_id=f"memory_{memory_id}",
                relation="mentioned_in"
            )
    
    def add_memory(self, memory) -> bool:
        """兼容旧接口"""
        try:
            memory_id = memory.id if hasattr(memory, 'id') else str(memory)
            content = memory.content if hasattr(memory, 'content') else str(memory)
            level = memory.level.value if hasattr(memory, 'level') else 'user'
            self.add_memory_to_graph(memory_id, content, level)
            return True
        except:
            return False
    
    def query_by_entity(self, entity_name: str) -> List[Dict]:
        matching_entities = [
            node for node in self.graph.nodes()
            if entity_name in str(node) or (
                self.graph.nodes[node].get("content", "") and 
                entity_name in self.graph.nodes[node].get("content", "")
            )
        ]
        
        results = []
        for entity_id in matching_entities:
            related = self.get_related_nodes(entity_id)
            for related_id, related_data in related:
                if related_id.startswith("memory_"):
                    results.append({
                        "memory_id": related_id.replace("memory_", ""),
                        "entity": entity_name,
                        "content": related_data.get("content", "")
                    })
        return results
    
    def get_graph_stats(self) -> dict:
        types = {}
        for node, data in self.graph.nodes(data=True):
            node_type = data.get("node_type", "unknown")
            types[node_type] = types.get(node_type, 0) + 1
        
        rel_types = {}
        for u, v, data in self.graph.edges(data=True):
            relation = data.get("relation", "unknown")
            rel_types[relation] = rel_types.get(relation, 0) + 1
        
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": types,
            "relation_types": rel_types
        }
    
    def clear(self):
        self.graph.clear()
        self._save_graph()
    
    def close(self):
        """关闭连接"""
        pass  # NetworkX 不需要关闭


class HybridSearch:
    """向量 + 图谱混合检索"""
    
    def __init__(self, memoryx=None, graph_memory=None):
        self.memoryx = memoryx
        self.graph_memory = graph_memory or GraphMemory()
    
    def search(self, query: str, user_id: str, limit: int = 5) -> List[dict]:
        results = []
        
        if self.memoryx:
            vector_results = self.memoryx.search(user_id=user_id, query=query, limit=limit * 2)
            results.extend([{"source": "vector", **r} for r in vector_results])
        
        entities = self.graph_memory.extract_entities(query)
        for entity in entities:
            graph_results = self.graph_memory.query_by_entity(entity["name"])
            results.extend([{"source": "graph", **r} for r in graph_results])
        
        seen = set()
        unique_results = []
        for r in results:
            rid = r.get("id") or r.get("memory_id")
            if rid and rid not in seen:
                seen.add(rid)
                unique_results.append(r)
        
        return unique_results[:limit]
    
    def rerank_by_graph(self, results: List[dict], query: str) -> List[dict]:
        if not results:
            return results
        
        query_entities = self.graph_memory.extract_entities(query)
        
        for result in results:
            graph_score = 0
            content = result.get("content", "")
            
            for entity in query_entities:
                if entity["name"] in content:
                    graph_score += 1
                
                result_id = result.get("id") or result.get("memory_id", "")
                path = self.graph_memory.find_path(entity["id"], f"memory_{result_id}")
                if path:
                    graph_score += len(path) * 0.5
            
            result["graph_score"] = graph_score
            result["hybrid_score"] = result.get("score", 0) * 0.7 + graph_score * 0.3
        
        results.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
        return results


# 兼容旧名称
KnowledgeGraph = GraphMemory


__all__ = [
    "GraphMemory",
    "HybridSearch",
    "KnowledgeGraph"
]
