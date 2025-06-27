from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/webhook")
async def receive_event(request: Request):
    data = await request.json()
    print(f"📩 Received event: {json.dumps(data, indent=2)}")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
