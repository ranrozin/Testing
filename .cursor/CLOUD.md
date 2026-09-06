# Cloud Agent

This repo is Ran's travel agent. Restaurant, hotel, coffee, and trip questions are not generic web search.

If `data/who-i-am.md` is missing, or `git status` shows this branch behind `origin/main`, pull before answering:

```
git fetch origin main && git merge --ff-only origin/main
```

Then follow `.cursor/skills/travel-agent/SKILL.md`. Cache, score with `scripts/taste_distance.py`, show distances. Do not recommend a place until that has run.

How to set rules: Android has no native Cursor app and no Rules screen (cursor.com/agents PWA). Edit `.cursor/rules/*.mdc` in this repo, or ask the agent to. Optional User Rules are desktop-only (Customize → Rules). See README.
