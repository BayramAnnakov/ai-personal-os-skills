# Ollama Installation Guide

Ollama lets you run AI models locally — your data never leaves your machine.

## Install

**Mac:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.com and run the installer.

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Pull a Model

```bash
# For 8GB+ RAM machines (9B model, 6.6 GB download)
ollama pull qwen3.5

# For 16GB+ RAM machines (27B model, 17 GB download, better quality)
ollama pull qwen3.5:27b
```

## Critical: Fix Context Window

Claude Code needs at least 64K tokens. Ollama defaults to 4K on most GPUs. Without this fix, agentic tasks silently fail (model thinks but nothing happens).

```bash
# Set context window before starting Ollama
OLLAMA_CONTEXT_LENGTH=64000 ollama serve
```

Or adjust via the Ollama app settings slider.

Verify with: `ollama ps` (check the CONTEXT column).

## Use with Claude Code

**Simplest (recommended):**
```bash
ollama launch claude --model qwen3.5
```

**Manual:**
```bash
ANTHROPIC_AUTH_TOKEN=ollama \
ANTHROPIC_API_KEY="" \
ANTHROPIC_BASE_URL=http://localhost:11434 \
claude --model qwen3.5
```

## Cloud Models (no local GPU needed)

Ollama also routes to cloud providers — cheaper than Claude API, better quality than local:

```bash
ollama launch claude --model kimi-k2.5:cloud    # Moonshot AI, $0.60/$3.00 per 1M tokens
ollama launch claude --model qwen3.5:cloud       # Qwen cloud inference
```

## Cost Management (without Ollama)

If cost is the concern but privacy isn't, use Claude Code's built-in controls:

```bash
/effort low        # Faster + cheaper on any Claude model
/model sonnet      # Switch from Opus to Sonnet mid-session
```

## Use in /morning (Privacy Router)

Add this to your /morning skill:

```
Before sending email content to the cloud API,
classify each email. If it contains:
- Financial data (revenue, pricing, contracts)
- Client names or contact details
- Medical or legal information
- Internal strategy documents

Summarize it locally via Ollama first.
Send only the SUMMARY (not raw content) to the cloud API.
```

This is the Router Pattern upgraded:
- Week 1: Which AI TOOL for which task?
- Week 5: Which AI LOCATION for which data?

## Quick Reference

| Command | What |
|---------|------|
| `ollama list` | Show downloaded models |
| `ollama pull <model>` | Download a model |
| `ollama launch claude` | Start Claude Code with Ollama |
| `ollama ps` | Show running models + context size |
| `ollama stop <model>` | Stop a running model (free RAM) |
| `ollama rm <model>` | Delete a model |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "ollama: command not found" | Restart terminal after install, or add to PATH |
| Model thinks but does nothing (agentic fails) | Context window too small: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve` |
| Download stuck | Check internet, `ollama pull` again (it resumes) |
| Out of memory | Use smaller model: `qwen3.5` instead of `:27b` |
| Slow responses | Normal for local models. Use for privacy, not speed. |
