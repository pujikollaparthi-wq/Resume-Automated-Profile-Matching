import os
import re
import io

def clean_extracted_text(text: str) -> str:
    """Normalize extracted text by removing extra whitespaces, line-breaks, and non-printable artifacts."""
    if not text:
        return ""
    # Normalize unicode spaces
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple spaces or multiple linebreaks
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def parse_pdf(file_bytes: bytes) -> str:
    """Parse text from PDF bytes using PyMuPDF (fitz) or pdfplumber or PyPDF2 fallback."""
    text_parts = []
    
    # 1. Try PyMuPDF (fast & robust)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text)
        if text_parts:
            return clean_extracted_text("\n".join(text_parts))
    except Exception as e:
        pass

    # 2. Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        if text_parts:
            return clean_extracted_text("\n".join(text_parts))
    except Exception as e:
        pass

    # 3. Try PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        if text_parts:
            return clean_extracted_text("\n".join(text_parts))
    except Exception as e:
        pass

    return clean_extracted_text("\n".join(text_parts))

def parse_docx(file_bytes: bytes) -> str:
    """Parse text from DOCX bytes using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        return clean_extracted_text("\n".join(paragraphs))
    except Exception as e:
        return ""

def parse_txt(file_bytes: bytes) -> str:
    """Decode text from plain text file bytes."""
    for enc in ['utf-8', 'latin-1', 'cp1252', 'ascii']:
        try:
            return clean_extracted_text(file_bytes.decode(enc))
        except UnicodeDecodeError:
            continue
    return clean_extracted_text(file_bytes.decode('utf-8', errors='ignore'))

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Detect file type and extract clean text."""
    ext = os.path.splitext(filename.lower())[1]
    if ext == '.pdf':
        return parse_pdf(file_bytes)
    elif ext in ['.docx', '.doc']:
        return parse_docx(file_bytes)
    else:
        return parse_txt(file_bytes)
