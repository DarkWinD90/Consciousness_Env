#!/usr/bin/env python3
"""Geometric collision validator for USPTO patent drawing SVGs.

Checks for issues that XML-only validators miss:
  G1: Signal-path-to-signal-path crossings
  G2: Arrow endpoints not touching target box edges
  G3: Signal paths passing through element boxes
  G4: Overlapping signal path segments
  G5: Text-text overlaps

These are the issues that repeatedly caused rejection-grade defects
in patent drawings despite passing structural compliance checks.
"""

import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class Rect:
    """An element box used as an arrow-target candidate.

    ``kind`` distinguishes three shape families:
    - "rect": axis-aligned rectangle defined by x, y, w, h.
    - "circle": true circle inscribed in the w x h bounding box
      (w == h required); center = (x + w/2, y + h/2), r = w/2.
    - "ellipse": ellipse with semi-axes rx = w/2, ry = h/2. Distance
      to boundary uses the quadratic implicit form rather than a
      circle approximation so elongated nodes (e.g., patent_c/fig7's
      BUF/SNP pills at rx=15, ry=25) report accurate gaps.
    """
    x: float
    y: float
    w: float
    h: float
    label: str = ""
    kind: str = "rect"  # "rect" | "circle" | "ellipse"

    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h

    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2
    @property
    def r(self): return self.w / 2  # only meaningful for circles
    @property
    def rx(self): return self.w / 2  # only meaningful for ellipses
    @property
    def ry(self): return self.h / 2  # only meaningful for ellipses

    def contains_point(self, px, py):
        if self.kind == "circle":
            return math.hypot(px - self.cx, py - self.cy) < self.r
        if self.kind == "ellipse" and self.rx > 0 and self.ry > 0:
            return ((px - self.cx) / self.rx) ** 2 + ((py - self.cy) / self.ry) ** 2 < 1.0
        return self.x < px < self.right and self.y < py < self.bottom

    def on_edge(self, px, py, tolerance=1.0):
        """Check if point is on the edge (within tolerance)."""
        on_left = abs(px - self.x) <= tolerance and self.y <= py <= self.bottom
        on_right = abs(px - self.right) <= tolerance and self.y <= py <= self.bottom
        on_top = abs(py - self.y) <= tolerance and self.x <= px <= self.right
        on_bottom = abs(py - self.bottom) <= tolerance and self.x <= px <= self.right
        return on_left or on_right or on_top or on_bottom

    def distance_to_edge(self, px, py):
        """Shortest distance from (px, py) to the boundary of this element.

        If the point lies inside the element, distance is 0. An arrow
        whose tip enters a target box has semantically reached the
        target; reporting a non-zero "gap" for a tip at the center of
        a rect would be a false positive (commonly seen with the
        10x10 axis-endpoint anchor rects in the Patent C figures).

        For rectangles outside the box, returns the minimum over the
        four edges, considering only edges whose perpendicular
        projection from the point lands on the edge. Returns infinity
        if the point's projection falls outside all four edge spans.

        For circles, returns ``abs(dist_to_center - r)`` when outside
        or touching, and 0 when strictly inside.

        For ellipses, evaluates the implicit quadratic form
        ``F = ((px-cx)/rx)^2 + ((py-cy)/ry)^2``. F <= 1 means the
        point is inside (distance 0). Otherwise distance is
        approximated as ``(sqrt(F) - 1) * min(rx, ry)`` — exact at
        the cardinal extremes (where arrow tips normally land) and
        slightly over-reports along diagonals. Accurate to within
        the 1.0u compliance tolerance.
        """
        if self.kind == "circle":
            dx = px - self.cx
            dy = py - self.cy
            dist_center = math.hypot(dx, dy)
            if dist_center <= self.r:
                return 0.0
            return dist_center - self.r
        if self.kind == "ellipse":
            if self.rx <= 0 or self.ry <= 0:
                return float("inf")
            f = ((px - self.cx) / self.rx) ** 2 + ((py - self.cy) / self.ry) ** 2
            if f <= 1.0:
                return 0.0
            return (math.sqrt(f) - 1.0) * min(self.rx, self.ry)
        if self.contains_point(px, py):
            return 0.0
        distances = []
        if self.x <= px <= self.right:
            distances.append(abs(py - self.y))
            distances.append(abs(py - self.bottom))
        if self.y <= py <= self.bottom:
            distances.append(abs(px - self.x))
            distances.append(abs(px - self.right))
        return min(distances) if distances else float("inf")


@dataclass
class Segment:
    """A horizontal or vertical line segment from a signal path."""
    x1: float
    y1: float
    x2: float
    y2: float
    path_id: str  # Which signal path this belongs to
    has_arrow: bool = False

    @property
    def is_horizontal(self):
        return abs(self.y1 - self.y2) < 0.5

    @property
    def is_vertical(self):
        return abs(self.x1 - self.x2) < 0.5

    @property
    def min_x(self): return min(self.x1, self.x2)
    @property
    def max_x(self): return max(self.x1, self.x2)
    @property
    def min_y(self): return min(self.y1, self.y2)
    @property
    def max_y(self): return max(self.y1, self.y2)


@dataclass
class TextBox:
    """Approximate bounding box for a text element."""
    x: float
    y: float
    width: float
    height: float
    content: str


def detect_transform_offset(content: str) -> Tuple[float, float]:
    """Detect the top-level <g transform="translate(x, y)"> offset."""
    m = re.search(r'<g\s+transform="translate\(([\d.]+)[,\s]+([\d.]+)\)"', content)
    if m:
        return float(m.group(1)), float(m.group(2))
    return 0.0, 0.0


def _attr(tag_str: str, name: str) -> Optional[str]:
    """Extract a single attribute value from an SVG tag string."""
    m = re.search(rf'{name}="([^"]*)"', tag_str)
    return m.group(1) if m else None


def _attr_f(tag_str: str, name: str, default: float = 0.0) -> float:
    """Extract a float attribute value from an SVG tag string."""
    val = _attr(tag_str, name)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def parse_rects(content: str, dx: float = 0, dy: float = 0) -> List[Rect]:
    """Extract all element boxes. Converts both ``<rect>`` and
    ``<circle>`` elements to bounding ``Rect`` instances.

    State-diagram figures (e.g., patent_c/fig2) draw their nodes as
    ``<circle>`` elements, so arrows landing on those nodes would be
    reported as G2 "gap" failures if only rects were considered. A
    circle is represented here as the axis-aligned bounding box of
    its circumscribed square (x = cx-r, y = cy-r, w = h = 2r), which
    lets ``check_arrow_endpoints`` see the circle boundary as four
    linear edges. The approximation is slightly permissive near the
    diagonals (the corner of the bbox lies ~0.41r outside the actual
    circle), but in practice arrows point at the cardinal directions
    of a node, not its 45-degree corners, so this is accurate enough
    for compliance checking.

    Ellipses are treated like circles: ``<ellipse cx cy rx ry>`` maps
    to Rect(cx-rx, cy-ry, 2*rx, 2*ry).

    Filters:
    - ``w == 0`` or ``h == 0`` are skipped (degenerate).
    - ``w > 800 or h > 800`` skipped — catches the full-page background
      ``<rect width="100%" height="100%">`` (which parses to very
      large w/h after integer coercion) and any unusually large
      container.
    - ``y > 790`` in reference-scale units is skipped to exclude
      legend boxes at the bottom of the page from being treated as
      arrow targets. This is scale-coupled — see
      docs/tooling_audit_2026-04-24.md §3 for the remaining HIGH bug.
    """
    rects = []

    for m in re.finditer(r'<rect\b([^>]*)/?>', content):
        attrs = m.group(1)
        x = _attr_f(attrs, 'x') + dx
        y = _attr_f(attrs, 'y') + dy
        w = _attr_f(attrs, 'width')
        h = _attr_f(attrs, 'height')
        if w == 0 or h == 0:
            continue
        if w > 800 or h > 800:
            continue
        # Legend-zone filter (bottom of page, y > 790). Two categories
        # of rect live in this zone and need different treatment:
        #  - Legend containers (typically w > 100) and small legend
        #    icons (w < 15 or h < 15) are decorative; skip them so
        #    they are neither G2 targets nor G3 obstacles.
        #  - Regular diagram boxes in the 15..100 size range (e.g.,
        #    flow-diagram terminal boxes in patent_c/fig5 at y=800,
        #    80x30) remain valid G2 arrow targets.
        # Above y=790, all rects are kept.
        if y > 790 and (w > 100 or h > 40 or w < 15 or h < 15):
            continue
        rects.append(Rect(x, y, w, h))

    for m in re.finditer(r'<circle\b([^>]*)/?>', content):
        attrs = m.group(1)
        cx = _attr_f(attrs, 'cx') + dx
        cy = _attr_f(attrs, 'cy') + dy
        r = _attr_f(attrs, 'r')
        if r <= 0:
            continue
        # Skip junction dots, spike-output junction markers, individual
        # neuron circles inside a layer, and leader-line anchors — none
        # of which are arrow targets in isolation. Radius threshold of
        # 12 (roughly 0.12 inch at reference scale) is chosen to admit
        # state-node circles (typically r=20..75) while rejecting
        # junction dots (r=3..8) and neuron-symbol circles (r=8..12).
        if r < 12:
            continue
        # Skip circles whose center sits in the legend zone.
        if cy > 790:
            continue
        rects.append(Rect(cx - r, cy - r, 2 * r, 2 * r, kind="circle"))

    for m in re.finditer(r'<ellipse\b([^>]*)/?>', content):
        attrs = m.group(1)
        cx = _attr_f(attrs, 'cx') + dx
        cy = _attr_f(attrs, 'cy') + dy
        rx = _attr_f(attrs, 'rx')
        ry = _attr_f(attrs, 'ry')
        if rx <= 0 or ry <= 0:
            continue
        if cy > 790:
            continue
        # Store as kind="ellipse" so Rect.distance_to_edge uses the
        # quadratic implicit form rather than the circle approximation.
        # Non-unit-aspect ellipses (rx != ry) land arrows on their
        # cardinal extremes (e.g., top of a tall pill at y=cy-ry),
        # which reads as "outside" under any circle approximation
        # but is on-boundary for the true ellipse.
        rects.append(Rect(cx - rx, cy - ry, 2 * rx, 2 * ry, kind="ellipse"))

    return rects


def parse_lines(content: str, dx: float = 0, dy: float = 0) -> List[Segment]:
    """Extract all signal path line segments (stroke-width >= 1.0)."""
    segments = []
    path_counter = 0

    for m in re.finditer(r'<line\b([^>]*)/?>', content):
        attrs = m.group(1)
        sw = _attr_f(attrs, 'stroke-width', 1.0)
        if sw < 1.0:  # Skip leader lines (0.5)
            continue

        # Skip legend lines (check surrounding context)
        line_pos = m.start()
        context_before = content[max(0, line_pos - 200):line_pos]
        if 'LEGEND' in context_before or 'SIGNAL PATHWAYS' in context_before:
            continue

        has_arrow = 'marker-end' in attrs
        seg = Segment(
            _attr_f(attrs, 'x1') + dx, _attr_f(attrs, 'y1') + dy,
            _attr_f(attrs, 'x2') + dx, _attr_f(attrs, 'y2') + dy,
            f"line_{path_counter}", has_arrow
        )
        segments.append(seg)
        path_counter += 1

    return segments


def parse_paths(content: str, dx: float = 0, dy: float = 0) -> List[Segment]:
    """Extract segments from <path> elements with stroke-width >= 1.0."""
    segments = []
    path_counter = 0

    for m in re.finditer(r'<path\b([^>]*)/?>', content):
        attrs = m.group(1)
        sw = _attr_f(attrs, 'stroke-width', 0.0)
        if sw < 1.0:
            continue

        d_match = re.search(r'd="([^"]+)"', attrs)
        if not d_match:
            continue
        d = d_match.group(1)
        has_arrow = 'marker-end' in attrs

        # Determine path group ID from dash pattern
        if 'dasharray="3,3"' in content[m.start():m.end() + 50]:
            group = "reflection"
        elif 'dasharray="6,3"' in content[m.start():m.end() + 50]:
            group = "thermal_xlink"
        else:
            group = f"path_{path_counter}"

        # Parse M/L/C/Q/T/S/A commands into point sequences
        # Curves (C, Q, T, S) and arcs (A) represent bridges — they break
        # the straight-line chain. We extract segments between straight points
        # and treat curves as gaps (the bridge convention).
        points = []  # list of (x, y, is_bridge_end)
        tokens = re.findall(r'([MLCAQTSZ])\s*([^MLCAQTSZ]*)', d, re.IGNORECASE)
        for cmd_type, coords_str in tokens:
            # SVG numbers can include optional sign, decimal point, and
            # exponent (e.g., 1e-3, +2.5). Avoid matching multi-dot
            # sequences like "1.2.3" as a single token.
            nums = re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', coords_str)
            cmd = cmd_type.upper()
            if cmd in ('M', 'L') and len(nums) >= 2:
                points.append((float(nums[0]), float(nums[1]), False))
            elif cmd == 'C' and len(nums) >= 6:
                # Cubic bezier: C cx1 cy1 cx2 cy2 ex ey
                # Mark the START of the curve as a break, add endpoint
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)  # mark as bridge start
                points.append((float(nums[4]), float(nums[5]), False))
            elif cmd == 'Q' and len(nums) >= 4:
                # Quadratic bezier: Q cx cy ex ey
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)
                points.append((float(nums[2]), float(nums[3]), False))
            elif cmd == 'T' and len(nums) >= 2:
                # Smooth quadratic: T ex ey (control point reflected)
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)
                points.append((float(nums[0]), float(nums[1]), False))
            elif cmd == 'S' and len(nums) >= 4:
                # Smooth cubic: S cx2 cy2 ex ey
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)
                points.append((float(nums[2]), float(nums[3]), False))
            elif cmd == 'A' and len(nums) >= 7:
                # Arc: A rx ry rotation large-arc sweep ex ey
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)
                points.append((float(nums[5]), float(nums[6]), False))
            # Z (close path) — ignore for segment extraction

        # Build segments, skipping bridge gaps
        for i in range(len(points) - 1):
            x1, y1, is_bridge = points[i]
            x2, y2, _ = points[i + 1]
            if is_bridge:
                continue  # Skip the curve/bridge — not a straight segment
            is_last = (i == len(points) - 2)
            seg = Segment(x1 + dx, y1 + dy, x2 + dx, y2 + dy, group, has_arrow and is_last)
            segments.append(seg)

        path_counter += 1

    return segments


def check_signal_crossings(segments: List[Segment]) -> List[str]:
    """G1: Check for signal-path-to-signal-path crossings."""
    issues = []
    h_segs = [s for s in segments if s.is_horizontal]
    v_segs = [s for s in segments if s.is_vertical]

    for h in h_segs:
        for v in v_segs:
            # Must be from different paths
            if h.path_id == v.path_id:
                continue

            hx_min, hx_max = h.min_x, h.max_x
            vy_min, vy_max = v.min_y, v.max_y
            vx = (v.x1 + v.x2) / 2  # vertical line x-coord
            hy = (h.y1 + h.y2) / 2  # horizontal line y-coord

            # Check if they cross (not just touch at endpoints)
            if hx_min < vx < hx_max and vy_min < hy < vy_max:
                issues.append(
                    f"CROSSING at ({vx:.0f}, {hy:.0f}): "
                    f"path '{h.path_id}' (H at y={hy:.0f}, x={hx_min:.0f}-{hx_max:.0f}) "
                    f"crosses path '{v.path_id}' (V at x={vx:.0f}, y={vy_min:.0f}-{vy_max:.0f})"
                )

    return issues


def check_arrow_endpoints(segments: List[Segment], rects: List[Rect]) -> List[str]:
    """G2: Check that arrows terminate at element edges.

    For rectangular targets, edge distance uses the perpendicular
    projection to each side (see Rect.distance_to_edge). For circular
    targets, edge distance is ``|dist_to_center - r|`` so arrows
    correctly register as "touching" when they land anywhere on the
    circumference, not just at the four cardinal points.

    A gap above 1.0u triggers a FAIL. A small tolerance accommodates
    hand-authored SVGs where the arrow endpoint rounds to an integer
    and the target edge falls on a half-pixel.
    """
    issues = []

    arrow_segs = [s for s in segments if s.has_arrow]

    for seg in arrow_segs:
        tip_x, tip_y = seg.x2, seg.y2

        best_dist = float('inf')
        best_rect = None
        for r in rects:
            d = r.distance_to_edge(tip_x, tip_y)
            if d < best_dist:
                best_dist = d
                best_rect = r

        if best_rect and best_dist > 1.0:
            shape = best_rect.kind
            issues.append(
                f"ARROW GAP ({best_dist:.0f}px): arrow at ({tip_x:.0f}, {tip_y:.0f}) "
                f"is {best_dist:.0f}px from nearest {shape} edge "
                f"(box at x={best_rect.x:.0f}, y={best_rect.y:.0f}, "
                f"w={best_rect.w:.0f}, h={best_rect.h:.0f})"
            )

    return issues


def check_path_through_box(segments: List[Segment], rects: List[Rect]) -> List[str]:
    """G3: Check if any signal path passes through an element box."""
    issues = []

    for seg in segments:
        for r in rects:
            if seg.is_vertical:
                vx = (seg.x1 + seg.x2) / 2
                # Does this vertical line pass through the rect horizontally?
                if r.x < vx < r.right:
                    # Does the segment span the rect vertically?
                    seg_top = seg.min_y
                    seg_bot = seg.max_y
                    # Passes through if segment enters and exits the box
                    enters_top = seg_top < r.y < seg_bot
                    enters_bottom = seg_top < r.bottom < seg_bot
                    if enters_top and enters_bottom:
                        issues.append(
                            f"PATH THROUGH BOX: vertical path '{seg.path_id}' at x={vx:.0f} "
                            f"(y={seg_top:.0f}-{seg_bot:.0f}) passes through box "
                            f"(x={r.x:.0f}-{r.right:.0f}, y={r.y:.0f}-{r.bottom:.0f})"
                        )
                    elif enters_top and not enters_bottom:
                        # Terminates inside or at the box — check if it's an arrow endpoint
                        if not seg.has_arrow and seg_bot > r.y + 5:
                            pass  # Entering the box from top might be intentional
                    elif enters_bottom and not enters_top:
                        if not seg.has_arrow and seg_top < r.bottom - 5:
                            pass

            elif seg.is_horizontal:
                hy = (seg.y1 + seg.y2) / 2
                if r.y < hy < r.bottom:
                    seg_left = seg.min_x
                    seg_right = seg.max_x
                    enters_left = seg_left < r.x < seg_right
                    enters_right = seg_left < r.right < seg_right
                    if enters_left and enters_right:
                        issues.append(
                            f"PATH THROUGH BOX: horizontal path '{seg.path_id}' at y={hy:.0f} "
                            f"(x={seg_left:.0f}-{seg_right:.0f}) passes through box "
                            f"(x={r.x:.0f}-{r.right:.0f}, y={r.y:.0f}-{r.bottom:.0f})"
                        )

    return issues


def parse_texts(content: str, dx: float = 0, dy: float = 0) -> List[TextBox]:
    """Extract text elements with approximate bounding boxes."""
    texts = []
    for m in re.finditer(r'<text\b([^>]*)>([^<]+)</text>', content):
        attrs = m.group(1)
        text = m.group(2).strip()
        if not text:
            continue

        # Skip rotated text — different bbox calculation needed
        if 'transform=' in attrs:
            continue

        x = _attr_f(attrs, 'x') + dx
        y = _attr_f(attrs, 'y') + dy
        font_size = _attr_f(attrs, 'font-size', 14)
        anchor = _attr(attrs, 'text-anchor') or 'start'

        char_width = font_size * 0.6  # approximate
        text_width = len(text) * char_width

        if anchor == "middle":
            tx = x - text_width / 2
        elif anchor == "end":
            tx = x - text_width
        else:  # start
            tx = x

        texts.append(TextBox(tx, y - font_size, text_width, font_size, text))

    return texts


def check_segment_overlaps(segments: List[Segment]) -> List[str]:
    """G4: Two different signal paths share a colinear overlapping segment.

    Two horizontal segments at the same y (within 0.5 tol) whose x-ranges
    overlap by more than 1 unit are flagged. Same for vertical segments.
    Endpoint-only touches are not reported.
    """
    issues = []

    def overlap_len(a_lo, a_hi, b_lo, b_hi):
        return max(0.0, min(a_hi, b_hi) - max(a_lo, b_lo))

    h_segs = [s for s in segments if s.is_horizontal]
    for i, a in enumerate(h_segs):
        for b in h_segs[i + 1:]:
            if a.path_id == b.path_id:
                continue
            if abs(a.y1 - b.y1) > 0.5:
                continue
            ov = overlap_len(a.min_x, a.max_x, b.min_x, b.max_x)
            if ov > 1.0:
                issues.append(
                    f"SEGMENT OVERLAP (H, {ov:.0f}u) at y={a.y1:.0f}: "
                    f"'{a.path_id}' and '{b.path_id}'"
                )

    v_segs = [s for s in segments if s.is_vertical]
    for i, a in enumerate(v_segs):
        for b in v_segs[i + 1:]:
            if a.path_id == b.path_id:
                continue
            if abs(a.x1 - b.x1) > 0.5:
                continue
            ov = overlap_len(a.min_y, a.max_y, b.min_y, b.max_y)
            if ov > 1.0:
                issues.append(
                    f"SEGMENT OVERLAP (V, {ov:.0f}u) at x={a.x1:.0f}: "
                    f"'{a.path_id}' and '{b.path_id}'"
                )

    return issues


def check_text_overlaps(texts: List[TextBox]) -> List[str]:
    """G5: Check for text-text overlaps."""
    issues = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            # Check bounding box overlap
            if (a.x < b.x + b.width and a.x + a.width > b.x and
                    a.y < b.y + b.height and a.y + a.height > b.y):
                issues.append(
                    f"TEXT OVERLAP: '{a.content}' at ({a.x:.0f},{a.y:.0f}) "
                    f"overlaps '{b.content}' at ({b.x:.0f},{b.y:.0f})"
                )
    return issues


def validate_geometry(svg_file: str) -> bool:
    """Run all geometric checks on an SVG file."""
    content = Path(svg_file).read_text(encoding='utf-8')
    filename = Path(svg_file).name

    print(f"\n{'='*60}")
    print(f"GEOMETRIC AUDIT: {filename}")
    print(f"{'='*60}\n")

    dx, dy = detect_transform_offset(content)
    rects = parse_rects(content, dx, dy)
    line_segs = parse_lines(content, dx, dy)
    path_segs = parse_paths(content, dx, dy)
    all_segs = line_segs + path_segs
    texts = parse_texts(content, dx, dy)

    print(f"[INFO] Found {len(rects)} element boxes")
    print(f"[INFO] Found {len(all_segs)} signal path segments")
    print(f"[INFO] Found {len(texts)} text elements\n")

    all_issues = []
    all_pass = True

    # G1: Signal crossings
    crossing_issues = check_signal_crossings(all_segs)
    if crossing_issues:
        print(f"[FAIL] G1 Signal Crossings: {len(crossing_issues)} crossing(s) found")
        for issue in crossing_issues:
            print(f"       {issue}")
        all_pass = False
    else:
        print("[PASS] G1 Signal Crossings: No path-to-path crossings")
    all_issues.extend(crossing_issues)

    # G2: Arrow endpoints
    arrow_issues = check_arrow_endpoints(all_segs, rects)
    if arrow_issues:
        print(f"[FAIL] G2 Arrow Endpoints: {len(arrow_issues)} gap(s) found")
        for issue in arrow_issues:
            print(f"       {issue}")
        all_pass = False
    else:
        print("[PASS] G2 Arrow Endpoints: All arrows touch box edges")
    all_issues.extend(arrow_issues)

    # G3: Path through box
    through_issues = check_path_through_box(all_segs, rects)
    if through_issues:
        print(f"[FAIL] G3 Path Through Box: {len(through_issues)} collision(s) found")
        for issue in through_issues:
            print(f"       {issue}")
        all_pass = False
    else:
        print("[PASS] G3 Path Through Box: No paths cross through boxes")
    all_issues.extend(through_issues)

    # G4: Signal segment overlaps
    overlap_issues = check_segment_overlaps(all_segs)
    if overlap_issues:
        print(f"[FAIL] G4 Segment Overlaps: {len(overlap_issues)} overlap(s) found")
        for issue in overlap_issues:
            print(f"       {issue}")
        all_pass = False
    else:
        print("[PASS] G4 Segment Overlaps: No colinear path overlaps")
    all_issues.extend(overlap_issues)

    # G5: Text overlaps
    text_issues = check_text_overlaps(texts)
    if text_issues:
        print(f"[FAIL] G5 Text Overlaps: {len(text_issues)} overlap(s) found")
        for issue in text_issues:
            print(f"       {issue}")
        all_pass = False
    else:
        print("[PASS] G5 Text Overlaps: No text elements overlap")
    all_issues.extend(text_issues)

    # Summary
    checks = 5
    passed = checks - (1 if crossing_issues else 0) - (1 if arrow_issues else 0) \
             - (1 if through_issues else 0) - (1 if overlap_issues else 0) \
             - (1 if text_issues else 0)

    print(f"\n{'-'*60}")
    print(f"GEOMETRIC SUMMARY: {passed}/{checks} checks passed")
    if all_pass:
        print("STATUS: GEOMETRY CLEAN")
    else:
        print(f"STATUS: {len(all_issues)} issue(s) require fixing")
    print(f"{'='*60}\n")

    return all_pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python geometric_validator.py <svg_file>")
        print("\nChecks:")
        print("  G1: Signal-path-to-signal-path crossings")
        print("  G2: Arrow endpoints touching box edges")
        print("  G3: Signal paths passing through element boxes")
        print("  G4: Colinear signal-path overlaps")
        print("  G5: Text-text overlaps")
        sys.exit(1)

    success = validate_geometry(sys.argv[1])
    sys.exit(0 if success else 1)
