## Architecture Guidelines

**Purpose:** Provide a blueprint for maintaining a Hexagonal Architecture that the AI can consistently follow.

### Hexagonal Architecture Overview

- **Core (Domain)**: Pure business logic with no external dependencies.
- **Ports (Interfaces)**: Contracts that define how the core interacts with the outside world.
- **Adapters (Implementations)**: Concrete implementations that satisfy ports, integrating external systems (databases, APIs, UIs).

### Directory Structure Example
``` plaintext
project/
  src/
    core/       # Domain logic
    ports/      # Interfaces the domain needs or provides
    adapters/   # External integrations implementing the ports
  tests/
    unit/       # Tests focusing on core logic
    integration/# Tests involving adapters and external systems
  docker/
  scripts/
```

### Naming and Coding Conventions

- Use descriptive, consistent naming.
- Keep domain logic framework-agnostic and free of I/O operations.
- Write docstrings to clarify the purpose of each port and adapter.
- Consult Sourcegraph and the local LLM for code navigation and architectural conformance checks.

### Adding or Modifying Features

- Start with domain logic changes in `core`.
- Define necessary ports in `ports/`.
- Implement adapters in `adapters/` as needed.
- Ensure every new feature is covered by unit and integration tests.

