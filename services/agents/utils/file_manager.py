"""
File Management Utilities
Handles large file splitting, chunked editing, and manageable file operations
"""

import os
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio
import aiofiles


@dataclass
class FileChunk:
    """Represents a chunk of a large file"""
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    content: str
    hash: str
    size: int
    metadata: Dict[str, Any]


@dataclass
class FileOperation:
    """Represents a file operation with context"""
    operation_id: str
    type: str  # 'create', 'update', 'delete'
    file_path: str
    chunks: List[FileChunk]
    context: Dict[str, Any]
    dependencies: List[str]
    rollback_info: Dict[str, Any]


class FileManager:
    """Manages large files through chunking and atomic operations"""
    
    def __init__(self, max_file_size: int = 10000, max_chunk_size: int = 2000):
        self.max_file_size = max_file_size
        self.max_chunk_size = max_chunk_size
        self.temp_dir = Path("/tmp/enterprise-ai-chunks")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Track active operations
        self.active_operations: Dict[str, FileOperation] = {}
        
        # File size thresholds for different strategies
        self.size_thresholds = {
            'small': 1000,      # < 1KB - direct edit
            'medium': 5000,     # 1KB - 5KB - chunked edit
            'large': 20000,     # 5KB - 20KB - split file
            'xlarge': 100000    # > 20KB - specialized handling
        }
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze file and recommend management strategy"""
        
        try:
            # Get file info
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {'error': f'File {file_path} does not exist'}
            
            file_size = file_path_obj.stat().st_size
            line_count = 0
            
            # Count lines if it's a text file
            if self._is_text_file(file_path):
                async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = await f.read()
                    line_count = len(content.split('\n'))
            
            # Determine strategy
            strategy = self._determine_strategy(file_size, line_count)
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'line_count': line_count,
                'strategy': strategy,
                'recommended_action': self._get_recommended_action(strategy),
                'estimated_chunks': self._estimate_chunk_count(file_size, strategy),
                'complexity': self._assess_file_complexity(file_size, line_count)
            }
            
        except Exception as e:
            return {'error': f'Failed to analyze file {file_path}: {str(e)}'}
    
    async def create_file_operation(
        self, 
        operation_type: str, 
        file_path: str, 
        content: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Create a new file operation"""
        
        operation_id = hashlib.md5(f"{file_path}_{operation_type}_{len(content)}".encode()).hexdigest()
        
        # Analyze file
        analysis = await self.analyze_file(file_path)
        
        if analysis.get('strategy') == 'direct':
            # Direct operation for small files
            chunk = FileChunk(
                chunk_id=f"{operation_id}_chunk_0",
                file_path=file_path,
                start_line=1,
                end_line=analysis.get('line_count', 0),
                content=content,
                hash=hashlib.md5(content.encode()).hexdigest(),
                size=len(content),
                metadata={'operation_type': operation_type}
            )
            
            operation = FileOperation(
                operation_id=operation_id,
                type=operation_type,
                file_path=file_path,
                chunks=[chunk],
                context=context or {},
                dependencies=[],
                rollback_info={'original_content': content}
            )
        
        else:
            # Chunked operation for larger files
            chunks = await self._chunk_content(content, file_path, analysis)
            operation = FileOperation(
                operation_id=operation_id,
                type=operation_type,
                file_path=file_path,
                chunks=chunks,
                context=context or {},
                dependencies=self._extract_dependencies(content),
                rollback_info={'chunk_count': len(chunks)}
            )
        
        self.active_operations[operation_id] = operation
        return operation_id
    
    async def execute_operation(self, operation_id: str) -> Dict[str, Any]:
        """Execute a file operation atomically"""
        
        if operation_id not in self.active_operations:
            return {'error': f'Operation {operation_id} not found'}
        
        operation = self.active_operations[operation_id]
        
        try:
            if operation.type == 'create':
                result = await self._execute_create_operation(operation)
            elif operation.type == 'update':
                result = await self._execute_update_operation(operation)
            elif operation.type == 'delete':
                result = await self._execute_delete_operation(operation)
            else:
                return {'error': f'Unknown operation type: {operation.type}'}
            
            # Clean up operation
            del self.active_operations[operation_id]
            
            return result
            
        except Exception as e:
            return {'error': f'Operation {operation_id} failed: {str(e)}'}
    
    async def rollback_operation(self, operation_id: str) -> Dict[str, Any]:
        """Rollback a file operation"""
        
        if operation_id not in self.active_operations:
            return {'error': f'Operation {operation_id} not found'}
        
        operation = self.active_operations[operation_id]
        
        try:
            if operation.type == 'update':
                result = await self._rollback_update_operation(operation)
            elif operation.type == 'create':
                result = await self._rollback_create_operation(operation)
            else:
                return {'error': f'Cannot rollback operation type: {operation.type}'}
            
            return result
            
        except Exception as e:
            return {'error': f'Rollback {operation_id} failed: {str(e)}'}
    
    async def get_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """Get status of an active operation"""
        
        if operation_id not in self.active_operations:
            return {'error': f'Operation {operation_id} not found'}
        
        operation = self.active_operations[operation_id]
        
        return {
            'operation_id': operation_id,
            'type': operation.type,
            'file_path': operation.file_path,
            'status': 'active',
            'chunk_count': len(operation.chunks),
            'chunks_processed': len([c for c in operation.chunks if hasattr(c, 'processed')]),
            'estimated_completion': self._estimate_completion_time(operation)
        }
    
    def _determine_strategy(self, file_size: int, line_count: int) -> str:
        """Determine the best strategy for file management"""
        
        if file_size < self.size_thresholds['small']:
            return 'direct'
        elif file_size < self.size_thresholds['medium']:
            return 'chunked'
        elif file_size < self.size_thresholds['large']:
            return 'split'
        else:
            return 'specialized'
    
    def _get_recommended_action(self, strategy: str) -> str:
        """Get recommended action based on strategy"""
        
        actions = {
            'direct': 'Edit file directly - small and manageable',
            'chunked': 'Chunk into sections for medium files - maintain context',
            'split': 'Split into multiple files for large files - improve maintainability',
            'specialized': 'Use specialized tools for very large files - consider refactoring'
        }
        
        return actions.get(strategy, 'Unknown strategy')
    
    def _estimate_chunk_count(self, file_size: int, strategy: str) -> int:
        """Estimate number of chunks needed"""
        
        if strategy == 'direct':
            return 1
        elif strategy == 'chunked':
            return max(2, file_size // self.max_chunk_size)
        elif strategy == 'split':
            return max(3, file_size // self.max_file_size)
        else:
            return 5  # Default for specialized
    
    def _assess_file_complexity(self, file_size: int, line_count: int) -> str:
        """Assess file complexity"""
        
        if line_count > 1000 or file_size > 50000:
            return 'high'
        elif line_count > 500 or file_size > 20000:
            return 'medium'
        elif line_count > 100 or file_size > 5000:
            return 'low'
        else:
            return 'minimal'
    
    async def _chunk_content(self, content: str, file_path: str, analysis: Dict) -> List[FileChunk]:
        """Chunk content into manageable pieces"""
        
        chunks = []
        lines = content.split('\n')
        total_lines = len(lines)
        
        strategy = analysis.get('strategy', 'chunked')
        chunk_size = self.max_chunk_size if strategy == 'chunked' else self.max_file_size
        
        for i in range(0, total_lines, chunk_size):
            start_line = i + 1
            end_line = min(i + chunk_size, total_lines)
            chunk_lines = lines[i:end_line]
            chunk_content = '\n'.join(chunk_lines)
            
            chunk = FileChunk(
                chunk_id=hashlib.md5(f"{file_path}_{i}".encode()).hexdigest(),
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                content=chunk_content,
                hash=hashlib.md5(chunk_content.encode()).hexdigest(),
                size=len(chunk_content),
                metadata={
                    'chunk_index': i // chunk_size,
                    'total_chunks': (total_lines + chunk_size - 1) // chunk_size + 1,
                    'strategy': strategy
                }
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from content"""
        
        dependencies = []
        
        # Common import patterns
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
            r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
            r'require\s*\(\s*["\']([^"\']+)["\']',
            r'import\s+["\']([^"\']+)["\']'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                dep = match[1] if len(match) > 1 else match[0]
                if dep and dep not in dependencies:
                    dependencies.append(dep)
        
        return dependencies
    
    async def _execute_create_operation(self, operation: FileOperation) -> Dict[str, Any]:
        """Execute file creation operation"""
        
        try:
            # Ensure directory exists
            file_path = Path(operation.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file atomically
            temp_path = self.temp_dir / f"{operation.operation_id}_temp"
            
            async with aiofiles.open(temp_path, 'w', encoding='utf-8') as f:
                await f.write(operation.chunks[0].content)
            
            # Atomic move
            temp_path.rename(operation.file_path)
            
            return {
                'success': True,
                'file_path': operation.file_path,
                'size': sum(c.size for c in operation.chunks),
                'chunks_written': len(operation.chunks)
            }
            
        except Exception as e:
            return {'error': f'Create operation failed: {str(e)}'}
    
    async def _execute_update_operation(self, operation: FileOperation) -> Dict[str, Any]:
        """Execute file update operation with chunking"""
        
        try:
            # Read original file
            original_content = await self._read_file_content(operation.file_path)
            
            # Apply changes chunk by chunk
            updated_content = original_content
            chunks_processed = 0
            
            for chunk in operation.chunks:
                # Find chunk location in original content
                lines = updated_content.split('\n')
                
                # Replace lines in chunk range
                start_idx = chunk.start_line - 1
                end_idx = min(chunk.end_line, len(lines))
                
                # Validate chunk boundaries
                if start_idx < len(lines) and end_idx <= len(lines):
                    chunk_lines = chunk.content.split('\n')
                    
                    # Ensure we don't exceed original file bounds
                    if end_idx - start_idx >= len(chunk_lines):
                        chunk_lines = chunk_lines[:end_idx - start_idx]
                    
                    lines[start_idx:end_idx] = chunk_lines
                    updated_content = '\n'.join(lines)
                    chunks_processed += 1
            
            # Write updated content
            await self._write_file_content(operation.file_path, updated_content)
            
            return {
                'success': True,
                'file_path': operation.file_path,
                'chunks_processed': chunks_processed,
                'total_chunks': len(operation.chunks)
            }
            
        except Exception as e:
            return {'error': f'Update operation failed: {str(e)}'}
    
    async def _execute_delete_operation(self, operation: FileOperation) -> Dict[str, Any]:
        """Execute file deletion operation"""
        
        try:
            file_path = Path(operation.file_path)
            
            if file_path.exists():
                # Move to temp first, then delete
                temp_path = self.temp_dir / f"{operation.operation_id}_delete"
                file_path.rename(temp_path)
                temp_path.unlink()
                
                return {
                    'success': True,
                    'file_path': operation.file_path,
                    'deleted': True
                }
            else:
                return {
                    'success': True,
                    'file_path': operation.file_path,
                    'deleted': False,
                    'message': 'File does not exist'
                }
                
        except Exception as e:
            return {'error': f'Delete operation failed: {str(e)}'}
    
    async def _rollback_update_operation(self, operation: FileOperation) -> Dict[str, Any]:
        """Rollback an update operation"""
        
        try:
            original_content = operation.rollback_info.get('original_content')
            if original_content:
                await self._write_file_content(operation.file_path, original_content)
                
                return {
                    'success': True,
                    'file_path': operation.file_path,
                    'rolled_back': True
                }
            else:
                return {
                    'success': False,
                    'message': 'No original content available for rollback'
                }
                
        except Exception as e:
            return {'error': f'Rollback failed: {str(e)}'}
    
    async def _rollback_create_operation(self, operation: FileOperation) -> Dict[str, Any]:
        """Rollback a create operation (delete the file)"""
        
        try:
            file_path = Path(operation.file_path)
            
            if file_path.exists():
                file_path.unlink()
                
                return {
                    'success': True,
                    'file_path': operation.file_path,
                    'deleted': True
                }
            else:
                return {
                    'success': True,
                    'file_path': operation.file_path,
                    'deleted': False,
                    'message': 'File does not exist'
                }
                
        except Exception as e:
            return {'error': f'Rollback failed: {str(e)}'}
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file"""
        
        text_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.cpp', '.c', '.h',
            '.css', '.scss', '.less', '.html', '.xml', '.json', '.yaml', '.yml',
            '.md', '.txt', '.sql', '.sh', '.bash', '.zsh'
        }
        
        return Path(file_path).suffix.lower() in text_extensions
    
    async def _read_file_content(self, file_path: str) -> str:
        """Read file content"""
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return await f.read()
        except Exception:
            return ''
    
    async def _write_file_content(self, file_path: str, content: str):
        """Write file content"""
        
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
        except Exception as e:
            raise e
    
    def _estimate_completion_time(self, operation: FileOperation) -> float:
        """Estimate operation completion time in seconds"""
        
        total_size = sum(c.size for c in operation.chunks)
        
        # Base processing rate: 1000 characters per second
        base_rate = 1000
        
        # Adjust based on operation type
        if operation.type == 'create':
            multiplier = 1.0
        elif operation.type == 'update':
            multiplier = 1.5  # Updates take longer
        elif operation.type == 'delete':
            multiplier = 0.5
        else:
            multiplier = 1.0
        
        return (total_size / base_rate) * multiplier
    
    def get_active_operations(self) -> List[Dict[str, Any]]:
        """Get all active operations"""
        
        return [
            {
                'operation_id': op_id,
                'type': op.type,
                'file_path': op.file_path,
                'status': 'active',
                'chunk_count': len(op.chunks),
                'created_at': '2024-01-16T22:30:00Z'  # TODO: Track actual creation time
            }
            for op_id, op in self.active_operations.items()
        ]
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass
