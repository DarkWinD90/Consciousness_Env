"""Regression tests for patent drawing hygiene-sensitive SVG structure."""

from pathlib import Path
import xml.etree.ElementTree as ET

_REPO_ROOT = Path(__file__).resolve().parent.parent


def test_fig3_snn_boundary_uses_rect_primitive() -> None:
    """Keep FIG. 3 SNN boundary as a validator-recognized component primitive."""
    repo_root = Path(__file__).resolve().parent.parent
    fig3_path = repo_root / "patent_drawings" / "patent_a" / "fig3.svg"
    # Explicit existence assertion so a missing file fails the test loudly
    # rather than crashing inside ET.parse before any assertion runs.
    assert fig3_path.exists(), f"Required fixture missing: {fig3_path}"
    root = ET.parse(fig3_path).getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # fig3.svg now uses the canonical 850x1100 canvas (100 units/inch) shared
    # with the other 20 figures; the SNN boundary rect sits at (107,67) with
    # size 520x367 in drawing-space coordinates inside the translate(0,50)
    # margin group. Prior session used a 2550x3300 (300 DPI) canvas with a
    # (320,200,1560,1100) rect; that layout was retired on 2026-04-24.
    boundary_rect = root.find(".//svg:g/svg:rect[@x='107'][@y='67'][@width='520'][@height='367']", ns)
    assert boundary_rect is not None, "Expected SNN boundary to be a <rect> primitive"

    boundary_path = root.find(
        ".//svg:g/svg:path[@d='M 148 100 L 692 100 Q 700 100 700 108 L 700 492 Q 700 500 692 500 L 148 500 Q 140 500 140 492 L 140 108 Q 140 100 148 100 Z']",
        ns,
    )
    assert boundary_path is None, "Legacy path boundary should not be present"
