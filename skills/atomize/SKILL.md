---
description: "Atomize any content into your Zettelkasten vault. Accepts text, file paths, or URLs. Extracts atomic ideas, finds connections to existing notes, and saves to your vault."
allowed-tools:
  - AskUserQuestion
  - Write
  - Read
  - Bash
  - Glob
  - Grep
---

# /atomize — Knowledge Atomizer

Turn any content into connected atomic notes in your Zettelkasten vault.

## Input Flow

Ask ONE question using `AskUserQuestion`:

### Question 1: What to atomize?
- **Question:** "What do you want to atomize?"
- **Options:** `["Paste text here", "Give a file path", "Describe an idea", "Atomize my recent daily logs"]`
- Accept whatever they provide.

Based on their choice:
- **Pasted text**: Use it directly
- **File path**: Read the file
- **Describe an idea**: Use their description
- **Daily logs**: Read all `notes/daily-log-*.md` files, extract Highlight and Blocker sections (ignore Vitals metrics — energy/focus/mood are data, not knowledge)

## Extraction Rules

From the input, extract atomic ideas following these rules:

1. **One concept per note** — if an idea has two parts, make two notes
2. **2-5 sentences** — express the idea concisely
3. **Own words** — reformulate, don't copy-paste. The goal is YOUR understanding, not a quote
4. **Tags** — add 2-4 relevant tags based on content
5. **Source attribution** — note where the idea came from

Typically extract 2-5 atomic notes from a paragraph or article excerpt. For daily logs, focus on:
- Ideas hidden in Highlight entries (things learned, realized, discovered)
- Patterns in Blocker entries (recurring problems = knowledge)
- Any insights that weren't fully developed

## Connection Discovery

For EACH extracted idea:

1. Use `Glob` to find all existing `atomic/*.md` files
2. Use `Grep` to search existing notes for related keywords and concepts
3. If related notes exist, add `[[wikilinks]]` with a brief explanation of the connection
4. If no related notes exist, that's fine — connections grow over time

## File Creation

1. Get today's date via `date +%Y-%m-%d` (Bash)
2. Create the `atomic/` directory if it doesn't exist
3. For each atomic idea, create a file: `atomic/YYYY-MM-DD_NNN.md` where NNN is a 3-digit sequence number (001, 002, 003...)
4. Check existing files to avoid number collisions

### File Template

```markdown
---
id: YYYY-MM-DD_NNN
title: "[Descriptive title]"
date: YYYY-MM-DD
source: "[Where the idea came from]"
tags: [tag1, tag2]
---

# [Title]

[2-5 sentences expressing the idea in your own words]

## Connections

- [[related-note-id]] — [Why this connects]

## Source Context

[Brief: who said it, where you read it, what prompted the thought]

---
*Created via /atomize*
```

## After Saving

Print a summary:

> Atomized! X notes created, Y connections found to existing notes.
>
> New notes:
> - atomic/YYYY-MM-DD_001.md — "[title]"
> - atomic/YYYY-MM-DD_002.md — "[title]" → connected to [[existing-note]]
> - atomic/YYYY-MM-DD_003.md — "[title]"

If this is their first time using /atomize and they have fewer than 3 atomic notes total, add:

> Tip: The more notes you add, the more connections appear. Try /atomize daily with one article, conversation, or idea.

## Edge Cases

- If `atomic/` has 0 existing notes: skip connection search, just create the notes and mention "No existing notes to connect to yet — your graph starts here!"
- If input is very short (1 sentence): create just 1 atomic note, that's fine
- If input is very long (full article): extract the 5-7 most important ideas, not everything
- If a daily log has "Nothing major" as blocker: skip it, no knowledge there

Do NOT turn this into a long conversation. Extract, create, summarize. The whole interaction should take under 3 minutes after the user provides input.
