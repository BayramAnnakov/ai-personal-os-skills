---
name: slide-inspector
description: "Visual and structural inspection of PowerPoint slides for quality, consistency, and design issues. Use this skill whenever reviewing, auditing, or QA-ing a .pptx file — whether you just created it or the user uploaded one. Triggers include: 'inspect my slides', 'check this deck', 'review this presentation', 'QA these slides', 'audit my pptx', 'are there any issues with this deck', or any request to evaluate slide quality. Also use as the QA step after creating any presentation with the pptx skill — every deck you produce should pass this inspection before being delivered. If you're about to declare a presentation 'done', run this skill first."
---

# Slide Inspector

A systematic quality audit for PowerPoint presentations. Catches layout bugs, design inconsistencies, readability problems, and structural anti-patterns that make slides look unpolished.

## When This Runs

**Post-creation QA (integrated):** After generating a .pptx with the pptx skill, run this inspection before delivering the file. Think of it as the compiler warnings step — you wouldn't ship code without checking for errors.

**Standalone audit:** When a user uploads a .pptx and asks you to review it, inspect it, or check for issues.

## The Inspection Pipeline

The inspection has two complementary layers. Both are needed — programmatic analysis catches structural issues humans miss (overlapping coordinates, font inconsistencies), while visual inspection catches aesthetic issues code can't judge (awkward spacing, visual weight imbalance).

### Step 1: Programmatic Analysis

Run the structural analyzer on the .pptx file:

```bash
python <this-skill-directory>/scripts/inspect_slides.py presentation.pptx
```

This script unpacks the PPTX XML and checks for:
- **Bounding box overlaps** — elements whose coordinates intersect
- **Edge proximity** — elements too close to slide margins (< 0.5")
- **Font inventory** — all fonts used, flagging inconsistencies (e.g., body text in 3 different fonts)
- **Color inventory** — all colors used, flagging palette sprawl
- **Text box fragmentation** — multiple single-line text boxes stacked vertically where one multi-line box would work (the "one box per line" anti-pattern)
- **Code snippet styling** — text using monospace fonts checked for: background fill, adequate padding, line height, box width vs content width
- **Font size variance** — same-role text (titles, body, captions) using inconsistent sizes across slides
- **Element count per slide** — flags slides with excessive element density

The script outputs a JSON report. Review it, but don't just parrot it — use it as input to your own judgment.

### Step 2: Visual Inspection

Convert slides to images and inspect them visually:

```bash
# Use the pptx skill's conversion pipeline (from the pptx skill's scripts directory)
python <pptx-skill>/scripts/office/soffice.py --headless --convert-to pdf presentation.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 presentation.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

Then view each slide image. Read `references/checklist.md` for the full visual inspection checklist. The key categories:

1. **Overlap & collision** — text through shapes, lines through words, stacked elements, footer colliding with content
2. **Spacing & alignment** — uneven gaps, elements too close, inconsistent margins, column misalignment
3. **Typography** — font consistency, size hierarchy, contrast against background, text wrapping issues
4. **Code snippets** — monospace font, background fill, padding, no wrapping, readable contrast, syntax coloring if present
5. **Visual consistency** — illustration style uniformity, icon treatment consistency, color palette adherence, image sizing patterns
6. **Simplicity & comprehension** — text density per slide, information hierarchy clarity, reading flow
7. **Structural anti-patterns** — "one box per line" fragmentation, redundant decorative elements, accent lines under titles (AI tell)

### Step 3: Generate Report

After both analysis passes, produce a structured report. The report has three output modes — use all three:

**A) In-chat issue list** — A concise summary in conversation, organized by severity:
- 🔴 **Critical** — Overlapping elements, text cut off, unreadable content
- 🟡 **Warning** — Inconsistent fonts/sizes, spacing issues, missing code styling
- 🟢 **Suggestion** — Minor aesthetic improvements, optional polish

**B) Annotated analysis** — For each slide with issues, describe what's wrong and where. Reference specific elements by their position (e.g., "the title text on slide 3 overlaps with the right-side image").

**C) Structured report file** — Save a markdown report to the filesystem:

```markdown
# Slide Inspection Report
## Summary
- X critical issues, Y warnings, Z suggestions
- Overall quality: [Poor / Needs Work / Good / Excellent]

## Slide-by-Slide Findings
### Slide 1: [slide title]
- [severity] [category]: [description]
...

## Cross-Slide Consistency
- Font usage: [findings]
- Color palette: [findings]
- Layout patterns: [findings]
- Code snippet styling: [findings]
- Illustration consistency: [findings]

## Recommendations
1. [prioritized fix]
2. ...
```

## Issue Categories — What to Look For

### Overlaps & Collisions
Elements whose bounding boxes intersect are the #1 visual bug. The programmatic analyzer catches coordinate overlaps, but visual inspection catches cases where elements are technically separate but visually collide (e.g., a descender from line 1 touching an ascender from line 2).

Common culprits:
- Decorative lines positioned for single-line titles that wrapped to two lines
- Source citations/footers that crept up into content area
- Icons placed inside text flow without adequate clearance
- Shape backgrounds that don't fully contain their text

### The "One Box Per Line" Anti-Pattern
This is one of the most common AI-generated slide problems. Instead of:
```javascript
// ❌ BAD: Separate addText() calls for each line
slide.addText("Line 1", { x: 1, y: 1, w: 8, h: 0.4 });
slide.addText("Line 2", { x: 1, y: 1.5, w: 8, h: 0.4 });
slide.addText("Line 3", { x: 1, y: 2, w: 8, h: 0.4 });
```

It should be:
```javascript
// ✅ GOOD: Single text box with breakLine
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 1, y: 1, w: 8, h: 1.5 });
```

The programmatic analyzer detects this by looking for sequences of text boxes at the same x-position with incrementing y-positions and similar widths. This pattern causes:
- Inconsistent line spacing (gaps between boxes ≠ natural line height)
- Selection/editing nightmares in PowerPoint
- Alignment brittleness — move one box and the paragraph breaks

### Code Snippet Styling
Code on slides needs special treatment to be readable. The inspection checks:

- **Font**: Must use a monospace font (Consolas, Courier New, Source Code Pro, Fira Code, JetBrains Mono). If code text is in Arial/Calibri, flag it.
- **Background**: Code blocks should have a filled background (light gray, dark theme, etc.) to visually separate them from surrounding content. No background = looks like regular text.
- **Padding**: The code text box should have internal margin/padding (at least 0.15") so text doesn't touch the edges of its background.
- **Line height**: Code needs tighter line spacing than prose. If line spacing is set to 1.5 or higher, flag it.
- **Width**: The code box must be wide enough that no line wraps. Wrapped code is unreadable. If the box width seems narrow relative to the longest code line, flag it.
- **Font size**: Code can be slightly smaller than body text (12-14pt is fine) but not so small it's unreadable (< 10pt).
- **Syntax coloring**: If the code has syntax highlighting (colored keywords), check that the colors have adequate contrast against the background. Light yellow keywords on a white background = invisible.

### Consistency Checks
These span the entire deck, not individual slides:

- **Font consistency**: Same role (title, body, caption) should use the same font and size across all slides. A title in Georgia on slide 1 and Calibri on slide 5 is a bug.
- **Color palette**: The deck should use a cohesive palette. Flag slides that introduce colors not used elsewhere — they break visual unity.
- **Layout rhythm**: Similar content types (e.g., "feature cards") should use similar layouts across slides. If slide 3 uses a 2-column layout for features and slide 7 uses a 3-column layout for similar content, that's worth flagging.
- **Illustration style**: If some slides use photos and others use flat vector icons, flag the mismatch. Mixing illustration styles looks unplanned.
- **Image sizing**: Similar-role images (e.g., team headshots, product screenshots) should be consistently sized across slides.
- **Decoration patterns**: If slide 2 has icons in colored circles and slide 6 has bare icons, flag the inconsistency. Pick one treatment and stick with it.

### Simplicity & Comprehension
Slides are a visual medium — dense text belongs in a document, not a deck.

- **Text density**: Flag slides with > 80 words. Suggest splitting or reducing.
- **Element count**: Flag slides with > 8 distinct elements (shapes + text boxes + images). Visual clutter hurts comprehension.
- **Font size floor**: Body text below 14pt is hard to read in a presentation setting. Flag anything below 12pt as critical.
- **Hierarchy clarity**: Every slide should have a clear visual hierarchy — one dominant element, supporting elements subordinate. If everything is the same size/weight, the audience doesn't know where to look.
- **Reading flow**: Content should flow left-to-right, top-to-bottom (for LTR languages). Flag layouts where the eye has to jump around.

## Severity Classification

Use these guidelines to assign severity:

| Severity | Criteria | Examples |
|----------|----------|----------|
| 🔴 Critical | Content is unreadable, missing, or visually broken | Text cut off, elements overlapping making text illegible, code in proportional font |
| 🟡 Warning | Noticeable quality issue that looks unprofessional | Inconsistent fonts across slides, uneven spacing, missing code background, "one box per line" pattern |
| 🟢 Suggestion | Minor polish that would elevate the deck | Slightly tighter margins possible, illustration style could be more unified, color palette could be tighter |

## Post-Inspection: What Happens Next

**If this was a post-creation QA step**: Fix all Critical and Warning issues before delivering. Re-run the inspection after fixes to verify — one fix often creates new problems (e.g., making a text box taller to prevent overflow may push it into the element below).

**If this was a standalone audit**: Present the report to the user and offer to fix the issues. Prioritize Critical → Warning → Suggestion.

## Dependencies

**Own scripts** (bundled with this skill):
- `scripts/inspect_slides.py` — Programmatic XML analysis

**From the pptx skill** (locate via `available_skills` → pptx → location):
- `scripts/office/soffice.py` — PDF conversion for visual inspection
- `scripts/office/unpack.py` — XML extraction (used internally by inspect_slides.py if needed)

**System tools** (pre-installed in the environment):
- `pdftoppm` (Poppler) — PDF to images
- `defusedxml` — Safe XML parsing (`pip install defusedxml` if missing)

**Path resolution at runtime**: When this skill triggers, resolve `<this-skill-directory>` to the directory containing this SKILL.md. Resolve `<pptx-skill>` by finding the pptx skill's location from `available_skills`. For example, if the pptx skill is at `/mnt/skills/public/pptx/`, its soffice script is at `/mnt/skills/public/pptx/scripts/office/soffice.py`.
