from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

from modules.pipeline_runner import execute_pipeline
from modules.resume_parser import ResumeParser

app = FastAPI(title="AI Resume Report API")

# Ensure outputs folder exists
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    inputType: str
    value: str
    targetRole: str = "Software Engineer"
    company: str = ""

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    """Analyze plain-text resume or documentation value."""
    if req.inputType in ("text", "documentation"):
        try:
            result = execute_pipeline(req.value, req.targetRole, req.company)
            return result
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "unsupported inputType"}

@app.post("/api/upload")
async def upload(
    file: UploadFile = File(...),
    targetRole: str = Form("Software Engineer"),
    company: str = Form("")
):
    """Receive a resume file and attempt to analyze its text."""
    try:
        content = await file.read()

        # Temporary save to use ResumeParser logic
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
            
        text = ResumeParser.extract_text(temp_path, is_file=True)
        os.remove(temp_path)

        result = execute_pipeline(text, targetRole, company)
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
