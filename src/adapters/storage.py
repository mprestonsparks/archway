"""SQLite-based storage adapter."""
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import aiosqlite

from ..core.models import (
    AnalysisResult,
    ArchitectureAnalysis,
    RefactoringPlan,
)
from ..ports.storage import AnalysisRecord, StorageProvider


class SQLiteConfig:
    """Configuration for SQLite storage."""

    def __init__(self, db_path: str = ".archway/analyses.db"):
        self.db_path = db_path


class SQLiteStorage(StorageProvider):
    """SQLite-based storage provider."""

    def __init__(self, config: SQLiteConfig):
        self.config = config
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure the database and tables exist."""
        db_dir = Path(self.config.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.config.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    result_type TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_file_path
                ON analyses(file_path)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_timestamp
                ON analyses(timestamp)
            """)

    def _serialize_result(
        self, result: AnalysisResult | ArchitectureAnalysis | RefactoringPlan
    ) -> tuple[str, str]:
        """Serialize an analysis result to JSON.
        
        Args:
            result: Result to serialize
            
        Returns:
            Tuple of (result_type, result_json)
        """
        result_type = result.__class__.__name__
        result_dict = {
            k: v for k, v in result.__dict__.items()
            if not k.startswith('_')
        }
        return result_type, json.dumps(result_dict)

    def _deserialize_result(self, result_type: str, result_json: str) -> AnalysisResult | ArchitectureAnalysis | RefactoringPlan:
        """Deserialize a result from JSON.
        
        Args:
            result_type: Type of the result
            result_json: JSON string of the result
            
        Returns:
            Deserialized result object
        """
        result_dict = json.loads(result_json)
        result_class = {
            'AnalysisResult': AnalysisResult,
            'ArchitectureAnalysis': ArchitectureAnalysis,
            'RefactoringPlan': RefactoringPlan,
        }[result_type]
        return result_class(**result_dict)

    async def save_analysis(
        self,
        file_path: str,
        result: AnalysisResult | ArchitectureAnalysis | RefactoringPlan,
    ) -> AnalysisRecord:
        """Save an analysis result.
        
        Args:
            file_path: Path to the analyzed file
            result: Analysis result to save
            
        Returns:
            AnalysisRecord with metadata
        """
        id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        result_type, result_json = self._serialize_result(result)

        async with aiosqlite.connect(self.config.db_path) as db:
            await db.execute(
                """
                INSERT INTO analyses (id, timestamp, file_path, result_type, result_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id, timestamp.isoformat(), file_path, result_type, result_json)
            )
            await db.commit()

        return AnalysisRecord(id, timestamp, file_path, result)

    async def get_analysis(self, id: str) -> Optional[AnalysisRecord]:
        """Get an analysis record by ID.
        
        Args:
            id: ID of the analysis record
            
        Returns:
            AnalysisRecord if found, None otherwise
        """
        async with aiosqlite.connect(self.config.db_path) as db:
            async with db.execute(
                "SELECT timestamp, file_path, result_type, result_json FROM analyses WHERE id = ?",
                (id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                timestamp = datetime.fromisoformat(row[0])
                file_path = row[1]
                result = self._deserialize_result(row[2], row[3])
                return AnalysisRecord(id, timestamp, file_path, result)

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
        query = ["SELECT id, timestamp, file_path, result_type, result_json FROM analyses"]
        params = []
        where_clauses = []

        if file_path:
            where_clauses.append("file_path = ?")
            params.append(file_path)
        if start_date:
            where_clauses.append("timestamp >= ?")
            params.append(start_date.isoformat())
        if end_date:
            where_clauses.append("timestamp <= ?")
            params.append(end_date.isoformat())

        if where_clauses:
            query.append("WHERE " + " AND ".join(where_clauses))

        query.append("ORDER BY timestamp DESC")

        async with aiosqlite.connect(self.config.db_path) as db:
            async with db.execute(" ".join(query), params) as cursor:
                records = []
                async for row in cursor:
                    id = row[0]
                    timestamp = datetime.fromisoformat(row[1])
                    file_path = row[2]
                    result = self._deserialize_result(row[3], row[4])
                    records.append(AnalysisRecord(id, timestamp, file_path, result))
                return records

    async def delete_analysis(self, id: str) -> bool:
        """Delete an analysis record.
        
        Args:
            id: ID of the analysis record
            
        Returns:
            True if deleted, False if not found
        """
        async with aiosqlite.connect(self.config.db_path) as db:
            cursor = await db.execute("DELETE FROM analyses WHERE id = ?", (id,))
            await db.commit()
            return cursor.rowcount > 0
