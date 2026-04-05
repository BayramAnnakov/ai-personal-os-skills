# Scheduling /morning — Daily Trigger Setup

## Mac: LaunchAgent

Create this file at `~/Library/LaunchAgents/com.user.morning-briefing.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.morning-briefing</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/claude</string>
        <string>--print</string>
        <string>Run /morning and send the output to my Telegram</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/morning-briefing.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/morning-briefing.err</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

### Install
```bash
# Copy the plist (adjust path if needed)
cp com.user.morning-briefing.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/com.user.morning-briefing.plist

# Verify it's loaded
launchctl list | grep morning
```

### Test
```bash
# Run it manually to verify
launchctl start com.user.morning-briefing

# Check output
cat /tmp/morning-briefing.log
cat /tmp/morning-briefing.err
```

### Adjust Time
Edit the `Hour` and `Minute` values. Unload, edit, reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.morning-briefing.plist
# edit the file
launchctl load ~/Library/LaunchAgents/com.user.morning-briefing.plist
```

## Windows: Task Scheduler

```powershell
# Create scheduled task for 7:00 AM daily
schtasks /create /tn "MorningBriefing" /tr "claude --print \"Run /morning and send output to Telegram\"" /sc daily /st 07:00

# Verify
schtasks /query /tn "MorningBriefing"

# Test run
schtasks /run /tn "MorningBriefing"

# Delete if needed
schtasks /delete /tn "MorningBriefing" /f
```

## Linux: Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs at 7:00 AM daily)
0 7 * * * /usr/local/bin/claude --print "Run /morning and send output to Telegram" >> /tmp/morning-briefing.log 2>&1
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "claude: command not found" | Use full path: `which claude` to find it, update the plist |
| No output | Check stderr log: `cat /tmp/morning-briefing.err` |
| MCP auth fails in LaunchAgent | Tokens may need to be refreshed — run `/cos-review status` |
| Runs but produces empty briefing | Run `/morning` interactively first to debug |
