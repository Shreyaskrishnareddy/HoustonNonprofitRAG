"""
Vector embedding service for Houston Nonprofit RAG System
Uses sentence-transformers and FAISS for semantic search
"""
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path

class EmbeddingService:
    """Service for creating and searching vector embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service
        
        Args:
            model_name: Sentence transformer model to use
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Paths for storing embeddings and index
        self.data_dir = Path("data/embeddings")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.data_dir / "faiss_index.bin"
        self.documents_path = self.data_dir / "documents.pkl"
        self.metadata_path = self.data_dir / "metadata.json"
        
        # Initialize FAISS index
        self.index = None
        self.documents = []
        self.metadata = {}
        
        # Load existing index if available
        self.load_index()
    
    def create_embeddings_from_nonprofits(self, nonprofits: List[Dict[str, Any]]) -> None:
        """
        Create embeddings from nonprofit data
        
        Args:
            nonprofits: List of nonprofit dictionaries
        """
        print(f"Creating embeddings for {len(nonprofits)} nonprofits...")
        
        # Prepare documents for embedding
        documents = []
        for org in nonprofits:
            # Create comprehensive text representation
            doc_text = self._create_document_text(org)
            documents.append(doc_text)
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.model.encode(documents, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        print("Creating FAISS index...")
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner Product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents and metadata
        self.documents = nonprofits
        self.metadata = {
            "num_documents": len(nonprofits),
            "embedding_dim": self.embedding_dim,
            "model_name": self.model_name,
            "created_at": str(np.datetime64('now'))
        }
        
        # Save to disk
        self.save_index()
        print(f"✅ Successfully created and saved embeddings for {len(nonprofits)} nonprofits")
    
    def _create_document_text(self, org: Dict[str, Any]) -> str:
        """Create searchable text from nonprofit data"""
        parts = []
        
        # Basic info
        if org.get('name'):
            parts.append(f"Organization: {org['name']}")
        
        # Mission and programs (most important for search)
        if org.get('mission_description'):
            parts.append(f"Mission: {org['mission_description']}")
        
        if org.get('program_description'):
            parts.append(f"Programs: {org['program_description']}")
        
        if org.get('activities_description'):
            parts.append(f"Activities: {org['activities_description']}")
        
        # Category
        if org.get('ntee_description'):
            parts.append(f"Category: {org['ntee_description']}")
        
        # Location
        if org.get('city') and org.get('state'):
            parts.append(f"Location: {org['city']}, {org['state']}")
        
        return " ".join(parts)
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search for nonprofits
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant nonprofit documents with scores
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.documents):
                    result = self.documents[idx].copy()
                    result['_score'] = float(score)
                    result['_rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def save_index(self) -> None:
        """Save FAISS index and documents to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
            
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                
            print("✅ Index saved successfully")
            
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def load_index(self) -> bool:
        """Load FAISS index and documents from disk"""
        try:
            if not all(p.exists() for p in [self.index_path, self.documents_path, self.metadata_path]):
                return False
            
            # Load index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load documents
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            # Load metadata
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            print(f"✅ Loaded index with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            print(f"Could not load existing index: {e}")
            return False
    
    def get_similar_organizations(self, org_name: str, k: int = 3) -> List[Dict[str, Any]]:
        """Find organizations similar to a given organization"""
        if not self.documents:
            return []
        
        # Find the organization
        target_org = None
        for org in self.documents:
            if org.get('name', '').lower() == org_name.lower():
                target_org = org
                break
        
        if not target_org:
            return []
        
        # Use its description for similarity search
        query = f"{target_org.get('mission_description', '')} {target_org.get('program_description', '')}"
        results = self.semantic_search(query, k + 1)  # +1 to exclude self
        
        # Filter out the original organization
        similar = [r for r in results if r.get('name', '').lower() != org_name.lower()]
        return similar[:k]
    
    def get_organizations_by_category(self, category_keywords: str, k: int = 10) -> List[Dict[str, Any]]:
        """Get organizations by category or cause area"""
        return self.semantic_search(f"organizations working on {category_keywords}", k)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        if self.index is None:
            return {"status": "No index loaded"}
        
        return {
            "num_documents": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "model_name": self.model_name,
            "index_size": self.index.ntotal,
            "metadata": self.metadata
        }
    
    def rebuild_index_if_needed(self, nonprofits: List[Dict[str, Any]]) -> None:
        """Rebuild index if data has changed or doesn't exist"""
        should_rebuild = (
            self.index is None or 
            len(self.documents) == 0 or 
            len(nonprofits) != len(self.documents)
        )
        
        if should_rebuild:
            print("Rebuilding vector index...")
            self.create_embeddings_from_nonprofits(nonprofits)
        else:
            print("Vector index is up to date")