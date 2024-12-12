"""Shared test fixtures and configuration."""
import pytest

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("SOURCEGRAPH_TOKEN", "test-token")
