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

## Prerequisites

Check that these are available before starting:

1. **AnySite MCP** - for research (search LinkedIn, Reddit, Twitter, YouTube).
   - If not connected via Claude Desktop: Customize > Connectors > AnySite > Connect
   - Alternatively: `claude mcp add anysite -s user -- npx -y @anthropic/anysite-mcp`
   - **Signup:** anysite.io - use promo code **BAYRAMMCP** for 30 days free

2. **Unipile MCP** - for publishing to LinkedIn.
   - If not connected, add via HTTP MCP:
     ```
     claude mcp add-json unipile '{"type":"http","url":"https://developer.unipile.com/mcp","headers":{"X-API-KEY":"YOUR_API_KEY"}}'
     ```
   - **Signup:** unipile.com - 7-day free trial, no credit card required
   - After signup: connect your LinkedIn account via the Hosted Auth Wizard in the Unipile dashboard
   - Get your API key from the dashboard Settings page

3. **SOUL.md** - for voice/style. Check if `SOUL.md` exists in the project root or user home. If not, the post will use a neutral professional tone.

## Workflow

### Step 1: Get the Topic

Ask the user: "What topic should your LinkedIn post be about?"

If they give a broad topic, help narrow it:
- "What specific angle or insight do you want to share?"
- "Who is your audience on LinkedIn?"

### Step 2: Research (2-3 min)

Launch 3 parallel sub-agents to research the topic:

**Sub-agent 1 - LinkedIn perspective:**
Search LinkedIn posts about the topic from the past week. Find the 3-5 most engaged posts. Note what angles are getting traction, what's missing, what's overdone.

**Sub-agent 2 - Community perspective:**
Search Reddit and Twitter for the topic. Find honest opinions, complaints, praised solutions. Note where community sentiment differs from LinkedIn's polished narrative.

**Sub-agent 3 - Deep content:**
Search YouTube for the topic. If a relevant video exists, get the subtitles and extract key frameworks or expert claims. Also do a web search for recent articles.

Present a synthesis to the user:
- Key themes across platforms
- What's trending vs what's missing (the content gap)
- 2-3 potential angles for their post

### Step 3: Draft (1-2 min)

Ask the user which content template they prefer:

**A: "Lesson Learned"** - Hook -> Mistake -> Learning -> Takeaways -> Question
**B: "Curated Insight"** - I found X -> 3 insights -> My take -> What are you seeing?
**C: "How I Do X"** - Problem -> My setup (3 steps) -> Result

Read the user's SOUL.md (if it exists) to match their voice and tone.

Draft the post following these LinkedIn best practices:
- Under 1300 characters (sweet spot for engagement)
- Opening hook in the first line (before the "see more" fold)
- No hashtags in the body text
- 3 hashtags maximum at the very end
- Line breaks between paragraphs for readability
- End with a question that invites discussion

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
- Option A: Copy the post text to clipboard for manual pasting
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
