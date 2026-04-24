"""Tests for reference_validator's numeral extraction and axis-label handling.

After the 2026-04-24 validator audit, axis-label detection is based solely
on explicit ``<g class="axis-label">`` wrapping — no coord-alignment
heuristic. The rationale is documented on
``.claude/skills/patent-drawer/validators/reference_validator.py``:
coord-alignment repeatedly misclassified horizontally-arranged reference
numerals (e.g., patent_b/fig2's spectrum-region numerals 28..36 at y=190)
as axis ticks and caused systematic false negatives for real ref numerals.

These tests lock in the new contract:
- Any numeric text inside ``<g class="axis-label">`` is an axis label,
  regardless of digit count or text-anchor.
- Any numeric text NOT inside such a block is a reference numeral
  (provided it is a 2-3 digit number, per 37 CFR 1.84(q)).
"""

import sys
from pathlib import Path

# Allow importing the validator module
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / ".claude" / "skills" / "patent-drawer" / "validators"),
)

from reference_validator import (  # noqa: E402
    _axis_label_block_ranges,
    _is_graph_axis_label,
    find_reference_numerals,
)


def _svg(body: str) -> str:
    """Wrap *body* in a minimal SVG shell."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 1100">\n'
        f"{body}\n"
        "</svg>"
    )


# ── _axis_label_block_ranges ──────────────────────────────────────────

def test_axis_block_range_single() -> None:
    """A single axis-label block is detected with correct line range."""
    content = _svg(
        '  <g class="axis-label">\n'
        '    <text x="100" y="500">100</text>\n'
        '  </g>'
    )
    ranges = _axis_label_block_ranges(content)
    assert len(ranges) == 1
    # Body starts at line 2 (SVG opens on line 1). <g> on line 2, </g> on line 4.
    assert ranges[0] == (2, 4)


def test_axis_block_range_multiple() -> None:
    """Multiple non-nested axis-label blocks each get their own range."""
    content = _svg(
        '  <g class="axis-label">\n'
        '    <text x="100" y="500">0</text>\n'
        '  </g>\n'
        '  <rect x="10" y="10" width="20" height="20"/>\n'
        '  <g class="axis-label">\n'
        '    <text x="200" y="600">50</text>\n'
        '  </g>'
    )
    ranges = _axis_label_block_ranges(content)
    assert len(ranges) == 2


def test_axis_block_range_absent() -> None:
    """A figure with no axis-label block has no ranges."""
    content = _svg(
        '  <text x="100" y="500">42</text>'
    )
    ranges = _axis_label_block_ranges(content)
    assert ranges == []


# ── _is_graph_axis_label ─────────────────────────────────────────────

def test_numeral_inside_axis_block_is_axis() -> None:
    """A numeral whose line is inside a <g class="axis-label"> range is an axis label."""
    content = _svg(
        '  <g class="axis-label">\n'
        '    <text x="100" y="500" text-anchor="middle">250</text>\n'
        '  </g>'
    )
    # "250" lives on line 3 (1-indexed) in the content above.
    assert _is_graph_axis_label(content, 100, 500, line_num=3) is True


def test_numeral_outside_axis_block_is_not_axis() -> None:
    """A numeral outside any axis-label block is NOT an axis label."""
    content = _svg(
        '  <text x="100" y="500" text-anchor="middle">250</text>'
    )
    assert _is_graph_axis_label(content, 100, 500, line_num=2) is False


def test_coord_alignment_does_not_force_axis() -> None:
    """Three co-aligned numerals outside any axis-label block are NOT axes.

    This is the crucial regression: the pre-2026-04-24 implementation
    would return True here because three centered numerics share y=500.
    The new implementation refuses to infer that.
    """
    content = _svg(
        '  <text x="200" y="500" text-anchor="middle">100</text>\n'
        '  <text x="350" y="500" text-anchor="middle">200</text>\n'
        '  <text x="500" y="500" text-anchor="middle">300</text>'
    )
    for line_num in (2, 3, 4):
        assert _is_graph_axis_label(content, 200, 500, line_num=line_num) is False


def test_axis_block_applies_to_any_text_anchor() -> None:
    """Inside an axis-label block, text-anchor=end numerals are still axis labels."""
    content = _svg(
        '  <g class="axis-label">\n'
        '    <text x="148" y="500" text-anchor="end">100</text>\n'
        '  </g>'
    )
    assert _is_graph_axis_label(content, 148, 500, line_num=3) is True


# ── find_reference_numerals ──────────────────────────────────────────

def test_standalone_numeral_included() -> None:
    """A numeral with no axis-label wrapper is returned as a ref numeral."""
    content = _svg('  <text x="100" y="200">42</text>')
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "42" in values


def test_axis_block_numerals_excluded() -> None:
    """Numerals inside a <g class="axis-label"> block are filtered out."""
    content = _svg(
        '  <g class="axis-label">\n'
        '    <text x="100" y="500" text-anchor="middle">100</text>\n'
        '    <text x="200" y="500" text-anchor="middle">250</text>\n'
        '    <text x="300" y="500" text-anchor="middle">500</text>\n'
        '  </g>\n'
        '  <text x="400" y="100">42</text>'
    )
    nums = find_reference_numerals(content)
    values = [n["value"] for n in nums]
    assert "100" not in values
    assert "250" not in values
    assert "500" not in values
    assert "42" in values


def test_horizontally_arranged_ref_numerals_preserved() -> None:
    """Ref numerals in a horizontal row (no axis block) must ALL be kept.

    Regression test for the patent_b/fig2 case: five spectrum-region
    reference numerals (28, 30, 32, 34, 36) sit at y=190 with
    text-anchor="middle" and look axis-like by coord alignment. The
    pre-2026-04-24 validator mis-filtered three of them.
    """
    content = _svg(
        '  <text x="150" y="190" text-anchor="middle">28</text>\n'
        '  <text x="300" y="190" text-anchor="middle">30</text>\n'
        '  <text x="450" y="190" text-anchor="middle">32</text>\n'
        '  <text x="600" y="190" text-anchor="middle">34</text>\n'
        '  <text x="750" y="190" text-anchor="middle">36</text>'
    )
    values = [n["value"] for n in find_reference_numerals(content)]
    assert values == ["28", "30", "32", "34", "36"]


def test_one_digit_numeric_not_a_ref() -> None:
    """Single-digit numerics are never reference numerals (37 CFR 1.84(q))."""
    content = _svg('  <text x="100" y="200">5</text>')
    values = [n["value"] for n in find_reference_numerals(content)]
    assert values == []
