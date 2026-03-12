import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def alice_webhook(request: Request):
    try:
        alice_request = await request.json()
        user_text = alice_request.get("request", {}).get("command", "")
        
        if not user_text:
            user_text = "привет"
        
        # Запрос к DeepSeek
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
                        {"role": "system", "content": "Ты добрый и заботливый собеседник. Отвечай тепло, коротко и поддерживающе. Твое имя Джой."},
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

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Сервер работает. Жду POST-запросы от Алисы"}
