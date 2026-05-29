from google import genai
from google.genai import types
from providers.base import BaseAIProvider, SYSTEM_PROMPT
from models.signal import MarketData, ProviderResult


class GeminiProvider(BaseAIProvider):
    name = "gemini"
    cost_per_1k_tokens = 0.000075  # Gemini Flash sangat murah

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def analyze(self, data: MarketData) -> ProviderResult:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self._build_prompt(data),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    max_output_tokens=1024,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            parsed = self._parse_response(response.text)
            return self._build_result(parsed)
        except Exception as e:
            return self._build_result({}, success=False, error=str(e))
