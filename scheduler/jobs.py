from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from config import settings
from services.market_data import fetch_ihsg_data
from services.ai_manager import AIManager
from services.notification import send_notification


ai_manager = AIManager()


def run_analysis():
    """Job utama: fetch data IHSG, analisis AI, kirim notifikasi."""
    print("[Scheduler] Memulai analisis IHSG...")
    try:
        market_data = fetch_ihsg_data()
        print(f"[Scheduler] IHSG: {market_data.current_price:,.0f} ({market_data.change_pct:+.2f}%)")

        result = ai_manager.analyze(market_data)
        print(f"[Scheduler] Sinyal: {result.signal.value} | Confidence: {result.confidence.value}")
        print(f"[Scheduler] Alasan: {result.reason}")
        print(f"[Scheduler] Provider: {result.provider_used}")

        send_notification(result)
        return result
    except Exception as e:
        print(f"[Scheduler] Error: {e}")
        return None


def create_scheduler() -> BackgroundScheduler:
    tz = pytz.timezone(settings.timezone)
    scheduler = BackgroundScheduler(timezone=tz)

    interval = settings.analysis_interval_minutes
    if interval >= 60:
        # Jadwalkan per jam, di menit ke-0
        hour_step = interval // 60
        cron_hour = f"{settings.market_open_hour}-{settings.market_close_hour}/{hour_step}"
        cron_minute = "0"
    else:
        cron_hour = f"{settings.market_open_hour}-{settings.market_close_hour}"
        cron_minute = f"*/{interval}"

    # Jalankan setiap N menit/jam, hanya saat jam bursa (Senin-Jumat)
    scheduler.add_job(
        run_analysis,
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour=cron_hour,
            minute=cron_minute,
            timezone=tz,
        ),
        id="ihsg_analysis",
        name="Analisis IHSG",
        replace_existing=True,
        misfire_grace_time=300,
    )

    return scheduler
