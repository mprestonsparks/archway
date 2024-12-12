# Code Patterns

## Command Implementation Pattern
```python
@dataclass
class CommandConfig:
    name: str
    description: str
    options: List[Option]

class BaseCommand:
    def __init__(self, config: CommandConfig):
        self.config = config

    async def execute(self, context: Context) -> Result:
        # Implementation
        pass
```

## Provider Implementation Pattern
```python
class BaseProvider(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def analyze_code(self, context: CodeContext) -> AnalysisResult:
        pass
```

## Error Handling Pattern
```python
class ArchWayError(Exception):
    """Base exception for all Archway errors"""
    pass

class ProviderError(ArchWayError):
    """Provider-specific errors"""
    pass

def handle_provider_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            raise ProviderError(f"Provider error: {str(e)}") from e
    return wrapper
```

## Configuration Pattern
```python
@dataclass
class ProviderConfig:
    api_key: Optional[str] = None
    model: str = "default"
    max_tokens: int = 1000
    temperature: float = 0.7

def load_config(config_path: str) -> ProviderConfig:
    # Implementation
    pass
```
