"""
{command_name} command implementation.

This command {command_description}
"""
from dataclasses import dataclass
from typing import List, Optional

from src.cli.base import BaseCommand, CommandConfig, Option, Context, Result
from src.adapters.llm import BaseProvider


@dataclass
class {command_name}Config(CommandConfig):
    """Configuration for {command_name} command."""
    name: str = "{command_lowercase}"
    description: str = "{command_description}"
    options: List[Option] = None

    def __post_init__(self):
        self.options = [
            Option(
                name="--example",
                description="Example option",
                required=False
            ),
        ]


class {command_name}Command(BaseCommand):
    """Implementation of {command_name} command."""
    
    def __init__(self, config: Optional[{command_name}Config] = None):
        """Initialize command with configuration."""
        super().__init__(config or {command_name}Config())
        self._provider: Optional[BaseProvider] = None
    
    async def initialize(self, provider: BaseProvider) -> None:
        """Initialize command with provider."""
        self._provider = provider
        await self._provider.initialize()
    
    async def execute(self, context: Context) -> Result:
        """Execute the command with given context."""
        if not self._provider:
            raise RuntimeError("Provider not initialized")
        
        try:
            # Implement command logic here
            result = await self._provider.some_method()
            return Result(success=True, data=result)
            
        except Exception as e:
            return Result(
                success=False,
                error=f"Error executing {self.config.name}: {str(e)}"
            )
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._provider:
            await self._provider.close()
