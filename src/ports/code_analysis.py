"""Interfaces for code analysis functionality."""
from abc import ABC, abstractmethod
from typing import List

from src.core.models import (
    AnalysisRequest,
    AnalysisResult,
    CodebaseContext,
    CodeSnippet
)

class CodeAnalyzer(ABC):
    """Interface for analyzing code."""
    
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze code based on the request."""
        pass

    @abstractmethod
    async def batch_analyze(self, requests: List[AnalysisRequest]) -> List[AnalysisResult]:
        """Analyze multiple code snippets in batch."""
        pass

class CodeIndexer(ABC):
    """Interface for indexing and searching code."""
    
    @abstractmethod
    async def index_codebase(self, root_path: str) -> CodebaseContext:
        """Index the entire codebase."""
        pass
    
    @abstractmethod
    async def search(self, query: str) -> List[CodeSnippet]:
        """Search for code snippets matching the query."""
        pass
    
    @abstractmethod
    async def get_context(self, snippet: CodeSnippet) -> List[CodeSnippet]:
        """Get surrounding context for a code snippet."""
        pass

class ModelProvider(ABC):
    """Interface for AI model providers."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model and required resources."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream a response from the model."""
        pass
