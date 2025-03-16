from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import api_router
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Devr.AI Backend",
    description="API for Devr.AI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Devr.AI API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)