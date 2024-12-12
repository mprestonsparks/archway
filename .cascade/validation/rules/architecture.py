"""
Architecture validation rules for code changes.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Set
import ast
from pathlib import Path

@dataclass
class ArchitectureRule:
    """Base class for architecture rules."""
    name: str
    description: str
    severity: str = "error"

    def validate(self, node: ast.AST, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate an AST node with context."""
        raise NotImplementedError

class DependencyRule(ArchitectureRule):
    """Validates dependency rules."""
    
    def __init__(self):
        super().__init__(
            name="dependencies",
            description="Validates dependency rules"
        )
        self.layer_order = [
            "cli",
            "service",
            "provider",
            "infrastructure"
        ]
        self.allowed_dependencies = {
            "cli": ["service"],
            "service": ["provider", "infrastructure"],
            "provider": ["infrastructure"],
            "infrastructure": []
        }
    
    def validate(self, node: ast.AST, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        current_layer = self._get_layer(context["file_path"])
        
        # Check imports
        for n in ast.walk(node):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                module = n.module if isinstance(n, ast.ImportFrom) else n.names[0].name
                import_layer = self._get_layer(module)
                
                if import_layer and not self._is_allowed_dependency(current_layer, import_layer):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Layer '{current_layer}' cannot depend on '{import_layer}'"
                    })
        
        return issues
    
    def _get_layer(self, path: str) -> str:
        """Get layer from path."""
        path_parts = Path(path).parts
        for layer in self.layer_order:
            if layer in path_parts:
                return layer
        return None
    
    def _is_allowed_dependency(self, from_layer: str, to_layer: str) -> bool:
        """Check if dependency is allowed."""
        return to_layer in self.allowed_dependencies.get(from_layer, [])

class ComponentBoundaryRule(ArchitectureRule):
    """Validates component boundary rules."""
    
    def __init__(self):
        super().__init__(
            name="component_boundaries",
            description="Validates component boundary rules"
        )
        self.private_patterns = [
            re.compile(r"^_[^_].*"),  # Single underscore
            re.compile(r"^__.*")      # Double underscore
        ]
    
    def validate(self, node: ast.AST, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        # Check access to private members
        for n in ast.walk(node):
            if isinstance(n, ast.Attribute):
                if self._is_private_access(n.attr):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Accessing private member '{n.attr}'"
                    })
        
        return issues
    
    def _is_private_access(self, name: str) -> bool:
        """Check if accessing private member."""
        return any(pattern.match(name) for pattern in self.private_patterns)

class AsyncPatternRule(ArchitectureRule):
    """Validates async pattern usage."""
    
    def __init__(self):
        super().__init__(
            name="async_patterns",
            description="Validates async pattern usage"
        )
        self.async_required_methods = {
            "initialize",
            "close",
            "analyze_code",
            "suggest_refactoring",
            "explain_architecture"
        }
    
    def validate(self, node: ast.AST, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                # Check if method should be async
                if n.name in self.async_required_methods and not isinstance(n, ast.AsyncFunctionDef):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Method '{n.name}' should be async"
                    })
                
                # Check async context usage
                if isinstance(n, ast.AsyncFunctionDef):
                    issues.extend(self._check_async_context(n))
        
        return issues
    
    def _check_async_context(self, node: ast.AsyncFunctionDef) -> List[Dict[str, Any]]:
        """Check async context usage."""
        issues = []
        
        # Check for blocking calls
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name) and not self._is_async_safe(n.func.id):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Potentially blocking call to '{n.func.id}'"
                    })
        
        return issues
    
    def _is_async_safe(self, func_name: str) -> bool:
        """Check if function is async-safe."""
        # Add known async-safe functions
        async_safe = {
            "len", "str", "int", "float", "list", "dict", "set",
            "print", "isinstance", "getattr", "setattr"
        }
        return func_name in async_safe

class InterfaceContractRule(ArchitectureRule):
    """Validates interface contracts."""
    
    def __init__(self):
        super().__init__(
            name="interface_contracts",
            description="Validates interface contracts"
        )
    
    def validate(self, node: ast.AST, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef):
                # Check interface implementation
                if any(base.id.startswith("Base") for base in n.bases if isinstance(base, ast.Name)):
                    issues.extend(self._check_interface_implementation(n))
        
        return issues
    
    def _check_interface_implementation(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Check interface implementation."""
        issues = []
        implemented_methods = {m.name for m in node.body if isinstance(m, ast.FunctionDef)}
        
        # Get required methods from base class (would need symbol table in real implementation)
        required_methods = {
            "initialize",
            "close",
            "analyze_code",
            "suggest_refactoring",
            "explain_architecture"
        }
        
        for method in required_methods:
            if method not in implemented_methods:
                issues.append({
                    "line": node.lineno,
                    "message": f"Missing interface method '{method}'"
                })
        
        return issues
