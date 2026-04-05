# System Scan Reference

How to test each component of the CoS system. All checks should be try/catch — never crash if something is missing.

**Platform detection:** Run `uname -s 2>/dev/null` first. "Darwin" = Mac, "Linux" = Linux, otherwise assume Windows. Adapt commands accordingly.

**Tool preference:** Use `Read`, `Glob`, `Grep` tools (cross-platform) instead of shell commands like `find` or `grep` where possible. Only use `Bash` when needed for system commands (ollama, schtasks, launchctl, curl).

## L1: Knows You

| Component | How to Check | Expected |
|-----------|-------------|----------|
| Global CLAUDE.md | `Read ~/.claude/CLAUDE.md` | File exists, 100+ words |
| SOUL.md | Glob for `**/SOUL.md` in home (max depth 5), also check `~/.claude/SOUL.md` explicitly | File exists |
| user-profile.md | Glob for `**/user-profile.md` in home (max depth 5), also check `~/.claude/` | File exists |
| Project CLAUDE.md | Glob `**/CLAUDE.md` from home (max depth 4), exclude node_modules/.git | 2+ files |
| Memory | Glob `~/.claude/projects/*/memory/*.md` — count files | 5+ entries across projects |

## L2: Has Sources

**IMPORTANT:** MCPs and plugins are configured in THREE locations. Check ALL of them:

| Source | Location | How to Parse |
|--------|----------|-------------|
| Standalone MCPs | `~/.claude/.mcp.json` | Read file, parse `mcpServers` key — each entry is an MCP server |
| Marketplace plugins | `~/.claude/settings.json` | Read file, parse `enabledPlugins` array — entries like `gmail@claude-plugins-official` |
| Project MCPs | `.mcp.json` in project root | Read file, parse `mcpServers` key |

**Common plugins to check for** (from `enabledPlugins`):
- Gmail: `gmail@claude-plugins-official` or `marketing_gmail@*`
- Calendar: `google-calendar@claude-plugins-official` or `marketing_google-calendar@*`
- Telegram: `telegram@claude-plugins-official`
- AnySite: check `~/.claude/.mcp.json` for `anysite-mcp` key

| Component | How to Test | Success | Failure |
|-----------|------------|---------|---------|
| Gmail | Try `gmail_get_profile` or `gmail_list_labels` | Returns data | Auth error or not configured |
| Calendar | Try listing today's events via calendar tools | Returns events (may be empty) | Auth error |
| Telegram | Try `list_chats` limit 1 (if telegram-mcp), or `list_messages` (if plugin) | Returns data | Not configured |
| AnySite | Try `duckduckgo_search` "test" | Returns results | Not configured |
| Chrome MCP | Check `.mcp.json` for chrome-devtools entry | Configured | Not found |
| Ollama | Run `ollama list` via Bash | Shows models | Not installed or no models |

**Important:** MCP test calls should be minimal — don't read emails or messages, just verify the connection works.

## L3: Has Procedures

| Component | How to Check | Expected |
|-----------|-------------|----------|
| Skills directory | Glob `~/.claude/skills/*/SKILL.md` — list and count | Skills exist |
| /morning | Check `~/.claude/skills/morning/SKILL.md` | File exists |
| /daily-log | Check `~/.claude/skills/daily-log/SKILL.md` or directory | Exists |
| /atomize | Check `~/.claude/skills/atomize/SKILL.md` or directory | Exists |
| /council | Check `~/.claude/skills/council/SKILL.md` or directory | Exists |
| /cos-review | Check `~/.claude/skills/cos-review/SKILL.md` | Exists |
| Custom skills | Count skills NOT from the standard set | 1+ custom skill |

## L4: Takes Initiative

**Detect platform first, then run the appropriate check:**

| Component | Mac | Windows | Linux |
|-----------|-----|---------|-------|
| Scheduled tasks | `ls ~/Library/LaunchAgents/ 2>/dev/null \| grep -i "morning\|autopilot\|claude\|daily\|briefing"` | `schtasks /query /fo LIST 2>NUL \| findstr /i "morning claude daily briefing"` | `crontab -l 2>/dev/null \| grep -i "morning\|claude\|daily"` |
| Agent teams env | Read `~/.claude/settings.json` → check `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` equals `"1"` | Same | Same |
| n8n | `curl -s http://localhost:5678/api/v1/workflows 2>/dev/null` | Same | Same |
| Hooks | Read `~/.claude/settings.json` → check `hooks` key is non-empty dict | Same | Same |

**Note:** Agent teams env is stored in `settings.json` under `env` as a dict key, NOT as a shell environment variable. Do NOT use `echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` — read the settings file instead.

## L5: Delivers Results

| Component | How to Check | Expected |
|-----------|-------------|----------|
| Morning briefings | Check these paths in order: `~/morning-briefings/`, `~/reports/daily/`, then Glob for `*morning*.md` or `*briefing*.md` in home (max depth 3) | 3+ files |
| Recent briefing | Find the most recent file in the briefing directory | Within last 3 days |
| Automated output | Check for any scheduled output directories or recent LaunchAgent logs | Evidence of automated production |

## Cross-Platform Notes

- **Mac:** LaunchAgents in `~/Library/LaunchAgents/`, Ollama via `brew install ollama`
- **Windows:** Task Scheduler via `schtasks` command, Ollama via installer from ollama.com
- **Linux:** cron jobs via `crontab -l`, Ollama via curl installer
- **All platforms:** `~/.claude/settings.json` for hooks, env, and plugin configs; `~/.claude/.mcp.json` for standalone MCPs
- **Path separator:** Use `/` in all paths — Claude Code normalizes this on Windows
