"""
Code change validator implementation.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import ast
from pathlib import Path

from .rules.structural import (
    StructuralRule,
    ImportOrganizationRule,
    ClassStructureRule,
    FileOrganizationRule
)
from .rules.patterns import (
    PatternRule,
    CommandPatternRule,
    ProviderPatternRule,
    ErrorHandlingPatternRule
)
from .rules.style import (
    StyleRule,
    NamingConventionRule,
    DocstringRule,
    TypeHintRule
)
from .rules.architecture import (
    ArchitectureRule,
    DependencyRule,
    ComponentBoundaryRule,
    AsyncPatternRule,
    InterfaceContractRule
)

@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

class CodeValidator:
    """Validates code changes against defined rules."""
    
    def __init__(self, rules: Optional[List[str]] = None):
        """Initialize validator with rules."""
        self.rules = rules or ["structure", "patterns", "style", "architecture"]
        self._load_rules()
    
    def _load_rules(self):
        """Load validation rules."""
        self.structural_rules: List[StructuralRule] = [
            ImportOrganizationRule(),
            ClassStructureRule(),
            FileOrganizationRule()
        ]
        
        self.pattern_rules: List[PatternRule] = [
            CommandPatternRule(),
            ProviderPatternRule(),
            ErrorHandlingPatternRule()
        ]
        
        self.style_rules: List[StyleRule] = [
            NamingConventionRule(),
            DocstringRule(),
            TypeHintRule()
        ]
        
        self.architecture_rules: List[ArchitectureRule] = [
            DependencyRule(),
            ComponentBoundaryRule(),
            AsyncPatternRule(),
            InterfaceContractRule()
        ]
    
    async def validate(
        self,
        original_code: str,
        new_code: str,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate code changes."""
        issues = []
        
        # Parse code
        try:
            original_ast = ast.parse(original_code)
            new_ast = ast.parse(new_code)
        except SyntaxError as e:
            return ValidationResult(
                valid=False,
                errors=[{"message": f"Syntax error: {str(e)}"}],
                warnings=[]
            )
        
        # Apply rules
        if "structure" in self.rules:
            for rule in self.structural_rules:
                issues.extend(rule.validate(new_ast))
        
        if "patterns" in self.rules:
            for rule in self.pattern_rules:
                issues.extend(rule.validate(new_ast))
        
        if "style" in self.rules:
            for rule in self.style_rules:
                issues.extend(rule.validate(new_ast))
        
        if "architecture" in self.rules:
            for rule in self.architecture_rules:
                issues.extend(rule.validate(new_ast, context))
        
        # Separate errors and warnings
        errors = [i for i in issues if i.get("severity", "error") == "error"]
        warnings = [i for i in issues if i.get("severity", "error") == "warning"]
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _get_changed_nodes(
        self,
        original_ast: ast.AST,
        new_ast: ast.AST
    ) -> List[ast.AST]:
        """Get changed nodes between ASTs."""
        # This would implement AST comparison logic
        # For now, validate entire new AST
        return [new_ast]
