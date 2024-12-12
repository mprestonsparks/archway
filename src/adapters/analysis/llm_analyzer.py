"""Code analyzer implementation using LLM."""
import asyncio
from datetime import datetime
from typing import Dict, List

from src.core.models import (
    AnalysisRequest,
    AnalysisResult,
    CodeAnalysisType,
    CodeSnippet,
    ModelType
)
from src.ports.code_analysis import CodeAnalyzer, ModelProvider


class LLMCodeAnalyzer(CodeAnalyzer):
    """Code analyzer that uses LLM for analysis."""

    def __init__(self, model_providers: Dict[ModelType, ModelProvider]):
        """Initialize the LLM code analyzer."""
        self.model_providers = model_providers

    def _create_prompt(self, request: AnalysisRequest) -> str:
        """Create a prompt for the LLM based on the analysis request."""
        prompt_templates = {
            CodeAnalysisType.SEMANTIC: self._create_semantic_prompt,
            CodeAnalysisType.SYNTACTIC: self._create_syntactic_prompt,
            CodeAnalysisType.ARCHITECTURAL: self._create_architectural_prompt,
            CodeAnalysisType.SECURITY: self._create_security_prompt,
        }
        
        template_func = prompt_templates.get(request.analysis_type)
        if not template_func:
            raise ValueError(f"Unsupported analysis type: {request.analysis_type}")
        
        return template_func(request)

    def _create_semantic_prompt(self, request: AnalysisRequest) -> str:
        """Create a prompt for semantic analysis."""
        code = request.code
        if isinstance(code, list):
            code = code[0]  # Use first snippet for demonstration
        
        return f"""Analyze the following code semantically and provide suggestions for improvement:

Code ({code.language}):
{code.content}

Consider:
1. Code readability and clarity
2. Variable and function naming
3. Code organization
4. Best practices for {code.language}

Provide specific, actionable suggestions in a concise format."""

    def _create_syntactic_prompt(self, request: AnalysisRequest) -> str:
        """Create a prompt for syntactic analysis."""
        code = request.code
        if isinstance(code, list):
            code = code[0]
        
        return f"""Analyze the following code for syntactic correctness and style:

Code ({code.language}):
{code.content}

Check for:
1. Syntax errors
2. Style guide compliance
3. Proper indentation
4. Consistent formatting

List any issues found and suggest fixes."""

    def _create_architectural_prompt(self, request: AnalysisRequest) -> str:
        """Create a prompt for architectural analysis."""
        code = request.code
        if isinstance(code, list):
            code = code[0]
        
        return f"""Analyze the following code for architectural patterns and design:

Code ({code.language}):
{code.content}

Context: {request.context or 'No additional context provided'}

Evaluate:
1. Design patterns used
2. Component relationships
3. Dependency management
4. Architectural principles

Provide recommendations for architectural improvements."""

    def _create_security_prompt(self, request: AnalysisRequest) -> str:
        """Create a prompt for security analysis."""
        code = request.code
        if isinstance(code, list):
            code = code[0]
        
        return f"""Analyze the following code for security vulnerabilities:

Code ({code.language}):
{code.content}

Check for:
1. Common vulnerabilities
2. Input validation
3. Authentication/authorization issues
4. Data handling concerns

List potential security issues and recommended fixes."""

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze code using the specified model."""
        start_time = datetime.utcnow()
        
        provider = self.model_providers.get(request.model_type)
        if not provider:
            raise ValueError(f"No provider found for model type: {request.model_type}")
        
        prompt = self._create_prompt(request)
        
        try:
            response = await provider.generate(prompt)
            suggestions = self._parse_suggestions(response)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AnalysisResult(
                request=request,
                suggestions=suggestions,
                confidence_score=0.8,  # TODO: Implement confidence scoring
                execution_time=execution_time,
                model_used=request.model_type
            )
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")

    async def batch_analyze(
        self,
        requests: List[AnalysisRequest]
    ) -> List[AnalysisResult]:
        """Analyze multiple code snippets in parallel."""
        tasks = [self.analyze(request) for request in requests]
        return await asyncio.gather(*tasks)

    def _parse_suggestions(self, response: str) -> List[str]:
        """Parse the LLM response into a list of suggestions."""
        # Split response into lines and filter out empty ones
        lines = [line.strip() for line in response.split("\n") if line.strip()]
        
        # Extract suggestions (lines that look like suggestions)
        suggestions = []
        for line in lines:
            # Remove common list markers
            cleaned = line.lstrip("*-•").strip()
            if cleaned:
                suggestions.append(cleaned)
        
        return suggestions
