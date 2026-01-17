"""
Frontend Implementation Agent
Handles UI implementation with design system compliance and API integration
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import openai
from openai import AsyncOpenAI

from services.api.config import settings
from services.agents.base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


@dataclass
class FrontendInput(AgentInput):
    design_spec: Optional[Dict[str, Any]] = None
    component_library: Dict[str, Any] = None
    api_client_config: Dict[str, Any] = None
    routing_config: Dict[str, Any] = None


@dataclass
class FrontendOutput(AgentOutput):
    component_changes: Dict[str, str] = None
    route_updates: Dict[str, Any] = None
    api_integrations: Dict[str, str] = None
    component_tests: Dict[str, str] = None
    user_flow_updates: Dict[str, Any] = None


class FrontendAgent(BaseAgent):
    """UI implementation with design system compliance"""
    
    def __init__(self):
        super().__init__("frontend", {})
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.supported_frameworks = ['react', 'vue', 'angular', 'svelte']
        self.supported_languages = ['javascript', 'typescript']
    
    async def execute(self, input_data: FrontendInput) -> FrontendOutput:
        """Execute frontend implementation with design system compliance"""
        
        try:
            # Analyze requirements and context
            requirements = input_data.context.get('requirements', {})
            file_scope = input_data.file_scope
            
            # Analyze design system and component library
            design_analysis = await self._analyze_design_system(input_data.design_spec)
            
            # Generate component changes
            component_changes = {}
            for file_path in file_scope:
                if self._is_component_file(file_path):
                    change = await self._generate_component_change(
                        file_path, requirements, design_analysis
                    )
                    if change:
                        component_changes[file_path] = change
            
            # Generate route updates
            route_updates = await self._generate_route_updates(
                component_changes, input_data.routing_config
            )
            
            # Generate API integrations
            api_integrations = await self._generate_api_integrations(
                component_changes, input_data.api_client_config
            )
            
            # Generate component tests
            component_tests = await self._generate_component_tests(
                component_changes, input_data.component_library
            )
            
            # Update user flows
            user_flows = await self._update_user_flows(
                component_changes, requirements
            )
            
            return FrontendOutput(
                status=AgentStatus.COMPLETED,
                files_modified=list(component_changes.keys()),
                files_created=list(component_tests.keys()),
                artifacts_created=["components", "routes", "api_integrations", "tests"],
                next_actions=["code_review", "integration_testing", "user_testing"],
                token_usage={"prompt_tokens": 2500, "completion_tokens": 1800, "total": 4300},
                component_changes=component_changes,
                route_updates=route_updates,
                api_integrations=api_integrations,
                component_tests=component_tests,
                user_flow_updates=user_flows
            )
            
        except Exception as e:
            return FrontendOutput(
                status=AgentStatus.FAILED,
                files_modified=[],
                files_created=[],
                artifacts_created=[],
                next_actions=["retry", "debug"],
                token_usage={},
                error_message=f"Frontend implementation failed: {str(e)}"
            )
    
    def validate_input(self, input_data: FrontendInput) -> bool:
        """Validate frontend implementation input"""
        return (
            hasattr(input_data, 'file_scope') and 
            len(input_data.file_scope) > 0 and
            hasattr(input_data, 'context')
        )
    
    def estimate_tokens(self, input_data: FrontendInput) -> int:
        """Estimate token usage for frontend implementation"""
        file_count = len(input_data.file_scope)
        context_size = len(str(input_data.context))
        return (file_count * 400) + context_size + 800
    
    async def _analyze_design_system(self, design_spec: Optional[Dict]) -> Dict[str, Any]:
        """Analyze design system and component library"""
        
        if not design_spec:
            return {
                'framework': 'unknown',
                'design_tokens': {},
                'component_patterns': {},
                'styling_approach': 'css'
            }
        
        return {
            'framework': design_spec.get('framework', 'react'),
            'design_tokens': design_spec.get('design_tokens', {}),
            'component_patterns': design_spec.get('component_patterns', {}),
            'styling_approach': design_spec.get('styling_approach', 'css'),
            'color_scheme': design_spec.get('color_scheme', {}),
            'typography': design_spec.get('typography', {})
        }
    
    async def _generate_component_change(
        self, 
        file_path: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> Optional[str]:
        """Generate component change following design system"""
        
        try:
            # Determine component type and framework
            component_name = Path(file_path).stem
            framework = design_analysis.get('framework', 'react')
            file_ext = Path(file_path).suffix.lower()
            
            # Get existing content (mock for now)
            existing_content = await self._get_existing_content(file_path)
            
            # Generate change based on requirements
            if framework == 'react':
                return await self._generate_react_component(
                    file_path, existing_content, requirements, design_analysis
                )
            elif framework == 'vue':
                return await self._generate_vue_component(
                    file_path, existing_content, requirements, design_analysis
                )
            elif framework == 'angular':
                return await self._generate_angular_component(
                    file_path, existing_content, requirements, design_analysis
                )
            else:
                return await self._generate_generic_component(
                    file_path, existing_content, requirements, design_analysis
                )
                
        except Exception as e:
            print(f"Failed to generate component change for {file_path}: {e}")
            return None
    
    async def _generate_react_component(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> str:
        """Generate React component following design system"""
        
        component_name = Path(file_path).stem
        feature_type = requirements.get('type', 'unknown')
        design_tokens = design_analysis.get('design_tokens', {})
        
        if feature_type == 'add_component':
            return f'''
import React from 'react';
import {{ {design_tokens.get('button_component', 'Button')} }} from '../components';

/**
 * {component_name} - {requirements.get('description', 'New component')}
 */
const {component_name}: React.FC = ({{
  // Props
  {self._generate_props_interface(requirements)}
}}) => {{
  return (
    <div className="{component_name}">
      {{'{{ TODO: Implement component based on requirements }}'}}
      <{design_tokens.get('button_component', 'Button')}>
        {requirements.get('button_text', 'Click me')}
      </{design_tokens.get('button_component', 'Button')}>
    </div>
  );
}};

export default {component_name};
'''
        elif feature_type == 'update_component':
            # Update existing component
            return await self._update_react_component(
                existing_content, requirements, design_analysis
            )
        else:
            return existing_content
    
    async def _generate_vue_component(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> str:
        """Generate Vue component following design system"""
        
        component_name = Path(file_path).stem
        design_tokens = design_analysis.get('design_tokens', {})
        
        return f'''
<template>
  <div class="{component_name}">
    <!-- TODO: Implement component based on requirements -->
  </div>
</template>

<script>
export default {{
  name: '{component_name}',
  props: {{
    // TODO: Define props based on requirements
  }}
}};
</script>

<style scoped>
.{component_name} {{
  /* TODO: Apply design tokens */
}}
</style>
'''
    
    async def _generate_angular_component(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> str:
        """Generate Angular component following design system"""
        
        component_name = Path(file_path).stem
        
        return f'''
import {{ Component }} from '@angular/core';

/**
 * {component_name} - {requirements.get('description', 'New component')}
 */
@Component({{
  selector: 'app-{component_name.lower()}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.css']
}})
export class {component_name}Component {{
  // TODO: Implement component logic
}}
'''
    
    async def _generate_route_updates(
        self, 
        component_changes: Dict[str, str], 
        routing_config: Dict
    ) -> Dict[str, Any]:
        """Generate routing updates for new components"""
        
        routes = {}
        
        for file_path, content in component_changes.items():
            component_name = Path(file_path).stem
            
            # Extract route information from content
            route_path = self._extract_route_from_component(content, component_name)
            
            if route_path:
                routes[component_name] = {
                    'path': route_path,
                    'component': component_name,
                    'method': 'GET',
                    'guards': [],
                    'lazy': True
                }
        
        return {
            'routes_added': routes,
            'routing_file': routing_config.get('file', 'src/routes/index.js'),
            'updates_required': len(routes) > 0
        }
    
    async def _generate_api_integrations(
        self, 
        component_changes: Dict[str, str], 
        api_config: Dict
    ) -> Dict[str, str]:
        """Generate API client integrations for components"""
        
        integrations = {}
        
        for file_path, content in component_changes.items():
            # Extract API calls from component
            api_calls = self._extract_api_calls_from_component(content)
            
            for call in api_calls:
                integration_file = f"api/{call['service']}.js"
                integrations[integration_file] = await self._generate_api_client(
                    call, api_config
                )
        
        return integrations
    
    async def _generate_component_tests(
        self, 
        component_changes: Dict[str, str], 
        component_library: Dict
    ) -> Dict[str, str]:
        """Generate component tests"""
        
        tests = {}
        test_framework = component_library.get('test_framework', 'jest')
        
        for file_path, content in component_changes.items():
            component_name = Path(file_path).stem
            
            if test_framework == 'jest':
                tests[file_path] = f'''
import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import {component_name} from './{component_name}';

describe('{component_name}', () => {{
  it('renders correctly', () => {{
    render(<{component_name} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  }});
  
  it('handles click events', () => {{
    const handleClick = jest.fn();
    render(<{component_name} onClick={{handleClick}} />);
    
    // TODO: Add specific interaction tests
  }});
  
  // TODO: Add more tests based on component functionality
}});
'''
            else:
                tests[file_path] = f'''
// Tests for {component_name}
// TODO: Implement test framework
'''
        
        return tests
    
    async def _update_user_flows(
        self, 
        component_changes: Dict[str, str], 
        requirements: Dict
    ) -> Dict[str, Any]:
        """Update user flows and navigation"""
        
        flows = {}
        
        # Analyze component changes for flow impact
        for file_path, content in component_changes.items():
            component_name = Path(file_path).stem
            
            # Extract navigation/flow information
            flow_info = self._extract_flow_information(content, component_name)
            
            if flow_info:
                flows[component_name] = flow_info
        
        return {
            'flows_updated': flows,
            'navigation_changes': self._generate_navigation_updates(flows),
            'user_journeys': self._analyze_user_journeys(flows)
        }
    
    def _generate_props_interface(self, requirements: Dict) -> str:
        """Generate TypeScript interface for component props"""
        
        props = requirements.get('props', {})
        if not props:
            return ''
        
        interface_lines = ['interface Props {']
        for prop_name, prop_type in props.items():
            interface_lines.append(f'  {prop_name}: {prop_type};')
        interface_lines.append('}')
        
        return '\n'.join(interface_lines)
    
    def _extract_route_from_component(self, content: str, component_name: str) -> Optional[str]:
        """Extract route path from component content"""
        
        # Look for route patterns
        patterns = [
            rf'path\s*[:]?[:]?[:]?["\']([^"\']+)["\'].*{component_name}',
            rf'route\s*[:]?[:]?[:]?["\']([^"\']+)["\'].*{component_name}',
            rf'/{component_name.lower()}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.groups():
                    return match.group(1)
                else:
                    return match.group(0)
        
        return None
    
    def _extract_api_calls_from_component(self, content: str) -> List[Dict]:
        """Extract API calls from component content"""
        
        api_calls = []
        
        # Common API call patterns
        patterns = [
            r'(fetch|axios|http)\s*\.\s*(get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']',
            r'api\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'service\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                service = match[1] if len(match) > 1 else 'unknown'
                api_calls.append({
                    'service': service,
                    'method': match[0] if len(match) > 1 else 'GET',
                    'endpoint': match[1] if len(match) > 1 else '/unknown'
                })
        
        return api_calls
    
    def _extract_flow_information(self, content: str, component_name: str) -> Optional[Dict]:
        """Extract user flow information from component"""
        
        # Look for navigation and flow patterns
        if 'navigate' in content or 'router' in content:
            return {
                'type': 'navigation',
                'target': self._extract_navigation_target(content),
                'triggers': self._extract_triggers(content)
            }
        
        return None
    
    def _generate_navigation_updates(self, flows: Dict) -> List[Dict]:
        """Generate navigation updates based on flows"""
        
        updates = []
        
        for component_name, flow_info in flows.items():
            if flow_info.get('type') == 'navigation':
                updates.append({
                    'type': 'navigation_add',
                    'component': component_name,
                    'target': flow_info.get('target'),
                    'route': f'/{component_name.lower()}'
                })
        
        return updates
    
    def _analyze_user_journeys(self, flows: Dict) -> List[Dict]:
        """Analyze complete user journeys"""
        
        journeys = []
        
        # Group flows by user journey
        navigation_flows = {
            name: info for name, info in flows.items() 
            if info.get('type') == 'navigation'
        }
        
        # Create journey mappings
        if navigation_flows:
            journeys.append({
                'name': 'Primary Navigation Flow',
                'steps': list(navigation_flows.keys()),
                'entry_point': list(navigation_flows.keys())[0] if navigation_flows else None
            })
        
        return journeys
    
    def _extract_navigation_target(self, content: str) -> str:
        """Extract navigation target from content"""
        
        patterns = [
            r'navigate\s*\(\s*["\']([^"\']+)["\']',
            r'router\.push\s*\(\s*["\']([^"\']+)["\']',
            r'history\.push\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return '/unknown'
    
    def _extract_triggers(self, content: str) -> List[str]:
        """Extract interaction triggers from content"""
        
        triggers = []
        
        # Common trigger patterns
        trigger_patterns = [
            r'onClick\s*=\s*{{([^}]+)}}',
            r'onSubmit\s*=\s*{{([^}]+)}}',
            r'onChange\s*=\s*{{([^}]+)}}',
            r'onClick\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in trigger_patterns:
            matches = re.findall(pattern, content)
            triggers.extend(matches)
        
        return list(set(triggers))
    
    def _is_component_file(self, file_path: str) -> bool:
        """Check if file is a component"""
        
        component_indicators = [
            'components/', 'src/components/', 'src/views/',
            '.jsx', '.tsx', '.vue', '.component.ts', '.component.js'
        ]
        
        file_path_lower = file_path.lower()
        return any(indicator in file_path_lower for indicator in component_indicators)
    
    async def _update_react_component(
        self, 
        existing_content: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> str:
        """Update existing React component"""
        
        # Simple implementation - in practice, would use AST parsing
        updates = requirements.get('updates', [])
        
        for update in updates:
            if update.get('type') == 'add_prop':
                # Add new prop to component
                prop_line = f"  {update.get('name')}: {update.get('type')};"
                # TODO: More sophisticated component updating
                existing_content += f"\n  // Added prop: {update.get('name')}"
        
        return existing_content
    
    async def _generate_generic_component(
        self, 
        file_path: str, 
        existing_content: str, 
        requirements: Dict, 
        design_analysis: Dict
    ) -> str:
        """Generate generic component code"""
        
        component_name = Path(file_path).stem
        
        return f'''
/**
 * {component_name} - {requirements.get('description', 'New component')}
 */
// TODO: Implement component based on requirements and design system
// Framework: {design_analysis.get('framework', 'unknown')}

export default {component_name};
'''
    
    async def _generate_api_client(
        self, 
        api_call: Dict, 
        api_config: Dict
    ) -> str:
        """Generate API client code"""
        
        service = api_call.get('service', 'unknown')
        method = api_call.get('method', 'GET')
        endpoint = api_call.get('endpoint', '/unknown')
        
        base_url = api_config.get('base_url', 'http://localhost:8000/api')
        
        return f'''
import axios from 'axios';

/**
 * API client for {service}
 */
class {service.title()}Client {{
  constructor(baseURL = '{base_url}') {{
    this.baseURL = baseURL;
  }}
  
  async {method.lower()}() {{
    try {{
      const response = await axios.{method.lower()}(`${{this.baseURL}}{endpoint}`);
      return response.data;
    }} catch (error) {{
      console.error('Error in {service} API:', error);
      throw error;
    }}
  }}
}}

export default {service.title()}Client;
'''
    
    async def _get_existing_content(self, file_path: str) -> str:
        """Get existing file content (mock implementation)"""
        # TODO: Implement actual file retrieval from storage
        return f"// Existing content of {file_path}\n// TODO: Load actual content"
