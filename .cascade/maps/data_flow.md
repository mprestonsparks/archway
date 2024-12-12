# Data Flow Map

## Code Analysis Flow
```mermaid
graph TD
    A[Source Code] --> B[Context Builder]
    B --> C[Analysis Request]
    C --> D{Provider Selection}
    D -->|OpenAI| E[O1ModelProvider]
    D -->|Local| F[LocalLLMProvider]
    
    subgraph Analysis Process
        E --> G[Code Analysis]
        F --> G
        G --> H[Suggestions]
        H --> I[Response Format]
    end
    
    I --> J[Cache]
    I --> K[Output]
```

## Configuration Flow
```mermaid
graph LR
    A[.env File] --> B[Environment Config]
    C[CLI Args] --> B
    B --> D[Provider Config]
    D --> E[Provider Instance]
    
    F[Default Config] -.-> B
```

## Cache Management
```mermaid
graph TD
    A[Analysis Request] --> B{Cache Check}
    B -->|Hit| C[Cached Response]
    B -->|Miss| D[Provider Request]
    D --> E[New Response]
    E --> F[Cache Update]
    F --> G[Response Output]
    C --> G
```

## Key Data Flows
1. Code analysis request processing
2. Configuration management
3. Cache utilization
4. Response handling
5. Error propagation
6. State persistence
