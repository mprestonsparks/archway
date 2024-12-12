# Code Templates

This directory contains templates for common code patterns in the Archway project.

## Templates

### Commands
- `command_template.py`: Base template for CLI commands
  - Includes command configuration
  - Standard lifecycle methods
  - Error handling patterns
  - Provider integration

### Providers
- `provider_template.py`: Base template for providers
  - Provider configuration
  - Initialization and cleanup
  - Standard provider methods
  - Error handling

### Tests
- `test_command_template.py`: Template for command tests
  - Command initialization tests
  - Execution tests
  - Error handling tests
  - Configuration tests

- `test_provider_template.py`: Template for provider tests
  - Provider initialization tests
  - Method tests
  - Error handling tests
  - Configuration tests

### Configuration
- `config_template.py`: Template for configuration classes
  - Environment variable integration
  - File-based configuration
  - Configuration validation
  - Configuration merging

## Usage

When creating new components:
1. Copy the appropriate template
2. Replace placeholder values:
   - `{command_name}` -> Your command name
   - `{command_description}` -> Command description
   - `{provider_name}` -> Provider name
   - `{provider_description}` -> Provider description
   - `{component_name}` -> Component name
3. Implement required methods
4. Add tests following the test template

## Best Practices
1. Always include docstrings
2. Implement all lifecycle methods
3. Add proper error handling
4. Include configuration validation
5. Write comprehensive tests
