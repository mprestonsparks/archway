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

## CLI Commands

Archway provides a powerful command-line interface for code analysis, search, and history management:

### Code Analysis

```bash
# Analyze a single file
archway analyze code <file_path>

# Get refactoring suggestions
archway analyze refactor <file_path> "<goal>"

# Analyze architecture of multiple files
archway analyze architecture <file_path1> <file_path2> ...
```

### Code Search

```bash
# Search for code using Sourcegraph
archway search search-code "<query>"

# Find symbol definition
archway search definition <file_path> <line> <character>

# Find symbol references
archway search references <file_path> <line> <character>
```

### Analysis History

```bash
# List all analyses
archway history list

# List analyses for a specific file
archway history list --file-path <file_path>

# List analyses since a specific date
archway history list --since YYYY-MM-DD

# Show details of a specific analysis
archway history show <analysis-id>

# Delete an analysis from history
archway history delete <analysis-id>
```

### Environment Variables

The following environment variables must be set:

- `OPENAI_API_KEY`: Your OpenAI API key
- `SOURCEGRAPH_ENDPOINT`: Your Sourcegraph instance URL
- `SOURCEGRAPH_TOKEN`: Your Sourcegraph access token

You can set these in a `.env` file in the project root.

## License

This project is the private property of [Preston Sparks](https://github.com/mprestonsparks). All rights reserved.
`
