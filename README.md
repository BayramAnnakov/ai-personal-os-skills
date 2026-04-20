# AI Personal OS Skills

Reusable [Claude Code](https://claude.ai/claude-code) skills for building your AI Personal OS. Installable as a Claude Code plugin marketplace.

## Available Skills

### `/onboarding` - Personal AI Onboarding

Set up your AI workspace in 10-15 minutes through a conversational interview.

**What it does:**
- Interviews you about your role, tools, workflows, and goals
- Creates `CLAUDE.md` - your AI's memory of who you are
- Creates `user-profile.md` - structured profile for AI context
- Creates `course-goals.md` - what you want to achieve
- Creates `SOUL.md` - your AI's personality and communication style

### `/daily-log` - Daily Energy-Mood-Focus Journal

5-minute daily check-in that builds your personal data foundation.

**What it does:**
- Quick structured entry: energy (1-5), mood (1-5), focus (1-5)
- Activity log with timestamps
- Auto-enrichment: pattern analysis every 3rd entry
- Saves to `notes/daily-log-YYYY-MM-DD.md`

**Example:**
```
/daily-log
```

### `/atomize` - Zettelkasten Note Extractor

Extract atomic ideas from any text into structured Zettelkasten-style notes.

**What it does:**
- Breaks content into individual atomic notes (one idea per note)
- Rewrites in your own voice (using SOUL.md if available)
- Adds tags and `[[wikilink]]` connections to existing notes
- Saves to `notes/` folder with descriptive filenames

**Example:**
```
/atomize [paste an article, book notes, meeting transcript, or any text]
```

### `/cos-review` - Chief of Staff System Review

Diagnose, build, and grow your personal AI operating system. Three modes for different needs.

**What it does:**
- **`/cos-review setup`** — First-time system scan: checks all 5 layers (identity, sources, procedures, initiative, results), analyzes your conversation history for usage patterns, scores your system 0-25, guides you through fixing the biggest gaps
- **`/cos-review`** — Bi-weekly review: smart diagnostic that remembers your previous score, tests all MCPs and plugins, detects manual repetitions (skill candidates), suggests ONE highest-leverage action
- **`/cos-review status`** — 30-second health check: tests every MCP/plugin connection, checks scheduled tasks, reports with ✅/⚠️ icons

**Cross-platform:** Works on Mac, Windows, and Linux. Detects your OS and adapts (LaunchAgents vs schtasks vs cron).

**Example:**
```
/cos-review setup    # First run — full scan + guided fixes
/cos-review          # Every 2 weeks — track your growth
/cos-review status   # Quick health check
```

### `/slide-inspector` - PowerPoint QA

Systematic quality audit for PowerPoint decks. Catches layout bugs, design inconsistencies, and structural anti-patterns that make slides look unpolished.

**What it does:**
- **Programmatic analysis** - unpacks .pptx XML and checks for bounding box overlaps, edge proximity, font/color inventory, text box fragmentation ("one box per line"), code snippet styling, element density
- **Visual inspection checklist** - 8 categories (overlap/collision, spacing, typography, code, consistency, simplicity, anti-patterns, slide-type-specific) for human/AI-vision review
- **Severity-tagged report** - 🔴 critical / 🟡 warning / 🟢 suggestion
- **Post-creation QA** - designed to run after the pptx skill before delivering any deck

**Usage:**
```
/slide-inspector presentation.pptx
```

Or invoked automatically as a QA step after generating a deck with the pptx skill.

### `/linkedin-research-post` - Research-to-LinkedIn Pipeline

Research a topic across platforms and publish a LinkedIn post in your voice.

**What it does:**
- Researches via sub-agents across LinkedIn, Reddit, Twitter, YouTube (AnySite MCP)
- Analyzes trending content and identifies content gaps
- Drafts a post using your SOUL.md voice profile
- Optionally runs `/council` for multi-perspective review
- Publishes to LinkedIn via Unipile MCP

**Requires:**
- [AnySite MCP](https://anysite.io) - use code **BAYRAMMCP** for 30 days free
- [Unipile MCP](https://unipile.com) - 7-day free trial for LinkedIn publishing

**Example:**
```
/linkedin-research-post AI productivity tools for product managers
```

## Installation

### Option 1: Plugin install (recommended)

In Claude Code, add the marketplace and install:
```
/plugin marketplace add BayramAnnakov/ai-personal-os-skills
/plugin install onboarding@ai-personal-os-skills
/plugin install daily-log@ai-personal-os-skills
/plugin install atomize@ai-personal-os-skills
/plugin install cos-review@ai-personal-os-skills
/plugin install slide-inspector@ai-personal-os-skills
/plugin install linkedin-research-post@ai-personal-os-skills
/reload-plugins
```

### Option 2: Clone and copy skills

```bash
# Clone the repo
git clone https://github.com/BayramAnnakov/ai-personal-os-skills.git

# Copy all skills at once
cp -r ai-personal-os-skills/skills/* ~/.claude/skills/

# Or copy individual skills
cp -r ai-personal-os-skills/skills/onboarding ~/.claude/skills/
cp -r ai-personal-os-skills/skills/daily-log ~/.claude/skills/
cp -r ai-personal-os-skills/skills/atomize ~/.claude/skills/
cp -r ai-personal-os-skills/skills/cos-review ~/.claude/skills/
cp -r ai-personal-os-skills/skills/slide-inspector ~/.claude/skills/
cp -r ai-personal-os-skills/skills/linkedin-research-post ~/.claude/skills/
```

### Option 3: Single skill via curl

```bash
mkdir -p ~/.claude/skills/daily-log
curl -o ~/.claude/skills/daily-log/SKILL.md \
  https://raw.githubusercontent.com/BayramAnnakov/ai-personal-os-skills/main/skills/daily-log/SKILL.md
```

## Usage

Open Claude Code and type the skill name:

```
/onboarding          # Set up your AI workspace (do this first)
/daily-log           # Daily 5-min journal
/atomize [text]      # Extract atomic notes from content
/cos-review setup    # Diagnose your system (do after onboarding)
/cos-review          # Bi-weekly performance review
/cos-review status   # Quick health check
/slide-inspector presentation.pptx   # QA a PowerPoint deck
```

For LinkedIn publishing, first set up AnySite + Unipile MCPs (see skill prerequisites), then:
```
/linkedin-research-post [topic]
```

## Skill Progression

These skills are designed to build on each other:

1. **`/onboarding`** - Create your CLAUDE.md and SOUL.md (foundation)
2. **`/daily-log`** - Build daily journaling habit (data collection)
3. **`/atomize`** - Extract knowledge from content (knowledge system)
4. **`/cos-review setup`** - Diagnose your system and fix gaps (system health)
5. **`/linkedin-research-post`** - Research and publish (output)
6. **`/cos-review`** - Bi-weekly review to track growth (ongoing)

## Course

Part of the [AI Personal OS](https://empatika.com) course (Season 2, 2026) by Bayram Annakov.

## License

MIT - see [LICENSE](LICENSE)
