# вытаскиваем текст из файла. Поддерживаю txt, docx и pdf
import io


def extract_text(data, filename):
    if filename is None:
        filename = ""
    name = filename.lower()

    if name.endswith(".docx"):
        return read_docx(data)
    elif name.endswith(".pdf"):
        return read_pdf(data)
    else:
        # считаем что это обычный текст
        return read_txt(data)


def read_txt(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        # на всякий случай если кодировка не utf-8
        text = data.decode("latin-1", errors="ignore")
    return text.strip()


def read_docx(data):
    from docx import Document
    doc = Document(io.BytesIO(data))
    lines = []
    for p in doc.paragraphs:
        lines.append(p.text)
    return "\n".join(lines).strip()


def read_pdf(data):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()
