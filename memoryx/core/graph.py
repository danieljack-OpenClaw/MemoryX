"""
MemoryX 知识图谱
用于关系推理和知识关联
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import re

from .models import Memory
from .config import Config


class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self, config: Config):
        self.config = config
        self.storage_path = config.storage_path / "graph"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 图数据结构
        self.nodes = {}  # 实体
        self.edges = []  # 关系
        self._load()
    
    def _load(self):
        """加载图数据"""
        # 从文件加载
        nodes_file = self.storage_path / "nodes.json"
        edges_file = self.storage_path / "edges.json"
        
        if nodes_file.exists():
            import json
            with open(nodes_file) as f:
                self.nodes = json.load(f)
        
        if edges_file.exists():
            import json
            with open(edges_file) as f:
                self.edges = json.load(f)
    
    def _save(self):
        """保存图数据"""
        import json
        
        nodes_file = self.storage_path / "nodes.json"
        edges_file = self.storage_path / "edges.json"
        
        with open(nodes_file, "w") as f:
            json.dump(self.nodes, f, ensure_ascii=False, indent=2)
        
        with open(edges_file, "w") as f:
            json.dump(self.edges, f, ensure_ascii=False, indent=2)
    
    def add_memory(self, memory: Memory):
        """从记忆中添加实体和关系"""
        # 提取实体
        entities = self._extract_entities(memory.content)
        
        # 添加实体
        for entity in entities:
            if entity not in self.nodes:
                self.nodes[entity] = {
                    "type": "entity",
                    "mention_count": 0,
                    "first_seen": memory.created_at,
                    "last_seen": memory.created_at
                }
            else:
                self.nodes[entity]["mention_count"] += 1
                self.nodes[entity]["last_seen"] = memory.created_at
        
        # 添加关系 (基于共现)
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                self._add_edge(e1, e2, memory.id)
        
        self._save()
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体"""
        # 简单实现: 提取大写开头的词和特定模式
        # 实际可使用 NER
        
        entities = []
        
        # 提取大写开头的词
        camel_words = re.findall(r'[A-Z][a-z]+(?=[A-Z]|\s|$)', text)
        entities.extend(camel_words)
        
        # 提取引号中的内容
        quoted = re.findall(r'"([^"]+)"', text)
        entities.extend(quoted)
        
        # 提取特定模式: XX的XX
        of_pattern = re.findall(r'([\u4e00-\u9fff]+)的([\u4e00-\u9fff]+)', text)
        for p in of_pattern:
            entities.extend(p)
        
        # 去重
        return list(set(entities))
    
    def _add_edge(self, source: str, target: str, memory_id: str):
        """添加边"""
        # 查找是否已存在
        for edge in self.edges:
            if edge["source"] == source and edge["target"] == target:
                edge["weight"] += 1
                if memory_id not in edge["memory_ids"]:
                    edge["memory_ids"].append(memory_id)
                return
        
        # 新边
        self.edges.append({
            "source": source,
            "target": target,
            "weight": 1,
            "memory_ids": [memory_id],
            "type": "co_occurrence"
        })
    
    def get_related(self, entity: str, depth: int = 1) -> List[Dict]:
        """获取相关实体"""
        related = []
        visited = {entity}
        queue = [(entity, 0)]
        
        while queue:
            current, d = queue.pop(0)
            
            if d >= depth:
                continue
            
            for edge in self.edges:
                neighbor = None
                if edge["source"] == current and edge["target"] not in visited:
                    neighbor = edge["target"]
                elif edge["target"] == current and edge["source"] not in visited:
                    neighbor = edge["source"]
                
                if neighbor:
                    related.append({
                        "entity": neighbor,
                        "relation": "co_occurs_with",
                        "weight": edge["weight"],
                        "distance": d + 1
                    })
                    visited.add(neighbor)
                    queue.append((neighbor, d + 1))
        
        return related
    
    def search_path(self, source: str, target: str) -> List[str]:
        """查找两个实体之间的路径"""
        # BFS
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return path
            
            for edge in self.edges:
                neighbor = None
                if edge["source"] == current and edge["target"] not in visited:
                    neighbor = edge["target"]
                elif edge["target"] == current and edge["source"] not in visited:
                    neighbor = edge["source"]
                
                if neighbor:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def query(self, question: str) -> Dict:
        """知识问答"""
        # 简单实现: 提取问题中的实体并返回相关知识
        entities = self._extract_entities(question)
        
        results = {}
        for entity in entities:
            if entity in self.nodes:
                related = self.get_related(entity)
                results[entity] = {
                    "info": self.nodes[entity],
                    "related": related
                }
        
        return results
    
    def close(self):
        """关闭"""
        self._save()
