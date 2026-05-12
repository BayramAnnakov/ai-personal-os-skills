---
name: slide-inspector
description: "Quality audit for PowerPoint decks. Catches layout bugs, design inconsistencies, accessibility issues, AI-generation tells, and silent generator failures."
when_to_use: "Use whenever reviewing, auditing, or QA-ing a .pptx file — whether you just created it or the user uploaded one. Triggers: 'inspect my slides', 'check this deck', 'review this presentation', 'QA these slides', 'audit my pptx', 'are there any issues with this deck'. Always use as the QA step after creating any presentation with the pptx skill — every deck must pass this inspection before delivery. If you're about to declare a presentation 'done', run this skill first. Also: 'calibrate slide-inspector' triggers one-time calibration mode that mines the user's correction history."
allowed-tools: Bash(python3 *) Bash(bash *) Bash(pdftoppm *) Bash(ls *) Bash(rm slide-*.jpg) Read
---

# Slide Inspector

A systematic quality audit for PowerPoint presentations. Catches layout bugs, design inconsistencies, readability problems, structural anti-patterns, and AI-generation tells that make slides look unpolished.

## When This Runs

**Post-creation QA (integrated):** After generating a .pptx with the pptx skill, run this inspection before delivering the file. Think of it as the compiler warnings step — you wouldn't ship code without checking for errors.

**Standalone audit:** When a user uploads a .pptx and asks you to review it, inspect it, or check for issues.

**Calibration (one-off, opt-in):** When the user invokes `calibrate` mode, scan their CC history to learn their personal correction patterns and propose custom checks. See `references/calibration.md` for the procedure.

## Step 0: First-Run Calibration Prompt

Before starting any inspection, check whether the user has been offered calibration:

1. Check if `~/.claude/skills/slide-inspector/user-overrides.yaml` exists.
2. **If it does NOT exist** — this is the user's first invocation. Prompt them ONCE, briefly:
   > "First time running slide-inspector. I can calibrate it to YOUR style by mining your past pptx correction history (~5-10 min). This adds custom checks for patterns you fix repeatedly that aren't in the defaults. Want to calibrate first? (yes / no)"
3. Based on the answer:
   - **yes** → Follow `references/calibration.md` to run the calibration procedure. It creates `user-overrides.yaml` populated with approved patterns. Then proceed with the inspection.
   - **no** → Write a minimal stub to `~/.claude/skills/slide-inspector/user-overrides.yaml`:
     ```yaml
     # User declined calibration on first run. Hand-edit anytime to add custom checks.
     # Re-run calibration any time with: "calibrate slide-inspector"
     overrides:
       calibration_status: declined
     checks: []
     ```
     Then proceed with the inspection. Do not ask again.
4. **If user-overrides.yaml DOES exist** — skip this step entirely. Calibration has either been completed or explicitly declined. Proceed straight to Step 1.

This is a one-time UX moment per user. Once the file exists, it's never re-prompted. The user can re-run calibration any time by saying "calibrate slide-inspector" — that just appends new patterns to the existing file.

## The Inspection Pipeline

The inspection has two complementary layers. Both are needed — programmatic analysis catches structural issues humans miss (overlapping coordinates, font inconsistencies, off-canvas elements), while visual inspection catches aesthetic issues code can't judge (awkward spacing, visual weight imbalance).

### Step 1: Programmatic Analysis

Run the structural analyzer on the .pptx file:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/inspect_slides.py presentation.pptx
```

This script unpacks the PPTX XML and checks for:
- **Bounding box overlaps** — elements whose coordinates intersect
- **Edge proximity** — elements too close to slide margins (< 0.5")
- **Off-canvas elements with text** — content beyond slide bounds (visible during screen-share)
- **Image aspect-ratio distortion** — rendered cx/cy ratio deviates >5% from source intrinsic ratio
- **Marooned image** — small image (<15% of slide area) on otherwise-empty slide
- **Empty / black-rectangle slides** — fewer than 3 elements OR large unfilled rectangle (silent generator failures)
- **Disconnected diagram arrows** — `<p:cxnSp>` connectors with no shape endpoints
- **Non-Latin script in text** — flags slides with Cyrillic/CJK/Arabic/etc. for visual font-coverage check (rendering as tofu/squares is a common bug)
- **Font inventory** — all fonts used, flagging inconsistencies
- **Color inventory** — all colors used, flagging palette sprawl
- **Text box fragmentation** — multiple single-line text boxes stacked vertically (the "one box per line" anti-pattern)
- **Code snippet styling** — text using monospace fonts checked for: background fill, padding, line height, box width vs content
- **Font size variance** — same-role text using inconsistent sizes across slides
- **Element count per slide** — flags slides with excessive element density
- **Text density (presenter mode)** — >40 words = warning, >60 = critical
- **In-slide scaffolding leak** — text matching timing labels (`Block 1 · 10min`, `Step N ·`, `\d+\s*min`) — generator metadata bleeding into slide content
- **Tool watermarks** — text matching AI-output leaks: `Here's a polished`, `As an AI`, `I cannot`, trailing markdown `**`
- **Vague title verbs** — titles starting with `Understanding X`, `Exploring Y`, `Navigating Z`, `Leveraging`, `Unlocking`, `Diving into` (AI scaffolding language)

The script outputs a JSON report. Review it, but don't just parrot it — use it as input to your own judgment.

### Step 2: Visual Inspection

Convert slides to images and inspect them visually. Uses `soffice` (LibreOffice) + `pdftoppm` (Poppler) — both common system tools, neither tied to any other skill:

```bash
# Convert pptx → pdf, then pdf → jpeg per slide
soffice --headless --convert-to pdf presentation.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 presentation.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

If LibreOffice isn't installed: `brew install --cask libreoffice` (macOS) or `apt install libreoffice` (Debian/Ubuntu). `pdftoppm` comes with `poppler` (`brew install poppler`).

If the user has the pptx skill installed, an alternative is its `scripts/thumbnail.py` which produces a multi-slide grid image instead of one-image-per-slide — useful for deck-level scanning.

Then view each slide image. Read `references/checklist.md` for the full visual inspection checklist. The key categories:

1. **Overlap & collision** — text through shapes, lines through words, stacked elements, footer colliding with content, off-canvas elements visible during screen-share
2. **Spacing & alignment** — uneven gaps, elements too close, inconsistent margins, column misalignment
3. **Typography** — font consistency, size hierarchy, contrast against background, text wrapping issues, **non-Latin script rendering**
4. **Code snippets** — monospace font, background fill, padding, no wrapping, readable contrast, syntax coloring if present
5. **Visual consistency** — illustration style uniformity, icon treatment consistency, color palette adherence, image sizing patterns
6. **Image treatment** — aspect-ratio integrity, marooned images, disconnected diagram arrows
7. **Simplicity & comprehension** — text density per slide (presenter mode: 40w threshold), information hierarchy clarity, reading flow
8. **Structural anti-patterns** — "one box per line" fragmentation, accent lines under titles (AI tell), in-slide scaffolding leak, vague title verbs, tool watermarks, redundant decorative elements

### Step 3: Generate Report

After both analysis passes, produce a structured report. The report has three output modes — use all three:

**A) In-chat issue list** — A concise summary in conversation, organized by severity:
- 🔴 **Critical** — Overlapping elements, text cut off, unreadable content, off-canvas text visible during screen-share, empty slides, code in proportional font
- 🟡 **Warning** — Inconsistent fonts/sizes, spacing issues, missing code styling, image aspect distortion, marooned images, scaffolding leaks, vague title verbs, non-Latin script needing font verification
- 🟢 **Suggestion** — Minor aesthetic improvements, optional polish, AI-tell vocabulary

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
- **Off-canvas elements with text content** — y-coordinate beyond slide bounds. Critical because screen-shares expose anything below the visible slide; "leftover from previous frame still present" is a classic AI-iteration bug.

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

### Image Treatment

- **Aspect-ratio integrity** — Each picture's rendered cx/cy ratio should match its embedded image's intrinsic pixel ratio. Deviation >5% means the image is stretched or squished; rescale to preserve ratio. This is the #1 empirical issue with AI-generated decks (~10× across 5 sessions in real-world correction history).
- **Marooned images** — A single small image (<15% of slide area) sitting in a corner of an otherwise-empty slide is a layout failure. Either the image should be larger (use the canvas) or other content should fill the rest.
- **Disconnected diagram arrows** — `<p:cxnSp>` connectors with no shape endpoints (free-floating arrows) usually indicate broken diagram generation. Common with AI-generated systems-thinking diagrams.

### Non-Latin Script Coverage

For decks containing Cyrillic, CJK, Arabic, Devanagari, Hebrew, Greek, etc.:

- The analyzer flags slides whose text runs contain non-Latin characters. Visually verify that the rendered font supports the script — some fonts render Cyrillic/CJK as tofu (□□□) or wrong glyphs.
- This is real-world breakage when the pptx generator picks Latin-only fonts for non-English content.

### Consistency Checks
These span the entire deck, not individual slides:

- **Font consistency**: Same role (title, body, caption) should use the same font and size across all slides. A title in Georgia on slide 1 and Calibri on slide 5 is a bug.
- **Color palette**: The deck should use a cohesive palette. Flag slides that introduce colors not used elsewhere — they break visual unity.
- **Layout rhythm**: Similar content types (e.g., "feature cards") should use similar layouts across slides. If slide 3 uses a 2-column layout for features and slide 7 uses a 3-column layout for similar content, that's worth flagging.
- **Illustration style**: If some slides use photos and others use flat vector icons, flag the mismatch. Mixing illustration styles looks unplanned.
- **Image sizing**: Similar-role images (e.g., team headshots, product screenshots) should be consistently sized across slides.
- **Decoration patterns**: If slide 2 has icons in colored circles and slide 6 has bare icons, flag the inconsistency. Pick one treatment and stick with it.

### Simplicity & Comprehension

Slides are a visual medium — dense text belongs in a document, not a deck. **This skill assumes presenter mode** (you're showing the slide while speaking). Density thresholds reflect that:

- **Text density (presenter mode)**: Flag slides with >40 words as warning; >60 as critical. The presenter speaks the rest; the slide carries one idea.
- **Element count**: Flag slides with > 8 distinct elements (shapes + text boxes + images). Visual clutter hurts comprehension.
- **Font size floor**: Body text below 14pt is hard to read in a presentation setting. Flag anything below 12pt as critical.
- **Hierarchy clarity**: Every slide should have a clear visual hierarchy — one dominant element, supporting elements subordinate. If everything is the same size/weight, the audience doesn't know where to look.
- **Reading flow**: Content should flow left-to-right, top-to-bottom (for LTR languages). Flag layouts where the eye has to jump around.

### Empty / Silent-Failure Slides

- **Empty slides**: Fewer than 3 elements often indicates a placeholder slide that didn't get filled. Flag.
- **Black or large unfilled rectangles**: Shapes with fill but no text covering >20% of slide area often indicate a generator error (image failed to load, placeholder rendered as colored box).

### Structural Anti-Patterns

- **"One box per line"** — Multiple stacked text boxes where a single multi-line text box should be used.
- **Accent lines under titles** — Thin decorative lines under titles are a strong signal of AI generation. Use whitespace or background color instead.
- **In-slide scaffolding leak** — Generator metadata bleeding into slide text: timing labels ("Block 1 · 10min"), step markers ("Step 0 · 8 min · Clear the W2 debt"), section numbers in slide body. Strip these.
- **Tool watermarks / leftover prompt fragments** — "Here's a polished", "As an AI", "I cannot", trailing markdown `**` — slipped through generation if user prompt contained scaffolding.
- **Vague title verbs** — Titles starting with "Understanding X", "Exploring Y", "Navigating Z", "Leveraging", "Unlocking", "Diving into" are AI-scaffolding language. Suggest a concrete title that states the slide's actual point.
- **Identical layouts** — Are all content slides using the exact same layout? Vary between columns, cards, callouts, and full-bleed images.
- **Bullet point overuse** — Are most slides just "title + bullet list"? Mix in other formats: stat callouts, comparison columns, timelines, diagrams.
- **Placeholder artifacts** — Is there any leftover template text like "Click to add title", "Lorem ipsum", "XXX", "[Insert]"?
- **Double bullets** — When bullet formatting is applied, are there also Unicode bullet characters (•) in the text, creating double bullets?

### Deck-Level Structural Audits

These checks span the whole deck rather than individual slides. They surface the kind of scaffolding bloat that experienced presenters strip out — the "skeleton" left behind when an AI builds a "complete" deck instead of a sparse briefing.

- **Preamble overhead**: Count slides before the first content slide (title + agenda + accountability + intro). If preamble exceeds ~15% of total deck length, flag as "preamble feels heavy for deck size — consider opening straight into content."

- **Decorative section dividers**: A section divider is a slide whose only content is a section label + tagline (no charts, screenshots, or data). Flag any divider whose section has fewer than 4 content slides — the divider is heavier than the section it introduces. Suggest replacing with a color-shifted title on the next content slide.

- **Image-led slide hierarchy**: When a slide has a chart, screenshot, or photograph that is clearly the slide's primary information carrier, check that the visual occupies the majority of the canvas (>50% of slide area). If the title text-block is comparable in size to the chart, the layout is reading as "chart caption" rather than "chart." Suggest the inverted layout: chart on top full-width → thin rule → title in band below.

- **Generated metaphorical imagery on specific-entity slides**: When a slide's topic names a specific real product, research paper, news incident, or company action (e.g., "Project Glasswing", "Anthropic post-mortem", "Figure 03 walks at White House"), and the visual on that slide is a stylized illustration / abstract metaphor, flag as "verify a real asset doesn't exist (official product graphic, research figure, press photo)." Real artifacts are nearly always more compelling than generated metaphors when the topic is concrete.

- **Color-as-architecture overuse**: If section colors appear on multiple decorative elements per slide (title + accent bar + glyph + underline), flag as "color is doing structural work that could be done by typography alone." A single colored title is usually sufficient.

- **Closing-slide weakness**: The final slide should ask a directive question or specify a concrete next step, not merely announce a generic ritual ("Q&A", "Thank you", "Commitment round"). Flag generic closes as a missed opportunity.

## User Overlay (Calibration)

Every user has personal correction patterns that go beyond the defaults. The skill supports a `user-overrides.yaml` file that adds custom checks specific to the user.

To generate this file from the user's own correction history:

```
User: "calibrate slide-inspector"
```

This triggers the calibration procedure described in `references/calibration.md`:

1. Scan `~/.claude/projects/*/` for pptx-related sessions
2. Extract user messages that follow pptx generation or slide-inspector runs
3. Cluster correction patterns
4. Propose top patterns as candidate custom checks (with verbatim examples)
5. User approves which to add
6. Write approved checks to `~/.claude/skills/slide-inspector/user-overrides.yaml`

The user-overrides file is loaded automatically on every subsequent inspection. See `user-overrides.yaml.example` for the schema and worked examples.

**Calibration is opt-in.** New users get full default coverage out of the box. Calibration is recommended after ~10+ pptx sessions when there's enough correction history to find real patterns.

## Severity Classification

Use these guidelines to assign severity:

| Severity | Criteria | Examples |
|----------|----------|----------|
| 🔴 Critical | Content is unreadable, missing, or visually broken | Text cut off, elements overlapping making text illegible, code in proportional font, off-canvas text visible during screen-share, empty slides, non-Latin text rendering as tofu |
| 🟡 Warning | Noticeable quality issue that looks unprofessional | Inconsistent fonts across slides, uneven spacing, missing code background, "one box per line" pattern, image aspect distortion, marooned images, scaffolding leaks, vague title verbs, tool watermarks |
| 🟢 Suggestion | Minor polish that would elevate the deck | Slightly tighter margins possible, illustration style could be more unified, color palette could be tighter, AI-tell vocabulary |

## Post-Inspection: What Happens Next

**If this was a post-creation QA step**: Fix all Critical and Warning issues before delivering. Re-run the inspection after fixes to verify — one fix often creates new problems (e.g., making a text box taller to prevent overflow may push it into the element below).

**If this was a standalone audit**: Present the report to the user and offer to fix the issues. Prioritize Critical → Warning → Suggestion.

## Dependencies

**Own scripts** (bundled with this skill):
- `scripts/inspect_slides.py` — Programmatic XML analysis
- `scripts/calibrate.sh` — Bash pre-filter for the calibration procedure (greps + jq-extracts pptx-related session corrections from `~/.claude/projects/`)

**Own references** (bundled):
- `references/checklist.md` — Full visual inspection checklist
- `references/calibration.md` — Step-by-step procedure for calibration mode

**Templates** (bundled):
- `user-overrides.yaml.example` — Schema and worked example for custom checks

**System tools** (must be installed; not bundled):
- `soffice` (LibreOffice) — PowerPoint to PDF conversion. Install: `brew install --cask libreoffice` or `apt install libreoffice`.
- `pdftoppm` (Poppler) — PDF to JPEG. Install: `brew install poppler` or `apt install poppler-utils`.
- `python3` — runs `inspect_slides.py`. Only Python stdlib used (no PIL/python-pptx required).
- `jq` — used by `calibrate.sh` for jsonl parsing. Install: `brew install jq` or `apt install jq`.

**Optional**: the pptx skill (Anthropic's bundled `document-skills/pptx`) ships a `scripts/thumbnail.py` that produces a single grid image instead of per-slide images. If the user has it installed, prefer that for fast deck-level scans. slide-inspector does NOT require the pptx skill — they're independent.

**Path resolution at runtime**: Use `${CLAUDE_SKILL_DIR}` for paths inside this skill — Claude Code resolves it automatically regardless of where this skill is installed.

## Gotchas

Real-world quirks that have bitten this skill in practice. Read these before reporting findings.

- **`<p:sp>` shapes always carry an empty `<p:txBody>`** in python-pptx/PowerPoint output, whether or not the user added text. The analyzer's `parse_element` defaults `<p:sp>` to `shape` and only promotes to `textbox` when actual text is present. If you see a "blank-rectangle" issue, the analyzer correctly identified a filled shape with no real text — don't second-guess it.

- **Title placeholders may have no `<a:xfrm>` element**. They inherit position from the slide layout. The analyzer falls back to a default title-area bbox so the title still reaches `vague-title` and other title checks. The reported coordinates for inherited-position titles are approximate, not exact.

- **Off-canvas elements with text are screen-share spoilers, even if they look "decorative"**. Flag as critical regardless of whether the text seems important — anyone screen-sharing the deck will see anything below the slide. Common cause: leftover element from a previous frame during AI iteration.

- **`non-latin-script` is a flag for visual review, not a confirmed font-coverage failure**. The analyzer detects script presence but doesn't verify font coverage. Always render the slide and check whether the text appears as readable glyphs vs tofu (□□□).

- **The `placeholder-leak` check is a substring match** — it will fire on the literal word "placeholder" in any context. If a slide is legitimately ABOUT placeholders (e.g., a tutorial slide), this is a false positive — exercise judgment.

- **Slide dimensions vary** — 4:3 (10×7.5") vs 16:9 widescreen (13.33×7.5"). The analyzer reads from `presentation.xml` and falls back to widescreen if missing. Off-canvas calculations adjust automatically.

- **Image intrinsic dimensions are read directly from PNG/JPEG/GIF headers** with no PIL dependency. This works for most embeds but fails silently for unusual formats (TIFF, WMF, EMF). If aspect-distortion checks miss an image, check the embedded format.

- **Density thresholds assume presenter mode** (40w warning, 60w critical). For document-style decks (slidedocs intended for reading, not presenting), these thresholds are too aggressive — note this in your report rather than fixing the slide.
