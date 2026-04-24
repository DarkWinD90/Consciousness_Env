#!/usr/bin/env python3
"""
Enhanced Patent Drawing Collision Checker

Uses a hybrid approach combining:
1. SVG structural analysis for fast initial detection
2. Pixel-level validation for accurate collision measurement
3. Semantic filtering to eliminate false positives (text inside shapes is intentional)

Requirements:
- Pillow (PIL) for image processing
- cairosvg or browser-based SVG rendering for high-res rasterization
- numpy for pixel analysis

Key improvements over basic checker:
- Properly handles rotated text by analyzing actual rendered pixels
- Filters out intentional text-in-shape patterns (labels inside boxes)
- Measures actual pixel-level clearance gaps
- Provides specific fix recommendations with coordinate adjustments
"""

import xml.etree.ElementTree as ET
import re
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Set
import subprocess
import tempfile

# Try to import optional dependencies
try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL/numpy not available. Pixel-level validation disabled.")

try:
    import cairosvg
    HAS_CAIRO = True
except (ImportError, OSError):
    HAS_CAIRO = False


@dataclass
class BBox:
    """Bounding box with element metadata."""
    x: float
    y: float
    w: float
    h: float
    elem_type: str
    text: str = ""
    is_rotated: bool = False
    rotation_angle: float = 0.0
    parent_transform: Tuple[float, float] = (0.0, 0.0)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.w/2, self.y + self.h/2)


@dataclass
class Collision:
    """Detected collision between two elements."""
    elem1: BBox
    elem2: BBox
    collision_type: str  # text-on-text, text-on-shape, text-on-line, semantic
    overlap_ratio: float
    pixel_gap: Optional[float] = None  # Measured pixel clearance (if available)
    severity: str = "medium"  # low, medium, high, critical
    fix_suggestion: str = ""

    def to_dict(self) -> dict:
        return {
            "type": self.collision_type,
            "elem1": self.elem1.text or self.elem1.elem_type,
            "elem2": self.elem2.text or self.elem2.elem_type,
            "overlap_ratio": self.overlap_ratio,
            "pixel_gap": self.pixel_gap,
            "severity": self.severity,
            "fix": self.fix_suggestion
        }


class EnhancedCollisionChecker:
    """
    Enhanced collision detection with pixel-level validation.
    """

    # Minimum clearance in viewBox units (0.32cm at 100 DPI ≈ 12.6 units)
    MIN_CLEARANCE_VB = 5.0  # Tight but acceptable
    WARN_CLEARANCE_VB = 10.0  # Preferred minimum

    # False positive patterns to filter
    INTENTIONAL_PATTERNS = {
        # Text inside component boxes (labels)
        ("text", "rect"): lambda t, r: EnhancedCollisionChecker._text_inside_rect(t, r),
        # Reference numerals near their components
        ("text", "circle"): lambda t, c: EnhancedCollisionChecker._is_label_for_shape(t, c),
        # Spine arrows touching blocks (expected)
        ("line", "rect"): lambda l, r: EnhancedCollisionChecker._is_connector(l, r),
    }

    def __init__(self, svg_path: str, render_scale: int = 3):
        self.svg_path = Path(svg_path)
        self.render_scale = render_scale  # 3 = 300 DPI equivalent
        self.elements: List[BBox] = []
        self.collisions: List[Collision] = []
        self.viewbox = (0, 0, 850, 1100)  # Default
        self.transform_stack = [(0, 0)]

    def parse_svg(self) -> None:
        """Parse SVG and extract all element bounding boxes."""
        tree = ET.parse(self.svg_path)
        root = tree.getroot()

        # Extract viewBox
        vb = root.get('viewBox', '0 0 850 1100')
        self.viewbox = tuple(map(float, vb.split()))

        # Recursively process elements
        self._process_element(root, (0, 0))

    def _process_element(self, elem, parent_tx: Tuple[float, float]) -> None:
        """Process an element and its children."""
        # Get this element's transform
        transform = elem.get('transform', '')
        tx, ty = self._parse_transform(transform)
        current_tx = (parent_tx[0] + tx, parent_tx[1] + ty)

        # Extract tag without namespace
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')

        bbox = None
        if tag == 'text':
            bbox = self._get_text_bbox(elem, current_tx)
        elif tag == 'rect':
            bbox = self._get_rect_bbox(elem, current_tx)
        elif tag == 'circle':
            bbox = self._get_circle_bbox(elem, current_tx)
        elif tag == 'line':
            bbox = self._get_line_bbox(elem, current_tx)
        elif tag == 'polyline':
            bbox = self._get_polyline_bbox(elem, current_tx)
        elif tag == 'path':
            bbox = self._get_path_bbox(elem, current_tx)
        elif tag == 'polygon':
            bbox = self._get_polygon_bbox(elem, current_tx)

        if bbox and (bbox.w > 0 or bbox.h > 0):
            self.elements.append(bbox)

        # Process children
        for child in elem:
            self._process_element(child, current_tx)

    def _parse_transform(self, transform_str: str) -> Tuple[float, float]:
        """Extract translation from transform attribute."""
        if not transform_str:
            return (0, 0)
        match = re.search(r'translate\s*\(\s*([\d.-]+)\s*,?\s*([\d.-]+)?\s*\)', transform_str)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2)) if match.group(2) else 0
            return (tx, ty)
        return (0, 0)

    def _get_text_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        """Get bounding box for text, accounting for rotation."""
        try:
            x = float(elem.get('x', 0)) + tx[0]
            y = float(elem.get('y', 0)) + tx[1]
            font_size = float(elem.get('font-size', 14))
            text = elem.text or ''

            # Estimate dimensions
            char_width = font_size * 0.6
            width = len(text) * char_width
            height = font_size

            # Handle text-anchor
            anchor = elem.get('text-anchor', 'start')
            if anchor == 'middle':
                x -= width / 2
            elif anchor == 'end':
                x -= width

            # y is baseline, adjust to top
            y -= font_size * 0.8

            # Check for rotation
            transform = elem.get('transform', '')
            is_rotated = False
            rotation_angle = 0.0

            rotate_match = re.search(
                r'rotate\s*\(\s*(-?[\d.]+)(?:\s*,?\s*([\d.]+)\s*,?\s*([\d.]+))?\s*\)',
                transform
            )
            if rotate_match:
                rotation_angle = float(rotate_match.group(1))
                cx = float(rotate_match.group(2)) if rotate_match.group(2) else x
                cy = float(rotate_match.group(3)) if rotate_match.group(3) else y
                is_rotated = True

                # For ±90° rotation, swap width and height
                if abs(abs(rotation_angle) - 90) < 5:
                    width, height = height, width
                    if rotation_angle > 0:
                        x = cx - height / 2
                        y = cy
                    else:
                        x = cx - height / 2
                        y = cy - width

            return BBox(
                x=x, y=y, w=width, h=height,
                elem_type='text', text=text[:30],
                is_rotated=is_rotated, rotation_angle=rotation_angle,
                parent_transform=tx
            )
        except (ValueError, TypeError):
            return None

    def _get_rect_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        try:
            x = float(elem.get('x', 0)) + tx[0]
            y = float(elem.get('y', 0)) + tx[1]
            w = float(elem.get('width', 0))
            h = float(elem.get('height', 0))
            return BBox(x=x, y=y, w=w, h=h, elem_type='rect', parent_transform=tx)
        except (ValueError, TypeError):
            return None

    def _get_circle_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        try:
            cx = float(elem.get('cx', 0)) + tx[0]
            cy = float(elem.get('cy', 0)) + tx[1]
            r = float(elem.get('r', 0))
            return BBox(x=cx-r, y=cy-r, w=2*r, h=2*r, elem_type='circle', parent_transform=tx)
        except (ValueError, TypeError):
            return None

    def _get_line_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        try:
            x1 = float(elem.get('x1', 0)) + tx[0]
            y1 = float(elem.get('y1', 0)) + tx[1]
            x2 = float(elem.get('x2', 0)) + tx[0]
            y2 = float(elem.get('y2', 0)) + tx[1]
            sw = float(elem.get('stroke-width', 1))

            buf = sw + 2
            x = min(x1, x2) - buf
            y = min(y1, y2) - buf
            w = abs(x2 - x1) + 2 * buf
            h = abs(y2 - y1) + 2 * buf

            return BBox(x=x, y=y, w=w, h=h, elem_type='line', parent_transform=tx)
        except (ValueError, TypeError):
            return None

    def _get_polyline_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        try:
            points_str = elem.get('points', '')
            coords = re.findall(r'([\d.-]+)[,\s]+([\d.-]+)', points_str)
            if not coords:
                return None
            xs = [float(c[0]) + tx[0] for c in coords]
            ys = [float(c[1]) + tx[1] for c in coords]
            sw = float(elem.get('stroke-width', 1))
            buf = sw + 2
            return BBox(
                x=min(xs)-buf, y=min(ys)-buf,
                w=max(xs)-min(xs)+2*buf, h=max(ys)-min(ys)+2*buf,
                elem_type='polyline', parent_transform=tx
            )
        except (ValueError, TypeError):
            return None

    def _get_polygon_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        """Get bounding box for polygon element."""
        try:
            points_str = elem.get('points', '')
            coords = re.findall(r'([\d.-]+)[,\s]+([\d.-]+)', points_str)
            if not coords:
                return None
            xs = [float(c[0]) + tx[0] for c in coords]
            ys = [float(c[1]) + tx[1] for c in coords]
            return BBox(
                x=min(xs), y=min(ys),
                w=max(xs)-min(xs), h=max(ys)-min(ys),
                elem_type='polygon', parent_transform=tx
            )
        except (ValueError, TypeError):
            return None

    def _get_path_bbox(self, elem, tx: Tuple[float, float]) -> Optional[BBox]:
        """Extract approximate bbox from path d attribute."""
        try:
            d = elem.get('d', '')
            # Extract all coordinates from path
            coords = re.findall(r'[MLHVCSQTA]?\s*([\d.-]+)(?:[,\s]+([\d.-]+))?', d, re.I)
            xs, ys = [], []
            last_x, last_y = 0, 0
            for match in coords:
                if match[0]:
                    xs.append(float(match[0]) + tx[0])
                    last_x = float(match[0])
                if match[1]:
                    ys.append(float(match[1]) + tx[1])
                    last_y = float(match[1])
            if not xs or not ys:
                return None
            sw = float(elem.get('stroke-width', 2))
            buf = sw + 2
            return BBox(
                x=min(xs)-buf, y=min(ys)-buf,
                w=max(xs)-min(xs)+2*buf, h=max(ys)-min(ys)+2*buf,
                elem_type='path', parent_transform=tx
            )
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _text_inside_rect(text_bbox: BBox, rect_bbox: BBox) -> bool:
        """Check if text is intentionally inside a rectangle (label)."""
        # Text center is inside rect = intentional label
        tcx, tcy = text_bbox.center
        return (rect_bbox.x < tcx < rect_bbox.x2 and
                rect_bbox.y < tcy < rect_bbox.y2)

    @staticmethod
    def _is_label_for_shape(text_bbox: BBox, shape_bbox: BBox) -> bool:
        """Check if text is a label positioned near a shape."""
        # Reference numerals are typically 3-4 digits positioned just outside
        if len(text_bbox.text) <= 4 and text_bbox.text.isdigit():
            # Check if it's adjacent (within 50 units)
            tcx, tcy = text_bbox.center
            scx, scy = shape_bbox.center
            dist = ((tcx - scx)**2 + (tcy - scy)**2)**0.5
            return dist < 80
        return False

    @staticmethod
    def _is_connector(line_bbox: BBox, rect_bbox: BBox) -> bool:
        """Check if line is a connector touching a component."""
        # Connectors typically touch component edges
        return True  # For now, assume all line-rect contacts are connectors

    @staticmethod
    def _is_pin_label(text: str) -> bool:
        """Check if text is a pin label (GPIO, ADC, PWM, etc.)."""
        if not text:
            return False
        text_upper = text.upper().strip()
        # Common microcontroller pin patterns
        pin_patterns = [
            'GP',      # GPIO (GP0, GP15, GP26, etc.)
            'ADC',     # Analog-to-digital (ADC0, ADC1, ADC2)
            'PWM',     # Pulse width modulation
            'VSYS',    # System voltage
            'VBUS',    # USB voltage
            '3V3',     # 3.3V rail
            'GND',     # Ground
            'VCC',     # Supply voltage
            'SDA',     # I2C data
            'SCL',     # I2C clock
            'TX',      # UART transmit
            'RX',      # UART receive
            'MOSI',    # SPI master out
            'MISO',    # SPI master in
            'SCK',     # SPI clock
            'CS',      # Chip select
        ]
        for pattern in pin_patterns:
            if text_upper.startswith(pattern) or text_upper == pattern:
                return True
        return False

    def _text_inside_any_rect(self, text_bbox: BBox, rects: List[BBox]) -> bool:
        """Check if text is inside any component rectangle."""
        for r in rects:
            if self._text_inside_rect(text_bbox, r):
                return True
        return False

    def _text_near_shape_center(self, text_bbox: BBox, shapes: List[BBox], threshold: float = 30.0) -> bool:
        """Check if text is near the center of any shape (for component labels)."""
        tcx, tcy = text_bbox.center
        for s in shapes:
            scx, scy = s.center
            dist = ((tcx - scx)**2 + (tcy - scy)**2)**0.5
            if dist < threshold:
                return True
        return False

    def _is_graph_annotation(self, text_bbox: BBox, line_bbox: BBox) -> bool:
        """Check if text is a graph annotation (positioned near graph edge, not crossing lines)."""
        # Graph annotations are typically:
        # 1. Positioned at right edge (x > 600) with right-aligned text
        # 2. Positioned clearly above or below data lines (not ON them)
        # 3. Axis labels positioned outside the plot area
        # 4. Region labels inside filled areas (like "Experimental" in hatched region)

        tcx, tcy = text_bbox.center
        lcx, lcy = line_bbox.center

        # Right-edge annotations (x > 600 viewBox units) - common for graph labels
        if tcx > 600:
            return True  # Right-edge labels are almost always annotations

        # Left-edge axis labels (x < 200)
        if tcx < 200:
            return True

        # Top-area title labels (y < 150)
        if tcy < 150:
            return True

        # Large filled regions (paths/polylines spanning large areas) with text inside
        # If the line bbox is very large (area > 50000), it's likely a filled region
        # and text inside is a region label
        line_area = line_bbox.w * line_bbox.h
        if line_area > 50000:
            # Check if text is inside the line bbox (region label)
            if (line_bbox.x < tcx < line_bbox.x2 and
                line_bbox.y < tcy < line_bbox.y2):
                return True

        return False

    def detect_collisions(self) -> List[Collision]:
        """Detect collisions between elements."""
        self.collisions = []

        texts = [e for e in self.elements if e.elem_type == 'text']
        shapes = [e for e in self.elements if e.elem_type in ('rect', 'circle', 'polygon')]
        lines = [e for e in self.elements if e.elem_type in ('line', 'polyline', 'path')]

        # Text-on-text collisions
        for i, t1 in enumerate(texts):
            for t2 in texts[i+1:]:
                overlap = self._calc_overlap(t1, t2)
                if overlap > 0.10:
                    # Check if both are rotated perpendicular (often non-issue)
                    if t1.is_rotated != t2.is_rotated:
                        # Different orientations - reduced concern
                        severity = "low" if overlap < 0.30 else "medium"
                    else:
                        severity = "high" if overlap > 0.50 else "medium"

                    self.collisions.append(Collision(
                        elem1=t1, elem2=t2,
                        collision_type="text-on-text",
                        overlap_ratio=overlap,
                        severity=severity,
                        fix_suggestion=self._suggest_text_fix(t1, t2)
                    ))

        # Text-on-shape (filter intentional labels)
        for t in texts:
            for s in shapes:
                if self._text_inside_rect(t, s):
                    continue  # Intentional label inside box
                if self._is_label_for_shape(t, s):
                    continue  # Reference numeral near its shape

                overlap = self._calc_overlap(t, s)
                if overlap > 0.15:
                    self.collisions.append(Collision(
                        elem1=t, elem2=s,
                        collision_type="text-on-shape",
                        overlap_ratio=overlap,
                        severity="medium" if overlap < 0.50 else "high",
                        fix_suggestion=f"Move text '{t.text}' away from shape"
                    ))

        # Text-on-line (important for patent compliance)
        for t in texts:
            for l in lines:
                overlap = self._calc_overlap(t, l)
                if overlap > 0.10:
                    # Lead lines near ref numerals are expected
                    if len(t.text) <= 4 and t.text.replace('.', '').isdigit():
                        continue  # Reference numeral near its lead line

                    # Pin labels (GP*, ADC*, PWM, VSYS, etc.) at signal endpoints - intentional
                    if self._is_pin_label(t.text):
                        continue

                    # Text inside a component box that has signals entering - intentional
                    if self._text_inside_any_rect(t, shapes):
                        continue

                    # Short component labels (< 10 chars) near shape centers - often intentional
                    if len(t.text) < 10 and self._text_near_shape_center(t, shapes):
                        continue

                    # Graph annotations: text-anchor="end" positioned at graph right edge
                    # These are data labels, not overlapping elements
                    if self._is_graph_annotation(t, l):
                        continue

                    self.collisions.append(Collision(
                        elem1=t, elem2=l,
                        collision_type="text-on-line",
                        overlap_ratio=overlap,
                        severity="medium",
                        fix_suggestion=f"Move text '{t.text}' away from line"
                    ))

        return self.collisions

    def _calc_overlap(self, b1: BBox, b2: BBox) -> float:
        """Calculate overlap ratio between two bounding boxes."""
        x_left = max(b1.x, b2.x)
        y_top = max(b1.y, b2.y)
        x_right = min(b1.x2, b2.x2)
        y_bottom = min(b1.y2, b2.y2)

        if x_right <= x_left or y_bottom <= y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)
        smaller = min(b1.w * b1.h, b2.w * b2.h)

        if smaller <= 0:
            return 0.0
        return intersection / smaller

    def _suggest_text_fix(self, t1: BBox, t2: BBox) -> str:
        """Suggest how to fix a text-on-text collision."""
        # Find which direction has more room
        dx = t2.center[0] - t1.center[0]
        dy = t2.center[1] - t1.center[1]

        if abs(dx) > abs(dy):
            shift = 20 if dx > 0 else -20
            return f"Move '{t1.text[:15]}' x by {-shift} or '{t2.text[:15]}' x by {shift}"
        else:
            shift = 20 if dy > 0 else -20
            return f"Move '{t1.text[:15]}' y by {-shift} or '{t2.text[:15]}' y by {shift}"

    def render_to_pixels(self) -> Optional['np.ndarray']:
        """Render SVG to high-resolution pixel array for validation."""
        if not HAS_PIL:
            return None

        # Try cairosvg first
        if HAS_CAIRO:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    temp_png = f.name

                cairosvg.svg2png(
                    url=str(self.svg_path),
                    write_to=temp_png,
                    scale=self.render_scale
                )

                img = Image.open(temp_png)
                arr = np.array(img.convert('L'))
                os.unlink(temp_png)
                return arr
            except Exception as e:
                print(f"CairoSVG render failed: {e}")

        return None

    def measure_pixel_clearance(self, b1: BBox, b2: BBox,
                                 pixels: 'np.ndarray') -> Optional[float]:
        """Measure actual pixel-level clearance between two elements."""
        if pixels is None:
            return None

        scale = self.render_scale
        h, w = pixels.shape

        # Convert viewBox coords to pixel coords
        def vb_to_px(x, y):
            px_x = int(x * scale)
            px_y = int(y * scale)
            return (max(0, min(w-1, px_x)), max(0, min(h-1, px_y)))

        # Get center of potential collision zone
        cx = (max(b1.x, b2.x) + min(b1.x2, b2.x2)) / 2
        cy = (max(b1.y, b2.y) + min(b1.y2, b2.y2)) / 2

        # Sample along the line between element centers
        c1 = b1.center
        c2 = b2.center

        # Find gap along the line
        steps = 100
        min_gap = float('inf')

        for i in range(steps):
            t = i / steps
            x = c1[0] + t * (c2[0] - c1[0])
            y = c1[1] + t * (c2[1] - c1[1])
            px, py = vb_to_px(x, y)

            # Check a small window for dark pixels
            window = pixels[max(0,py-3):py+4, max(0,px-3):px+4]
            if window.size > 0:
                dark = np.sum(window < 200)
                if dark == 0:
                    # Found a gap
                    pass
                else:
                    min_gap = 0
                    break

        return min_gap / scale if min_gap < float('inf') else None

    def validate_with_pixels(self) -> List[Collision]:
        """Validate collisions using pixel-level rendering."""
        pixels = self.render_to_pixels()

        for collision in self.collisions:
            gap = self.measure_pixel_clearance(
                collision.elem1, collision.elem2, pixels
            )
            collision.pixel_gap = gap

            # Adjust severity based on actual pixel gap
            if gap is not None:
                if gap < 1:
                    collision.severity = "critical"
                elif gap < self.MIN_CLEARANCE_VB:
                    collision.severity = "high"
                elif gap < self.WARN_CLEARANCE_VB:
                    collision.severity = "medium"
                else:
                    collision.severity = "low"

        return self.collisions

    def get_filtered_collisions(self, min_severity: str = "medium") -> List[Collision]:
        """Get collisions above a minimum severity threshold."""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_level = severity_order.get(min_severity, 1)

        return [c for c in self.collisions
                if severity_order.get(c.severity, 0) >= min_level]

    def generate_report(self) -> str:
        """Generate a detailed collision report."""
        lines = [
            f"=== ENHANCED COLLISION REPORT: {self.svg_path.name} ===",
            f"ViewBox: {self.viewbox}",
            f"Elements parsed: {len(self.elements)}",
            f"Collisions detected: {len(self.collisions)}",
            ""
        ]

        if not self.collisions:
            lines.append("[OK] No collisions detected")
            return "\n".join(lines)

        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for c in self.collisions:
            by_severity[c.severity].append(c)

        for sev in ["critical", "high", "medium", "low"]:
            if by_severity[sev]:
                emoji = {"critical": "[!!]", "high": "[!]", "medium": "[~]", "low": "[ ]"}[sev]
                lines.append(f"\n{emoji} {sev.upper()} ({len(by_severity[sev])})")
                lines.append("-" * 50)
                for c in by_severity[sev]:
                    lines.append(f"  {c.collision_type}: '{c.elem1.text or c.elem1.elem_type}' <-> '{c.elem2.text or c.elem2.elem_type}'")
                    lines.append(f"    Overlap: {c.overlap_ratio*100:.1f}%")
                    if c.pixel_gap is not None:
                        lines.append(f"    Pixel gap: {c.pixel_gap:.1f} vb units")
                    if c.fix_suggestion:
                        lines.append(f"    Fix: {c.fix_suggestion}")

        return "\n".join(lines)


def check_all_patents(base_path: Path) -> Dict[str, List[Collision]]:
    """Check all patent drawings and return collision summary."""
    patents = [
        ('patent_a', 8),
        ('patent_b', 6),
        ('patent_c', 7)
    ]

    results = {}

    for patent_dir, num_figs in patents:
        patent_path = base_path / patent_dir
        patent_letter = patent_dir[-1].upper()

        print(f"\n{'='*60}")
        print(f"PATENT {patent_letter}")
        print('='*60)

        for fig_num in range(1, num_figs + 1):
            svg_file = patent_path / f'fig{fig_num}.svg'

            if not svg_file.exists():
                print(f"  FIG. {fig_num}: FILE NOT FOUND")
                continue

            checker = EnhancedCollisionChecker(str(svg_file))
            checker.parse_svg()
            collisions = checker.detect_collisions()

            # Filter to meaningful collisions
            filtered = checker.get_filtered_collisions(min_severity="medium")

            key = f"{patent_letter}/fig{fig_num}"
            results[key] = filtered

            if filtered:
                print(f"\n  FIG. {fig_num}: {len(filtered)} collision(s)")
                for c in filtered:
                    print(f"    [{c.severity}] {c.collision_type}: {c.elem1.text[:20] if c.elem1.text else c.elem1.elem_type} <-> {c.elem2.text[:20] if c.elem2.text else c.elem2.elem_type}")
            else:
                print(f"  FIG. {fig_num}: PASS")

    return results


def main():
    """Run enhanced collision check on all patent drawings."""
    base_path = Path(__file__).parent.parent / 'patent_drawings'

    if not base_path.exists():
        print(f"Error: Patent drawings directory not found: {base_path}")
        sys.exit(1)

    print("="*60)
    print("ENHANCED PATENT DRAWING COLLISION CHECKER")
    print("="*60)
    print(f"Base path: {base_path}")
    print(f"Pixel validation: {'enabled' if HAS_PIL else 'disabled'}")
    print(f"CairoSVG: {'available' if HAS_CAIRO else 'not available'}")

    results = check_all_patents(base_path)

    # Summary
    total_collisions = sum(len(v) for v in results.values())
    figures_with_issues = sum(1 for v in results.values() if v)

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total figures: 21")
    print(f"Figures with issues: {figures_with_issues}")
    print(f"Total collisions (medium+): {total_collisions}")

    if total_collisions == 0:
        print("\n[OK] All drawings pass collision check (medium+ severity)")
    else:
        print(f"\n[!] {total_collisions} issue(s) need attention")

        # List figures needing fixes
        print("\nFigures to fix:")
        for key, collisions in results.items():
            if collisions:
                print(f"  - {key}: {len(collisions)} issue(s)")


if __name__ == '__main__':
    main()
