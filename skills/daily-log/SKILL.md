---
description: "Daily 5-minute energy-mood-focus journal. Creates structured daily logs in notes/ folder. Run this every day to build your personal data foundation for Week 2's Knowledge OS."
allowed-tools:
  - AskUserQuestion
  - Write
  - Read
  - Bash
---

# /daily-log — Daily Journal

Run a quick 5-minute daily check-in. Ask 6 questions, save a structured note.

## Interview Flow

Ask each question one at a time using `AskUserQuestion`. Keep it brisk and friendly.

### Question 1: Energy
- **Question:** "How's your energy today?"
- **Options:** `["1-3 (Low)", "4-5 (Below average)", "6-7 (Good)", "8-10 (Great)"]`
- Map the answer to a number: Low=2, Below average=5, Good=7, Great=9

### Question 2: Focus
- **Question:** "How well could you concentrate today?"
- **Options:** `["1-3 (Low)", "4-5 (Below average)", "6-7 (Good)", "8-10 (Great)"]`
- Map the answer to a number: Low=2, Below average=5, Good=7, Great=9

### Question 3: Mood
- **Question:** "Overall mood?"
- **Options:** `["1-3 (Low)", "4-5 (Below average)", "6-7 (Good)", "8-10 (Great)"]`
- Map the answer to a number: Low=2, Below average=5, Good=7, Great=9

### Question 4: Highlight
- **Question:** "What was the highlight of your day?"
- **Options:** `["Got something important done", "Had a great conversation", "Learned something new", "Other"]`
- Accept whatever they type — the options are just prompts.

### Question 5: Blocker
- **Question:** "What slowed you down or frustrated you?"
- **Options:** `["Too many meetings", "Couldn't focus", "Stuck on a problem", "Nothing major", "Other"]`
- Accept whatever they type.

### Question 6: Tomorrow
- **Question:** "What's the one thing you want to accomplish tomorrow?"
- **Options:** `["Finish a key task", "Start something new", "Clear my backlog", "Other"]`
- Accept whatever they type.

## Save the Log

1. Get today's date in YYYY-MM-DD format (run `date +%Y-%m-%d` via Bash).
2. Create the `notes/` directory in the current working directory if it does not exist.
3. Write the file to `notes/daily-log-YYYY-MM-DD.md` with this format:

```markdown
# Daily Log — YYYY-MM-DD

## Vitals
- Energy: X/10
- Focus: X/10
- Mood: X/10

## Highlight
[their answer]

## Blocker
[their answer]

## Tomorrow
[their answer]

---
*Logged via /daily-log*
```

## After Saving

Print a one-line confirmation:

> Logged! Energy X, Focus X, Mood X. See you tomorrow.

If an `achievements.md` file exists in the current directory, update it:
- Count `notes/daily-log-*.md` files to update streak and check achievement unlocks (First Log, Consistency, Week Warrior, Fortnight Force).
- Add an entry to the Activity Log table.

## Auto-Enrich: Pattern Analysis (every 3rd log)

After saving, count all `notes/daily-log-*.md` files. If the count is divisible by 3 (3, 6, 9, 12...):

1. Read ALL daily-log files in `notes/`
2. Read `user-profile.md` (if it exists)
3. Analyze patterns across all logs:
   - Energy/focus/mood trends (which days are high/low?)
   - Recurring blockers (what themes keep appearing?)
   - Correlations (does high energy correlate with certain activities?)
   - Productivity windows (any time-of-week patterns?)
4. Add or update a `## Patterns From Daily Logs` section at the end of `user-profile.md`
5. Keep it concise — 5-8 bullet points max. Replace the previous version, don't append.
6. Tell the user: "Updated user-profile.md with patterns from X logs."

Example patterns section:
```markdown
## Patterns From Daily Logs
*Auto-updated from 9 daily logs*
- Energy peaks mid-week (Tue-Thu avg 8, Mon avg 5)
- Most common blocker: context-switching between projects
- Focus improves on days with a clear "one thing" from previous log
- Mood correlates strongly with getting the highlight task done
- Best productivity window: mornings before first meeting
```

## Optional: Group Share

After everything is saved, ask ONE final question:

- **Question:** "Share something with the course group?"
- **Options:** `["Share streak + vibe (e.g. 'Day 5. Energy 8.')", "Write a custom message", "Skip — keep it private"]`

If they choose to share:
1. Compose a short one-liner (streak count + vitals, or their custom text)
2. Show the exact message to the user
3. Save it as a **draft** in the course Telegram group **"edu-ai-productivity-s2"** using `save_draft` via MCP (do NOT send — draft only)
4. Tell them: "Draft saved to the group chat. Open it in Telegram to review and send."
5. If MCP is not connected or drafting fails, just print the message and say "Copy this to the group chat when you're ready"

If they skip, move on silently.

Do NOT turn this into a long conversation. The whole interaction should take under 5 minutes.
