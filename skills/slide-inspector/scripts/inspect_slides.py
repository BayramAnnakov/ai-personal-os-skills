#!/usr/bin/env python3
"""
Programmatic slide inspector for PowerPoint files.

Unpacks a .pptx file and analyzes the XML structure for common issues:
- Bounding box overlaps between elements
- Elements too close to slide edges
- Font and color inventory with consistency checks
- Text box fragmentation ("one box per line" anti-pattern)
- Code snippet styling issues
- Font size variance across same-role elements
- Element density per slide

Usage:
    python inspect_slides.py presentation.pptx [--json] [--verbose]

Output:
    By default, prints a human-readable report. With --json, outputs structured JSON.
"""

import argparse
import json
import os
import re
import sys
import tempfile
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

# OOXML namespaces
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
}

# EMU (English Metric Unit) conversion: 914400 EMUs = 1 inch
EMU_PER_INCH = 914400

# Known monospace fonts (lowercase for matching)
MONOSPACE_FONTS = {
    'consolas', 'courier', 'courier new', 'source code pro', 'fira code',
    'fira mono', 'jetbrains mono', 'menlo', 'monaco', 'lucida console',
    'dejavu sans mono', 'ubuntu mono', 'roboto mono', 'cascadia code',
    'cascadia mono', 'sf mono', 'hack', 'inconsolata', 'droid sans mono',
}


def emu_to_inches(emu: int) -> float:
    """Convert EMUs to inches."""
    return round(emu / EMU_PER_INCH, 3)


@dataclass
class BoundingBox:
    """Represents an element's position and size on a slide."""
    x: float  # inches from left
    y: float  # inches from top
    w: float  # width in inches
    h: float  # height in inches

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def overlaps(self, other: 'BoundingBox', tolerance: float = 0.05) -> bool:
        """Check if two bounding boxes overlap (with tolerance for near-misses)."""
        return not (
            self.right <= other.x + tolerance or
            other.right <= self.x + tolerance or
            self.bottom <= other.y + tolerance or
            other.bottom <= self.y + tolerance
        )

    def distance_to_edge(self, slide_w: float = 10.0, slide_h: float = 5.625) -> dict:
        """Distance from each edge of the element to the slide boundary."""
        return {
            'left': round(self.x, 3),
            'top': round(self.y, 3),
            'right': round(slide_w - self.right, 3),
            'bottom': round(slide_h - self.bottom, 3),
        }


@dataclass
class SlideElement:
    """Represents a shape/text box/image on a slide."""
    element_type: str  # 'textbox', 'shape', 'image', 'group', 'other'
    bbox: BoundingBox
    text_content: str = ''
    font_face: Optional[str] = None
    font_size: Optional[float] = None  # in points
    font_color: Optional[str] = None
    has_fill: bool = False
    fill_color: Optional[str] = None
    is_code: bool = False  # detected as code snippet
    line_count: int = 1
    has_bullet: bool = False


@dataclass
class Issue:
    """A detected issue."""
    slide_num: int
    severity: str  # 'critical', 'warning', 'suggestion'
    category: str  # 'overlap', 'edge', 'font', 'color', 'fragmentation', 'code', 'density', 'consistency'
    description: str
    elements: list = field(default_factory=list)  # involved element descriptions


@dataclass
class SlideAnalysis:
    """Analysis results for a single slide."""
    slide_num: int
    elements: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    word_count: int = 0
    element_count: int = 0


def extract_slides_xml(pptx_path: str) -> list[tuple[int, ET.Element]]:
    """Extract slide XML elements from a .pptx file."""
    slides = []
    with zipfile.ZipFile(pptx_path, 'r') as zf:
        slide_files = sorted([
            f for f in zf.namelist()
            if re.match(r'ppt/slides/slide\d+\.xml$', f)
        ], key=lambda f: int(re.search(r'slide(\d+)', f).group(1)))

        for slide_file in slide_files:
            slide_num = int(re.search(r'slide(\d+)', slide_file).group(1))
            xml_content = zf.read(slide_file)
            root = ET.fromstring(xml_content)
            slides.append((slide_num, root))
    return slides


def parse_element(sp_elem: ET.Element) -> Optional[SlideElement]:
    """Parse a shape element into a SlideElement."""
    # Get position and size from spPr/xfrm
    xfrm = sp_elem.find('.//p:spPr/a:xfrm', NS)
    if xfrm is None:
        xfrm = sp_elem.find('.//a:xfrm', NS)
    if xfrm is None:
        return None

    off = xfrm.find('a:off', NS)
    ext = xfrm.find('a:ext', NS)
    if off is None or ext is None:
        return None

    try:
        x = emu_to_inches(int(off.get('x', 0)))
        y = emu_to_inches(int(off.get('y', 0)))
        w = emu_to_inches(int(ext.get('cx', 0)))
        h = emu_to_inches(int(ext.get('cy', 0)))
    except (ValueError, TypeError):
        return None

    if w == 0 and h == 0:
        return None

    bbox = BoundingBox(x, y, w, h)

    # Determine element type
    elem_type = 'other'
    if sp_elem.find('.//p:txBody', NS) is not None or sp_elem.find('.//a:txBody', NS) is not None:
        elem_type = 'textbox'
    elif sp_elem.find('.//a:blipFill', NS) is not None or sp_elem.find('.//p:blipFill', NS) is not None:
        elem_type = 'image'
    elif sp_elem.tag.endswith('}sp') or sp_elem.tag.endswith('}cxnSp'):
        elem_type = 'shape'

    # Extract text content and formatting
    text_parts = []
    fonts = []
    font_sizes = []
    font_colors = []
    has_bullet = False

    txBody = sp_elem.find('.//p:txBody', NS)
    if txBody is None:
        txBody = sp_elem.find('.//a:txBody', NS)
    if txBody is not None:
        for para in txBody.findall('.//a:p', NS):
            # Check for bullets
            pPr = para.find('a:pPr', NS)
            if pPr is not None:
                buNone = pPr.find('a:buNone', NS)
                buChar = pPr.find('a:buChar', NS)
                buAutoNum = pPr.find('a:buAutoNum', NS)
                if buChar is not None or buAutoNum is not None:
                    has_bullet = True

            for run in para.findall('.//a:r', NS):
                t = run.find('a:t', NS)
                if t is not None and t.text:
                    text_parts.append(t.text)

                rPr = run.find('a:rPr', NS)
                if rPr is not None:
                    # Font face
                    latin = rPr.find('a:latin', NS)
                    if latin is not None:
                        font = latin.get('typeface')
                        if font:
                            fonts.append(font)

                    # Font size (in hundredths of a point)
                    sz = rPr.get('sz')
                    if sz:
                        try:
                            font_sizes.append(int(sz) / 100)
                        except ValueError:
                            pass

                    # Font color
                    solidFill = rPr.find('a:solidFill', NS)
                    if solidFill is not None:
                        srgb = solidFill.find('a:srgbClr', NS)
                        if srgb is not None:
                            font_colors.append(srgb.get('val', ''))

    text_content = ' '.join(text_parts)
    line_count = max(1, len(txBody.findall('.//a:p', NS))) if txBody is not None else 1

    # Check for background fill on the shape
    has_fill = False
    fill_color = None
    spPr = sp_elem.find('.//p:spPr', NS)
    if spPr is None:
        spPr = sp_elem.find('p:spPr', NS)
    if spPr is not None:
        solidFill = spPr.find('a:solidFill', NS)
        if solidFill is not None:
            has_fill = True
            srgb = solidFill.find('a:srgbClr', NS)
            if srgb is not None:
                fill_color = srgb.get('val', '')

    # Detect if this is a code snippet
    is_code = False
    if fonts:
        primary_font = fonts[0].lower()
        if primary_font in MONOSPACE_FONTS:
            is_code = True
    # Also detect by content heuristics
    if text_content and not is_code:
        code_indicators = ['=>', '()', '{}', '[];', 'function ', 'const ', 'let ', 'var ',
                          'import ', 'def ', 'class ', 'return ', 'if (', '===', '!==',
                          'console.', 'print(', '#!/', 'sudo ', 'pip ', 'npm ']
        if sum(1 for ind in code_indicators if ind in text_content) >= 2:
            is_code = True

    return SlideElement(
        element_type=elem_type,
        bbox=bbox,
        text_content=text_content,
        font_face=fonts[0] if fonts else None,
        font_size=font_sizes[0] if font_sizes else None,
        font_color=font_colors[0] if font_colors else None,
        has_fill=has_fill,
        fill_color=fill_color,
        is_code=is_code,
        line_count=line_count,
        has_bullet=has_bullet,
    )


def analyze_slide(slide_num: int, root: ET.Element) -> SlideAnalysis:
    """Analyze a single slide for issues."""
    analysis = SlideAnalysis(slide_num=slide_num)

    # Find all shape elements
    spTree = root.find('.//p:cSld/p:spTree', NS)
    if spTree is None:
        return analysis

    shape_tags = [
        f'{{{NS["p"]}}}sp',
        f'{{{NS["p"]}}}pic',
        f'{{{NS["p"]}}}cxnSp',
        f'{{{NS["p"]}}}grpSp',
    ]

    for child in spTree:
        if child.tag in shape_tags:
            elem = parse_element(child)
            if elem:
                analysis.elements.append(elem)

    analysis.element_count = len(analysis.elements)
    analysis.word_count = sum(
        len(e.text_content.split()) for e in analysis.elements if e.text_content
    )

    # --- Check: Bounding box overlaps ---
    text_and_image_elems = [
        e for e in analysis.elements
        if e.element_type in ('textbox', 'image') and e.text_content.strip()
    ]
    for i, a in enumerate(text_and_image_elems):
        for b in text_and_image_elems[i+1:]:
            if a.bbox.overlaps(b.bbox, tolerance=0.02):
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='critical',
                    category='overlap',
                    description=f'Elements overlap: "{a.text_content[:40]}..." and "{b.text_content[:40]}..."',
                    elements=[
                        f'{a.element_type} at ({a.bbox.x}", {a.bbox.y}")',
                        f'{b.element_type} at ({b.bbox.x}", {b.bbox.y}")',
                    ]
                ))

    # --- Check: Edge proximity ---
    for elem in analysis.elements:
        if elem.element_type in ('textbox', 'image'):
            edges = elem.bbox.distance_to_edge()
            for edge_name, dist in edges.items():
                if dist < 0:
                    analysis.issues.append(Issue(
                        slide_num=slide_num,
                        severity='critical',
                        category='edge',
                        description=f'Element extends beyond {edge_name} edge by {abs(dist):.2f}" — content will be clipped',
                        elements=[f'{elem.element_type}: "{elem.text_content[:40]}"']
                    ))
                elif dist < 0.3 and elem.text_content.strip():
                    analysis.issues.append(Issue(
                        slide_num=slide_num,
                        severity='warning',
                        category='edge',
                        description=f'Element only {dist:.2f}" from {edge_name} edge (recommend ≥ 0.5")',
                        elements=[f'{elem.element_type}: "{elem.text_content[:40]}"']
                    ))

    # --- Check: Text box fragmentation ("one box per line") ---
    textboxes = [e for e in analysis.elements if e.element_type == 'textbox' and e.text_content.strip()]
    textboxes_sorted = sorted(textboxes, key=lambda e: (round(e.bbox.x, 1), e.bbox.y))

    i = 0
    while i < len(textboxes_sorted):
        # Look for sequences at same x with incrementing y, similar width, single-line each
        seq = [textboxes_sorted[i]]
        j = i + 1
        while j < len(textboxes_sorted):
            prev = seq[-1]
            curr = textboxes_sorted[j]
            same_x = abs(curr.bbox.x - prev.bbox.x) < 0.15
            sequential_y = 0 < (curr.bbox.y - prev.bbox.y) < 0.8
            similar_width = abs(curr.bbox.w - prev.bbox.w) < 0.5
            short_height = curr.bbox.h < 0.6 and prev.bbox.h < 0.6

            if same_x and sequential_y and similar_width and short_height:
                seq.append(curr)
                j += 1
            else:
                break

        if len(seq) >= 3:
            texts = [f'"{e.text_content[:30]}"' for e in seq[:4]]
            analysis.issues.append(Issue(
                slide_num=slide_num,
                severity='warning',
                category='fragmentation',
                description=f'{len(seq)} stacked single-line text boxes detected — should be one multi-line text box. Boxes contain: {", ".join(texts)}',
                elements=[f'y={e.bbox.y:.2f}" h={e.bbox.h:.2f}"' for e in seq]
            ))

        i = j if j > i + 1 else i + 1

    # --- Check: Code snippet styling ---
    for elem in analysis.elements:
        if elem.is_code:
            if elem.font_face and elem.font_face.lower() not in MONOSPACE_FONTS:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='critical',
                    category='code',
                    description=f'Code snippet uses proportional font "{elem.font_face}" — should use monospace (Consolas, Courier New, etc.)',
                    elements=[f'"{elem.text_content[:50]}"']
                ))

            if not elem.has_fill:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='warning',
                    category='code',
                    description='Code snippet has no background fill — hard to distinguish from regular text',
                    elements=[f'"{elem.text_content[:50]}"']
                ))

            if elem.font_size and elem.font_size < 10:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='warning',
                    category='code',
                    description=f'Code snippet font size is {elem.font_size}pt — too small for presentation readability (recommend ≥ 10pt)',
                    elements=[f'"{elem.text_content[:50]}"']
                ))

            # Check if box seems too narrow for code (rough heuristic)
            if elem.text_content:
                longest_line = max(
                    (line for line in elem.text_content.split('\n')),
                    key=len, default=''
                )
                # Rough: monospace char ≈ 0.08" at 12pt
                est_char_width = 0.08 * (elem.font_size / 12 if elem.font_size else 1)
                estimated_width = len(longest_line) * est_char_width + 0.3  # padding
                if estimated_width > elem.bbox.w * 1.1:
                    analysis.issues.append(Issue(
                        slide_num=slide_num,
                        severity='warning',
                        category='code',
                        description=f'Code box may be too narrow ({elem.bbox.w:.1f}") for content — lines may wrap',
                        elements=[f'Longest line: "{longest_line[:60]}"']
                    ))

    # --- Check: Element density ---
    if analysis.element_count > 10:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='warning',
            category='density',
            description=f'Slide has {analysis.element_count} elements — consider simplifying (recommend ≤ 8 distinct elements)',
        ))

    # --- Check: Word count ---
    if analysis.word_count > 120:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='critical',
            category='density',
            description=f'Slide has {analysis.word_count} words — this is a document, not a slide. Split into multiple slides.',
        ))
    elif analysis.word_count > 80:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='warning',
            category='density',
            description=f'Slide has {analysis.word_count} words — too text-heavy for a presentation slide (recommend ≤ 80)',
        ))

    # --- Check: Small font sizes ---
    for elem in analysis.elements:
        if elem.font_size and elem.font_size < 12 and not elem.is_code:
            analysis.issues.append(Issue(
                slide_num=slide_num,
                severity='warning',
                category='font',
                description=f'Text at {elem.font_size}pt is below recommended minimum (12pt) for readability',
                elements=[f'"{elem.text_content[:40]}"']
            ))

    return analysis


def analyze_cross_slide_consistency(analyses: list[SlideAnalysis]) -> list[Issue]:
    """Check for consistency issues across all slides."""
    issues = []

    # Collect all fonts by role
    title_fonts = defaultdict(list)  # font -> [slide_nums]
    body_fonts = defaultdict(list)
    all_colors = defaultdict(list)
    code_elements = []

    for analysis in analyses:
        for elem in analysis.elements:
            if elem.font_face:
                # Heuristic: large font = title, small = body
                if elem.font_size and elem.font_size >= 24:
                    title_fonts[elem.font_face].append(analysis.slide_num)
                elif elem.font_size and elem.font_size < 24:
                    body_fonts[elem.font_face].append(analysis.slide_num)

            if elem.font_color:
                all_colors[elem.font_color].append(analysis.slide_num)

            if elem.is_code:
                code_elements.append((analysis.slide_num, elem))

    # Font consistency
    if len(title_fonts) > 2:
        fonts_desc = ', '.join(f'{f} (slides {",".join(map(str,s[:3]))})' for f, s in title_fonts.items())
        issues.append(Issue(
            slide_num=0,
            severity='warning',
            category='consistency',
            description=f'Title text uses {len(title_fonts)} different fonts: {fonts_desc}. Pick one and use it everywhere.',
        ))

    if len(body_fonts) > 2:
        fonts_desc = ', '.join(f'{f} (slides {",".join(map(str,s[:3]))})' for f, s in body_fonts.items())
        issues.append(Issue(
            slide_num=0,
            severity='warning',
            category='consistency',
            description=f'Body text uses {len(body_fonts)} different fonts: {fonts_desc}. Pick one and use it everywhere.',
        ))

    # Color palette sprawl
    if len(all_colors) > 6:
        issues.append(Issue(
            slide_num=0,
            severity='suggestion',
            category='consistency',
            description=f'Deck uses {len(all_colors)} different text colors — consider tightening to 3-4 for a cohesive palette.',
        ))

    # Code snippet consistency
    if len(code_elements) >= 2:
        code_fonts = set(e.font_face for _, e in code_elements if e.font_face)
        code_fills = set(e.has_fill for _, e in code_elements)

        if len(code_fonts) > 1:
            issues.append(Issue(
                slide_num=0,
                severity='warning',
                category='consistency',
                description=f'Code snippets use inconsistent fonts: {", ".join(code_fonts)}. Use one monospace font throughout.',
            ))

        if True in code_fills and False in code_fills:
            issues.append(Issue(
                slide_num=0,
                severity='warning',
                category='consistency',
                description='Some code snippets have background fills and others don\'t. Apply consistent styling.',
            ))

    return issues


def format_report(analyses: list[SlideAnalysis], cross_issues: list[Issue], verbose: bool = False) -> str:
    """Format the analysis results as a human-readable report."""
    lines = []
    lines.append('=' * 60)
    lines.append('SLIDE INSPECTION REPORT')
    lines.append('=' * 60)

    # Summary counts
    all_issues = cross_issues.copy()
    for a in analyses:
        all_issues.extend(a.issues)

    critical = sum(1 for i in all_issues if i.severity == 'critical')
    warning = sum(1 for i in all_issues if i.severity == 'warning')
    suggestion = sum(1 for i in all_issues if i.severity == 'suggestion')

    lines.append(f'\nSummary: {critical} critical, {warning} warnings, {suggestion} suggestions')

    if critical == 0 and warning == 0:
        lines.append('Overall: ✅ Looking good!')
    elif critical > 0:
        lines.append('Overall: 🔴 Needs fixes before delivery')
    else:
        lines.append('Overall: 🟡 Acceptable but could be polished')

    # Cross-slide issues
    if cross_issues:
        lines.append(f'\n{"─" * 40}')
        lines.append('CROSS-SLIDE CONSISTENCY')
        lines.append(f'{"─" * 40}')
        for issue in cross_issues:
            icon = {'critical': '🔴', 'warning': '🟡', 'suggestion': '🟢'}[issue.severity]
            lines.append(f'{icon} [{issue.category}] {issue.description}')

    # Per-slide issues
    for analysis in analyses:
        if analysis.issues or verbose:
            lines.append(f'\n{"─" * 40}')
            lines.append(f'SLIDE {analysis.slide_num} ({analysis.element_count} elements, {analysis.word_count} words)')
            lines.append(f'{"─" * 40}')

            if not analysis.issues:
                lines.append('  No issues detected.')
            else:
                for issue in analysis.issues:
                    icon = {'critical': '🔴', 'warning': '🟡', 'suggestion': '🟢'}[issue.severity]
                    lines.append(f'  {icon} [{issue.category}] {issue.description}')
                    if verbose and issue.elements:
                        for elem in issue.elements:
                            lines.append(f'      → {elem}')

    lines.append(f'\n{"=" * 60}')
    return '\n'.join(lines)


def format_json(analyses: list[SlideAnalysis], cross_issues: list[Issue]) -> str:
    """Format the analysis results as JSON."""
    all_issues = [asdict(i) for i in cross_issues]
    for a in analyses:
        all_issues.extend(asdict(i) for i in a.issues)

    result = {
        'summary': {
            'total_slides': len(analyses),
            'total_issues': len(all_issues),
            'critical': sum(1 for i in all_issues if i['severity'] == 'critical'),
            'warnings': sum(1 for i in all_issues if i['severity'] == 'warning'),
            'suggestions': sum(1 for i in all_issues if i['severity'] == 'suggestion'),
        },
        'cross_slide_issues': [asdict(i) for i in cross_issues],
        'slides': [
            {
                'slide_num': a.slide_num,
                'element_count': a.element_count,
                'word_count': a.word_count,
                'issues': [asdict(i) for i in a.issues],
            }
            for a in analyses
        ],
    }
    return json.dumps(result, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Inspect PowerPoint slides for quality issues')
    parser.add_argument('pptx_file', help='Path to .pptx file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', action='store_true', help='Show element details for each issue')
    args = parser.parse_args()

    if not os.path.exists(args.pptx_file):
        print(f'Error: {args.pptx_file} not found', file=sys.stderr)
        sys.exit(1)

    if not args.pptx_file.endswith('.pptx'):
        print(f'Error: {args.pptx_file} is not a .pptx file', file=sys.stderr)
        sys.exit(1)

    # Extract and analyze
    slides = extract_slides_xml(args.pptx_file)
    analyses = [analyze_slide(num, root) for num, root in slides]
    cross_issues = analyze_cross_slide_consistency(analyses)

    # Output
    if args.json:
        print(format_json(analyses, cross_issues))
    else:
        print(format_report(analyses, cross_issues, verbose=args.verbose))


if __name__ == '__main__':
    main()
