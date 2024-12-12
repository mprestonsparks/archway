"""Storage port for persisting analysis results."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..core.models import (
    AnalysisResult,
    ArchitectureAnalysis,
    RefactoringPlan,
)


class AnalysisRecord:
    """Record of a code analysis with metadata."""

    def __init__(
        self,
        id: str,
        timestamp: datetime,
        file_path: str,
        result: AnalysisResult | ArchitectureAnalysis | RefactoringPlan,
    ):
        self.id = id
        self.timestamp = timestamp
        self.file_path = file_path
        self.result = result


class StorageProvider(ABC):
    """Interface for storing and retrieving analysis results."""

    @abstractmethod
    async def save_analysis(
        self, file_path: str, result: AnalysisResult | ArchitectureAnalysis | RefactoringPlan
    ) -> AnalysisRecord:
        """Save an analysis result.
        
        Args:
            file_path: Path to the analyzed file
            result: Analysis result to save
            
        Returns:
            AnalysisRecord with metadata
        """
        pass

    @abstractmethod
    async def get_analysis(self, id: str) -> Optional[AnalysisRecord]:
        """Get an analysis record by ID.
        
        Args:
            id: ID of the analysis record
            
        Returns:
            AnalysisRecord if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_analyses(
        self,
        file_path: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AnalysisRecord]:
        """List analysis records with optional filters.
        
        Args:
            file_path: Filter by file path
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of matching AnalysisRecord objects
        """
        pass

    @abstractmethod
    async def delete_analysis(self, id: str) -> bool:
        """Delete an analysis record.
        
        Args:
            id: ID of the analysis record
            
        Returns:
            True if deleted, False if not found
        """
        pass
