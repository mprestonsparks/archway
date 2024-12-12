"""
Configuration for {component_name}.

This module contains configuration classes and utilities for {component_name}.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path
import os
import json


@dataclass
class {component_name}Config:
    """Configuration for {component_name}."""
    
    # Required parameters
    name: str
    version: str
    
    # Optional parameters with defaults
    enabled: bool = True
    debug: bool = False
    
    # Complex parameters
    options: Dict[str, Any] = field(default_factory=dict)
    paths: Dict[str, Path] = field(default_factory=dict)
    
    # Environment-based parameters
    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("API_KEY")
    )
    
    def __post_init__(self):
        """Validate and process configuration after initialization."""
        self._validate_config()
        self._process_paths()
    
    def _validate_config(self):
        """Validate configuration values."""
        if not self.name:
            raise ValueError("Name must be specified")
        if not self.version:
            raise ValueError("Version must be specified")
    
    def _process_paths(self):
        """Process and validate paths."""
        processed_paths = {}
        for key, path in self.paths.items():
            if isinstance(path, str):
                processed_paths[key] = Path(path)
            else:
                processed_paths[key] = path
        self.paths = processed_paths
    
    @classmethod
    def from_file(cls, path: str) -> '{component_name}Config':
        """Create configuration from JSON file."""
        with open(path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    def to_file(self, path: str) -> None:
        """Save configuration to JSON file."""
        config_data = {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'debug': self.debug,
            'options': self.options,
            'paths': {k: str(v) for k, v in self.paths.items()},
        }
        with open(path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def merge(self, other: '{component_name}Config') -> None:
        """Merge another configuration into this one."""
        for field in self.__dataclass_fields__:
            other_value = getattr(other, field)
            if other_value is not None:
                setattr(self, field, other_value)
