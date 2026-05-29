from openai import OpenAI
from providers.base import BaseAIProvider, SYSTEM_PROMPT
from models.signal import MarketData, ProviderResult


class OpenAIProvider(BaseAIProvider):
    name = "openai"
    cost_per_1k_tokens = 0.0025  # $2.5/1M tokens (GPT-4o)

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze(self, data: MarketData) -> ProviderResult:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": self._build_prompt(data)},
                ],
            )
            parsed = self._parse_response(response.choices[0].message.content)
            return self._build_result(parsed)
        except Exception as e:
            return self._build_result({}, success=False, error=str(e))
