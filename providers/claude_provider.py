import anthropic
from providers.base import BaseAIProvider, SYSTEM_PROMPT
from models.signal import MarketData, ProviderResult


class ClaudeProvider(BaseAIProvider):
    name = "claude"
    cost_per_1k_tokens = 0.003  # $3/1M tokens

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze(self, data: MarketData) -> ProviderResult:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": self._build_prompt(data)}],
            )
            parsed = self._parse_response(response.content[0].text)
            return self._build_result(parsed)
        except Exception as e:
            return self._build_result({}, success=False, error=str(e))
