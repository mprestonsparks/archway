"""Core business logic for code analysis."""
from datetime import datetime
from typing import Dict, List, Optional

from src.core.models import (
    AnalysisRequest,
    AnalysisResult,
    CodeAnalysisType,
    CodeSnippet,
    ModelType
)
from src.ports.code_analysis import CodeAnalyzer, CodeIndexer, ModelProvider

class CodeAnalysisService:
    """Core service for analyzing code."""

    def __init__(
        self,
        analyzer: CodeAnalyzer,
        indexer: CodeIndexer,
        model_providers: Dict[ModelType, ModelProvider]
    ):
        """Initialize the code analysis service."""
        self.analyzer = analyzer
        self.indexer = indexer
        self.model_providers = model_providers
        self._analysis_cache: Dict[str, AnalysisResult] = {}

    async def analyze_code(
        self,
        code: CodeSnippet,
        analysis_type: CodeAnalysisType,
        model_type: ModelType,
        use_cache: bool = True
    ) -> AnalysisResult:
        """
        Analyze a code snippet using the specified model and analysis type.
        
        Args:
            code: The code snippet to analyze
            analysis_type: Type of analysis to perform
            model_type: Type of model to use
            use_cache: Whether to use cached results if available
        
        Returns:
            AnalysisResult containing the analysis
        """
        cache_key = self._generate_cache_key(code, analysis_type, model_type)
        
        if use_cache and cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        # Get additional context if needed
        context_snippets = await self._get_relevant_context(code)
        
        # Create analysis request
        request = AnalysisRequest(
            code=code,
            analysis_type=analysis_type,
            model_type=model_type,
            context={"related_snippets": len(context_snippets)}
        )
        
        # Perform analysis
        result = await self.analyzer.analyze(request)
        
        # Cache result
        if use_cache:
            self._analysis_cache[cache_key] = result
        
        return result

    async def batch_analyze(
        self,
        codes: List[CodeSnippet],
        analysis_type: CodeAnalysisType,
        model_type: ModelType
    ) -> List[AnalysisResult]:
        """Analyze multiple code snippets in batch."""
        requests = []
        
        for code in codes:
            context_snippets = await self._get_relevant_context(code)
            request = AnalysisRequest(
                code=code,
                analysis_type=analysis_type,
                model_type=model_type,
                context={"related_snippets": len(context_snippets)}
            )
            requests.append(request)
        
        return await self.analyzer.batch_analyze(requests)

    async def _get_relevant_context(self, code: CodeSnippet) -> List[CodeSnippet]:
        """Get relevant context for a code snippet."""
        return await self.indexer.get_context(code)

    def _generate_cache_key(
        self,
        code: CodeSnippet,
        analysis_type: CodeAnalysisType,
        model_type: ModelType
    ) -> str:
        """Generate a cache key for an analysis request."""
        return f"{code.location.file_path}:{code.location.start_line}:{analysis_type.value}:{model_type.value}"

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._analysis_cache.clear()
