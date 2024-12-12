"""Unit tests for LLM-based code analyzer."""
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.adapters.analysis.llm_analyzer import LLMCodeAnalyzer
from src.core.models import (
    AnalysisRequest,
    CodeAnalysisType,
    CodeLocation,
    CodeSnippet,
    ModelType
)

@pytest.fixture
def code_snippet():
    """Create a test code snippet."""
    return CodeSnippet(
        content="def test(): pass",
        location=CodeLocation(
            file_path="test.py",
            start_line=1,
            end_line=1
        ),
        language="python",
        last_modified=datetime.utcnow()
    )

@pytest.fixture
def mock_model_provider():
    """Create a mock model provider."""
    provider = AsyncMock()
    provider.generate.return_value = """
    1. Improve function name to be more descriptive
    2. Add docstring
    3. Consider adding type hints
    """
    return provider

@pytest.fixture
def analyzer(mock_model_provider):
    """Create a test analyzer instance."""
    return LLMCodeAnalyzer({
        ModelType.LOCAL_LLM: mock_model_provider
    })

@pytest.mark.asyncio
async def test_analyze_semantic(analyzer, code_snippet):
    """Test semantic code analysis."""
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    result = await analyzer.analyze(request)
    
    assert result.request == request
    assert len(result.suggestions) > 0
    assert result.model_used == ModelType.LOCAL_LLM
    assert result.execution_time > 0

@pytest.mark.asyncio
async def test_analyze_syntactic(analyzer, code_snippet):
    """Test syntactic code analysis."""
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.SYNTACTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    result = await analyzer.analyze(request)
    
    assert result.request == request
    assert len(result.suggestions) > 0
    assert result.model_used == ModelType.LOCAL_LLM

@pytest.mark.asyncio
async def test_analyze_architectural(analyzer, code_snippet):
    """Test architectural code analysis."""
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.ARCHITECTURAL,
        model_type=ModelType.LOCAL_LLM,
        context={"module": "test_module"}
    )
    
    result = await analyzer.analyze(request)
    
    assert result.request == request
    assert len(result.suggestions) > 0
    assert result.model_used == ModelType.LOCAL_LLM

@pytest.mark.asyncio
async def test_analyze_security(analyzer, code_snippet):
    """Test security code analysis."""
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.SECURITY,
        model_type=ModelType.LOCAL_LLM
    )
    
    result = await analyzer.analyze(request)
    
    assert result.request == request
    assert len(result.suggestions) > 0
    assert result.model_used == ModelType.LOCAL_LLM

@pytest.mark.asyncio
async def test_batch_analyze(analyzer, code_snippet):
    """Test batch code analysis."""
    requests = [
        AnalysisRequest(
            code=code_snippet,
            analysis_type=analysis_type,
            model_type=ModelType.LOCAL_LLM
        )
        for analysis_type in CodeAnalysisType
    ]
    
    results = await analyzer.batch_analyze(requests)
    
    assert len(results) == len(requests)
    for result in results:
        assert len(result.suggestions) > 0
        assert result.model_used == ModelType.LOCAL_LLM

@pytest.mark.asyncio
async def test_analyze_invalid_model_type(analyzer, code_snippet):
    """Test analysis with invalid model type."""
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.OPENAI_O1  # Not provided in the analyzer
    )
    
    with pytest.raises(ValueError):
        await analyzer.analyze(request)

@pytest.mark.asyncio
async def test_analyze_with_error(analyzer, code_snippet, mock_model_provider):
    """Test analysis when model generation fails."""
    mock_model_provider.generate.side_effect = Exception("Generation failed")
    
    request = AnalysisRequest(
        code=code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    with pytest.raises(RuntimeError):
        await analyzer.analyze(request)
