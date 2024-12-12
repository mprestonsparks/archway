"""LLM adapter module for OpenAI's O1 model."""

from dataclasses import dataclass
from typing import List, Optional

from openai import OpenAI

from ..ports.llm import LLMConfig, LLMProvider, LLMResponse
from ..core.models import CodeSnippet


@dataclass
class O1Config(LLMConfig):
    """Configuration for OpenAI's O1 model."""

    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class O1ModelProvider(LLMProvider):
    """Provider for OpenAI's O1 model."""

    def __init__(self, config: O1Config):
        """Initialize the O1 model provider.

        Args:
            config: Configuration for the model
        """
        self.client = OpenAI(api_key=config.api_key)
        self.config = config

    async def initialize(self) -> None:
        """Initialize the provider. No-op for O1ModelProvider."""
        pass

    async def close(self) -> None:
        """Close the provider. No-op for O1ModelProvider."""
        pass

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from the model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            LLMResponse containing the generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
        )

        return LLMResponse(text=response.choices[0].message.content)

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
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        responses = []
        async for chunk in await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            top_p=self.config.top_p,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                responses.append(LLMResponse(text=chunk.choices[0].delta.content))

        return responses

    async def analyze_code(self, snippet: CodeSnippet) -> str:
        """Analyze code using the O1 model.

        Args:
            snippet: Code snippet to analyze

        Returns:
            Analysis result as a string
        """
        prompt = f"""Please analyze this code:

```{snippet.language}
{snippet.content}
```

Provide a detailed analysis including:
1. Code quality
2. Potential issues
3. Suggestions for improvement
"""
        response = await self.generate(prompt)
        return response.text

    async def suggest_refactoring(self, snippet: CodeSnippet, goal: str) -> str:
        """Suggest refactoring for code.

        Args:
            snippet: Code snippet to refactor
            goal: Goal of the refactoring

        Returns:
            Refactoring suggestions as a string
        """
        prompt = f"""Please suggest refactoring for this code with the goal: {goal}

```{snippet.language}
{snippet.content}
```

Provide:
1. Specific refactoring suggestions
2. Code examples where relevant
3. Expected benefits
"""
        response = await self.generate(prompt)
        return response.text

    async def explain_architecture(self, snippets: List[CodeSnippet]) -> str:
        """Explain the architecture of multiple code files.

        Args:
            snippets: List of code snippets to analyze

        Returns:
            Architecture explanation as a string
        """
        prompt = "Please analyze the architecture of these code files:\n\n"
        for snippet in snippets:
            prompt += f"""File: {snippet.location.path}
```{snippet.language}
{snippet.content}
```

"""
        prompt += """Provide:
1. Overall architecture description
2. Component relationships
3. Design patterns used
4. Potential improvements"""
        
        response = await self.generate(prompt)
        return response.text
