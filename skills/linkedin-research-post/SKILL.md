---
description: "Research a topic across multiple platforms and publish a LinkedIn post in your voice. Uses AnySite MCP for research, sub-agents for parallel investigation, /council for review, and Unipile MCP for publishing. Triggers: 'linkedin post', 'research and post', 'write a linkedin post about', 'publish to linkedin'."
allowed-tools:
  - Agent
  - AskUserQuestion
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# LinkedIn Research Post

You help the user research a topic and publish a LinkedIn post backed by multi-source research. The full pipeline: Research -> Analyze -> Draft -> Review -> Publish.

## Prerequisites - VERIFY BEFORE STARTING

Before launching any agents, run these checks:

**1. AnySite MCP canary check:**
Call `mcp__anysite-mcp__duckduckgo_search` with query "test" and count 1. If it returns results, AnySite is connected. If it errors, tell the user:
- Claude Desktop: Customize > Connectors > AnySite > Connect
- CLI: `claude mcp add anysite -s user -- npx -y @anthropic/anysite-mcp`
- Signup: anysite.io - promo code **BAYRAMMCP** for 30 days free

DO NOT launch research agents until this check passes.

**2. Voice profile:**
Check for voice/style in this order:
1. `SOUL.md` in project root or home directory
2. `user-profile.md` in project root
3. Memory files via recall
4. If nothing found, ask the user: "How would you describe your writing style in 1 sentence?"

**3. Unipile MCP (optional - check only at publish time):**
- Signup: unipile.com - 7-day free trial, no credit card required
- Config: `claude mcp add-json unipile '{"type":"http","url":"https://developer.unipile.com/mcp","headers":{"X-API-KEY":"YOUR_API_KEY"}}'`

## Workflow

### Step 1: Get the Topic

If the topic was provided via $ARGUMENTS, use it directly.

Otherwise ask: "What topic should your LinkedIn post be about?"

If too broad, narrow it:
- "What specific angle or insight do you want to share?"
- "Who is your audience on LinkedIn?"

### Step 2: Research (2-3 min)

Launch 3 parallel sub-agents. Each agent prompt MUST include the exact MCP tool names below. Do NOT say "use AnySite MCP" - agents don't know what that means.

**CRITICAL: Include these exact instructions in each agent prompt:**

**Sub-agent 1 - LinkedIn perspective:**
```
Research "[TOPIC]" on LinkedIn.

You MUST use these exact MCP tools (not WebSearch, not WebFetch):
- mcp__anysite-mcp__search_linkedin_posts(keywords="[TOPIC]", count=10, date_posted="past-week")
- mcp__anysite-mcp__get_linkedin_post_comments(urn="[post_urn]", count=5) for top posts

Find the 5 most engaged posts. For each note:
- Author name and headline
- Post text (first 200 chars)
- Reaction count and comment count
- The angle/take they used

Summarize: what angles get traction, what's overdone, what's missing.

PRIORITY: Try mcp__anysite-mcp tools first. If they fail, fall back to WebSearch/WebFetch.
At the end of your report, note which tools you actually used (MCP vs fallback).
```

**Sub-agent 2 - Community perspective:**
```
Research "[TOPIC]" on Reddit and Twitter.

You MUST use these exact MCP tools (not WebSearch, not WebFetch):
- mcp__anysite-mcp__search_reddit_posts(query="[TOPIC]", count=10, sort="top", time_filter="month")
- mcp__anysite-mcp__search_twitter_posts(query="[TOPIC]", count=10)
- mcp__anysite-mcp__get_reddit_post_comments(post_url="[url]") for top 2-3 posts

Find honest opinions, complaints, praised solutions.
Note where community sentiment DIFFERS from LinkedIn's polished narrative.

PRIORITY: Try mcp__anysite-mcp tools first. If they fail, fall back to WebSearch/WebFetch.
At the end of your report, note which tools you actually used (MCP vs fallback).
```

**Sub-agent 3 - Deep content:**
```
Research "[TOPIC]" on YouTube and the web.

You MUST use these exact MCP tools (not WebSearch, not WebFetch):
- mcp__anysite-mcp__search_youtube_videos(query="[TOPIC]", count=5)
- mcp__anysite-mcp__get_youtube_video_subtitles(video="[video_id]") for the top result
- mcp__anysite-mcp__duckduckgo_search(query="[TOPIC]", count=5) for web articles
- mcp__anysite-mcp__parse_webpage(url="[article_url]") to read top articles

Extract key frameworks, data points, expert claims.

PRIORITY: Try mcp__anysite-mcp tools first. If they fail, fall back to WebSearch/WebFetch.
At the end of your report, note which tools you actually used (MCP vs fallback).
```

**After launching agents:** Check their output within 15-20 seconds to verify they are using the MCP tools, not WebSearch/WebFetch. If any agent is using the wrong tools, send a corrective message immediately via SendMessage with the exact tool names.

**Synthesis:** Present to the user:
- Key themes across platforms (note which platform said what)
- "Different Truths": LinkedIn=aspirational, Reddit=honest, Twitter=reactive, YouTube=deep
- The content gap: what's trending vs what's missing
- 2-3 potential angles for their post, each mapped to a content template

### Step 3: Draft (1-2 min)

Ask the user which angle and template they prefer:

**A: "Lesson Learned"** - Hook -> Mistake -> Learning -> 3-5 Takeaways -> Question
**B: "Curated Insight"** - I found X -> 3 insights with context -> My take -> What are you seeing?
**C: "How I Do X"** - Problem everyone faces -> My setup (3 steps) -> Result with numbers

Read the user's voice profile (SOUL.md, user-profile.md, or memory) to match their tone.

Draft the post following these LinkedIn best practices:
- Under 1300 characters (sweet spot for engagement)
- Opening hook in the first line (before the "see more" fold)
- No hashtags in the body text
- 3 hashtags maximum at the very end
- Line breaks between paragraphs for readability
- End with a question that invites discussion
- Use specific data points from the research (not vague claims)

### Step 4: Review

Present the draft to the user. Ask:
- "Does this sound like YOU? What would you change?"
- "Any facts to verify or personal details to add?"

If the user wants a second opinion, offer to run /council:
```
/council "Should I publish this LinkedIn post? Is the angle compelling? What would make it stronger?"
```

Incorporate feedback. Iterate until the user is satisfied.

### Step 5: Publish

When the user approves, publish via Unipile MCP.

Unipile MCP is an OpenAPI proxy with these tools:
- `mcp__unipile__search-endpoints` - find the right API endpoint
- `mcp__unipile__get-endpoint` - get endpoint details (params, auth)
- `mcp__unipile__execute-request` - execute the API call via HAR format

To publish a LinkedIn post:

1. First, get the user's Unipile base URL and API key. Ask them for:
   - **Base URL** (e.g., `https://api1.unipile.com:13118`) - subdomain and port are user-specific
   - **API Key** - from their Unipile dashboard

2. List their LinkedIn accounts to get the account_id:
   ```json
   mcp__unipile__execute-request({
     "harRequest": {
       "method": "GET",
       "url": "https://{subdomain}.unipile.com:{port}/api/v1/accounts",
       "headers": [{"name": "X-API-KEY", "value": "{their_key}"}]
     }
   })
   ```

3. Create the post using **multipart/form-data** (CRITICAL - JSON body does NOT work):
   ```json
   mcp__unipile__execute-request({
     "harRequest": {
       "method": "POST",
       "url": "https://{subdomain}.unipile.com:{port}/api/v1/posts",
       "headers": [
         {"name": "X-API-KEY", "value": "{their_key}"},
         {"name": "Content-Type", "value": "multipart/form-data; boundary=Boundary123"}
       ],
       "postData": {
         "mimeType": "multipart/form-data",
         "text": "--Boundary123\r\nContent-Disposition: form-data; name=\"account_id\"\r\n\r\n{account_id}\r\n--Boundary123\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\n{post_text}\r\n--Boundary123--\r\n"
       }
     }
   })
   ```
   Successful response: `{"object":"PostCreated","post_id":"..."}`

If Unipile is not connected:
- Option A: Copy the post text for manual pasting
- Option B: Save as a draft file for later publishing

After publishing, suggest:
- "Share the post URL in your course group for cross-engagement"
- "Set a reminder to respond to comments in 2-4 hours"

## Voice Guidelines

When SOUL.md exists, use it as the primary voice reference. When it doesn't, use these defaults:
- Professional but human (not corporate)
- Specific over vague (numbers, names, concrete examples)
- Personal perspective over generic advice
- Conversational, not academic
- No buzzwords: "leverage," "synergy," "game-changer," "unlock"
