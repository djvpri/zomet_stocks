from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from scheduler.jobs import create_scheduler, run_analysis
from services.market_data import fetch_ihsg_data
from services.ai_manager import AIManager
from services.notification import send_to_device, send_notification
from models.signal import AnalysisResult
from config import settings
import uvicorn

ai_manager = AIManager()
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = create_scheduler()
    scheduler.start()
    print(f"[Server] Scheduler aktif | Mode AI: {settings.ai_mode} | Provider: {settings.primary_provider}")
    yield
    scheduler.shutdown()
    print("[Server] Scheduler berhenti")


app = FastAPI(
    title="IHSG AI Signal API",
    description="Backend analisis IHSG menggunakan multi-provider AI",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "status": "running",
        "ai_mode": settings.ai_mode,
        "primary_provider": settings.primary_provider,
        "ihsg_symbol": settings.ihsg_symbol,
    }


@app.get("/analyze", response_model=AnalysisResult)
def analyze_now():
    """Jalankan analisis IHSG sekarang (manual trigger)."""
    try:
        market_data = fetch_ihsg_data()
        result = ai_manager.analyze(market_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-data")
def get_market_data():
    """Ambil data IHSG terkini tanpa analisis AI."""
    try:
        data = fetch_ihsg_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notify-device")
def notify_device(device_token: str = Body(..., embed=True)):
    """Analisis dan kirim notifikasi ke satu device spesifik."""
    try:
        market_data = fetch_ihsg_data()
        result = ai_manager.analyze(market_data)
        success = send_to_device(result, device_token)
        return {"success": success, "signal": result.signal, "confidence": result.confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-notify-topic")
def test_notify_topic():
    """Test kirim notifikasi ke semua subscriber topik 'ihsg_signals'."""
    try:
        market_data = fetch_ihsg_data()
        result = ai_manager.analyze(market_data)
        success = send_notification(result, topic="ihsg_signals")
        return {"success": success, "signal": result.signal, "confidence": result.confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/settings")
def get_settings():
    """Lihat konfigurasi aktif."""
    return {
        "ai_mode": settings.ai_mode,
        "primary_provider": settings.primary_provider,
        "fallback_providers": settings.get_fallback_list(),
        "consensus_providers": settings.get_consensus_list(),
        "analysis_interval_minutes": settings.analysis_interval_minutes,
        "market_hours": f"{settings.market_open_hour:02d}:{settings.market_open_minute:02d} - {settings.market_close_hour:02d}:{settings.market_close_minute:02d} WIB",
        "timezone": settings.timezone,
        "active_api_keys": {
            "claude": bool(settings.claude_api_key),
            "qwen": bool(settings.qwen_api_key),
            "deepseek": bool(settings.deepseek_api_key),
            "gemini": bool(settings.gemini_api_key),
            "groq": bool(settings.groq_api_key),
            "openai": bool(settings.openai_api_key),
        },
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
