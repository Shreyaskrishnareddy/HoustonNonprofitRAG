# 🏥 Houston Nonprofit RAG System

A sophisticated **Retrieval-Augmented Generation (RAG)** system that provides intelligent, data-driven insights about Houston's nonprofit organizations. Built with FastAPI, modern embeddings, and Groq LLM integration for fast, accurate responses about nonprofit financials, missions, programs, and impact.

## ✨ Features

- **🤖 AI-Powered Chat Interface**: Ask natural language questions about Houston nonprofits
- **📊 Financial Analytics**: Access real revenue, expenses, and net assets data from IRS Form 990 filings
- **🔍 Smart Search**: Semantic search across 62+ Houston nonprofit organizations
- **📈 Impact Analysis**: Automatically ranks nonprofits by financial impact and scale
- **🌐 Web Interface**: User-friendly chat interface for easy interaction
- **⚡ Fast Response**: Powered by Groq's lightning-fast LLM inference

## 🎯 Key Capabilities

- **Largest Nonprofits Query**: "What are Houston's largest nonprofits by impact?"
- **Organization Details**: "Tell me about the Houston Food Bank"
- **Category Search**: "What healthcare nonprofits are in Houston?"
- **Financial Insights**: Revenue, expenses, and net assets analysis
- **Program Information**: Missions, activities, and service areas

## 🏆 Sample Results

When you ask **"What are Houston's largest nonprofits by impact?"**, the system correctly identifies:

1. **Houston Food Bank** - $425,000,000 revenue (Human Services - Emergency Aid)
2. **Houston Methodist Hospital Foundation** - $125,000,000 revenue (Health - Hospitals)
3. **Memorial Hermann Foundation** - $85,000,000 revenue (Health - Hospitals)
4. **United Way of Greater Houston** - $75,000,000 revenue (Human Services)
5. **Houston Zoo** - $65,000,000 revenue (Animal Protection)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Internet connection for Groq API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Gitit-app/HoustonRag.git
   cd HoustonRag
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic pandas requests groq python-dotenv httpx scikit-learn
   ```

4. **Start the backend server**
   ```bash
   python3 run_backend.py
   ```

5. **Launch web interface**
   ```bash
   # In a new terminal
   python3 -m http.server 3000
   ```

6. **Open your browser**
   ```
   http://localhost:3000/test_interface.html
   ```

## 🛠️ Architecture

```
houston-nonprofit-rag/
├── backend/
│   ├── app/main.py              # FastAPI application
│   ├── services/
│   │   ├── rag_service.py       # Main RAG logic
│   │   ├── groq_service.py      # Groq LLM integration
│   │   └── simple_embedding_service.py  # TF-IDF embeddings
│   ├── database/                # Database models and connections
│   └── models/                  # Pydantic models
├── data/
│   ├── processed/               # Nonprofit data (JSON)
│   └── embeddings/              # Vector embeddings cache
├── test_interface.html          # Web testing interface
└── run_backend.py              # Server startup script
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Main chat interface |
| `/api/nonprofits` | GET | List nonprofits with filtering |
| `/api/system/stats` | GET | System statistics |
| `/api/chat/suggestions` | GET | Sample questions |

### Chat API Example

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are Houston'\''s largest nonprofits by impact?",
    "conversation_id": "demo"
  }'
```

## 💾 Data Source

The system uses **real IRS Form 990 data** from Houston-area nonprofits, including:

- **Financial Metrics**: Total revenue, expenses, net assets
- **Organization Details**: EIN, mission statements, programs
- **NTEE Classifications**: National Taxonomy of Exempt Entities codes
- **Contact Information**: Addresses, websites

## 🤖 Technology Stack

- **Backend**: FastAPI (Python)
- **LLM**: Groq API with Llama 3.3 70B model
- **Embeddings**: TF-IDF with scikit-learn
- **Database**: SQLite/PostgreSQL support
- **Frontend**: Vanilla HTML/JavaScript
- **Search**: Semantic search with cosine similarity

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./nonprofits.db
```

### Groq API Key

Get your free API key from [Groq Console](https://console.groq.com/)

## 🧪 Testing

The system includes comprehensive testing capabilities:

### Web Interface Testing
- Interactive chat interface
- Sample question buttons
- Real-time API communication
- Source citations with financial data

### API Testing
```bash
# Test health
curl http://localhost:8000/health

# Test chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the Houston Food Bank"}'

# Get system stats
curl http://localhost:8000/api/system/stats
```

## 📈 Performance

- **Response Time**: < 2 seconds for most queries
- **Data Coverage**: 62 Houston nonprofit organizations
- **Search Accuracy**: Revenue-based ranking for impact queries
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🎨 Sample Queries

Try these questions in the web interface:

- "What are Houston's largest nonprofits by impact?"
- "Tell me about the Houston Food Bank"
- "What healthcare nonprofits are in Houston?"
- "Which nonprofits focus on education?"
- "Show me organizations helping with food insecurity"
- "What's the revenue of United Way of Greater Houston?"

## 🔄 System Features

### Smart Query Processing
- **Size Queries**: Automatically detects questions about "largest", "biggest", "top" organizations
- **Financial Ranking**: Sorts results by revenue for impact-based queries
- **Semantic Search**: Uses TF-IDF for relevant document retrieval
- **Context-Aware**: Maintains conversation history

### Data Processing
- **Real-time Updates**: Embedding index can be rebuilt as data changes
- **Financial Analysis**: Comprehensive revenue, expense, and asset metrics
- **Category Filtering**: Search by NTEE codes and organization types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Data Source**: IRS Form 990 Series Downloads
- **LLM**: Groq for fast inference
- **Classification**: NTEE (National Taxonomy of Exempt Entities)
- **Houston Nonprofit Community**: For their impactful work

## 📞 Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/Gitit-app/HoustonRag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gitit-app/HoustonRag/discussions)

---
