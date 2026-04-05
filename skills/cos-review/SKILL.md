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
- Search for `SOUL.md`:
  1. Check `~/.claude/SOUL.md` first (the standard global location)
  2. If not there, Glob `**/SOUL.md` in home (max depth 5, exclude node_modules/.git/Library)
  3. If found elsewhere but NOT in `~/.claude/`: report "SOUL.md exists at [path] but is not globally accessible. Recommend: copy to `~/.claude/SOUL.md`"
  4. Check if `~/.claude/CLAUDE.md` references SOUL.md — if not, flag: "SOUL.md won't be auto-loaded unless CLAUDE.md references it"
- Search for `user-profile.md` — same 4-step approach as SOUL.md
- Count project-level CLAUDE.md files — use Glob `**/CLAUDE.md` from home (max depth 4, exclude node_modules/.git)
- Check memory — use Glob `~/.claude/projects/*/memory/*.md` and count entries

**L2: Has Sources**
- MCPs and plugins are configured in THREE locations — check ALL of them:
  1. `~/.claude/.mcp.json` — read and parse the `mcpServers` key (standalone MCP servers)
  2. `~/.claude/settings.json` — read and parse the `enabledPlugins` object (key:boolean dict, e.g., `"gmail@claude-plugins-official": true`)
  3. Project-level `.mcp.json` files — Glob for them in the current project
- For each source found, try a lightweight test call (skip if tool not available):
  - Gmail: try `gmail_get_profile` or `gmail_list_labels`
  - Telegram: try `list_chats` (limit 1)
  - AnySite: try `duckduckgo_search` with "test"
  - Calendar: try listing today's events
- Ollama: run `ollama list` (works on Mac, Windows, Linux). If command not found, mark as not installed.
  - If installed, check for both local models (e.g., qwen3.5) and cloud models (e.g., kimi-k2.5:cloud, qwen3.5:cloud)
  - Note: cloud models via Ollama are fast and cheap but data goes to a third-party provider. Local models are fully private but require a strong GPU — slow on laptops.
  - If not installed and user has privacy or cost concerns, suggest: `brew install ollama` then `ollama launch claude --model kimi-k2.5:cloud` for cost savings, or local model for full privacy
- Report which sources are installed, which respond, which have expired tokens

**L3: Has Procedures**
- List skills: Glob `~/.claude/skills/*/SKILL.md` — count and list names
- Check for key skills: morning, daily-log, atomize, council, cos-review
- If /morning skill is missing, check for EQUIVALENT morning systems:
  - Look for LaunchAgents/schtasks/cron with "morning" or "autopilot" (from L4 check)
  - Search common directories for morning scripts: `~/GH/*/morning*`, `~/scripts/morning*`
  - If found: "Your morning system exists at [path] as a [type]. This works! Optionally create a /morning SKILL.md wrapper for consistency."
- Count total available slash commands (skills + built-in)

**L4: Takes Initiative**
- Detect platform, then check for scheduled tasks:
  - **Mac:** check `~/Library/LaunchAgents/` for plist files matching morning/autopilot/claude/daily/briefing
  - **Windows:** run `schtasks /query /fo LIST 2>NUL` and search for morning/claude/daily/briefing entries
  - **Linux:** run `crontab -l 2>/dev/null` and search for morning/claude/daily entries
- Agent teams: read `~/.claude/settings.json`, check if `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` equals "1" (it's stored in the `env` dict, NOT as a shell variable)
- Hooks: read `~/.claude/settings.json`, check if `hooks` key has any entries (not just exists — check it's non-empty)
  - If hooks exist, enumerate which event types are configured (e.g., SessionStart, PreCompact, PostToolUse, Stop)
  - Check that hook commands reference scripts that actually exist (if command points to a `.sh` file, verify it's there)
  - If empty, proactively suggest two hooks:
    1. **SessionStart** — loads today's briefing into every session:
       ```json
       "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "cat ~/morning-briefings/$(date +%Y-%m-%d).md 2>/dev/null || echo 'No briefing today'", "timeout": 10}]}]
       ```
    2. **PreCompact** — saves session transcripts before context compaction:
       ```json
       "PreCompact": [{"matcher": "", "hooks": [{"type": "command", "command": "your-transcript-backup-script.sh", "async": true, "timeout": 10}]}]
       ```
  - If only SessionStart exists, suggest PreCompact as the next hook
  - Note: for complex hook logic, recommend external script files (e.g., `~/.claude/hooks/session-start.sh`) instead of inline commands
- Heartbeat (periodic sweep between sessions):
  - Check for a `/heartbeat` skill: Glob `~/.claude/skills/heartbeat/SKILL.md`
  - Check for a periodic LaunchAgent/cron matching "heartbeat" in addition to "morning"
  - Check `~/heartbeat.log` for recent entries (if file exists, when was it last updated?)
  - If no heartbeat exists, explain the concept and offer to build it:
    "Your CoS only wakes when you start a session or when /morning runs at 7 AM. Between those moments, it's dormant — emails arrive, calendar changes, deadlines approach, and your CoS has no idea. A heartbeat is a silent periodic sweep (every 2-4 hours) that checks for changes and only pings you via Telegram if something needs attention. Think of it as the difference between checking your phone once a day vs having a smart notification system."
  - If they want it, use the Guided Heartbeat Builder (see below)
- Two-way access: check if the user can reach their CoS from their phone
  - Check for Telegram channel plugin (`telegram@claude-plugins-official` in enabledPlugins)
  - Check for Claude Desktop Dispatch (ask the user)
  - If neither: suggest Telegram channels (`/plugin install telegram@claude-plugins-official`, then `claude --channels`) or Claude Desktop Dispatch as options

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
2. Check understanding: "Do you know what [concept] is, or want me to explain first?" If the user is unsure, give a brief plain-language explanation before suggesting the fix. Examples:
   - Hooks → "Hooks are automatic actions that fire at specific moments — like your CoS reading today's briefing before every conversation, without you asking."
   - Agent teams → "Agent teams are multiple AI agents that talk to EACH OTHER and coordinate, unlike sub-agents which just report back to you."
   - SOUL.md → "SOUL.md defines your AI's voice — how it writes, what tone it uses, what words it avoids. Without it, every output sounds generic."
   - Ollama → "Ollama lets you run AI models on your own machine. Your data never leaves your laptop — useful for sensitive work."
3. Ask: "Want me to set this up now? (y/n)"
4. If yes, use the relevant guide from `references/setup-guides/`
5. Test it works
6. Move to next priority

Read `references/layer-actions.md` for specific actions per layer gap.

#### Guided /morning Builder

If /morning is missing (one of the top priorities — it flips 3-5 questions across L3, L4, and L5), offer to build it through an interview:

> "Your biggest gap is /morning. Want me to help you build it? I'll interview you."

If yes, ask these questions ONE AT A TIME, waiting for each answer:
1. What data sources do you have? (Gmail, Calendar, AnySite, Vault, Telegram — list what works)
2. Single agent, sub-agents, or agent team with Researcher/Analyst/Learner roles?
3. Do you handle sensitive data that should stay local via Ollama?
4. How should the briefing be delivered? (Telegram, terminal, saved to file)
5. How should your system LEARN from yesterday's briefing?
6. When this breaks at 7 AM, what do you check first?

After all answers, build the SKILL.md at `~/.claude/skills/morning/SKILL.md`.
Use SOUL.md for voice if it exists. Save output to `~/morning-briefings/YYYY-MM-DD.md`.
Include a Learner role or step that reads yesterday's briefing and feeds patterns forward.

Then test: run `/morning` and verify it produces output. Debug if needed.

#### Guided Heartbeat Builder

If the user has /morning working but no periodic awareness between sessions, offer to build a heartbeat:

> "Your /morning runs at 7 AM. But between then and your next session, your CoS is dormant. Want me to build a /heartbeat that checks for changes every few hours and only pings you when something needs attention?"

If yes, ask these questions ONE AT A TIME:
1. What should it check? (unread emails, calendar next 2 hours, approaching deadlines, task file changes)
2. How often? (every 2 hours, every 4 hours, 3x/day at 10am/1pm/5pm)
3. When should it NOTIFY you vs stay silent? (only urgent items? any new email from key people? calendar conflicts?)
4. How should it notify? (Telegram message, save to ~/heartbeat.log, both)
5. Should it auto-resolve safe items? (e.g., acknowledge meeting invites, file routine emails) Or just report?

After answers, build two things:

**1. The /heartbeat skill** at `~/.claude/skills/heartbeat/SKILL.md`:
```
Steps:
1. SCAN — Check each data source (email count + urgent senders, calendar next 2h, task deadlines)
2. TRIAGE — For each item: urgent (notify now), routine (auto-resolve if allowed), ignorable (skip)
3. ACT — Auto-resolve safe items if user opted in (acknowledge, file, update task list)
4. NOTIFY — If anything needs human attention → send Telegram message with ONE sentence per item
5. LOG — Append timestamp + summary to ~/heartbeat.log
6. SILENT — If nothing changed: log "HEARTBEAT_OK", send no notification
```

**2. The scheduled trigger:**
- Mac: create a LaunchAgent plist at `~/Library/LaunchAgents/com.user.heartbeat.plist` that runs `claude --print "Run /heartbeat"` at the chosen intervals
- Windows: `schtasks /create /tn "Heartbeat" /tr "claude --print \"Run /heartbeat\"" /sc daily /st 10:00` (repeat for each time slot)
- Linux: add crontab entries for each time slot

Test: run `/heartbeat` manually first. Verify it stays silent when nothing is urgent. Then enable the schedule.

**Growth path to explain to the user:**
```
Level 1: SessionStart hook    — CoS loads context when YOU start talking (you have this)
Level 2: /morning at 7 AM     — CoS prepares your day once (you have this)
Level 3: /heartbeat every 2-4h — CoS checks for changes, pings you only when needed (building now)
Level 4: Always-on Telegram    — CoS listens 24/7, you can ask anytime from your phone
```

Only do 2-3 priorities per session. "Good enough for today. Do the rest this week."

### Step 5: Schedule First Review

After setup is complete:

1. Save baseline to `~/cos-reviews/[DATE]-baseline.md` using the YAML format below
2. Tell the user: "Your first review is in 2 weeks. Run `/cos-review` then."
3. If they have Telegram connected, offer to set a reminder: "Want me to send you a Telegram reminder in 2 weeks?"
4. If yes, send a Telegram message with a reminder, or suggest they set a phone reminder/calendar event

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
- Check hooks in `~/.claude/settings.json`: which event types are configured? If hook commands reference script files, verify they exist.
- Check heartbeat: does `/heartbeat` skill exist? Is it scheduled? Check `~/heartbeat.log` for recent entries.

Report with status icons:
```
SYSTEM HEALTH
✅ Gmail MCP          responding
⚠️ Calendar MCP       token expired
✅ /morning           last run: today 07:00
✅ Memory             24 entries (↑3 since last review)
⚠️ Vault              last /atomize: 8 days ago
✅ Hooks              SessionStart + PreCompact configured
✅ Heartbeat          last sweep: 2h ago, HEARTBEAT_OK
```

### Step 4: Conversation Pattern Check

Scan MEMORY.md entries created since last review date (Glob `~/.claude/projects/*/memory/*.md`, check file modification dates). Do NOT try to read conversation transcripts (.jsonl) — they are not accessible.

Look for patterns in memory entries:
- New skills mentioned?
- New MCPs referenced?
- Repeated tasks or complaints?

"Since your last review, your memory mentions [task] multiple times. That's a skill candidate."

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
✅ Ollama             installed (qwen3.5 local + kimi-k2.5:cloud)
✅ /morning           last run: today 07:00
✅ Memory             24 entries
⚠️ Vault              last /atomize: 8 days ago
✅ Hooks              SessionStart configured
✅ Heartbeat          last sweep: 2h ago (HEARTBEAT_OK)
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
