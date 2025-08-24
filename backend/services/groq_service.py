"""
Groq API integration for Houston Nonprofit RAG System
Provides LLM capabilities using Groq's fast inference
"""
import asyncio
from typing import List, Dict, Any, Optional
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    """Service for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Current production model
        
    async def generate_rag_response(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]],
        max_tokens: int = 1000
    ) -> str:
        """
        Generate RAG response using retrieved nonprofit documents
        
        Args:
            query: User's question
            context_docs: Retrieved nonprofit documents
            max_tokens: Maximum response length
            
        Returns:
            str: Generated response
        """
        try:
            # Format context from retrieved documents
            context_text = self._format_context(context_docs)
            
            # Create RAG prompt
            system_prompt = """You are a helpful assistant specializing in Houston nonprofit organizations. 
            You have access to detailed information about nonprofits including their missions, programs, 
            financial data, and activities. Provide accurate, helpful responses based on the provided context.
            
            When discussing financial information, format numbers clearly (e.g., $1.2M for millions).
            Focus on being informative and actionable for users interested in Houston nonprofits."""
            
            user_prompt = f"""Based on the following information about Houston nonprofits, please answer this question: {query}

Context:
{context_text}

Please provide a comprehensive answer based on the nonprofit data provided. If the context doesn't contain enough information to fully answer the question, mention what additional information might be helpful."""

            # Make async call to Groq
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self._sync_chat_completion,
                system_prompt,
                user_prompt,
                max_tokens
            )
            
            return response
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return f"I apologize, but I encountered an error while processing your question about Houston nonprofits. Please try rephrasing your question."
    
    def _sync_chat_completion(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Synchronous chat completion for use with executor"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error in sync chat completion: {e}")
            raise e
    
    def _format_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context text"""
        context_parts = []
        
        for i, doc in enumerate(context_docs[:5], 1):  # Limit to top 5 for token efficiency
            doc_text = f"""
Organization {i}: {doc.get('name', 'Unknown')}
- EIN: {doc.get('ein', 'N/A')}
- Category: {doc.get('ntee_description', 'N/A')} ({doc.get('ntee_code', 'N/A')})
- Mission: {doc.get('mission_description', 'N/A')}
- Programs: {doc.get('program_description', 'N/A')}
- Activities: {doc.get('activities_description', 'N/A')}
- Location: {doc.get('city', 'N/A')}, {doc.get('state', 'N/A')}
- Revenue: ${doc.get('total_revenue', 0):,}
- Expenses: ${doc.get('total_expenses', 0):,}
- Net Assets: ${doc.get('net_assets', 0):,}
- Website: {doc.get('website', 'N/A')}
"""
            context_parts.append(doc_text)
        
        return "\n".join(context_parts)
    
    async def generate_summary(self, nonprofits: List[Dict[str, Any]]) -> str:
        """Generate a summary of nonprofit organizations"""
        try:
            # Create summary data
            total_orgs = len(nonprofits)
            total_revenue = sum(org.get('total_revenue', 0) for org in nonprofits)
            categories = {}
            
            for org in nonprofits:
                category = org.get('ntee_description', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
            
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            
            prompt = f"""Please create a brief summary of Houston's nonprofit landscape based on this data:

Total Organizations: {total_orgs}
Combined Revenue: ${total_revenue:,}
Top Categories: {', '.join([f"{cat} ({count})" for cat, count in top_categories])}

Provide 2-3 sentences highlighting the diversity and impact of Houston's nonprofit sector."""

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self._sync_simple_completion,
                prompt
            )
            
            return response
            
        except Exception as e:
            return f"Houston has a diverse nonprofit sector with {len(nonprofits)} organizations serving the community across various causes."
    
    def _sync_simple_completion(self, prompt: str) -> str:
        """Simple completion for summaries"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.5
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise e
    
    async def health_check(self) -> bool:
        """Check if Groq service is working"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self._sync_simple_completion,
                "Say 'healthy' if you can respond."
            )
            return "healthy" in response.lower()
            
        except Exception:
            return False