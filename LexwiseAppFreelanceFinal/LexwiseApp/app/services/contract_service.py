import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx

UPLOAD_FOLDER = 'app/static/uploads'

def save_contract_file(file, user_id):
    """Save uploaded contract file to disk"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    filename = secure_filename(file.filename)
    # Add user_id and timestamp to avoid collisions
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{user_id}_{timestamp}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    file.save(file_path)
    return file_path

def extract_contract_text(file_path):
    """Extract text from contract file (PDF, DOCX, TXT)"""
    ext = file_path.rsplit('.', 1)[1].lower() if '.' in file_path else ''
    
    try:
        if ext == 'pdf':
            return extract_pdf_text(file_path)
        elif ext == 'docx':
            return extract_docx_text(file_path)
        else:
            return extract_txt_text(file_path)
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def extract_pdf_text(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_docx_text(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_txt_text(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def analyze_contract_structure(text):
    """Analyze contract structure (clauses, sections)"""
    import re
    
    # Look for common clause markers
    clause_patterns = [
        r'(\d+\.\s+[A-Z][^\n]+)',  # Numbered clauses (1. Title)
        r'([A-Z][A-Z\s]+:)',  # ALL CAPS HEADERS
        r'(Section\s+\d+[^\n]+)',  # Section X
        r'(Article\s+\d+[^\n]+)'  # Article X
    ]
    
    clauses = []
    for pattern in clause_patterns:
        matches = re.findall(pattern, text)
        clauses.extend(matches)
    
    return list(set(clauses[:20]))  # Return unique clauses