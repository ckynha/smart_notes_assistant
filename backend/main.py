# главный файл бэкенда. Пока просто проверяю что FastAPI поднимается
from fastapi import FastAPI

app = FastAPI(title="Smart Notes Assistant")


@app.get("/")
def root():
    return {"message": "Smart Notes Assistant API"}


@app.get("/health")
def health():
    return {"status": "ok"}
