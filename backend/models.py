# тут все запросы к базе. Обычного sqlite хватает
from .database import get_connection


# ---- notes ----

def create_note(raw_text, filename=None):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO notes (filename, raw_text) VALUES (?, ?)",
        (filename, raw_text)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_note(note_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def list_notes():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, filename, subject, created_at FROM notes ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append(dict(r))
    return result


def update_note_analysis(note_id, subject, summary):
    conn = get_connection()
    conn.execute(
        "UPDATE notes SET subject = ?, summary = ? WHERE id = ?",
        (subject, summary, note_id)
    )
    conn.commit()
    conn.close()


# ---- topics ----

def replace_topics(note_id, topics):
    # topics - список словарей {title, content}
    conn = get_connection()
    conn.execute("DELETE FROM topics WHERE note_id = ?", (note_id,))
    for t in topics:
        conn.execute(
            "INSERT INTO topics (note_id, title, content) VALUES (?, ?, ?)",
            (note_id, t.get("title", ""), t.get("content", ""))
        )
    conn.commit()
    conn.close()


def get_topics(note_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, content FROM topics WHERE note_id = ?", (note_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---- questions ----

def replace_questions(note_id, questions):
    conn = get_connection()
    conn.execute("DELETE FROM questions WHERE note_id = ?", (note_id,))
    for q in questions:
        conn.execute(
            "INSERT INTO questions (note_id, question) VALUES (?, ?)",
            (note_id, q)
        )
    conn.commit()
    conn.close()


def get_questions(note_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, question FROM questions WHERE note_id = ?", (note_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
