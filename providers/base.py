from abc import ABC, abstractmethod
from models.signal import MarketData, ProviderResult, SignalType, ConfidenceLevel
import json
import re


SYSTEM_PROMPT = """Kamu adalah analis saham profesional Indonesia yang berpengalaman lebih dari 20 tahun.
Spesialisasi kamu adalah IHSG (Indeks Harga Saham Gabungan) dan pasar modal Indonesia.
Analisis kamu mempertimbangkan:
- Indikator teknikal (RSI, MA, MACD)
- Kondisi pasar regional Asia
- Sentimen investor
- Manajemen risiko

Selalu jawab dalam format JSON yang valid. Jangan tambahkan teks di luar JSON."""

USER_PROMPT_TEMPLATE = """Analisis data IHSG berikut dan berikan rekomendasi trading:

DATA PASAR SAAT INI:
- Harga IHSG: {current_price:,.0f}
- Perubahan hari ini: {change_pct:+.2f}%
- Volume vs rata-rata: {volume_ratio:+.0f}%
- Tren 5 hari: {trend_5d:+.2f}%
- Tren 1 bulan: {trend_1m:+.2f}%

INDIKATOR TEKNIKAL:
- RSI(14): {rsi:.1f}
- MA20: {ma20:,.0f} | MA50: {ma50:,.0f} | MA200: {ma200:,.0f}
- MACD: {macd:.2f} | Signal: {macd_signal:.2f}
- 52W High: {high_52w:,.0f} | 52W Low: {low_52w:,.0f}

INTERPRETASI CEPAT:
- RSI: {"Oversold (potensi rebound)" if {rsi:.1f} < 30 else "Overbought (potensi koreksi)" if {rsi:.1f} > 70 else "Netral"}
- MA Trend: {"Bullish (MA20 > MA50)" if {ma20:.0f} > {ma50:.0f} else "Bearish (MA20 < MA50)"}
- MACD: {"Bullish crossover" if {macd:.2f} > {macd_signal:.2f} else "Bearish crossover"}

Berikan analisis dalam format JSON berikut:
{{
  "signal": "BELI" | "JUAL" | "HOLD",
  "confidence": "rendah" | "sedang" | "tinggi",
  "reason": "alasan singkat maksimal 2 kalimat",
  "risk": "faktor risiko yang perlu diwaspadai (opsional)"
}}"""


class BaseAIProvider(ABC):
    name: str = "base"

    def _build_prompt(self, data: MarketData) -> str:
        volume_ratio = ((data.volume / data.avg_volume) - 1) * 100 if data.avg_volume > 0 else 0
        rsi = data.rsi

        prompt = f"""Analisis data IHSG berikut dan berikan rekomendasi trading:

DATA PASAR SAAT INI:
- Harga IHSG: {data.current_price:,.0f}
- Perubahan hari ini: {data.change_pct:+.2f}%
- Volume vs rata-rata: {volume_ratio:+.0f}%
- Tren 5 hari: {data.trend_5d:+.2f}%
- Tren 1 bulan: {data.trend_1m:+.2f}%

INDIKATOR TEKNIKAL:
- RSI(14): {rsi:.1f}
- MA20: {data.ma20:,.0f} | MA50: {data.ma50:,.0f} | MA200: {data.ma200:,.0f}
- MACD: {data.macd:.2f} | Signal: {data.macd_signal:.2f}
- 52W High: {data.high_52w:,.0f} | 52W Low: {data.low_52w:,.0f}

INTERPRETASI CEPAT:
- RSI: {"Oversold (potensi rebound)" if rsi < 30 else "Overbought (potensi koreksi)" if rsi > 70 else "Netral"}
- MA Trend: {"Bullish (MA20 > MA50)" if data.ma20 > data.ma50 else "Bearish (MA20 < MA50)"}
- MACD: {"Bullish crossover" if data.macd > data.macd_signal else "Bearish crossover"}

Berikan analisis dalam format JSON berikut:
{{
  "signal": "BELI" | "JUAL" | "HOLD",
  "confidence": "rendah" | "sedang" | "tinggi",
  "reason": "alasan singkat maksimal 2 kalimat",
  "risk": "faktor risiko yang perlu diwaspadai (opsional)"
}}"""
        return prompt

    def _parse_response(self, raw: str) -> dict:
        # Bersihkan markdown code fence jika ada
        cleaned = re.sub(r'```(?:json)?\s*', '', raw).strip()

        # Coba parse langsung
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Cari blok JSON pertama yang valid
        for match in re.finditer(r'\{[^{}]*\}', cleaned, re.DOTALL):
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue

        # Coba ekstrak dengan regex greedy (untuk nested object)
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Tidak ada JSON valid dalam response: {raw[:300]}")

    def _build_result(self, parsed: dict, success: bool = True, error: str = None) -> ProviderResult:
        if not success:
            return ProviderResult(
                provider=self.name,
                signal=SignalType.HOLD,
                confidence=ConfidenceLevel.LOW,
                reason="Analisis tidak tersedia",
                success=False,
                error=error,
            )
        return ProviderResult(
            provider=self.name,
            signal=SignalType(parsed.get("signal", "HOLD")),
            confidence=ConfidenceLevel(parsed.get("confidence", "rendah")),
            reason=parsed.get("reason", ""),
            risk=parsed.get("risk"),
            success=True,
        )

    @abstractmethod
    def analyze(self, data: MarketData) -> ProviderResult:
        pass

    @property
    def cost_per_1k_tokens(self) -> float:
        return 0.0
