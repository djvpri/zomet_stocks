from typing import List, Optional
from config import settings
from models.signal import MarketData, AnalysisResult, ProviderResult, SignalType, ConfidenceLevel
from providers.base import BaseAIProvider
from datetime import datetime


def _load_provider(name: str) -> Optional[BaseAIProvider]:
    """Inisialisasi provider berdasarkan nama, return None jika API key kosong."""
    name = name.strip().lower()

    if name == "claude" and settings.claude_api_key:
        from providers.claude_provider import ClaudeProvider
        return ClaudeProvider(settings.claude_api_key)

    elif name == "qwen" and settings.qwen_api_key:
        from providers.qwen_provider import QwenProvider
        return QwenProvider(settings.qwen_api_key)

    elif name == "deepseek" and settings.deepseek_api_key:
        from providers.deepseek_provider import DeepSeekProvider
        return DeepSeekProvider(settings.deepseek_api_key)

    elif name == "gemini" and settings.gemini_api_key:
        from providers.gemini_provider import GeminiProvider
        return GeminiProvider(settings.gemini_api_key)

    elif name == "groq" and settings.groq_api_key:
        from providers.groq_provider import GroqProvider
        return GroqProvider(settings.groq_api_key)

    elif name == "openai" and settings.openai_api_key:
        from providers.openai_provider import OpenAIProvider
        return OpenAIProvider(settings.openai_api_key)

    return None


def _confidence_weight(level: ConfidenceLevel) -> int:
    return {"rendah": 1, "sedang": 2, "tinggi": 3}.get(level, 1)


class AIManager:
    def analyze(self, market_data: MarketData) -> AnalysisResult:
        mode = settings.ai_mode.lower()

        if mode == "single":
            return self._single(market_data)
        elif mode == "fallback":
            return self._fallback(market_data)
        elif mode == "consensus":
            return self._consensus(market_data)
        elif mode == "cheapest":
            return self._cheapest(market_data)
        else:
            return self._fallback(market_data)

    def _single(self, data: MarketData) -> AnalysisResult:
        provider = _load_provider(settings.primary_provider)
        if not provider:
            raise RuntimeError(f"Provider '{settings.primary_provider}' tidak tersedia atau API key kosong")
        result = provider.analyze(data)
        return self._to_analysis(result, data, [result])

    def _fallback(self, data: MarketData) -> AnalysisResult:
        # Coba primary dulu
        primary = _load_provider(settings.primary_provider)
        if primary:
            result = primary.analyze(data)
            if result.success:
                return self._to_analysis(result, data, [result])

        # Fallback ke provider berikutnya
        for name in settings.get_fallback_list():
            provider = _load_provider(name)
            if not provider:
                continue
            result = provider.analyze(data)
            if result.success:
                return self._to_analysis(result, data, [result])

        raise RuntimeError("Semua provider AI gagal menganalisis data")

    def _consensus(self, data: MarketData) -> AnalysisResult:
        results: List[ProviderResult] = []

        for name in settings.get_consensus_list():
            provider = _load_provider(name)
            if not provider:
                continue
            result = provider.analyze(data)
            results.append(result)

        if not results:
            raise RuntimeError("Tidak ada provider aktif untuk consensus")

        successful = [r for r in results if r.success]
        if not successful:
            raise RuntimeError("Semua provider gagal dalam mode consensus")

        # Hitung votes dengan bobot confidence
        vote_scores: dict = {}
        for r in successful:
            score = _confidence_weight(r.confidence)
            vote_scores[r.signal] = vote_scores.get(r.signal, 0) + score

        winning_signal = max(vote_scores, key=vote_scores.get)
        total_score = sum(vote_scores.values())
        win_ratio = vote_scores[winning_signal] / total_score

        # Tentukan confidence berdasarkan kekuatan consensus
        if win_ratio >= 0.75:
            confidence = ConfidenceLevel.HIGH
        elif win_ratio >= 0.5:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW

        # Gabungkan alasan dari provider yang setuju
        matching = [r for r in successful if r.signal == winning_signal]
        reason = matching[0].reason if matching else "Consensus AI"
        risk = next((r.risk for r in matching if r.risk), None)

        final = ProviderResult(
            provider=f"consensus({len(successful)} providers)",
            signal=winning_signal,
            confidence=confidence,
            reason=reason,
            risk=risk,
            success=True,
        )

        votes = {str(k): v for k, v in vote_scores.items()}
        return self._to_analysis(final, data, results, consensus_votes=votes)

    def _cheapest(self, data: MarketData) -> AnalysisResult:
        # Urutkan semua provider berdasarkan cost, pakai yang termurah dan aktif
        all_providers = ["gemini", "deepseek", "qwen", "groq", "openai", "claude"]
        for name in all_providers:
            provider = _load_provider(name)
            if not provider:
                continue
            result = provider.analyze(data)
            if result.success:
                return self._to_analysis(result, data, [result])

        raise RuntimeError("Tidak ada provider aktif")

    def _to_analysis(
        self,
        result: ProviderResult,
        data: MarketData,
        all_results: List[ProviderResult],
        consensus_votes: dict = None,
    ) -> AnalysisResult:
        return AnalysisResult(
            timestamp=datetime.now(),
            ihsg_price=data.current_price,
            ihsg_change_pct=data.change_pct,
            signal=result.signal,
            confidence=result.confidence,
            reason=result.reason,
            risk=result.risk,
            provider_used=result.provider,
            all_results=all_results,
            consensus_votes=consensus_votes,
        )
