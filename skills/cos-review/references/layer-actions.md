# Prescriptive Actions Per Layer Gap

When a layer has gaps, suggest the highest-leverage action from this list. ONE action only.

## L1: KNOWS YOU — Identity & Memory

| Gap | Action | Impact |
|-----|--------|--------|
| No global CLAUDE.md | "Create `~/.claude/CLAUDE.md` with your preferences, defaults, writing style, timezone, and key projects. Start with 200 words." | Foundation — everything downstream reads this |
| No SOUL.md | "Create SOUL.md defining your AI's voice: tone, formality, humor level, vocabulary. 'Write like me, not like a press release.'" | Every output matches your voice |
| No user-profile.md | "Write user-profile.md: your role, goals, responsibilities, working hours, communication preferences." | System understands WHO you are |
| No project CLAUDE.md | "Write a CLAUDE.md for the project folder you work in most. Current goal, key people, decisions made, what's blocked." | Context loaded automatically when you `cd` |
| No memory | "Enable auto-memory in Claude Code. Every significant session leaves a trace." | System learns over time |

**Build offer:** "Want me to create your CLAUDE.md now? I'll ask you 5 questions and write it."

## L2: HAS SOURCES — Perception

| Gap | Action | Impact |
|-----|--------|--------|
| No Gmail | "Install Gmail plugin: `/plugin install gmail@claude-plugins-official` — follow OAuth prompts" | CoS can read your email |
| No Calendar | "Install Calendar plugin: `/plugin install google-calendar@claude-plugins-official`" | CoS knows your schedule |
| No AnySite | "Install AnySite MCP for LinkedIn/Twitter/Reddit research. See course gist for setup." | CoS can research the web |
| No Telegram | "Install Telegram plugin: `/plugin install telegram@claude-plugins-official`" | CoS reaches you on your phone |
| No Ollama | "Mac: `brew install ollama && ollama pull qwen3.5` / Windows: download from ollama.com, then `ollama pull qwen3.5`. IMPORTANT: set `OLLAMA_CONTEXT_LENGTH=64000 ollama serve` before using with Claude Code." | Sensitive data stays local |
| Token expired | "Re-install the plugin: `/plugin install [name]@claude-plugins-official` — refreshes OAuth" | Restores broken connection |

**Build offer:** "Want me to install [MCP] now? I'll walk you through the auth."

## L3: HAS PROCEDURES — Skills

| Gap | Action | Impact |
|-----|--------|--------|
| No /morning | "Want me to help you build /morning? I'll interview you about your sources, intelligence level, privacy needs, and what makes your system learn — then build the SKILL.md." | The capstone daily habit — flips 3-5 questions across L3/L4/L5 |
| No custom skills | "Pick the task you do most often. Describe it to me. I'll write the SKILL.md." | Your first playbook |
| No /daily-log | "Create a /daily-log skill: ask me 3 questions (energy, mood, focus), log to a daily file. I'll write the SKILL.md now." | Daily energy/mood/focus tracking |
| No /atomize | "Create a /atomize skill: take any input (article, conversation, idea), extract key insights, save as an atomic note in your vault." | Knowledge extraction habit |
| No /council | "Create a /council skill: simulate 3-5 expert perspectives on a question, then synthesize. I'll write the SKILL.md now." | Better strategic decisions |
| Few skills (<5) | "Law #3: what did you do manually 3+ times? That's your next skill." | Organic growth |

**Build offer:** "Want me to write that skill now? Tell me the task and I'll create the SKILL.md."

## L4: TAKES INITIATIVE — Autonomy

| Gap | Action | Impact |
|-----|--------|--------|
| No scheduled tasks | "Mac: create a LaunchAgent plist (template in setup-guides/). Windows: `schtasks /create /tn MorningBriefing /tr \"claude --print 'Run /morning'\" /sc daily /st 07:00`. Linux: add to crontab." | System works while you sleep |
| No agent teams | "Enable agent teams: `claude settings set env CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS 1` then restart Claude Code" | Staff that collaborates |
| No hooks | "Add two hooks to settings.json: (1) SessionStart to load today's briefing — `\"SessionStart\": [{\"matcher\": \"\", \"hooks\": [{\"type\": \"command\", \"command\": \"cat ~/morning-briefings/$(date +%Y-%m-%d).md 2>/dev/null\", \"timeout\": 10}]}]` (2) PreCompact to save transcripts before compaction (set `async: true`). For complex logic, create script files in `~/.claude/hooks/` instead of inline commands." | CoS reads briefing before every session + transcripts preserved |
| No two-way access | "Set up Telegram channels (`/plugin install telegram@claude-plugins-official`, then `claude --channels`) or Claude Desktop Dispatch so you can reach your CoS from your phone" | Two-way communication, not just push notifications |
| Nothing runs before you | "The single biggest upgrade: schedule /morning for 7 AM. Everything else follows." | The system serves YOU, not the other way around |

**Build offer:** "Want me to create the LaunchAgent/scheduled task now?"

## L5: DELIVERS RESULTS — Output

| Gap | Action | Impact |
|-----|--------|--------|
| No morning briefings | "Run /morning manually 3 times this week. Fix what breaks. Then automate." | Prove it works before automating |
| No end-to-end tasks | "Pick ONE workflow: trigger → process → deliver. Build it this week." | Your first fully automated output |
| Not daily use | "Commit: 'My SYSTEM will run /morning at 7 AM for 30 days.' Law #6." | Habit formation |
| No real outcomes | "Point to one thing that exists BECAUSE of your CoS. If you can't, the system isn't delivering yet." | Honest assessment |

**Build offer:** "Want me to help you run /morning right now and debug any issues?"

## Priority Logic

Always fix BOTTOM-UP: L1 → L2 → L3 → L4 → L5.

A CoS with great procedures but no sources is a skilled assistant locked in a windowless room.
A CoS with initiative but no identity will take action in the wrong direction.

If multiple layers have gaps, fix the LOWEST numbered layer first.
Exception: if a token expired (L2), fix that immediately regardless of other gaps — it's a quick fix with immediate impact.
