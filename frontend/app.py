# интерфейс на streamlit. Сам ничего не считает, только дергает бэкенд
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Помощник по конспектам", page_icon="📚")


# небольшие обёртки чтобы не писать url каждый раз
def get(path):
    r = requests.get(BACKEND + path, timeout=120)
    r.raise_for_status()
    return r.json()


def post(path, **kwargs):
    r = requests.post(BACKEND + path, timeout=120, **kwargs)
    r.raise_for_status()
    return r.json()


# запоминаем какой конспект сейчас выбран
if "note_id" not in st.session_state:
    st.session_state.note_id = None

st.title("📚 Умный помощник по конспектам")

# ---- сайдбар со списком конспектов ----
st.sidebar.header("Мои конспекты")
try:
    notes = get("/notes")
    if len(notes) == 0:
        st.sidebar.caption("Пока пусто")
    for n in notes:
        name = n.get("subject") or n.get("filename") or ("Конспект #" + str(n["id"]))
        if st.sidebar.button("#" + str(n["id"]) + " — " + name, key="n" + str(n["id"])):
            st.session_state.note_id = n["id"]
except Exception as e:
    st.sidebar.error("Не получилось загрузить список: " + str(e))

if st.sidebar.button("➕ Новый конспект"):
    st.session_state.note_id = None


# ---- если конспект не выбран, показываем форму загрузки ----
if st.session_state.note_id is None:
    st.subheader("Загрузить конспект")

    tab1, tab2 = st.tabs(["Вставить текст", "Загрузить файл"])

    with tab1:
        my_text = st.text_area("Текст конспекта", height=250)
        if st.button("Сохранить текст"):
            if my_text.strip() != "":
                try:
                    res = post("/notes", data={"text": my_text})
                    st.session_state.note_id = res["id"]
                    st.rerun()
                except Exception as e:
                    st.error("Ошибка: " + str(e))
            else:
                st.warning("Введите текст")

    with tab2:
        uploaded = st.file_uploader("Файл", type=["txt", "docx", "pdf"])
        if st.button("Загрузить файл"):
            if uploaded is not None:
                try:
                    files = {"file": (uploaded.name, uploaded.getvalue())}
                    res = post("/notes", files=files)
                    st.session_state.note_id = res["id"]
                    st.rerun()
                except Exception as e:
                    st.error("Ошибка: " + str(e))
            else:
                st.warning("Выберите файл")

# ---- иначе работаем с выбранным конспектом ----
else:
    note_id = st.session_state.note_id
    st.subheader("Конспект #" + str(note_id))

    if st.button("🔍 Анализировать"):
        with st.spinner("Анализирую..."):
            try:
                post("/notes/" + str(note_id) + "/analyze")
            except Exception as e:
                st.error("Ошибка анализа: " + str(e))

    # показываем что есть по конспекту
    data = None
    try:
        data = get("/notes/" + str(note_id) + "/summary")
    except Exception as e:
        st.error("Не удалось загрузить: " + str(e))

    if data is not None:
        if data.get("subject"):
            st.write("**Предмет:** " + data["subject"])

        if data.get("summary"):
            st.markdown("### Резюме")
            st.write(data["summary"])

        topics = data.get("topics") or []
        if len(topics) > 0:
            st.markdown("### Темы")
            for t in topics:
                with st.expander(t.get("title") or "Без названия"):
                    st.write(t.get("content") or "-")

        questions = data.get("questions") or []
        if len(questions) > 0:
            st.markdown("### Вопросы для самопроверки")
            for q in questions:
                st.write("- " + q.get("question"))

        if not data.get("summary") and len(topics) == 0 and len(questions) == 0:
            st.info("Конспект ещё не анализировали. Жми кнопку выше.")

    # ---- вопрос по конспекту ----
    st.markdown("### Задать вопрос")
    q = st.text_input("Ваш вопрос")
    if st.button("Спросить"):
        if q.strip() != "":
            with st.spinner("Думаю..."):
                try:
                    res = post("/notes/" + str(note_id) + "/ask", json={"question": q})
                    st.write("**Ответ:**")
                    st.write(res["answer"])
                except Exception as e:
                    st.error("Ошибка: " + str(e))
        else:
            st.warning("Напишите вопрос")
