"""Tests for validate_line_thickness compliance behaviour.

Ensures that thin stroke widths (below 0.5px) cause a compliance failure,
while valid stroke widths pass.
"""

import sys
import tempfile
from pathlib import Path

# Allow importing the validator module
sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / ".claude" / "skills" / "patent-drawer" / "validators"),
)

from full_compliance import validate_line_thickness


# ── helpers ──────────────────────────────────────────────────────────

def _svg(body: str) -> str:
    """Wrap *body* in a minimal SVG shell."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 1100">\n'
        f"{body}\n"
        "</svg>"
    )


def _write_tmp_svg(content: str) -> str:
    """Write *content* to a temporary .svg file and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".svg", mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


# ── tests ────────────────────────────────────────────────────────────

def test_valid_stroke_widths_pass() -> None:
    """Stroke widths >= 0.5 should pass."""
    svg = _svg(
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1"/>\n'
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="0.5"/>\n'
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="2"/>'
    )
    path = _write_tmp_svg(svg)
    assert validate_line_thickness(path) is True


def test_thin_stroke_width_fails() -> None:
    """A stroke-width below 0.5 must cause a failure (return False)."""
    svg = _svg(
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="0.3"/>'
    )
    path = _write_tmp_svg(svg)
    assert validate_line_thickness(path) is False


def test_mixed_stroke_widths_fails() -> None:
    """If any stroke-width is below the minimum, the check must fail."""
    svg = _svg(
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="1.5"/>\n'
        '<line x1="0" y1="0" x2="100" y2="100" stroke="black" stroke-width="0.2"/>'
    )
    path = _write_tmp_svg(svg)
    assert validate_line_thickness(path) is False


def test_no_stroke_widths_pass() -> None:
    """SVGs with no explicit stroke-width attributes should pass."""
    svg = _svg('<rect x="10" y="10" width="100" height="100" fill="black"/>')
    path = _write_tmp_svg(svg)
    assert validate_line_thickness(path) is True


if __name__ == "__main__":
    test_valid_stroke_widths_pass()
    test_thin_stroke_width_fails()
    test_mixed_stroke_widths_fails()
    test_no_stroke_widths_pass()
    print("All tests passed.")
