from fastapi import FastAPI

app = FastAPI()  # Ensure this exists

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
