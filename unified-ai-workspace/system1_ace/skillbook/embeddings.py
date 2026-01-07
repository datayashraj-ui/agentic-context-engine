"""
Embedding manager for semantic skill search

Uses sentence-transformers for generating embeddings
and ChromaDB for vector storage
"""

from typing import List, Dict, Any, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from core.config import get_config
from core.database import get_database


class EmbeddingManager:
    """
    Manages embeddings for semantic search of skills

    Uses:
    - sentence-transformers for embedding generation
    - ChromaDB for vector storage and similarity search
    """

    def __init__(self, model_name: Optional[str] = None):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")

        config = get_config()
        self.model_name = model_name or config.database.embedding_model
        self.model = SentenceTransformer(self.model_name)

        # Get ChromaDB collection from database
        db = get_database()
        if db.vector_db:
            self.collection = db.vector_db.get_or_create_collection(
                name="skills",
                metadata={"description": "Prompt engineering skills embeddings"}
            )
        else:
            self.collection = None
            print("Warning: ChromaDB not available. Semantic search disabled.")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return embeddings.tolist()

    def store_embedding(
        self,
        skill_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """
        Store embedding in vector database

        Args:
            skill_id: Unique identifier for the skill
            embedding: Embedding vector
            metadata: Additional metadata to store
        """
        if not self.collection:
            return

        self.collection.upsert(
            ids=[skill_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar skills

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            filter_metadata: Optional metadata filters

        Returns:
            List of results with id, distance, and metadata
        """
        if not self.collection:
            return []

        where = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where
        )

        # Format results
        formatted = []
        if results['ids'] and results['ids'][0]:
            for i, skill_id in enumerate(results['ids'][0]):
                formatted.append({
                    'id': skill_id,
                    'distance': results['distances'][0][i] if results['distances'] else 0,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })

        return formatted

    def delete_embedding(self, skill_id: str):
        """Delete embedding from vector database"""
        if not self.collection:
            return

        try:
            self.collection.delete(ids=[skill_id])
        except:
            pass  # ID might not exist
