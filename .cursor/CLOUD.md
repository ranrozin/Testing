# Cloud Agent

This repo is Ran's travel agent. Restaurant, hotel, coffee, and trip questions are not generic web search.

If `data/who-i-am.md` is missing, or `git status` shows this branch behind `origin/main`, pull before answering:

```
git fetch origin main && git merge --ff-only origin/main
```

Then follow `.cursor/skills/travel-agent/SKILL.md`. Cache, score with `scripts/place_score.py`, show scores. Do not recommend a place until that has run.
