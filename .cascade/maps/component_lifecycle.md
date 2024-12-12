# Component Lifecycle Map

## Provider Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Uninitialized
    Uninitialized --> Initializing: initialize()
    Initializing --> Ready: initialization complete
    Initializing --> Error: initialization failed
    Ready --> Processing: request received
    Processing --> Ready: request complete
    Processing --> Error: request failed
    Ready --> Closing: close()
    Closing --> [*]
    Error --> Closing: close()
```

## Command Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Parsing
    Parsing --> Validating: parse complete
    Validating --> Executing: validation passed
    Validating --> Failed: validation failed
    Executing --> Processing: provider call
    Processing --> Formatting: provider response
    Formatting --> Complete: output ready
    Processing --> Failed: provider error
    Failed --> [*]
    Complete --> [*]
```

## Cache Entry Lifecycle
```mermaid
stateDiagram-v2
    [*] --> Empty
    Empty --> Pending: request started
    Pending --> Valid: response cached
    Pending --> Invalid: request failed
    Valid --> Stale: TTL expired
    Stale --> Pending: refresh
    Invalid --> Pending: retry
    Valid --> [*]: clear cache
    Stale --> [*]: clear cache
    Invalid --> [*]: clear cache
```

## Key Lifecycle Events
1. Provider initialization and shutdown
2. Command execution flow
3. Cache entry management
4. Error handling states
5. Resource cleanup
6. State transitions
