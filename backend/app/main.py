from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from ..database.database import get_db, create_tables
from ..services.data_service import NonprofitService
from ..services.rag_service import RAGService
from ..models.nonprofit import ChatMessage, ChatResponse

load_dotenv()

# Create tables on startup
create_tables()

# Initialize RAG service
rag_service = RAGService()

app = FastAPI(
    title="Houston Nonprofit RAG API",
    description="API for Houston nonprofit data analysis with RAG capabilities",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize RAG service on startup"""
    await rag_service.initialize_with_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Houston Nonprofit RAG API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/nonprofits")
async def get_nonprofits(
    limit: int = 100,
    offset: int = 0,
    ntee_code: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get nonprofit organizations with optional filtering"""
    service = NonprofitService(db)
    nonprofits = service.get_nonprofits(
        skip=offset,
        limit=limit,
        ntee_code=ntee_code,
        search=search
    )
    
    # Convert to dict format for JSON response
    result = []
    for np in nonprofits:
        result.append({
            "id": np.id,
            "ein": np.ein,
            "name": np.name,
            "ntee_code": np.ntee_code,
            "ntee_description": np.ntee_description,
            "city": np.city,
            "state": np.state,
            "total_revenue": np.total_revenue,
            "total_expenses": np.total_expenses,
            "net_assets": np.net_assets,
            "mission_description": np.mission_description,
            "website": np.website
        })
    
    return {
        "nonprofits": result,
        "total": len(result),
        "offset": offset,
        "limit": limit
    }

@app.get("/api/stats/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    service = NonprofitService(db)
    
    financial_summary = service.get_financial_summary()
    ntee_distribution = service.get_ntee_distribution()
    
    # Top 5 categories by count
    top_categories = sorted(ntee_distribution, key=lambda x: x['count'], reverse=True)[:5]
    
    return {
        "total_nonprofits": financial_summary['total_organizations'],
        "total_revenue": financial_summary['total_revenue'],
        "total_expenses": financial_summary['total_expenses'],
        "total_assets": financial_summary['total_assets'],
        "average_revenue": financial_summary['average_revenue'],
        "top_categories": top_categories,
        "ntee_distribution": ntee_distribution
    }

@app.post("/api/chat")
async def chat_with_rag(message: ChatMessage, db: Session = Depends(get_db)):
    """Chat endpoint for RAG-powered Q&A about nonprofits"""
    try:
        # Use RAG service for intelligent responses
        rag_response = await rag_service.chat(
            query=message.message,
            conversation_id=message.conversation_id or "default"
        )
        
        return ChatResponse(
            response=rag_response["response"],
            sources=rag_response["sources"],
            conversation_id=rag_response["conversation_id"]
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"I encountered an error while processing your question: {str(e)}",
            sources=[],
            conversation_id=message.conversation_id or "default"
        )

@app.get("/api/chat/suggestions")
async def get_chat_suggestions():
    """Get suggested questions for users"""
    suggestions = await rag_service.suggest_questions()
    return {"suggestions": suggestions}

@app.get("/api/search/semantic")
async def semantic_search(query: str, limit: int = 10):
    """Perform semantic search across nonprofits"""
    try:
        results = rag_service.embedding_service.semantic_search(query, k=limit)
        return {"results": results, "query": query, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/organization/{org_name}")
async def get_organization_details(org_name: str):
    """Get detailed information about a specific organization"""
    result = await rag_service.get_organization_details(org_name)
    if result.get("found"):
        return result
    else:
        raise HTTPException(status_code=404, detail="Organization not found")

@app.get("/api/insights/financial")
async def get_financial_insights(query: str = "nonprofit financial overview"):
    """Get financial insights"""
    result = await rag_service.get_financial_insights(query)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/api/system/stats")
async def get_system_stats():
    """Get RAG system statistics"""
    return rag_service.get_system_stats()

@app.get("/api/system/health")
async def rag_health_check():
    """Check RAG system health"""
    healthy = await rag_service.health_check()
    if healthy:
        return {"status": "healthy", "rag_enabled": True}
    else:
        return {"status": "degraded", "rag_enabled": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)