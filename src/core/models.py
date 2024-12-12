"""Core domain models for Archway."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

class CodeAnalysisType(Enum):
    """Types of code analysis that can be performed."""
    SEMANTIC = "semantic"
    SYNTACTIC = "syntactic"
    ARCHITECTURAL = "architectural"
    SECURITY = "security"

class ModelType(Enum):
    """Types of AI models available in the system."""
    LOCAL_LLM = "local_llm"
    OPENAI_O1 = "openai_o1"

@dataclass
class CodeLocation:
    """Represents a location in the codebase."""
    file_path: str
    start_line: int
    end_line: Optional[int] = None
    start_column: Optional[int] = None
    end_column: Optional[int] = None

@dataclass
class CodeSnippet:
    """Represents a piece of code with its location and metadata."""
    content: str
    location: CodeLocation
    language: str
    last_modified: datetime
    metadata: Dict[str, str] = None

@dataclass
class AnalysisRequest:
    """Represents a request for code analysis."""
    code: Union[CodeSnippet, List[CodeSnippet]]
    analysis_type: CodeAnalysisType
    model_type: ModelType
    context: Optional[Dict[str, str]] = None

@dataclass
class AnalysisResult:
    """Represents the result of a code analysis."""
    request: AnalysisRequest
    suggestions: List[str]
    confidence_score: float
    execution_time: float
    model_used: ModelType
    timestamp: datetime = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class CodebaseContext:
    """Represents the context of the entire codebase."""
    root_path: str
    indexed_files: List[str]
    last_indexed: datetime
    total_files: int
    languages: Dict[str, int]  # language -> number of files
    metadata: Dict[str, str] = None
