"""
Semantic Indexing Service
Handles code chunking, embedding generation, and vector similarity search
"""

import asyncio
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import openai
from openai import AsyncOpenAI
import tiktoken

from services.api.config import settings
from services.api.database import AsyncSessionLocal
from services.agents.utils.file_analyzer import FileAnalyzer


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata"""
    file_path: str
    chunk_type: str
    content: str
    start_line: int
    end_line: int
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    metadata: Dict[str, Any]


@dataclass
class SearchResult:
    """Represents a semantic search result"""
    file_path: str
    content: str
    similarity_score: float
    chunk_type: str
    language: str
    context: Dict[str, Any]


class SemanticIndexService:
    """Handles semantic indexing and vector similarity search"""
    
    def __init__(self):
        self.file_analyzer = FileAnalyzer()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.embedding_model = "text-embedding-ada-002"
        self.max_tokens = 8191  # ada-002 limit
        self.chunk_size = 500  # Max characters per chunk
        self.chunk_overlap = 50  # Overlap between chunks
        
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.encoding_for_model(self.embedding_model)
    
    async def index_repository(self, repository_id: str, file_tree: Dict) -> Dict[str, Any]:
        """Index all code files in a repository"""
        
        files = file_tree.get('files', [])
        chunks_created = 0
        embeddings_generated = 0
        
        # Filter files for indexing
        indexable_files = self._filter_indexable_files(files)
        
        for file_info in indexable_files:
            try:
                # Chunk the file content
                chunks = await self._chunk_file(file_info)
                
                # Generate embeddings for chunks
                for chunk in chunks:
                    embedding = await self._generate_embedding(chunk.content)
                    
                    if embedding:
                        await self._store_chunk(repository_id, chunk, embedding)
                        embeddings_generated += 1
                
                chunks_created += len(chunks)
                
            except Exception as e:
                print(f"Failed to index file {file_info['path']}: {e}")
        
        return {
            'repository_id': repository_id,
            'files_processed': len(indexable_files),
            'chunks_created': chunks_created,
            'embeddings_generated': embeddings_generated,
            'indexed_at': '2024-01-16T22:30:00Z'
        }
    
    async def search_similar_code(
        self, 
        query: str, 
        repository_ids: Optional[List[str]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[SearchResult]:
        """Search for semantically similar code"""
        
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # Convert to numpy array for PostgreSQL
            query_vector = np.array(query_embedding).tolist()
            
            # Search using pgvector
            async with AsyncSessionLocal() as db:
                # Build the SQL query for vector similarity
                sql_query = text("""
                    SELECT 
                        file_path,
                        content,
                        chunk_type,
                        language,
                        metadata,
                        1 - (embedding <=> :query_vector) as similarity_score
                    FROM code_chunks 
                    WHERE (:repository_ids IS NULL OR repository_id = ANY(:repository_ids))
                    AND 1 - (embedding <=> :query_vector) > :similarity_threshold
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                """)
                
                result = await db.execute(sql_query, {
                    'query_vector': query_vector,
                    'repository_ids': repository_ids,
                    'similarity_threshold': similarity_threshold,
                    'limit': limit
                })
                
                rows = result.fetchall()
                
                # Convert to SearchResult objects
                search_results = []
                for row in rows:
                    search_results.append(SearchResult(
                        file_path=row.file_path,
                        content=row.content,
                        similarity_score=float(row.similarity_score),
                        chunk_type=row.chunk_type,
                        language=row.language,
                        context=row.metadata or {}
                    ))
                
                return search_results
                
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
    
    async def find_related_files(
        self, 
        file_path: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find files semantically related to a given file"""
        
        try:
            async with AsyncSessionLocal() as db:
                # Get embedding for the target file
                target_query = text("""
                    SELECT embedding FROM code_chunks 
                    WHERE file_path = :file_path 
                    LIMIT 1
                """)
                
                target_result = await db.execute(target_query, {'file_path': file_path})
                target_row = target_result.fetchone()
                
                if not target_row:
                    return []
                
                target_embedding = target_row.embedding
                
                # Find similar files
                similar_query = text("""
                    SELECT 
                        file_path,
                        chunk_type,
                        language,
                        1 - (embedding <=> :target_embedding) as similarity_score
                    FROM code_chunks 
                    WHERE file_path != :file_path
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                """)
                
                similar_result = await db.execute(similar_query, {
                    'target_embedding': target_embedding.tolist(),
                    'file_path': file_path,
                    'limit': limit
                })
                
                similar_rows = similar_result.fetchall()
                
                return [
                    {
                        'file_path': row.file_path,
                        'chunk_type': row.chunk_type,
                        'language': row.language,
                        'similarity_score': float(row.similarity_score)
                    }
                    for row in similar_rows
                ]
                
        except Exception as e:
            print(f"Related files search failed: {e}")
            return []
    
    async def _chunk_file(self, file_info: Dict) -> List[CodeChunk]:
        """Chunk a file into semantically meaningful pieces"""
        
        content = file_info.get('content_preview', '')
        file_path = file_info['path']
        language = file_info.get('language', 'unknown')
        
        if not content or len(content) < 50:
            return []
        
        # Determine chunking strategy based on language
        if language in ['javascript', 'typescript', 'python', 'java']:
            chunks = self._chunk_code_by_structure(content, file_path, language)
        else:
            chunks = self._chunk_code_by_size(content, file_path, language)
        
        return chunks
    
    def _chunk_code_by_structure(self, content: str, file_path: str, language: str) -> List[CodeChunk]:
        """Chunk code based on functions, classes, and logical blocks"""
        
        chunks = []
        lines = content.split('\n')
        
        # Language-specific patterns
        if language == 'python':
            chunks.extend(self._chunk_python_code(lines, file_path))
        elif language in ['javascript', 'typescript']:
            chunks.extend(self._chunk_javascript_code(lines, file_path))
        elif language == 'java':
            chunks.extend(self._chunk_java_code(lines, file_path))
        else:
            # Fallback to size-based chunking
            chunks.extend(self._chunk_code_by_size(content, file_path, language))
        
        return chunks
    
    def _chunk_python_code(self, lines: List[str], file_path: str) -> List[CodeChunk]:
        """Chunk Python code by functions and classes"""
        
        chunks = []
        current_chunk = []
        current_start = 0
        current_line = 0
        indent_level = 0
        in_function = False
        in_class = False
        
        for i, line in enumerate(lines):
            current_line = i + 1
            
            # Track indentation
            if line.strip():
                new_indent = len(line) - len(line.lstrip())
                if new_indent < indent_level and not in_function and not in_class:
                    # End of block
                    if current_chunk:
                        chunks.append(self._create_chunk(
                            '\n'.join(current_chunk), file_path, 'python',
                            current_start, current_line - 1, current_chunk
                        ))
                        current_chunk = []
                    current_start = current_line
                indent_level = new_indent
            
            # Detect function/class definitions
            stripped = line.strip()
            if (stripped.startswith('def ') or stripped.startswith('async def ')) and not in_class:
                in_function = True
            elif stripped.startswith('class '):
                in_class = True
            elif stripped and not line.startswith(' ') and indent_level == 0:
                in_function = False
                in_class = False
            
            current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                '\n'.join(current_chunk), file_path, 'python',
                current_start, current_line, current_chunk
            ))
        
        return chunks
    
    def _chunk_javascript_code(self, lines: List[str], file_path: str) -> List[CodeChunk]:
        """Chunk JavaScript/TypeScript code by functions and modules"""
        
        chunks = []
        current_chunk = []
        current_start = 0
        current_line = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            current_line = i + 1
            
            # Track braces for block detection
            brace_count += line.count('{') - line.count('}')
            
            # Start new chunk on function/module boundaries
            stripped = line.strip()
            if (stripped.startswith('function ') or 
                stripped.startswith('const ') and '=' in stripped or
                stripped.startswith('class ') or
                (brace_count == 0 and current_chunk and not stripped.startswith('//'))):
                
                if current_chunk:
                    chunks.append(self._create_chunk(
                        '\n'.join(current_chunk), file_path, 'javascript',
                        current_start, current_line - 1, current_chunk
                    ))
                    current_chunk = []
                    current_start = current_line
            
            current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                '\n'.join(current_chunk), file_path, 'javascript',
                current_start, current_line, current_chunk
            ))
        
        return chunks
    
    def _chunk_java_code(self, lines: List[str], file_path: str) -> List[CodeChunk]:
        """Chunk Java code by classes and methods"""
        
        chunks = []
        current_chunk = []
        current_start = 0
        current_line = 0
        brace_count = 0
        
        for i, line in enumerate(lines):
            current_line = i + 1
            
            # Track braces
            brace_count += line.count('{') - line.count('}')
            
            # Start new chunk on class/method boundaries
            stripped = line.strip()
            if (stripped.startswith('public class ') or 
                stripped.startswith('private class ') or
                stripped.startswith('public ') and '(' in stripped or
                (brace_count == 0 and current_chunk and not stripped.startswith('//'))):
                
                if current_chunk:
                    chunks.append(self._create_chunk(
                        '\n'.join(current_chunk), file_path, 'java',
                        current_start, current_line - 1, current_chunk
                    ))
                    current_chunk = []
                    current_start = current_line
            
            current_chunk.append(line)
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(
                '\n'.join(current_chunk), file_path, 'java',
                current_start, current_line, current_chunk
            ))
        
        return chunks
    
    def _chunk_code_by_size(self, content: str, file_path: str, language: str) -> List[CodeChunk]:
        """Chunk code by fixed size with overlap"""
        
        chunks = []
        content_length = len(content)
        
        for start in range(0, content_length, self.chunk_size - self.chunk_overlap):
            end = min(start + self.chunk_size, content_length)
            chunk_content = content[start:end]
            
            # Find line numbers
            lines_before = content[:start].count('\n')
            start_line = lines_before + 1
            lines_in_chunk = chunk_content.count('\n')
            end_line = start_line + lines_in_chunk
            
            chunks.append(self._create_chunk(
                chunk_content, file_path, language,
                start_line, end_line, [chunk_content]
            ))
        
        return chunks
    
    def _create_chunk(
        self, 
        content: str, 
        file_path: str, 
        language: str,
        start_line: int, 
        end_line: int,
        raw_lines: List[str]
    ) -> CodeChunk:
        """Create a CodeChunk object"""
        
        # Extract functions, classes, and imports
        functions = self._extract_functions(content, language)
        classes = self._extract_classes(content, language)
        imports = self._extract_imports(content, language)
        
        # Determine chunk type
        chunk_type = self._determine_chunk_type(content, functions, classes)
        
        return CodeChunk(
            file_path=file_path,
            chunk_type=chunk_type,
            content=content,
            start_line=start_line,
            end_line=end_line,
            language=language,
            functions=functions,
            classes=classes,
            imports=imports,
            metadata={
                'line_count': content.count('\n') + 1,
                'char_count': len(content),
                'hash': hashlib.md5(content.encode()).hexdigest()
            }
        )
    
    def _extract_functions(self, content: str, language: str) -> List[str]:
        """Extract function names from code"""
        functions = []
        
        if language == 'python':
            pattern = r'(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        elif language in ['javascript', 'typescript']:
            pattern = r'(?:async\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(|const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:function|\([^)]*\)\s*=>)'
        elif language == 'java':
            pattern = r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?[a-zA-Z_][a-zA-Z0-9_<>]*\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        else:
            return []
        
        matches = re.findall(pattern, content)
        return [match[0] or match[1] for match in matches if match[0] or match[1]]
    
    def _extract_classes(self, content: str, language: str) -> List[str]:
        """Extract class names from code"""
        classes = []
        
        if language == 'python':
            pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\([^)]*\))?\s*:'
        elif language == 'java':
            pattern = r'(?:public\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:extends\s+[a-zA-Z_][a-zA-Z0-9_]*)?\s*\{?'
        elif language in ['javascript', 'typescript']:
            pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:extends\s+[a-zA-Z_][a-zA-Z0-9_]*)?\s*\{?'
        else:
            return []
        
        matches = re.findall(pattern, content)
        return [match for match in matches]
    
    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if language == 'python':
            patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            ]
        elif language in ['javascript', 'typescript']:
            patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]'
            ]
        elif language == 'java':
            patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.*?);',
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.*?);'
            ]
        else:
            return []
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        return list(set(imports))
    
    def _determine_chunk_type(self, content: str, functions: List[str], classes: List[str]) -> str:
        """Determine the type of code chunk"""
        if classes:
            return 'class'
        elif functions:
            return 'function'
        elif any(keyword in content.lower() for keyword in ['config', 'settings', 'env']):
            return 'config'
        elif any(keyword in content.lower() for keyword in ['test', 'spec']):
            return 'test'
        else:
            return 'general'
    
    def _filter_indexable_files(self, files: List[Dict]) -> List[Dict]:
        """Filter files that should be indexed"""
        indexable_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.swift',
            '.kt', '.scala', '.sql', '.html', '.css', '.scss', '.less',
            '.json', '.yaml', '.yml', '.xml', '.sh', '.bash', '.zsh'
        }
        
        exclude_patterns = [
            'test', 'spec', 'mock', 'fixture', 'node_modules', '__pycache__',
            '.git', 'dist', 'build', 'target', 'coverage', '.vscode', '.idea'
        ]
        
        indexable_files = []
        for file_info in files:
            file_path = file_info['path'].lower()
            extension = file_info.get('extension', '').lower()
            
            # Check extension
            if extension not in indexable_extensions:
                continue
            
            # Check exclude patterns
            if any(pattern in file_path for pattern in exclude_patterns):
                continue
            
            # Check file size (skip very large files)
            if file_info.get('size', 0) > 1024 * 1024:  # 1MB
                continue
            
            indexable_files.append(file_info)
        
        return indexable_files
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI"""
        if not self.client:
            return None
        
        try:
            # Check token count
            tokens = len(self.tokenizer.encode(text))
            if tokens > self.max_tokens:
                # Truncate text if too long
                text = self.tokenizer.decode(self.tokenizer.encode(text)[:self.max_tokens])
            
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return None
    
    async def _store_chunk(self, repository_id: str, chunk: CodeChunk, embedding: List[float]):
        """Store chunk and embedding in database"""
        try:
            async with AsyncSessionLocal() as db:
                # Convert embedding to PostgreSQL vector format
                embedding_str = str(embedding)
                
                # Insert chunk
                insert_query = text("""
                    INSERT INTO code_chunks (
                        repository_id, file_path, chunk_type, content, 
                        start_line, end_line, language, functions, 
                        classes, imports, metadata, embedding
                    ) VALUES (
                        :repository_id, :file_path, :chunk_type, :content,
                        :start_line, :end_line, :language, :functions,
                        :classes, :imports, :metadata, :embedding
                    )
                """)
                
                await db.execute(insert_query, {
                    'repository_id': repository_id,
                    'file_path': chunk.file_path,
                    'chunk_type': chunk.chunk_type,
                    'content': chunk.content,
                    'start_line': chunk.start_line,
                    'end_line': chunk.end_line,
                    'language': chunk.language,
                    'functions': chunk.functions,
                    'classes': chunk.classes,
                    'imports': chunk.imports,
                    'metadata': chunk.metadata,
                    'embedding': embedding_str
                })
                
                await db.commit()
                
        except Exception as e:
            print(f"Failed to store chunk: {e}")
            # Don't raise - continue with other chunks
