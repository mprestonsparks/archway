# Archway

Archway is a fully integrated, AI-driven development environment that combines local and cloud-based LLMs with robust code indexing and semantic navigation capabilities.

## Features

- Sourcegraph integration for code indexing and semantic navigation
- Local LLM layer for rapid code queries and context retrieval
- Cloud LLM layer (OpenAI "o1" model) for deep architectural reasoning
- Dockerized environments for consistent builds
- Hexagonal Architecture pattern
- Automated CI/CD pipeline
- Interactive development support

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Sourcegraph
- Access to OpenAI's "o1" model

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/archway.git
   cd archway
   ```

2. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

## Project Structure

```
archway/
├── src/
│   ├── core/       # Domain logic
│   ├── ports/      # Interfaces
│   └── adapters/   # External integrations
├── tests/
│   ├── unit/
│   └── integration/
├── docker/
└── scripts/
```

## Development

Follow the hexagonal architecture pattern:
1. Implement domain logic in `core/`
2. Define interfaces in `ports/`
3. Create external integrations in `adapters/`

## Testing

Run tests using:
```bash
docker-compose run --rm app pytest
```

## License

[Add appropriate license information]