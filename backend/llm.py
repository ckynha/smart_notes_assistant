# обращение к OpenRouter (gemini). По сути просто шлем запрос и парсим ответ
import os
import json
import requests
from dotenv import load_dotenv

from . import prompts

load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash"


def chat(system_prompt, user_prompt, temperature=0.3):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        # если забыли прописать ключ в .env
        raise RuntimeError("Не задан OPENROUTER_API_KEY (см. .env.example)")

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    r = requests.post(API_URL, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    answer = r.json()["choices"][0]["message"]["content"]
    return answer


def parse_json(text):
    # gemini иногда оборачивает json в ```json ... ```, чистим это
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        # после strip может остаться слово json в начале
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # запасной вариант - берем кусок от первой { до последней }
        start = text.find("{")
        end = text.rfind("}")
        return json.loads(text[start:end + 1])


def analyze_note(note_text):
    raw = chat(
        prompts.ANALYZE_SYSTEM_PROMPT,
        prompts.build_analyze_prompt(note_text),
        temperature=0.2,
    )
    data = parse_json(raw)

    # приводим к нужному виду, иногда модель присылает не все
    subject = data.get("subject", "")
    summary = data.get("summary", "")

    topics = []
    for t in data.get("topics", []):
        if isinstance(t, dict):
            topics.append({
                "title": t.get("title", ""),
                "content": t.get("content", ""),
            })
        else:
            topics.append({"title": str(t), "content": ""})

    questions = []
    for q in data.get("questions", []):
        if q:
            questions.append(str(q))

    return {
        "subject": subject,
        "summary": summary,
        "topics": topics,
        "questions": questions,
    }
