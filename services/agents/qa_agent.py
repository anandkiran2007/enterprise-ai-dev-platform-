"""
QA Agent
Performs automated testing and quality assurance
"""

import asyncio
import subprocess
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

from services.api.config import settings
from services.agents.base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


@dataclass
class QAInput(AgentInput):
    test_commands: List[str] = None
    quality_gates: Dict[str, Any] = None
    performance_benchmarks: Dict[str, Any] = None


@dataclass
class QAOutput(AgentOutput):
    test_results: Dict[str, Any] = None
    quality_metrics: Dict[str, Any] = None
    performance_results: Dict[str, Any] = None
    coverage_report: Dict[str, Any] = None
    release_readiness: bool = None


class QAAgent(BaseAgent):
    """Automated testing and quality assurance"""
    
    def __init__(self):
        super().__init__("qa", {})
        self.test_frameworks = {
            'python': 'pytest',
            'javascript': 'jest',
            'typescript': 'jest',
            'java': 'junit',
            'go': 'go test'
        }
        
        self.quality_tools = {
            'linters': {
                'python': ['flake8', 'pylint'],
                'javascript': ['eslint'],
                'typescript': ['eslint'],
                'java': ['checkstyle'],
                'go': ['golint', 'go vet']
            },
            'security': ['bandit', 'semgrep', 'snyk'],
            'complexity': ['radon', 'complexity'],
            'coverage': ['coverage.py', 'nyc', 'jacoco']
        }
    
    async def execute(self, input_data: QAInput) -> QAOutput:
        """Execute comprehensive QA testing"""
        
        try:
            # Get context and file scope
            context = input_data.context
            file_scope = input_data.file_scope
            
            # Detect project languages and frameworks
            project_info = await self._analyze_project_structure(file_scope)
            
            # Run unit tests
            unit_test_results = await self._run_unit_tests(
                file_scope, project_info, input_data.test_commands
            )
            
            # Run integration tests
            integration_test_results = await self._run_integration_tests(
                file_scope, project_info
            )
            
            # Run quality checks
            quality_metrics = await self._run_quality_checks(
                file_scope, project_info, input_data.quality_gates
            )
            
            # Run performance benchmarks
            performance_results = await self._run_performance_benchmarks(
                file_scope, project_info, input_data.performance_benchmarks
            )
            
            # Generate coverage report
            coverage_report = await self._generate_coverage_report(
                unit_test_results, integration_test_results
            )
            
            # Assess release readiness
            release_readiness = await self._assess_release_readiness(
                unit_test_results, integration_test_results, 
                quality_metrics, performance_results
            )
            
            return QAOutput(
                status=AgentStatus.COMPLETED,
                files_modified=[],
                files_created=[],
                artifacts_created=["test_results", "quality_metrics", "performance_report"],
                next_actions=["deploy_if_ready", "fix_issues", "documentation_update"],
                token_usage={"prompt_tokens": 1500, "completion_tokens": 1000, "total": 2500},
                test_results={
                    'unit_tests': unit_test_results,
                    'integration_tests': integration_test_results
                },
                quality_metrics=quality_metrics,
                performance_results=performance_results,
                coverage_report=coverage_report,
                release_readiness=release_readiness
            )
            
        except Exception as e:
            return QAOutput(
                status=AgentStatus.FAILED,
                files_modified=[],
                files_created=[],
                artifacts_created=[],
                next_actions=["retry", "debug"],
                token_usage={},
                error_message=f"QA testing failed: {str(e)}"
            )
    
    def validate_input(self, input_data: QAInput) -> bool:
        """Validate QA input"""
        return (
            hasattr(input_data, 'file_scope') and 
            len(input_data.file_scope) > 0
        )
    
    def estimate_tokens(self, input_data: QAInput) -> int:
        """Estimate token usage for QA testing"""
        file_count = len(input_data.file_scope)
        return (file_count * 100) + 1000
    
    async def _analyze_project_structure(self, file_scope: List[str]) -> Dict[str, Any]:
        """Analyze project structure to determine languages and frameworks"""
        
        languages = {}
        frameworks = []
        test_directories = []
        
        for file_path in file_scope:
            ext = Path(file_path).suffix.lower()
            
            # Count languages
            if ext in ['.py']:
                languages['python'] = languages.get('python', 0) + 1
            elif ext in ['.js', '.jsx']:
                languages['javascript'] = languages.get('javascript', 0) + 1
            elif ext in ['.ts', '.tsx']:
                languages['typescript'] = languages.get('typescript', 0) + 1
            elif ext in ['.java']:
                languages['java'] = languages.get('java', 0) + 1
            
            # Detect test directories
            if 'test' in file_path.lower():
                test_directories.append(file_path)
            
            # Detect frameworks from file patterns
            content = await self._get_file_content(file_path)
            if 'package.json' in file_path:
                if 'react' in content:
                    frameworks.append('react')
                elif 'vue' in content:
                    frameworks.append('vue')
                elif 'angular' in content:
                    frameworks.append('angular')
            elif 'requirements.txt' in file_path or 'Pipfile' in file_path:
                frameworks.extend(['django', 'flask', 'fastapi'])
        
        return {
            'languages': languages,
            'frameworks': list(set(frameworks)),
            'test_directories': test_directories,
            'primary_language': max(languages.items(), key=lambda x: x[1])[0] if languages else 'unknown'
        }
    
    async def _run_unit_tests(self, file_scope: List[str], project_info: Dict, custom_commands: List[str]) -> Dict[str, Any]:
        """Run unit tests based on project language"""
        
        results = {
            'framework': self.test_frameworks.get(project_info.get('primary_language', 'python'), 'pytest'),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_suites': [],
            'execution_time': 0,
            'coverage_percentage': 0
        }
        
        # Use custom commands if provided
        if custom_commands:
            for command in custom_commands:
                try:
                    result = await self._execute_test_command(command)
                    results['test_suites'].append(result)
                    results['tests_run'] += result.get('tests_run', 0)
                    results['tests_passed'] += result.get('tests_passed', 0)
                    results['tests_failed'] += result.get('tests_failed', 0)
                except Exception as e:
                    results['test_suites'].append({
                        'command': command,
                        'error': str(e),
                        'tests_run': 0,
                        'tests_passed': 0,
                        'tests_failed': 0
                    })
        else:
            # Default test execution based on language
            primary_lang = project_info.get('primary_language', 'python')
            
            if primary_lang == 'python':
                results.update(await self._run_python_tests(file_scope))
            elif primary_lang in ['javascript', 'typescript']:
                results.update(await self._run_javascript_tests(file_scope))
            elif primary_lang == 'java':
                results.update(await self._run_java_tests(file_scope))
        
        return results
    
    async def _run_integration_tests(self, file_scope: List[str], project_info: Dict) -> Dict[str, Any]:
        """Run integration tests"""
        
        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_suites': [],
            'execution_time': 0,
            'api_endpoints_tested': []
        }
        
        # Look for integration test files
        integration_files = [
            f for f in file_scope 
            if 'integration' in f.lower() or 'e2e' in f.lower()
        ]
        
        for test_file in integration_files:
            try:
                # Determine test framework
                ext = Path(test_file).suffix.lower()
                framework = 'jest' if ext in ['.js', '.jsx', '.ts', '.tsx'] else 'pytest'
                
                result = await self._execute_test_command(f"{framework} {test_file}")
                results['test_suites'].append(result)
                results['tests_run'] += result.get('tests_run', 0)
                results['tests_passed'] += result.get('tests_passed', 0)
                results['tests_failed'] += result.get('tests_failed', 0)
                
                # Extract API endpoints tested
                content = await self._get_file_content(test_file)
                endpoints = re.findall(r'["\'](/api/[^"\']+)["\']', content)
                results['api_endpoints_tested'].extend(endpoints)
                
            except Exception as e:
                results['test_suites'].append({
                    'file': test_file,
                    'error': str(e),
                    'tests_run': 0,
                    'tests_passed': 0,
                    'tests_failed': 0
                })
        
        return results
    
    async def _run_quality_checks(self, file_scope: List[str], project_info: Dict, quality_gates: Dict) -> Dict[str, Any]:
        """Run code quality checks"""
        
        metrics = {
            'linting': {},
            'security_scan': {},
            'complexity_analysis': {},
            'code_smells': [],
            'duplicate_code': [],
            'quality_score': 0
        }
        
        primary_lang = project_info.get('primary_language', 'python')
        
        # Run linting
        linters = self.quality_tools['linters'].get(primary_lang, [])
        for linter in linters:
            try:
                linter_result = await self._run_linter(linter, file_scope)
                metrics['linting'][linter] = linter_result
            except Exception as e:
                metrics['linting'][linter] = {'error': str(e)}
        
        # Run security scan
        security_tools = self.quality_tools['security']
        for tool in security_tools:
            try:
                security_result = await self._run_security_scan(tool, file_scope)
                metrics['security_scan'][tool] = security_result
            except Exception as e:
                metrics['security_scan'][tool] = {'error': str(e)}
        
        # Analyze complexity
        complexity_tools = self.quality_tools['complexity'].get(primary_lang, [])
        for tool in complexity_tools:
            try:
                complexity_result = await self._run_complexity_analysis(tool, file_scope)
                metrics['complexity_analysis'][tool] = complexity_result
            except Exception as e:
                metrics['complexity_analysis'][tool] = {'error': str(e)}
        
        # Calculate overall quality score
        metrics['quality_score'] = self._calculate_quality_score(metrics)
        
        return metrics
    
    async def _run_performance_benchmarks(self, file_scope: List[str], project_info: Dict, benchmarks: Dict) -> Dict[str, Any]:
        """Run performance benchmarks"""
        
        results = {
            'benchmarks_run': [],
            'performance_metrics': {},
            'memory_usage': {},
            'response_times': {},
            'throughput': {},
            'performance_score': 0
        }
        
        # Default benchmarks if none provided
        if not benchmarks:
            benchmarks = {
                'load_time': {'target': 2000},  # 2 seconds
                'memory_usage': {'target': 512},   # 512 MB
                'cpu_usage': {'target': 70}        # 70%
            }
        
        for benchmark_name, benchmark_config in benchmarks.items():
            try:
                benchmark_result = await self._run_benchmark(benchmark_name, benchmark_config, file_scope)
                results['benchmarks_run'].append(benchmark_result)
                results['performance_metrics'][benchmark_name] = benchmark_result
            except Exception as e:
                results['benchmarks_run'].append({
                    'benchmark': benchmark_name,
                    'error': str(e)
                })
        
        # Calculate performance score
        results['performance_score'] = self._calculate_performance_score(results['performance_metrics'])
        
        return results
    
    async def _generate_coverage_report(
        self, 
        unit_results: Dict, 
        integration_results: Dict
    ) -> Dict[str, Any]:
        """Generate comprehensive coverage report"""
        
        total_tests = unit_results.get('tests_run', 0) + integration_results.get('tests_run', 0)
        total_passed = unit_results.get('tests_passed', 0) + integration_results.get('tests_passed', 0)
        total_failed = unit_results.get('tests_failed', 0) + integration_results.get('tests_failed', 0)
        
        coverage_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'tests_passed': total_passed,
            'tests_failed': total_failed,
            'coverage_percentage': round(coverage_percentage, 2),
            'unit_test_coverage': unit_results.get('coverage_percentage', 0),
            'integration_test_coverage': integration_results.get('coverage_percentage', 0),
            'coverage_gaps': self._identify_coverage_gaps(unit_results, integration_results)
        }
    
    async def _assess_release_readiness(
        self, 
        unit_results: Dict, 
        integration_results: Dict, 
        quality_metrics: Dict, 
        performance_results: Dict
    ) -> bool:
        """Assess if code is ready for release"""
        
        # Check test pass rate
        total_tests = unit_results.get('tests_run', 0) + integration_results.get('tests_run', 0)
        total_passed = unit_results.get('tests_passed', 0) + integration_results.get('tests_passed', 0)
        pass_rate = (total_passed / total_tests) if total_tests > 0 else 0
        
        # Check quality score
        quality_score = quality_metrics.get('quality_score', 0)
        
        # Check performance score
        performance_score = performance_results.get('performance_score', 0)
        
        # Release criteria
        release_ready = (
            pass_rate >= 0.95 and           # 95% test pass rate
            quality_score >= 80 and           # 80% quality score
            performance_score >= 70 and           # 70% performance score
            not self._has_critical_issues(quality_metrics)  # No critical issues
        )
        
        return release_ready
    
    async def _execute_test_command(self, command: str) -> Dict[str, Any]:
        """Execute test command and return results"""
        
        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=300  # 5 minutes
            )
            
            stdout, stderr = await process.communicate()
            
            # Parse test output
            return self._parse_test_output(stdout, stderr)
            
        except asyncio.TimeoutError:
            return {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'error': 'Test execution timed out',
                'command': command
            }
        except Exception as e:
            return {
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'error': str(e),
                'command': command
            }
    
    async def _run_linter(self, linter: str, file_scope: List[str]) -> Dict[str, Any]:
        """Run linter on files"""
        
        command = f"{linter} {' '.join(file_scope)}"
        result = await self._execute_test_command(command)
        
        return {
            'linter': linter,
            'files_checked': file_scope,
            'issues_found': result.get('tests_failed', 0),
            'warnings': result.get('error', ''),
            'output': result
        }
    
    async def _run_security_scan(self, tool: str, file_scope: List[str]) -> Dict[str, Any]:
        """Run security scan on files"""
        
        command = f"{tool} {' '.join(file_scope)}"
        result = await self._execute_test_command(command)
        
        return {
            'tool': tool,
            'files_scanned': file_scope,
            'vulnerabilities_found': result.get('tests_failed', 0),
            'high_risk_issues': 0,  # TODO: Parse from output
            'output': result
        }
    
    async def _run_complexity_analysis(self, tool: str, file_scope: List[str]) -> Dict[str, Any]:
        """Run complexity analysis on files"""
        
        command = f"{tool} {' '.join(file_scope)}"
        result = await self._execute_test_command(command)
        
        return {
            'tool': tool,
            'files_analyzed': file_scope,
            'complexity_score': 0,  # TODO: Parse from output
            'maintainability_index': 0,
            'output': result
        }
    
    async def _run_benchmark(self, benchmark_name: str, config: Dict, file_scope: List[str]) -> Dict[str, Any]:
        """Run performance benchmark"""
        
        # Mock benchmark execution
        return {
            'benchmark': benchmark_name,
            'target': config.get('target', 0),
            'actual': 0,  # TODO: Actual benchmark execution
            'passed': config.get('target', 0) <= 0,  # Mock result
            'unit': config.get('unit', 'ms')
        }
    
    async def _run_python_tests(self, file_scope: List[str]) -> Dict[str, Any]:
        """Run Python tests"""
        
        test_files = [f for f in file_scope if f.endswith('.py') and 'test' in f]
        command = f"pytest {' '.join(test_files)} --verbose --tb=short"
        result = await self._execute_test_command(command)
        
        return {
            'framework': 'pytest',
            'files_tested': test_files,
            'tests_run': result.get('tests_run', 0),
            'tests_passed': result.get('tests_passed', 0),
            'tests_failed': result.get('tests_failed', 0),
            'coverage': result.get('coverage_percentage', 0)
        }
    
    async def _run_javascript_tests(self, file_scope: List[str]) -> Dict[str, Any]:
        """Run JavaScript/TypeScript tests"""
        
        test_files = [f for f in file_scope if f.endswith(('.js', '.jsx', '.ts', '.tsx')) and 'test' in f]
        command = f"npm test {' '.join(test_files)}"
        result = await self._execute_test_command(command)
        
        return {
            'framework': 'jest',
            'files_tested': test_files,
            'tests_run': result.get('tests_run', 0),
            'tests_passed': result.get('tests_passed', 0),
            'tests_failed': result.get('tests_failed', 0),
            'coverage': result.get('coverage_percentage', 0)
        }
    
    async def _run_java_tests(self, file_scope: List[str]) -> Dict[str, Any]:
        """Run Java tests"""
        
        test_files = [f for f in file_scope if f.endswith('.java') and 'test' in f]
        command = f"mvn test {' '.join(test_files)}"
        result = await self._execute_test_command(command)
        
        return {
            'framework': 'junit',
            'files_tested': test_files,
            'tests_run': result.get('tests_run', 0),
            'tests_passed': result.get('tests_passed', 0),
            'tests_failed': result.get('tests_failed', 0),
            'coverage': result.get('coverage_percentage', 0)
        }
    
    def _parse_test_output(self, stdout: str, stderr: str) -> Dict[str, int]:
        """Parse test output to extract metrics"""
        
        # Simple parsing - in practice, would be more sophisticated
        output = stdout + stderr
        
        # Look for test result patterns
        passed_pattern = r'(\d+) passed'
        failed_pattern = r'(\d+) failed'
        
        passed_matches = re.findall(passed_pattern, output)
        failed_matches = re.findall(failed_pattern, output)
        
        tests_passed = sum(int(match) for match in passed_matches)
        tests_failed = sum(int(match) for match in failed_matches)
        tests_run = tests_passed + tests_failed
        
        return {
            'tests_run': tests_run,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed
        }
    
    def _calculate_quality_score(self, metrics: Dict) -> int:
        """Calculate overall quality score"""
        
        score = 100  # Start with perfect score
        
        # Deduct for linting issues
        for linter_result in metrics.get('linting', {}).values():
            issues = linter_result.get('issues_found', 0)
            score -= min(issues * 2, 30)  # Max 30 points deduction
        
        # Deduct for security issues
        for security_result in metrics.get('security_scan', {}).values():
            vulnerabilities = security_result.get('vulnerabilities_found', 0)
            score -= min(vulnerabilities * 10, 40)  # Max 40 points deduction
        
        # Deduct for complexity
        for complexity_result in metrics.get('complexity_analysis', {}).values():
            complexity_score = complexity_result.get('complexity_score', 0)
            if complexity_score > 20:
                score -= min((complexity_score - 20) * 2, 20)  # Max 20 points deduction
        
        return max(score, 0)  # Ensure score doesn't go negative
    
    def _calculate_performance_score(self, metrics: Dict) -> int:
        """Calculate performance score"""
        
        score = 100  # Start with perfect score
        
        for benchmark_name, benchmark_result in metrics.items():
            target = benchmark_result.get('target', 0)
            actual = benchmark_result.get('actual', 0)
            
            if not benchmark_result.get('passed', True):
                # Calculate performance penalty
                if target > 0:
                    performance_ratio = actual / target
                    if performance_ratio > 1.2:  # 20% slower than target
                        score -= 20
                    elif performance_ratio > 1.1:  # 10% slower
                        score -= 10
                    elif performance_ratio > 1.05:  # 5% slower
                        score -= 5
        
        return max(score, 0)
    
    def _has_critical_issues(self, quality_metrics: Dict) -> bool:
        """Check for critical quality issues"""
        
        # Check for critical security issues
        for security_result in quality_metrics.get('security_scan', {}).values():
            high_risk = security_result.get('high_risk_issues', 0)
            if high_risk > 0:
                return True
        
        # Check for critical quality issues
        for linter_result in quality_metrics.get('linting', {}).values():
            issues = linter_result.get('issues_found', 0)
            if issues > 10:  # More than 10 linting issues
                return True
        
        return False
    
    def _identify_coverage_gaps(self, unit_results: Dict, integration_results: Dict) -> List[str]:
        """Identify coverage gaps"""
        
        gaps = []
        
        # Check for missing test types
        if unit_results.get('coverage_percentage', 0) < 80:
            gaps.append("Unit test coverage below 80%")
        
        if integration_results.get('coverage_percentage', 0) < 70:
            gaps.append("Integration test coverage below 70%")
        
        # Check for missing test files
        if not unit_results.get('test_suites'):
            gaps.append("No unit test suites found")
        
        if not integration_results.get('test_suites'):
            gaps.append("No integration test suites found")
        
        return gaps
    
    async def _get_file_content(self, file_path: str) -> str:
        """Get file content (mock implementation)"""
        # TODO: Implement actual file retrieval from storage
        return f"# Content of {file_path}\n# TODO: Load actual content"
