from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router  
import uvicorn

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  
)

# Include GitHub webhook routes (preserving functionality from the existing file)
app.include_router(router, prefix="/api")  

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
