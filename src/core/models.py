"""Core domain models."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class AnalysisType(str, Enum):
    """Type of code analysis."""

    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"


@dataclass
class CodeLocation:
    """Location of a code symbol."""

    path: str
    line: int
    character: int


@dataclass
class CodeSnippet:
    """Code snippet with location information."""

    content: str
    language: str
    location: CodeLocation


@dataclass
class AnalysisResult:
    """Result of code analysis."""

    analysis_type: AnalysisType
    findings: List[str]
    suggestions: List[str]


@dataclass
class RefactoringStep:
    """Step in a refactoring process."""

    description: str
    code_changes: List[CodeSnippet]


@dataclass
class RefactoringPlan:
    """Plan for refactoring code."""

    goal: str
    steps: List[RefactoringStep]
    estimated_effort: str


@dataclass
class ArchitectureComponent:
    """Component in a software architecture."""

    name: str
    description: str
    responsibilities: List[str]
    dependencies: List[str]


@dataclass
class ArchitectureAnalysis:
    """Analysis of software architecture."""

    components: List[ArchitectureComponent]
    patterns: List[str]
    concerns: List[str]
    recommendations: List[str]


@dataclass
class SearchQuery:
    """Query for code search."""

    text: str
    file_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    max_results: int = 10
