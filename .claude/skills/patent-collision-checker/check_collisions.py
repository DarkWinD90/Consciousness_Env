#!/usr/bin/env python3
"""
USPTO Patent Drawing Collision Checker

Detects overlapping elements in SVG patent drawings that violate
37 CFR 1.84(p)(1) legibility requirements.

Collision types:
  - text-on-text: Two text bounding boxes overlap
  - text-on-shape: Text overlaps a rect, circle, or line
  - shape-on-shape: Two shapes overlap unexpectedly
  - boundary-clip: Element extends outside drawing area or parent container

Usage:
    python check_collisions.py [--all] [--patent a|b|c] [--file PATH]
    python check_collisions.py --all --json   # machine-readable output
"""

import argparse
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VIEWBOX_W, VIEWBOX_H = 850, 1100
MARGIN = 50  # minimum distance from edge for content
OVERLAP_THRESHOLD = 0.10  # 10% overlap triggers a collision
CHAR_WIDTH_FACTOR = 0.6  # approximate char width as fraction of font-size
CHAR_WIDTH_FACTOR_MONO = 0.6  # monospace is slightly wider per char
TEXT_HEIGHT_FACTOR = 1.2  # line height relative to font-size

# Patent drawing directories (relative to repo root)
PATENT_DIRS = {
    'a': 'patent_drawings/patent_a',
    'b': 'patent_drawings/patent_b',
    'c': 'patent_drawings/patent_c',
}

SVG_NS = '{http://www.w3.org/2000/svg}'


# ---------------------------------------------------------------------------
# Bounding Box Helpers
# ---------------------------------------------------------------------------

class BBox:
    """Axis-aligned bounding box."""
    __slots__ = ('x1', 'y1', 'x2', 'y2', 'label', 'kind', 'elem_id')

    def __init__(self, x1, y1, x2, y2, label='', kind='unknown', elem_id=''):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.label = label
        self.kind = kind  # 'text', 'rect', 'circle', 'line', 'polyline', 'ellipse', 'polygon'
        self.elem_id = elem_id

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    @property
    def area(self):
        return max(0, self.width) * max(0, self.height)

    def intersection(self, other):
        """Return intersection BBox, or None if no overlap."""
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)
        if ix1 < ix2 and iy1 < iy2:
            return BBox(ix1, iy1, ix2, iy2)
        return None

    def overlap_ratio(self, other):
        """Overlap area / smaller element area."""
        isect = self.intersection(other)
        if isect is None:
            return 0.0
        smaller = min(self.area, other.area)
        if smaller <= 0:
            return 0.0
        return isect.area / smaller

    def __repr__(self):
        return f'BBox({self.x1:.0f},{self.y1:.0f},{self.x2:.0f},{self.y2:.0f} "{self.label}" {self.kind})'


# ---------------------------------------------------------------------------
# SVG Element Extraction
# ---------------------------------------------------------------------------

def _float(val, default=0.0):
    """Safely parse a float from an SVG attribute."""
    if val is None:
        return default
    try:
        return float(val.replace('px', '').replace('pt', ''))
    except (ValueError, TypeError):
        return default


def _estimate_text_width(text_content, font_size, font_family=''):
    """Estimate text width in SVG units based on character count and font."""
    if not text_content:
        return 0
    factor = CHAR_WIDTH_FACTOR_MONO if 'mono' in font_family.lower() or 'courier' in font_family.lower() else CHAR_WIDTH_FACTOR
    return len(text_content) * font_size * factor


def _parse_rotate_transform(transform_str):
    """Parse rotate(angle, cx, cy) or rotate(angle cx cy) from transform attr."""
    if not transform_str:
        return None
    m = re.search(r'rotate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)', transform_str)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    m = re.search(r'rotate\(\s*(-?[\d.]+)\s*\)', transform_str)
    if m:
        return float(m.group(1)), 0.0, 0.0
    return None


def _rotated_bbox(x, y, w, h, angle, cx, cy):
    """Compute axis-aligned bounding box of a rotated rectangle."""
    rad = math.radians(angle)
    cos_a = abs(math.cos(rad))
    sin_a = abs(math.sin(rad))

    # Corners of original rect relative to center
    corners = [
        (x, y - h),       # top-left (text baseline is bottom)
        (x + w, y - h),   # top-right
        (x + w, y),       # bottom-right
        (x, y),           # bottom-left
    ]

    # Rotate each corner around (cx, cy)
    rotated = []
    for px, py in corners:
        dx, dy = px - cx, py - cy
        rx = cx + dx * math.cos(rad) - dy * math.sin(rad)
        ry = cy + dx * math.sin(rad) + dy * math.cos(rad)
        rotated.append((rx, ry))

    xs = [p[0] for p in rotated]
    ys = [p[1] for p in rotated]
    return min(xs), min(ys), max(xs), max(ys)


def _parse_translate(transform_str):
    """Parse translate(x, y) from a transform attribute."""
    if not transform_str:
        return 0.0, 0.0
    m = re.search(r'translate\(\s*(-?[\d.]+)[,\s]+(-?[\d.]+)\s*\)', transform_str)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r'translate\(\s*(-?[\d.]+)\s*\)', transform_str)
    if m:
        return float(m.group(1)), 0.0
    return 0.0, 0.0


def extract_bboxes(svg_path):
    """Parse an SVG file and return a list of BBox objects for all elements."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    bboxes = []

    def tag(elem):
        return elem.tag.replace(SVG_NS, '')

    def _walk(parent, dx=0.0, dy=0.0):
        """Recursively walk the SVG tree, accumulating g-transform offsets."""
        for elem in parent:
            t = tag(elem)
            # Handle <g transform="translate(...)"> by accumulating offset
            if t == 'g':
                gdx, gdy = _parse_translate(elem.get('transform', ''))
                yield from _walk(elem, dx + gdx, dy + gdy)
                continue
            yield elem, dx, dy

    idx = 0
    for elem, dx, dy in _walk(root):
        t = tag(elem)
        eid = f'{t}_{idx}'
        idx += 1

        if t == 'text':
            text_content = (elem.text or '').strip()
            # Also check for tspan children
            for child in elem:
                if tag(child) == 'tspan' and child.text:
                    text_content += child.text.strip()
            if not text_content:
                continue

            x = _float(elem.get('x')) + dx
            y = _float(elem.get('y')) + dy
            font_size = _float(elem.get('font-size'), 14)
            font_family = elem.get('font-family', '')
            text_anchor = elem.get('text-anchor', 'start')
            transform = elem.get('transform', '')

            w = _estimate_text_width(text_content, font_size, font_family)
            h = font_size * TEXT_HEIGHT_FACTOR

            # Adjust x based on text-anchor
            if text_anchor == 'middle':
                x -= w / 2
            elif text_anchor == 'end':
                x -= w

            # Handle rotation (apply g-offset to rotation center too)
            rotation = _parse_rotate_transform(transform)
            if rotation:
                angle, cx, cy = rotation
                cx += dx
                cy += dy
                bx1, by1, bx2, by2 = _rotated_bbox(x, y, w, h, angle, cx, cy)
                bboxes.append(BBox(bx1, by1, bx2, by2,
                                   label=text_content, kind='text', elem_id=eid))
            else:
                bboxes.append(BBox(x, y - h, x + w, y,
                                   label=text_content, kind='text', elem_id=eid))

        elif t == 'rect':
            x = _float(elem.get('x')) + dx
            y = _float(elem.get('y')) + dy
            w = _float(elem.get('width'))
            h = _float(elem.get('height'))
            if w > 0 and h > 0:
                # Skip the full-page background rect
                if w >= VIEWBOX_W - 10 and h >= VIEWBOX_H - 10:
                    continue
                bboxes.append(BBox(x, y, x + w, y + h,
                                   label=f'rect@({x:.0f},{y:.0f})',
                                   kind='rect', elem_id=eid))

        elif t == 'circle':
            cx = _float(elem.get('cx')) + dx
            cy = _float(elem.get('cy')) + dy
            r = _float(elem.get('r'))
            if r > 0:
                bboxes.append(BBox(cx - r, cy - r, cx + r, cy + r,
                                   label=f'circle@({cx:.0f},{cy:.0f})',
                                   kind='circle', elem_id=eid))

        elif t == 'ellipse':
            cx = _float(elem.get('cx')) + dx
            cy = _float(elem.get('cy')) + dy
            rx = _float(elem.get('rx'))
            ry = _float(elem.get('ry'))
            if rx > 0 and ry > 0:
                bboxes.append(BBox(cx - rx, cy - ry, cx + rx, cy + ry,
                                   label=f'ellipse@({cx:.0f},{cy:.0f})',
                                   kind='ellipse', elem_id=eid))

        elif t == 'line':
            x1 = _float(elem.get('x1')) + dx
            y1 = _float(elem.get('y1')) + dy
            x2 = _float(elem.get('x2')) + dx
            y2 = _float(elem.get('y2')) + dy
            sw = _float(elem.get('stroke-width'), 1) + 2  # buffer
            bboxes.append(BBox(min(x1, x2) - sw, min(y1, y2) - sw,
                               max(x1, x2) + sw, max(y1, y2) + sw,
                               label=f'line({x1:.0f},{y1:.0f})-({x2:.0f},{y2:.0f})',
                               kind='line', elem_id=eid))

        elif t == 'polyline':
            points_str = elem.get('points', '')
            coords = re.findall(r'(-?[\d.]+)', points_str)
            if len(coords) >= 4:
                xs = [float(coords[i]) + dx for i in range(0, len(coords), 2)]
                ys = [float(coords[i]) + dy for i in range(1, len(coords), 2)]
                bboxes.append(BBox(min(xs), min(ys), max(xs), max(ys),
                                   label='polyline', kind='polyline', elem_id=eid))

        elif t == 'polygon':
            points_str = elem.get('points', '')
            coords = re.findall(r'(-?[\d.]+)', points_str)
            if len(coords) >= 4:
                xs = [float(coords[i]) + dx for i in range(0, len(coords), 2)]
                ys = [float(coords[i]) + dy for i in range(1, len(coords), 2)]
                bboxes.append(BBox(min(xs), min(ys), max(xs), max(ys),
                                   label='polygon', kind='polygon', elem_id=eid))

        elif t == 'path':
            d = elem.get('d', '')
            nums = re.findall(r'(-?[\d.]+)', d)
            if len(nums) >= 4:
                # Extract pairs as approximate coordinates
                pairs = [(float(nums[i]) + dx, float(nums[i+1]) + dy)
                         for i in range(0, len(nums) - 1, 2)]
                if pairs:
                    xs = [p[0] for p in pairs]
                    ys = [p[1] for p in pairs]
                    bboxes.append(BBox(min(xs), min(ys), max(xs), max(ys),
                                       label='path', kind='path', elem_id=eid))

    return bboxes


# ---------------------------------------------------------------------------
# Collision Detection
# ---------------------------------------------------------------------------

def _is_short_line(b, max_len=30):
    """Check if a bbox represents a short line (tick mark, small connector)."""
    return b.kind == 'line' and max(b.width, b.height) < max_len


def _perp_distance_to_line(text_bb, line_bb):
    """Compute perpendicular distance from text center to the actual line segment.

    Returns the distance, or None if the line label can't be parsed.
    For diagonal lines, the axis-aligned bbox is much larger than the line's
    visual footprint, so bbox overlap is misleading.  This function computes
    the true geometric distance.
    """
    import math
    m = re.match(r'^line\((-?[\d.]+),(-?[\d.]+)\)-\((-?[\d.]+),(-?[\d.]+)\)$', line_bb.label)
    if not m:
        return None
    lx1, ly1, lx2, ly2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    tx = (text_bb.x1 + text_bb.x2) / 2
    ty = (text_bb.y1 + text_bb.y2) / 2
    dx, dy = lx2 - lx1, ly2 - ly1
    line_len_sq = dx * dx + dy * dy
    if line_len_sq == 0:
        return math.hypot(tx - lx1, ty - ly1)
    t = max(0, min(1, ((tx - lx1) * dx + (ty - ly1) * dy) / line_len_sq))
    px, py = lx1 + t * dx, ly1 + t * dy
    return math.hypot(tx - px, ty - py)


def _text_is_line_label(text_bb, line_bb, tolerance=40):
    """Check if text is a label for a line (positioned near an endpoint).

    Patent drawings commonly place labels next to arrows and connectors.
    This detects transition labels (e.g., "208" near a state arrow) and
    graph threshold labels ("CRITICAL" at start of a grid line).

    Checks the closest point of the text bbox to each line endpoint,
    not just the text center, because text-anchor=start/end places the
    anchor edge near the endpoint while the center is further away.
    """
    import math
    m = re.match(r'^line\((-?[\d.]+),(-?[\d.]+)\)-\((-?[\d.]+),(-?[\d.]+)\)$', line_bb.label)
    if not m:
        return False
    lx1, ly1, lx2, ly2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    # Check all 4 corners + center of text bbox against each endpoint
    points = [
        ((text_bb.x1 + text_bb.x2) / 2, (text_bb.y1 + text_bb.y2) / 2),  # center
        (text_bb.x1, text_bb.y1),  # top-left
        (text_bb.x2, text_bb.y1),  # top-right
        (text_bb.x1, text_bb.y2),  # bottom-left
        (text_bb.x2, text_bb.y2),  # bottom-right
    ]
    for px, py in points:
        d1 = math.hypot(px - lx1, py - ly1)
        d2 = math.hypot(px - lx2, py - ly2)
        if min(d1, d2) <= tolerance:
            return True
    return False


def _is_connector_line(line_bb, shape_bb, tolerance=20):
    """Check if a line connects to a shape (arrow endpoint near shape edge)."""
    if line_bb.kind != 'line':
        return False
    if shape_bb.kind not in ('rect', 'circle', 'ellipse', 'polygon'):
        return False
    # Check if either line endpoint (approximated from bbox extremes) is near shape edge
    # For vertical lines, endpoints are at (mid_x, y1) and (mid_x, y2)
    # For horizontal lines, endpoints are at (x1, mid_y) and (x2, mid_y)
    lx = (line_bb.x1 + line_bb.x2) / 2
    ly = (line_bb.y1 + line_bb.y2) / 2
    # Near top/bottom edge
    if (shape_bb.x1 - tolerance <= lx <= shape_bb.x2 + tolerance):
        if abs(ly - shape_bb.y1) < tolerance or abs(ly - shape_bb.y2) < tolerance:
            return True
        # Also check line's actual y endpoints against shape edges
        for ey in [line_bb.y1, line_bb.y2]:
            if abs(ey - shape_bb.y1) < tolerance or abs(ey - shape_bb.y2) < tolerance:
                if shape_bb.x1 - tolerance <= lx <= shape_bb.x2 + tolerance:
                    return True
    # Near left/right edge
    if (shape_bb.y1 - tolerance <= ly <= shape_bb.y2 + tolerance):
        if abs(lx - shape_bb.x1) < tolerance or abs(lx - shape_bb.x2) < tolerance:
            return True
        # Also check line's actual x endpoints
        for ex in [line_bb.x1, line_bb.x2]:
            if abs(ex - shape_bb.x1) < tolerance or abs(ex - shape_bb.x2) < tolerance:
                if shape_bb.y1 - tolerance <= ly <= shape_bb.y2 + tolerance:
                    return True
    return False


def _is_label_for_shape(text_bb, shape_bb, max_dist=40):
    """Check if text is a label/numeral positioned just outside a shape."""
    # Reference numerals and labels are typically placed just outside their shape
    tx = (text_bb.x1 + text_bb.x2) / 2
    ty = (text_bb.y1 + text_bb.y2) / 2
    # Check if text center is within max_dist of any shape edge
    near_h = shape_bb.x1 - max_dist <= tx <= shape_bb.x2 + max_dist
    near_v = shape_bb.y1 - max_dist <= ty <= shape_bb.y2 + max_dist
    # Text is just above, below, left, or right of shape
    just_outside_top = near_h and shape_bb.y1 - max_dist <= ty <= shape_bb.y1
    just_outside_bot = near_h and shape_bb.y2 <= ty <= shape_bb.y2 + max_dist
    just_outside_left = near_v and shape_bb.x1 - max_dist <= tx <= shape_bb.x1
    just_outside_right = near_v and shape_bb.x2 <= tx <= shape_bb.x2 + max_dist
    return just_outside_top or just_outside_bot or just_outside_left or just_outside_right


def _text_is_inside(text_bb, container_bb, margin=5):
    """Check if text bbox is inside a container (rect, circle, ellipse)."""
    return (container_bb.x1 - margin <= text_bb.x1 and
            container_bb.y1 - margin <= text_bb.y1 and
            container_bb.x2 + margin >= text_bb.x2 and
            container_bb.y2 + margin >= text_bb.y2)


def _text_center_in_circle(text_bb, circ_bb, margin=10):
    """Check if text center is inside a circular/elliptical shape."""
    cx = (circ_bb.x1 + circ_bb.x2) / 2
    cy = (circ_bb.y1 + circ_bb.y2) / 2
    rx = (circ_bb.x2 - circ_bb.x1) / 2 + margin
    ry = (circ_bb.y2 - circ_bb.y1) / 2 + margin
    tx = (text_bb.x1 + text_bb.x2) / 2
    ty = (text_bb.y1 + text_bb.y2) / 2
    if rx > 0 and ry > 0:
        return ((tx - cx) / rx) ** 2 + ((ty - cy) / ry) ** 2 <= 1
    return False


def _find_containing_circle(text_bb, bboxes):
    """Return the circle/ellipse bbox that contains the text center, or None."""
    for bb in bboxes:
        if bb.kind in ('circle', 'ellipse') and _text_center_in_circle(text_bb, bb):
            return bb
    return None


def _should_skip_pair(a, b, all_bboxes=None):
    """Skip known non-collision pairs (intentional overlaps in patent drawings)."""
    # Skip line-on-line (axes, gridlines, arrows commonly share endpoints)
    if a.kind == 'line' and b.kind == 'line':
        return True
    # Skip all polyline overlaps (chart data lines span graph area intentionally)
    if a.kind == 'polyline' or b.kind == 'polyline':
        return True
    # Skip path elements (cloud shapes, bezier curves span large areas)
    if a.kind == 'path' or b.kind == 'path':
        return True
    # Skip very small elements (markers, arrowheads, tiny tick marks)
    if a.area < 50 or b.area < 50:
        return True
    # Skip short tick-mark lines vs everything
    if _is_short_line(a) or _is_short_line(b):
        return True
    # Skip connector lines touching shapes (arrows into/out of boxes/circles)
    if _is_connector_line(a, b) or _is_connector_line(b, a):
        return True
    # Skip text INSIDE a rect (intentional label containment)
    if a.kind == 'rect' and b.kind == 'text' and _text_is_inside(b, a):
        return True
    if b.kind == 'rect' and a.kind == 'text' and _text_is_inside(a, b):
        return True
    # Skip text inside circles/ellipses (state labels)
    if a.kind in ('circle', 'ellipse') and b.kind == 'text':
        if _text_center_in_circle(b, a):
            return True
    if b.kind in ('circle', 'ellipse') and a.kind == 'text':
        if _text_center_in_circle(a, b):
            return True
    # Skip rect-on-rect if one is fully inside the other (nested containers)
    if a.kind == 'rect' and b.kind == 'rect':
        if _text_is_inside(a, b) or _text_is_inside(b, a):
            return True
    # Skip small circles inside large rects (e.g., neuron circles inside SNN box)
    if a.kind == 'rect' and b.kind == 'circle':
        if a.area > 5000 and b.area < 1000 and _text_is_inside(b, a, margin=10):
            return True
    if b.kind == 'rect' and a.kind == 'circle':
        if b.area > 5000 and a.area < 1000 and _text_is_inside(a, b, margin=10):
            return True
    # Skip polygon elements overlapping adjacent shapes (diamond decision nodes)
    if a.kind == 'polygon' or b.kind == 'polygon':
        return True
    # Skip reference numerals positioned just outside their labeled shape
    if a.kind == 'text' and b.kind in ('rect', 'circle', 'ellipse'):
        # Check if this looks like a reference numeral (2-3 digit number)
        if re.match(r'^\d{2,3}$', a.label):
            if _is_label_for_shape(a, b):
                return True
    if b.kind == 'text' and a.kind in ('rect', 'circle', 'ellipse'):
        if re.match(r'^\d{2,3}$', b.label):
            if _is_label_for_shape(b, a):
                return True
    # Skip text-on-line when the text is NOT visually near the line stroke.
    # Diagonal lines have large axis-aligned bboxes that enclose text far from
    # the actual stroke.  Use perpendicular distance to distinguish real visual
    # overlap (text crossing/sitting on the line) from incidental bbox overlap.
    # Also skip: labels near endpoints, reference numerals for lines, minor overlap,
    # and single-char symbols inside circles (junction markers like "+").
    if a.kind == 'line' and b.kind == 'text':
        perp = _perp_distance_to_line(b, a)
        if perp is not None and perp > 20:
            return True  # text is far from actual stroke — bbox artifact
        if a.overlap_ratio(b) < 0.25 or _text_is_line_label(b, a):
            return True
        if re.match(r'^\d{2,3}$', b.label):
            return True  # reference numeral labeling the line element
        if len(b.label) <= 2 and all_bboxes is not None:
            circ = _find_containing_circle(b, all_bboxes)
            if circ is not None and a.intersection(circ) is not None:
                return True  # symbol inside a circle that the line intersects
    if b.kind == 'line' and a.kind == 'text':
        perp = _perp_distance_to_line(a, b)
        if perp is not None and perp > 20:
            return True  # text is far from actual stroke — bbox artifact
        if b.overlap_ratio(a) < 0.25 or _text_is_line_label(a, b):
            return True
        if re.match(r'^\d{2,3}$', a.label):
            return True  # reference numeral labeling the line element
        if len(a.label) <= 2 and all_bboxes is not None:
            circ = _find_containing_circle(a, all_bboxes)
            if circ is not None and b.intersection(circ) is not None:
                return True  # symbol inside a circle that the line intersects
    # Skip multi-line text labels (two text elements stacked vertically for one label)
    if a.kind == 'text' and b.kind == 'text':
        # If two text elements have similar x centers and y-diff <= 20, it's a multi-line label
        ax = (a.x1 + a.x2) / 2
        bx = (b.x1 + b.x2) / 2
        if abs(ax - bx) < 30:  # Similar horizontal position
            ay_bot = a.y2
            by_top = b.y1
            by_bot = b.y2
            ay_top = a.y1
            # Check if they're stacked with small gap
            if 0 <= by_top - ay_bot <= 5 or 0 <= ay_top - by_bot <= 5:
                return True
        # Also skip if overlap is very small — borderline text width estimation error
        if a.overlap_ratio(b) < 0.12:
            return True
    # Skip lines inside or at edge of rects (legend lines, internal dividers, connector arrows)
    if a.kind == 'rect' and b.kind == 'line':
        margin = 5
        if (a.x1 - margin <= b.x1 and a.y1 - margin <= b.y1 and
                a.x2 + margin >= b.x2 and a.y2 + margin >= b.y2):
            return True
    if b.kind == 'rect' and a.kind == 'line':
        margin = 5
        if (b.x1 - margin <= a.x1 and b.y1 - margin <= a.y1 and
                b.x2 + margin >= a.x2 and b.y2 + margin >= a.y2):
            return True
    # Skip text labels that are NEAR their own small rect (label boxes with text outside)
    if a.kind == 'text' and b.kind == 'rect':
        if b.area < 5000 and _is_label_for_shape(a, b, max_dist=25):
            return True
    if b.kind == 'text' and a.kind == 'rect':
        if a.area < 5000 and _is_label_for_shape(b, a, max_dist=25):
            return True
    # Skip text-on-shape where the full text bbox is inside the rect
    # Use 10px margin to account for text width estimation error.
    # Tighter margin ensures text that overflows a narrow box is still flagged.
    if a.kind == 'text' and b.kind == 'rect':
        if _text_is_inside(a, b, margin=10):
            return True
    if b.kind == 'text' and a.kind == 'rect':
        if _text_is_inside(b, a, margin=10):
            return True
    # Skip circle-on-line overlaps where circle is at line endpoint (start/end marker)
    if a.kind == 'circle' and b.kind == 'line':
        cx = (a.x1 + a.x2) / 2
        cy = (a.y1 + a.y2) / 2
        r = (a.x2 - a.x1) / 2
        if r < 15:  # small circle (marker dot)
            return True
    if b.kind == 'circle' and a.kind == 'line':
        cx = (b.x1 + b.x2) / 2
        cy = (b.y1 + b.y2) / 2
        r = (b.x2 - b.x1) / 2
        if r < 15:
            return True
    return False


def _collision_type(a, b):
    """Classify the collision type."""
    if a.kind == 'text' and b.kind == 'text':
        return 'text-on-text'
    if 'text' in (a.kind, b.kind) and 'rect' in (a.kind, b.kind):
        return 'text-on-shape'
    if 'text' in (a.kind, b.kind) and 'line' in (a.kind, b.kind):
        return 'text-on-line'
    if 'text' in (a.kind, b.kind) and b.kind in ('circle', 'ellipse', 'polygon'):
        return 'text-on-shape'
    if a.kind == 'text' and b.kind in ('circle', 'ellipse', 'polygon'):
        return 'text-on-shape'
    if a.kind == 'rect' and b.kind == 'rect':
        return 'shape-on-shape'
    if 'text' in (a.kind, b.kind) and 'polyline' in (a.kind, b.kind):
        return 'text-on-line'
    return 'element-overlap'


def detect_collisions(bboxes, threshold=OVERLAP_THRESHOLD):
    """Find all overlapping pairs above the threshold."""
    collisions = []
    n = len(bboxes)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = bboxes[i], bboxes[j]
            if _should_skip_pair(a, b, all_bboxes=bboxes):
                continue
            ratio = a.overlap_ratio(b)
            if ratio >= threshold:
                ctype = _collision_type(a, b)
                collisions.append({
                    'a': a,
                    'b': b,
                    'overlap': ratio,
                    'type': ctype,
                })
    return collisions


def detect_boundary_clips(bboxes, margin=MARGIN):
    """Find elements that extend outside the safe drawing area."""
    clips = []
    safe = BBox(margin, margin, VIEWBOX_W - margin, VIEWBOX_H - margin)
    for b in bboxes:
        # Only check meaningful elements (skip tiny markers)
        if b.area < 50:
            continue
        if b.kind in ('line', 'polyline', 'path', 'polygon'):
            continue
        # Skip page numbers (e.g., "1/7", "2/8") — intentionally in top margin
        if b.kind == 'text' and re.match(r'^\d+/\d+$', b.label):
            continue
        # Skip rects that are intentional background/container elements
        if b.kind == 'rect' and b.area > 100000:
            continue
        if b.x1 < safe.x1 or b.y1 < safe.y1 or b.x2 > safe.x2 or b.y2 > safe.y2:
            clips.append({
                'bbox': b,
                'type': 'boundary-clip',
                'detail': f'{b.kind} "{b.label}" extends outside margin '
                          f'(bbox: {b.x1:.0f},{b.y1:.0f} to {b.x2:.0f},{b.y2:.0f})'
            })
    return clips


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def check_svg(svg_path, patent_label='', fig_label=''):
    """Run full collision check on a single SVG file."""
    bboxes = extract_bboxes(svg_path)
    collisions = detect_collisions(bboxes)
    clips = detect_boundary_clips(bboxes)
    return {
        'file': svg_path,
        'patent': patent_label,
        'figure': fig_label,
        'elements': len(bboxes),
        'collisions': collisions,
        'clips': clips,
    }


def print_report(results):
    """Print human-readable collision report."""
    total_collisions = 0
    total_clips = 0

    for r in results:
        header = f"=== {r['patent'].upper()} — {r['figure']} ({os.path.basename(r['file'])}) ==="
        collisions = r['collisions']
        clips = r['clips']

        if not collisions and not clips:
            continue

        print(header)
        print(f"    Elements scanned: {r['elements']}")

        for c in collisions:
            a, b = c['a'], c['b']
            print(f"  [!] COLLISION: {a.kind} \"{a.label}\" overlaps {b.kind} \"{b.label}\"")
            print(f"      Overlap: {c['overlap']:.0%} | Type: {c['type']}")
            total_collisions += 1

        for cl in clips:
            print(f"  [!] CLIP: {cl['detail']}")
            total_clips += 1

        print()

    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Files checked: {len(results)}")
    print(f"  Collisions:    {total_collisions}")
    print(f"  Boundary clips: {total_clips}")
    print(f"  Total issues:  {total_collisions + total_clips}")
    print("=" * 60)

    if total_collisions + total_clips > 0:
        print(f"\nSTATUS: {total_collisions + total_clips} COLLISION/CLIP ISSUES FOUND")
    else:
        print("\nSTATUS: NO COLLISIONS DETECTED")

    return total_collisions + total_clips


def print_json(results):
    """Print machine-readable JSON output."""
    output = []
    for r in results:
        entry = {
            'file': r['file'],
            'patent': r['patent'],
            'figure': r['figure'],
            'elements': r['elements'],
            'collisions': [
                {
                    'a': {'label': c['a'].label, 'kind': c['a'].kind,
                          'bbox': [c['a'].x1, c['a'].y1, c['a'].x2, c['a'].y2]},
                    'b': {'label': c['b'].label, 'kind': c['b'].kind,
                          'bbox': [c['b'].x1, c['b'].y1, c['b'].x2, c['b'].y2]},
                    'overlap': round(c['overlap'], 3),
                    'type': c['type'],
                }
                for c in r['collisions']
            ],
            'clips': [
                {'label': cl['bbox'].label, 'kind': cl['bbox'].kind,
                 'detail': cl['detail'],
                 'bbox': [cl['bbox'].x1, cl['bbox'].y1, cl['bbox'].x2, cl['bbox'].y2]}
                for cl in r['clips']
            ],
        }
        output.append(entry)
    print(json.dumps(output, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_base_dir():
    """Walk up from script location to find repo root."""
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.isdir(os.path.join(d, 'patent_drawings')):
            return d
        d = os.path.dirname(d)
    return os.getcwd()


def main():
    parser = argparse.ArgumentParser(description='USPTO Patent Drawing Collision Checker')
    parser.add_argument('--all', action='store_true', help='Check all patents')
    parser.add_argument('--patent', choices=['a', 'b', 'c'], help='Check specific patent')
    parser.add_argument('--file', type=str, help='Check a single SVG file')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('--threshold', type=float, default=OVERLAP_THRESHOLD,
                        help=f'Overlap threshold (default: {OVERLAP_THRESHOLD})')
    args = parser.parse_args()

    base_dir = find_base_dir()
    results = []

    if args.file:
        r = check_svg(args.file, patent_label='?', fig_label='?')
        results.append(r)
    else:
        patents = ['a', 'b', 'c'] if args.all else ([args.patent] if args.patent else ['a', 'b', 'c'])
        for p in patents:
            pdir = os.path.join(base_dir, PATENT_DIRS[p])
            if not os.path.isdir(pdir):
                print(f"WARNING: Directory not found: {pdir}", file=sys.stderr)
                continue
            svgs = sorted(f for f in os.listdir(pdir) if f.endswith('.svg'))
            for svg_name in svgs:
                fig_num = svg_name.replace('fig', '').replace('.svg', '')
                r = check_svg(
                    os.path.join(pdir, svg_name),
                    patent_label=f'Patent {p.upper()}',
                    fig_label=f'FIG. {fig_num}',
                )
                results.append(r)

    if args.json:
        print_json(results)
    else:
        issues = print_report(results)
        sys.exit(1 if issues > 0 else 0)


if __name__ == '__main__':
    main()
