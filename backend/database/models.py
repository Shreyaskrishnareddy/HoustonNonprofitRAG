from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Nonprofit(Base):
    __tablename__ = "nonprofits"
    
    id = Column(Integer, primary_key=True, index=True)
    ein = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    
    # Classification
    ntee_code = Column(String(10), index=True)
    ntee_description = Column(String(255))
    
    # Location
    street_address = Column(String(255))
    city = Column(String(100), index=True)
    state = Column(String(2), index=True)
    zip_code = Column(String(10), index=True)
    
    # Contact
    website = Column(String(255))
    phone = Column(String(20))
    
    # Financial data
    total_revenue = Column(Float)
    total_expenses = Column(Float)
    net_assets = Column(Float)
    
    # Form 990 data
    tax_year = Column(Integer, index=True)
    filing_type = Column(String(10))  # 990, 990EZ, 990PF, etc.
    
    # Text data for RAG
    mission_description = Column(Text)
    program_description = Column(Text)
    activities_description = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_location', 'city', 'state'),
        Index('idx_revenue', 'total_revenue'),
        Index('idx_ntee_revenue', 'ntee_code', 'total_revenue'),
    )

class NonprofitDocument(Base):
    """Table for storing document chunks for RAG system"""
    __tablename__ = "nonprofit_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    nonprofit_id = Column(Integer, nullable=False, index=True)
    document_type = Column(String(50), nullable=False)  # 'mission', 'programs', 'activities'
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_nonprofit_doc_type', 'nonprofit_id', 'document_type'),
    )