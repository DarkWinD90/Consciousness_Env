#!/usr/bin/env python3
"""Run USPTO drawing compliance audit with strict visual + structural checks.

Outputs dated artifacts under patent_drawings/compliance_runs/YYYY-MM-DD/.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import cairosvg
from PIL import Image

SVG_NS = "{http://www.w3.org/2000/svg}"
MIN_TEXT_SIZE = 12.6
MARGIN_BOUNDS = {
    "left": 100.0,
    "top": 100.0,
    "right": 787.5,
    "bottom": 1062.5,
}
ALLOWED_COLORS = {"black", "#000", "#000000", "white", "#fff", "#ffffff", "none", "transparent"}


@dataclass
class FigureResult:
    patent: str
    figure: int
    sheet: str
    file: str
    viewbox: bool
    margins: bool
    min_text: bool
    min_font_seen: float
    bw_only: bool
    fig_label: bool
    sheet_number: bool
    diagram_hygiene: bool
    status: str
    issues: Dict[str, List[str]]


@dataclass
class Shape:
    tag: str
    bbox: Tuple[float, float, float, float]
    points: List[Tuple[float, float]]
    stroke_width: float
    has_marker: bool
    dashed: bool


def parse_style(style: str | None) -> Dict[str, str]:
    if not style:
        return {}
    out: Dict[str, str] = {}
    for part in style.split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def clean_color(val: str | None) -> str | None:
    if val is None:
        return None
    return val.strip().lower()


def color_ok(val: str | None) -> bool:
    if val is None:
        return True
    c = clean_color(val)
    if c in ALLOWED_COLORS:
        return True
    if c.startswith("url("):
        return True
    if c.startswith("rgb("):
        nums = re.findall(r"\d+", c)
        if len(nums) >= 3:
            r, g, b = nums[:3]
            return r == g == b and r in ("0", "255")
    return False


# 2D affine helpers: (a,b,c,d,e,f) => x' = ax + cy + e, y' = bx + dy + f
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mul_mat(m1: Tuple[float, float, float, float, float, float], m2: Tuple[float, float, float, float, float, float]):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def apply_mat(m: Tuple[float, float, float, float, float, float], p: Tuple[float, float]) -> Tuple[float, float]:
    a, b, c, d, e, f = m
    x, y = p
    return a * x + c * y + e, b * x + d * y + f


def parse_transform(transform: str | None) -> Tuple[float, float, float, float, float, float]:
    if not transform:
        return IDENTITY
    mat = IDENTITY
    for name, raw_args in re.findall(r"([a-zA-Z]+)\(([^)]*)\)", transform):
        args = [float(x) for x in re.findall(r"-?\d*\.?\d+", raw_args)]
        if name == "translate":
            tx = args[0] if args else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            cur = (1.0, 0.0, 0.0, 1.0, tx, ty)
        elif name == "scale":
            sx = args[0] if args else 1.0
            sy = args[1] if len(args) > 1 else sx
            cur = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif name == "rotate" and args:
            ang = math.radians(args[0])
            ca, sa = math.cos(ang), math.sin(ang)
            rot = (ca, sa, -sa, ca, 0.0, 0.0)
            if len(args) >= 3:
                cx, cy = args[1], args[2]
                cur = mul_mat(mul_mat((1.0, 0.0, 0.0, 1.0, cx, cy), rot), (1.0, 0.0, 0.0, 1.0, -cx, -cy))
            else:
                cur = rot
        elif name == "matrix" and len(args) >= 6:
            cur = tuple(args[:6])  # type: ignore[assignment]
        else:
            continue
        mat = mul_mat(mat, cur)
    return mat


def iter_svg_elements(root: ET.Element) -> Iterable[Tuple[ET.Element, str, Tuple[float, float, float, float], bool]]:
    def walk(node: ET.Element, parent_mat, in_defs: bool):
        tag = node.tag.replace(SVG_NS, "")
        local = parse_transform(node.get("transform"))
        mat = mul_mat(parent_mat, local)
        now_in_defs = in_defs or tag in {"defs", "marker", "clipPath", "mask", "pattern"}
        yield node, tag, mat, now_in_defs
        for child in node:
            yield from walk(child, mat, now_in_defs)

    yield from walk(root, IDENTITY, False)


def text_bbox_estimate(x: float, y: float, font_size: float, anchor: str, text: str) -> Tuple[float, float, float, float]:
    width = max(1, len(text)) * font_size * 0.6
    if anchor == "middle":
        x0 = x - width / 2
    elif anchor == "end":
        x0 = x - width
    else:
        x0 = x
    y0 = y - font_size
    return x0, y0, x0 + width, y


def render_rgba(svg_path: Path) -> Image.Image:
    png = cairosvg.svg2png(url=str(svg_path), output_width=850, output_height=1100)
    return Image.open(BytesIO(png)).convert("RGBA")


def nonwhite_bbox(img: Image.Image) -> Tuple[int, int, int, int] | None:
    px = img.load()
    min_x = min_y = None
    max_x = max_y = None
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if (r, g, b) != (255, 255, 255):
                min_x = x if min_x is None else min(min_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_x = x if max_x is None else max(max_x, x)
                max_y = y if max_y is None else max(max_y, y)
    if min_x is None:
        return None
    return min_x, min_y, max_x, max_y


def mask_page_indicators(img: Image.Image, root: ET.Element) -> None:
    px = img.load()
    for el, tag, mat, in_defs in iter_svg_elements(root):
        if in_defs or tag != "text":
            continue
        text = "".join(el.itertext()).strip()
        if not (re.fullmatch(r"FIG\.\s*\d+", text) or re.fullmatch(r"\d+/\d+", text)):
            continue
        try:
            x = float(el.get("x", "0"))
            y = float(el.get("y", "0"))
            fs = float(el.get("font-size", "14"))
            anchor = el.get("text-anchor", "start")
            x0, y0, x1, y1 = text_bbox_estimate(x, y, fs, anchor, text)
            corners = [apply_mat(mat, (x0, y0)), apply_mat(mat, (x1, y0)), apply_mat(mat, (x1, y1)), apply_mat(mat, (x0, y1))]
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            ix0 = max(0, int(min(xs)) - 4)
            iy0 = max(0, int(min(ys)) - 4)
            ix1 = min(img.width - 1, int(max(xs)) + 4)
            iy1 = min(img.height - 1, int(max(ys)) + 4)
            for yy in range(iy0, iy1 + 1):
                for xx in range(ix0, ix1 + 1):
                    px[xx, yy] = (255, 255, 255, 255)
        except ValueError:
            continue


def get_stroke_width(el: ET.Element, style: Dict[str, str]) -> float:
    try:
        return float(style.get("stroke-width", el.get("stroke-width", "1")))
    except ValueError:
        return 1.0


def extract_path_points(d: str) -> List[Tuple[float, float]]:
    tokens = re.findall(r"[MmLlHhVv]|-?\d*\.?\d+", d)
    pts: List[Tuple[float, float]] = []
    i = 0
    cmd = ""
    x = y = 0.0
    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r"[MmLlHhVv]", tok):
            cmd = tok
            i += 1
            continue
        if cmd in ("M", "L") and i + 1 < len(tokens):
            x, y = float(tokens[i]), float(tokens[i + 1])
            pts.append((x, y))
            i += 2
        elif cmd in ("m", "l") and i + 1 < len(tokens):
            x += float(tokens[i])
            y += float(tokens[i + 1])
            pts.append((x, y))
            i += 2
        elif cmd == "H":
            x = float(tokens[i])
            pts.append((x, y))
            i += 1
        elif cmd == "h":
            x += float(tokens[i])
            pts.append((x, y))
            i += 1
        elif cmd == "V":
            y = float(tokens[i])
            pts.append((x, y))
            i += 1
        elif cmd == "v":
            y += float(tokens[i])
            pts.append((x, y))
            i += 1
        else:
            i += 1
    return pts


def bbox_from_points(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float] | None:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def extract_shape(el: ET.Element, tag: str, mat: Tuple[float, float, float, float, float, float], in_defs: bool) -> Shape | None:
    if in_defs or tag in {"text", "svg", "g", "defs", "marker"}:
        return None
    style = parse_style(el.get("style"))
    stroke_width = get_stroke_width(el, style)
    dashed = bool(style.get("stroke-dasharray") or el.get("stroke-dasharray"))
    has_marker = any(el.get(a) for a in ("marker-start", "marker-mid", "marker-end"))

    points: List[Tuple[float, float]] = []
    try:
        if tag == "line":
            points = [
                (float(el.get("x1", "0")), float(el.get("y1", "0"))),
                (float(el.get("x2", "0")), float(el.get("y2", "0"))),
            ]
        elif tag == "rect":
            x = float(el.get("x", "0"))
            y = float(el.get("y", "0"))
            w = float(el.get("width", "0"))
            h = float(el.get("height", "0"))
            points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        elif tag in {"polyline", "polygon"}:
            raw = el.get("points", "")
            coords = [c for c in re.split(r"[\s,]+", raw.strip()) if c]
            if len(coords) % 2:
                return None
            points = [(float(coords[i]), float(coords[i + 1])) for i in range(0, len(coords), 2)]
        elif tag == "path":
            points = extract_path_points(el.get("d", ""))
        elif tag == "ellipse":
            cx = float(el.get("cx", "0"))
            cy = float(el.get("cy", "0"))
            rx = float(el.get("rx", "0"))
            ry = float(el.get("ry", "0"))
            points = [(cx - rx, cy - ry), (cx + rx, cy + ry)]
        elif tag == "circle":
            cx = float(el.get("cx", "0"))
            cy = float(el.get("cy", "0"))
            r = float(el.get("r", "0"))
            points = [(cx - r, cy - r), (cx + r, cy + r)]
        else:
            return None
    except ValueError:
        return None

    points = [apply_mat(mat, p) for p in points]
    bbox = bbox_from_points(points)
    if not bbox:
        return None

    # ignore background/page frame rectangles
    if tag == "rect" and bbox[2] - bbox[0] > 820 and bbox[3] - bbox[1] > 1070:
        return None

    return Shape(tag=tag, bbox=bbox, points=points, stroke_width=stroke_width, has_marker=has_marker, dashed=dashed)


def bbox_overlap(a: Tuple[float, float, float, float], b: Tuple[float, float, float, float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def point_to_bbox_distance(p: Tuple[float, float], b: Tuple[float, float, float, float]) -> float:
    x, y = p
    cx = min(max(x, b[0]), b[2])
    cy = min(max(y, b[1]), b[3])
    return ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5


def segment_intersection(a1, a2, b1, b2) -> bool:
    def ccw(p1, p2, p3):
        return (p3[1] - p1[1]) * (p2[0] - p1[0]) > (p2[1] - p1[1]) * (p3[0] - p1[0])

    return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)


def evaluate_diagram_hygiene(
    shapes: List[Shape], numeric_text_nodes: List[Tuple[str, Tuple[float, float, float, float]]]
) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    components = [s for s in shapes if s.tag in {"rect", "ellipse", "circle", "polygon"} and s.stroke_width >= 1.0]
    signal_paths = [s for s in shapes if s.tag in {"line", "polyline", "path"} and (s.has_marker or s.dashed)]
    leader_lines = [s for s in shapes if s.tag in {"line", "path"} and s.stroke_width <= 0.8]

    # Element collisions (ignore tiny overlaps due to stroke joins)
    for i in range(len(components)):
        for j in range(i + 1, len(components)):
            if bbox_overlap(components[i].bbox, components[j].bbox) > 120:
                issues.append("component overlap/collision detected")
                break

    # Signal path start/end anchoring
    for idx, s in enumerate(signal_paths, start=1):
        if len(s.points) < 2:
            continue
        start, end = s.points[0], s.points[-1]
        start_ok = any(point_to_bbox_distance(start, c.bbox) <= 14 for c in components)
        end_ok = any(point_to_bbox_distance(end, c.bbox) <= 14 for c in components)
        if not start_ok or not end_ok:
            issues.append(f"signal path #{idx} has floating start/end")

    # Signal crossing other signal paths.
    crossing_found = False
    for i in range(len(signal_paths)):
        a = signal_paths[i]
        if len(a.points) < 2:
            continue
        for j in range(i + 1, len(signal_paths)):
            b = signal_paths[j]
            if len(b.points) < 2:
                continue
            for ai in range(len(a.points) - 1):
                for bi in range(len(b.points) - 1):
                    if segment_intersection(a.points[ai], a.points[ai + 1], b.points[bi], b.points[bi + 1]):
                        crossing_found = True
                        break
                if crossing_found:
                    break
            if crossing_found:
                break
        if crossing_found:
            break
    if crossing_found:
        issues.append("signal path crossing detected")

    # Signal paths through elements (excluding endpoint-touching)
    for idx, s in enumerate(signal_paths, start=1):
        if len(s.points) < 2:
            continue
        for c in components:
            intersects_mid = False
            for i in range(len(s.points) - 1):
                p1, p2 = s.points[i], s.points[i + 1]
                seg_bbox = (min(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[0], p2[0]), max(p1[1], p2[1]))
                if bbox_overlap(seg_bbox, c.bbox) <= 0:
                    continue
                if point_to_bbox_distance(p1, c.bbox) <= 5 or point_to_bbox_distance(p2, c.bbox) <= 5:
                    continue
                intersects_mid = True
                break
            if intersects_mid:
                issues.append(f"signal path #{idx} intersects component interior")
                break

    # Reference numeral placement + leader lines
    leader_points = [p for l in leader_lines for p in (l.points[:1] + l.points[-1:])]
    for num, bb in numeric_text_nodes:
        center = ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
        if any(bbox_overlap(bb, c.bbox) > 0 for c in components):
            issues.append(f"reference numeral {num} overlaps element")
        if leader_points and not any((((center[0] - p[0]) ** 2 + (center[1] - p[1]) ** 2) ** 0.5) <= 28 for p in leader_points):
            issues.append(f"reference numeral {num} missing nearby leader line")

    issues = sorted(set(issues))[:15]
    return (len(issues) == 0), issues


def check_figure(svg_path: Path, patent: str, fig_num: int, total: int) -> FigureResult:
    root = ET.parse(svg_path).getroot()

    viewbox_ok = root.get("viewBox", "").strip() == "0 0 850 1100"
    min_font_seen = 9999.0
    min_text_ok = True
    text_issues: List[str] = []
    color_ok_all = True
    color_issues: List[str] = []
    texts: List[str] = []
    shapes: List[Shape] = []
    numeric_text_nodes: List[Tuple[str, Tuple[float, float, float, float]]] = []

    for el, tag, mat, in_defs in iter_svg_elements(root):
        style = parse_style(el.get("style"))
        if not in_defs:
            for attr in ("fill", "stroke", "color", "stop-color"):
                val = style.get(attr, el.get(attr))
                if not color_ok(val):
                    color_ok_all = False
                    color_issues.append(f"{tag}:{attr}={val}")

        if not in_defs and tag == "text":
            txt = "".join(el.itertext()).strip()
            texts.append(txt)
            try:
                fs = float(el.get("font-size", "14"))
                min_font_seen = min(min_font_seen, fs)
                if fs < MIN_TEXT_SIZE:
                    min_text_ok = False
                    text_issues.append(f"{txt} ({fs})")
            except ValueError:
                min_text_ok = False
                text_issues.append(f"{txt} (invalid font-size)")

            if re.fullmatch(r"\d+", txt):
                try:
                    x = float(el.get("x", "0"))
                    y = float(el.get("y", "0"))
                    fs = float(el.get("font-size", "14"))
                    anchor = el.get("text-anchor", "start")
                    bb = text_bbox_estimate(x, y, fs, anchor, txt)
                    corners = [apply_mat(mat, (bb[0], bb[1])), apply_mat(mat, (bb[2], bb[1])), apply_mat(mat, (bb[2], bb[3])), apply_mat(mat, (bb[0], bb[3]))]
                    numeric_text_nodes.append((txt, bbox_from_points(corners) or bb))
                except ValueError:
                    pass

        shape = extract_shape(el, tag, mat, in_defs)
        if shape:
            shapes.append(shape)

    fig_label_ok = f"FIG. {fig_num}" in texts
    sheet_ok = f"{fig_num}/{total}" in texts

    img = render_rgba(svg_path)
    mask_page_indicators(img, root)
    bbox = nonwhite_bbox(img)
    margin_ok = True
    margin_issues: List[str] = []
    if bbox:
        min_x, min_y, max_x, max_y = bbox
        if min_x < MARGIN_BOUNDS["left"]:
            margin_ok = False
            margin_issues.append(f"left content at x={min_x}")
        if min_y < MARGIN_BOUNDS["top"]:
            margin_ok = False
            margin_issues.append(f"top content at y={min_y}")
        if max_x > MARGIN_BOUNDS["right"]:
            margin_ok = False
            margin_issues.append(f"right content at x={max_x}")
        if max_y > MARGIN_BOUNDS["bottom"]:
            margin_ok = False
            margin_issues.append(f"bottom content at y={max_y}")

    hygiene_ok, hygiene_issues = evaluate_diagram_hygiene(shapes, numeric_text_nodes)

    status = "PASS" if all([viewbox_ok, margin_ok, min_text_ok, color_ok_all, fig_label_ok, sheet_ok, hygiene_ok]) else "FAIL"

    return FigureResult(
        patent=patent,
        figure=fig_num,
        sheet=f"{fig_num}/{total}",
        file=str(svg_path),
        viewbox=viewbox_ok,
        margins=margin_ok,
        min_text=min_text_ok,
        min_font_seen=0.0 if min_font_seen == 9999.0 else round(min_font_seen, 2),
        bw_only=color_ok_all,
        fig_label=fig_label_ok,
        sheet_number=sheet_ok,
        diagram_hygiene=hygiene_ok,
        status=status,
        issues={
            "margins": sorted(set(margin_issues))[:10],
            "text": sorted(set(text_issues))[:10],
            "color": sorted(set(color_issues))[:10],
            "diagram": sorted(set(hygiene_issues))[:12],
        },
    )


def run(output_date: str | None = None) -> int:
    run_date = output_date or date.today().isoformat()
    run_dir = Path("patent_drawings") / "compliance_runs" / run_date
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    patent_counts = [("patent_a", 8), ("patent_b", 6), ("patent_c", 7)]

    results: List[FigureResult] = []
    any_fail = False
    for patent, total in patent_counts:
        for fig in range(1, total + 1):
            svg = Path("patent_drawings") / patent / f"fig{fig}.svg"
            result = check_figure(svg, patent, fig, total)
            results.append(result)
            if result.status == "FAIL":
                any_fail = True

    json_path = logs_dir / "uspto_compliance_results.json"
    json_path.write_text(json.dumps([asdict(r) for r in results], indent=2) + "\n")

    md_lines = [
        "# USPTO PATENT DRAWING COMPLIANCE REPORT",
        "",
        f"**Date**: {run_date}",
        "**Scope**: 21 SVG drawings across Patent A/B/C",
        "**Validator mode**: strict (visual margin raster check + source SVG semantic checks)",
        "**Checks**: page geometry, statutory margins, minimum text size, black/white-only palette, figure label, sheet numbering, diagram hygiene (signal crossings/collisions/leaders)",
        "",
        "| Patent | Figure | Sheet | ViewBox 850x1100 | Margins | Min Text >=12.6 | B/W only | Label `FIG. X` | Sheet `n/N` | Diagram hygiene | Status |",
        "|---|---:|---:|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        yn = lambda b: "PASS" if b else "FAIL"
        md_lines.append(
            f"| {r.patent} | FIG. {r.figure} | {r.sheet} | {yn(r.viewbox)} | {yn(r.margins)} | {yn(r.min_text)} (min={r.min_font_seen}) | {yn(r.bw_only)} | {yn(r.fig_label)} | {yn(r.sheet_number)} | {yn(r.diagram_hygiene)} | **{r.status}** |"
        )

    md_lines.extend(["", "## Issues (failing checks)"])
    for r in results:
        if r.status == "FAIL":
            md_lines.append(f"- `{r.file}`")
            for k, values in r.issues.items():
                if values:
                    md_lines.append(f"  - {k}: {', '.join(values)}")
    if not any_fail:
        md_lines.append("- None. All figures passed all required checks.")

    report_path = run_dir / "USPTO_Compliance_Report.md"
    report_path.write_text("\n".join(md_lines) + "\n")

    log_lines = [
        f"Wrote {report_path}",
        f"Wrote {json_path}",
        f"Summary: {'FAILURES DETECTED' if any_fail else 'ALL PASS'}",
    ]
    for r in results:
        log_lines.append(f"{r.patent}/fig{r.figure}: {r.status}")
    log_path = logs_dir / "uspto_compliance_validator.log"
    log_path.write_text("\n".join(log_lines) + "\n")

    print("\n".join(log_lines))
    return 2 if any_fail else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", dest="run_date", default=None, help="Override run date (YYYY-MM-DD).")
    args = parser.parse_args()
    raise SystemExit(run(args.run_date))


if __name__ == "__main__":
    main()
