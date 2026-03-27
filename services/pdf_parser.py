import pdfplumber
import io

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Reads pure bytes from an uploaded PDF and uses pdfplumber to extract text.
    """
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"PDF parsing error: {e}")
        raise ValueError("Failed to parse PDF format.")
        
    return text.strip()
