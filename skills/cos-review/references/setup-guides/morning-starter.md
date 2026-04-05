# Starter /morning Skill

Create this at `~/.claude/skills/morning/SKILL.md`. It adapts to whatever MCPs you have available.

```markdown
---
description: "Morning briefing — gather context, analyze priorities, deliver a narrative report."
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
---

# /morning — Your Morning Briefing

## Before Starting

Check which data sources are available (try each, skip if unavailable):
- Gmail MCP → read unread emails
- Google Calendar → today's meetings
- Obsidian vault (~/obsidian/ or similar) → notes on meeting participants
- AnySite MCP → research new contacts

## Steps

### 1. Gather Context
For each available source, collect today's relevant data:

**Email** (if Gmail available):
- Search for unread emails from the last 24 hours
- For each: sender, subject, urgency (high/medium/low)
- Flag anything that needs a reply before 10 AM

**Calendar** (if Calendar available):
- List today's meetings with times and participants
- For recurring meetings: note the usual agenda

**Vault** (if Obsidian vault exists):
- For each meeting participant, search the vault for existing notes
- Surface recent interactions, decisions, and context
- Only do external research for people NOT in the vault

### 2. Analyze Priorities
- Cross-reference: which emails relate to today's meetings?
- Identify the ONE thing that needs attention before 10 AM
- Flag contradictions across sources (email says X, calendar says Y)
- Rank today's priorities based on goals from user-profile.md

### 3. Write the Briefing
Read SOUL.md for voice and tone. Write a narrative briefing:

**Format:**
1. **Priority alert** (if anything urgent)
2. **Today's meetings** with prep notes for each
3. **Email triage** — what needs replies, what can wait
4. **One priority** for today
5. **One thing to stop doing** today

Keep under 500 words. Be direct, not verbose.

### 4. Save and Deliver
- Save to `~/morning-briefings/YYYY-MM-DD.md`
- If Telegram is available, send the briefing there too

### 5. Archive (if vault exists)
- Save key insights about meeting participants back to the vault
- Use /atomize format if available

## Graceful Degradation
If ANY source fails, skip it and note what failed:
"⚠️ Gmail MCP unavailable — email triage skipped. Fix: refresh token."
Always produce SOMETHING, even if partial.

## Quality Check
- Briefing is under 500 words
- Written in SOUL.md voice (not generic AI)
- ONE clear priority identified
- Meetings have prep context (not just times)
```

## After Creating

1. Test it: run `/morning` in Claude Code
2. If it works, set up a daily trigger (see `launchagent-template.md`)
3. Run it manually for 3 days before automating
