"""
Style validation rules for code changes.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import ast
import re

@dataclass
class StyleRule:
    """Base class for style rules."""
    name: str
    description: str
    severity: str = "warning"

    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        """Validate an AST node."""
        raise NotImplementedError

class NamingConventionRule(StyleRule):
    """Validates naming conventions."""
    
    def __init__(self):
        super().__init__(
            name="naming_convention",
            description="Validates naming conventions"
        )
        self.patterns = {
            "class": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
            "function": re.compile(r"^[a-z][a-z0-9_]*$"),
            "constant": re.compile(r"^[A-Z][A-Z0-9_]*$"),
            "variable": re.compile(r"^[a-z][a-z0-9_]*$")
        }
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef):
                if not self.patterns["class"].match(n.name):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Class name '{n.name}' does not follow PascalCase convention"
                    })
            
            elif isinstance(n, ast.FunctionDef):
                if not self.patterns["function"].match(n.name):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Function name '{n.name}' does not follow snake_case convention"
                    })
            
            elif isinstance(n, ast.Name):
                if isinstance(n.ctx, ast.Store):
                    if n.id.isupper() and not self.patterns["constant"].match(n.id):
                        issues.append({
                            "line": n.lineno,
                            "message": f"Constant '{n.id}' does not follow UPPER_CASE convention"
                        })
                    elif not n.id.isupper() and not self.patterns["variable"].match(n.id):
                        issues.append({
                            "line": n.lineno,
                            "message": f"Variable '{n.id}' does not follow snake_case convention"
                        })
        
        return issues

class DocstringRule(StyleRule):
    """Validates docstring conventions."""
    
    def __init__(self):
        super().__init__(
            name="docstring",
            description="Validates docstring conventions"
        )
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                docstring = ast.get_docstring(n)
                if not docstring:
                    issues.append({
                        "line": n.lineno,
                        "message": f"Missing docstring for {self._get_node_type(n)} '{getattr(n, 'name', 'module')}'"
                    })
                else:
                    # Check docstring format
                    issues.extend(self._check_docstring_format(docstring, n))
        
        return issues
    
    def _get_node_type(self, node: ast.AST) -> str:
        """Get node type description."""
        if isinstance(node, ast.Module):
            return "module"
        elif isinstance(node, ast.ClassDef):
            return "class"
        elif isinstance(node, ast.FunctionDef):
            return "function"
        return "unknown"
    
    def _check_docstring_format(self, docstring: str, node: ast.AST) -> List[Dict[str, Any]]:
        """Check docstring format."""
        issues = []
        lines = docstring.split("\n")
        
        # Check first line
        if not lines[0].strip():
            issues.append({
                "line": node.lineno,
                "message": "Docstring should start with a summary line"
            })
        
        # Check blank line after summary
        if len(lines) > 1 and lines[1].strip():
            issues.append({
                "line": node.lineno,
                "message": "Docstring should have a blank line after summary"
            })
        
        # Check parameter documentation for functions
        if isinstance(node, ast.FunctionDef) and node.args.args:
            param_docs = [l for l in lines if l.strip().startswith(":param")]
            if len(param_docs) < len(node.args.args) - 1:  # Exclude self
                issues.append({
                    "line": node.lineno,
                    "message": "Missing parameter documentation in docstring"
                })
        
        return issues

class TypeHintRule(StyleRule):
    """Validates type hint usage."""
    
    def __init__(self):
        super().__init__(
            name="type_hints",
            description="Validates type hint usage"
        )
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.FunctionDef):
                # Check parameter type hints
                for arg in n.args.args:
                    if arg.arg != "self" and not arg.annotation:
                        issues.append({
                            "line": arg.lineno,
                            "message": f"Missing type hint for parameter '{arg.arg}'"
                        })
                
                # Check return type hint
                if not n.returns and not self._is_abstract_method(n):
                    issues.append({
                        "line": n.lineno,
                        "message": f"Missing return type hint for function '{n.name}'"
                    })
        
        return issues
    
    def _is_abstract_method(self, node: ast.FunctionDef) -> bool:
        """Check if method is abstract."""
        return any(
            isinstance(d, ast.Name) and d.id == "abstractmethod"
            for d in node.decorator_list
        )
