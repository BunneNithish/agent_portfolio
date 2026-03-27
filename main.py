from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import uvicorn
from dotenv import load_dotenv

from services.pdf_parser import extract_text_from_pdf
from services.ai_processor import process_resume_text
from services.generator import generate_portfolio

# Load variables from .env if present
load_dotenv()

app = FastAPI(
    title="AI Resume to Portfolio Generator Agent",
    description="Upload a PDF resume, and this API will generate a static portfolio website using AI.",
    version="1.0.0"
)

# Optional: adding CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory for the full app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure required folders exist on startup
os.makedirs(os.path.join(BASE_DIR, "generated_sites"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "frontend"), exist_ok=True)

# Mount the generated sites explicitly for the live-preview iframe!
app.mount("/sites", StaticFiles(directory=os.path.join(BASE_DIR, "generated_sites")), name="sites")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serves the beautiful HTML frontend UI."""
    with open(os.path.join(BASE_DIR, "frontend", "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), theme: str = Form("light")):
    """
    Accepts a PDF resume, extracts text, uses AI to structure the data,
    and generates a personalized static website.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
    try:
        # 1. Read PDF file contents
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided.")
            
        # 2. Extract Text via standard PDF processing
        text = extract_text_from_pdf(content)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found in the PDF.")
            
        # 3. AI Processing to structure the text into JSON
        parsed_data = await process_resume_text(text)
        
        # 4. Generate the Portfolio website using Jinja2
        username = str(uuid.uuid4())[:8] # Generate a short unique ID/folder name
        zip_path = generate_portfolio(username, parsed_data, theme)
        
        return {
            "message": "Portfolio generated successfully",
            "username": username,
            "data_extracted": parsed_data,
            "download_url": f"/download/{username}"
        }
        
    except ValueError as val_e:
        raise HTTPException(status_code=500, detail=str(val_e))
    except Exception as e:
        print(f"Error during upload process: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred processing the request.")

@app.get("/download/{username}")
async def download_portfolio(username: str):
    """
    Downloads the zipped generated portfolio site.
    """
    zip_path = os.path.join(BASE_DIR, "generated_sites", f"{username}.zip")
    if os.path.exists(zip_path):
        return FileResponse(
            path=zip_path, 
            filename="My_AI_Portfolio.zip", 
            media_type='application/zip'
        )
    raise HTTPException(status_code=404, detail="Portfolio not found or has been deleted.")

# Entrypoint to run via Python execution directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
