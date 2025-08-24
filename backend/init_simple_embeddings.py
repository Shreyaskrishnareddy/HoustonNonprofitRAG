"""
Initialize TF-IDF embeddings for Houston nonprofit data
This script loads all nonprofit data and creates vector embeddings using scikit-learn
"""
import json
import sys
import os
from pathlib import Path

# Add backend to path so we can import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.simple_embedding_service import SimpleEmbeddingService

def load_nonprofit_data():
    """Load all nonprofit data from JSON files"""
    nonprofits = []
    data_dir = Path("../data/processed")
    
    # Load sample data
    sample_file = data_dir / "houston_nonprofits_sample.json"
    if sample_file.exists():
        print(f"Loading sample data from {sample_file}")
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)
            nonprofits.extend(sample_data)
    
    # Load summary data if available
    summary_file = data_dir / "houston_nonprofits_summary.json"
    if summary_file.exists():
        print(f"Loading summary data from {summary_file}")
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
            if isinstance(summary_data, list):
                # Filter out duplicates by EIN
                existing_eins = {org.get('ein') for org in nonprofits if org.get('ein')}
                for org in summary_data:
                    if org.get('ein') and org['ein'] not in existing_eins:
                        nonprofits.append(org)
                        existing_eins.add(org['ein'])
    
    print(f"Loaded {len(nonprofits)} total nonprofit organizations")
    return nonprofits

def main():
    """Main function to initialize embeddings"""
    print("🚀 Initializing Houston Nonprofit RAG System (TF-IDF)")
    print("=" * 55)
    
    try:
        # Load nonprofit data
        nonprofits = load_nonprofit_data()
        
        if not nonprofits:
            print("❌ No nonprofit data found. Please ensure data files exist in ../data/processed/")
            return
        
        # Initialize embedding service
        print("\n📊 Initializing TF-IDF embedding service...")
        embedding_service = SimpleEmbeddingService()
        
        # Create embeddings
        print("🔄 Creating TF-IDF vector embeddings...")
        embedding_service.create_embeddings_from_nonprofits(nonprofits)
        
        # Test the system
        print("\n🧪 Testing search functionality...")
        test_queries = [
            "food bank hungry feeding people",
            "education school children learning", 
            "health medical hospital care",
            "arts culture museum music",
            "homeless shelter housing",
            "environment conservation nature"
        ]
        
        for query in test_queries:
            results = embedding_service.semantic_search(query, k=2)
            if results:
                top_result = results[0]
                score = top_result.get('_score', 0)
                print(f"  Query: '{query}' → {top_result['name']} (score: {score:.3f})")
        
        # Display statistics
        stats = embedding_service.get_index_stats()
        print(f"\n📈 System Statistics:")
        print(f"  • Total organizations: {stats['num_documents']}")
        print(f"  • Embedding type: {stats['embedding_type']}")
        print(f"  • Vocabulary size: {stats['vocabulary_size']}")
        print(f"  • Max features: {stats['max_features']}")
        
        print("\n✅ Houston Nonprofit RAG System initialized successfully!")
        print("   You can now start the backend server and use the chat functionality.")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()