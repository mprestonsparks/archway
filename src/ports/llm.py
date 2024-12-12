"""LLM port interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LLMConfig:
    """Base configuration for LLM providers."""

    pass


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    text: str


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from the model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            LLMResponse containing the generated text
        """
        pass

    @abstractmethod
    async def generate_stream(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> List[LLMResponse]:
        """Generate a streaming response from the model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            List of LLMResponse containing the generated text chunks
        """
        pass
