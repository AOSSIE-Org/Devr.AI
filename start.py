#!/usr/bin/env python3
"""
Devr.AI Startup Script - Fix for path issues
Run from project root: poetry run python start.py
"""
import sys
import os
from pathlib import Path

# Fix path issues - add backend to Python path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

if __name__ == "__main__":
    try:
        from main import api
        import uvicorn
        print("🚀 Starting Devr.AI Backend from root directory...")
        uvicorn.run("main:api", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure dependencies are installed: poetry install")
