"""Regression tests for patent drawing hygiene-sensitive SVG structure."""

from pathlib import Path
import xml.etree.ElementTree as ET

_REPO_ROOT = Path(__file__).resolve().parent.parent


def test_fig3_snn_boundary_uses_rect_primitive() -> None:
    """Keep FIG. 3 SNN boundary as a validator-recognized component primitive."""
    repo_root = Path(__file__).resolve().parent.parent
    fig3_path = repo_root / "patent_drawings" / "patent_a" / "fig3.svg"
    root = ET.parse(fig3_path).getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # fig3.svg uses a 300 DPI canvas (viewBox 2550×3300) with translate(300,300) margin.
    # The SNN boundary rect sits at (320,200) with size 1560×1100 in drawing-space coords.
    boundary_rect = root.find(".//svg:g/svg:rect[@x='320'][@y='200'][@width='1560'][@height='1100']", ns)
    assert boundary_rect is not None, "Expected SNN boundary to be a <rect> primitive"

    boundary_path = root.find(
        ".//svg:g/svg:path[@d='M 148 100 L 692 100 Q 700 100 700 108 L 700 492 Q 700 500 692 500 L 148 500 Q 140 500 140 492 L 140 108 Q 140 100 148 100 Z']",
        ns,
    )
    assert boundary_path is None, "Legacy path boundary should not be present"
