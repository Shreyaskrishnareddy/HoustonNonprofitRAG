#!/usr/bin/env python3
"""
Run the Houston Nonprofit RAG backend API
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)