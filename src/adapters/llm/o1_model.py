"""OpenAI o1 model adapter implementation."""
import asyncio
from datetime import datetime
from typing import AsyncIterator, Dict, List, Optional, Union

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from src.core.models import CodeSnippet
from src.ports.code_analysis import ModelProvider


class O1Config(BaseModel):
    """Configuration for OpenAI o1 model."""
    api_key: str = Field(default=None)
    model: str = Field(default="o1")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2048)
    timeout: float = Field(default=30.0)
    stream: bool = Field(default=False)
    max_context_tokens: int = Field(default=8192)


class O1ModelProvider(ModelProvider):
    """Adapter for OpenAI's o1 model."""

    def __init__(self, config: Optional[O1Config] = None):
        """Initialize the o1 model provider."""
        self.config = config or O1Config()
        self._client: Optional[AsyncOpenAI] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the OpenAI client."""
        try:
            if not self.config.api_key:
                raise ValueError("OpenAI API key is required")
            
            self._client = AsyncOpenAI(api_key=self.config.api_key)
            # Test connection with a minimal request
            await self._client.models.retrieve(self.config.model)
            self._initialized = True
            return True
        except Exception:
            self._initialized = False
            return False

    async def _ensure_initialized(self) -> None:
        """Ensure the provider is initialized."""
        if not self._initialized:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize o1 model provider")

    def _prepare_prompt(
        self,
        prompt: str,
        code_snippets: Optional[List[CodeSnippet]] = None
    ) -> str:
        """Prepare the prompt with code context."""
        if not code_snippets:
            return prompt

        context_str = "\nRelevant code context:\n"
        for snippet in code_snippets:
            context_str += f"\nFile: {snippet.location.file_path}\n"
            context_str += f"Lines {snippet.location.start_line}-{snippet.location.end_line}:\n"
            context_str += f"```{snippet.language}\n{snippet.content}\n```\n"

        return f"{prompt}\n{context_str}"

    def _create_messages(
        self,
        prompt: str,
        code_snippets: Optional[List[CodeSnippet]] = None,
        system_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Create message list for the API call."""
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        else:
            messages.append({
                "role": "system",
                "content": (
                    "You are an expert software developer assistant. "
                    "Analyze code and provide detailed, accurate responses. "
                    "Focus on architectural patterns, best practices, and potential improvements."
                )
            })
        
        # Add user message with context
        messages.append({
            "role": "user",
            "content": self._prepare_prompt(prompt, code_snippets)
        })
        
        return messages

    async def generate(
        self,
        prompt: str,
        code_snippets: Optional[List[CodeSnippet]] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response from the model."""
        await self._ensure_initialized()
        
        try:
            messages = self._create_messages(prompt, code_snippets, system_message)
            
            # Prepare parameters
            params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": False
            }
            params.update(kwargs)
            
            response = await self._client.chat.completions.create(**params)
            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"Error generating response: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        code_snippets: Optional[List[CodeSnippet]] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream a response from the model."""
        await self._ensure_initialized()
        
        try:
            messages = self._create_messages(prompt, code_snippets, system_message)
            
            # Prepare parameters
            params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": True
            }
            params.update(kwargs)
            
            async for chunk in await self._client.chat.completions.create(**params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"Error streaming response: {str(e)}")

    async def analyze_code(
        self,
        code_snippets: Union[CodeSnippet, List[CodeSnippet]],
        analysis_type: str,
        **kwargs
    ) -> str:
        """Analyze code using the o1 model."""
        if isinstance(code_snippets, CodeSnippet):
            code_snippets = [code_snippets]

        prompt = f"Analyze the following code focusing on {analysis_type}. "
        prompt += "Provide specific, actionable recommendations for improvement."

        return await self.generate(
            prompt=prompt,
            code_snippets=code_snippets,
            system_message=(
                "You are an expert code reviewer. Focus on providing detailed, "
                f"actionable feedback regarding {analysis_type}. Consider best "
                "practices, common pitfalls, and potential optimizations."
            ),
            **kwargs
        )

    async def suggest_refactoring(
        self,
        code_snippets: Union[CodeSnippet, List[CodeSnippet]],
        goal: str,
        **kwargs
    ) -> str:
        """Suggest refactoring steps for the given code."""
        if isinstance(code_snippets, CodeSnippet):
            code_snippets = [code_snippets]

        prompt = f"Suggest a detailed refactoring plan to achieve the following goal: {goal}\n"
        prompt += "Provide step-by-step instructions and explain the benefits of each change."

        return await self.generate(
            prompt=prompt,
            code_snippets=code_snippets,
            system_message=(
                "You are an expert in code refactoring. Provide detailed, practical "
                "refactoring suggestions that improve code quality while maintaining "
                "functionality. Consider maintainability, readability, and performance."
            ),
            **kwargs
        )

    async def explain_architecture(
        self,
        code_snippets: List[CodeSnippet],
        **kwargs
    ) -> str:
        """Explain the architecture of the provided code."""
        prompt = (
            "Analyze and explain the architecture of the provided code. "
            "Focus on design patterns, component relationships, and architectural decisions."
        )

        return await self.generate(
            prompt=prompt,
            code_snippets=code_snippets,
            system_message=(
                "You are an expert software architect. Analyze and explain code "
                "architecture in detail, focusing on patterns, principles, and "
                "design decisions. Consider scalability, maintainability, and "
                "best practices."
            ),
            **kwargs
        )

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.close()
            self._initialized = False
