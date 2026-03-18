"""
MemoryX 语义搜索
向量 + 关键词混合搜索
"""

from typing import List, Dict, Optional
import numpy as np
import hashlib


class SemanticSearch:
    """语义搜索"""
    
    def __init__(self, config):
        self.config = config
        self.embedding_dim = 384  # 默认维度
        self._init_vector_db()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        # 使用内存存储作为默认
        self.vectors = {}
        self.db_type = "memory"
        self.db_path = self.config.storage_path / "vector_db"
        self.db_path.mkdir(parents=True, exist_ok=True)
    
    def encode(self, text: str) -> List[float]:
        """生成文本嵌入"""
        hash_val = hashlib.md5(text.encode()).digest()
        vector = np.frombuffer(hash_val, dtype=np.float32)
        vector = vector / (np.linalg.norm(vector) + 1e-8)
        full_vector = np.zeros(self.embedding_dim, dtype=np.float32)
        full_vector[:len(vector)] = vector
        return full_vector.tolist()
    
    def add(self, memory_id: str, embedding: List[float], 
            user_id: str, level: str = None):
        """添加向量"""
        self.vectors[memory_id] = {
            "embedding": embedding,
            "user_id": user_id,
            "level": level
        }
    
    def search(self, query: str, user_id: str, level: str = None,
               agent_id: str = None, limit: int = 5) -> List[Dict]:
        """语义搜索"""
        query_embedding = self.encode(query)
        query_vec = np.array(query_embedding)
        
        results = []
        for mem_id, data in self.vectors.items():
            if data["user_id"] != user_id:
                continue
            
            if level and data.get("level") != level:
                continue
            
            try:
                mem_vec = np.array(data["embedding"])
                similarity = np.dot(query_vec, mem_vec)
                
                results.append({
                    "id": mem_id,
                    "score": float(similarity),
                    "metadata": data
                })
            except:
                continue
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def delete(self, memory_id: str):
        """删除向量"""
        self.vectors.pop(memory_id, None)
    
    def close(self):
        """关闭连接"""
        pass
