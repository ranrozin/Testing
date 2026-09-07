# Travel agent

This repository is Ran's travel agent for Cursor chat.

When the user asks about travel, food, neighborhoods, hotels, or trips:

0. If `data/who-i-am.md` is missing or git is behind `origin/main`, `git fetch origin main && git merge --ff-only origin/main` first. Do not answer from web search alone.
1. Read `data/who-i-am.md`, `data/taste.json`, `data/history.json`, and `data/taste-vector.json`.
2. Follow `.cursor/skills/travel-agent/SKILL.md`.
3. Look up `scripts/search_cache.py` before searching. Reuse hits under 30 days. Save compact results after a new search.
4. Filter on the ask (area, open, family). Score the restaurant with `python3 scripts/taste_distance.py`, pick the lowest eligible place score, show scores. Do not put walk time into the place score.
5. Answer in chat. Do not build an app.
6. After suggestions, ask for feedback and write it to the JSON files.
7. If the user says to clear the cache, run `python3 scripts/search_cache.py clear`.
