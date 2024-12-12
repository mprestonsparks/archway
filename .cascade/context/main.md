# Archway Project Context

## Project Overview
Archway is a CLI-based framework designed to enhance development workflows through AI assistance. It integrates with various LLM providers (OpenAI, local models) to provide code analysis, refactoring suggestions, and architectural insights.

## Core Components

### CLI Framework
- Primary interface for user interactions
- Handles command parsing and execution
- Manages configuration and environment setup

### Adapters
- Abstract interfaces for different services
- Provides consistent API across different providers
- Handles provider-specific implementations

### Providers
- OpenAI Provider: Integrates with OpenAI's API (o1 model)
- Local LLM Provider: Manages local model interactions
- Sourcegraph Provider: Handles code search and indexing

## Key Terminology
- **Provider**: Implementation of an AI service interface
- **Adapter**: Abstract interface defining service capabilities
- **Command**: CLI command implementation
- **Context**: Code analysis context and history

## Design Principles
1. **Modularity**: Components are loosely coupled and independently testable
2. **Extensibility**: Easy to add new providers and commands
3. **Consistency**: Uniform interface across different providers
4. **Reliability**: Robust error handling and fallback mechanisms
