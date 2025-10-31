"""
Code Instrumenter - Injects coverage tracking into source code.

Supports:
- JavaScript/TypeScript (using Babel/Istanbul)
- Python (using Coverage.py hooks)
- Runtime injection without breaking original behavior
"""

import os
import ast
import hashlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from ..models import InstrumentedFile


@dataclass
class InstrumentationResult:
    """Result of code instrumentation."""
    instrumented_files: List[InstrumentedFile]
    coverage_map: Dict[str, Dict[int, str]]  # file_path -> {line_num -> coverage_id}
    failed_files: List[Tuple[str, str]]  # (file_path, error_message)


class CodeInstrumenter:
    """
    Instruments code for coverage tracking.

    Supports multiple languages with appropriate tooling:
    - JS/TS: Babel plugin + Istanbul
    - Python: AST transformation + Coverage.py
    """

    def __init__(self):
        """Initialize code instrumenter."""
        self.instrumented_files: Dict[str, InstrumentedFile] = {}
        self.coverage_map: Dict[str, Dict[int, str]] = {}

    async def instrument_files(
        self,
        file_paths: List[str],
        base_path: Optional[Path] = None
    ) -> InstrumentationResult:
        """
        Instrument multiple files for coverage tracking.

        Args:
            file_paths: List of file paths to instrument
            base_path: Base path for resolving relative paths

        Returns:
            InstrumentationResult with instrumented files
        """
        print(f"🔧 Instrumenting {len(file_paths)} files...")

        instrumented_files = []
        failed_files = []

        for file_path in file_paths:
            try:
                result = await self._instrument_file(file_path, base_path)
                if result:
                    instrumented_files.append(result)
                    print(f"   ✅ {file_path}")
                else:
                    failed_files.append((file_path, "Unsupported file type"))
                    print(f"   ⏭️  {file_path} (skipped)")
            except Exception as e:
                failed_files.append((file_path, str(e)))
                print(f"   ❌ {file_path}: {str(e)}")

        print(f"✅ Instrumentation complete:")
        print(f"   Success: {len(instrumented_files)}")
        print(f"   Failed: {len(failed_files)}")

        return InstrumentationResult(
            instrumented_files=instrumented_files,
            coverage_map=self.coverage_map,
            failed_files=failed_files
        )

    async def _instrument_file(
        self,
        file_path: str,
        base_path: Optional[Path]
    ) -> Optional[InstrumentedFile]:
        """Instrument a single file."""
        # Read original content
        full_path = Path(base_path) / file_path if base_path else Path(file_path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Determine language
        language = self._detect_language(file_path)

        # Instrument based on language
        if language == 'python':
            instrumented_content, source_map = self._instrument_python(
                original_content, file_path
            )
        elif language in ['javascript', 'typescript']:
            instrumented_content, source_map = self._instrument_javascript(
                original_content, file_path
            )
        else:
            return None

        return InstrumentedFile(
            file_path=file_path,
            original_content=original_content,
            instrumented_content=instrumented_content,
            source_map=source_map,
            language=language
        )

    def _instrument_python(
        self,
        code: str,
        file_path: str
    ) -> Tuple[str, Dict[int, int]]:
        """
        Instrument Python code using AST transformation.

        Injects coverage tracking calls at:
        - Function entry/exit
        - Branch points (if/elif/else)
        - Loop iterations
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {e}")

        # Transform AST to add coverage calls
        transformer = PythonCoverageTransformer(file_path)
        transformed_tree = transformer.visit(tree)

        # Generate instrumented code
        import astor
        try:
            instrumented_code = astor.to_source(transformed_tree)
        except:
            # Fallback: use ast.unparse (Python 3.9+)
            instrumented_code = ast.unparse(transformed_tree)

        return instrumented_code, transformer.source_map

    def _instrument_javascript(
        self,
        code: str,
        file_path: str
    ) -> Tuple[str, Dict[int, int]]:
        """
        Instrument JavaScript/TypeScript code.

        Uses a simplified approach since full Babel integration
        would require Node.js runtime.
        """
        # For now, use a simple line-by-line injection approach
        lines = code.split('\n')
        instrumented_lines = []
        source_map = {}

        for i, line in enumerate(lines, 1):
            # Add coverage tracking before executable statements
            if self._is_executable_js_line(line):
                coverage_id = self._generate_coverage_id(file_path, i)
                tracking_call = f"__coverage__['{coverage_id}']++;"
                instrumented_lines.append(tracking_call)
                source_map[len(instrumented_lines)] = i

            instrumented_lines.append(line)
            source_map[len(instrumented_lines)] = i

        # Add coverage object initialization at top
        init_code = """
if (typeof __coverage__ === 'undefined') {
    globalThis.__coverage__ = {};
}
"""
        instrumented_code = init_code + '\n'.join(instrumented_lines)

        return instrumented_code, source_map

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.rb': 'ruby'
        }

        return language_map.get(ext, 'unknown')

    def _is_executable_js_line(self, line: str) -> bool:
        """Check if JavaScript line is executable (not comment/empty)."""
        stripped = line.strip()

        if not stripped:
            return False
        if stripped.startswith('//'):
            return False
        if stripped.startswith('/*'):
            return False
        if stripped.startswith('*'):
            return False

        # Simple heuristic: contains statement-like keywords
        keywords = ['function', 'const', 'let', 'var', 'if', 'for', 'while',
                   'return', 'throw', 'class', 'import', 'export']

        return any(keyword in stripped for keyword in keywords)

    def _generate_coverage_id(self, file_path: str, line_number: int) -> str:
        """Generate unique coverage ID for file:line."""
        content = f"{file_path}:{line_number}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:12]


class PythonCoverageTransformer(ast.NodeTransformer):
    """AST transformer to inject coverage tracking into Python code."""

    def __init__(self, file_path: str):
        """
        Initialize transformer.

        Args:
            file_path: Path to file being instrumented
        """
        self.file_path = file_path
        self.source_map: Dict[int, int] = {}
        self.coverage_counter = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Inject coverage tracking at function entry."""
        # Generate coverage ID
        coverage_id = self._generate_coverage_id(node.lineno)

        # Create tracking call: __coverage__[coverage_id] += 1
        tracking_call = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='__track_coverage__', ctx=ast.Load()),
                args=[ast.Constant(value=coverage_id)],
                keywords=[]
            )
        )

        # Insert at beginning of function body
        node.body.insert(0, tracking_call)

        # Continue traversing
        self.generic_visit(node)

        return node

    def visit_If(self, node: ast.If) -> ast.If:
        """Inject coverage tracking at branches."""
        # Track if condition
        if_coverage_id = self._generate_coverage_id(node.lineno)
        if_tracking = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='__track_branch__', ctx=ast.Load()),
                args=[
                    ast.Constant(value=if_coverage_id),
                    ast.Constant(value='if_true')
                ],
                keywords=[]
            )
        )
        node.body.insert(0, if_tracking)

        # Track else branch if exists
        if node.orelse:
            else_coverage_id = self._generate_coverage_id(node.lineno)
            else_tracking = ast.Expr(
                value=ast.Call(
                    func=ast.Name(id='__track_branch__', ctx=ast.Load()),
                    args=[
                        ast.Constant(value=else_coverage_id),
                        ast.Constant(value='if_false')
                    ],
                    keywords=[]
                )
            )
            node.orelse.insert(0, else_tracking)

        self.generic_visit(node)
        return node

    def _generate_coverage_id(self, line_number: int) -> str:
        """Generate unique coverage ID."""
        self.coverage_counter += 1
        coverage_id = f"{self.file_path}:{line_number}:{self.coverage_counter}"
        self.source_map[self.coverage_counter] = line_number
        return coverage_id
