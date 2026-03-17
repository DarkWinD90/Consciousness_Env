"""Tests for reference_validator centered-numeral handling.

Ensures that lone centered 100-500 numerals are treated as reference
numerals (validated for leader lines), while clusters of axis-like
values aligned on the same coordinate are still skipped.
"""

import sys
from pathlib import Path

# Allow importing the validator module
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / ".claude" / "skills" / "patent-drawer" / "validators"),
)

from reference_validator import find_reference_numerals, _is_graph_axis_label


# ── helpers ──────────────────────────────────────────────────────────

def _svg(body: str) -> str:
    """Wrap *body* in a minimal SVG shell."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 1100">\n'
        f"{body}\n"
        "</svg>"
    )


# ── _is_graph_axis_label ────────────────────────────────────────────

def test_lone_centered_100_is_not_axis_label() -> None:
    """A single centered '100' with no nearby axis peers is NOT an axis label."""
    content = _svg(
        '<text x="420" y="300" font-size="14" text-anchor="middle">100</text>'
    )
    assert _is_graph_axis_label(content, "100", 420, 300) is False


def test_cluster_of_three_on_same_y_is_axis_label() -> None:
    """Three round axis values on the same y → graph axis."""
    content = _svg(
        '<text x="200" y="500" font-size="14" text-anchor="middle">100</text>\n'
        '<text x="350" y="500" font-size="14" text-anchor="middle">200</text>\n'
        '<text x="500" y="500" font-size="14" text-anchor="middle">300</text>'
    )
    assert _is_graph_axis_label(content, "100", 200, 500) is True


def test_cluster_of_three_on_same_x_is_axis_label() -> None:
    """Three round axis values on the same x → vertical axis."""
    content = _svg(
        '<text x="100" y="200" font-size="14" text-anchor="middle">100</text>\n'
        '<text x="100" y="350" font-size="14" text-anchor="middle">200</text>\n'
        '<text x="100" y="500" font-size="14" text-anchor="middle">300</text>'
    )
    assert _is_graph_axis_label(content, "200", 100, 350) is True


def test_two_axis_values_not_enough() -> None:
    """Only two axis values on same y → NOT enough to declare an axis."""
    content = _svg(
        '<text x="200" y="500" font-size="14" text-anchor="middle">100</text>\n'
        '<text x="350" y="500" font-size="14" text-anchor="middle">200</text>'
    )
    assert _is_graph_axis_label(content, "100", 200, 500) is False


def test_non_axis_value_ignored() -> None:
    """A numeral outside {100,200,300,400,500} is never an axis label."""
    content = _svg(
        '<text x="200" y="500" font-size="14" text-anchor="middle">102</text>'
    )
    assert _is_graph_axis_label(content, "102", 200, 500) is False


# ── find_reference_numerals ─────────────────────────────────────────

def test_lone_centered_100_included_in_results() -> None:
    """A lone centered '100' must appear in the extracted numerals list."""
    content = _svg(
        '<text x="420" y="300" font-size="14" text-anchor="middle">100</text>'
    )
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "100" in values, f"Expected '100' in {values}"


def test_axis_cluster_excluded_from_results() -> None:
    """When ≥3 axis values are aligned, they should be excluded."""
    content = _svg(
        '<text x="200" y="500" font-size="14" text-anchor="middle">100</text>\n'
        '<text x="350" y="500" font-size="14" text-anchor="middle">200</text>\n'
        '<text x="500" y="500" font-size="14" text-anchor="middle">300</text>'
    )
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "100" not in values
    assert "200" not in values
    assert "300" not in values


def test_non_centered_100_always_included() -> None:
    """A non-centered '100' (e.g. text-anchor='end') is always included."""
    content = _svg(
        '<text x="208" y="205" font-size="14" text-anchor="end">100</text>'
    )
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "100" in values


def test_centered_500_lone_included() -> None:
    """A single centered '500' must appear in results (not skipped)."""
    content = _svg(
        '<text x="670" y="400" font-size="14" text-anchor="middle">500</text>'
    )
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "500" in values, f"Expected '500' in {values}"
