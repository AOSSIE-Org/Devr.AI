from fastapi import FastAPI
from routes import router
import uvicorn

app = FastAPI()

# Include GitHub webhook routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)