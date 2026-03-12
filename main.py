import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_text}],
        }
    )
    try:
    data = response.json()
    # Проверим, есть ли choices
    if "choices" in data:
        answer = data["choices"][0]["message"]["content"]
    else:
        # Если нет choices, значит пришла ошибка
        answer = f"Ошибка от DeepSeek: {data}"
        # Дополнительно распечатаем в логи Render
        print("Ответ от DeepSeek не содержит choices:", data)
except Exception as e:
    answer = f"Ошибка при разборе ответа: {e}"
    print("Исключение:", e)

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")  # <- ЭТО ВАЖНО! Именно POST
async def alice_webhook(request: Request):
    try:
        alice_request = await request.json()
        user_text = alice_request.get("request", {}).get("command", "")
        
        if not user_text:
            user_text = "привет"
        
        # Здесь запрос к DeepSeek
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Ты добрый собеседник Джой."},
                        {"role": "user", "content": user_text}
                    ],
                    "max_tokens": 300
                }
            )
            
            data = response.json()
            if "choices" in data:
                ai_text = data["choices"][0]["message"]["content"]
            else:
                ai_text = "Извини, я временно не могу ответить."
                
    except Exception as e:
        ai_text = "Привет! Я тебя слышу. Расскажи, что случилось?"
    
    # Формируем ответ для Алисы
    alice_response = {
        "response": {
            "text": ai_text,
            "tts": ai_text,
            "end_session": False
        },
        "session": alice_request.get("session", {}),
        "version": alice_request.get("version", "1.0")
    }
    
    return JSONResponse(content=alice_response)

@app.get("/")  # Это для проверки в браузере
async def health_check():
    return {"status": "ok", "message": "Сервер работает. Жду POST-запросы от Алисы"}
