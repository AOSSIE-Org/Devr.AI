"""
Script to start the GitHub MCP server
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from app.agents.devrel.github.services.github_mcp_server import app
        import uvicorn
        
        print("Starting GitHub MCP Server...")
        print("Server will be available at: http://localhost:8001")
        print("Health check: http://localhost:8001/health")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the backend directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
