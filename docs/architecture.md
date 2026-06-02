# Умный помощник по конспектам — Архитектура

Локальный пет-проект : загружаешь конспекты (текст / `.docx` / `.pdf`), приложение сохраняет их в базу, анализирует через LLM, выдаёт структурированное резюме (предмет, темы, ключевая информация), генерирует вопросы для самопроверки и отвечает на вопросы по конспекту.

---

## 1. Технологический стек

| Слой | Технология |
|------|-----------|
| Язык | Python 3.11+ |
| Фронтенд | Streamlit |
| Бэкенд | FastAPI (Uvicorn) |
| База данных | SQLite |
| LLM | OpenRouter API, модель `google/gemini-2.5-flash` |
| Парсинг файлов | `python-docx` (.docx), `pypdf` (.pdf) |

Запуск полностью локальный: один процесс FastAPI + один процесс Streamlit.

---

## 2. Общая архитектура

```mermaid
flowchart LR
    User[Пользователь] --> UI[Streamlit UI]
    UI -->|HTTP запросы| API[FastAPI backend]
    API --> Parser[Модуль парсинга файлов]
    API --> DB[(SQLite)]
    API --> LLM[Модуль LLM клиента]
    LLM -->|HTTPS| OR[OpenRouter API gemini-2.5-flash]
```

Принцип: Streamlit отвечает только за интерфейс и общается с бэкендом по HTTP. Вся логика (парсинг, БД, вызовы LLM) живёт в FastAPI.

---

## 3. Поток данных

```mermaid
sequenceDiagram
    participant U as Пользователь
    participant S as Streamlit
    participant F as FastAPI
    participant L as LLM OpenRouter
    participant D as SQLite

    U->>S: Загружает файл или текст
    S->>F: POST /notes (контент)
    F->>F: Парсинг текста из файла
    F->>D: Сохранить конспект
    S->>F: POST /notes/{id}/analyze
    F->>L: Промпт на структурирование
    L-->>F: Предмет, темы, резюме, вопросы
    F->>D: Сохранить результат анализа
    S->>F: GET /notes/{id}/summary
    F->>D: Достать резюме и вопросы
    F-->>S: Показать пользователю
    U->>S: Задаёт вопрос по теме
    S->>F: POST /notes/{id}/ask
    F->>D: Взять текст конспекта
    F->>L: Промпт текст плюс вопрос
    L-->>F: Ответ
    F-->>S: Показать ответ
```

---

## 4. Схема базы данных (SQLite)

Минимальный набор таблиц.

```mermaid
erDiagram
    NOTES ||--o{ TOPICS : содержит
    NOTES ||--o{ QUESTIONS : содержит

    NOTES {
        int id PK
        string filename
        string subject
        text raw_text
        text summary
        datetime created_at
    }
    TOPICS {
        int id PK
        int note_id FK
        string title
        text content
    }
    QUESTIONS {
        int id PK
        int note_id FK
        string question
    }
```

- `NOTES` — исходный конспект: имя файла, распознанный предмет, полный текст, общее резюме.
- `TOPICS` — выделенные из конспекта темы с краткой выжимкой по каждой.
- `QUESTIONS` — сгенерированные вопросы для самопроверки.

---

## 5. Эндпоинты FastAPI

| Метод | Путь | Назначение |
|-------|------|-----------|
| `POST` | `/notes` | Принять текст или файл (.docx/.pdf), распарсить, сохранить в БД, вернуть `id` |
| `POST` | `/notes/{id}/analyze` | Отправить текст в LLM, получить предмет + темы + резюме + вопросы, сохранить |
| `GET` | `/notes/{id}/summary` | Вернуть резюме, список тем и вопросов по конспекту |
| `POST` | `/notes/{id}/ask` | Ответить на вопрос пользователя по конспекту (текст + вопрос в промпт LLM) |
| `GET` | `/notes` | Список всех загруженных конспектов (id, предмет, имя файла) |

---

## 6. Модуль LLM (OpenRouter)

Отдельный файл-обёртка над HTTP-вызовом к OpenRouter:

- читает `OPENROUTER_API_KEY` из переменных окружения (`.env`);
- модель `google/gemini-2.5-flash`;
- одна функция отправки промпта и получения ответа;
- два сценария промптов:
  1. **Анализ конспекта** — просим LLM вернуть JSON: `subject`, `topics[]`, `summary`, `questions[]`.
  2. **Ответ на вопрос** — передаём релевантный текст конспекта + вопрос пользователя, получаем текстовый ответ.

Q&A реализуется просто: текст конспекта (или нужной темы) подставляется в промпт, без эмбеддингов и векторного поиска.

---

## 7. Модуль парсинга файлов

Одна функция «извлечь текст», которая по расширению выбирает обработчик:

- `.txt` / обычный текст — как есть;
- `.docx` — через `python-docx`;
- `.pdf` — через `pypdf`.

Возвращает обычную строку, которая дальше идёт в БД и в LLM.

---

## 8. Структура проекта

```
smart_notes_assistant/
├── docs/
│   └── architecture.md        # этот документ
├── backend/
│   ├── main.py                # FastAPI приложение и эндпоинты
│   ├── database.py            # подключение и инициализация SQLite
│   ├── models.py              # схемы/запросы к таблицам
│   ├── llm.py                 # клиент OpenRouter (gemini-2.5-flash)
│   ├── parser.py              # извлечение текста из файлов
│   └── prompts.py             # шаблоны промптов
├── frontend/
│   └── app.py                 # Streamlit интерфейс
├── .env.example               # пример: OPENROUTER_API_KEY=...
├── requirements.txt           # зависимости
└── README.md
```

---

## 9. Зависимости (requirements.txt)

```
fastapi
uvicorn
streamlit
requests
python-docx
pypdf
python-dotenv
```

SQLite используется через встроенный в Python модуль `sqlite3` — отдельная зависимость не нужна.

---

## 10. Запуск проекта

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Прописать ключ OpenRouter в .env
cp .env.example .env

# 3. Запустить бэкенд
uvicorn backend.main:app --reload

# 4. В отдельном терминале запустить фронтенд
streamlit run frontend/app.py
```

---

## 11. Сценарий пользователя

```mermaid
flowchart TD
    A[Открыть Streamlit] --> B[Загрузить конспект или вставить текст]
    B --> C[Нажать Анализировать]
    C --> D[Увидеть предмет, темы и резюме]
    D --> E[Посмотреть вопросы для самопроверки]
    D --> F[Задать свой вопрос по теме]
    F --> G[Получить ответ от помощника]
```
