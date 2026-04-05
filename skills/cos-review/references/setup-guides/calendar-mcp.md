# Google Calendar MCP Setup

Connect your calendar so your CoS knows your schedule.

## Install

```bash
/plugin install google-calendar@claude-plugins-official
```

Follow the OAuth prompts to authorize access to your Google Calendar.

## Verify

After installation, test with:
```
Show me today's calendar events
```

Expected: a list of today's meetings with times, titles, and participants.

## What This Enables

- /morning can prep you for today's meetings
- CoS knows when you're free vs busy
- Meeting participants can be researched automatically
- Calendar conflicts are surfaced before they become problems

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Not authorized" | Re-run: `/plugin install google-calendar@claude-plugins-official` to refresh OAuth |
| No events showing | Check you authorized the correct Google account |
| Token expired | Re-install the plugin to refresh tokens |
| Multiple calendars | By default shows all calendars. Filter in your /morning skill if needed. |
