# api.py — FastAPI REST server for StreetSense
# Run: uvicorn api:app --reload --port 8000

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import os

from src.analyzer import analyze_image
from src.gps_extractor import extract_gps
from src.database import save_report, get_all_reports, get_stats

app = FastAPI(
    title="StreetSense API",
    description="AI-powered road hazard detection API for Indian roads",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

@app.get("/")
def root():
    return {
        "name": "StreetSense API",
        "version": "2.0.0",
        "endpoints": ["/analyze", "/reports", "/stats", "/docs"]
    }

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    location: str = Form(""),
    save: bool = Form(True)
):
    """
    Analyze a road image for hazards.
    Returns severity score, hazard types, civic report, and more.
    """
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured on server")

    contents = await file.read()

    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    gps = extract_gps(contents)

    try:
        result = analyze_image(image, GROQ_API_KEY, location)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {str(e)}")

    report_id = None
    if save:
        report_id = save_report(result, gps, location, source="api")

    return {
        "report_id": report_id,
        "gps": gps,
        "location": location,
        "hazards_detected": result.get("hazards_detected"),
        "primary_hazard": result.get("primary_hazard"),
        "severity_score": result.get("severity_score"),
        "severity_label": result.get("severity_label"),
        "road_condition": result.get("road_condition"),
        "confidence": result.get("confidence"),
        "passable": result.get("passable"),
        "affected_area_percent": result.get("affected_area_percent"),
        "immediate_action": result.get("immediate_action"),
        "civic_report": result.get("civic_report"),
    }

@app.get("/reports")
def list_reports(limit: int = 50):
    """Get all submitted hazard reports."""
    reports = get_all_reports()
    return {"total": len(reports), "reports": reports[:limit]}

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    """Get a specific report by ID."""
    reports = get_all_reports()
    for r in reports:
        if r["id"] == report_id:
            return r
    raise HTTPException(status_code=404, detail="Report not found")

@app.get("/stats")
def stats():
    """Get overall statistics across all reports."""
    return get_stats()

@app.get("/health")
def health():
    return {"status": "ok", "groq_configured": bool(GROQ_API_KEY)}
