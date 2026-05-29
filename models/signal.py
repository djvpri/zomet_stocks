from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import datetime


class SignalType(str, Enum):
    BUY = "BELI"
    SELL = "JUAL"
    HOLD = "HOLD"


class ConfidenceLevel(str, Enum):
    LOW = "rendah"
    MEDIUM = "sedang"
    HIGH = "tinggi"


class ProviderResult(BaseModel):
    provider: str
    signal: SignalType
    confidence: ConfidenceLevel
    reason: str
    risk: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    timestamp: datetime
    ihsg_price: float
    ihsg_change_pct: float
    signal: SignalType
    confidence: ConfidenceLevel
    reason: str
    risk: Optional[str] = None
    provider_used: str
    all_results: Optional[List[ProviderResult]] = None
    consensus_votes: Optional[dict] = None


class MarketData(BaseModel):
    symbol: str
    current_price: float
    change_pct: float
    volume: float
    avg_volume: float
    rsi: float
    ma20: float
    ma50: float
    ma200: float
    macd: float
    macd_signal: float
    trend_5d: float
    trend_1m: float
    high_52w: float
    low_52w: float
