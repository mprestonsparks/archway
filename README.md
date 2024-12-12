# Archway

Archway is a development environment that combines local and cloud LLMs to help you write, understand, and maintain code. It runs Code Llama locally for quick code suggestions and uses OpenAI's o1 model for deeper analysis like refactoring and architectural decisions.

## Core Components

- **Local Code Understanding**: Uses Code Llama for rapid code queries and context retrieval
- **Architectural Analysis**: Employs OpenAI's o1 model for deep architectural reasoning and complex refactoring
- **Code Navigation**: Uses Sourcegraph for code indexing and semantic navigation
- **Docker-First**: Operates entirely within containerized environments for consistent and reproducible builds

## How It Works

1. **Local Analysis**: Code Llama runs locally to handle:
   - Rapid code queries
   - Context retrieval
   - Basic code understanding
   - Quick suggestions

2. **Deep Analysis**: The o1 model handles complex tasks:
   - Multi-file refactoring
   - Architecture optimization
   - Design pattern suggestions
   - Technical debt analysis

3. **Code Navigation**: Sourcegraph integration enables:
   - Semantic code search
   - Jump-to-definition
   - Find references
   - Cross-repository understanding

## Development & Integration

Archway provides a foundation for AI-assisted development:

- **Core Capabilities**
  - Real-time code assistance via Local Analysis
  - Complex code understanding through Deep Analysis
  - Code navigation and indexing
  - State and context management for AI agents

- **Integration with Windsurf**
  - Powers Windsurf's code analysis and generation
  - Provides semantic navigation features
  - Enables autonomous development workflows
  - Maintains development context across sessions

All features are exposed through well-defined interfaces, allowing integration with both Windsurf and other potential clients. The ultimate goal is for Archway to power its own development, creating a fully autonomous development cycle.

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
