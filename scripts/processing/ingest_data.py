#!/usr/bin/env python3
"""
Script to ingest Houston nonprofit data into the database
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.database.database import create_tables, SessionLocal
from backend.services.data_service import DataIngestionService

def main():
    """Ingest sample data into the database"""
    
    # Create tables if they don't exist
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create ingestion service
        ingestion_service = DataIngestionService(db)
        
        # Path to sample data
        data_file = Path(__file__).parent.parent.parent / "data" / "processed" / "houston_nonprofits_sample.json"
        
        if not data_file.exists():
            print(f"Data file not found: {data_file}")
            print("Please run the sample data generation script first.")
            return
        
        print(f"Ingesting data from: {data_file}")
        
        # Ingest the data
        result = ingestion_service.ingest_from_json(str(data_file))
        
        print(f"Ingestion complete!")
        print(f"  Created: {result['created']} organizations")
        print(f"  Updated: {result['updated']} organizations")
        print(f"  Errors: {result['errors']} organizations")
        print(f"  Total processed: {result['total_processed']} organizations")
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()