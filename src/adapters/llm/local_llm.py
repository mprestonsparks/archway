"""Local LLM adapter implementation using Code Llama."""
import asyncio
from typing import AsyncIterator, Dict, Optional

import httpx
from pydantic import BaseModel, Field

from src.ports.code_analysis import ModelProvider


class LLMConfig(BaseModel):
    """Configuration for the local LLM service."""
    endpoint_url: str = Field(default="http://localhost:8080/generate")
    max_new_tokens: int = Field(default=512)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.95)
    timeout: float = Field(default=30.0)
    stream: bool = Field(default=False)


class LocalLLMProvider(ModelProvider):
    """Adapter for local Code Llama model."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the local LLM provider."""
        self.config = config or LLMConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the connection to the local LLM service."""
        try:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
            # Test the connection
            await self._client.get(self.config.endpoint_url.replace("/generate", "/health"))
            self._initialized = True
            return True
        except httpx.RequestError:
            self._initialized = False
            return False

    async def _ensure_initialized(self) -> None:
        """Ensure the provider is initialized."""
        if not self._initialized:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize Local LLM provider")

    def _prepare_prompt(self, prompt: str) -> Dict:
        """Prepare the prompt for the model."""
        return {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "stream": self.config.stream,
            }
        }

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        await self._ensure_initialized()
        
        # Override default parameters with kwargs
        params = self._prepare_prompt(prompt)
        params["parameters"].update(kwargs)
        
        try:
            response = await self._client.post(
                self.config.endpoint_url,
                json=params
            )
            response.raise_for_status()
            result = response.json()
            return result["generated_text"]
        except httpx.RequestError as e:
            raise RuntimeError(f"Error generating response: {str(e)}")

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream a response from the model."""
        await self._ensure_initialized()
        
        # Ensure streaming is enabled
        params = self._prepare_prompt(prompt)
        params["parameters"]["stream"] = True
        params["parameters"].update(kwargs)
        
        try:
            async with self._client.stream(
                "POST",
                self.config.endpoint_url,
                json=params
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        # Parse streaming response format
                        chunk = line.split("data: ")[-1]
                        if chunk != "[DONE]":
                            yield chunk
        except httpx.RequestError as e:
            raise RuntimeError(f"Error streaming response: {str(e)}")

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._initialized = False
