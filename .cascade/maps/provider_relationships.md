# Provider Relationships Map

## Provider Hierarchy
```mermaid
classDiagram
    class BaseProvider {
        <<abstract>>
        +initialize()
        +close()
        +analyze_code()
        +suggest_refactoring()
        +explain_architecture()
    }
    
    class O1ModelProvider {
        -api_key: str
        -model: str
        +initialize()
        +analyze_code()
        +suggest_refactoring()
        +explain_architecture()
    }
    
    class LocalLLMProvider {
        -model_path: str
        -config: dict
        +initialize()
        +analyze_code()
        +suggest_refactoring()
        +explain_architecture()
    }
    
    class SourcegraphProvider {
        -endpoint: str
        -token: str
        +initialize()
        +search_code()
        +analyze_dependencies()
    }
    
    BaseProvider <|-- O1ModelProvider
    BaseProvider <|-- LocalLLMProvider
    BaseProvider <|-- SourcegraphProvider
```

## Provider Dependencies
```mermaid
graph TD
    A[CLI Commands] --> B[Provider Factory]
    B --> C{Provider Type}
    C -->|OpenAI| D[O1ModelProvider]
    C -->|Local| E[LocalLLMProvider]
    C -->|Search| F[SourcegraphProvider]
    
    D --> G[OpenAI API]
    E --> H[Local Model]
    F --> I[Sourcegraph API]
    
    J[Environment Config] --> D
    J --> E
    J --> F
```

## Key Relationships
1. All providers inherit from BaseProvider
2. Provider Factory manages instantiation
3. Environment config influences all providers
4. Each provider has unique dependencies
5. Providers can be used independently
6. Cross-provider functionality supported
