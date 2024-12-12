# Code Change Validation Framework

This framework validates AI-suggested code changes before implementation to ensure consistency and quality.

## Validation Categories

1. **Structural Validation**
   - File organization
   - Class/function structure
   - Import organization
   - Naming conventions

2. **Pattern Compliance**
   - Command pattern adherence
   - Provider interface compliance
   - Error handling patterns
   - Configuration patterns

3. **Style Validation**
   - PEP 8 compliance
   - Project-specific style rules
   - Documentation requirements
   - Type hints

4. **Architectural Validation**
   - Component boundaries
   - Dependency rules
   - Interface contracts
   - Async pattern usage

## Usage

```python
from validation import CodeValidator

# Create validator with rules
validator = CodeValidator(
    rules=['structure', 'patterns', 'style', 'architecture']
)

# Validate code changes
result = await validator.validate(
    original_code="...",
    new_code="...",
    context={
        'file_path': '...',
        'component_type': '...',
        'change_type': '...'
    }
)

if result.valid:
    print("Changes are valid!")
else:
    print("Validation failed:", result.errors)
```

## Rule Sets

Each validation category has its own rule set defined in:
- `rules/structural.py`
- `rules/patterns.py`
- `rules/style.py`
- `rules/architecture.py`
