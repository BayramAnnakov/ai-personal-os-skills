---
description: "Chief of Staff Review — diagnose, build, and grow your personal AI operating system. Three modes: setup (first run), review (bi-weekly check-in), status (quick health check)."
allowed-tools:
  - AskUserQuestion
  - Write
  - Read
  - Bash
  - Glob
  - Grep
  - Agent
---

# /cos-review — Chief of Staff Review

Diagnose, build, and grow your personal AI operating system.

Your AI is your Chief of Staff. This skill is the performance review.

## Detect Mode

Check what the user typed:
- `/cos-review setup` → run **Setup Mode**
- `/cos-review status` → run **Status Mode**
- `/cos-review` (no arguments) → run **Review Mode**

---

## MODE 1: Setup (first run)

Run this the first time, or when rebuilding the system from scratch. It scans everything, analyzes usage, and guides the user through fixing their biggest gaps.

### Step 1: System Scan

Scan automatically — don't ask, CHECK. Report what exists and what's missing.

**Important:** Use `Read`, `Glob`, and `Grep` tools (cross-platform) instead of shell commands like `find` or `grep`. Only fall back to `Bash` when no dedicated tool works. Detect the OS first (`uname` on Mac/Linux, or check for Windows paths) and adapt commands accordingly.

**L1: Knows You**
- Read `~/.claude/CLAUDE.md` — exists? word count?
- Search for `SOUL.md` — use Glob to check: `~/.claude/SOUL.md`, `~/SOUL.md`, project root, `~/.claude/skills/*/SOUL.md`, and `Glob **/SOUL.md` in home (max depth 5, exclude node_modules/.git/Library)
- Search for `user-profile.md` — same approach as SOUL.md
- Count project-level CLAUDE.md files — use Glob `**/CLAUDE.md` from home (max depth 4, exclude node_modules/.git)
- Check memory — use Glob `~/.claude/projects/*/memory/*.md` and count entries

**L2: Has Sources**
- MCPs and plugins are configured in THREE locations — check ALL of them:
  1. `~/.claude/.mcp.json` — read and parse the `mcpServers` key (standalone MCP servers)
  2. `~/.claude/settings.json` — read and parse the `enabledPlugins` array (marketplace plugins like Gmail, Telegram, Figma)
  3. Project-level `.mcp.json` files — Glob for them in the current project
- For each source found, try a lightweight test call (skip if tool not available):
  - Gmail: try `gmail_get_profile` or `gmail_list_labels`
  - Telegram: try `list_chats` (limit 1)
  - AnySite: try `duckduckgo_search` with "test"
  - Calendar: try listing today's events
- Ollama: run `ollama list` (works on Mac, Windows, Linux). If command not found, mark as not installed
- Report which sources are installed, which respond, which have expired tokens

**L3: Has Procedures**
- List skills: Glob `~/.claude/skills/*/SKILL.md` — count and list names
- Check for key skills: morning, daily-log, atomize, council, cos-review
- Count total available slash commands (skills + built-in)

**L4: Takes Initiative**
- Detect platform, then check for scheduled tasks:
  - **Mac:** check `~/Library/LaunchAgents/` for plist files matching morning/autopilot/claude/daily/briefing
  - **Windows:** run `schtasks /query /fo LIST 2>NUL` and search for morning/claude/daily/briefing entries
  - **Linux:** run `crontab -l 2>/dev/null` and search for morning/claude/daily entries
- Agent teams: read `~/.claude/settings.json`, check if `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` equals "1" (it's stored in the `env` dict, NOT as a shell variable)
- Hooks: read `~/.claude/settings.json`, check if `hooks` key has any entries (not just exists — check it's non-empty)
- n8n: try `curl -s http://localhost:5678/api/v1/workflows` — if JSON returned, n8n is running

**L5: Delivers Results**
- Check MULTIPLE paths for morning briefings (users store them differently):
  1. `~/morning-briefings/` — the recommended path from the course
  2. `~/reports/daily/` — common alternative
  3. Search for recent `.md` files with "morning" or "briefing" in the name
- If found: count files, find most recent, check if within last 3 days
- If not found: note it — this is the most common L5 gap

### Step 2: Conversation History Analysis

Read the user's past Claude Code context to understand ACTUAL usage patterns.

- Read `~/.claude/projects/` — list subdirectories (these are project contexts)
- For the 3-5 most recently modified projects, read their MEMORY.md
- Look at `~/.claude/settings.json` for recently used configuration
- Search recent memory entries for patterns:
  - What skills/commands are mentioned most?
  - What MCPs appear in memory entries?
  - What tasks or workflows are described?
  - What frustrations or errors are noted?

Present findings:
```
USAGE PATTERNS (from your recent sessions):
- You use [skill X] frequently — strongest habit
- You use [MCP Y] in [N] different projects — active source
- You manually [task Z] multiple times — SKILL CANDIDATE
- [MCP A] is installed but never appears in sessions — installed ≠ used
- You haven't used [skill B] recently — dormant
```

### Step 3: System Map

Combine scan + conversation analysis into a visual report:

```
YOUR CHIEF OF STAFF — CURRENT STATE
Score: X/25 — [RANK]

L1: KNOWS YOU          ████░  4/5
L2: HAS SOURCES        ███░░  3/5
L3: HAS PROCEDURES     ██░░░  2/5
L4: TAKES INITIATIVE   ░░░░░  0/5
L5: DELIVERS RESULTS   ░░░░░  0/5

INSTALLED BUT UNUSED: [from conversation analysis]
MANUAL REPETITIONS: [potential skill candidates]
STRONGEST HABIT: [most-used skill/pattern]
```

Read `references/diagnostic-questions.md` for the full 25-question scoring criteria.

### Step 4: Setup Priority

Based on weakest layer, suggest a prioritized list. Fix BOTTOM-UP (L1 before L4).

For each priority:
1. Explain WHY it matters (one sentence)
2. Ask: "Want me to set this up now? (y/n)"
3. If yes, use the relevant guide from `references/setup-guides/`
4. Test it works
5. Move to next priority

Read `references/layer-actions.md` for specific actions per layer gap.

Only do 2-3 priorities per session. "Good enough for today. Do the rest this week."

### Step 5: Schedule First Review

After setup is complete:

1. Save baseline to `~/cos-reviews/[DATE]-baseline.md` using the YAML format below
2. Tell the user: "Your first review is in 2 weeks. Run `/cos-review` then."
3. If they have Telegram connected, offer to set a reminder: "Want me to schedule a Telegram reminder in 2 weeks?"
4. If yes, use the `/schedule` skill or create a calendar event

---

## MODE 2: Review (default — bi-weekly)

The regular performance review. Run every 2 weeks.

### Step 1: Load Previous Review

Read the most recent file from `~/cos-reviews/`. If none exists, say: "No previous review found. Run `/cos-review setup` first, or I'll do a fresh assessment now."

### Step 2: Smart Diagnostic

Read `references/diagnostic-questions.md` for the 25 questions.

**Don't re-ask everything.** Be smart:
- Questions that were YES last time: spot-check 2-3 to verify (things can break)
- Questions that were NO last time: ask if anything changed
- This should take 2 minutes, not 10

Calculate new score + rank. Compare to previous.

### Step 3: System Health Check

Actually TEST the system — don't ask, VERIFY:
- Discover MCPs from all 3 sources (`.mcp.json`, `enabledPlugins`, project `.mcp.json`) — try a lightweight test call for each
- Check if /morning skill exists (`~/.claude/skills/morning/SKILL.md`) and when it last produced output (check `~/morning-briefings/` and `~/reports/daily/`)
- Check memory entry count (Glob `~/.claude/projects/*/memory/*.md`) — growing or stagnant?
- Check Ollama: run `ollama list`
- Check scheduled tasks (platform-aware: LaunchAgents on Mac, schtasks on Windows, crontab on Linux)

Report with status icons:
```
SYSTEM HEALTH
✅ Gmail MCP          responding
⚠️ Calendar MCP       token expired
✅ /morning           last run: today 07:00
✅ Memory             24 entries (↑3 since last review)
⚠️ Vault              last /atomize: 8 days ago
```

### Step 4: Conversation Pattern Check

Scan conversation history since last review date:
- New skills used?
- New MCPs called?
- Manual repetitions detected?

"Since your last review, you manually [task] X times. That's a skill candidate."

### Step 5: Growth Question

Ask ONE question:

> "What task did you do manually 3+ times in the past 2 weeks?"

- If they name one → "That's your next skill. Want me to help you write it now?"
- If blank → "Watch for repetitions this week. Law #3: manual, twice, playbook."

### Step 6: One Action

Based on weakest layer, suggest ONE specific action. Read `references/layer-actions.md`.

Not a list. ONE thing. The highest-leverage investment.

"Your ONE investment: [specific action]. That alone flips [N] of your Layer [X] gaps."

Offer to BUILD it: "Want me to do this now? (y/n)"

### Step 7: Log

Save review to `~/cos-reviews/YYYY-MM-DD.md`:

```yaml
---
date: YYYY-MM-DD
score: X
rank: [Intern|Junior Assistant|Trained CoS|Senior CoS|Pravaya Ruka]
previous_score: X
delta: +/-X
layers:
  L1: X
  L2: X
  L3: X
  L4: X
  L5: X
weakest: LX
health:
  gmail: ok|expired|not_configured
  calendar: ok|expired|not_configured
  telegram: ok|not_configured
  anysite: ok|not_configured
  ollama: ok|not_installed
  morning_skill: exists|missing
  morning_last_run: YYYY-MM-DD|never
  memory_entries: X
  vault_last_atomize: YYYY-MM-DD|never
growth_candidate: "description of repeated task"
action: "the ONE action suggested"
---

## Review Notes
[Summary of the review conversation]

## Progress
[Score trend if 3+ reviews exist]
```

Show the trend:
```
Apr 5:  14/25 JUNIOR    ████████░░░░░
Apr 19: 17/25 TRAINED   ██████████░░░
May 3:  19/25 TRAINED   ███████████░░
```

---

## MODE 3: Status (quick health check)

No questions. No diagnostic. Just test everything and report. Takes 30 seconds.

Run all health checks from Step 3 of Review mode. Discover MCPs/plugins from all 3 config sources (`.mcp.json`, `enabledPlugins`, project `.mcp.json`). Test each. Report status + issues + fix commands.

Detect platform for scheduled task checks (Mac: LaunchAgents, Windows: schtasks, Linux: crontab).

```
YOUR CoS HEALTH — [DATE]
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Gmail plugin       responding
⚠️ Calendar plugin    token expired 2d ago
✅ AnySite MCP        responding
✅ Telegram MCP       responding
✅ Ollama             qwen3.5:7b loaded
✅ /morning           last run: today 07:00
✅ Memory             24 entries
⚠️ Vault              last /atomize: 8 days ago
✅ Hooks              SessionStart configured
✅ Scheduled task     LaunchAgent active (Mac)

ISSUES: 1 critical, 1 warning
FIX: Refresh Calendar token — run: /plugin install google-calendar@claude-plugins-official
```

---

## The 7 Laws (Context)

These principles guide the review. Read `references/7-laws.md` for full context.

1. You fall to the level of your systems.
2. Every complex system that works evolved from a simple system that worked.
3. Do it manually. Do it again. Third time — write a playbook.
4. Information flows up AND down. Without the downward arrows, it's a dead pipeline.
5. Alignment over volume.
6. Not "I will." My SYSTEM will.
7. Your CoS is always briefed, knows every playbook, dispatches specialists, and never forgets.

## Tone

- Direct, not preachy
- Celebrate progress ("Score went from 14 to 17 — that's real growth")
- Honest about gaps ("Layer 4 is still at zero. That's where the leverage is.")
- Action-oriented ("Want me to build this now?")
- Never overwhelming (ONE action, not ten)
