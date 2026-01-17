"""
Code Reviewer Agent
Performs enterprise-grade code review with security and pattern compliance checks
"""

import re
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import openai
from openai import AsyncOpenAI

from services.api.config import settings
from services.agents.base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


@dataclass
class ReviewerInput(AgentInput):
    proposed_changes: Dict[str, str] = None
    coding_standards: Dict[str, Any] = None
    security_rules: Dict[str, Any] = None
    test_coverage_requirements: Dict[str, Any] = None


@dataclass
class ReviewerOutput(AgentOutput):
    review_status: str = None
    security_issues: List[Dict[str, Any]] = None
    pattern_violations: List[Dict[str, Any]] = None
    test_coverage_gaps: List[str] = None
    recommendations: List[str] = None
    can_merge: bool = None


class CodeReviewerAgent(BaseAgent):
    """Enterprise-grade code review with security focus"""
    
    def __init__(self):
        super().__init__("reviewer", {})
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        
        # Security patterns
        self.security_patterns = {
            'sql_injection': [
                r'(SELECT|INSERT|UPDATE|DELETE).*\+.*[\'"]',
                r'execute\s*\(\s*["\'].*\+',
                r'query\s*\(\s*["\'].*\+'
            ],
            'xss': [
                r'innerHTML\s*=',
                r'outerHTML\s*=',
                r'document\.write\s*\(',
                r'eval\s*\(\s*["\'].*<.*>'
            ],
            'command_injection': [
                r'eval\s*\(',
                r'exec\s*\(',
                r'shell_exec\s*\(',
                r'system\s*\(',
                r'os\.system\s*\('
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'readFile\s*\(',
                r'fs\.readFileSync\s*\('
            ],
            'hardcoded_secrets': [
                r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                r'API_KEY\s*=\s*["\'][^"\']+["\']',
                r'SECRET\s*=\s*["\'][^"\']+["\']'
            ],
            'insecure_deserialization': [
                r'pickle\.loads',
                r'yaml\.load\s*\(',
                r'json\.loads\s*\(',
                r'marshal\.loads'
            ]
        }
        
        # Pattern compliance checks
        self.pattern_checks = {
            'naming_conventions': self._check_naming_conventions,
            'code_structure': self._check_code_structure,
            'error_handling': self._check_error_handling,
            'documentation': self._check_documentation,
            'testing': self._check_testing_patterns
        }
    
    async def execute(self, input_data: ReviewerInput) -> ReviewerOutput:
        """Perform comprehensive code review"""
        
        try:
            proposed_changes = input_data.proposed_changes or {}
            coding_standards = input_data.coding_standards or {}
            
            # Perform security analysis
            security_issues = await self._analyze_security(proposed_changes)
            
            # Check pattern compliance
            pattern_violations = await self._check_pattern_compliance(
                proposed_changes, coding_standards
            )
            
            # Analyze test coverage
            test_coverage_gaps = await self._analyze_test_coverage(
                proposed_changes, input_data.test_coverage_requirements
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                security_issues, pattern_violations, test_coverage_gaps
            )
            
            # Determine if code can be merged
            can_merge = await self._assess_merge_readiness(
                security_issues, pattern_violations, test_coverage_gaps
            )
            
            return ReviewerOutput(
                status=AgentStatus.COMPLETED,
                files_modified=[],
                files_created=[],
                artifacts_created=["security_review", "pattern_review", "test_analysis"],
                next_actions=["fix_issues", "add_tests", "resubmit"],
                token_usage={"prompt_tokens": 2000, "completion_tokens": 1500, "total": 3500},
                review_status="completed",
                security_issues=security_issues,
                pattern_violations=pattern_violations,
                test_coverage_gaps=test_coverage_gaps,
                recommendations=recommendations,
                can_merge=can_merge
            )
            
        except Exception as e:
            return ReviewerOutput(
                status=AgentStatus.FAILED,
                files_modified=[],
                files_created=[],
                artifacts_created=[],
                next_actions=["retry", "debug"],
                token_usage={},
                error_message=f"Code review failed: {str(e)}"
            )
    
    def validate_input(self, input_data: ReviewerInput) -> bool:
        """Validate code review input"""
        return (
            hasattr(input_data, 'proposed_changes') and 
            isinstance(input_data.proposed_changes, dict) and
            len(input_data.proposed_changes) > 0
        )
    
    def estimate_tokens(self, input_data: ReviewerInput) -> int:
        """Estimate token usage for code review"""
        changes_size = sum(len(content) for content in input_data.proposed_changes.values())
        return (changes_size // 4) + 1500
    
    async def _analyze_security(self, proposed_changes: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze code for security vulnerabilities"""
        
        security_issues = []
        
        for file_path, content in proposed_changes.items():
            file_issues = []
            
            # Check each security pattern
            for vulnerability_type, patterns in self.security_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        file_issues.append({
                            'type': vulnerability_type,
                            'severity': self._get_severity(vulnerability_type),
                            'line_number': content[:match.start()].count('\n') + 1,
                            'code_snippet': content[max(0, match.start()-20):match.end()+20],
                            'description': self._get_security_description(vulnerability_type),
                            'recommendation': self._get_security_recommendation(vulnerability_type)
                        })
            
            if file_issues:
                security_issues.append({
                    'file_path': file_path,
                    'issues': file_issues
                })
        
        return security_issues
    
    async def _check_pattern_compliance(
        self, 
        proposed_changes: Dict[str, str], 
        coding_standards: Dict
    ) -> List[Dict[str, Any]]:
        """Check compliance with coding standards and patterns"""
        
        violations = []
        
        for file_path, content in proposed_changes.items():
            file_violations = []
            
            # Check each pattern type
            for check_name, check_function in self.pattern_checks.items():
                if check_name in coding_standards:
                    violations_list = check_function(content, coding_standards.get(check_name, {}))
                    file_violations.extend(violations_list)
            
            if file_violations:
                violations.append({
                    'file_path': file_path,
                    'violations': file_violations
                })
        
        return violations
    
    async def _analyze_test_coverage(
        self, 
        proposed_changes: Dict[str, str], 
        test_requirements: Dict
    ) -> List[str]:
        """Analyze test coverage gaps"""
        
        gaps = []
        
        # Check if tests are included
        has_tests = any('test' in file_path.lower() for file_path in proposed_changes.keys())
        
        if not has_tests:
            gaps.append("No test files included in changes")
        
        # Check for test coverage requirements
        required_coverage = test_requirements.get('minimum_coverage', 80)
        gaps.append(f"Test coverage should meet minimum {required_coverage}%")
        
        # Check for different test types
        test_types = ['unit', 'integration', 'e2e']
        for test_type in test_types:
            if not any(test_type in file_path.lower() for file_path in proposed_changes.keys()):
                gaps.append(f"Missing {test_type} tests")
        
        return gaps
    
    async def _generate_recommendations(
        self, 
        security_issues: List[Dict], 
        pattern_violations: List[Dict], 
        test_gaps: List[str]
    ) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Security recommendations
        if security_issues:
            recommendations.append("Address all security vulnerabilities before merging")
            recommendations.append("Implement input validation and sanitization")
            recommendations.append("Use parameterized queries instead of string concatenation")
        
        # Pattern compliance recommendations
        if pattern_violations:
            recommendations.append("Fix coding standard violations")
            recommendations.append("Follow established naming conventions")
            recommendations.append("Add proper error handling")
        
        # Testing recommendations
        if test_gaps:
            recommendations.append("Add comprehensive test coverage")
            recommendations.append("Include unit, integration, and E2E tests")
            recommendations.append("Test edge cases and error scenarios")
        
        # General recommendations
        recommendations.extend([
            "Add inline documentation for complex logic",
            "Consider performance implications",
            "Review for potential breaking changes",
            "Ensure backward compatibility"
        ])
        
        return list(set(recommendations))
    
    async def _assess_merge_readiness(
        self, 
        security_issues: List[Dict], 
        pattern_violations: List[Dict], 
        test_gaps: List[str]
    ) -> bool:
        """Assess if code is ready for merge"""
        
        # Count critical issues
        critical_security = sum(
            1 for issue in security_issues 
            for file_issues in issue.get('issues', [])
            for issue in file_issues
            if issue.get('severity') == 'critical'
        )
        
        # Count pattern violations
        total_violations = sum(
            len(violations.get('violations', []))
            for violations in pattern_violations
        )
        
        # Merge criteria
        can_merge = (
            critical_security == 0 and  # No critical security issues
            total_violations < 5 and     # Few pattern violations
            len(test_gaps) < 3        # Minimal test gaps
        )
        
        return can_merge
    
    def _get_severity(self, vulnerability_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            'sql_injection': 'critical',
            'xss': 'critical',
            'command_injection': 'critical',
            'path_traversal': 'high',
            'hardcoded_secrets': 'critical',
            'insecure_deserialization': 'high'
        }
        return severity_map.get(vulnerability_type, 'medium')
    
    def _get_security_description(self, vulnerability_type: str) -> str:
        """Get description for security vulnerability"""
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability through string concatenation',
            'xss': 'Cross-site scripting vulnerability through dynamic HTML content',
            'command_injection': 'Code injection vulnerability through eval/exec functions',
            'path_traversal': 'Path traversal vulnerability through insufficient input validation',
            'hardcoded_secrets': 'Hardcoded credentials or secrets in source code',
            'insecure_deserialization': 'Insecure deserialization of user input'
        }
        return descriptions.get(vulnerability_type, 'Security vulnerability detected')
    
    def _get_security_recommendation(self, vulnerability_type: str) -> str:
        """Get recommendation for security vulnerability"""
        recommendations = {
            'sql_injection': 'Use parameterized queries and input validation',
            'xss': 'Sanitize user input and use proper HTML escaping',
            'command_injection': 'Avoid eval/exec functions with user input',
            'path_traversal': 'Validate and sanitize file paths',
            'hardcoded_secrets': 'Use environment variables or secure credential management',
            'insecure_deserialization': 'Validate serialized data and use safe deserialization'
        }
        return recommendations.get(vulnerability_type, 'Review and fix security issue')
    
    def _check_naming_conventions(self, content: str, standards: Dict) -> List[Dict]:
        """Check naming convention compliance"""
        
        violations = []
        convention = standards.get('style', 'snake_case')
        
        # Parse code based on language
        try:
            tree = ast.parse(content)
            violations.extend(self._check_python_naming(tree, convention))
        except:
            # Fallback for other languages
            violations.extend(self._check_generic_naming(content, convention))
        
        return violations
    
    def _check_python_naming(self, tree: ast.AST, convention: str) -> List[Dict]:
        """Check Python naming conventions"""
        
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name
                if not self._follows_convention(name, 'function', convention):
                    violations.append({
                        'type': 'naming_convention',
                        'name': name,
                        'line': node.lineno,
                        'message': f"Function name '{name}' doesn't follow {convention} convention"
                    })
            
            elif isinstance(node, ast.ClassDef):
                name = node.name
                if not self._follows_convention(name, 'class', convention):
                    violations.append({
                        'type': 'naming_convention',
                        'name': name,
                        'line': node.lineno,
                        'message': f"Class name '{name}' doesn't follow {convention} convention"
                    })
        
        return violations
    
    def _check_generic_naming(self, content: str, convention: str) -> List[Dict]:
        """Check naming conventions in generic code"""
        
        violations = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Simple pattern matching for function/variable names
            matches = re.findall(r'\b(def|class|var|let|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            for match in matches:
                name = match[1]
                if not self._follows_convention(name, 'variable', convention):
                    violations.append({
                        'type': 'naming_convention',
                        'name': name,
                        'line': i,
                        'message': f"Name '{name}' doesn't follow {convention} convention"
                    })
        
        return violations
    
    def _follows_convention(self, name: str, entity_type: str, convention: str) -> bool:
        """Check if name follows convention"""
        
        if convention == 'snake_case':
            return name == name.lower() and '_' in name or name.islower()
        elif convention == 'camelCase':
            return name[0].islower() and '_' not in name
        elif convention == 'PascalCase':
            return name[0].isupper() and '_' not in name
        else:
            return True
    
    def _check_code_structure(self, content: str, standards: Dict) -> List[Dict]:
        """Check code structure compliance"""
        
        violations = []
        
        # Check for proper imports
        if not re.search(r'^import|^from', content, re.MULTILINE):
            violations.append({
                'type': 'code_structure',
                'message': 'Missing import statements at top of file'
            })
        
        # Check for function documentation
        functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', content)
        for func in functions:
            if not re.search(f'def\s+{func}\s*\(\s*.*?\):\s*["\'].*["\']', content):
                violations.append({
                    'type': 'documentation',
                    'name': func,
                    'message': f"Function '{func}' missing docstring"
                })
        
        return violations
    
    def _check_error_handling(self, content: str, standards: Dict) -> List[Dict]:
        """Check error handling compliance"""
        
        violations = []
        
        # Look for bare except clauses
        bare_excepts = re.findall(r'except\s*:\s*$', content, re.MULTILINE)
        for i, match in enumerate(bare_excepts, 1):
            violations.append({
                'type': 'error_handling',
                'line': content[:content.find(match)].count('\n') + 1,
                'message': 'Bare except clause - should specify exception type'
            })
        
        # Check for unhandled operations
        if re.search(r'(open|read|write)\s*\([^)]*\)\s*$', content, re.MULTILINE):
            violations.append({
                'type': 'error_handling',
                'message': 'File operation without error handling'
            })
        
        return violations
    
    def _check_documentation(self, content: str, standards: Dict) -> List[Dict]:
        """Check documentation compliance"""
        
        violations = []
        
        # Check for module docstring
        if not re.search(r'^["\']{3}.*?["\']{3}', content.split('\n')[0] if '\n' in content else content):
            violations.append({
                'type': 'documentation',
                'message': 'Missing module docstring'
            })
        
        # Check for complex functions without documentation
        complex_functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]{20,})\s*:', content)
        for func in complex_functions:
            if not re.search(f'def\s+{func}\s*\([^)]*\)\s*:\s*["\'].*["\']', content):
                violations.append({
                    'type': 'documentation',
                    'name': func,
                    'message': f"Complex function '{func}' missing docstring"
                })
        
        return violations
    
    def _check_testing_patterns(self, content: str, standards: Dict) -> List[Dict]:
        """Check testing pattern compliance"""
        
        violations = []
        
        # Check for test file naming
        if 'test' not in content.lower() and re.search(r'def\s+test_', content):
            violations.append({
                'type': 'testing',
                'message': 'Test function should be in proper test file'
            })
        
        # Check for assertion usage
        if 'assert' not in content and 'test' in content.lower():
            violations.append({
                'type': 'testing',
                'message': 'Test missing assertions'
            })
        
        return violations
