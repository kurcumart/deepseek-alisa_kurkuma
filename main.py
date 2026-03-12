import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/")
async def alice_webhook(request: Request):
    alice_request = await request.json()
    # Просто отвечаем фиксированным текстом
    alice_response = {
        "response": {
            "text": "Привет! Я Джой. Как твои дела?",
            "tts": "Привет! Я Джой. Как твои дела?",
            "end_session": False
        },
        "session": alice_request.get("session", {}),
        "version": alice_request.get("version", "1.0")
    }
    return JSONResponse(content=alice_response)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Сервер работает."}
