import os
from typing import Optional

from openai import OpenAI


class DeepSeekClient:
    """
    DeepSeek-R1 clinical reasoning agent.

    This agent performs clinical reasoning using information
    prepared by FLAN-T5 and evidence retrieved through RAG.

    It does not provide a confirmed diagnosis or replace
    the existing safety layer.
    """

    def __init__(self, model: str = "deepseek-reasoner"):
        self.model = model
        self._client: Optional[OpenAI] = None

    def _init_client(self) -> None:
        if self._client is not None:
            return

        api_key = os.getenv("DEEPSEEK_API_KEY")

        if not api_key:
            raise EnvironmentError(
                "DEEPSEEK_API_KEY not found. Add it to apikey.env."
            )

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self._init_client()

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        if not response.choices:
            raise RuntimeError(
                "DeepSeek returned an empty response."
            )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "DeepSeek returned an empty response."
            )

        return content.strip()
