"""
MemoryX 语义搜索
向量 + 关键词混合搜索
"""

from typing import List, Dict, Optional
import numpy as np

from .config import Config


class SemanticSearch:
    """语义搜索"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_dim = 384  # 默认维度
        self._init_vector_db()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        # 支持多种向量数据库
        db_type = self.config.vector_db_type
        
        if db_type == "chroma":
            self._init_chroma()
        elif db_type == "qdrant":
            self._init_qdrant()
        elif db_type == "memory":
            self._init_memory()
        else:
            self._init_memory()
    
    def _init_chroma(self):
        """初始化 ChromaDB"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            db_path = self.config.storage_path / "vector_db"
            db_path.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(str(db_path))
            self.collection = self.client.get_or_create_collection(
                name="memories",
                metadata={"hnsw:space": "cosine"}
            )
            self.db_type = "chroma"
        except ImportError:
            print("ChromaDB not installed, using in-memory fallback")
            self._init_memory()
    
    def _init_qdrant(self):
        """初始化 Qdrant"""
        try:
            from qdrant_client import QdrantClient
            
            self.client = QdrantClient(":memory:")
            self.db_type = "qdrant"
        except ImportError:
            self._init_memory()
    
    def _init_memory(self):
        """内存向量存储 ( fallback )"""
        self.vectors = {}
        self.db_type = "memory"
    
    def encode(self, text: str) -> List[float]:
        """
        生成文本嵌入
        
        在实际实现中，可以使用:
        - sentence-transformers
        - openai embedding
        - cohere
        """
        # 简单哈希作为占位符
        # 实际使用时应替换为真正的 embedding
        import hashlib
        
        hash_val = hashlib.md5(text.encode()).digest()
        # 转换为固定维度的向量
        vector = np.frombuffer(hash_val, dtype=np.float32)
        # 归一化
        vector = vector / (np.linalg.norm(vector) + 1e-8)
        # 填充到目标维度
        full_vector = np.zeros(self.embedding_dim, dtype=np.float32)
        full_vector[:len(vector)] = vector
        
        return full_vector.tolist()
    
    def add(self, memory_id: str, embedding: List[float], 
            user_id: str, level: str = None):
        """添加向量"""
        if self.db_type == "chroma":
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[{"user_id": user_id, "level": level}]
            )
        elif self.db_type == "memory":
            self.vectors[memory_id] = {
                "embedding": embedding,
                "user_id": user_id,
                "level": level
            }
    
    def search(self, query: str, user_id: str, level: str = None,
               agent_id: str = None, limit: int = 5) -> List[Dict]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            user_id: 用户 ID
            level: 记忆层级
            agent_id: Agent ID
            limit: 返回数量
            
        Returns:
            List[Dict]: 搜索结果
        """
        # 生成查询向量
        query_embedding = self.encode(query)
        
        if self.db_type == "chroma":
            # ChromaDB 搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # 多取一些，后面过滤
                where={"user_id": user_id}
            )
            
            output = []
            for i, mem_id in enumerate(results["ids"][0]):
                output.append({
                    "id": mem_id,
                    "score": 1 - results["distances"][0][i],  # 转换为相似度
                    "metadata": results["metadatas"][0][i]
                })
            
            return output
        
        elif self.db_type == "memory":
            # 内存搜索
            query_vec = np.array(query_embedding)
            
            results = []
            for mem_id, data in self.vectors.items():
                if data["user_id"] != user_id:
                    continue
                
                if level and data.get("level") != level:
                    continue
                
                # 计算余弦相似度
                mem_vec = np.array(data["embedding"])
                similarity = np.dot(query_vec, mem_vec)
                
                results.append({
                    "id": mem_id,
                    "score": float(similarity),
                    "metadata": data
                })
            
            # 排序
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
        
        return []
    
    def delete(self, memory_id: str):
        """删除向量"""
        if self.db_type == "chroma":
            self.collection.delete(ids=[memory_id])
        elif self.db_type == "memory":
            self.vectors.pop(memory_id, None)
    
    def close(self):
        """关闭连接"""
        pass
