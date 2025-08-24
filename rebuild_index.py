#!/usr/bin/env python3
"""Rebuild embeddings index for Houston nonprofit data"""
import sys
import json
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from backend.services.simple_embedding_service import SimpleEmbeddingService

def main():
    # Load the data
    with open('data/processed/houston_nonprofits_sample.json', 'r') as f:
        nonprofits = json.load(f)
    
    print(f"Loaded {len(nonprofits)} nonprofits from JSON")
    
    # Create new embedding service and rebuild index
    service = SimpleEmbeddingService()
    service.create_embeddings_from_nonprofits(nonprofits)
    print(f'Rebuilt index with {len(nonprofits)} nonprofits')
    
    # Test search for Houston Food Bank specifically
    print("\nTesting search for 'Houston Food Bank largest nonprofits revenue':")
    results = service.semantic_search('Houston Food Bank largest nonprofits revenue', k=5)
    for i, result in enumerate(results):
        print(f'{i+1}. {result.get("name", "Unknown")} - Revenue: ${result.get("total_revenue", 0):,}')
    
    # Test search for largest by revenue directly
    print("\nTesting search for 'Houston nonprofits organizations':")
    results = service.semantic_search('Houston nonprofits organizations', k=10)
    print(f"Found {len(results)} results")
    
    # Sort by revenue to see top results
    results_by_revenue = sorted(results, key=lambda x: x.get("total_revenue", 0), reverse=True)
    print("\nTop 5 by revenue:")
    for i, result in enumerate(results_by_revenue[:5]):
        print(f'{i+1}. {result.get("name", "Unknown")} - Revenue: ${result.get("total_revenue", 0):,}')

if __name__ == "__main__":
    main()