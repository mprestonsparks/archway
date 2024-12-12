"""Unit tests for core analysis functionality."""
from datetime import datetime
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.analysis import CodeAnalysisService
from src.core.models import (
    AnalysisRequest,
    AnalysisResult,
    CodeAnalysisType,
    CodeLocation,
    CodeSnippet,
    ModelType
)
from src.ports.code_analysis import CodeAnalyzer, CodeIndexer, ModelProvider

@pytest.fixture
def mock_analyzer():
    """Create a mock code analyzer."""
    analyzer = AsyncMock(spec=CodeAnalyzer)
    analyzer.analyze.return_value = AnalysisResult(
        request=None,
        suggestions=["Test suggestion"],
        confidence_score=0.9,
        execution_time=0.1,
        model_used=ModelType.LOCAL_LLM
    )
    return analyzer

@pytest.fixture
def mock_indexer():
    """Create a mock code indexer."""
    indexer = AsyncMock(spec=CodeIndexer)
    indexer.get_context.return_value = []
    return indexer

@pytest.fixture
def mock_model_providers():
    """Create mock model providers."""
    providers = {
        ModelType.LOCAL_LLM: AsyncMock(spec=ModelProvider),
        ModelType.OPENAI_O1: AsyncMock(spec=ModelProvider)
    }
    return providers

@pytest.fixture
def analysis_service(mock_analyzer, mock_indexer, mock_model_providers):
    """Create a CodeAnalysisService instance with mock dependencies."""
    return CodeAnalysisService(
        analyzer=mock_analyzer,
        indexer=mock_indexer,
        model_providers=mock_model_providers
    )

@pytest.fixture
def sample_code_snippet():
    """Create a sample code snippet for testing."""
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

@pytest.mark.asyncio
async def test_analyze_code(analysis_service, sample_code_snippet):
    """Test analyzing a single code snippet."""
    result = await analysis_service.analyze_code(
        code=sample_code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    assert isinstance(result, AnalysisResult)
    assert result.suggestions == ["Test suggestion"]
    assert result.confidence_score == 0.9
    assert result.model_used == ModelType.LOCAL_LLM

@pytest.mark.asyncio
async def test_analyze_code_caching(analysis_service, sample_code_snippet):
    """Test that analysis results are properly cached."""
    # First call
    result1 = await analysis_service.analyze_code(
        code=sample_code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    # Second call with same parameters
    result2 = await analysis_service.analyze_code(
        code=sample_code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    # Should return cached result
    assert result1 == result2
    assert analysis_service.analyzer.analyze.call_count == 1

@pytest.mark.asyncio
async def test_batch_analyze(analysis_service, sample_code_snippet):
    """Test analyzing multiple code snippets in batch."""
    snippets = [sample_code_snippet] * 3
    
    results = await analysis_service.batch_analyze(
        codes=snippets,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    assert len(results) == 3
    assert all(isinstance(r, AnalysisResult) for r in results)

@pytest.mark.asyncio
async def test_clear_cache(analysis_service, sample_code_snippet):
    """Test clearing the analysis cache."""
    # Perform analysis to populate cache
    await analysis_service.analyze_code(
        code=sample_code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    # Clear cache
    analysis_service.clear_cache()
    
    # Perform analysis again
    await analysis_service.analyze_code(
        code=sample_code_snippet,
        analysis_type=CodeAnalysisType.SEMANTIC,
        model_type=ModelType.LOCAL_LLM
    )
    
    # Should have called analyze twice
    assert analysis_service.analyzer.analyze.call_count == 2
