#!/usr/bin/env python3
"""
Code Simplifier Tool for Consciousness System Environment

This tool analyzes Python code for complexity and provides suggestions
for simplification. It can identify:
- Overly complex functions
- Deeply nested code
- Redundant patterns
- Opportunities for refactoring

Usage:
    python -m tools.code_simplifier <file_or_directory>
    python -m tools.code_simplifier --analyze phases/
    python -m tools.code_simplifier --suggest appendices/appendix_a_base_simulation.py
"""

import ast
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any


@dataclass
class ComplexityMetrics:
    """Metrics for code complexity analysis."""
    cyclomatic_complexity: int = 0
    max_nesting_depth: int = 0
    num_functions: int = 0
    num_classes: int = 0
    lines_of_code: int = 0
    num_imports: int = 0
    num_variables: int = 0
    long_functions: List[Tuple[str, int]] = field(default_factory=list)
    deeply_nested: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class SimplificationSuggestion:
    """A suggestion for code simplification."""
    line_number: int
    original_code: str
    suggestion: str
    category: str  # 'refactor', 'simplify', 'extract', 'remove'
    priority: str  # 'high', 'medium', 'low'


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate code complexity metrics."""

    def __init__(self):
        self.complexity = 1  # Base complexity
        self.current_depth = 0
        self.max_depth = 0
        self.function_complexities: Dict[str, int] = {}
        self.function_lines: Dict[str, int] = {}
        self.current_function: Optional[str] = None
        self.function_nesting: Dict[str, int] = {}

    def _increment_complexity(self):
        self.complexity += 1
        if self.current_function:
            self.function_complexities[self.current_function] = \
                self.function_complexities.get(self.current_function, 1) + 1

    def _track_depth(self):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        if self.current_function:
            self.function_nesting[self.current_function] = max(
                self.function_nesting.get(self.current_function, 0),
                self.current_depth
            )

    def _untrack_depth(self):
        self.current_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prev_function = self.current_function
        self.current_function = node.name
        self.function_complexities[node.name] = 1
        self.function_lines[node.name] = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        self.function_nesting[node.name] = 0
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore

    def visit_If(self, node: ast.If) -> None:
        self._increment_complexity()
        self._track_depth()
        self.generic_visit(node)
        self._untrack_depth()

    def visit_For(self, node: ast.For) -> None:
        self._increment_complexity()
        self._track_depth()
        self.generic_visit(node)
        self._untrack_depth()

    def visit_While(self, node: ast.While) -> None:
        self._increment_complexity()
        self._track_depth()
        self.generic_visit(node)
        self._untrack_depth()

    def visit_Try(self, node: ast.Try) -> None:
        self._increment_complexity()
        self._track_depth()
        self.generic_visit(node)
        self._untrack_depth()

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._increment_complexity()
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self._track_depth()
        self.generic_visit(node)
        self._untrack_depth()

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each 'and'/'or' adds complexity
        self.complexity += len(node.values) - 1
        if self.current_function:
            self.function_complexities[self.current_function] = \
                self.function_complexities.get(self.current_function, 1) + len(node.values) - 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        for _ in node.generators:
            self._increment_complexity()
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        for _ in node.generators:
            self._increment_complexity()
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._increment_complexity()
        self.generic_visit(node)


class SimplificationAnalyzer(ast.NodeVisitor):
    """Analyzes code and suggests simplifications."""

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.suggestions: List[SimplificationSuggestion] = []
        self.current_function: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.current_function = node.name

        # Check for long functions (>50 lines)
        func_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        if func_lines > 50:
            self.suggestions.append(SimplificationSuggestion(
                line_number=node.lineno,
                original_code=f"def {node.name}(...): # {func_lines} lines",
                suggestion=f"Function '{node.name}' has {func_lines} lines. Consider breaking it into smaller functions.",
                category='extract',
                priority='high' if func_lines > 100 else 'medium'
            ))

        # Check for too many parameters
        num_params = len(node.args.args)
        if num_params > 5:
            self.suggestions.append(SimplificationSuggestion(
                line_number=node.lineno,
                original_code=f"def {node.name}({num_params} params)",
                suggestion=f"Function '{node.name}' has {num_params} parameters. Consider using a dataclass or config object.",
                category='refactor',
                priority='medium'
            ))

        self.generic_visit(node)
        self.current_function = None

    def visit_If(self, node: ast.If) -> None:
        # Check for deeply nested if statements
        depth = self._get_nesting_depth(node)
        if depth > 3:
            line = self.source_lines[node.lineno - 1].strip() if node.lineno <= len(self.source_lines) else ""
            self.suggestions.append(SimplificationSuggestion(
                line_number=node.lineno,
                original_code=line[:60] + "..." if len(line) > 60 else line,
                suggestion="Deeply nested if statement. Consider early returns or extracting to a function.",
                category='simplify',
                priority='medium'
            ))

        # Check for redundant boolean comparisons
        if isinstance(node.test, ast.Compare):
            if len(node.test.comparators) == 1:
                if isinstance(node.test.comparators[0], ast.Constant):
                    if node.test.comparators[0].value in (True, False):
                        line = self.source_lines[node.lineno - 1].strip() if node.lineno <= len(self.source_lines) else ""
                        self.suggestions.append(SimplificationSuggestion(
                            line_number=node.lineno,
                            original_code=line,
                            suggestion="Comparing to True/False is redundant. Use 'if x:' or 'if not x:' instead.",
                            category='simplify',
                            priority='low'
                        ))

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        # Check for enumerate opportunities
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == 'range' and len(node.iter.args) == 1:
                    if isinstance(node.iter.args[0], ast.Call):
                        if isinstance(node.iter.args[0].func, ast.Name):
                            if node.iter.args[0].func.id == 'len':
                                line = self.source_lines[node.lineno - 1].strip() if node.lineno <= len(self.source_lines) else ""
                                self.suggestions.append(SimplificationSuggestion(
                                    line_number=node.lineno,
                                    original_code=line,
                                    suggestion="Use 'for i, item in enumerate(collection):' instead of 'for i in range(len(collection)):'",
                                    category='simplify',
                                    priority='low'
                                ))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # Check for overly long lines
        if node.lineno <= len(self.source_lines):
            line = self.source_lines[node.lineno - 1]
            if len(line) > 120:
                self.suggestions.append(SimplificationSuggestion(
                    line_number=node.lineno,
                    original_code=line.strip()[:60] + "...",
                    suggestion=f"Line is {len(line)} characters long. Consider breaking it up or using intermediate variables.",
                    category='refactor',
                    priority='low'
                ))
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        # Check for bare except
        for handler in node.handlers:
            if handler.type is None:
                line = self.source_lines[handler.lineno - 1].strip() if handler.lineno <= len(self.source_lines) else ""
                self.suggestions.append(SimplificationSuggestion(
                    line_number=handler.lineno,
                    original_code=line,
                    suggestion="Bare 'except:' catches all exceptions including KeyboardInterrupt. Use 'except Exception:' instead.",
                    category='refactor',
                    priority='high'
                ))
        self.generic_visit(node)

    def _get_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate the nesting depth of a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._get_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth


class CodeSimplifier:
    """Main class for code analysis and simplification."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def analyze_file(self, filepath: str) -> Tuple[ComplexityMetrics, List[SimplificationSuggestion]]:
        """Analyze a single Python file for complexity and simplification opportunities."""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        return self.analyze_source(source, filepath)

    def analyze_source(self, source: str, filename: str = "<string>") -> Tuple[ComplexityMetrics, List[SimplificationSuggestion]]:
        """Analyze Python source code."""
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            print(f"Syntax error in {filename}: {e}")
            return ComplexityMetrics(), []

        source_lines = source.split('\n')

        # Calculate complexity metrics
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)

        metrics = ComplexityMetrics(
            cyclomatic_complexity=complexity_visitor.complexity,
            max_nesting_depth=complexity_visitor.max_depth,
            num_functions=len([n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]),
            num_classes=len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            lines_of_code=len([l for l in source_lines if l.strip() and not l.strip().startswith('#')]),
            num_imports=len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
        )

        # Find long and deeply nested functions
        for func_name, complexity in complexity_visitor.function_complexities.items():
            if complexity > 10:
                metrics.long_functions.append((func_name, complexity))

        for func_name, nesting in complexity_visitor.function_nesting.items():
            if nesting > 3:
                metrics.deeply_nested.append((func_name, nesting))

        # Get simplification suggestions
        simplifier = SimplificationAnalyzer(source_lines)
        simplifier.visit(tree)

        return metrics, simplifier.suggestions

    def analyze_directory(self, directory: str) -> Dict[str, Tuple[ComplexityMetrics, List[SimplificationSuggestion]]]:
        """Analyze all Python files in a directory."""
        results = {}

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if self.verbose:
                        print(f"Analyzing {filepath}...")
                    results[filepath] = self.analyze_file(filepath)

        return results

    def format_report(self, filepath: str, metrics: ComplexityMetrics,
                     suggestions: List[SimplificationSuggestion]) -> str:
        """Format analysis results as a readable report."""
        lines = [
            f"\n{'='*60}",
            f"Analysis Report: {filepath}",
            f"{'='*60}",
            "",
            "Complexity Metrics:",
            f"  - Cyclomatic Complexity: {metrics.cyclomatic_complexity}",
            f"  - Max Nesting Depth: {metrics.max_nesting_depth}",
            f"  - Lines of Code: {metrics.lines_of_code}",
            f"  - Functions: {metrics.num_functions}",
            f"  - Classes: {metrics.num_classes}",
            f"  - Imports: {metrics.num_imports}",
        ]

        if metrics.long_functions:
            lines.append("")
            lines.append("Complex Functions (complexity > 10):")
            for func_name, complexity in sorted(metrics.long_functions, key=lambda x: -x[1]):
                lines.append(f"  - {func_name}: complexity {complexity}")

        if metrics.deeply_nested:
            lines.append("")
            lines.append("Deeply Nested Functions (depth > 3):")
            for func_name, depth in sorted(metrics.deeply_nested, key=lambda x: -x[1]):
                lines.append(f"  - {func_name}: depth {depth}")

        if suggestions:
            lines.append("")
            lines.append(f"Simplification Suggestions ({len(suggestions)} found):")

            # Group by priority
            high = [s for s in suggestions if s.priority == 'high']
            medium = [s for s in suggestions if s.priority == 'medium']
            low = [s for s in suggestions if s.priority == 'low']

            for priority, items in [('HIGH', high), ('MEDIUM', medium), ('LOW', low)]:
                if items:
                    lines.append(f"\n  [{priority} Priority]")
                    for s in items:
                        lines.append(f"    Line {s.line_number} ({s.category}):")
                        lines.append(f"      {s.original_code}")
                        lines.append(f"      -> {s.suggestion}")
        else:
            lines.append("")
            lines.append("No simplification suggestions found.")

        lines.append("")
        return '\n'.join(lines)


def analyze_complexity(path: str, verbose: bool = False) -> Dict[str, ComplexityMetrics]:
    """Analyze complexity of Python files at the given path."""
    simplifier = CodeSimplifier(verbose=verbose)

    if os.path.isfile(path):
        metrics, _ = simplifier.analyze_file(path)
        return {path: metrics}
    elif os.path.isdir(path):
        results = simplifier.analyze_directory(path)
        return {k: v[0] for k, v in results.items()}
    else:
        raise ValueError(f"Path does not exist: {path}")


def simplify_file(filepath: str, output: bool = True) -> List[SimplificationSuggestion]:
    """Analyze a file and return/print simplification suggestions."""
    simplifier = CodeSimplifier()
    metrics, suggestions = simplifier.analyze_file(filepath)

    if output:
        print(simplifier.format_report(filepath, metrics, suggestions))

    return suggestions


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Code Simplifier Tool for analyzing Python code complexity',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s phases/                          # Analyze all files in phases/
  %(prog)s --suggest appendices/            # Show simplification suggestions
  %(prog)s --summary .                       # Summary of entire codebase
        """
    )

    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--suggest', '-s', action='store_true',
                       help='Show simplification suggestions')
    parser.add_argument('--summary', action='store_true',
                       help='Show summary only')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)

    simplifier = CodeSimplifier(verbose=args.verbose)

    if os.path.isfile(args.path):
        metrics, suggestions = simplifier.analyze_file(args.path)
        results = {args.path: (metrics, suggestions)}
    else:
        results = simplifier.analyze_directory(args.path)

    if args.json:
        import json
        output = {}
        for filepath, (metrics, suggestions) in results.items():
            output[filepath] = {
                'metrics': {
                    'cyclomatic_complexity': metrics.cyclomatic_complexity,
                    'max_nesting_depth': metrics.max_nesting_depth,
                    'lines_of_code': metrics.lines_of_code,
                    'num_functions': metrics.num_functions,
                    'num_classes': metrics.num_classes,
                    'num_imports': metrics.num_imports,
                    'complex_functions': metrics.long_functions,
                    'deeply_nested': metrics.deeply_nested,
                },
                'suggestions': [
                    {
                        'line': s.line_number,
                        'category': s.category,
                        'priority': s.priority,
                        'suggestion': s.suggestion,
                    }
                    for s in suggestions
                ]
            }
        print(json.dumps(output, indent=2))
    elif args.summary:
        total_loc = sum(m.lines_of_code for m, _ in results.values())
        total_functions = sum(m.num_functions for m, _ in results.values())
        total_classes = sum(m.num_classes for m, _ in results.values())
        total_complexity = sum(m.cyclomatic_complexity for m, _ in results.values())
        total_suggestions = sum(len(s) for _, s in results.values())

        print(f"\n{'='*60}")
        print(f"Codebase Summary: {args.path}")
        print(f"{'='*60}")
        print(f"  Files analyzed: {len(results)}")
        print(f"  Total lines of code: {total_loc}")
        print(f"  Total functions: {total_functions}")
        print(f"  Total classes: {total_classes}")
        print(f"  Total cyclomatic complexity: {total_complexity}")
        print(f"  Average complexity per file: {total_complexity / len(results):.1f}")
        print(f"  Simplification suggestions: {total_suggestions}")

        # Top complex files
        sorted_files = sorted(results.items(),
                             key=lambda x: x[1][0].cyclomatic_complexity,
                             reverse=True)[:5]
        print(f"\nMost Complex Files:")
        for filepath, (metrics, _) in sorted_files:
            print(f"  {filepath}: complexity {metrics.cyclomatic_complexity}")
        print()
    else:
        for filepath, (metrics, suggestions) in results.items():
            if args.suggest or suggestions:
                print(simplifier.format_report(filepath, metrics, suggestions))
            else:
                print(f"{filepath}: complexity={metrics.cyclomatic_complexity}, "
                      f"loc={metrics.lines_of_code}, functions={metrics.num_functions}")


if __name__ == '__main__':
    main()
