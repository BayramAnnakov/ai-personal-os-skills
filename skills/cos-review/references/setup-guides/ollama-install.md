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
# For 8GB RAM machines
ollama pull qwen3.5:7b

# For 16GB+ RAM machines (better quality)
ollama pull qwen3.5:14b
```

## Use with Claude Code

```bash
ANTHROPIC_BASE_URL=http://localhost:11434 \
ANTHROPIC_API_KEY=ollama \
claude
```

This runs Claude Code with Ollama as the backend. Slower and less capable than Claude API, but completely private.

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
| `ollama run <model>` | Chat with a model directly |
| `ollama stop <model>` | Stop a running model (free RAM) |
| `ollama rm <model>` | Delete a model |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "ollama: command not found" | Restart terminal after install, or add to PATH |
| Download stuck | Check internet connection, try `ollama pull` again (it resumes) |
| Out of memory | Use smaller model: `qwen3.5:7b` instead of `14b` |
| Slow responses | Normal for local models. Use for privacy, not speed. |
