# тут все запросы к базе. Обычного sqlite хватает
from .database import get_connection


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
        "SELECT id, filename, created_at FROM notes ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append(dict(r))
    return result
