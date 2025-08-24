from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NonprofitBase(BaseModel):
    ein: str = Field(..., description="Employer Identification Number")
    name: str = Field(..., description="Organization name")
    ntee_code: Optional[str] = Field(None, description="NTEE classification code")
    ntee_description: Optional[str] = Field(None, description="NTEE code description")
    mission_description: Optional[str] = Field(None, description="Organization mission")
    
class NonprofitCreate(NonprofitBase):
    pass

class NonprofitUpdate(BaseModel):
    name: Optional[str] = None
    ntee_code: Optional[str] = None
    ntee_description: Optional[str] = None
    mission_description: Optional[str] = None

class NonprofitResponse(NonprofitBase):
    id: int
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    total_revenue: Optional[float] = None
    total_expenses: Optional[float] = None
    net_assets: Optional[float] = None
    tax_year: Optional[int] = None
    filing_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NonprofitSearch(BaseModel):
    query: str = Field(..., description="Search query")
    ntee_codes: Optional[List[str]] = Field(None, description="Filter by NTEE codes")
    revenue_min: Optional[float] = Field(None, description="Minimum revenue filter")
    revenue_max: Optional[float] = Field(None, description="Maximum revenue filter")
    limit: int = Field(default=20, le=100, description="Number of results to return")
    
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message for RAG chat")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI assistant response")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source documents used")
    conversation_id: str = Field(..., description="Conversation identifier")