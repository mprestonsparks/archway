"""LLM adapter for OpenAI."""
from dataclasses import dataclass
from typing import List, Optional

import openai


@dataclass
class O1Config:
    """Configuration for O1 model provider."""
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048


class O1ModelProvider:
    """O1 model provider."""
    def __init__(self, config: O1Config):
        """Initialize O1 model provider."""
        self.config = config
        openai.api_key = config.api_key

    async def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Analyze code using O1 model."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await openai.ChatCompletion.acreate(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return response.choices[0].message.content
