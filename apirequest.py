from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import os
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

class GenerateRequest(BaseModel):
    url: str
    emoji: str
    style: str
    text_size: str

@app.post("/generate")
def generate_post(req: GenerateRequest):
    page = requests.get(req.url, timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")

    text = " ".join(s.strip() for s in soup.stripped_strings)
    print("✅ /generate вызван с url:", req.url) 
    print(f"style {req.style}") 
    completion = client.chat.completions.create(
        model="qwen/qwen3-30b-a3b:free",
        messages=[
            {"role": "system", "content": f"Ты — администратор Telegram-канала. Напиши пост на основе статьи в следующем формате: Заголовок Описание — Почему это важно (максимум 3 пункта в виде коротких тезисов) Призыв к действию Хэштеги Стиль текста: {req.style} Используй эмодзи: {req.emoji} Объём: {req.text_size} (кратко, но содержательно) Не добавляй пояснений, вступлений, комментариев или форматирования. Только готовый пост — сразу с первой строки.ОТВЕЧАЙ НА ТОМ ЯЗЫКЕ НА КОТОРОМ НАПИСАНА НОВОСТЬ"},
            {"role": "user", "content": text}
        ]
    )
    print(f"Ты администратор Telegram-канала. Твоя задача: кратко и ярко написать пост в стиле Telegram-канала для данной статьи.Формат:- Заголовок описание - Почему это важно (список)- Призыв к действию- ХэштегиНе объясняй, что ты делаешь.Не пиши вступлений типа «Хорошо, вот текст».Сразу выдай готовый пост. Стиль текста {req.style}, использовать емодзи: {req.emoji}, количесвто текста {req.text_size}. НЕ ИСПОЛЬЗУЙ ФОРМАТИРОВАНИЯ ТЕКСТА") 
    print("✅ /generate вызван с url:", req.url) 
    return {"post": completion.choices[0].message.content}

@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apirequest:app", host="0.0.0.0", port=5000, reload=True)

