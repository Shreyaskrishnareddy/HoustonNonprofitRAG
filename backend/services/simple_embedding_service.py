"""
Simple embedding service using TF-IDF for Houston Nonprofit RAG System
Lightweight alternative to sentence-transformers
"""
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import re

class SimpleEmbeddingService:
    """Simple embedding service using TF-IDF vectorization"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        # Paths for storing embeddings and index
        self.data_dir = Path("data/embeddings")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer_path = self.data_dir / "tfidf_vectorizer.pkl"
        self.embeddings_path = self.data_dir / "embeddings.npy"
        self.documents_path = self.data_dir / "documents.pkl"
        self.metadata_path = self.data_dir / "metadata.json"
        
        # Initialize storage
        self.embeddings = None
        self.documents = []
        self.metadata = {}
        
        # Load existing data if available
        self.load_index()
    
    def create_embeddings_from_nonprofits(self, nonprofits: List[Dict[str, Any]]) -> None:
        """
        Create TF-IDF embeddings from nonprofit data
        
        Args:
            nonprofits: List of nonprofit dictionaries
        """
        print(f"Creating TF-IDF embeddings for {len(nonprofits)} nonprofits...")
        
        # Prepare documents for embedding
        documents = []
        for org in nonprofits:
            doc_text = self._create_document_text(org)
            documents.append(doc_text)
        
        # Generate TF-IDF embeddings
        print("Generating TF-IDF vectors...")
        self.embeddings = self.vectorizer.fit_transform(documents)
        
        # Store documents and metadata
        self.documents = nonprofits
        self.metadata = {
            "num_documents": len(nonprofits),
            "embedding_type": "tfidf",
            "max_features": self.vectorizer.max_features,
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
        
        text = " ".join(parts)
        # Clean up the text
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search for nonprofits using TF-IDF similarity
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant nonprofit documents with scores
        """
        if self.embeddings is None or len(self.documents) == 0:
            return []
        
        try:
            # Clean query
            query = re.sub(r'[^\w\s]', ' ', query)
            query = re.sub(r'\s+', ' ', query).strip()
            
            # Transform query using fitted vectorizer
            query_vector = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, self.embeddings).flatten()
            
            # Get top k indices
            top_indices = similarities.argsort()[-k:][::-1]
            
            # Prepare results
            results = []
            for i, idx in enumerate(top_indices):
                # Lower threshold to include more results (even very small similarities)
                if similarities[idx] >= 0:  # Include all non-negative similarities
                    result = self.documents[idx].copy()
                    result['_score'] = float(similarities[idx])
                    result['_rank'] = i + 1
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    def save_index(self) -> None:
        """Save TF-IDF vectorizer and embeddings to disk"""
        try:
            # Save vectorizer
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            # Save embeddings
            if self.embeddings is not None:
                np.save(self.embeddings_path, self.embeddings.toarray())
            
            # Save documents
            with open(self.documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                
            print("✅ Index saved successfully")
            
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def load_index(self) -> bool:
        """Load TF-IDF vectorizer and embeddings from disk"""
        try:
            required_files = [self.vectorizer_path, self.embeddings_path, 
                            self.documents_path, self.metadata_path]
            
            if not all(p.exists() for p in required_files):
                return False
            
            # Load vectorizer
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # Load embeddings
            embeddings_array = np.load(self.embeddings_path)
            # Convert back to sparse matrix for memory efficiency
            from scipy.sparse import csr_matrix
            self.embeddings = csr_matrix(embeddings_array)
            
            # Load documents
            with open(self.documents_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            # Load metadata
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            print(f"✅ Loaded TF-IDF index with {len(self.documents)} documents")
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
        query_parts = []
        if target_org.get('mission_description'):
            query_parts.append(target_org['mission_description'])
        if target_org.get('program_description'):
            query_parts.append(target_org['program_description'])
        if target_org.get('ntee_description'):
            query_parts.append(target_org['ntee_description'])
        
        query = " ".join(query_parts)
        results = self.semantic_search(query, k + 1)  # +1 to exclude self
        
        # Filter out the original organization
        similar = [r for r in results if r.get('name', '').lower() != org_name.lower()]
        return similar[:k]
    
    def get_organizations_by_category(self, category_keywords: str, k: int = 10) -> List[Dict[str, Any]]:
        """Get organizations by category or cause area"""
        return self.semantic_search(f"organizations working on {category_keywords}", k)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        if self.embeddings is None:
            return {"status": "No index loaded"}
        
        return {
            "num_documents": len(self.documents),
            "embedding_type": "TF-IDF",
            "max_features": getattr(self.vectorizer, 'max_features', 0),
            "vocabulary_size": len(getattr(self.vectorizer, 'vocabulary_', {})),
            "embedding_shape": self.embeddings.shape if self.embeddings is not None else None,
            "metadata": self.metadata
        }
    
    def rebuild_index_if_needed(self, nonprofits: List[Dict[str, Any]]) -> None:
        """Rebuild index if data has changed or doesn't exist"""
        should_rebuild = (
            self.embeddings is None or 
            len(self.documents) == 0 or 
            len(nonprofits) != len(self.documents)
        )
        
        if should_rebuild:
            print("Rebuilding TF-IDF index...")
            self.create_embeddings_from_nonprofits(nonprofits)
        else:
            print("TF-IDF index is up to date")
    
    def get_top_terms_for_query(self, query: str, n_terms: int = 10) -> List[str]:
        """Get top TF-IDF terms for a query"""
        if not hasattr(self.vectorizer, 'vocabulary_'):
            return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get non-zero features and their scores
            nonzero_features = query_vector.nonzero()[1]
            scores = [(feature_names[i], query_vector[0, i]) for i in nonzero_features]
            
            # Sort by score and return top terms
            scores.sort(key=lambda x: x[1], reverse=True)
            return [term for term, score in scores[:n_terms]]
            
        except Exception as e:
            print(f"Error getting top terms: {e}")
            return []