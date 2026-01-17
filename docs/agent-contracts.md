# Agent Contracts and Interfaces

## Base Agent Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class AgentInput:
    """Standard input structure for all agents"""
    execution_plan_id: str
    phase_number: int
    context: Dict[str, Any]
    repositories: List[str]
    file_scope: List[str]  # Specific files agent can modify
    constraints: Dict[str, Any]
    memory_snapshot: Dict[str, Any]

@dataclass
class AgentOutput:
    """Standard output structure for all agents"""
    status: AgentStatus
    files_modified: List[str]
    files_created: List[str]
    artifacts_created: List[str]
    next_actions: List[str]
    token_usage: Dict[str, int]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Base contract for all agent implementations"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.PENDING
    
    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Execute the agent's primary function"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate input before execution"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, input_data: AgentInput) -> int:
        """Estimate token usage for cost control"""
        pass
```

## 1. Strategic Planner Agent

```python
@dataclass
class PlannerInput(AgentInput):
    feature_request: Dict[str, Any]
    discovery_reports: List[Dict[str, Any]]
    dependency_graph: Dict[str, Any]
    existing_api_contracts: List[Dict[str, Any]]

@dataclass
class PlannerOutput(AgentOutput):
    execution_plan: Dict[str, Any]
    blast_radius: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    api_contract_proposal: Optional[Dict[str, Any]]
    test_strategy: Dict[str, Any]
    rollout_plan: Dict[str, Any]
    evidence_links: List[str]  # Links to repo evidence

class StrategicPlannerAgent(BaseAgent):
    """Enterprise brain - creates safe, evidence-based plans"""
    
    async def execute(self, input_data: PlannerInput) -> PlannerOutput:
        """
        1. Analyze feature request against discovery data
        2. Identify impacted repos and files with evidence
        3. Generate phased execution plan
        4. Assess blast radius and risks
        5. Create API contract proposal if needed
        6. Define test strategy and rollout approach
        """
        pass
    
    def validate_input(self, input_data: PlannerInput) -> bool:
        """Ensure discovery data is sufficient for planning"""
        required_fields = ['feature_request', 'discovery_reports']
        return all(field in input_data.__dict__ for field in required_fields)
```

## 2. Backend Implementation Agent

```python
@dataclass
class BackendInput(AgentInput):
    api_contract: Optional[Dict[str, Any]]
    existing_patterns: List[Dict[str, Any]]
    database_schema: Optional[Dict[str, Any]]
    test_framework: str

@dataclass
class BackendOutput(AgentOutput):
    code_changes: Dict[str, str]  # file_path -> new_content
    unit_tests: Dict[str, str]
    api_updates: Dict[str, Any]
    migration_scripts: List[str]
    integration_notes: str

class BackendAgent(BaseAgent):
    """Scoped backend code modifications with pattern compliance"""
    
    async def execute(self, input_data: BackendInput) -> BackendOutput:
        """
        1. Analyze existing code patterns in scope
        2. Implement changes following established patterns
        3. Generate/update unit tests
        4. Update API contracts if required
        5. Create database migrations if needed
        6. Document integration requirements
        """
        pass
    
    def validate_input(self, input_data: BackendInput) -> bool:
        """Ensure file scope is valid and patterns exist"""
        return len(input_data.file_scope) > 0 and input_data.existing_patterns
```

## 3. Frontend Implementation Agent

```python
@dataclass
class FrontendInput(AgentInput):
    design_spec: Optional[Dict[str, Any]]
    component_library: Dict[str, Any]
    api_client_config: Dict[str, Any]
    routing_config: Dict[str, Any]

@dataclass
class FrontendOutput(AgentOutput):
    component_changes: Dict[str, str]
    route_updates: Dict[str, Any]
    api_integrations: Dict[str, str]
    component_tests: Dict[str, str]
    user_flow_updates: Dict[str, Any]

class FrontendAgent(BaseAgent):
    """UI implementation with design system compliance"""
    
    async def execute(self, input_data: FrontendInput) -> FrontendOutput:
        """
        1. Analyze design spec and component library
        2. Implement/update components following design system
        3. Update routing and navigation
        4. Integrate with API endpoints
        5. Generate component tests
        6. Update user flows and state management
        """
        pass
```

## 4. Code Reviewer Agent

```python
@dataclass
class ReviewerInput(AgentInput):
    proposed_changes: Dict[str, str]  # file_path -> diff
    coding_standards: Dict[str, Any]
    security_rules: Dict[str, Any]
    test_coverage_requirements: Dict[str, Any]

@dataclass
class ReviewerOutput(AgentOutput):
    review_status: str  # "approved", "needs_changes", "blocked"
    security_issues: List[Dict[str, Any]]
    pattern_violations: List[Dict[str, Any]]
    test_coverage_gaps: List[str]
    recommendations: List[str]
    can_merge: bool

class CodeReviewerAgent(BaseAgent):
    """Enterprise-grade code review with security focus"""
    
    async def execute(self, input_data: ReviewerInput) -> ReviewerOutput:
        """
        1. Check for security vulnerabilities
        2. Verify coding pattern compliance
        3. Validate API contract consistency
        4. Check test coverage
        5. Identify breaking changes
        6. Provide actionable recommendations
        """
        pass
    
    def validate_input(self, input_data: ReviewerInput) -> bool:
        """Ensure changes are provided and standards exist"""
        return input_data.proposed_changes and input_data.coding_standards
```

## 5. QA Agent

```python
@dataclass
class QAInput(AgentInput):
    test_commands: List[str]
    quality_gates: Dict[str, Any]
    performance_benchmarks: Dict[str, Any]

@dataclass
class QAOutput(AgentOutput):
    test_results: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    performance_results: Dict[str, Any]
    coverage_report: Dict[str, Any]
    release_readiness: bool

class QAAgent(BaseAgent):
    """Automated testing and quality assurance"""
    
    async def execute(self, input_data: QAInput) -> QAOutput:
        """
        1. Run unit tests
        2. Execute integration tests
        3. Perform security scans
        4. Check performance benchmarks
        5. Generate coverage reports
        6. Evaluate release readiness
        """
        pass
```

## 6. UX Designer Agent

```python
@dataclass
class UXInput(AgentInput):
    feature_requirements: Dict[str, Any]
    existing_design_system: Dict[str, Any]
    user_flows: List[Dict[str, Any]]
    accessibility_requirements: Dict[str, Any]

@dataclass
class UXOutput(AgentOutput):
    user_flows: List[Dict[str, Any]]
    wireframes: Dict[str, Any]  # Structured JSON specs
    design_tokens: Dict[str, Any]
    component_specifications: Dict[str, Any]
    figma_integration_data: Dict[str, Any]

class UXDesignerAgent(BaseAgent):
    """UX design generation with enterprise design systems"""
    
    async def execute(self, input_data: UXInput) -> UXOutput:
        """
        1. Analyze feature requirements and user needs
        2. Design user flows and interactions
        3. Generate wireframes in structured format
        4. Define design tokens and component specs
        5. Prepare Figma integration data
        6. Ensure accessibility compliance
        """
        pass
```

## Agent Orchestration Rules

### 1. Execution Order
```python
AGENT_EXECUTION_ORDER = {
    "feature_request": ["strategic_planner"],
    "api_change": ["strategic_planner", "backend", "code_reviewer", "qa"],
    "ui_change": ["strategic_planner", "ux_designer", "frontend", "code_reviewer", "qa"],
    "full_stack": ["strategic_planner", "ux_designer", "backend", "frontend", "code_reviewer", "qa"]
}
```

### 2. Token Limits per Agent
```python
AGENT_TOKEN_LIMITS = {
    "strategic_planner": {"max_input": 10000, "max_output": 5000},
    "backend": {"max_input": 15000, "max_output": 8000},
    "frontend": {"max_input": 12000, "max_output": 6000},
    "code_reviewer": {"max_input": 20000, "max_output": 3000},
    "qa": {"max_input": 5000, "max_output": 2000},
    "ux_designer": {"max_input": 8000, "max_output": 4000}
}
```

### 3. Failure Handling
- **Planner failures**: Block execution, require manual intervention
- **Implementation failures**: Retry 2 times, then escalate
- **Reviewer failures**: Block PR creation, notify human
- **QA failures**: Block merge, require fix

### 4. Memory Access Patterns
```python
AGENT_MEMORY_ACCESS = {
    "strategic_planner": ["discovery_reports", "dependency_graph", "api_contracts"],
    "backend": ["code_patterns", "database_schema", "api_contracts"],
    "frontend": ["design_system", "component_library", "api_specs"],
    "code_reviewer": ["coding_standards", "security_rules", "test_requirements"],
    "qa": ["test_history", "quality_gates", "performance_benchmarks"],
    "ux_designer": ["design_system", "user_research", "accessibility_guidelines"]
}
```
