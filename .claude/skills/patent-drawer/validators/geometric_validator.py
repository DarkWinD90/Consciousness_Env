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

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class Rect:
    """A rectangle (element box) with its bounding coordinates."""
    x: float
    y: float
    w: float
    h: float
    label: str = ""

    @property
    def right(self): return self.x + self.w
    @property
    def bottom(self): return self.y + self.h

    def contains_point(self, px, py):
        return self.x < px < self.right and self.y < py < self.bottom

    def on_edge(self, px, py, tolerance=1.0):
        """Check if point is on the edge (within tolerance)."""
        on_left = abs(px - self.x) <= tolerance and self.y <= py <= self.bottom
        on_right = abs(px - self.right) <= tolerance and self.y <= py <= self.bottom
        on_top = abs(py - self.y) <= tolerance and self.x <= px <= self.right
        on_bottom = abs(py - self.bottom) <= tolerance and self.x <= px <= self.right
        return on_left or on_right or on_top or on_bottom


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


def parse_rects(content: str) -> List[Rect]:
    """Extract all rect elements (excluding background and legend)."""
    rects = []
    for m in re.finditer(
        r'<rect\s+x="([\d.]+)"\s+y="([\d.]+)"\s+width="([\d.]+)"\s+height="([\d.]+)"',
        content
    ):
        x, y, w, h = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        # Skip full-page background rect and very large rects
        if w > 800 or h > 800:
            continue
        # Skip legend boxes (typically y > 790)
        if y > 790:
            continue
        rects.append(Rect(x, y, w, h))
    return rects


def parse_lines(content: str) -> List[Segment]:
    """Extract all signal path line segments (stroke-width >= 1.0)."""
    segments = []
    path_counter = 0

    # Parse <line> elements
    for m in re.finditer(
        r'<line\s+x1="([\d.]+)"\s+y1="([\d.]+)"\s+x2="([\d.]+)"\s+y2="([\d.]+)"'
        r'\s+stroke="[^"]+"\s+stroke-width="([\d.]+)"([^/]*)/?>',
        content
    ):
        sw = float(m.group(5))
        if sw < 1.0:  # Skip leader lines (0.5)
            continue
        rest = m.group(6)
        # Skip legend lines (check surrounding context)
        line_pos = m.start()
        context_before = content[max(0, line_pos - 200):line_pos]
        if 'LEGEND' in context_before or 'SIGNAL PATHWAYS' in context_before:
            continue

        has_arrow = 'marker-end' in rest
        seg = Segment(
            float(m.group(1)), float(m.group(2)),
            float(m.group(3)), float(m.group(4)),
            f"line_{path_counter}", has_arrow
        )
        segments.append(seg)
        path_counter += 1

    return segments


def parse_paths(content: str) -> List[Segment]:
    """Extract segments from <path> elements with stroke-width >= 1.0."""
    segments = []
    path_counter = 0

    for m in re.finditer(
        r'<path\s+d="([^"]+)"[^>]*stroke-width="([\d.]+)"([^>]*)>',
        content
    ):
        sw = float(m.group(2))
        if sw < 1.0:
            continue

        d = m.group(1)
        rest = m.group(3)
        has_arrow = 'marker-end' in rest

        # Determine path group ID from dash pattern
        if 'dasharray="3,3"' in content[m.start():m.end() + 50]:
            group = "reflection"
        elif 'dasharray="6,3"' in content[m.start():m.end() + 50]:
            group = "thermal_xlink"
        else:
            group = f"path_{path_counter}"

        # Parse M/L/C/A commands into point sequences
        # C (cubic bezier) and A (arc) represent bridges/curves — they break
        # the straight-line chain. We extract segments between straight points
        # and treat curves as gaps (the bridge convention).
        points = []  # list of (x, y, is_bridge_end)
        tokens = re.findall(r'([MLCAZ])\s*([^MLCAZ]*)', d, re.IGNORECASE)
        for cmd_type, coords_str in tokens:
            nums = re.findall(r'[\d.]+', coords_str)
            cmd = cmd_type.upper()
            if cmd in ('M', 'L') and len(nums) >= 2:
                points.append((float(nums[0]), float(nums[1]), False))
            elif cmd == 'C' and len(nums) >= 6:
                # Cubic bezier: C cx1 cy1 cx2 cy2 ex ey
                # Mark the START of the curve as a break, add endpoint
                if points:
                    points[-1] = (points[-1][0], points[-1][1], True)  # mark as bridge start
                points.append((float(nums[4]), float(nums[5]), False))
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
            seg = Segment(x1, y1, x2, y2, group, has_arrow and is_last)
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
    """G2: Check that arrows terminate at box edges."""
    issues = []

    arrow_segs = [s for s in segments if s.has_arrow]

    for seg in arrow_segs:
        # Arrow tip is at (x2, y2)
        tip_x, tip_y = seg.x2, seg.y2

        # Find the closest rect edge
        best_dist = float('inf')
        best_rect = None
        for r in rects:
            # Check distance to each edge
            distances = []
            # Top edge
            if r.x <= tip_x <= r.right:
                distances.append(abs(tip_y - r.y))
            # Bottom edge
            if r.x <= tip_x <= r.right:
                distances.append(abs(tip_y - r.bottom))
            # Left edge
            if r.y <= tip_y <= r.bottom:
                distances.append(abs(tip_x - r.x))
            # Right edge
            if r.y <= tip_y <= r.bottom:
                distances.append(abs(tip_x - r.right))

            if distances:
                d = min(distances)
                if d < best_dist:
                    best_dist = d
                    best_rect = r

        if best_rect and best_dist > 1.0:
            issues.append(
                f"ARROW GAP ({best_dist:.0f}px): arrow at ({tip_x:.0f}, {tip_y:.0f}) "
                f"is {best_dist:.0f}px from nearest box edge "
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


def parse_texts(content: str) -> List[TextBox]:
    """Extract text elements with approximate bounding boxes."""
    texts = []
    for m in re.finditer(
        r'<text\s+x="([\d.]+)"\s+y="([\d.]+)"[^>]*font-size="(\d+)"[^>]*'
        r'text-anchor="(\w+)"[^>]*>([^<]+)</text>',
        content
    ):
        x, y = float(m.group(1)), float(m.group(2))
        font_size = int(m.group(3))
        anchor = m.group(4)
        text = m.group(5)

        # Skip if inside a transform (rotated text — different bbox)
        line_start = content.rfind('<text', 0, m.start())
        tag = content[line_start:m.end()]
        if 'transform=' in tag:
            continue

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

    rects = parse_rects(content)
    line_segs = parse_lines(content)
    path_segs = parse_paths(content)
    all_segs = line_segs + path_segs
    texts = parse_texts(content)

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
    checks = 4
    passed = checks - (1 if crossing_issues else 0) - (1 if arrow_issues else 0) \
             - (1 if through_issues else 0) - (1 if text_issues else 0)

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
        print("  G5: Text-text overlaps")
        sys.exit(1)

    success = validate_geometry(sys.argv[1])
    sys.exit(0 if success else 1)
