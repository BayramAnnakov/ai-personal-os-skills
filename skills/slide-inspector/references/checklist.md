# Visual Inspection Checklist

Use this checklist when visually reviewing slide images. The programmatic analyzer catches coordinate-level issues, but these checks require human (or AI vision) judgment.

## Table of Contents
1. [Overlap & Collision](#overlap--collision)
2. [Spacing & Alignment](#spacing--alignment)
3. [Typography](#typography)
4. [Code Snippets](#code-snippets)
5. [Visual Consistency](#visual-consistency)
6. [Image Treatment](#image-treatment)
7. [Non-Latin Script Coverage](#non-latin-script-coverage)
8. [Simplicity & Comprehension](#simplicity--comprehension)
9. [Empty / Silent-Failure Slides](#empty--silent-failure-slides)
10. [Structural Anti-Patterns](#structural-anti-patterns)
11. [Slide-Type-Specific Checks](#slide-type-specific-checks)

---

## Overlap & Collision

These are the highest-priority visual bugs. Even a 1-pixel overlap makes a slide look broken.

- [ ] **Text through shapes**: Does any text visually intersect with a shape, line, or decorative element?
- [ ] **Lines through words**: Do decorative lines, dividers, or connectors cross over text?
- [ ] **Stacked elements**: Are any elements piled on top of each other in a way that wasn't intentional (e.g., a caption sitting on top of body text)?
- [ ] **Footer/citation collision**: Do source citations, page numbers, or footer text collide with the content above them?
- [ ] **Decorative vs content conflict**: Do decorative elements (background shapes, accent lines, watermarks) interfere with reading the actual content?
- [ ] **Icon-text clearance**: When icons sit next to text, is there enough gap (at least 0.15") between them?
- [ ] **Title wrapping problems**: If a title wraps to two lines, does it push into or overlap with content below? (Common with decorative underlines designed for single-line titles.)
- [ ] **Off-canvas elements visible during screen-share**: Any elements positioned BELOW or to the RIGHT of the slide bounds. Even though they're "outside" the slide, screen-share viewers see the full window. Common AI-iteration bug: leftover elements from a previous frame still hanging below the visible slide area.
- [ ] **Person-image overlap with title text**: On title slides where a portrait/character is meant to be visible, check that text isn't covering the face/key parts of the image.

## Spacing & Alignment

Uneven spacing makes slides look hastily assembled, even if the content is excellent.

- [ ] **Consistent gaps**: Are gaps between similar elements (e.g., between bullet points, between cards) uniform? Visually measure — don't trust your first impression.
- [ ] **Edge margins**: Is there at least 0.5" of breathing room from all slide edges? Content touching edges looks cramped.
- [ ] **Column alignment**: If there are multiple columns, are they aligned at the top? Do they have equal widths or deliberately different widths?
- [ ] **Card/grid alignment**: In grid layouts, are all cards the same size? Are the gutters between them uniform?
- [ ] **Vertical rhythm**: Does the vertical spacing between sections follow a consistent pattern?
- [ ] **Empty space distribution**: Is whitespace distributed intentionally, or are there awkward large gaps in some places and cramped areas in others?
- [ ] **Horizontal alignment of text starts**: Do body text blocks across slides start at the same x-position? Inconsistent left margins across slides feel sloppy.
- [ ] **Element centering**: If elements are meant to be centered, are they actually centered? Off-center "centered" elements are very noticeable.

## Typography

Font issues are subtle but create an unprofessional impression across the deck.

- [ ] **Font consistency by role**: Do all titles use the same font and size? All body text? All captions?
- [ ] **Size hierarchy**: Is there clear visual hierarchy? Titles should be noticeably larger than body text (at least 8pt difference). Captions should be noticeably smaller.
- [ ] **Contrast against background**: Can all text be read easily against its background? Check light text on light backgrounds, dark text on dark backgrounds, and text over images.
- [ ] **Text wrapping**: Are any text boxes too narrow, causing awkward wrapping (e.g., one word on a second line)?
- [ ] **Orphaned words**: Are there single words dangling on their own line at the end of a paragraph?
- [ ] **Alignment consistency**: If titles are left-aligned on most slides, are they left-aligned on ALL slides? A suddenly centered title breaks rhythm.
- [ ] **Bold/italic consistency**: Are emphasis styles (bold, italic) used consistently for the same purpose across slides?
- [ ] **All-caps consistency**: If some titles are ALL CAPS, all titles should be ALL CAPS (or none should).

## Code Snippets

Code on slides needs fundamentally different styling than prose. Every code block should pass these checks:

- [ ] **Monospace font**: Is the code in Consolas, Courier New, Source Code Pro, Fira Code, JetBrains Mono, or another monospace font? Code in Arial or Calibri is unacceptable.
- [ ] **Background fill**: Does the code block have a distinct background (light gray, dark theme, etc.) that visually separates it from surrounding content? Without a background, code blends into regular text.
- [ ] **Padding**: Is there visible internal padding between the code text and the edges of its background box? Text touching the box edges looks cramped. At least 0.15" on all sides.
- [ ] **No wrapping**: Do any code lines wrap? If yes, either the font is too large or the box is too narrow. Wrapped code is very hard to read.
- [ ] **Line height**: Is the code line spacing tight (1.0-1.15)? Code with 1.5 line spacing looks wrong and wastes vertical space.
- [ ] **Font size**: Is the code between 10-14pt? Smaller than 10pt is unreadable. Larger than 16pt wastes space.
- [ ] **Syntax coloring**: If syntax highlighting is present, do the colors have adequate contrast against the code block's background? Yellow keywords on white = invisible.
- [ ] **Consistent code styling**: If there are multiple code blocks across slides, do they all use the same font, background color, padding, and size?
- [ ] **Language-appropriate**: Does the code look like real, syntactically correct code? Pseudo-code presented as real code with syntax highlighting looks wrong.
- [ ] **No smart quotes**: Have straight quotes in code been auto-corrected to curly quotes? This breaks code readability.

## Visual Consistency

These checks span the entire deck. Look at all slides as a set, not individually.

- [ ] **Illustration style**: Do all illustrations/images use the same visual style? Mixing flat vector icons with 3D renders with stock photos looks unplanned.
- [ ] **Image sizing**: Are similar-role images (headshots, product screenshots, icons) consistently sized across slides?
- [ ] **Icon treatment**: If icons are used, are they consistently styled? (e.g., all in colored circles, or all bare, or all with backgrounds — not a mix)
- [ ] **Color palette adherence**: Does every slide use colors from the same palette? A slide that introduces a random new color breaks cohesion.
- [ ] **Background consistency**: If some slides have colored backgrounds and others don't, is this intentional (e.g., title slides dark, content slides light)?
- [ ] **Border/shadow treatment**: Are borders and shadows used consistently? If one image has a shadow, all similar images should.
- [ ] **Decorative element repetition**: If a visual motif is used (e.g., rounded corners on cards, gradient bars), is it applied everywhere it should be?
- [ ] **Layout pattern consistency**: Do slides with similar content (e.g., "feature X" and "feature Y") use the same layout?

## Image Treatment

These checks catch the most-frequent empirical issues with AI-generated decks: stretched images, marooned images, broken diagrams.

- [ ] **Aspect-ratio integrity**: Compare each picture's rendered dimensions to its source. If the rendered W:H ratio differs >5% from the source image's intrinsic pixel ratio, the image is stretched or squished. Rescale to preserve the source ratio.
- [ ] **Marooned images**: A small image (<15% of slide area) sitting alone on a mostly-empty slide is a layout failure. Either enlarge the image to use the canvas, or add other content to fill the slide.
- [ ] **Disconnected diagram arrows**: Arrows/connectors with floating endpoints (not attached to any shape) usually mean the diagram broke during generation. Reattach to source/target shapes.
- [ ] **Image quality at projection size**: Even a high-res image looks bad if compressed too aggressively. Check for visible compression artifacts (blockiness, ringing) at full-screen view.
- [ ] **Image cropping**: Important content (faces, key chart elements) is not cut off by the crop bounds.

## Non-Latin Script Coverage

For decks containing non-Latin text (Cyrillic, CJK, Arabic, Devanagari, Hebrew, Greek, Thai, etc.):

- [ ] **Font supports the script**: Verify the rendered font has Unicode coverage for the script in use. Common bug: text renders as tofu (□□□) or wrong glyphs because the AI picked a Latin-only font for non-English content.
- [ ] **Mixed-script consistency**: If the deck mixes Latin + non-Latin text on the same slide, are both rendered with proper visual weight matching? (Some fonts have very different x-heights between scripts.)
- [ ] **Punctuation rendering**: CJK and RTL scripts have script-specific punctuation. Check that quotation marks, dashes, and brackets render correctly for the script.

## Simplicity & Comprehension

A slide should communicate one idea clearly. If you need 10 seconds to understand what the slide is saying, it's too complex. **This checklist assumes presenter mode** (you're showing the slide while speaking). For document-style decks (slidedocs), thresholds are looser.

- [ ] **One idea per slide**: Can you state the slide's message in one sentence? If not, it may need splitting.
- [ ] **Text density (presenter mode)**: ≤40 words per slide is the warning threshold; >60 words is critical. The presenter speaks the rest; the slide carries one idea.
- [ ] **Visual focus point**: Is there one element that draws the eye first? If everything competes for attention equally, the audience doesn't know where to look.
- [ ] **Reading flow**: Does the content flow naturally left-to-right, top-to-bottom? Or does the eye have to jump around?
- [ ] **Redundancy**: Is the slide title just restating what the bullets say? Eliminate redundancy.
- [ ] **Label clarity**: Are all charts, diagrams, and images clearly labeled? Can you understand them without the speaker explaining?
- [ ] **Jargon density**: Would the target audience understand all the terms used? Acronyms without definitions are a common problem.

## Empty / Silent-Failure Slides

Generators sometimes silently fail to fill a slide. These checks catch the result.

- [ ] **Empty slides**: Slides with very few elements (≤2) are often placeholder slides that didn't get filled. Either add content or delete the slide.
- [ ] **Black or large unfilled rectangles**: A shape with fill but no text covering >20% of slide area often means an image failed to load or a placeholder rendered as a colored box.
- [ ] **Frontmatter empty**: A title slide where the title or subtitle is blank — placeholder leaked through.
- [ ] **Charts with one data point**: A time-series chart with a single point usually means the data aggregation went wrong. Check the source.

## Structural Anti-Patterns

These are patterns that are technically "correct" but indicate poor slide construction.

- [ ] **"One box per line"**: Are there multiple stacked text boxes where a single multi-line text box should be used? This is the most common AI-generated slide problem. Tell-tale signs: slightly uneven vertical spacing between lines, and selecting one line in PowerPoint selects only that line (not the whole paragraph).
- [ ] **Accent lines under titles**: Thin decorative lines under titles are a strong signal of AI generation. Use whitespace or background color instead.
- [ ] **In-slide scaffolding leak**: Generator metadata bleeding into slide text — timing labels ("Block 1 · 10min"), step markers ("Step 0 ·"), section numbers in slide body. Strip these.
- [ ] **Tool watermarks / leftover prompt fragments**: "Here's a polished", "As an AI", "I cannot", trailing markdown `**`. These are AI-output scaffolding that slipped through.
- [ ] **Vague title verbs**: Titles starting with "Understanding X", "Exploring Y", "Navigating Z", "Leveraging", "Unlocking", "Diving into" are AI-scaffolding language. Rewrite as a concrete title that states the slide's actual point.
- [ ] **Identical layouts**: Are all content slides using the exact same layout? Vary between columns, cards, callouts, and full-bleed images.
- [ ] **Bullet point overuse**: Are most slides just "title + bullet list"? Mix in other formats: stat callouts, comparison columns, timelines, diagrams.
- [ ] **Placeholder artifacts**: Is there any leftover template text like "Click to add title", "Lorem ipsum", "XXX", "[Insert]"?
- [ ] **Double bullets**: When bullet formatting is applied, are there also Unicode bullet characters (•) in the text, creating double bullets?

## Slide-Type-Specific Checks

### Title Slides
- [ ] Title is prominently sized (44pt+)
- [ ] Subtitle is clearly subordinate (20-24pt)
- [ ] Visual weight is balanced (not all crammed into one corner)
- [ ] Background is distinct from content slides (sets the tone for the deck)

### Data/Chart Slides
- [ ] Chart has a clear title
- [ ] Axes are labeled with units
- [ ] Legend is readable and positioned clearly
- [ ] Data labels are large enough to read
- [ ] Colors in the chart are consistent with the deck palette
- [ ] Source is cited if data is external

### Comparison/Grid Slides
- [ ] All columns/cells are the same width (unless deliberately different)
- [ ] Headers are visually distinct from cell content
- [ ] Enough padding inside cells that text doesn't touch borders
- [ ] No cells are overflowing their boundaries

### Closing/CTA Slides
- [ ] Call-to-action is prominent and clear
- [ ] Contact information is complete and readable
- [ ] Doesn't introduce new content — wraps up the story
