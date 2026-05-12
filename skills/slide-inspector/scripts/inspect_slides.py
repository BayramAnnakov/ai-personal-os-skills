#!/usr/bin/env python3
"""
Programmatic slide inspector for PowerPoint files.

Unpacks a .pptx file and analyzes the XML structure for common issues:
- Bounding box overlaps between elements
- Elements too close to slide edges
- Off-canvas elements with text content (screen-share spoilers)
- Image aspect-ratio distortion
- Marooned images (small image on otherwise-empty slide)
- Empty / black-rectangle slides (silent generator failures)
- Disconnected diagram arrows
- Non-Latin script in text (visual font-coverage check needed)
- Font and color inventory with consistency checks
- Text box fragmentation ("one box per line" anti-pattern)
- Code snippet styling issues
- Font size variance across same-role elements
- Element density per slide
- Text density (presenter mode: 40w threshold)
- In-slide scaffolding leak (timing labels, "Block N", "Step N ·")
- Tool watermarks (leftover prompt fragments)
- Vague title verbs (AI scaffolding language)

Usage:
    python inspect_slides.py presentation.pptx [--json] [--verbose]

Output:
    By default, prints a human-readable report. With --json, outputs structured JSON.
"""

import argparse
import json
import os
import re
import struct
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field, asdict
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

# Default slide dimensions (16:9 widescreen) — overridden if presentation.xml specifies
DEFAULT_SLIDE_W_INCHES = 13.333
DEFAULT_SLIDE_H_INCHES = 7.5

# Known monospace fonts (lowercase for matching)
MONOSPACE_FONTS = {
    'consolas', 'courier', 'courier new', 'source code pro', 'fira code',
    'fira mono', 'jetbrains mono', 'menlo', 'monaco', 'lucida console',
    'dejavu sans mono', 'ubuntu mono', 'roboto mono', 'cascadia code',
    'cascadia mono', 'sf mono', 'hack', 'inconsolata', 'droid sans mono',
}

# Vague AI-scaffolding title openers (case-insensitive)
VAGUE_TITLE_VERBS = [
    'understanding', 'exploring', 'navigating', 'leveraging',
    'unlocking', 'diving into', 'unpacking', 'discovering',
]

# Tool watermark patterns (case-insensitive substrings)
TOOL_WATERMARK_PATTERNS = [
    r"here'?s a polished",
    r"here'?s the polished",
    r"as an ai",
    r"as a language model",
    r"i cannot",
    r"i'?m unable to",
    r"i don'?t have the ability",
    r"\bcertainly[!,.]",  # AI-flavored opener
    r"i'?d be happy to",
]

# In-slide scaffolding leak patterns
SCAFFOLDING_PATTERNS = [
    r"\bblock\s+\d+\b",                      # "Block 1", "Block 2"
    r"\bstep\s+\d+\s*[·•:]",                 # "Step 0 ·", "Step 1 :"
    r"\b\d+\s*(min|sec|hr|minutes?|seconds?|hours?)\b",  # "10min", "5 minutes"
    r"\bsection\s+\d+:",                     # "Section 3:"
    r"\bpart\s+\d+\s+of\s+\d+\b",            # "Part 1 of 5"
]

# Common placeholder/template artifacts
PLACEHOLDER_PATTERNS = [
    r"click to add (title|text|subtitle|content)",
    r"lorem ipsum",
    r"\[insert\b",
    r"\[your\s+\w+\s+here\]",
    r"\bxxx\b",
    r"\btbd\b",
    r"\bplaceholder\b",
]

# Non-Latin script Unicode ranges (for detection only — we don't claim to verify font coverage)
NON_LATIN_SCRIPT_RANGES = [
    ('Cyrillic', 0x0400, 0x04FF),
    ('Greek', 0x0370, 0x03FF),
    ('Hebrew', 0x0590, 0x05FF),
    ('Arabic', 0x0600, 0x06FF),
    ('Devanagari', 0x0900, 0x097F),
    ('CJK Unified Ideographs', 0x4E00, 0x9FFF),
    ('Hiragana', 0x3040, 0x309F),
    ('Katakana', 0x30A0, 0x30FF),
    ('Hangul Syllables', 0xAC00, 0xD7AF),
    ('Thai', 0x0E00, 0x0E7F),
]


def emu_to_inches(emu: int) -> float:
    """Convert EMUs to inches."""
    return round(emu / EMU_PER_INCH, 3)


def detect_non_latin_scripts(text: str) -> list[str]:
    """Return list of non-Latin script names present in text."""
    if not text:
        return []
    found = set()
    for ch in text:
        cp = ord(ch)
        for name, lo, hi in NON_LATIN_SCRIPT_RANGES:
            if lo <= cp <= hi:
                found.add(name)
                break
    return sorted(found)


def get_image_intrinsic_dims(zf: zipfile.ZipFile, image_path: str) -> Optional[tuple[int, int]]:
    """Read embedded image bytes and return (width_px, height_px). Supports PNG/JPEG/GIF."""
    try:
        data = zf.read(image_path)
    except KeyError:
        return None

    # PNG: 8-byte signature + IHDR (4 length + 4 type + 4 width + 4 height)
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        try:
            w = struct.unpack('>I', data[16:20])[0]
            h = struct.unpack('>I', data[20:24])[0]
            return (w, h)
        except struct.error:
            return None

    # JPEG: scan SOF marker
    if data[:2] == b'\xff\xd8':
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i+1]
            # SOF0..SOF3, SOF5..SOF7, SOF9..SOF11, SOF13..SOF15
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                try:
                    h = struct.unpack('>H', data[i+5:i+7])[0]
                    w = struct.unpack('>H', data[i+7:i+9])[0]
                    return (w, h)
                except struct.error:
                    return None
            # Skip this segment
            try:
                seg_len = struct.unpack('>H', data[i+2:i+4])[0]
                i += 2 + seg_len
            except struct.error:
                return None
        return None

    # GIF: signature + 4 bytes width/height (little-endian)
    if data[:6] in (b'GIF87a', b'GIF89a'):
        try:
            w = struct.unpack('<H', data[6:8])[0]
            h = struct.unpack('<H', data[8:10])[0]
            return (w, h)
        except struct.error:
            return None

    return None


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

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    def overlaps(self, other: 'BoundingBox', tolerance: float = 0.05) -> bool:
        """Check if two bounding boxes overlap (with tolerance for near-misses)."""
        return not (
            self.right <= other.x + tolerance or
            other.right <= self.x + tolerance or
            self.bottom <= other.y + tolerance or
            other.bottom <= self.y + tolerance
        )

    def distance_to_edge(self, slide_w: float, slide_h: float) -> dict:
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
    element_type: str  # 'textbox', 'shape', 'image', 'connector', 'group', 'other'
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
    is_title_placeholder: bool = False
    image_rid: Optional[str] = None  # for picture elements: r:embed ID
    intrinsic_w_px: Optional[int] = None  # for picture elements: source pixel width
    intrinsic_h_px: Optional[int] = None
    has_endpoint_connections: bool = True  # for connector elements: True if endpoints attach to shapes


@dataclass
class Issue:
    """A detected issue."""
    slide_num: int
    severity: str  # 'critical', 'warning', 'suggestion'
    category: str
    description: str
    elements: list = field(default_factory=list)


@dataclass
class SlideAnalysis:
    """Analysis results for a single slide."""
    slide_num: int
    elements: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    word_count: int = 0
    element_count: int = 0


def get_slide_dimensions(zf: zipfile.ZipFile) -> tuple[float, float]:
    """Read slide width/height from presentation.xml. Falls back to 16:9 widescreen."""
    try:
        data = zf.read('ppt/presentation.xml')
        root = ET.fromstring(data)
        sldSz = root.find('p:sldSz', NS)
        if sldSz is not None:
            cx = int(sldSz.get('cx', 0))
            cy = int(sldSz.get('cy', 0))
            if cx > 0 and cy > 0:
                return (emu_to_inches(cx), emu_to_inches(cy))
    except (KeyError, ET.ParseError, ValueError):
        pass
    return (DEFAULT_SLIDE_W_INCHES, DEFAULT_SLIDE_H_INCHES)


def get_slide_rels(zf: zipfile.ZipFile, slide_num: int) -> dict[str, str]:
    """Return a map of {rId: target_path} for a given slide's relationships file."""
    rels_path = f'ppt/slides/_rels/slide{slide_num}.xml.rels'
    try:
        data = zf.read(rels_path)
    except KeyError:
        return {}
    rels = {}
    try:
        root = ET.fromstring(data)
        for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            rid = rel.get('Id')
            target = rel.get('Target', '')
            # Resolve relative path: "../media/image1.png" → "ppt/media/image1.png"
            if target.startswith('../'):
                resolved = 'ppt/' + target[3:]
            elif target.startswith('/'):
                resolved = target.lstrip('/')
            else:
                resolved = f'ppt/slides/{target}'
            rels[rid] = resolved
    except ET.ParseError:
        return {}
    return rels


def extract_slides_xml(pptx_path: str) -> tuple[list[tuple[int, ET.Element]], float, float, dict]:
    """Extract slide XML elements + dimensions + per-slide rels from a .pptx file."""
    slides = []
    rels_by_slide = {}
    intrinsic_dims = {}  # {(slide_num, rid): (w_px, h_px)}

    with zipfile.ZipFile(pptx_path, 'r') as zf:
        slide_w, slide_h = get_slide_dimensions(zf)

        def _slide_num_from_path(path: str) -> int:
            m = re.search(r'slide(\d+)', path)
            return int(m.group(1)) if m else 0

        slide_files = sorted([
            f for f in zf.namelist()
            if re.match(r'ppt/slides/slide\d+\.xml$', f)
        ], key=_slide_num_from_path)

        for slide_file in slide_files:
            slide_num = _slide_num_from_path(slide_file)
            xml_content = zf.read(slide_file)
            root = ET.fromstring(xml_content)
            slides.append((slide_num, root))

            rels = get_slide_rels(zf, slide_num)
            rels_by_slide[slide_num] = rels

            # Pre-fetch intrinsic image dimensions for any image referenced by this slide
            for rid, target in rels.items():
                if any(target.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif')):
                    dims = get_image_intrinsic_dims(zf, target)
                    if dims:
                        intrinsic_dims[(slide_num, rid)] = dims

    return slides, slide_w, slide_h, {'rels': rels_by_slide, 'intrinsic_dims': intrinsic_dims}


def parse_element(sp_elem: ET.Element, slide_num: int, ctx: dict, slide_w: float, slide_h: float) -> Optional[SlideElement]:
    """Parse a shape element into a SlideElement."""
    # Detect placeholder upfront (needed for fallback bbox + later title checks)
    is_placeholder = False
    ph_type = ''
    nvSpPr = sp_elem.find('.//p:nvSpPr', NS)
    if nvSpPr is not None:
        ph = nvSpPr.find('.//p:ph', NS)
        if ph is not None:
            is_placeholder = True
            ph_type = ph.get('type', '') or ''
    is_title_placeholder = ph_type in ('title', 'ctrTitle')

    # Get position and size from spPr/xfrm
    xfrm = sp_elem.find('.//p:spPr/a:xfrm', NS)
    if xfrm is None:
        xfrm = sp_elem.find('.//a:xfrm', NS)

    if xfrm is None:
        # No explicit xfrm. Placeholders inherit from slide layout — use sensible defaults
        # so the element still reaches the title/text checks. Non-placeholders are skipped.
        if is_placeholder:
            if is_title_placeholder:
                bbox = BoundingBox(0.5, 0.3, slide_w - 1.0, 1.5)
            else:
                bbox = BoundingBox(0.5, 2.0, slide_w - 1.0, max(0.5, slide_h - 2.5))
        else:
            return None
    else:
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

    # Determine element type (initial classification)
    # NOTE: every <p:sp> from python-pptx / PowerPoint contains an empty <p:txBody>
    # whether or not the user added text. So we default <p:sp> to 'shape' and only
    # promote to 'textbox' AFTER parsing reveals real text content.
    elem_type = 'other'
    is_connector = sp_elem.tag.endswith('}cxnSp')
    is_picture = sp_elem.tag.endswith('}pic')

    if is_picture:
        elem_type = 'image'
    elif is_connector:
        elem_type = 'connector'
    elif sp_elem.tag.endswith('}sp'):
        elem_type = 'shape'  # promoted to 'textbox' below if real text is found

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
            pPr = para.find('a:pPr', NS)
            if pPr is not None:
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
                    latin = rPr.find('a:latin', NS)
                    if latin is not None:
                        font = latin.get('typeface')
                        if font:
                            fonts.append(font)

                    sz = rPr.get('sz')
                    if sz:
                        try:
                            font_sizes.append(int(sz) / 100)
                        except ValueError:
                            pass

                    solidFill = rPr.find('a:solidFill', NS)
                    if solidFill is not None:
                        srgb = solidFill.find('a:srgbClr', NS)
                        if srgb is not None:
                            font_colors.append(srgb.get('val', ''))

    text_content = ' '.join(text_parts)
    line_count = max(1, len(txBody.findall('.//a:p', NS))) if txBody is not None else 1

    # Promote shape → textbox if it actually has text content.
    # (We default <p:sp> to 'shape' since python-pptx/PPT always emit empty <p:txBody>.)
    if elem_type == 'shape' and text_content.strip():
        elem_type = 'textbox'

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
    if text_content and not is_code:
        code_indicators = ['=>', '()', '{}', '[];', 'function ', 'const ', 'let ', 'var ',
                          'import ', 'def ', 'class ', 'return ', 'if (', '===', '!==',
                          'console.', 'print(', '#!/', 'sudo ', 'pip ', 'npm ']
        if sum(1 for ind in code_indicators if ind in text_content) >= 2:
            is_code = True

    # Picture: extract embedded image rId and intrinsic dimensions
    image_rid = None
    intrinsic_w = intrinsic_h = None
    if is_picture:
        blip = sp_elem.find('.//a:blip', NS)
        if blip is not None:
            image_rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if image_rid:
                dims = ctx.get('intrinsic_dims', {}).get((slide_num, image_rid))
                if dims:
                    intrinsic_w, intrinsic_h = dims

    # Connector: check if endpoints connect to shapes
    has_endpoint_connections = True
    if is_connector:
        nvCxnSpPr = sp_elem.find('.//p:nvCxnSpPr', NS)
        st = end = None
        if nvCxnSpPr is not None:
            cNvCxnSpPr = nvCxnSpPr.find('p:cNvCxnSpPr', NS)
            if cNvCxnSpPr is not None:
                st = cNvCxnSpPr.find('a:stCxn', NS)
                end = cNvCxnSpPr.find('a:endCxn', NS)
        # If neither endpoint has stCxn/endCxn, the arrow is "free-floating"
        has_endpoint_connections = (st is not None) or (end is not None)

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
        is_title_placeholder=is_title_placeholder,
        image_rid=image_rid,
        intrinsic_w_px=intrinsic_w,
        intrinsic_h_px=intrinsic_h,
        has_endpoint_connections=has_endpoint_connections,
    )


def analyze_slide(slide_num: int, root: ET.Element, slide_w: float, slide_h: float, ctx: dict) -> SlideAnalysis:
    """Analyze a single slide for issues."""
    analysis = SlideAnalysis(slide_num=slide_num)

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
            elem = parse_element(child, slide_num, ctx, slide_w, slide_h)
            if elem:
                analysis.elements.append(elem)

    analysis.element_count = len(analysis.elements)
    analysis.word_count = sum(
        len(e.text_content.split()) for e in analysis.elements if e.text_content
    )

    slide_area = slide_w * slide_h

    # --- Check: Bounding box overlaps ---
    text_and_image_elems = [
        e for e in analysis.elements
        if e.element_type in ('textbox', 'image') and (e.text_content.strip() or e.element_type == 'image')
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

    # --- Check: Edge proximity + Off-canvas elements ---
    for elem in analysis.elements:
        if elem.element_type in ('textbox', 'image'):
            edges = elem.bbox.distance_to_edge(slide_w, slide_h)
            for edge_name, dist in edges.items():
                if dist < 0:
                    # Element extends beyond the slide
                    if elem.text_content.strip() and edge_name in ('bottom', 'right'):
                        # Off-canvas with text: critical screen-share spoiler
                        analysis.issues.append(Issue(
                            slide_num=slide_num,
                            severity='critical',
                            category='off-canvas',
                            description=f'Off-canvas element with text: extends beyond {edge_name} edge by {abs(dist):.2f}". Visible during screen-share — likely leftover from previous frame.',
                            elements=[f'{elem.element_type}: "{elem.text_content[:40]}"']
                        ))
                    else:
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

    # --- Check: Image aspect-ratio distortion ---
    for elem in analysis.elements:
        if elem.element_type == 'image' and elem.intrinsic_w_px and elem.intrinsic_h_px:
            if elem.bbox.w > 0 and elem.bbox.h > 0:
                rendered_ratio = elem.bbox.w / elem.bbox.h
                intrinsic_ratio = elem.intrinsic_w_px / elem.intrinsic_h_px
                if intrinsic_ratio > 0:
                    deviation = abs(rendered_ratio - intrinsic_ratio) / intrinsic_ratio
                    if deviation > 0.05:
                        direction = 'stretched horizontally' if rendered_ratio > intrinsic_ratio else 'stretched vertically'
                        analysis.issues.append(Issue(
                            slide_num=slide_num,
                            severity='warning',
                            category='image-distortion',
                            description=f'Image is {direction} ({deviation*100:.0f}% deviation from source ratio). Source: {elem.intrinsic_w_px}×{elem.intrinsic_h_px}px ({intrinsic_ratio:.2f}); rendered: {elem.bbox.w:.2f}×{elem.bbox.h:.2f}" ({rendered_ratio:.2f}).',
                            elements=[f'image at ({elem.bbox.x}", {elem.bbox.y}")']
                        ))

    # --- Check: Marooned image (small image alone on slide) ---
    images = [e for e in analysis.elements if e.element_type == 'image']
    text_elems_with_content = [e for e in analysis.elements if e.element_type == 'textbox' and e.text_content.strip()]

    for img in images:
        img_area_pct = (img.bbox.area / slide_area) * 100 if slide_area > 0 else 0
        if img_area_pct < 15:
            # Only flag as marooned if the slide is otherwise mostly empty
            other_content_area = sum(e.bbox.area for e in text_elems_with_content) + sum(i.bbox.area for i in images if i is not img)
            other_content_pct = (other_content_area / slide_area) * 100 if slide_area > 0 else 0
            if other_content_pct < 25:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='warning',
                    category='image-marooned',
                    description=f'Marooned image: occupies only {img_area_pct:.1f}% of slide area on a mostly-empty slide. Either enlarge the image or add content to fill the canvas.',
                    elements=[f'image at ({img.bbox.x}", {img.bbox.y}"), size {img.bbox.w:.1f}×{img.bbox.h:.1f}"']
                ))

    # --- Check: Disconnected diagram arrows ---
    connectors = [e for e in analysis.elements if e.element_type == 'connector']
    for conn in connectors:
        if not conn.has_endpoint_connections:
            analysis.issues.append(Issue(
                slide_num=slide_num,
                severity='warning',
                category='disconnected-arrow',
                description=f'Connector/arrow has no shape endpoints — free-floating. Likely indicates a broken diagram.',
                elements=[f'connector at ({conn.bbox.x}", {conn.bbox.y}")']
            ))

    # --- Check: Empty slides + black-rectangle slides ---
    if analysis.element_count < 3:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='critical',
            category='empty-slide',
            description=f'Slide has only {analysis.element_count} element(s) — likely a placeholder that didn\'t get filled or a generator failure.',
        ))

    # Black/colored rectangle: a filled shape covering >20% of slide with no text
    for elem in analysis.elements:
        if elem.element_type == 'shape' and elem.has_fill and not elem.text_content.strip():
            shape_area_pct = (elem.bbox.area / slide_area) * 100 if slide_area > 0 else 0
            if shape_area_pct > 20:
                color_desc = f' (#{elem.fill_color})' if elem.fill_color else ''
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='critical',
                    category='blank-rectangle',
                    description=f'Large filled rectangle{color_desc} covering {shape_area_pct:.0f}% of slide with no text. Likely a generator error (image failed to load or placeholder rendered as colored box).',
                    elements=[f'shape at ({elem.bbox.x}", {elem.bbox.y}"), size {elem.bbox.w:.1f}×{elem.bbox.h:.1f}"']
                ))

    # --- Check: Non-Latin script (flag for visual font-coverage verification) ---
    scripts_in_slide = set()
    for elem in analysis.elements:
        if elem.text_content:
            scripts = detect_non_latin_scripts(elem.text_content)
            scripts_in_slide.update(scripts)
    if scripts_in_slide:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='warning',
            category='non-latin-script',
            description=f'Slide contains non-Latin text ({", ".join(sorted(scripts_in_slide))}). Visually verify the rendered font supports the script — common bug: text renders as tofu (□□□).',
        ))

    # --- Check: Text box fragmentation ("one box per line") ---
    textboxes = [e for e in analysis.elements if e.element_type == 'textbox' and e.text_content.strip()]
    textboxes_sorted = sorted(textboxes, key=lambda e: (round(e.bbox.x, 1), e.bbox.y))

    i = 0
    while i < len(textboxes_sorted):
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

            if elem.text_content:
                longest_line = max(
                    (line for line in elem.text_content.split('\n')),
                    key=len, default=''
                )
                est_char_width = 0.08 * (elem.font_size / 12 if elem.font_size else 1)
                estimated_width = len(longest_line) * est_char_width + 0.3
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

    # --- Check: Text density (presenter mode: 40w threshold) ---
    if analysis.word_count > 60:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='critical',
            category='density',
            description=f'Slide has {analysis.word_count} words — way too text-heavy for a presenter slide. The presenter speaks the rest; the slide carries one idea. Split or reduce.',
        ))
    elif analysis.word_count > 40:
        analysis.issues.append(Issue(
            slide_num=slide_num,
            severity='warning',
            category='density',
            description=f'Slide has {analysis.word_count} words — too text-heavy for a presenter slide (recommend ≤ 40)',
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

    # --- Check: In-slide scaffolding leak ---
    for elem in analysis.elements:
        if not elem.text_content:
            continue
        for pattern in SCAFFOLDING_PATTERNS:
            m = re.search(pattern, elem.text_content, re.IGNORECASE)
            if m:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='warning',
                    category='scaffolding-leak',
                    description=f'In-slide scaffolding leak: "{m.group(0)}" looks like generator metadata (timing label, block marker, step counter). Strip it.',
                    elements=[f'in: "{elem.text_content[:60]}"']
                ))
                break  # one match per element is enough

    # --- Check: Tool watermarks (leftover prompt fragments) ---
    for elem in analysis.elements:
        if not elem.text_content:
            continue
        for pattern in TOOL_WATERMARK_PATTERNS:
            m = re.search(pattern, elem.text_content, re.IGNORECASE)
            if m:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='warning',
                    category='tool-watermark',
                    description=f'Tool watermark / leftover prompt fragment: "{m.group(0)}" — looks like AI-output scaffolding leaked into slide content.',
                    elements=[f'in: "{elem.text_content[:80]}"']
                ))
                break

    # --- Check: Vague title verbs ---
    for elem in analysis.elements:
        if not elem.is_title_placeholder or not elem.text_content:
            continue
        title_lc = elem.text_content.strip().lower()
        for verb in VAGUE_TITLE_VERBS:
            if title_lc.startswith(verb + ' ') or title_lc.startswith(verb + ':'):
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='suggestion',
                    category='vague-title',
                    description=f'Vague title verb: "{elem.text_content[:60]}" starts with "{verb.title()}" — AI scaffolding language. Suggest a concrete title that states the slide\'s actual point.',
                    elements=[f'title: "{elem.text_content[:80]}"']
                ))
                break

    # --- Check: Placeholder artifacts ---
    for elem in analysis.elements:
        if not elem.text_content:
            continue
        for pattern in PLACEHOLDER_PATTERNS:
            m = re.search(pattern, elem.text_content, re.IGNORECASE)
            if m:
                analysis.issues.append(Issue(
                    slide_num=slide_num,
                    severity='critical',
                    category='placeholder-leak',
                    description=f'Placeholder text not replaced: "{m.group(0)}" — template artifact left in deck.',
                    elements=[f'in: "{elem.text_content[:80]}"']
                ))
                break

    return analysis


def analyze_cross_slide_consistency(analyses: list[SlideAnalysis]) -> list[Issue]:
    """Check for consistency issues across all slides."""
    issues = []

    title_fonts = defaultdict(list)
    body_fonts = defaultdict(list)
    all_colors = defaultdict(list)
    code_elements = []

    for analysis in analyses:
        for elem in analysis.elements:
            if elem.font_face:
                if elem.font_size and elem.font_size >= 24:
                    title_fonts[elem.font_face].append(analysis.slide_num)
                elif elem.font_size and elem.font_size < 24:
                    body_fonts[elem.font_face].append(analysis.slide_num)

            if elem.font_color:
                all_colors[elem.font_color].append(analysis.slide_num)

            if elem.is_code:
                code_elements.append((analysis.slide_num, elem))

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

    if len(all_colors) > 6:
        issues.append(Issue(
            slide_num=0,
            severity='suggestion',
            category='consistency',
            description=f'Deck uses {len(all_colors)} different text colors — consider tightening to 3-4 for a cohesive palette.',
        ))

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
    lines = []
    lines.append('=' * 60)
    lines.append('SLIDE INSPECTION REPORT')
    lines.append('=' * 60)

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

    if cross_issues:
        lines.append(f'\n{"─" * 40}')
        lines.append('CROSS-SLIDE CONSISTENCY')
        lines.append(f'{"─" * 40}')
        for issue in cross_issues:
            icon = {'critical': '🔴', 'warning': '🟡', 'suggestion': '🟢'}[issue.severity]
            lines.append(f'{icon} [{issue.category}] {issue.description}')

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

    slides, slide_w, slide_h, ctx = extract_slides_xml(args.pptx_file)
    analyses = [analyze_slide(num, root, slide_w, slide_h, ctx) for num, root in slides]
    cross_issues = analyze_cross_slide_consistency(analyses)

    if args.json:
        print(format_json(analyses, cross_issues))
    else:
        print(format_report(analyses, cross_issues, verbose=args.verbose))


if __name__ == '__main__':
    main()
