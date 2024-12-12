# Command Flow Map

## CLI Command Flow
```mermaid
graph TD
    A[CLI Input] --> B[Command Parser]
    B --> C[Command Handler]
    C --> D{Provider Type}
    D -->|OpenAI| E[O1ModelProvider]
    D -->|Local| F[LocalLLMProvider]
    D -->|Code Search| G[SourcegraphProvider]
    E --> H[Response Handler]
    F --> H
    G --> H
    H --> I[Formatted Output]

    subgraph Error Handling
        C -.->|Error| J[Error Handler]
        E -.->|Error| J
        F -.->|Error| J
        G -.->|Error| J
        J -.-> I
    end
```

## State Management Flow
```mermaid
graph LR
    A[Command Context] --> B[Provider State]
    B --> C[Response Cache]
    C --> D[Output State]
    
    E[Environment Config] --> F[Provider Config]
    F --> B
```

## Key Interactions
1. Command Parser validates and routes commands
2. Command Handler manages execution flow
3. Provider selection based on command and config
4. Response handling and formatting
5. Error propagation and handling
6. State management and caching
