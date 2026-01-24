"""Tests for the code simplifier tool."""

import pytest
import os
import tempfile
from tools.code_simplifier import (
    CodeSimplifier,
    ComplexityMetrics,
    ComplexityVisitor,
    SimplificationAnalyzer,
    SimplificationSuggestion,
    analyze_complexity,
    simplify_file,
)


class TestComplexityVisitor:
    """Tests for the ComplexityVisitor class."""

    def test_simple_function_complexity(self):
        """A simple function should have low complexity."""
        source = """
def simple():
    return 42
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 1
        assert metrics.num_functions == 1

    def test_if_statement_increases_complexity(self):
        """If statements should increase cyclomatic complexity."""
        source = """
def with_if(x):
    if x > 0:
        return 1
    return 0
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 2

    def test_nested_if_increases_depth(self):
        """Nested if statements should increase nesting depth."""
        source = """
def nested(x, y):
    if x > 0:
        if y > 0:
            if x > y:
                return x
            return y
        return 0
    return -1
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.max_nesting_depth == 3

    def test_for_loop_increases_complexity(self):
        """For loops should increase cyclomatic complexity."""
        source = """
def with_loop(items):
    total = 0
    for item in items:
        total += item
    return total
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 2

    def test_while_loop_increases_complexity(self):
        """While loops should increase cyclomatic complexity."""
        source = """
def with_while(n):
    while n > 0:
        n -= 1
    return n
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 2

    def test_try_except_increases_complexity(self):
        """Try-except blocks should increase cyclomatic complexity."""
        source = """
def with_try():
    try:
        return int("42")
    except ValueError:
        return 0
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity >= 2

    def test_boolean_operators_increase_complexity(self):
        """Boolean operators (and/or) should increase complexity."""
        source = """
def with_bool(a, b, c):
    if a and b and c:
        return True
    return False
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        # 1 base + 1 if + 2 additional 'and' operators
        assert metrics.cyclomatic_complexity == 4

    def test_list_comprehension_increases_complexity(self):
        """List comprehensions should increase complexity."""
        source = """
def with_listcomp(items):
    return [x * 2 for x in items]
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 2

    def test_lambda_increases_complexity(self):
        """Lambda expressions should increase complexity."""
        source = """
def with_lambda():
    return lambda x: x * 2
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.cyclomatic_complexity == 2


class TestComplexityMetrics:
    """Tests for complexity metrics calculation."""

    def test_counts_functions(self):
        """Should correctly count functions."""
        source = """
def func1():
    pass

def func2():
    pass

async def func3():
    pass
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.num_functions == 3

    def test_counts_classes(self):
        """Should correctly count classes."""
        source = """
class Foo:
    pass

class Bar:
    pass
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.num_classes == 2

    def test_counts_imports(self):
        """Should correctly count imports."""
        source = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.num_imports == 4

    def test_counts_lines_of_code(self):
        """Should correctly count non-empty, non-comment lines."""
        source = """
# This is a comment
def foo():
    # Another comment
    x = 1
    return x

"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        assert metrics.lines_of_code == 3  # def, x = 1, return x (comments excluded)


class TestSimplificationAnalyzer:
    """Tests for the SimplificationAnalyzer class."""

    def test_detects_long_functions(self):
        """Should detect functions longer than 50 lines."""
        # Create a function with 60 lines
        lines = ["def long_function():"]
        for i in range(59):
            lines.append(f"    x{i} = {i}")
        source = "\n".join(lines)

        simplifier = CodeSimplifier()
        _, suggestions = simplifier.analyze_source(source)

        extract_suggestions = [s for s in suggestions if s.category == 'extract']
        assert len(extract_suggestions) >= 1
        assert any('long_function' in s.suggestion for s in extract_suggestions)

    def test_detects_too_many_parameters(self):
        """Should detect functions with more than 5 parameters."""
        source = """
def many_params(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
"""
        simplifier = CodeSimplifier()
        _, suggestions = simplifier.analyze_source(source)

        refactor_suggestions = [s for s in suggestions if s.category == 'refactor']
        assert len(refactor_suggestions) >= 1
        assert any('7 parameters' in s.suggestion for s in refactor_suggestions)

    def test_detects_bare_except(self):
        """Should detect bare except clauses."""
        source = """
def risky():
    try:
        return 1 / 0
    except:
        return 0
"""
        simplifier = CodeSimplifier()
        _, suggestions = simplifier.analyze_source(source)

        high_priority = [s for s in suggestions if s.priority == 'high']
        assert len(high_priority) >= 1
        assert any('Bare' in s.suggestion for s in high_priority)

    def test_no_suggestions_for_clean_code(self):
        """Clean code should have minimal suggestions."""
        source = """
def clean_function(x: int) -> int:
    if x > 0:
        return x * 2
    return 0
"""
        simplifier = CodeSimplifier()
        _, suggestions = simplifier.analyze_source(source)

        # Should have no high priority suggestions
        high_priority = [s for s in suggestions if s.priority == 'high']
        assert len(high_priority) == 0


class TestCodeSimplifier:
    """Tests for the main CodeSimplifier class."""

    def test_analyze_source_returns_metrics_and_suggestions(self):
        """analyze_source should return both metrics and suggestions."""
        source = "def foo(): return 42"
        simplifier = CodeSimplifier()
        metrics, suggestions = simplifier.analyze_source(source)

        assert isinstance(metrics, ComplexityMetrics)
        assert isinstance(suggestions, list)

    def test_analyze_file_with_valid_file(self):
        """Should analyze a valid Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test(): return 1")
            f.flush()

            try:
                simplifier = CodeSimplifier()
                metrics, suggestions = simplifier.analyze_file(f.name)
                assert metrics.num_functions == 1
            finally:
                os.unlink(f.name)

    def test_analyze_directory(self):
        """Should analyze all Python files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            with open(os.path.join(tmpdir, 'file1.py'), 'w') as f:
                f.write("def func1(): pass")
            with open(os.path.join(tmpdir, 'file2.py'), 'w') as f:
                f.write("def func2(): pass\ndef func3(): pass")

            simplifier = CodeSimplifier()
            results = simplifier.analyze_directory(tmpdir)

            assert len(results) == 2
            total_functions = sum(m.num_functions for m, _ in results.values())
            assert total_functions == 3

    def test_format_report_produces_output(self):
        """format_report should produce readable output."""
        metrics = ComplexityMetrics(
            cyclomatic_complexity=10,
            max_nesting_depth=3,
            lines_of_code=100,
            num_functions=5,
            num_classes=2,
            num_imports=4,
        )
        suggestions = [
            SimplificationSuggestion(
                line_number=10,
                original_code="def foo():",
                suggestion="Consider refactoring",
                category='refactor',
                priority='medium',
            )
        ]

        simplifier = CodeSimplifier()
        report = simplifier.format_report("test.py", metrics, suggestions)

        assert "test.py" in report
        assert "Cyclomatic Complexity: 10" in report
        assert "Consider refactoring" in report

    def test_handles_syntax_errors_gracefully(self):
        """Should handle syntax errors without crashing."""
        source = "def broken( return"
        simplifier = CodeSimplifier()
        metrics, suggestions = simplifier.analyze_source(source)

        # Should return empty metrics on syntax error
        assert metrics.cyclomatic_complexity == 0


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_analyze_complexity_with_file(self):
        """analyze_complexity should work with a single file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test(): return 1")
            f.flush()

            try:
                results = analyze_complexity(f.name)
                assert f.name in results
                assert results[f.name].num_functions == 1
            finally:
                os.unlink(f.name)

    def test_analyze_complexity_with_directory(self):
        """analyze_complexity should work with a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, 'test.py'), 'w') as f:
                f.write("def func(): pass")

            results = analyze_complexity(tmpdir)
            assert len(results) == 1

    def test_analyze_complexity_invalid_path(self):
        """analyze_complexity should raise error for invalid path."""
        with pytest.raises(ValueError):
            analyze_complexity("/nonexistent/path")

    def test_simplify_file(self, capsys):
        """simplify_file should print a report."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test(): return 1")
            f.flush()

            try:
                suggestions = simplify_file(f.name, output=True)
                captured = capsys.readouterr()
                assert "Analysis Report" in captured.out
                assert isinstance(suggestions, list)
            finally:
                os.unlink(f.name)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_file(self):
        """Should handle empty files."""
        simplifier = CodeSimplifier()
        metrics, suggestions = simplifier.analyze_source("")
        assert metrics.lines_of_code == 0
        assert metrics.num_functions == 0

    def test_comments_only(self):
        """Should handle files with only comments."""
        source = """
# Comment 1
# Comment 2
# Comment 3
"""
        simplifier = CodeSimplifier()
        metrics, suggestions = simplifier.analyze_source(source)
        assert metrics.lines_of_code == 0

    def test_deeply_nested_code(self):
        """Should detect deeply nested code."""
        source = """
def deep():
    if True:
        if True:
            if True:
                if True:
                    return 1
"""
        simplifier = CodeSimplifier()
        metrics, suggestions = simplifier.analyze_source(source)
        assert metrics.max_nesting_depth >= 4

    def test_complex_function_detection(self):
        """Should identify complex functions."""
        # Create a function with high complexity
        source = """
def complex_func(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    if i % 3 == 0:
                        return i
    elif x < 0:
        while x < 0:
            x += 1
    else:
        try:
            return int(x)
        except ValueError:
            return 0
    return x
"""
        simplifier = CodeSimplifier()
        metrics, _ = simplifier.analyze_source(source)
        # Should have significant complexity
        assert metrics.cyclomatic_complexity >= 8
