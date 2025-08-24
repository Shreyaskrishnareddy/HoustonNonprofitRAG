import json
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database.models import Nonprofit, NonprofitDocument
from ..models.nonprofit import NonprofitCreate, NonprofitSearch

class NonprofitService:
    """Service for managing nonprofit data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_nonprofit(self, nonprofit_data: dict) -> Nonprofit:
        """Create a new nonprofit record"""
        db_nonprofit = Nonprofit(**nonprofit_data)
        self.db.add(db_nonprofit)
        self.db.commit()
        self.db.refresh(db_nonprofit)
        return db_nonprofit
    
    def get_nonprofit_by_ein(self, ein: str) -> Optional[Nonprofit]:
        """Get nonprofit by EIN"""
        return self.db.query(Nonprofit).filter(Nonprofit.ein == ein).first()
    
    def get_nonprofits(
        self, 
        skip: int = 0, 
        limit: int = 100,
        ntee_code: Optional[str] = None,
        search: Optional[str] = None,
        min_revenue: Optional[float] = None,
        max_revenue: Optional[float] = None
    ) -> List[Nonprofit]:
        """Get nonprofits with optional filtering"""
        query = self.db.query(Nonprofit)
        
        # Apply filters
        if ntee_code:
            query = query.filter(Nonprofit.ntee_code == ntee_code)
        
        if search:
            search_filter = or_(
                Nonprofit.name.ilike(f"%{search}%"),
                Nonprofit.mission_description.ilike(f"%{search}%"),
                Nonprofit.program_description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if min_revenue is not None:
            query = query.filter(Nonprofit.total_revenue >= min_revenue)
        
        if max_revenue is not None:
            query = query.filter(Nonprofit.total_revenue <= max_revenue)
        
        return query.offset(skip).limit(limit).all()
    
    def get_nonprofit_count(self) -> int:
        """Get total count of nonprofits"""
        return self.db.query(Nonprofit).count()
    
    def get_ntee_distribution(self) -> dict:
        """Get distribution of organizations by NTEE code"""
        from sqlalchemy import func
        
        results = self.db.query(
            Nonprofit.ntee_code,
            Nonprofit.ntee_description,
            func.count(Nonprofit.id).label('count')
        ).group_by(
            Nonprofit.ntee_code, 
            Nonprofit.ntee_description
        ).all()
        
        return [
            {
                'code': r.ntee_code,
                'description': r.ntee_description,
                'count': r.count
            }
            for r in results
        ]
    
    def get_financial_summary(self) -> dict:
        """Get financial summary statistics"""
        from sqlalchemy import func
        
        result = self.db.query(
            func.sum(Nonprofit.total_revenue).label('total_revenue'),
            func.sum(Nonprofit.total_expenses).label('total_expenses'),
            func.sum(Nonprofit.net_assets).label('total_assets'),
            func.avg(Nonprofit.total_revenue).label('avg_revenue'),
            func.count(Nonprofit.id).label('total_orgs')
        ).first()
        
        return {
            'total_revenue': float(result.total_revenue or 0),
            'total_expenses': float(result.total_expenses or 0),
            'total_assets': float(result.total_assets or 0),
            'average_revenue': float(result.avg_revenue or 0),
            'total_organizations': result.total_orgs
        }
    
    def add_document_chunk(
        self, 
        nonprofit_id: int, 
        content: str, 
        document_type: str
    ) -> NonprofitDocument:
        """Add a document chunk for RAG system"""
        # Create content hash to avoid duplicates
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Check if already exists
        existing = self.db.query(NonprofitDocument).filter(
            NonprofitDocument.content_hash == content_hash
        ).first()
        
        if existing:
            return existing
        
        # Create new document
        doc = NonprofitDocument(
            nonprofit_id=nonprofit_id,
            document_type=document_type,
            content=content,
            content_hash=content_hash
        )
        
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc
    
    def get_documents_for_rag(self, limit: int = 1000) -> List[NonprofitDocument]:
        """Get document chunks for RAG system"""
        return self.db.query(NonprofitDocument).limit(limit).all()

class DataIngestionService:
    """Service for ingesting nonprofit data from files"""
    
    def __init__(self, db: Session):
        self.db = db
        self.nonprofit_service = NonprofitService(db)
    
    def ingest_from_json(self, file_path: str) -> dict:
        """Ingest nonprofit data from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for nonprofit_data in data:
            try:
                ein = nonprofit_data.get('ein')
                if not ein:
                    error_count += 1
                    continue
                
                # Check if nonprofit already exists
                existing = self.nonprofit_service.get_nonprofit_by_ein(ein)
                
                # Filter out fields that don't exist in the model
                filtered_data = {}
                for key, value in nonprofit_data.items():
                    if hasattr(Nonprofit, key) and key != 'id':
                        filtered_data[key] = value
                
                if existing:
                    # Update existing record
                    for key, value in filtered_data.items():
                        setattr(existing, key, value)
                    self.db.commit()
                    updated_count += 1
                else:
                    # Create new record
                    self.nonprofit_service.create_nonprofit(filtered_data)
                    created_count += 1
                
                # Add document chunks for RAG
                if existing or created_count > 0:
                    nonprofit = existing or self.nonprofit_service.get_nonprofit_by_ein(ein)
                    self._create_document_chunks(nonprofit, nonprofit_data)
                    
            except Exception as e:
                print(f"Error processing nonprofit {nonprofit_data.get('name', 'Unknown')}: {e}")
                error_count += 1
        
        return {
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'total_processed': len(data)
        }
    
    def _create_document_chunks(self, nonprofit: Nonprofit, data: dict):
        """Create document chunks for RAG system"""
        # Mission description
        if data.get('mission_description'):
            self.nonprofit_service.add_document_chunk(
                nonprofit.id,
                data['mission_description'],
                'mission'
            )
        
        # Program description
        if data.get('program_description'):
            self.nonprofit_service.add_document_chunk(
                nonprofit.id,
                data['program_description'],
                'programs'
            )
        
        # Activities description
        if data.get('activities_description'):
            self.nonprofit_service.add_document_chunk(
                nonprofit.id,
                data['activities_description'],
                'activities'
            )
        
        # Combined summary for better context
        summary_parts = []
        summary_parts.append(f"Organization: {nonprofit.name}")
        summary_parts.append(f"NTEE Code: {nonprofit.ntee_code} - {nonprofit.ntee_description}")
        if data.get('mission_description'):
            summary_parts.append(f"Mission: {data['mission_description']}")
        if nonprofit.total_revenue:
            summary_parts.append(f"Annual Revenue: ${nonprofit.total_revenue:,.2f}")
        
        summary = ". ".join(summary_parts)
        self.nonprofit_service.add_document_chunk(
            nonprofit.id,
            summary,
            'summary'
        )