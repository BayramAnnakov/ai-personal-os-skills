# Visual Inspection Checklist

Use this checklist when visually reviewing slide images. The programmatic analyzer catches coordinate-level issues, but these checks require human (or AI vision) judgment.

## Table of Contents
1. [Overlap & Collision](#overlap--collision)
2. [Spacing & Alignment](#spacing--alignment)
3. [Typography](#typography)
4. [Code Snippets](#code-snippets)
5. [Visual Consistency](#visual-consistency)
6. [Simplicity & Comprehension](#simplicity--comprehension)
7. [Structural Anti-Patterns](#structural-anti-patterns)
8. [Slide-Type-Specific Checks](#slide-type-specific-checks)

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

## Simplicity & Comprehension

A slide should communicate one idea clearly. If you need 10 seconds to understand what the slide is saying, it's too complex.

- [ ] **One idea per slide**: Can you state the slide's message in one sentence? If not, it may need splitting.
- [ ] **Text density**: Is there so much text that it becomes a "reading slide" rather than a "presenting slide"? More than 5-6 bullet points or ~80 words is usually too much.
- [ ] **Visual focus point**: Is there one element that draws the eye first? If everything competes for attention equally, the audience doesn't know where to look.
- [ ] **Reading flow**: Does the content flow naturally left-to-right, top-to-bottom? Or does the eye have to jump around?
- [ ] **Redundancy**: Is the slide title just restating what the bullets say? Eliminate redundancy.
- [ ] **Label clarity**: Are all charts, diagrams, and images clearly labeled? Can you understand them without the speaker explaining?
- [ ] **Jargon density**: Would the target audience understand all the terms used? Acronyms without definitions are a common problem.

## Structural Anti-Patterns

These are patterns that are technically "correct" but indicate poor slide construction.

- [ ] **"One box per line"**: Are there multiple stacked text boxes where a single multi-line text box should be used? This is the most common AI-generated slide problem. Tell-tale signs: slightly uneven vertical spacing between lines, and selecting one line in PowerPoint selects only that line (not the whole paragraph).
- [ ] **Accent lines under titles**: Thin decorative lines under titles are a strong signal of AI generation. Use whitespace or background color instead.
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
