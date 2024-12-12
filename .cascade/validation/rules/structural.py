"""
Structural validation rules for code changes.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import ast
from pathlib import Path

@dataclass
class StructuralRule:
    """Base class for structural rules."""
    name: str
    description: str
    severity: str = "error"  # error, warning, info

    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        """Validate an AST node."""
        raise NotImplementedError

class ImportOrganizationRule(StructuralRule):
    """Validates import organization."""
    
    def __init__(self):
        super().__init__(
            name="import_organization",
            description="Validates import statement organization"
        )
        self.import_groups = [
            "stdlib",
            "third_party",
            "local"
        ]
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        imports = []
        
        # Collect imports
        for n in ast.walk(node):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                imports.append(n)
        
        # Check order
        current_group = None
        for imp in imports:
            group = self._get_import_group(imp)
            if current_group and self._group_order(group) < self._group_order(current_group):
                issues.append({
                    "line": imp.lineno,
                    "message": f"Import from '{group}' should come before '{current_group}'"
                })
            current_group = group
        
        return issues
    
    def _get_import_group(self, node: ast.AST) -> str:
        """Determine import group."""
        if isinstance(node, ast.ImportFrom):
            module = node.module
        else:
            module = node.names[0].name.split(".")[0]
        
        if module in self._get_stdlib_modules():
            return "stdlib"
        elif "." in module:
            return "local"
        else:
            return "third_party"
    
    def _group_order(self, group: str) -> int:
        """Get group order index."""
        return self.import_groups.index(group)
    
    def _get_stdlib_modules(self) -> List[str]:
        """Get list of stdlib modules."""
        import sys
        return sys.stdlib_module_names

class ClassStructureRule(StructuralRule):
    """Validates class structure."""
    
    def __init__(self):
        super().__init__(
            name="class_structure",
            description="Validates class structure and organization"
        )
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef):
                # Check method order
                methods = self._get_methods(n)
                issues.extend(self._check_method_order(methods))
                
                # Check property organization
                issues.extend(self._check_properties(n))
        
        return issues
    
    def _get_methods(self, node: ast.ClassDef) -> List[ast.FunctionDef]:
        """Get class methods in order."""
        return [n for n in node.body if isinstance(n, ast.FunctionDef)]
    
    def _check_method_order(self, methods: List[ast.FunctionDef]) -> List[Dict[str, Any]]:
        """Check method ordering."""
        issues = []
        method_groups = {
            "special": lambda x: x.name.startswith("__"),
            "lifecycle": lambda x: x.name in ["initialize", "cleanup"],
            "public": lambda x: not x.name.startswith("_"),
            "private": lambda x: x.name.startswith("_") and not x.name.startswith("__")
        }
        
        current_group = None
        for method in methods:
            group = next(k for k, v in method_groups.items() if v(method))
            if current_group and self._group_priority(group) < self._group_priority(current_group):
                issues.append({
                    "line": method.lineno,
                    "message": f"Method '{method.name}' ({group}) should come before {current_group} methods"
                })
            current_group = group
        
        return issues
    
    def _group_priority(self, group: str) -> int:
        """Get group priority."""
        priorities = {
            "special": 0,
            "lifecycle": 1,
            "public": 2,
            "private": 3
        }
        return priorities[group]
    
    def _check_properties(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Check property organization."""
        issues = []
        properties = []
        
        for n in node.body:
            if isinstance(n, ast.FunctionDef) and any(
                isinstance(d, ast.Name) and d.id == "property"
                for d in n.decorator_list
            ):
                properties.append(n)
        
        # Properties should be grouped together
        if properties and not self._are_properties_grouped(node.body, properties):
            issues.append({
                "line": properties[0].lineno,
                "message": "Properties should be grouped together"
            })
        
        return issues
    
    def _are_properties_grouped(self, body: List[ast.AST], properties: List[ast.FunctionDef]) -> bool:
        """Check if properties are grouped together."""
        property_indices = [body.index(p) for p in properties]
        return max(property_indices) - min(property_indices) == len(properties) - 1

class FileOrganizationRule(StructuralRule):
    """Validates file organization."""
    
    def __init__(self):
        super().__init__(
            name="file_organization",
            description="Validates file structure and organization"
        )
    
    def validate(self, node: ast.AST) -> List[Dict[str, Any]]:
        issues = []
        
        # Check docstring
        if not ast.get_docstring(node):
            issues.append({
                "line": 1,
                "message": "File missing module docstring"
            })
        
        # Check section ordering
        sections = self._get_sections(node)
        issues.extend(self._check_section_order(sections))
        
        return issues
    
    def _get_sections(self, node: ast.AST) -> Dict[str, List[ast.AST]]:
        """Get file sections."""
        sections = {
            "imports": [],
            "constants": [],
            "classes": [],
            "functions": []
        }
        
        for n in node.body:
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                sections["imports"].append(n)
            elif isinstance(n, ast.Assign) and all(
                isinstance(t, ast.Name) and t.id.isupper()
                for t in n.targets
            ):
                sections["constants"].append(n)
            elif isinstance(n, ast.ClassDef):
                sections["classes"].append(n)
            elif isinstance(n, ast.FunctionDef):
                sections["functions"].append(n)
        
        return sections
    
    def _check_section_order(self, sections: Dict[str, List[ast.AST]]) -> List[Dict[str, Any]]:
        """Check section ordering."""
        issues = []
        expected_order = ["imports", "constants", "classes", "functions"]
        
        last_section = None
        for section in expected_order:
            if sections[section]:
                if last_section:
                    last_node = sections[last_section][-1]
                    current_node = sections[section][0]
                    if current_node.lineno < last_node.lineno:
                        issues.append({
                            "line": current_node.lineno,
                            "message": f"{section} should come after {last_section}"
                        })
                last_section = section
        
        return issues
