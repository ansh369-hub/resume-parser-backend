from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, uuid
import os

from app.parser import parse_resume_pdf

app = FastAPI(title="Resume Parser API")

allowed_origin = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:8080")
allowed_origins = [origin.strip() for origin in allowed_origin.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    temp_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = parse_resume_pdf(temp_path)
        return result

    finally:
        if temp_path.exists():
            temp_path.unlink()
