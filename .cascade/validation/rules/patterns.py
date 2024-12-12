"""
Pattern validation rules for code changes.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import ast
import re

@dataclass
class PatternRule:
    """Base class for pattern rules."""
    name: str
    description: str
    severity: str = "error"

    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        """Validate an AST node."""
        raise NotImplementedError

class CommandPatternRule(PatternRule):
    """Validates command pattern implementation."""
    
    def __init__(self):
        super().__init__(
            name="command_pattern",
            description="Validates command pattern implementation"
        )
        self.required_methods = {
            "initialize": ["provider"],
            "execute": ["context"],
            "cleanup": []
        }
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef) and n.name.endswith("Command"):
                # Check base class
                if not any(base.id == "BaseCommand" for base in n.bases if isinstance(base, ast.Name)):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Command class '{n.name}' must inherit from BaseCommand"
                    })
                
                # Check required methods
                methods = {m.name: m for m in n.body if isinstance(m, ast.FunctionDef)}
                for method, params in self.required_methods.items():
                    if method not in methods:
                        issues.append({
                            "line": n.lineno,
                            "message": f"Command class '{n.name}' missing required method '{method}'"
                        })
                    else:
                        # Check method parameters
                        method_node = methods[method]
                        method_params = [a.arg for a in method_node.args.args if a.arg != "self"]
                        for param in params:
                            if param not in method_params:
                                issues.append({
                                    "line": method_node.lineno,
                                    "message": f"Method '{method}' missing required parameter '{param}'"
                                })
                
                # Check configuration
                if not any(isinstance(n, ast.ClassDef) and n.name.endswith("Config") for n in ast.walk(node)):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Command '{n.name}' missing configuration class"
                    })
        
        return issues

class ProviderPatternRule(PatternRule):
    """Validates provider pattern implementation."""
    
    def __init__(self):
        super().__init__(
            name="provider_pattern",
            description="Validates provider pattern implementation"
        )
        self.required_methods = {
            "initialize": [],
            "close": [],
            "analyze_code": ["context"],
            "suggest_refactoring": ["context"],
            "explain_architecture": ["context"]
        }
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef) and n.name.endswith("Provider"):
                # Check base class
                if not any(base.id == "BaseProvider" for base in n.bases if isinstance(base, ast.Name)):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Provider class '{n.name}' must inherit from BaseProvider"
                    })
                
                # Check required methods
                methods = {m.name: m for m in n.body if isinstance(m, ast.FunctionDef)}
                for method, params in self.required_methods.items():
                    if method not in methods:
                        issues.append({
                            "line": n.lineno,
                            "message": f"Provider class '{n.name}' missing required method '{method}'"
                        })
                    else:
                        # Check method parameters
                        method_node = methods[method]
                        method_params = [a.arg for a in method_node.args.args if a.arg != "self"]
                        for param in params:
                            if param not in method_params:
                                issues.append({
                                    "line": method_node.lineno,
                                    "message": f"Method '{method}' missing required parameter '{param}'"
                                })
                
                # Check async implementation
                for method in methods.values():
                    if not any(isinstance(d, ast.Name) and d.id == "abstractmethod" for d in method.decorator_list):
                        if not self._is_async_method(method):
                            issues.append({
                                "line": method.lineno,
                                "message": f"Method '{method.name}' should be async"
                            })
        
        return issues
    
    def _is_async_method(self, node: ast.FunctionDef) -> bool:
        """Check if method is async."""
        return isinstance(node, ast.AsyncFunctionDef)

class ErrorHandlingPatternRule(PatternRule):
    """Validates error handling pattern implementation."""
    
    def __init__(self):
        super().__init__(
            name="error_handling",
            description="Validates error handling patterns"
        )
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                # Check try-except blocks
                try_blocks = [b for b in ast.walk(n) if isinstance(b, ast.Try)]
                if not try_blocks and self._needs_error_handling(n):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Method '{n.name}' should include error handling"
                    })
                
                # Check exception types
                for block in try_blocks:
                    for handler in block.handlers:
                        if handler.type is None or (
                            isinstance(handler.type, ast.Name) and handler.type.id == "Exception"
                        ):
                            issues.append({
                                "line": handler.lineno,
                                "message": "Avoid catching generic Exception"
                            })
        
        return issues
    
    def _needs_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if method needs error handling."""
        # Methods that interact with external systems or do complex operations
        return any(
            isinstance(n, (ast.Call, ast.Attribute))
            for n in ast.walk(node)
        )
