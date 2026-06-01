# главный файл бэкенда, тут все ручки FastAPI
from fastapi import FastAPI, File, Form, UploadFile, HTTPException

from . import models
from . import parser
from . import llm
from .database import init_db

app = FastAPI(title="Smart Notes Assistant")

# создаем таблицы при старте
init_db()


@app.post("/notes")
async def create_note(text: str = Form(None), file: UploadFile = File(None)):
    # можно прислать либо текст, либо файл
    filename = None
    raw_text = None

    if file is not None:
        content = await file.read()
        filename = file.filename
        raw_text = parser.extract_text(content, filename)
    elif text:
        raw_text = text.strip()

    if not raw_text:
        raise HTTPException(status_code=400, detail="Пустой конспект, нужен текст или файл")

    note_id = models.create_note(raw_text, filename)
    return {"id": note_id, "filename": filename}


@app.post("/notes/{note_id}/analyze")
def analyze(note_id: int):
    note = models.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Конспект не найден")

    try:
        result = llm.analyze_note(note["raw_text"])
    except Exception as e:
        raise HTTPException(status_code=502, detail="Ошибка LLM: " + str(e))

    # сохраняем все в базу
    models.update_note_analysis(note_id, result["subject"], result["summary"])
    models.replace_topics(note_id, result["topics"])
    models.replace_questions(note_id, result["questions"])

    return {
        "id": note_id,
        "subject": result["subject"],
        "summary": result["summary"],
        "topics": result["topics"],
        "questions": result["questions"],
    }


@app.get("/notes")
def get_notes():
    return models.list_notes()
