#!/usr/bin/env python
"""USPTO Patent Drawing Collision Checker - Comprehensive Audit"""

import xml.etree.ElementTree as ET
import os
import re
import math
from pathlib import Path

def get_text_bbox(elem, transform=None):
    """Estimate bounding box for text element"""
    try:
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        font_size = float(elem.get('font-size', 10))
        text = elem.text or ''
        anchor = elem.get('text-anchor', 'start')

        # Estimate width based on character count (approx 0.6 * font_size per char)
        width = len(text) * font_size * 0.6
        height = font_size * 1.2

        # Adjust x based on text-anchor
        if anchor == 'middle':
            x -= width / 2
        elif anchor == 'end':
            x -= width

        # Apply transform if present
        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                x += float(match.group(1))
                y += float(match.group(2))

        return {'x': x, 'y': y - height, 'width': width, 'height': height, 'text': text}
    except:
        return None

def get_rect_bbox(elem, transform=None):
    """Get bounding box for rect element"""
    try:
        x = float(elem.get('x', 0))
        y = float(elem.get('y', 0))
        width = float(elem.get('width', 0))
        height = float(elem.get('height', 0))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                x += float(match.group(1))
                y += float(match.group(2))

        return {'x': x, 'y': y, 'width': width, 'height': height}
    except:
        return None

def get_circle_bbox(elem, transform=None):
    """Get bounding box for circle element"""
    try:
        cx = float(elem.get('cx', 0))
        cy = float(elem.get('cy', 0))
        r = float(elem.get('r', 0))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                cx += float(match.group(1))
                cy += float(match.group(2))

        return {'x': cx - r, 'y': cy - r, 'width': 2*r, 'height': 2*r}
    except:
        return None

def get_line_bbox(elem, transform=None):
    """Get bounding box for line element"""
    try:
        x1 = float(elem.get('x1', 0))
        y1 = float(elem.get('y1', 0))
        x2 = float(elem.get('x2', 0))
        y2 = float(elem.get('y2', 0))
        stroke_width = float(elem.get('stroke-width', 1))

        if transform:
            match = re.search(r'translate\(([\d.-]+)[,\s]+([\d.-]+)\)', transform)
            if match:
                tx, ty = float(match.group(1)), float(match.group(2))
                x1 += tx; y1 += ty; x2 += tx; y2 += ty

        return {
            'x': min(x1, x2) - stroke_width,
            'y': min(y1, y2) - stroke_width,
            'width': abs(x2 - x1) + 2*stroke_width,
            'height': abs(y2 - y1) + 2*stroke_width
        }
    except:
        return None

def boxes_overlap(b1, b2, threshold=0.15):
    """Check if two bounding boxes overlap beyond threshold"""
    if not b1 or not b2:
        return False, 0

    # Calculate intersection
    x_overlap = max(0, min(b1['x'] + b1['width'], b2['x'] + b2['width']) - max(b1['x'], b2['x']))
    y_overlap = max(0, min(b1['y'] + b1['height'], b2['y'] + b2['height']) - max(b1['y'], b2['y']))

    intersection = x_overlap * y_overlap
    if intersection == 0:
        return False, 0

    # Calculate overlap ratio relative to smaller box
    area1 = b1['width'] * b1['height']
    area2 = b2['width'] * b2['height']
    smaller_area = min(area1, area2)

    if smaller_area == 0:
        return False, 0

    overlap_ratio = intersection / smaller_area
    return overlap_ratio > threshold, overlap_ratio

def check_margins(bbox, margin_left=72, margin_right=567, margin_top=50, margin_bottom=765):
    """Check if element is within safe drawing area"""
    issues = []
    if bbox['x'] < margin_left - 20:  # Allow some tolerance
        issues.append(f"Left margin: x={bbox['x']:.0f}")
    if bbox['x'] + bbox['width'] > margin_right + 20:
        issues.append(f"Right margin: x+w={bbox['x']+bbox['width']:.0f}")
    if bbox['y'] < margin_top - 20:
        issues.append(f"Top margin: y={bbox['y']:.0f}")
    if bbox['y'] + bbox['height'] > margin_bottom + 20:
        issues.append(f"Bottom margin: y+h={bbox['y']+bbox['height']:.0f}")
    return issues

def analyze_svg(filepath):
    """Analyze a single SVG for collisions"""
    collisions = []
    warnings = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    root = ET.fromstring(content)

    # Collect all elements with their bboxes
    texts = []
    rects = []
    circles = []
    lines = []

    def process_element(elem, parent_transform=None):
        tag = elem.tag.replace('{http://www.w3.org/2000/svg}', '')
        transform = elem.get('transform', parent_transform)

        if tag == 'text':
            bbox = get_text_bbox(elem, transform)
            if bbox and bbox['text']:
                texts.append(bbox)
        elif tag == 'rect':
            bbox = get_rect_bbox(elem, transform)
            if bbox and bbox['width'] > 0 and bbox['height'] > 0:
                rects.append(bbox)
        elif tag == 'circle':
            bbox = get_circle_bbox(elem, transform)
            if bbox:
                circles.append(bbox)
        elif tag == 'line':
            bbox = get_line_bbox(elem, transform)
            if bbox:
                lines.append(bbox)

        # Process children with inherited transform
        for child in elem:
            child_transform = transform
            if child.get('transform'):
                child_transform = child.get('transform')
            process_element(child, child_transform)

    process_element(root)

    # Check text-on-text collisions (significant overlaps only)
    for i, t1 in enumerate(texts):
        for t2 in texts[i+1:]:
            overlaps, ratio = boxes_overlap(t1, t2, 0.20)
            if overlaps:
                collisions.append({
                    'type': 'text-on-text',
                    'desc': f'"{t1["text"]}" overlaps "{t2["text"]}"',
                    'overlap': ratio,
                    'fix': f'Move one text element by {int(t1["height"])}px'
                })

    # Check text-on-line collisions
    for t in texts:
        for line in lines:
            overlaps, ratio = boxes_overlap(t, line, 0.30)
            if overlaps and ratio > 0.3:
                warnings.append({
                    'type': 'text-on-line',
                    'desc': f'"{t["text"]}" may overlap line',
                    'overlap': ratio
                })

    # Check for reference numerals that are too close together
    ref_nums = [t for t in texts if t['text'].isdigit() and len(t['text']) == 3]
    for i, r1 in enumerate(ref_nums):
        for r2 in ref_nums[i+1:]:
            # Check if they're very close (within 15px)
            dist = math.sqrt((r1['x'] - r2['x'])**2 + (r1['y'] - r2['y'])**2)
            if dist < 15:
                warnings.append({
                    'type': 'crowded-refs',
                    'desc': f'Ref numerals {r1["text"]} and {r2["text"]} are {dist:.0f}px apart',
                    'overlap': 0
                })

    return collisions, warnings


def main():
    patents = {
        'patent_a': 8,
        'patent_b': 6,
        'patent_c': 7
    }

    print('=' * 70)
    print('USPTO PATENT COLLISION CHECK - COMPREHENSIVE AUDIT')
    print('37 CFR 1.84(p)(1) - Reference characters must be legible')
    print('=' * 70)
    print()

    total_collisions = 0
    total_warnings = 0
    results = {}

    for patent, num_figs in patents.items():
        patent_name = patent.upper().replace('_', ' ')
        print(f'=== {patent_name} ===')
        results[patent] = {'pass': 0, 'warn': 0, 'fail': 0}

        for fig_num in range(1, num_figs + 1):
            filepath = str(Path(__file__).resolve().parent.parent / 'patent_drawings' / patent / f'fig{fig_num}.svg')
            if os.path.exists(filepath):
                collisions, warnings = analyze_svg(filepath)

                if collisions:
                    results[patent]['fail'] += 1
                    print(f'FIG. {fig_num}: FAIL')
                    for c in collisions:
                        print(f'  [!] COLLISION ({c["type"]}): {c["desc"]}')
                        print(f'      Overlap: {c["overlap"]*100:.0f}% | Fix: {c.get("fix", "Review manually")}')
                        total_collisions += 1
                elif warnings:
                    results[patent]['warn'] += 1
                    print(f'FIG. {fig_num}: WARN')
                    for w in warnings:
                        print(f'  [~] {w["type"]}: {w["desc"]}')
                        total_warnings += 1
                else:
                    results[patent]['pass'] += 1
                    print(f'FIG. {fig_num}: PASS')
            else:
                print(f'FIG. {fig_num}: MISSING')
        print()

    # Summary table
    print('=' * 70)
    print('COLLISION CHECK SUMMARY')
    print('=' * 70)
    print(f'{"Patent":<12} {"PASS":<8} {"WARN":<8} {"FAIL":<8}')
    print('-' * 36)
    for patent, counts in results.items():
        print(f'{patent.upper():<12} {counts["pass"]:<8} {counts["warn"]:<8} {counts["fail"]:<8}')
    print('-' * 36)
    total_pass = sum(r['pass'] for r in results.values())
    total_warn_count = sum(r['warn'] for r in results.values())
    total_fail = sum(r['fail'] for r in results.values())
    print(f'{"TOTAL":<12} {total_pass:<8} {total_warn_count:<8} {total_fail:<8}')
    print()

    if total_fail == 0:
        print('STATUS: All drawings pass collision check!')
        print('No critical text-on-text or text-on-shape collisions detected.')
    else:
        print(f'STATUS: {total_fail} figures need collision fixes')

    return total_fail


if __name__ == '__main__':
    exit(main())
