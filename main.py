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
