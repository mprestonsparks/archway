"""Integration tests for LLM adapters."""
import asyncio
import os
from typing import AsyncGenerator

import pytest
from pydantic import SecretStr

from src.adapters.llm import O1Config, O1ModelProvider
from src.core.models import CodeLocation, CodeSnippet


@pytest.fixture
def code_snippet() -> CodeSnippet:
    """Create a test code snippet."""
    return CodeSnippet(
        content="""def calculate_sum(a: int, b: int) -> int:
    \"\"\"Calculate the sum of two integers.\"\"\"
    return a + b""",
        language="python",
        location=CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=3
        )
    )


@pytest.fixture
async def o1_provider() -> AsyncGenerator[O1ModelProvider, None]:
    """Create and initialize an o1 model provider."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OpenAI API key not found in environment")
    
    config = O1Config(
        api_key=api_key,
        model="gpt-4",  # Use GPT-4 for testing
        temperature=0.0,  # Use deterministic responses
        max_tokens=500
    )
    provider = O1ModelProvider(config)
    
    try:
        success = await provider.initialize()
        if not success:
            pytest.skip("Failed to initialize o1 model provider")
        yield provider
    finally:
        await provider.close()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_code_analysis(o1_provider: O1ModelProvider, code_snippet: CodeSnippet):
    """Test code analysis with the o1 model."""
    result = await o1_provider.analyze_code(
        code_snippet,
        analysis_type="code quality"
    )
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0
    # The response should mention type hints since we used them
    assert "type" in result.lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_refactoring_suggestion(o1_provider: O1ModelProvider, code_snippet: CodeSnippet):
    """Test refactoring suggestions with the o1 model."""
    result = await o1_provider.suggest_refactoring(
        code_snippet,
        goal="improve readability"
    )
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0
    # The response should mention docstring since that's a common readability improvement
    assert "docstring" in result.lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_streaming_generation(o1_provider: O1ModelProvider, code_snippet: CodeSnippet):
    """Test streaming generation with the o1 model."""
    chunks = []
    async for chunk in await o1_provider.stream_generate(
        "Explain this code",
        code_snippets=[code_snippet]
    ):
        assert chunk
        assert isinstance(chunk, str)
        chunks.append(chunk)
    
    complete_response = "".join(chunks)
    assert len(complete_response) > 0
    # The response should mention the function name
    assert "calculate_sum" in complete_response


@pytest.mark.asyncio
@pytest.mark.integration
async def test_architecture_explanation(o1_provider: O1ModelProvider):
    """Test architecture explanation with multiple code snippets."""
    snippets = [
        CodeSnippet(
            content="""class UserService:
    \"\"\"Service for managing users.\"\"\"
    def __init__(self, repository):
        self.repository = repository
    
    async def get_user(self, user_id: str):
        return await self.repository.get(user_id)""",
            language="python",
            location=CodeLocation(
                file_path="user_service.py",
                start_line=1,
                end_line=7
            )
        ),
        CodeSnippet(
            content="""class UserRepository:
    \"\"\"Repository for user data.\"\"\"
    async def get(self, user_id: str):
        # Get user from database
        return await self.db.users.find_one({"_id": user_id})""",
            language="python",
            location=CodeLocation(
                file_path="user_repository.py",
                start_line=1,
                end_line=5
            )
        )
    ]
    
    result = await o1_provider.explain_architecture(snippets)
    
    assert result
    assert isinstance(result, str)
    assert len(result) > 0
    # The response should mention common architectural patterns
    assert any(pattern in result.lower() for pattern in ["repository", "service", "layer"])
