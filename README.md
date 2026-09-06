# Travel agent (Cursor)

This repo is a **Cursor chat agent**, not a web app and not a trip-planner UI.

Open the repo in Cursor (or start a Cloud Agent on it) and ask. Cursor’s model is the agent. There are no outside LLM APIs to pay for.

## How to use it

Ask in plain language, for example:

- We’re in Munich 6–8 Sep with Noga and Shir. Coffee and dinner tonight?
- Innsbruck for five nights. One easy nature day, not a hike-heavy trip.
- We went to Man Versus Machine. Liked it.

The agent reads your files, answers, then asks what you thought so it can update taste and history.

## How to set a rule

There is no Rules field on [cursor.com/agents](https://cursor.com/agents). Cloud Agents read rules from this repo (and, optionally, from User Rules in the Cursor desktop app).

**In this repo (already set).** Edit `.cursor/rules/travel-agent.mdc` and commit. That file is the travel-agent rule (`alwaysApply: true`). To add another rule, add another `.mdc` file in `.cursor/rules/` or ask Agent: `/create-rule`.

**In Cursor desktop (User Rules — optional).** These apply to every project and every Cloud Agent on your account. They are not on the website.

1. Open the **Cursor app** on your computer (not cursor.com).
2. Open **Customize** in the left sidebar. If you do not see it: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux), type **Customize**, or open **Cursor Settings → Rules**.
3. Click **Rules**.
4. Paste into **User Rules**:

```
This Testing repo is my travel agent. If data/who-i-am.md is missing, run git fetch origin main && git merge --ff-only origin/main before any restaurant, hotel, or coffee answer. Follow .cursor/skills/travel-agent/SKILL.md. Do not web-search a restaurant until those files exist.
```

User Rules are belt-and-suspenders for a Cloud Agent that boots from a stale snapshot. Day to day, the project rule in `.cursor/rules/travel-agent.mdc` is enough.

**Team plans.** Admins can also set Team Rules at [cursor.com/dashboard](https://cursor.com/dashboard) → team content. That is a different screen from Cloud Agents.

## Files

| File | Who writes it | Role |
| ---- | ------------- | ---- |
| `data/who-i-am.md` | You | Identity. The agent reads it and does not rewrite it. |
| `data/taste.json` | Agent, from your replies | Living likes, dislikes, feedback log. |
| `data/taste-vector.json` | Agent | Numeric taste vector. Options are scored and ranked by distance. |
| `data/history.json` | Agent, when you say you went | Places visited, liked or disliked. |
| `data/search-cache.json` | Agent | Last 30 days of scored options. Cleared on request. Not committed. |
| `.cursor/rules/travel-agent.mdc` | You (or ask the agent) | The always-on rule. This is how you set rules for this repo. |

Behavior lives in `.cursor/rules/travel-agent.mdc` and `.cursor/skills/travel-agent/SKILL.md`. Cloud Agents also read `.cursor/CLOUD.md`: if the checkout is behind `origin/main`, pull before answering.
