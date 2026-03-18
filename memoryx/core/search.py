# -*- coding: utf-8 -*-
"""
MemoryX Semantic Search with Real Embeddings
"""

from typing import List, Dict
import numpy as np

from .config import Config


class SemanticSearch:
    """Semantic Search with real embeddings"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        self._init_embedder()
        self._init_vector_db()
    
    def _init_embedder(self):
        """Initialize real embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.use_real_embedding = True
            print(f"[MemoryX] Using real embeddings: all-MiniLM-L6-v2 (dim={self.embedding_dim})")
        except ImportError:
            print("[MemoryX] sentence-transformers not installed, using fallback")
            self.use_real_embedding = False
    
    def _init_vector_db(self):
        """Initialize vector database"""
        db_type = self.config.vector_db_type
        
        if db_type == "chroma":
            self._init_chroma()
        else:
            self._init_memory()
    
    def _init_chroma(self):
        """Initialize ChromaDB"""
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
            self._init_memory()
    
    def _init_memory(self):
        """In-memory vector storage"""
        self.vectors = {}
        self.db_type = "memory"
    
    def encode(self, text: str) -> List[float]:
        """Generate text embedding"""
        if self.use_real_embedding:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        else:
            # Fallback: simple hash
            import hashlib
            hash_val = hashlib.md5(text.encode()).digest()
            vector = np.frombuffer(hash_val, dtype=np.float32)
            vector = vector / (np.linalg.norm(vector) + 1e-8)
            full_vector = np.zeros(self.embedding_dim, dtype=np.float32)
            full_vector[:len(vector)] = vector
            return full_vector.tolist()
    
    def add(self, memory_id: str, embedding: List[float], 
            user_id: str, level: str = None):
        """Add vector"""
        if self.db_type == "chroma":
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                metadatas=[{"user_id": user_id, "level": level or ""}]
            )
        elif self.db_type == "memory":
            self.vectors[memory_id] = {
                "embedding": embedding,
                "user_id": user_id,
                "level": level
            }
    
    def search(self, query: str, user_id: str, level: str = None,
               agent_id: str = None, limit: int = 5) -> List[Dict]:
        """Semantic search"""
        query_embedding = self.encode(query)
        
        if self.db_type == "chroma":
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,
                where={"user_id": user_id}
            )
            
            output = []
            for i, mem_id in enumerate(results["ids"][0]):
                output.append({
                    "id": mem_id,
                    "score": 1 - results["distances"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
            return output
        
        elif self.db_type == "memory":
            query_vec = np.array(query_embedding)
            results = []
            
            for mem_id, data in self.vectors.items():
                if data["user_id"] != user_id:
                    continue
                
                mem_vec = np.array(data["embedding"])
                similarity = float(np.dot(query_vec, mem_vec))
                
                results.append({
                    "id": mem_id,
                    "score": similarity,
                    "metadata": data
                })
            
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
        
        return []
    
    def delete(self, memory_id: str):
        """Delete vector"""
        if self.db_type == "chroma":
            self.collection.delete(ids=[memory_id])
        elif self.db_type == "memory":
            self.vectors.pop(memory_id, None)
    
    def close(self):
        """Close connections"""
        pass
