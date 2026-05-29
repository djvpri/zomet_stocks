from openai import OpenAI
from providers.base import BaseAIProvider, SYSTEM_PROMPT
from models.signal import MarketData, ProviderResult


class QwenProvider(BaseAIProvider):
    name = "qwen"
    cost_per_1k_tokens = 0.0004  # $0.4/1M tokens

    def __init__(self, api_key: str, model: str = "qwen-plus"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
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
