# главный файл бэкенда, тут все ручки FastAPI
from fastapi import FastAPI, Form, HTTPException

from . import models
from .database import init_db

app = FastAPI(title="Smart Notes Assistant")

# создаем таблицы при старте
init_db()


@app.post("/notes")
def create_note(text: str = Form(...)):
    raw_text = text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Пустой конспект, нужен текст")

    note_id = models.create_note(raw_text)
    return {"id": note_id}


@app.get("/notes")
def get_notes():
    return models.list_notes()
