"""
FastAPI application serving the Generator-Reviewer agent pipeline.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from agents import run_pipeline

app = FastAPI(title="Generator-Reviewer Agent")
templates = Jinja2Templates(directory="templates")


class PipelineRequest(BaseModel):
    grade: int
    topic: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/generate")
async def generate(req: PipelineRequest):
    """Run the full agent pipeline and return all stage results."""
    try:
        result = run_pipeline(grade=req.grade, topic=req.topic)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
