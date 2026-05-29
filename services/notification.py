import firebase_admin
from firebase_admin import credentials, messaging
from models.signal import AnalysisResult, SignalType
from config import settings
import os


_initialized = False


def _init_firebase():
    global _initialized
    if not _initialized and os.path.exists(settings.firebase_credentials_path):
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred)
        _initialized = True


def _build_notification(result: AnalysisResult) -> tuple[str, str]:
    emoji = {"BELI": "📈", "JUAL": "📉", "HOLD": "⏸️"}.get(result.signal.value, "📊")
    confidence_label = {"rendah": "⚠️ Rendah", "sedang": "🔸 Sedang", "tinggi": "✅ Tinggi"}.get(
        result.confidence.value, ""
    )

    title = f"{emoji} IHSG: Sinyal {result.signal.value}"
    body = (
        f"Harga: {result.ihsg_price:,.0f} ({result.ihsg_change_pct:+.2f}%)\n"
        f"Keyakinan: {confidence_label}\n"
        f"{result.reason}"
    )
    if result.risk:
        body += f"\n⚠️ {result.risk}"

    return title, body


def send_notification(result: AnalysisResult, topic: str = "ihsg_signals") -> bool:
    """Kirim notifikasi ke semua subscriber topik via FCM."""
    _init_firebase()
    if not _initialized:
        print("[FCM] Firebase tidak diinisialisasi, notifikasi dilewati")
        return False

    title, body = _build_notification(result)

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data={
            "signal": result.signal.value,
            "confidence": result.confidence.value,
            "price": str(result.ihsg_price),
            "change_pct": str(result.ihsg_change_pct),
            "provider": result.provider_used,
        },
        topic=topic,
    )

    try:
        response = messaging.send(message)
        print(f"[FCM] Notifikasi terkirim: {response}")
        return True
    except Exception as e:
        print(f"[FCM] Gagal mengirim notifikasi: {e}")
        return False


def send_to_device(result: AnalysisResult, device_token: str) -> bool:
    """Kirim notifikasi ke satu device spesifik."""
    _init_firebase()
    if not _initialized:
        return False

    title, body = _build_notification(result)

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        data={
            "signal": result.signal.value,
            "confidence": result.confidence.value,
            "price": str(result.ihsg_price),
        },
        token=device_token,
    )

    try:
        messaging.send(message)
        return True
    except Exception as e:
        print(f"[FCM] Gagal kirim ke device: {e}")
        return False
