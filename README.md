# Умный помощник по конспектам (Smart Notes Assistant)

Локальный пет-проект: загружаешь конспекты (текст / `.txt` / `.docx` / `.pdf`),
приложение сохраняет их в SQLite, анализирует через LLM (OpenRouter,
`google/gemini-2.5-flash`), выдаёт структурированное резюме (предмет, темы,
ключевая информация), генерирует вопросы для самопроверки и отвечает на
вопросы по конспекту.

Подробная архитектура — в [`docs/architecture.md`](docs/architecture.md).

## Технологии

- Python 3.11+
- Бэкенд: FastAPI + Uvicorn
- Фронтенд: Streamlit
- База данных: SQLite (через встроенный `sqlite3`)
- LLM: OpenRouter API, модель `google/gemini-2.5-flash`
- Парсинг файлов: `python-docx` (.docx), `pypdf` (.pdf)

## Структура проекта

```
smart_notes_assistant/
├── docs/
│   └── architecture.md
├── backend/
│   ├── main.py        # FastAPI приложение и эндпоинты
│   ├── database.py    # подключение и инициализация SQLite
│   ├── models.py      # запросы к таблицам
│   ├── llm.py         # клиент OpenRouter
│   ├── parser.py      # извлечение текста из файлов
│   └── prompts.py     # шаблоны промптов
├── frontend/
│   └── app.py         # Streamlit интерфейс
├── .env.example
├── requirements.txt
└── README.md
```

## Установка и запуск

```bash
# 1. (опционально) создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate

# 2. установить зависимости
pip install -r requirements.txt

# 3. прописать ключ OpenRouter
cp .env.example .env
# отредактируйте .env и впишите OPENROUTER_API_KEY

# 4. запустить бэкенд
uvicorn backend.main:app --reload

# 5. в отдельном терминале запустить фронтенд
streamlit run frontend/app.py
```

После запуска:
- API доступно на `http://localhost:8000` (Swagger UI — `http://localhost:8000/docs`);
- интерфейс Streamlit — на `http://localhost:8501`.

## Эндпоинты API

| Метод | Путь | Назначение |
|-------|------|-----------|
| `POST` | `/notes` | Принять текст или файл (.txt/.docx/.pdf), распарсить, сохранить, вернуть `id` |
| `POST` | `/notes/{id}/analyze` | Отправить текст в LLM, получить предмет + темы + резюме + вопросы |
| `GET`  | `/notes/{id}/summary` | Вернуть резюме, темы и вопросы по конспекту |
| `POST` | `/notes/{id}/ask` | Ответить на вопрос пользователя по конспекту |
| `GET`  | `/notes` | Список всех загруженных конспектов |
