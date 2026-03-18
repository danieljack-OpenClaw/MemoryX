# -*- coding: utf-8 -*-
"""
MemoryX Enhanced Semantic Search with Better Embeddings
"""

from typing import List, Dict
import numpy as np

from .config import Config


class SemanticSearch:
    """Enhanced Semantic Search with optimized embeddings"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_dim = 384
        self._init_embedder()
        self._init_vector_db()
    
    def _init_embedder(self):
        """Initialize optimized embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use a better model for semantic similarity
            # all-mpnet-base-v2 has better performance than all-MiniLM-L6-v2
            self.model = SentenceTransformer('all-mpnet-base-v2')
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.use_real_embedding = True
            print(f"[MemoryX] Using enhanced embeddings: all-mpnet-base-v2 (dim={self.embedding_dim})")
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
        """Generate optimized text embedding"""
        if self.use_real_embedding:
            # Use mean pooling for better semantic representation
            embedding = self.model.encode(
                text, 
                convert_to_numpy=True,
                normalize_embeddings=True  # Already normalized
            )
            return embedding.tolist()
        else:
            # Fallback
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple hash-based embedding as fallback"""
        import hashlib
        hash_val = hashlib.sha256(text.encode()).digest()
        vector = np.frombuffer(hash_val, dtype=np.float32)
        vector = vector / (np.linalg.norm(vector) + 1e-8)
        
        # Pad to required dimension
        full_vector = np.zeros(self.embedding_dim, dtype=np.float32)
        full_vector[:len(vector)] = vector
        return full_vector.tolist()
    
    def add(self, memory_id: str, embedding: List[float], 
            user_id: str, level: str = None):
        """Add vector to storage"""
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
        """Enhanced semantic search with re-ranking"""
        query_embedding = self.encode(query)
        
        if self.db_type == "chroma":
            return self._chroma_search(query_embedding, user_id, level, limit)
        elif self.db_type == "memory":
            return self._memory_search(query_embedding, user_id, level, limit)
        
        return []
    
    def _chroma_search(self, query_embedding: List[float], user_id: str, 
                     level: str, limit: int) -> List[Dict]:
        """ChromaDB search"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit * 3,  # Get more for re-ranking
            where={"user_id": user_id}
        )
        
        output = []
        for i, mem_id in enumerate(results["ids"][0]):
            # Convert distance to similarity (cosine)
            score = 1 - results["distances"][0][i]
            output.append({
                "id": mem_id,
                "score": score,
                "metadata": results["metadatas"][0][i]
            })
        
        # Sort by score
        output.sort(key=lambda x: x["score"], reverse=True)
        return output[:limit]
    
    def _memory_search(self, query_embedding: List[float], user_id: str,
                      level: str, limit: int) -> List[Dict]:
        """In-memory search"""
        query_vec = np.array(query_embedding)
        results = []
        
        for mem_id, data in self.vectors.items():
            if data["user_id"] != user_id:
                continue
            
            if level and data.get("level") != level:
                continue
            
            # Cosine similarity
            mem_vec = np.array(data["embedding"])
            similarity = float(np.dot(query_vec, mem_vec))
            
            results.append({
                "id": mem_id,
                "score": similarity,
                "metadata": data
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def delete(self, memory_id: str):
        """Delete vector"""
        if self.db_type == "chroma":
            self.collection.delete(ids=[memory_id])
        elif self.db_type == "memory":
            self.vectors.pop(memory_id, None)
    
    def close(self):
        """Close connections"""
        pass
