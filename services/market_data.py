import yfinance as yf
import pandas as pd
import ta
from models.signal import MarketData
from config import settings


def fetch_ihsg_data() -> MarketData:
    ticker = yf.Ticker(settings.ihsg_symbol)
    df = ticker.history(period="1y", interval="1d")

    if df.empty:
        raise ValueError("Gagal mengambil data IHSG dari Yahoo Finance")

    df.dropna(inplace=True)

    # Harga terkini
    current_price = float(df["Close"].iloc[-1])
    prev_close = float(df["Close"].iloc[-2])
    change_pct = ((current_price - prev_close) / prev_close) * 100

    # Volume
    volume = float(df["Volume"].iloc[-1])
    avg_volume = float(df["Volume"].tail(20).mean())

    # RSI
    rsi_series = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi()
    rsi = float(rsi_series.iloc[-1])

    # Moving Averages
    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())
    ma200 = float(df["Close"].tail(200).mean())

    # MACD
    macd_indicator = ta.trend.MACD(close=df["Close"])
    macd = float(macd_indicator.macd().iloc[-1])
    macd_signal = float(macd_indicator.macd_signal().iloc[-1])

    # Trend
    price_5d_ago = float(df["Close"].iloc[-6]) if len(df) >= 6 else current_price
    price_1m_ago = float(df["Close"].iloc[-22]) if len(df) >= 22 else current_price
    trend_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
    trend_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100

    # 52W High/Low
    high_52w = float(df["High"].tail(252).max())
    low_52w = float(df["Low"].tail(252).min())

    return MarketData(
        symbol=settings.ihsg_symbol,
        current_price=current_price,
        change_pct=change_pct,
        volume=volume,
        avg_volume=avg_volume,
        rsi=rsi,
        ma20=ma20,
        ma50=ma50,
        ma200=ma200,
        macd=macd,
        macd_signal=macd_signal,
        trend_5d=trend_5d,
        trend_1m=trend_1m,
        high_52w=high_52w,
        low_52w=low_52w,
    )
