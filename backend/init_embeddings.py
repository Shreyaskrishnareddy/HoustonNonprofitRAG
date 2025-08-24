"""
Initialize embeddings for Houston nonprofit data
This script loads all nonprofit data and creates vector embeddings
"""
import json
import sys
import os
from pathlib import Path

# Add backend to path so we can import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.embedding_service import EmbeddingService

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
                nonprofits.extend(summary_data)
    
    print(f"Loaded {len(nonprofits)} total nonprofit organizations")
    return nonprofits

def main():
    """Main function to initialize embeddings"""
    print("🚀 Initializing Houston Nonprofit RAG System")
    print("=" * 50)
    
    try:
        # Load nonprofit data
        nonprofits = load_nonprofit_data()
        
        if not nonprofits:
            print("❌ No nonprofit data found. Please ensure data files exist in ../data/processed/")
            return
        
        # Initialize embedding service
        print("\n📊 Initializing embedding service...")
        embedding_service = EmbeddingService()
        
        # Create embeddings
        print("🔄 Creating vector embeddings...")
        embedding_service.create_embeddings_from_nonprofits(nonprofits)
        
        # Test the system
        print("\n🧪 Testing search functionality...")
        test_queries = [
            "food bank hungry feeding people",
            "education school children learning",
            "health medical hospital care",
            "arts culture museum music"
        ]
        
        for query in test_queries:
            results = embedding_service.semantic_search(query, k=2)
            if results:
                print(f"  Query: '{query}' → Found: {results[0]['name']}")
        
        # Display statistics
        stats = embedding_service.get_index_stats()
        print(f"\n📈 System Statistics:")
        print(f"  • Total organizations: {stats['num_documents']}")
        print(f"  • Embedding model: {stats['model_name']}")
        print(f"  • Vector dimension: {stats['embedding_dimension']}")
        
        print("\n✅ Houston Nonprofit RAG System initialized successfully!")
        print("   You can now start the backend server and use the chat functionality.")
        
    except Exception as e:
        print(f"❌ Error initializing system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()