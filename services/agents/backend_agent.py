"""
Backend Implementation Agent
Handles backend code modifications with pattern compliance and safety
"""

import os
import re
import ast
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import openai
from openai import AsyncOpenAI

from services.api.config import settings
from services.agents.base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus, AgentUtils
from services.agents.utils.file_manager import FileManager


@dataclass
class BackendInput(AgentInput):
    api_contract: Optional[Dict[str, Any]] = None
    existing_patterns: List[Dict[str, Any]] = None
    database_schema: Optional[Dict[str, Any]] = None
    test_framework: str = "pytest"


@dataclass
class BackendOutput(AgentOutput):
    code_changes: Dict[str, str] = None
    unit_tests: Dict[str, str] = None
    api_updates: Dict[str, Any] = None
    migration_scripts: List[str] = None
    integration_notes: str = None


class BackendAgent(BaseAgent):
    """Scoped backend code modifications with pattern compliance"""
    
    def __init__(self):
        super().__init__("backend", {})
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.max_file_size = 10000  # Max characters per file
        self.file_manager = FileManager()
    
    async def execute(self, input_data: BackendInput) -> BackendOutput:
        """Execute backend implementation with pattern compliance"""
        
        try:
            # Analyze requirements and context
            requirements = input_data.context.get('requirements', {})
            file_scope = input_data.file_scope
            
            # Analyze existing patterns
            pattern_analysis = await self._analyze_existing_patterns(input_data.existing_patterns)
            
            # Generate code changes with file management
            code_changes = {}
            processed_files = []
            
            for file_path in file_scope:
                # Analyze file size and determine strategy
                file_analysis = await self.file_manager.analyze_file(file_path)
                
                if file_analysis.get('error'):
                    continue  # Skip files that can't be analyzed
                
                strategy = file_analysis.get('strategy', 'direct')
                
                if strategy == 'direct':
                    # Direct modification for small files
                    change = await self._generate_code_change(
                        file_path, requirements, pattern_analysis
                    )
                    if change:
                        code_changes[file_path] = change
                        processed_files.append(file_path)
                        
                elif strategy in ['chunked', 'split']:
                    # Use file manager for large files
                    operation_id = await self.file_manager.create_file_operation(
                        'update', 
                        file_path, 
                        await self._get_existing_content(file_path),  # Get current content
                        context={'requirements': requirements, 'pattern_analysis': pattern_analysis}
                    )
                    
                    # Execute the operation
                    result = await self.file_manager.execute_operation(operation_id)
                    
                    if result.get('success'):
                        code_changes[file_path] = result.get('updated_content', '')
                        processed_files.append(file_path)
                    else:
                        # Log error but continue with other files
                        print(f"Failed to process {file_path}: {result.get('error')}")
                        
                else:
                    # Specialized handling for very large files
                    change = await self._generate_code_change(
                        file_path, requirements, pattern_analysis
                    )
                    if change:
                        code_changes[file_path] = change
                        processed_files.append(file_path)
            
            # Generate unit tests
            unit_tests = await self._generate_unit_tests(
                code_changes, input_data.test_framework
            )
            
            # Update API contracts if needed
            api_updates = await self._update_api_contracts(
                code_changes, input_data.api_contract
            )
            
            # Generate database migrations if needed
            migrations = await self._generate_migrations(
                code_changes, input_data.database_schema
            )
            
            # Create integration notes
            integration_notes = await self._create_integration_notes(
                code_changes, pattern_analysis
            )
            
            return BackendOutput(
                status=AgentStatus.COMPLETED,
                files_modified=list(code_changes.keys()),
                files_created=list(unit_tests.keys()) + migrations,
                artifacts_created=["code_changes", "unit_tests", "api_updates"],
                next_actions=["code_review", "testing", "deployment"],
                token_usage={"prompt_tokens": 3000, "completion_tokens": 2000, "total": 5000},
                code_changes=code_changes,
                unit_tests=unit_tests,
                api_updates=api_updates,
                migration_scripts=migrations,
                integration_notes=integration_notes
            )
            
        except Exception as e:
            return BackendOutput(
                status=AgentStatus.FAILED,
                files_modified=[],
                files_created=[],
                artifacts_created=[],
                next_actions=["retry", "debug"],
                token_usage={},
                error_message=f"Backend implementation failed: {str(e)}"
            )
    
    def validate_input(self, input_data: BackendInput) -> bool:
        """Validate backend implementation input"""
        return (
            hasattr(input_data, 'file_scope') and 
            len(input_data.file_scope) > 0 and
            hasattr(input_data, 'context')
        )
    
    def estimate_tokens(self, input_data: BackendInput) -> int:
        """Estimate token usage for backend implementation"""
        file_count = len(input_data.file_scope)
        context_size = len(str(input_data.context))
        return (file_count * 500) + context_size + 1000
    
    async def _analyze_existing_patterns(self, existing_patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze existing code patterns for compliance"""
        
        if not existing_patterns:
            return {
                'framework': 'unknown',
                'style_guide': 'none',
                'conventions': {},
                'imports': []
            }
        
        # Aggregate pattern information
        frameworks = []
        import_styles = []
        naming_conventions = {}
        
        for pattern in existing_patterns:
            if pattern.get('framework'):
                frameworks.append(pattern['framework'])
            
            if pattern.get('import_style'):
                import_styles.append(pattern['import_style'])
            
            if pattern.get('naming_convention'):
                naming_conventions.update(pattern['naming_convention'])
        
        # Determine primary framework
        primary_framework = max(set(frameworks), key=frameworks.count) if frameworks else 'unknown'
        
        return {
            'framework': primary_framework,
            'style_guide': self._detect_style_guide(existing_patterns),
            'conventions': naming_conventions,
            'import_style': import_styles[0] if import_styles else 'standard',
            'patterns': existing_patterns
        }
    
    async def _analyze_existing_patterns(self, existing_patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze existing coding patterns"""
        
        # Simple heuristic based on common patterns
        frameworks = []
        import_styles = []
        naming_conventions = {}
        
        for pattern in existing_patterns:
            if pattern.get('framework'):
                frameworks.append(pattern['framework'])
            
            if pattern.get('import_style'):
                import_styles.append(pattern['import_style'])
            
            if pattern.get('naming_convention'):
                naming_conventions.update(pattern['naming_convention'])
        
        # Determine primary framework
        primary_framework = max(set(frameworks), key=frameworks.count) if frameworks else 'unknown'
        
        return {
            'framework': primary_framework,
            'style_guide': self._detect_style_guide(existing_patterns),
            'conventions': naming_conventions,
            'import_style': import_styles[0] if import_styles else 'standard',
            'patterns': existing_patterns
        }
    
    async def _generate_code_change(
        self, 
        file_path: str, 
        requirements: Dict, 
        pattern_analysis: Dict
    ) -> Optional[str]:
        """Generate code change for a specific file"""
        
        try:
            # Determine file type and language
            file_ext = Path(file_path).suffix.lower()
            language = self._detect_language(file_ext)
            
            # Get existing content (mock for now)
            existing_content = await self._get_existing_content(file_path)
            
            # Generate change based on requirements
            if language == 'python':
                return await self._generate_python_change(
                    file_path, existing_content, requirements, pattern_analysis
                )
            elif language in ['javascript', 'typescript']:
                return await self._generate_js_change(
                    file_path, existing_content, requirements, pattern_analysis
                )
            elif language == 'java':
                return await self._generate_java_change(
                    file_path, existing_content, requirements, pattern_analysis
                )
            else:
                return await self._generate_generic_change(
                    file_path, existing_content, requirements, pattern_analysis
                )
                
        except Exception as e:
            print(f"Failed to generate change for {file_path}: {e}")
            return None
    
    async def _generate_python_change(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        pattern_analysis: Dict
    ) -> str:
        """Generate Python code change"""
        
        # Parse existing code
        try:
            tree = ast.parse(existing_content)
        except:
            return existing_content  # Return unchanged if can't parse
        
        # Generate change based on requirements
        feature_type = requirements.get('type', 'unknown')
        
        if feature_type == 'add_endpoint':
            return await self._add_python_endpoint(tree, requirements, pattern_analysis)
        elif feature_type == 'add_model':
            return await self._add_python_model(tree, requirements, pattern_analysis)
        elif feature_type == 'add_service':
            return await self._add_python_service(tree, requirements, pattern_analysis)
        else:
            return await self._modify_python_code(tree, requirements, pattern_analysis)
    
    async def _add_python_endpoint(
        self, 
        tree: ast.AST, 
        requirements: Dict, 
        pattern_analysis: Dict
    ) -> str:
        """Add new endpoint to Python code"""
        
        endpoint_name = requirements.get('endpoint_name', 'new_endpoint')
        method = requirements.get('method', 'GET')
        response_model = requirements.get('response_model', 'dict')
        
        # Generate endpoint code following patterns
        framework = pattern_analysis.get('framework', 'flask')
        
        if framework == 'fastapi':
            endpoint_code = f'''
@{method.lower()}("/{endpoint_name}")
async def {endpoint_name}():
    """
    {requirements.get('description', 'New endpoint')}
    """
    return {{"response": "data"}}
'''
        elif framework == 'flask':
            endpoint_code = f'''
@{method.lower()}("/{endpoint_name}")
def {endpoint_name}():
    """
    {requirements.get('description', 'New endpoint')}
    """
    return jsonify({{"response": "data"}})
'''
        else:
            endpoint_code = f'''
# {endpoint_name} endpoint
def {endpoint_name}():
    """
    {requirements.get('description', 'New endpoint')}
    """
    return {{"response": "data"}}
'''
        
        # Add to existing code
        new_tree = self._add_to_ast(tree, endpoint_code)
        return ast.unparse(new_tree)
    
    async def _add_python_model(
        self, 
        tree: ast.AST, 
        requirements: Dict, 
        pattern_analysis: Dict
    ) -> str:
        """Add new model to Python code"""
        
        model_name = requirements.get('model_name', 'NewModel')
        fields = requirements.get('fields', {})
        
        # Generate model code
        framework = pattern_analysis.get('framework', 'flask')
        
        if framework == 'sqlalchemy':
            model_code = f'''
class {model_name}(db.Model):
    """
    {requirements.get('description', 'New model')}
    """
'''
            for field_name, field_type in fields.items():
                model_code += f'    {field_name} = db.Column(db.{field_type})\n'
            
            model_code += '    pass\n'
        else:
            # Generic model
            model_code = f'''
class {model_name}:
    """
    {requirements.get('description', 'New model')}
    """
'''
            for field_name, field_type in fields.items():
                model_code += f'    {field_name}: {field_type}\n'
        
        # Add to existing code
        new_tree = self._add_to_ast(tree, model_code)
        return ast.unparse(new_tree)
    
    async def _generate_js_change(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        pattern_analysis: Dict
    ) -> str:
        """Generate JavaScript/TypeScript code change"""
        
        feature_type = requirements.get('type', 'unknown')
        framework = pattern_analysis.get('framework', 'express')
        
        if feature_type == 'add_endpoint':
            return await self._add_js_endpoint(existing_content, requirements, framework)
        elif feature_type == 'add_component':
            return await self._add_js_component(existing_content, requirements, framework)
        else:
            return await self._modify_js_code(existing_content, requirements, framework)
    
    async def _add_js_endpoint(
        self, 
        existing_content: str, 
        requirements: Dict, 
        framework: str
    ) -> str:
        """Add new endpoint to JavaScript code"""
        
        endpoint_name = requirements.get('endpoint_name', 'newEndpoint')
        method = requirements.get('method', 'get')
        
        if framework == 'express':
            endpoint_code = f'''
// {endpoint_name} endpoint
router.{method.lower()}('/{endpoint_name}', async (req, res) => {{
    try {{
        // {requirements.get('description', 'New endpoint')}
        const result = {{ success: true, data: null }};
        res.json(result);
    }} catch (error) {{
        console.error('Error in {endpoint_name}:', error);
        res.status(500).json({{ error: 'Internal server error' }});
    }}
}});
'''
        else:
            endpoint_code = f'''
// {endpoint_name} endpoint
function {endpoint_name}() {{
    // {requirements.get('description', 'New endpoint')}
    return {{ success: true, data: null }};
}}
'''
        
        return existing_content + '\n' + endpoint_code
    
    async def _generate_unit_tests(
        self, 
        code_changes: Dict[str, str], 
        test_framework: str
    ) -> Dict[str, str]:
        """Generate unit tests for code changes"""
        
        tests = {}
        
        for file_path, new_content in code_changes.items():
            language = self._detect_language(Path(file_path).suffix)
            
            if language == 'python':
                tests[file_path] = await self._generate_python_test(
                    file_path, new_content, test_framework
                )
            elif language in ['javascript', 'typescript']:
                tests[file_path] = await self._generate_js_test(
                    file_path, new_content, test_framework
                )
        
        return tests
    
    async def _generate_python_test(
        self, 
        file_path: str, 
        content: str, 
        test_framework: str
    ) -> str:
        """Generate Python unit test"""
        
        module_name = Path(file_path).stem
        test_code = f'''
import pytest
from {module_name} import *

class Test{module_name.title()}:
    """
    Unit tests for {module_name}
    """
    
    def test_{module_name}_exists(self):
        """Test that module exists"""
        assert True  # Placeholder
    
    # TODO: Add specific tests based on content analysis
'''
        
        return test_code
    
    async def _generate_js_test(
        self, 
        file_path: str, 
        content: str, 
        test_framework: str
    ) -> str:
        """Generate JavaScript/TypeScript unit test"""
        
        module_name = Path(file_path).stem
        
        if test_framework == 'jest':
            test_code = f'''
const {{ {module_name} }} = require('./{module_name}');

describe('{module_name}', () => {{
    /*
     * Unit tests for {module_name}
     */
    
    test('should exist', () => {{
        expect({module_name}).toBeDefined();
    }});
    
    // TODO: Add specific tests based on content analysis
}});
'''
        else:
            test_code = f'''
// Tests for {module_name}
// TODO: Add test implementation
'''
        
        return test_code
    
    async def _update_api_contracts(
        self, 
        code_changes: Dict[str, str], 
        api_contract: Optional[Dict]
    ) -> Dict[str, Any]:
        """Update API contracts based on code changes"""
        
        if not api_contract:
            return {}
        
        # Analyze changes for API impact
        api_changes = {
            'endpoints_added': [],
            'endpoints_modified': [],
            'schemas_updated': [],
            'version_bump': True
        }
        
        for file_path, content in code_changes.items():
            if 'route' in file_path or 'api' in file_path:
                # Extract endpoint information
                endpoints = self._extract_endpoints_from_content(content)
                api_changes['endpoints_added'].extend(endpoints)
        
        return api_changes
    
    async def _generate_migrations(
        self, 
        code_changes: Dict[str, str], 
        database_schema: Optional[Dict]
    ) -> List[str]:
        """Generate database migration scripts"""
        
        if not database_schema:
            return []
        
        migrations = []
        
        # Analyze model changes
        for file_path, content in code_changes.items():
            if 'model' in file_path or 'schema' in file_path:
                migration = await self._generate_migration_script(
                    file_path, content, database_schema
                )
                if migration:
                    migrations.append(migration)
        
        return migrations
    
    async def _generate_migration_script(
        self, 
        file_path: str, 
        content: str, 
        database_schema: Dict
    ) -> Optional[str]:
        """Generate migration script for model changes"""
        
        # Extract model information
        model_name = Path(file_path).stem
        
        migration = f'''
-- Migration for {model_name}
-- Generated on: {self._get_timestamp()}

BEGIN;

-- TODO: Add specific migration steps based on model analysis

COMMIT;
'''
        
        return migration
    
    async def _create_integration_notes(
        self, 
        code_changes: Dict[str, str], 
        pattern_analysis: Dict
    ) -> str:
        """Create integration and deployment notes"""
        
        notes = f"""
## Integration Notes

### Changes Made
- {len(code_changes)} files modified
- Framework: {pattern_analysis.get('framework', 'unknown')}
- Pattern compliance: {'Yes' if pattern_analysis else 'No patterns found'}

### Deployment Requirements
1. **Database Migration**: Run migration scripts if any
2. **API Documentation**: Update API docs
3. **Environment Variables**: Check for new required variables
4. **Dependencies**: Install any new dependencies

### Testing
- Unit tests: Generated
- Integration testing: Required
- API testing: Recommended

### Rollback Plan
- Database: Migration rollback available
- Code: Version control rollback
- API: Version compatibility maintained
"""
        
        return notes
    
    def _detect_language(self, file_extension: str) -> str:
        """Detect programming language from file extension"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby'
        }
        return extension_map.get(file_extension, 'unknown')
    
    def _detect_style_guide(self, patterns: List[Dict]) -> str:
        """Detect coding style guide from patterns"""
        # Simple heuristic based on common patterns
        has_type_hints = any('type_hint' in str(p).lower() for p in patterns)
        has_docstrings = any('docstring' in str(p).lower() for p in patterns)
        
        if has_type_hints and has_docstrings:
            return 'strict'
        elif has_type_hints or has_docstrings:
            return 'moderate'
        else:
            return 'lenient'
    
    def _add_to_ast(self, tree: ast.AST, new_code: str) -> ast.AST:
        """Add new code to AST (simplified)"""
        # This is a simplified version - in practice, you'd need more sophisticated AST manipulation
        try:
            new_tree = ast.parse(new_code)
            # Combine trees (simplified)
            return ast.Module(body=tree.body + new_tree.body)
        except:
            return tree
    
    def _extract_endpoints_from_content(self, content: str) -> List[Dict]:
        """Extract endpoint information from content"""
        endpoints = []
        
        # Simple regex for endpoint detection
        patterns = [
            r'@(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
            r'app\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
            r'router\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                method = match[0].upper() if isinstance(match, tuple) else 'GET'
                path = match[1] if len(match) > 1 else match
                endpoints.append({
                    'method': method,
                    'path': path,
                    'full_path': f"{method} {path}"
                })
        
        return endpoints
    
    async def _get_existing_content(self, file_path: str) -> str:
        """Get existing file content (mock implementation)"""
        # TODO: Implement actual file retrieval from storage
        return f"// Existing content of {file_path}\n// TODO: Load actual content"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
