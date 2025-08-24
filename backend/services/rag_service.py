"""
RAG (Retrieval-Augmented Generation) service for Houston Nonprofit System
Combines semantic search with LLM generation
"""
from typing import List, Dict, Any, Optional
from .simple_embedding_service import SimpleEmbeddingService
from .groq_service import GroqService
from .data_service import NonprofitService
import asyncio

class RAGService:
    """Main RAG service combining retrieval and generation"""
    
    def __init__(self):
        self.embedding_service = SimpleEmbeddingService()
        self.groq_service = GroqService()
        self.nonprofit_service = None  # Will be set when we have DB session
        
    async def initialize_with_data(self, db_session=None):
        """Initialize RAG service with nonprofit data"""
        try:
            if db_session:
                self.nonprofit_service = NonprofitService(db_session)
            
            # Load nonprofit data from processed JSON files
            import json
            from pathlib import Path
            
            # Try to load from processed data
            processed_file = Path("data/processed/houston_nonprofits_sample.json")
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    nonprofits = json.load(f)
                
                # Rebuild index if needed
                self.embedding_service.rebuild_index_if_needed(nonprofits)
                print(f"✅ RAG service initialized with {len(nonprofits)} nonprofits")
                
            else:
                print("⚠️ No processed nonprofit data found")
                
        except Exception as e:
            print(f"Error initializing RAG service: {e}")
    
    async def chat(self, query: str, conversation_id: str = "default") -> Dict[str, Any]:
        """
        Main chat interface for RAG system
        
        Args:
            query: User's question
            conversation_id: Conversation identifier
            
        Returns:
            Dict with response, sources, and metadata
        """
        try:
            # Check if this is a question about "largest" or "biggest" nonprofits
            query_lower = query.lower()
            is_size_query = any(term in query_lower for term in ["largest", "biggest", "major", "top", "leading", "impact"])
            
            if is_size_query:
                # For size/impact queries, get ALL documents and sort by financial metrics
                # Load all documents from the embedding service
                all_docs = self.embedding_service.documents if hasattr(self.embedding_service, 'documents') else []
                
                if not all_docs:
                    # Fallback to semantic search
                    relevant_docs = self.embedding_service.semantic_search("Houston", k=50)
                else:
                    # Use all available documents
                    relevant_docs = all_docs.copy()
                
                if relevant_docs:
                    # Sort by total revenue (primary impact indicator)
                    relevant_docs.sort(key=lambda x: x.get("total_revenue", 0), reverse=True)
                    relevant_docs = relevant_docs[:10]  # Top 10 by revenue
            else:
                # Step 1: Regular semantic search
                relevant_docs = self.embedding_service.semantic_search(query, k=5)
            
            if not relevant_docs:
                return {
                    "response": "I don't have enough information about Houston nonprofits to answer that question. Please try a different query.",
                    "sources": [],
                    "conversation_id": conversation_id,
                    "query": query,
                    "retrieved_count": 0
                }
            
            # Step 2: Generate response using Groq
            response = await self.groq_service.generate_rag_response(
                query=query,
                context_docs=relevant_docs
            )
            
            # Step 3: Prepare sources
            sources = []
            for doc in relevant_docs:
                source = {
                    "name": doc.get("name", "Unknown"),
                    "ein": doc.get("ein", ""),
                    "category": doc.get("ntee_description", ""),
                    "website": doc.get("website", ""),
                    "relevance_score": round(doc.get("_score", 0), 3),
                    "revenue": doc.get("total_revenue", 0)
                }
                sources.append(source)
            
            return {
                "response": response,
                "sources": sources,
                "conversation_id": conversation_id,
                "query": query,
                "retrieved_count": len(relevant_docs)
            }
            
        except Exception as e:
            print(f"Error in RAG chat: {e}")
            return {
                "response": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "conversation_id": conversation_id,
                "query": query,
                "retrieved_count": 0
            }
    
    async def get_organization_details(self, org_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific organization"""
        try:
            # Search for the organization
            results = self.embedding_service.semantic_search(f"organization named {org_name}", k=3)
            
            if not results:
                return {"error": "Organization not found"}
            
            # Get the best match
            org = results[0]
            
            # Get similar organizations
            similar = self.embedding_service.get_similar_organizations(org_name, k=3)
            
            return {
                "organization": org,
                "similar_organizations": similar,
                "found": True
            }
            
        except Exception as e:
            return {"error": str(e), "found": False}
    
    async def get_organizations_by_cause(self, cause: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find organizations working on a specific cause"""
        try:
            query = f"nonprofits organizations working on {cause} programs services"
            results = self.embedding_service.semantic_search(query, k=limit)
            return results
            
        except Exception as e:
            print(f"Error searching by cause: {e}")
            return []
    
    async def get_financial_insights(self, query: str) -> Dict[str, Any]:
        """Get insights about nonprofit financial data"""
        try:
            # Search for relevant organizations
            orgs = self.embedding_service.semantic_search(query, k=20)
            
            if not orgs:
                return {"error": "No relevant organizations found"}
            
            # Calculate financial insights
            total_revenue = sum(org.get("total_revenue", 0) for org in orgs)
            total_expenses = sum(org.get("total_expenses", 0) for org in orgs)
            avg_revenue = total_revenue / len(orgs) if orgs else 0
            
            # Generate insights with Groq
            financial_context = f"""
            Found {len(orgs)} relevant organizations:
            - Total combined revenue: ${total_revenue:,}
            - Total combined expenses: ${total_expenses:,}
            - Average revenue: ${avg_revenue:,}
            
            Top organizations by revenue:
            {chr(10).join([f"- {org.get('name', 'Unknown')}: ${org.get('total_revenue', 0):,}" for org in orgs[:5]])}
            """
            
            insight = await self.groq_service.generate_rag_response(
                query=f"Provide financial insights for: {query}",
                context_docs=orgs[:5]
            )
            
            return {
                "insight": insight,
                "statistics": {
                    "total_revenue": total_revenue,
                    "total_expenses": total_expenses,
                    "average_revenue": avg_revenue,
                    "organization_count": len(orgs)
                },
                "top_organizations": orgs[:5]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def suggest_questions(self) -> List[str]:
        """Suggest sample questions users can ask"""
        return [
            "What are the largest nonprofits in Houston?",
            "Tell me about organizations helping with food insecurity",
            "Which nonprofits focus on education in Houston?",
            "Show me health-related nonprofits with their financial information",
            "What organizations work with homeless populations?",
            "Find nonprofits focused on arts and culture",
            "Which organizations have the highest revenue?",
            "Tell me about environmental nonprofits in Houston",
            "What nonprofits serve children and youth?",
            "Show me organizations working on community development"
        ]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        embedding_stats = self.embedding_service.get_index_stats()
        
        return {
            "embedding_service": embedding_stats,
            "groq_service": {
                "model": self.groq_service.model,
                "api_configured": bool(self.groq_service.api_key)
            },
            "status": "operational" if embedding_stats.get("num_documents", 0) > 0 else "no_data"
        }
    
    async def health_check(self) -> bool:
        """Check if RAG service is healthy"""
        try:
            # Check embedding service
            if self.embedding_service.embeddings is None:
                return False
            
            # Check Groq service
            groq_healthy = await self.groq_service.health_check()
            
            return groq_healthy
            
        except Exception as e:
            print(f"RAG health check failed: {e}")
            return False