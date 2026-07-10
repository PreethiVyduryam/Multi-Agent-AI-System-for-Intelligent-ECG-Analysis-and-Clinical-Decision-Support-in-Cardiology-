import os
import time
from typing import Optional, Sequence, Callable, Any


class GeminiChatModel:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self._client = None  # Lazy init

    def _init_client(self):
        if self._client is not None:
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not found. Add it to apikey.env."
            )

        # Lazy import here (IMPORTANT)
        from google import genai
        from google.genai import types

        self._genai = genai
        self._types = types
        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> str:
        self._init_client()

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        max_retries = 4
        base_delay = 2

        for attempt in range(max_retries):
            try:
                config = None
                if tools:
                    config = self._types.GenerateContentConfig(
                        tools=list(tools)
                    )

                response = self._client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=config,
                )

                if not response.text:
                    raise RuntimeError("Gemini returned an empty response.")

                return response.text.strip()

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay ** (attempt + 1)
                    print(
                        f"Gemini error: {e}. Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                    continue

                raise RuntimeError(
                    f"Failed after {max_retries} attempts: {e}"
                ) from e